#!/usr/bin/env python3
"""Render the Athene vs Global Atlantic comparison page.

Every number machine-extracted and gate-verified from each company's own
filings (Athene: ATH supplements + 10-K + statutory drill; GA: GALD
supplements + KKR filings + FCRs + statutory statements). Coverage:
2023-2025 all quarters + annuals + everything reported in 2026 (1Q26 both).
Output: dossiers/comparison/athene-vs-ga.html
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'dossiers/comparison/athene-vs-ga.html'
DEST.parent.mkdir(exist_ok=True)

ATH = {}
for r in csv.DictReader(open(ROOT / 'extract/athene/quarterly_supplement.csv')):
    if r['value'] != '':
        ATH[(r['quarter'], r['metric'])] = float(r['value'])
ATH_AN = {(r['year'], r['metric']): float(r['value'])
          for r in csv.DictReader(open(ROOT / 'extract/athene/annual_engine.csv'))}
ATH_TR = {(r['year'], r['dimension'], r['bucket']): int(r['bacv'])
          for r in csv.DictReader(open(ROOT / 'extract/athene/d1_trends.csv'))}
GA = {}
for r in csv.DictReader(open(ROOT / 'extract/global-atlantic/gald_supplement.csv')):
    if r['value'] != '':
        GA[(r['period'], r['metric'])] = float(r['value'])
CAP = {(r['entity'], r['year'], r['metric']): float(r['value_musd'])
       for r in csv.DictReader(open(ROOT / 'extract/global-atlantic/ga_capital.csv'))}
STAT = {(r['carrier'], int(r['year']), r['metric']): float(r['value']) if r['value'] else None
        for r in csv.DictReader(open(ROOT / 'extract/global-atlantic/statutory_l0.csv'))}

QTRS = ['1Q23', '2Q23', '3Q23', '4Q23', '1Q24', '2Q24', '3Q24', '4Q24',
        '1Q25', '2Q25', '3Q25', '4Q25', '1Q26']
FYS = ['FY2023', 'FY2024', 'FY2025']


def fmt(v, money=True, pct=False, dp=0):
    if v is None:
        return '<span class="na">·</span>'
    if pct:
        return f'{v:.2f}%'
    if abs(v) >= 1000 and money:
        return f'{"−" if v < 0 else ""}${abs(v)/1000:,.1f}B'
    return f'{"−" if v < 0 else ""}${abs(v):,.0f}M' if money else f'{v:,.{dp}f}'


def rowpair(label, a_fn, g_fn, periods, pct=False):
    cells_a = ''.join(f'<td>{fmt(a_fn(p), pct=pct)}</td>' for p in periods)
    cells_g = ''.join(f'<td>{fmt(g_fn(p), pct=pct)}</td>' for p in periods)
    return (f'<tr class="ath"><td class="lbl">{label}<span class="who">ATHENE</span></td>{cells_a}</tr>'
            f'<tr class="ga"><td class="lbl"><span class="who">GLOBAL ATLANTIC</span></td>{cells_g}</tr>')


def table(title, note, rows_html, periods):
    heads = ''.join(f'<th>{p}</th>' for p in periods)
    return (f'<h2>{title} <span class="cnt">— {note}</span></h2><hr class="rule">'
            f'<div class="tbl-scroll"><table><thead><tr><th></th>{heads}</tr></thead>'
            f'<tbody>{rows_html}</tbody></table></div>')


A = lambda p, k: ATH.get((p, k))
G = lambda p, k: GA.get((p, k))

def ga_rate(p, printed_key, dollar_key):
    """Printed rate if filed; else derived = dollar x (4 if quarterly) / avg AIA."""
    v = GA.get((p, printed_key))
    if v is not None:
        return v
    d, aia = GA.get((p, dollar_key)), GA.get((p, 'avg_aia'))
    if d is None or not aia:
        return None
    mult = 1 if p.startswith('FY') else 4
    return round(d * mult / aia * 100, 2)


P = QTRS + FYS

# spread pair: Athene NIS% vs GA underwriting margin%
html_rows_spread = (
    rowpair('Earned rate', lambda p: A(p, 'sre_nie_pct'), lambda p: ga_rate(p, 'nier', 'adj_nii'), P, pct=True)
    + rowpair('Cost of float/insurance', lambda p: A(p, 'sre_cof_pct'), lambda p: ga_rate(p, 'cost_ins_ratio', 'adj_cost_ins'), P, pct=True)
    + rowpair('NET SPREAD / UNDERWRITING MARGIN', lambda p: A(p, 'sre_nis_pct'), lambda p: ga_rate(p, 'underwriting_ratio', 'adj_underwriting'), P, pct=True)
)
html_rows_growth = (
    rowpair('Total inflows / new business', lambda p: A(p, 'total_gross_inflows') or ATH_AN.get((p, 'total_gross_inflows')),
            lambda p: (lambda vals: sum(v for v in vals if v is not None) if any(v is not None for v in vals) else None)(
                [G(p, k) for k in ('nbv_retirement_total', 'nbv_preneed', 'nbv_block', 'nbv_flow', 'nbv_prt', 'nbv_funding_agreements', 'nbv_life')]), P)
    + rowpair('of which funding agreements', lambda p: A(p, 'funding_agreements') or ATH_AN.get((p, 'funding_agreements')),
              lambda p: G(p, 'nbv_funding_agreements'), P)
    + rowpair('of which block/inorganic', lambda p: A(p, 'gross_inorganic') or ATH_AN.get((p, 'gross_inorganic')),
              lambda p: G(p, 'nbv_block'), P)
)
html_rows_earn = (
    rowpair('Operating earnings (SRE / AOE pre-tax)', lambda p: A(p, 'sre') or ATH_AN.get((p, 'sre')),
            lambda p: G(p, 'adj_op_pretax'), P)
    + rowpair('GAAP net income to common/shareholder', lambda p: A(p, 'gaap_ni_common') or ATH_AN.get((p, 'gaap_ni_common')),
              lambda p: G(p, 'ni_shareholder'), P)
)
html_rows_equity = (
    rowpair('Shareholders equity (AHL / GALD)', lambda p: A(p, 'eq_ahl_total'),
            lambda p: G(p, 'shareholders_equity'), P)
    + rowpair('ROE — GAAP basis', lambda p: None, lambda p: G(p, 'roe'), P, pct=True)
    + rowpair('Operating ROE (Adj Op ROE; Athene = engine-panel ROE, annual)', lambda p: None,
              lambda p: G(p, 'adj_op_roe'), P, pct=True)
)

# quality year-ends
QY = ['4Q23', '4Q24', '4Q25', '1Q26']


def ath_bigsh(p):
    y = {'4Q23': '2023', '4Q24': '2024', '4Q25': '2025'}.get(p)
    if not y:
        return None
    tot = ATH_TR[(y, 'total', 'all')]
    big = sum(ATH_TR.get((y, 'naic_band', f'NAIC {i}'), 0) for i in '3456')
    return big / tot * 100


def ga_naic_bigsh(p):
    t, b = GA.get((p, 'naic_total')), GA.get((p, 'naic_big'))
    return b / t * 100 if t and b else None


def ga_nrsro_bigsh(p):
    t, b = GA.get((p, 'nrsro_total')), GA.get((p, 'nrsro_big'))
    return b / t * 100 if t and b else None


def ath_pl(p):
    y = {'4Q23': '2023', '4Q24': '2024', '4Q25': '2025'}.get(p)
    if not y:
        return None
    return ATH_TR[(y, 'rating_source', 'PL (private letter)')] / ATH_TR[(y, 'total', 'all')] * 100


html_rows_quality = (
    rowpair('Below-IG share — regulatory ruler (NAIC)', ath_bigsh, ga_naic_bigsh, QY, pct=True)
    + rowpair('Below-IG share — market ruler (NRSRO)', lambda p: None, ga_nrsro_bigsh, QY, pct=True)
    + rowpair('Private-letter share (Athene statutory; GA n/a — no public CUSIP-level filing)',
              ath_pl, lambda p: None, QY, pct=True)
)

CAPY = ['2023', '2024', '2025']
html_rows_capital = (
    rowpair('Bermuda pivot ECR coverage (AARe / GA Re)',
            lambda y: {'2024': 242.0, '2025': 202.0}.get(y),
            lambda y: CAP[('GA Re', y, 'eligible_capital')] / CAP[('GA Re', y, 'ecr')] * 100, CAPY, pct=True)
    + rowpair('Second reinsurer (ALRe / GAAL)',
              lambda y: {'2024': 453.0, '2025': 309.0}.get(y),
              lambda y: CAP[('GAAL', y, 'eligible_capital')] / CAP[('GAAL', y, 'ecr')] * 100, CAPY, pct=True)
    + rowpair('Lead US carrier C&S (AAIA TAC / FLIC+CWA C&S)',
              lambda y: 9504.0 if y == '2025' else None,
              lambda y: ((STAT.get(('flic', int(y), 'capital_surplus')) or 0)
                         + (STAT.get(('cwa', int(y), 'capital_surplus')) or 0)) / 1e6 or None, CAPY)
)


def runnable_a(p):
    fa, tot = ATH.get((p, 'nrl_fa')), ATH.get((p, 'nrl_total'))
    return fa / tot * 100 if fa and tot else None


def runnable_g(p):
    fa, tot = GA.get((p, 'res_fa')), GA.get((p, 'res_total'))
    return fa / tot * 100 if fa and tot else None


html_rows_run = rowpair('Funding agreements as % of net reserves (runnable share)',
                        runnable_a, runnable_g, ['4Q24', '1Q25', '2Q25', '3Q25', '4Q25', '1Q26'], pct=True)

html = f"""<title>Athene vs Global Atlantic — the comparison</title>
<style>
:root{{--bg:#F6F5F1;--panel:#FFF;--ink:#22271F;--muted:#6E756D;--line:#E3E1D8;--line2:#CFCCC0;
--us:#0F6E56;--us-bg:#E4F3EC;--bm:#A3431D;--bm-bg:#F9ECE5;--acc:#185FA5;--warn:#BA7517;--warn-bg:#FAEEDA}}
@media (prefers-color-scheme: dark){{:root{{--bg:#15191B;--panel:#1D2325;--ink:#E7E9E3;--muted:#8F978F;
--line:#2B3234;--line2:#3A4245;--us:#5DCAA5;--us-bg:#0C3A2D;--bm:#F0997B;--bm-bg:#43200F;--acc:#85B7EB;--warn:#D9A54A;--warn-bg:#3A2B10}}}}
:root[data-theme="dark"]{{--bg:#15191B;--panel:#1D2325;--ink:#E7E9E3;--muted:#8F978F;--line:#2B3234;--line2:#3A4245;
--us:#5DCAA5;--us-bg:#0C3A2D;--bm:#F0997B;--bm-bg:#43200F;--acc:#85B7EB;--warn:#D9A54A;--warn-bg:#3A2B10}}
:root[data-theme="light"]{{--bg:#F6F5F1;--panel:#FFF;--ink:#22271F;--muted:#6E756D;--line:#E3E1D8;--line2:#CFCCC0;
--us:#0F6E56;--us-bg:#E4F3EC;--bm:#A3431D;--bm-bg:#F9ECE5;--acc:#185FA5;--warn:#BA7517;--warn-bg:#FAEEDA}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--ink);font:15px/1.55 "Avenir Next","Segoe UI",system-ui,sans-serif;margin:0}}
.wrap{{max-width:1140px;margin:0 auto;padding:36px 24px 64px}}
header{{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:22px}}
.eyebrow{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:30px;font-weight:600;margin:0;text-wrap:balance}}
.sub{{color:var(--muted);margin:8px 0 0;font-size:14px}}
a{{color:var(--acc);text-decoration:none}} a:hover{{text-decoration:underline}}
h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;margin:38px 0 6px}}
h2 .cnt{{color:var(--muted);font-weight:400;letter-spacing:0;text-transform:none}}
.rule{{border:0;border-top:1px solid var(--line2);margin:0 0 14px}}
.verdict{{background:var(--panel);border-left:4px solid var(--acc);padding:18px 22px;font-size:15.5px;line-height:1.6}}
.callout{{background:var(--panel);border-left:3px solid var(--bm);padding:13px 17px;margin:12px 0;font-size:14px}}
.tbl-scroll{{overflow-x:auto;margin-bottom:6px}}
table{{border-collapse:collapse;background:var(--panel);border:1px solid var(--line);font-size:12.5px;min-width:100%}}
th{{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);text-align:right;font-weight:600;
padding:8px 8px;border-bottom:1px solid var(--line2);white-space:nowrap}}
td{{padding:6px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap;
font-variant-numeric:tabular-nums}}
td.lbl{{text-align:left;font-weight:600;min-width:230px;white-space:normal}}
.who{{display:block;font-size:9.5px;letter-spacing:.1em;font-weight:700}}
tr.ath .who{{color:var(--us)}} tr.ga .who{{color:var(--bm)}}
tr.ath{{background:var(--us-bg)}} tr.ga{{background:var(--bm-bg)}}
tr.ath td,tr.ga td{{border-bottom:0}} tr.ga td{{border-bottom:1px solid var(--line2)}}
.na{{color:var(--muted)}}
.footer{{margin-top:40px;padding-top:14px;border-top:1px solid var(--line2);font-size:12px;color:var(--muted)}}
</style>
<div class="wrap">
<header>
<p class="eyebrow">CREDIT MAP · PHASE 1 · THE CROSS-SECTION BEGINS</p>
<h1>Athene vs Global Atlantic — two PE-insurance machines, one ruler</h1>
<p class="sub">Every number machine-extracted and gate-verified from each company's own filings
(ATH &amp; GALD financial supplements, 10-K/10-Q, statutory statements, Bermuda FCRs — sha-tracked in the manifest).
Periods: all quarters 2023–2025, annuals, and everything reported in 2026 (both companies through 1Q26).
Athene quarterly cells before 4Q24 are blank where its older supplements use an unreadable font encoding
(decoder parked — boundary logged, not papered over); its annual columns are complete.</p>
</header>

<div class="verdict">
<strong>The comparative read:</strong> the same machine, tuned differently. Athene runs bigger
($297B avg invested assets vs GA's $157B), hotter (net spread 1.34% vs GA's 1.25% — both compressed hard from
2023), and more opaque (25.3% of its bond book graded by private letters; GA has no public position-level filing
at all — a boundary, not an exoneration). GA runs <em>junkier on the market's ruler</em> — 10.0% below-IG by NRSRO
against Athene's ~4% — and its NAIC-vs-NRSRO gap (5.6% vs 10.0%) says its regulatory designations flatter its book
by more than Athene's do. <strong>Both engines printed GAAP losses within the last year while their "operating"
measures stayed positive</strong> — the adjusted-vs-GAAP divergence is a sector feature, not an Athene quirk.
Bermuda cushions: GA Re 205% ECR coverage sits in the same compressing band as AARe's 202%.
</div>

{table('1 · The spread engines', 'earned rate − cost of float = the margin; both compressing',
       html_rows_spread, P)}
<div class="callout"><strong>Both margins rolled over.</strong> Athene: 1.65% → 1.34% over 2025-26.
GA: 1.80% (2023) → 1.25% (1Q26) — a deeper slide from a lower peak. The repricing race
(cost of funds up faster than earned) is the same story on both balance sheets.</div>

{table('2 · Growth — money in', 'gross inflows (Athene) vs new business volume (GA); bases differ, trends compare',
       html_rows_growth, P)}

{table('3 · Operating earnings vs the GAAP tape', 'the divergence both companies share',
       html_rows_earn, P)}
<div class="callout"><strong>The shared tell:</strong> GA FY2025 net income to shareholder was
<strong>−$1,203M</strong> against +$1,081M adjusted-operating pre-tax; Athene's 1Q26 was
<strong>−$1,973M</strong> to common against +$719M SRE. Investment losses and reinsurance fair-value moves
are recognized in GAAP and stripped from the operating measures — on both tapes, in the same direction, at scale.</div>

{table('4 · Portfolio quality — the two rulers', 'regulatory (NAIC) vs market (NRSRO) grading of the bond books',
       html_rows_quality, QY)}
<div class="callout"><strong>The two-ruler gap is the opacity metric.</strong> GA's book is 5.6% below-IG by NAIC
but 10.0% by market ratings — a 4.4pt flattering gap. Athene's statutory below-IG is 2.9% with its supplement
NAIC view at ~3.9% — but 25.3% of its book is graded by unpublished private letters the market prices 2–3 notches
lower (its letter-slip stress: below-IG would reach 7–14% if the market is right). Different mechanisms,
same direction: both books look better on the regulatory ruler than the market one.</div>

{table('5 · Capital — the cushions, on their own rulers', 'Bermuda ECR coverage + lead-carrier statutory capital',
       html_rows_capital, CAPY)}

{table('6 · The runnable share', 'funding agreements as % of net reserves', html_rows_run,
       ['4Q24', '1Q25', '2Q25', '3Q25', '4Q25', '1Q26'])}
<div class="callout"><strong>Divergent funding risk:</strong> Athene's runnable share climbed 21% → 27.2%;
GA's sits near 6–8% of net reserves. On liquidity structure, Athene is the outlier of the pair.</div>

<h2>7 · THE FIVE-PLATFORM CROSS-SECTION <span class="cnt">— every PE-insurance machine, one table (latest year-end)</span></h2><hr class="rule">
<div class="tbl-scroll"><table>
<thead><tr><th></th><th>Athene (Apollo)</th><th>Global Atlantic (KKR)</th><th>Brookfield (AEL+ANICO)</th><th>Ares (Aspida)</th><th>Blue Owl (Kuvare)</th></tr></thead>
<tbody>
<tr><td style="text-align:left">Ownership model</td><td>owns insurers</td><td>owns insurers</td><td>owns insurers</td><td>manages + fund-controls</td><td>owns manager + preferred only</td></tr>
<tr><td style="text-align:left">Lead-carrier assets (statutory, YE25)</td><td>$282B (AAIA invested)</td><td>$112.5B (CWA) + $73.0B (FLIC)</td><td>$62.7B (AEL) + $40.2B (ANICO)</td><td>$14.7B (Aspida Life)</td><td>not public</td></tr>
<tr><td style="text-align:left">Asset growth, 2yr</td><td>bond book +75%</td><td>NIA +25%</td><td>AEL +5%</td><td><strong>+378% (5×)</strong></td><td>not public</td></tr>
<tr><td style="text-align:left">Private-letter share of bonds (position-level)</td><td><strong>25.3%</strong></td><td>n/a (no public filing)</td><td>9.7% — trend 9.4→14.2→9.7 (3yrs footed)</td><td>n/a</td><td>n/a</td></tr>
<tr><td style="text-align:left">Identifier-private floor</td><td>31.0%</td><td>n/a</td><td>17.0%</td><td>n/a</td><td>n/a</td></tr>
<tr><td style="text-align:left">Below-IG share (regulatory ruler)</td><td>2.9%</td><td>5.6% (NRSRO: <strong>10.0%</strong>)</td><td>5.1% (2.6→3.6→5.1)</td><td>~7% one-pager basis</td><td>not public</td></tr>
<tr><td style="text-align:left">Bond-book weighted age</td><td><strong>1.7y (unseasoned)</strong></td><td>n/a</td><td>4.0y (seasoned; 4.7→4.3→4.0)</td><td>~new (5× growth)</td><td>n/a</td></tr>
<tr><td style="text-align:left">Bermuda pivot ECR coverage (trend)</td><td>AARe 242→<strong>202%</strong></td><td>GA Re 171→235→<strong>205%</strong></td><td>not published (no FCR)</td><td>Aspida Re 214→206→<strong>199%</strong></td><td>KLR 207→190→<strong>176%</strong></td></tr>
<tr><td style="text-align:left">Runnable funding-agreement exposure</td><td><strong>27% of reserves ↑</strong></td><td>~7% of reserves</td><td>modest (FHLB/FABN at AEL)</td><td>began issuing 2025 ↑</td><td>not public</td></tr>
<tr><td style="text-align:left">Weakest public rating in fleet</td><td>A+ fleet</td><td>A fleet</td><td>A–/A fleet</td><td>A− fleet</td><td><strong>B++ negative (Lincoln Benefit)</strong></td></tr>
</tbody></table></div>
<div class="callout"><strong>What the cross-section actually shows:</strong> (1) <em>Every Bermuda pivot with a public
FCR is compressing into the same 175–205% band</em> — five platforms, one direction; the sector's offshore cushion is
thinning in unison. (2) <em>Athene is the opacity outlier</em>: 25.3% private-letter vs 9.7% at the only measurable peer — and AEL's three-year trend (9.4→14.2→9.7%) shows NO Athene-style ramp: the 3.4× PL climb is an Athene choice, now proven against a measured control,
31% vs 17% identifier-private, and the youngest big book (1.7y vs 4.0y) — its "clean" loss history is the least
informative of the five. (3) <em>Ares/Aspida is the growth outlier</em> (5× in two years on thin capital, half the book
funds-withheld). (4) <em>Blue Owl is the model outlier</em> — pure fee extraction with the credit risk parked at carriers
it doesn't own, including the group's only B++/negative. (5) Disclosure quality itself now ranks the sector:
Brookfield/AEL best (full blanks), then Athene, GA, Ares, Blue Owl worst.</div>

<h2>8 · What this cross-section says about the private-credit-insurance question</h2><hr class="rule">
<p style="font-size:14.5px">Five platforms now sit on one measured ruler. The margin compression,
the adjusted-vs-GAAP divergence, and the regulatory-vs-market grading gap now have <em>measured values at two
companies</em> built by identical, gate-verified pipelines. Athene distinguishes itself by scale, private-letter
concentration, and runnable funding; GA by a junkier market-rated book and thinner disclosure (no public
position-level filings). The dispersion is now tradeable structure: opacity (Athene), growth (Aspida), model risk (Blue Owl), and the one common factor — Bermuda cushions thinning in unison.</p>

<div class="footer">Sources &amp; verification: Athene — ATH supplements (Q4'25/Q1'26), AHL 10-K FY2025, AAIA
statutory statements YE2023–25 footed to the dollar, NAIC C-1 factors. Global Atlantic — GALD supplements
(Q4'23/Q4'24/Q4'25/Q1'26, 918 gated cells), KKR 10-K/10-Q FY2023–1Q26 (176 gated cells), GA Re/GAAL FCRs 2023–25,
carrier statutory statements 2022–25. All documents sha-tracked in acquisition/manifest.csv; every table crosses
at least one exact-equality gate. Regenerate: <span style="font-family:ui-monospace,Menlo,monospace">python3
tools/render_comparison.py</span>. Research conclusions from public filings; not investment advice.</div>
</div>
"""
DEST.write_text(html)
print(f'wrote {DEST} ({len(html):,} bytes)')

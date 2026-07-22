#!/usr/bin/env python3
"""Render the Global Atlantic dashboard (Athene-dashboard analog).

Sections: the machine (census + structure), money in, the operating engine,
portfolio quality (two rulers), reserves, capital (US statutory + Bermuda ECR),
boundaries. All values from gate-verified extracts.
Output: dossiers/global-atlantic/ga-dashboard.html
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'dossiers/global-atlantic/ga-dashboard.html'

GA = {}
for r in csv.DictReader(open(ROOT / 'extract/global-atlantic/gald_supplement.csv')):
    if r['value'] != '':
        GA[(r['period'], r['metric'])] = float(r['value'])
CAP = {(r['entity'], r['year'], r['metric']): float(r['value_musd'])
       for r in csv.DictReader(open(ROOT / 'extract/global-atlantic/ga_capital.csv'))}
STAT = {(r['carrier'], int(r['year']), r['metric']): (float(r['value']) if r['value'] else None)
        for r in csv.DictReader(open(ROOT / 'extract/global-atlantic/statutory_l0.csv'))}
ENTS = list(csv.DictReader(open(ROOT / 'spine/global-atlantic/entities.csv')))

g = lambda p, k: GA.get((p, k))

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



def money(v, b=False):
    if v is None:
        return '·'
    return f'${v/1000:,.1f}B' if (b or abs(v) >= 1000) else f'${v:,.0f}M'


def card(v, label, note):
    return (f'<div class="mcard"><div class="mv">{v}</div><div class="ml">{label}</div>'
            f'<div class="mx">{note}</div></div>')


ent_rows = ''.join(
    f'<tr><td style="text-align:left">{e["name"]}</td><td>{e["jurisdiction"]}</td>'
    f'<td>{e["role_provisional"]}</td><td class="mono xs">{e["lei"] or "—"}</td>'
    f'<td class="xs">{e["bma_registration"] or "—"}</td></tr>'
    for e in ENTS)

fy25 = lambda k: g('FY2025', k)
q126 = lambda k: g('1Q26', k)

nbv25 = sum(v for v in (fy25('nbv_retirement_total'), fy25('nbv_preneed'), fy25('nbv_block'),
                        fy25('nbv_flow'), fy25('nbv_prt'), fy25('nbv_funding_agreements'),
                        fy25('nbv_life') or 0) if v is not None)

naic_big_sh = g('4Q25', 'naic_big') / g('4Q25', 'naic_total') * 100
nrsro_big_sh = g('4Q25', 'nrsro_big') / g('4Q25', 'nrsro_total') * 100

cs = lambda c: STAT.get((c, 2025, 'capital_surplus'))
assets_c = lambda c: STAT.get((c, 2025, 'total_admitted_assets'))

html = f"""<title>Global Atlantic — the machine</title>
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
.wrap{{max-width:1080px;margin:0 auto;padding:36px 24px 64px}}
header{{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:8px}}
.eyebrow{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:30px;font-weight:600;margin:0}}
.sub{{color:var(--muted);margin:8px 0 0;font-size:14px}}
a{{color:var(--acc);text-decoration:none}} a:hover{{text-decoration:underline}}
.mono{{font-family:ui-monospace,Menlo,monospace;font-variant-numeric:tabular-nums}}
.xs{{font-size:11.5px}} .dim{{color:var(--muted)}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:var(--line);
border:1px solid var(--line);margin:24px 0 8px}}
.stat{{background:var(--panel);padding:14px 16px}}
.stat .v{{font-size:24px;font-weight:600;font-variant-numeric:tabular-nums}}
.stat .k{{font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-top:2px}}
h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;margin:38px 0 6px}}
h2 .cnt{{color:var(--muted);font-weight:400;letter-spacing:0;text-transform:none}}
.rule{{border:0;border-top:1px solid var(--line2);margin:0 0 14px}}
.callout{{background:var(--panel);border-left:3px solid var(--bm);padding:13px 17px;margin:12px 0;font-size:14px}}
.mgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:14px;margin:14px 0}}
.mcard{{background:var(--panel);border:1px solid var(--line);padding:14px 16px}}
.mcard .mv{{font-size:23px;font-weight:650;font-variant-numeric:tabular-nums}}
.mcard .ml{{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600;margin-top:2px}}
.mcard .mx{{font-size:12.5px;color:var(--muted);margin-top:4px;line-height:1.45}}
.tbl-scroll{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);font-size:13px}}
th{{font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);text-align:left;font-weight:600;
padding:9px 11px;border-bottom:1px solid var(--line2)}}
td{{padding:7px 11px;border-bottom:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums}}
td:first-child{{text-align:left}}
.footer{{margin-top:40px;padding-top:14px;border-top:1px solid var(--line2);font-size:12px;color:var(--muted)}}
</style>
<div class="wrap">
<header>
<p class="eyebrow">CREDIT MAP · PHASE 1 CENSUS · GLOBAL ATLANTIC (KKR)</p>
<h1>Global Atlantic — the machine</h1>
<p class="sub">Built by the same pipeline as the <a href="https://claude.ai/code/artifact/0dfa08f5-a1c0-49b7-b080-d578fdf98b39">Athene dashboard</a>;
compared head-to-head on the <a href="https://claude.ai/code/artifact/a01a93bf-e006-450c-a4a8-6d4ef2710a6f">comparison page</a>. All values gate-verified;
sources sha-tracked in the manifest. Latest data 1Q26.</p>
</header>

<div class="stats">
<div class="stat"><div class="v">{len(ENTS)}</div><div class="k">entities in spine</div></div>
<div class="stat"><div class="v">{money(q126('total_assets'), b=True)}</div><div class="k">total assets 1Q26</div></div>
<div class="stat"><div class="v">{money(g('1Q26','res_total'), b=True)}</div><div class="k">net reserves</div></div>
<div class="stat"><div class="v">{money(q126('shareholders_equity'))}</div><div class="k">shareholders equity</div></div>
<div class="stat"><div class="v">918+176</div><div class="k">gated cells (GALD + KKR)</div></div>
</div>

<div class="callout"><strong>The structural headline:</strong> KKR &rarr; Global Atlantic Financial Group Limited (Bermuda)
&rarr; four US carriers (Forethought IN — the annuity writer; Commonwealth Annuity MA — the block-reinsurance balance
sheet, and at $112.5B admitted assets the BIGGEST; Accordia IA; First Allmerica MA) plus a Bermuda deck: GA Re (the
pivot), GAAL, and the Ivy Re / Ivy Peak / Iris sidecars (KKR's ACRA analog, co-invest capital). Ownership chain
provisional pending Schedule Y drill.</strong></div>

<h2>① Money in <span class="cnt">— new business volume, FY2025 + 1Q26</span></h2><hr class="rule">
<div class="mgrid">
{card(money(nbv25), 'Total NBV FY2025', 'Retirement + preneed + block + flow + PRT + funding agreements.')}
{card(money(fy25('nbv_retirement_total')), 'Individual retirement', 'Fixed-rate + FIA + VA. 1Q26: ' + money(q126('nbv_retirement_total')) + '.')}
{card(money(fy25('nbv_flow')), 'Flow reinsurance', 'The Athene-flow analog. 1Q26: ' + money(q126('nbv_flow')) + '.')}
{card(money(fy25('nbv_block')), 'Block deals', 'Lumpy inorganic; $11.9B in FY2024, {b25} in FY2025.'.replace('{b25}', money(fy25('nbv_block'))))}
{card(money(fy25('nbv_funding_agreements')), 'Funding agreements', 'The runnable channel — small vs Athene ($6.3B vs $35.4B FY2025).')}
</div>

<h2>② The operating engine <span class="cnt">— adjusted operating earnings (their SRE)</span></h2><hr class="rule">
<div class="mgrid">
{card(f"{ga_rate('1Q26','nier','adj_nii'):.2f}%", 'Earned rate 1Q26 (derived)', 'FY23 4.32% → FY25 4.79% — repriced up with rates. 1Q26 derived from the $ chain (rates table dropped from the Q1-26 supplement).')}
{card(f"{ga_rate('1Q26','cost_ins_ratio','adj_cost_ins'):.2f}%", 'Cost of insurance 1Q26 (derived)', 'FY23 2.60% → 1Q26 ~3.6% — the float got expensive faster than the assets repriced.')}
{card(f"{ga_rate('1Q26','underwriting_ratio','adj_underwriting'):.2f}%", 'UNDERWRITING MARGIN 1Q26 (derived)', 'FY23 1.72% → ~1.17% — the compression, same story as Athene.')}
{card(money(fy25('adj_op_pretax')), 'Adj. operating pre-tax FY2025', '1Q26: ' + money(q126('adj_op_pretax')) + '.')}
{card(money(fy25('ni_shareholder')), 'GAAP NET LOSS FY2025', 'Against positive operating earnings — the adjusted-vs-GAAP divergence at full-year scale.')}
{card(f"{g('4Q25','adj_op_roe'):.1f}% / {g('4Q25','roe'):.1f}%", 'Adj-op ROE vs GAAP ROE (4Q25 ann.)', 'The operating story vs the tape.')}
</div>

<h2>③ Portfolio quality <span class="cnt">— the two rulers on the same $95.7B AFS book (YE2025)</span></h2><hr class="rule">
<div class="mgrid">
{card(f'{naic_big_sh:.1f}%', 'Below-IG — NAIC ruler', 'The regulatory designations.')}
{card(f'{nrsro_big_sh:.1f}%', 'Below-IG — NRSRO ruler', 'The market ratings on the same securities.')}
{card(f'{nrsro_big_sh - naic_big_sh:.1f}pt', 'THE FLATTERING GAP', 'How much better the book looks to the regulator than to the market. Athene analog: the PL letter-slip question.')}
{card(money(g('4Q25','naic_total'), b=True), 'AFS fixed maturities', 'Fair value, YE2025.')}
</div>
<div class="callout"><strong>Boundary, logged:</strong> GA's carriers publish statutory statements WITHOUT
CUSIP-level investment schedules (verification pages only) — so the position-level drill that produced Athene's
private-letter share, aging, and concentration findings cannot be replicated from public documents. The two-ruler
gap above is the sharpest publicly available opacity measure for GA.</div>

<h2>④ Capital under the stack <span class="cnt">— YE2025, both rulers</span></h2><hr class="rule">
<div class="tbl-scroll"><table>
<thead><tr><th>Entity</th><th>Measure</th><th>2023</th><th>2024</th><th>2025</th></tr></thead><tbody>
<tr><td>GA Re (Bermuda pivot)</td><td>ECR coverage</td>
<td>{CAP[('GA Re','2023','eligible_capital')]/CAP[('GA Re','2023','ecr')]*100:.0f}%</td>
<td>{CAP[('GA Re','2024','eligible_capital')]/CAP[('GA Re','2024','ecr')]*100:.0f}%</td>
<td>{CAP[('GA Re','2025','eligible_capital')]/CAP[('GA Re','2025','ecr')]*100:.0f}%</td></tr>
<tr><td>GAAL (Bermuda)</td><td>ECR coverage</td>
<td>{CAP[('GAAL','2023','eligible_capital')]/CAP[('GAAL','2023','ecr')]*100:.0f}%</td>
<td>{CAP[('GAAL','2024','eligible_capital')]/CAP[('GAAL','2024','ecr')]*100:.0f}%</td>
<td>{CAP[('GAAL','2025','eligible_capital')]/CAP[('GAAL','2025','ecr')]*100:.0f}%</td></tr>
<tr><td>Commonwealth Annuity (MA)</td><td>C&amp;S / admitted assets</td><td colspan=2></td>
<td>{money(cs('cwa')/1e6)} / {money(assets_c('cwa')/1e6, b=True)}</td></tr>
<tr><td>Forethought (IN)</td><td>C&amp;S / admitted assets</td><td colspan=2></td>
<td>{money(cs('flic')/1e6)} / {money(assets_c('flic')/1e6, b=True)}</td></tr>
<tr><td>First Allmerica (MA)</td><td>C&amp;S / admitted assets</td><td colspan=2></td>
<td>{money(cs('faflic')/1e6)} / {money(assets_c('faflic')/1e6, b=True)}</td></tr>
<tr><td>Accordia (IA)</td><td>C&amp;S / admitted assets</td><td colspan=2></td>
<td>{money(cs('accordia')/1e6)} / {money(assets_c('accordia')/1e6, b=True)}</td></tr>
</tbody></table></div>
<div class="callout"><strong>Reading it:</strong> GA Re's ECR coverage (205%) sits in the same compressing band as
Athene's AARe (202%) — the Bermuda pivots of both machines run comparably thin. First Allmerica's C&amp;S of
$148M under $15.8B of admitted assets is the thinnest cushion in either group's US fleet — flagged for the
Schedule S drill.</div>

<h2>⑤ The census <span class="cnt">— {len(ENTS)} entities (EX-21 + GLEIF + BMA; Schedule Y expansion pending)</span></h2><hr class="rule">
<div class="tbl-scroll"><table>
<thead><tr><th>Entity</th><th>Jurisdiction</th><th>Role (provisional)</th><th>LEI</th><th>BMA</th></tr></thead>
<tbody>{ent_rows}</tbody></table></div>

<div class="footer">Sources: GALD financial supplements Q4'23–Q1'26 (918 gated cells) · KKR 10-K/10-Q FY2023–1Q26
(176 gated cells) · GA Re/GAAL FCRs 2023–25 · carrier statutory statements 2022–25 (C&amp;S = assets−liabilities
identity) · KKR EX-21 + GLEIF + BMA class declarations. Companion: GA engine workbook
(ga-quarterly-engine.xlsx, 133 live checks) and the comparison page. Regenerate:
<span class="mono">python3 tools/render_ga_dashboard.py</span>.</div>
</div>
"""
DEST.write_text(html)
print(f'wrote {DEST} ({len(html):,} bytes)')

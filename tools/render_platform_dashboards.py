#!/usr/bin/env python3
"""Render Brookfield / Ares / Blue Owl platform dashboards (one template, three
pages) from the gated cross-section extracts. Same conventions as the Athene
and GA dashboards. Outputs: dossiers/<platform>/<platform>-dashboard.html
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAP = list(csv.DictReader(open(ROOT / 'extract/cross-section/capital.csv')))
STAT = list(csv.DictReader(open(ROOT / 'extract/cross-section/statutory_l0.csv')))
AEL = json.load(open(ROOT / 'extract/cross-section/ael_bond_features.json'))

CSS = """<style>
:root{--bg:#F6F5F1;--panel:#FFF;--ink:#22271F;--muted:#6E756D;--line:#E3E1D8;--line2:#CFCCC0;
--us:#0F6E56;--us-bg:#E4F3EC;--bm:#A3431D;--bm-bg:#F9ECE5;--acc:#185FA5;--warn:#BA7517;--warn-bg:#FAEEDA}
@media (prefers-color-scheme: dark){:root{--bg:#15191B;--panel:#1D2325;--ink:#E7E9E3;--muted:#8F978F;
--line:#2B3234;--line2:#3A4245;--us:#5DCAA5;--us-bg:#0C3A2D;--bm:#F0997B;--bm-bg:#43200F;--acc:#85B7EB;--warn:#D9A54A;--warn-bg:#3A2B10}}
:root[data-theme="dark"]{--bg:#15191B;--panel:#1D2325;--ink:#E7E9E3;--muted:#8F978F;--line:#2B3234;--line2:#3A4245;
--us:#5DCAA5;--us-bg:#0C3A2D;--bm:#F0997B;--bm-bg:#43200F;--acc:#85B7EB;--warn:#D9A54A;--warn-bg:#3A2B10}
:root[data-theme="light"]{--bg:#F6F5F1;--panel:#FFF;--ink:#22271F;--muted:#6E756D;--line:#E3E1D8;--line2:#CFCCC0;
--us:#0F6E56;--us-bg:#E4F3EC;--bm:#A3431D;--bm-bg:#F9ECE5;--acc:#185FA5;--warn:#BA7517;--warn-bg:#FAEEDA}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:15px/1.55 "Avenir Next","Segoe UI",system-ui,sans-serif;margin:0}
.wrap{max-width:1020px;margin:0 auto;padding:36px 24px 64px}
header{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:8px}
.eyebrow{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
h1{font-size:29px;font-weight:600;margin:0}
.sub{color:var(--muted);margin:8px 0 0;font-size:14px}
a{color:var(--acc);text-decoration:none} a:hover{text-decoration:underline}
h2{font-size:13px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;margin:36px 0 6px}
.rule{border:0;border-top:1px solid var(--line2);margin:0 0 14px}
.callout{background:var(--panel);border-left:3px solid var(--bm);padding:13px 17px;margin:12px 0;font-size:14px}
.mgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin:14px 0}
.mcard{background:var(--panel);border:1px solid var(--line);padding:14px 16px}
.mcard .mv{font-size:22px;font-weight:650;font-variant-numeric:tabular-nums}
.mcard .ml{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600;margin-top:2px}
.mcard .mx{font-size:12.5px;color:var(--muted);margin-top:4px;line-height:1.45}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);font-size:13px}
th{font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);text-align:left;font-weight:600;padding:9px 11px;border-bottom:1px solid var(--line2)}
td{padding:7px 11px;border-bottom:1px solid var(--line);text-align:right;font-variant-numeric:tabular-nums}
td:first-child{text-align:left}
.footer{margin-top:38px;padding-top:14px;border-top:1px solid var(--line2);font-size:12px;color:var(--muted)}
</style>"""


def card(v, l, n):
    return f'<div class="mcard"><div class="mv">{v}</div><div class="ml">{l}</div><div class="mx">{n}</div></div>'


def cap_rows(platform):
    out = {}
    for r in CAP:
        if r['platform'] == platform:
            out[(r['entity'], r['year'], r['metric'])] = float(r['value_kusd'])
    return out


def stat_rows(platform):
    out = {}
    for r in STAT:
        if r['platform'] == platform:
            out[(r['carrier'], int(r['year']), r['metric'])] = float(r['value_kusd']) if 'value_kusd' in r else float(r.get('value', 0))
    return out


# statutory CSV columns: platform,carrier,year,metric,value(...),source — normalize
STAT_N = {}
for r in STAT:
    val_key = 'value_kusd' if 'value_kusd' in r and r['value_kusd'] else 'value'
    STAT_N[(r['platform'], r['carrier'], int(r['year']), r['metric'])] = float(r[val_key])


def s(pl, c, y, m):
    return STAT_N.get((pl, c, y, m))


def page(platform, title, eyebrow, verdict, cards, tables, boundaries, sources):
    return f"""<title>{title}</title>
{CSS}
<div class="wrap">
<header><p class="eyebrow">{eyebrow}</p><h1>{title}</h1>
<p class="sub">Built by the credit-map pipeline (same conventions as the
<a href="https://claude.ai/code/artifact/0dfa08f5-a1c0-49b7-b080-d578fdf98b39">Athene</a> and
<a href="https://claude.ai/code/artifact/b68af7a4-dc57-409b-a0d7-a31da4e1b3dc">Global Atlantic</a> dashboards;
head-to-head on the <a href="https://claude.ai/code/artifact/a01a93bf-e006-450c-a4a8-6d4ef2710a6f">comparison page</a>).
All values from sha-tracked public filings. As of 2026-07-22.</p></header>
<div class="callout"><strong>The read:</strong> {verdict}</div>
<h2>The numbers</h2><hr class="rule"><div class="mgrid">{cards}</div>
{tables}
<h2>Boundaries, logged</h2><hr class="rule"><div class="callout" style="border-left-color:var(--warn)">{boundaries}</div>
<div class="footer">{sources}</div>
</div>"""


# ---------- Brookfield ----------
c = cap_rows('brookfield')
bf_cards = (
    card(f"${AEL['total']/1e9:.1f}B", 'AEL bond book (footed ×3 years)',
         'YE2023/24/25 ALL foot TO THE DOLLAR through the Athene parser (5,199 / 5,203 / 5,692 positions; zero exceptions in 2023-24) — the only peer with the full position-level drill.')
    + card(' → '.join(f"{AEL['years'][y]['pl_share_pct']}%" for y in ('2023','2024','2025')), 'AEL PL share, 3-year trend',
           'NO Athene-style ramp (Athene: 15.6% → 25.3% over the same window). The PL climb is an Athene choice, now proven against a measured control.')
    + card(' → '.join(f"{AEL['years'][y]['below_ig_pct']}%" for y in ('2023','2024','2025')), 'AEL below-IG trend (NAIC)',
           'Creeping up under Brookfield — the one deteriorating dial on this book.')
    + card('$423M = 1.0%', 'Top concentration: BROOKFIELD SECURITIZATION CFO', 'An affiliate-originated structure at #1 — the same fingerprint as Athene\'s AP Grange, at 1/9th the weight (Athene top name: 2.3% of book).')
    + card(f"{AEL['src']['PL']/AEL['total']*100:.1f}%", 'AEL private-letter share',
           'vs Athene 25.3% — Athene runs 2.6× the PL concentration of its closest structural peer.')
    + card(f"{(AEL['ids']['ppn']+AEL['ids'].get('noid',0))/AEL['total']*100:.1f}%", 'AEL identifier-private floor', 'vs Athene 31.0%.')
    + card(f"{sum(v for k,v in AEL['naic'].items() if k in '3456')/AEL['total']*100:.1f}%", 'AEL below-IG (NAIC)', 'vs Athene 2.9% — junkier designations, but far more publicly rated (FE 71.3% vs 49.3%).')
    + card(f"{AEL['wavg_age']:.1f}y", 'AEL weighted holding age',
           'vs Athene 1.7y — a SEASONED book, already inside the loss-emergence window.')
    + card(f"${s('brookfield','ael',2025,'total_admitted_assets')/1e9:.1f}B / ${s('brookfield','ael',2025,'capital_surplus')/1e9:.2f}B", 'AEL assets / C&S YE2025',
           f"C&S fell from ${s('brookfield','ael',2023,'capital_surplus')/1e9:.2f}B at YE2023 while assets grew — leverage rising.")
    + card(f"${s('brookfield','anico',2025,'total_admitted_assets')/1e9:.1f}B", 'American National assets YE2025',
           f"C&S ${s('brookfield','anico',2025,'capital_surplus')/1e9:.2f}B.")
    + card('$642M → $658M', 'BNT quarterly gross spread (DOE basis, 1Q25→1Q26)',
           'Cost of funds rose every quarter ($904M → $1,028M) — the same repricing race as Athene/GA, now measured at a third platform. Full chain in the engine workbook (87 checks).')
    + card('−$602M vs +$438M', 'BNT 1Q26: GAAP net loss vs DOE',
           'The adjusted-vs-GAAP divergence, quarterly: GAAP −$282M/+$21M/−$602M in 1Q25/4Q25/1Q26 while DOE held ~$437M every single quarter. A metronome over a tape.')
)
bf_boundaries = ('BNT/BWS is a foreign private issuer (20-F/6-K); its quarterly supplement series only began 1Q25. '
                 'North End Re and Freestone Re publish audited FS via the BMA but NO Financial Condition Reports — '
                 'Bermuda coverage ratios are not publicly computable for Brookfield (unlike every other platform here). '
                 'North End Re (Cayman) SPC publishes nothing. AEL Re Bermuda appears wound down after 2023. '
                 'The BN/BNT merger (approved 2026-07-16) will likely END standalone BNT reporting — documents archived now.')
bf_html = page('brookfield', 'Brookfield Wealth Solutions — the machine', 'CREDIT MAP · CROSS-SECTION · BROOKFIELD (BNT)',
               'The only peer whose lead carrier (AEL, Iowa) publishes FULL statutory statements — so the Athene-grade '
               'position-level drill actually ran, and footed exactly. AEL is older, more publicly rated, and less '
               'private-letter-dependent than Athene, but its designations run junkier and its surplus is shrinking '
               'while assets grow. Ownership: Brookfield owns its insurers outright — the Apollo/KKR model.',
               bf_cards, '', bf_boundaries,
               'Sources: AEL statutory annual statements 2023–2025 + 1Q26 (american-equity.com; Schedule D parsed by '
               'tools/parse_sched_d.py, gates exact) · ANICO statutory 2023–2025 · BNT 20-Fs FY2023–25 + 6-K 1Q26 · '
               'BWS supplements 1Q25–1Q26 · North End Re / Freestone Re audited FS (BMA). sha-tracked in manifest. '
               'Engine workbook: dossiers/brookfield/bnt-quarterly-engine.xlsx (quarterly + FY tabs, 87 live checks).')

# ---------- Ares ----------
ar_cards = (
    card('$3.1B → $14.7B', 'Aspida Life admitted assets 2023→2025',
         '≈5× in two years — the fastest-growing balance sheet in the cross-section (EY-audited statutory FS via EDGAR).')
    + card('$635M', 'Aspida Life C&S YE2025', 'Under $14.7B of assets; cumulative statutory net losses $159M (2022–24, KBRA).')
    + card('199%', 'Aspida Re ECR coverage YE2025', '214% → 206% → 199% — the same compressing band as AARe (202%), GA Re (205%), Kuvare Life Re (176%).')
    + card('398%', 'Aspida Life RBC (CAL, 2024)', 'Down from 480% in 2023 (KBRA). Both rulers compressing while assets 5×.')
    + card('$25.9B', 'AIS-managed AUM for Aspida', 'Of which $16.9B sub-advised by Ares vehicles (ares-10k-fy2025) — the manager-owner loop, Apollo-style.')
    + card('49.7%', 'Invested assets restricted', 'Under funds-withheld reinsurance (audited statutory notes) — half the balance sheet works for counterparties.')
    + card('−$48.8M → −$36.7M → −$0.01M', 'Net loss trend (statutory)',
           'Three straight loss years shrinking to exact breakeven; C&S growth is all capital contributions. Full chain in the engine workbook (33 checks).')
    + card('61%', 'Ceded share of gross annuity reserves YE2025',
           '21% → 58% → 61%: gross reserves $12.8B but net only $5.1B — most of the machine now runs through reinsurance counterparties (incl. Aspida Re, its own Bermuda affiliate).')
)
ar_boundaries = ('No public NAIC blanks (no Schedule D detail) — the audited statutory FS embedded in EDGAR RILA filings '
                 'are the public substitute. No consolidated Aspida Holdings GAAP statements (one-pager only: $31B assets, '
                 '$2.4B non-GAAP equity at 3/31/26). Aspida Re Cayman Ltd (rated Jan 2026) publishes nothing — a growing '
                 'entity entirely outside public view. No quarterly cadence anywhere: Ares 10-Qs carry zero Aspida data. '
                 'Aspida began issuing FUNDING AGREEMENTS in 2025 — the runnable channel opens.')
ar_html = page('ares', 'Ares / Aspida — the machine', 'CREDIT MAP · CROSS-SECTION · ARES (ASPIDA)',
               'The hypergrowth machine: assets 5× in two years on thin, falling-ratio capital, half the balance sheet '
               'funds-withheld to counterparties, both capital rulers compressing, and the thinnest public disclosure of '
               'any platform with an SEC-registered product. Ownership: Ares manages and fund-controls Aspida — '
               'the manager IS the shareholder controller (BMA term), one step more entangled than the Apollo model.',
               ar_cards, '', ar_boundaries,
               'Sources: EY-audited statutory FS FY2022–25 (EDGAR 485BPOS/N-4, CIK 1934234) · Aspida Re FCRs FY2021–25 '
               '(aspidare.bm) · Aspida Re GAAP FS (BMA) · ares-10k-fy2025 · KBRA/AM Best actions · group one-pager 3/31/26. '
               'Engine workbook: dossiers/ares/aspida-annual-engine.xlsx (FY2023–25, 33 live checks).')

# ---------- Blue Owl ----------
kc = cap_rows('blueowl')
klr_cov = {y: kc[('Kuvare Life Re', y, 'eligible_capital')] / kc[('Kuvare Life Re', y, 'ecr')] * 100 for y in ('2023', '2024', '2025')}
ow_cards = (
    card(f"{klr_cov['2025']:.0f}%", 'Kuvare Life Re ECR coverage YE2025',
         f"{klr_cov['2023']:.0f}% → {klr_cov['2024']:.0f}% → {klr_cov['2025']:.0f}% — compressing, the fifth Bermuda pivot doing the same thing.")
    + card('$842M + $250M', 'What Blue Owl actually bought', 'KAM (the asset manager, 100%, July 2024) + a $250M preferred in Kuvare UK Holdings marked $267M → $304M. It owns the MANAGER, not the insurers.')
    + card('$19.2B', 'IG-credit AUM at Blue Owl', 'The KAM-driven strategy; management fees $27.9M → $67.6M in one year — the fee engine the deal was for.')
    + card('$40M', 'GILICO surplus notes held by Kuvare Life Re', '6% due 2049 + 5.5% due 2051 — capital circularity inside the group, flagged.')
    + card('−$175M → −$64M → $172M', 'KLR shareholder equity 2022→2025',
           'The Bermuda pivot ran NEGATIVE GAAP equity through YE2023 and holds $172M against $9.8B of assets (1.8%) at YE2025. Full statements in the engine workbook (20 checks).')
    + card('$80M', 'Misprint found in KLR 2025 FS',
           'FY2024 operating-cash comparative prints $1,601.2M where its own components and restatement note prove $1,681.2M — caught by the footing gate, logged as a finding.')
)
ow_boundaries = ('The three US carriers (Guaranty Income LA, United Life IA, Lincoln Benefit NE) publish NO statutory '
                 'statements — only ALIRT derivatives and reinsurance summaries; United Life\'s site is bot-walled. '
                 'Lincoln Benefit carries AM Best B++ with a NEGATIVE outlook (2024) — the weakest rating in this entire '
                 'cross-section. No Kuvare GAAP statements exist publicly. Blue Owl\'s stake is a Level-III fair-value '
                 'preferred — its marks are the manager\'s own. Bermuda (Kuvare Life Re FCRs FY22–25 + audited FS, and '
                 'Kuvare Bermuda Re) is the only transparency window.')
ow_html = page('blueowl', 'Blue Owl / Kuvare — the machine', 'CREDIT MAP · CROSS-SECTION · BLUE OWL (KUVARE)',
               'The purest fee-machine model: Blue Owl owns the asset manager and a preferred stake, the insurers are '
               'AUM clients, and the credit risk lives with policyholders and a B++/negative-rated carrier while the '
               'manager collects. The public window is Bermuda only — and its pivot\'s coverage is compressing like '
               'everyone else\'s.',
               ow_cards, '', ow_boundaries,
               'Sources: Kuvare Life Re FCRs FY2022–25 (kuvare.com) + audited FS FY2023–25 (BMA) · Kuvare Bermuda Re FS · '
               'owl-10k-fy2025 (KAM acquisition + preferred marks) · GILICO/LBL disclosure pages · AM Best/KBRA actions. '
               'Engine workbook: dossiers/blueowl/klr-annual-engine.xlsx (FY2022–25, LDTI-restated basis, 20 live checks).')

for name, html in (('brookfield', bf_html), ('ares', ar_html), ('blueowl', ow_html)):
    d = ROOT / f'dossiers/{name}'
    d.mkdir(exist_ok=True)
    (d / f'{name}-dashboard.html').write_text(html)
    print(f'wrote dossiers/{name}/{name}-dashboard.html ({len(html):,} bytes)')

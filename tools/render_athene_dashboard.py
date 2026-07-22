#!/usr/bin/env python3
"""Render dossiers/athene/entity-dashboard.html from spine + manifest CSVs."""
import csv, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ents = list(csv.DictReader(open(ROOT / 'spine/athene/entities.csv')))
docs = list(csv.DictReader(open(ROOT / 'acquisition/manifest.csv')))

ROLE_LABEL = {
    'insurer': 'US insurer', 'reinsurer': 'Reinsurer', 'holdco': 'Holdco',
    'manager': 'Manager', 'manager-parent': 'Manager', 'fund': 'Fund',
    'affiliated-insurer': 'Affiliated', 'other': 'Other',
}
ROLE_CLASS = {
    'insurer': 'r-us', 'reinsurer': 'r-re', 'holdco': 'r-hc', 'manager': 'r-mg',
    'manager-parent': 'r-mg', 'fund': 'r-fd', 'affiliated-insurer': 'r-af', 'other': 'r-ot',
}

def e(s): return html.escape(s or '')

rows = []
for r in ents:
    role = r['role_provisional']
    ids = []
    if r['naic_cocode']: ids.append(f"NAIC {e(r['naic_cocode'])}")
    if r['fein']: ids.append(f"FEIN {e(r['fein'])}")
    idcell = '<br>'.join(ids)
    lei = f"<span class=\"mono dim\" title=\"LEI\">{e(r['lei'])}</span>" if r['lei'] else ''
    pct = f" · {e(r['parent_pct'])}%" if r['parent_pct'] else ''
    parent = f"{e(r['parent_entity'])}{pct}" if r['parent_entity'] else '<span class="dim">—</span>'
    rows.append(
        f"<tr data-role=\"{e(role)}\" data-q=\"{e((r['name']+' '+r['jurisdiction']+' '+r['notes']+' '+r['parent_entity']+' '+r['naic_cocode']+' '+r['lei']+' '+r['fein']).lower())}\">"
        f"<td><div class=\"nm\">{e(r['name'])}</div><div class=\"note\">{e(r['notes'])}</div>{lei}</td>"
        f"<td>{e(r['jurisdiction'])}</td>"
        f"<td><span class=\"chip {ROLE_CLASS.get(role,'r-ot')}\">{ROLE_LABEL.get(role, role)}</span></td>"
        f"<td class=\"mono sm\">{idcell}</td>"
        f"<td class=\"sm\">{parent}</td>"
        f"<td class=\"mono xs dim\">{e(r['sources'].replace(';', ' · '))}</td>"
        f"</tr>"
    )
ROWS = '\n'.join(rows)

doc_rows = []
for d in docs:
    status = e(d['status'])
    flag = ' <span class="chip r-af">local only</span>' if 'local-only' in status else ''
    doc_rows.append(
        f"<tr><td><div class=\"nm\">{e(d['entity'])}</div><div class=\"note\">{e(d['doc_type'])} · {e(d['period'])}</div></td>"
        f"<td class=\"mono xs\" title=\"{e(d['sha256'])}\">{e(d['sha256'][:16])}…</td>"
        f"<td class=\"sm\">{e(d['published_date'])}{flag}</td>"
        f"<td><a href=\"{e(d['source_url'])}\">source</a></td></tr>"
    )
DOCS = '\n'.join(doc_rows)

n_total = len(ents)
n_coc = sum(1 for r in ents if r['naic_cocode'])
n_bm = sum(1 for r in ents if r['jurisdiction'] == 'Bermuda')
n_lei = sum(1 for r in ents if r['lei'])

claims = {r['metric']: r for r in csv.DictReader(open(ROOT / 'extract/athene/l0-claims.csv'))}

def fmt(metric):
    c = claims[metric]
    v = float(c['value'])
    if c['unit'] == 'PCT':
        return f'{v:.0f}%'
    b = v / 1e3 if c['unit'] == 'USD_M' else v / 1e9
    return f'${b:,.1f}B'

STEPS = [
 ('step1', '①', 'Money in', 'FY2025 flow — the top arrow of the picture',
  'New money entering the machine during 2025. Two cuts of the same year: by product (what kind of promise) and by owner (whose risk).', [
  ('gross_inflows_total', 'Gross inflows', 'All new money taken in during 2025: annuity sales, pension buyouts, funding agreements, assumed reinsurance. The real growth number — GAAP "premiums" were only $2.6B because deposits never touch the income statement.'),
  ('funding_agreement_deposits', 'of which funding agreements', 'Institutional borrowings dressed as insurance: FABN notes sold to bond investors, FHLB advances, repurchase-style agreements. $7.2B in 2023 → $35.4B in 2025.'),
  ('inflows_attrib_acra_nci', 'of which third-party (ADIP)', 'Inflows belonging to outside investors in the ACRA sidecars — not Athene shareholders. Apollo raised this capital and charges fees on it too.'),
  ('net_flows', 'Net flows', 'Inflows minus outflows (surrenders, withdrawals, maturities, benefit payments). The machine grew $47.9B net in one year.'),
 ]),
 ('step2', '②', 'What it becomes: reserves', 'the liability stock at the US insurer',
  'Money in accumulates as reserves — the obligation owed back to savers and institutions. A liability, not a stash: the money itself sits in the assets (⑤).', [
  ('net_reserve_liabilities', 'Net reserve liabilities', "Policyholder obligations net of reinsurance — the money Athene owes savers and institutions, at its own economic share. The denominator for every risk ratio."),
  ('funding_agreements_net_reserve_liab', 'of which runnable funding agreements', 'The slice of the reserves that can leave on a schedule: FABN, FABR, FHLB. 26.3% of net reserve liabilities, was 21.0% a year ago — the F4 signal.'),
  ('interest_sensitive_contract_liabilities', 'GAAP gross: interest-sensitive liabilities', 'The consolidated balance-sheet line holding the annuity and funding-agreement reserves before netting — the gross version of the same obligation.'),
 ]),
 ('step3', '③', 'The offshore door', 'AAIA → AARe, decomposed into its 29 treaties',
  'AAIA passes the economics of most of its book to one Bermuda counterparty, AARe, through reinsurance treaties. The cards are the statement control totals; the table below is those totals split into every individual treaty — and it foots.', [
  ('schedS_modco_reserve_total', 'ModCo reserves', "The dual-ledger number: liabilities kept legally on AAIA's books while the investment economics belong to AARe in Bermuda. $116.1B general account + $52.2B separate account."),
  ('schedS_reserve_credit_taken_total', 'Reserve credit taken', "Reserves removed from AAIA's balance sheet entirely because they are ceded outright (mostly funds-withheld coinsurance to AARe under 2024+ treaties)."),
  ('schedS_funds_withheld_total', 'Funds withheld', 'Assets AAIA physically keeps as collateral backing the coinsurance it ceded — legally held onshore, economically working for Bermuda.'),
  ('schedS_premiums_ceded_total', 'Premiums ceded FY2025', "The year's premium passed through to reinsurers. Every affiliate dollar of it went to one counterparty: AARe."),
 ]),
 ('step4', '④', 'The sidecars', 'ACRA — where third-party capital shares the risk',
  "Below AARe, the economics split between Athene's own account and the ACRA sidecars, capitalized ~one-third Athene / two-thirds ADIP (outside investors). ADIP holds equity — it shares profit AND losses; the $18.5B inflow slice in ① is the business its equity backs, not money it paid in. Note: ACRA files no public FCR — the sidecars sit outside the Bermuda sub-group's own disclosure.", [
  ('noncontrolling_interests', 'Noncontrolling interests (ADIP equity)', "Third-party (mostly ADIP) equity inside consolidated ACRA vehicles. Was $9.5B a year ago — up 59% in one year."),
  ('statcs_acra2a', 'ACRA statutory capital (2A; 1A adds $3.8B)', 'The sidecar cushions: ACRA 2A $6.6B + ACRA 1A $3.8B = ~$10.4B of capital, roughly two-thirds of it ADIP third-party money. Both Class C.'),
 ]),
 ('step5', '⑤', "The assets + Apollo's take", 'where the money is invested, and who gets paid',
  'The reserves are invested — physically held at AAIA (ModCo keeps assets onshore), managed and largely originated by Apollo, for fees at every touch.', [
  ('total_assets', 'Total assets', 'Athene Holding consolidated, everything on the books at 12/31/2025. Up from $363.3B a year earlier.'),
  ('total_investments', 'Total investments', 'The general-account investment portfolio at fair value: $192.6B AFS securities, $91.9B mortgage loans, plus trading, derivatives, funds withheld.'),
  ('net_invested_assets_incl_rp_vie', 'Net invested assets', "Management's economic measure: adds related-party holdings and consolidated-VIE look-through, counts ACRA at Athene's economic share."),
  ('apollo_management_fees', 'Management fees to Apollo', 'FY2025 base + sub-allocation + performance fees under the Fee Agreement (0.225% base on the first $103.4B, higher sub-allocation fees for higher-alpha asset classes). Plus $66M sub-advisory passthrough.'),
  ('net_investment_income', 'Net investment income', 'What the portfolio earned in FY2025 (net of the fees above; includes $2.1B earned from related-party investments).'),
 ]),
 ('step6', '⑥', 'The cushion', 'loss-absorbing capital under the whole stack',
  'The thin equity layer that eats losses before policyholders do — measured by two different rulers: US RBC (Iowa) and Bermuda BSCR (BMA). Both currently pass; both trends point the same direction.', [
  ('aaia_total_adjusted_capital', 'AAIA total adjusted capital', "The regulatory capital measure for the lead US insurer. Against a $1.09B authorized-control-level RBC, the ratio is ~871% ACL (~436% company-action level) — healthy on its face. The catch: RBC is measured AFTER the economics were ceded to Bermuda affiliates, the exact mechanism the shadow-insurance literature flags as flattering. And AAIA's maximum dividend without Iowa approval is $0."),
  ('aare_bscr_ratio', 'AARe BSCR ratio — compressing', 'The Bermuda ruler: eligible capital $30.6B vs required (ECR) $15.2B. Was 242% a year ago — required capital jumped 27% in one year while capital grew slower. Still above the 120% target level, but the trend is the story. (FCR, April 2026)'),
  ('alre_bscr_ratio', 'ALRe BSCR ratio — compressing faster', 'Was 453% a year ago. Eligible capital fell $23.9B → $18.6B (the $3.9B statutory capital outflow shows up here too) while required capital rose. One year took a third off the ratio.'),
  ('statcs_aare', 'AARe statutory capital & surplus', "The Bermuda pivot's own cushion (Class E; ECR is its binding constraint). Bermuda CIT revocation (Jan 2026) will cut this by $847M in Q1 2026."),
  ('statcs_alre', 'ALRe statutory capital & surplus', 'Down $3.9B in one year ($17.6B → $13.7B) while earning only +$0.6B — roughly $4.5B moved out. Where it went is an L1 trace item.'),
  ('athene_re_usa_iv_loc_admitted', 'Vermont captive: LOCs counted as capital', 'Athene Re USA IV counts $76M of letters of credit as admitted assets under a Vermont permitted practice — and the note says WITHOUT this practice it would not have exceeded authorized-control-level RBC. Onshore shadow insurance, disclosed in plain text.'),
 ]),
]

def musd(metric):
    return float(claims[metric]['value'])

def fmt_b(v):
    return f'${v/1e3:,.1f}B'

def stackbar(segs, total):
    parts = []
    for label, v, cls in segs:
        pct = 100 * v / total
        inner = f'{pct:.0f}%' if pct >= 7 else ''
        parts.append(f'<div class="seg {cls}" style="width:{pct:.3f}%" '
                     f'title="{html.escape(label)}: {fmt_b(v)} ({pct:.1f}%)">{inner}</div>')
    return f'<div class="stackbar">{"".join(parts)}</div>'

def legend(segs, total):
    items = []
    for label, v, cls in segs:
        pct = 100 * v / total
        items.append(f'<div class="lg"><span class="dot {cls}"></span>'
                     f'<span class="lgl">{html.escape(label)}</span>'
                     f'<span class="lgv">{fmt_b(v)} · {pct:.0f}%</span></div>')
    return f'<div class="legend">{"".join(items)}</div>'

PROD_TOTAL = musd('gross_premiums_deposits_net_ext_ceded')  # 83,650
prod_groups = [
    ('Annuities (retail, stickier)', musd('premiums_total_annuity'), 'seg-annuity'),
    ('Funding agreements (institutional, runnable)', musd('funding_agreement_deposits'), 'seg-funding'),
    ('Life & other', musd('premiums_life_other'), 'seg-life'),
]
prod_detail = [
    ('Fixed rate annuities', 'premiums_fixed_annuity', 'annuity'),
    ('Indexed annuities', 'premiums_indexed_annuity', 'annuity'),
    ('Pension group annuities', 'premiums_pension_group_annuity', 'annuity'),
    ('Payout annuities', 'premiums_payout_annuity', 'annuity'),
]
prod_rows = []
for label, key, _ in prod_detail:
    v = musd(key); pct = 100 * v / PROD_TOTAL
    prod_rows.append(f'<tr><td>{label}</td><td>{fmt_b(v)}</td><td>{pct:.0f}%</td></tr>')
ann = musd('premiums_total_annuity'); fa = musd('funding_agreement_deposits'); lo = musd('premiums_life_other')
prod_table = (
    '<table class="ptable">'
    '<tr class="sub subhead"><td>Annuities — total</td><td>' + fmt_b(ann) + '</td><td>' + f'{100*ann/PROD_TOTAL:.0f}%' + '</td></tr>'
    + ''.join(prod_rows)
    + '<tr class="sub"><td>Funding agreements</td><td>' + fmt_b(fa) + '</td><td>' + f'{100*fa/PROD_TOTAL:.0f}%' + '</td></tr>'
    + '<tr class="sub"><td>Life &amp; other</td><td>' + fmt_b(lo) + '</td><td>' + f'{100*lo/PROD_TOTAL:.0f}%' + '</td></tr>'
    + '<tr class="sub"><td>Gross premiums &amp; deposits</td><td>' + fmt_b(PROD_TOTAL) + '</td><td>100%</td></tr>'
    + '</table>'
)

ATTRIB_TOTAL = musd('gross_inflows_total')  # 83,438
attrib = [
    ('Athene', musd('inflows_attrib_athene'), 'seg-athene'),
    ('ACRA third-party (ADIP investors)', musd('inflows_attrib_acra_nci'), 'seg-acra'),
    ('Ceded to third-party reinsurers', musd('inflows_ceded_third_party'), 'seg-ceded'),
]

CAPITAL_FLOW = (
    '<p class="cfnote">Two views of the same year of new money. Athene reports two closely-related totals that '
    'differ by definition: <strong>gross premiums &amp; deposits</strong> ($83.7B, broken out by product below) and '
    '<strong>gross inflows</strong> ($83.4B, the management flow metric split by whose money it is). '
    'They differ ~$0.2B by basis — not an error, two different definitions.</p>'
    '<div class="cflabel"><span class="t">By product — what kind of promise</span>'
    f'<span class="n">total {fmt_b(PROD_TOTAL)}</span></div>'
    + stackbar(prod_groups, PROD_TOTAL) + legend(prod_groups, PROD_TOTAL) + prod_table
    + '<div class="cflabel"><span class="t">By whose money — attribution</span>'
    f'<span class="n">total {fmt_b(ATTRIB_TOTAL)}</span></div>'
    + stackbar(attrib, ATTRIB_TOTAL) + legend(attrib, ATTRIB_TOTAL)
    + '<div class="callout" style="margin-top:18px"><strong>What the split says:</strong> '
    '42% of the money in is <strong>funding agreements</strong> — institutional, contractually-dated, runnable money, not sticky retiree annuities (the F4 runnability signal). '
    'And 22% of gross inflows — <strong>$18.5B</strong> — is third-party ADIP capital, not Athene\'s own; Apollo raised it and earns fees on it. '
    'Only ~$63B of the headline $83B is economically Athene\'s.</div>'
)

treaties = list(csv.DictReader(open(ROOT / 'extract/athene/treaties.csv')))
def money(v):
    v = int(v)
    return f'{v/1e9:,.1f}' if v else '—'
trows = []
for r in treaties:
    trows.append(f"<tr><td>{e(r['effective'])}</td><td>{e(r['account'])}</td><td>{e(r['reins_type'])}</td><td>{e(r['business'])}</td>"
                 f"<td>{money(r['premiums_fy2025'])}</td><td>{money(r['modco_reserve'])}</td>"
                 f"<td>{money(r['reserve_credit_cur'])}</td><td>{money(r['funds_withheld'])}</td></tr>")
TREATY_TABLE = (
    '<div class="tbl-scroll"><table class="ptable"><thead><tr>'
    '<th>Effective</th><th>Acct</th><th>Type</th><th>Business</th>'
    '<th>Premiums FY25 ($B)</th><th>ModCo ($B)</th><th>Res. credit ($B)</th><th>Funds withheld ($B)</th>'
    '</tr></thead><tbody>' + '\n'.join(trows) + '</tbody></table></div>'
)

CONNECT = """
<div class="callout" style="border-left-color:var(--acc)">
<strong>How to read this page:</strong> the diagram below is the machine; the numbered badges on it are sections of this page, in order.
Each section decomposes exactly one part of the picture and foots to it:
<a href="#step1">① money in</a> →
<a href="#step2">② reserves</a> →
<a href="#step3">③ the offshore door</a> →
<a href="#step4">④ the sidecars</a> →
<a href="#step5">⑤ the assets + Apollo's take</a> →
<a href="#step6">⑥ the cushion</a>.
Every number is cited to its filed source.
</div>"""

TREATY_FOOT = """<div class="callout"><strong>This table foots to the ③ cards above — exactly.</strong>
ModCo column total <strong>$168.3B = the ModCo card</strong> (all affiliate ModCo is AARe).
Reserve-credit column total $65.3B is the AARe share of the $74.3B card — the balance is the Vermont captive ($1.2B) and ~250 small third-party treaties ($7.9B).
Funds-withheld column total $65.5B of the $66.7B card (balance: Vermont captive $1.2B).
Premiums $35.2B of the $35.8B card (balance: US cessions $0.6B).
8/8 footing gates pass in <span class="mono">extract/athene/treaties.csv</span>.</div>"""

extras = {
 'step1': ('<div style="margin-top:18px"></div>' + CAPITAL_FLOW),
 'step3': ('<p class="cfnote" style="margin-top:18px"><strong>The 29 treaties behind those cards.</strong> Two families: 2018–2022 ModCo vintages (unauthorized status) and 2024+ funds-withheld coinsurance (reciprocal jurisdiction). The structure is readable from which column is populated — ModCo treaties fill the ModCo column; COFW treaties fill reserve credit + funds withheld. Business codes: IA individual annuities, FA funding agreements, VA variable, OA/OL other.</p>'
           + TREATY_TABLE + TREATY_FOOT
           + '<div class="callout"><strong>Mirror-check status:</strong> AARe publishes no unconsolidated statutory statement, so Iowa\'s ceded numbers cannot be line-item reconciled against Bermuda\'s assumed side from public documents. The FCR confirms the aggregate EBS picture (AARe eligible capital $30.6B vs required $15.2B). The treaty-level mirror is not publicly checkable — a measured opacity finding, logged not papered over.</div>'),
}

sections = []
for sid, badge, title, sub, intro, items in STEPS:
    cs = []
    for m, label, expl in items:
        c = claims[m]
        srcline = f"{c['source_doc']} · {c['source_location']}"
        cs.append(f'<div class="mcard"><div class="mv">{fmt(m)}</div><div class="ml">{html.escape(label)}</div>'
                  f'<div class="mx">{html.escape(expl)}</div><div class="ms">{html.escape(srcline)}</div></div>')
    sections.append(
        f'<h2 id="{sid}"><span class="stepchip">{badge}</span> {html.escape(title)} <span class="cnt">— {html.escape(sub)}</span></h2>'
        f'<hr class="rule"><p class="cfnote">{intro}</p>'
        f'<div class="mgrid">{"".join(cs)}</div>'
        + extras.get(sid, '')
    )
FLOW_SECTIONS = '\n'.join(sections)

TEMPLATE = open(ROOT / 'tools/dashboard_template.html').read()
out = (TEMPLATE
       .replace('__ROWS__', ROWS).replace('__DOCS__', DOCS)
       .replace('__FLOW_SECTIONS__', FLOW_SECTIONS)
              .replace('__CONNECT__', CONNECT)
              .replace('__N_TOTAL__', str(n_total)).replace('__N_COC__', str(n_coc))
       .replace('__N_BM__', str(n_bm)).replace('__N_LEI__', str(n_lei))
       .replace('__N_DOCS__', str(len(docs))))
import re as _re
for m in set(_re.findall(r'__F_([A-Za-z0-9_]+?)__', out)):
    out = out.replace(f'__F_{m}__', fmt(m))
dest = ROOT / 'dossiers/athene/entity-dashboard.html'
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(out)
print('wrote', dest, len(out), 'bytes')

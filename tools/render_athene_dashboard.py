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
    b = v / 1e3 if c['unit'] == 'USD_M' else v / 1e9
    return f'${b:,.1f}B'

GROUPS = [
 ('Money in — FY2025', [
  ('gross_inflows_total', 'Gross inflows', 'All new money taken in during 2025: annuity sales, pension buyouts, funding agreements, assumed reinsurance. The real growth number — GAAP "premiums" were only $2.6B because deposits never touch the income statement.'),
  ('funding_agreement_deposits', 'of which funding agreements', 'Institutional borrowings dressed as insurance: FABN notes sold to bond investors, FHLB advances, repurchase-style agreements. $7.2B in 2023 → $35.4B in 2025.'),
  ('inflows_attrib_acra_nci', 'of which third-party (ADIP)', "Inflows belonging to outside investors in the ACRA sidecars — not Athene shareholders. Apollo raised this capital and charges fees on it too."),
  ('net_flows', 'Net flows', 'Inflows minus outflows (surrenders, withdrawals, maturities, benefit payments). The machine grew $47.9B net in one year.'),
 ]),
 ('Offshore transfer — AAIA to AARe (statutory)', [
  ('schedS_modco_reserve_total', 'ModCo reserves', "The dual-ledger number: liabilities kept legally on AAIA's books while the investment economics belong to AARe in Bermuda. $116.1B general account + $52.2B separate account."),
  ('schedS_reserve_credit_taken_total', 'Reserve credit taken', "Reserves removed from AAIA's balance sheet entirely because they are ceded outright (mostly funds-withheld coinsurance to AARe under 2024+ treaties)."),
  ('schedS_funds_withheld_total', 'Funds withheld', 'Assets AAIA physically keeps as collateral backing the coinsurance it ceded — legally held onshore, economically working for Bermuda.'),
  ('schedS_premiums_ceded_total', 'Premiums ceded FY2025', "The year's premium passed through to reinsurers. Every affiliate dollar of it went to one counterparty: AARe."),
 ]),
 ('Group balance sheet — GAAP', [
  ('total_assets', 'Total assets', "Athene Holding consolidated, everything on the books at 12/31/2025. Up from $363.3B a year earlier."),
  ('total_investments', 'Total investments', 'The general-account investment portfolio at fair value: $192.6B AFS securities, $91.9B mortgage loans, plus trading, derivatives, funds withheld.'),
  ('net_invested_assets_incl_rp_vie', 'Net invested assets', "Management's economic measure: adds related-party holdings and consolidated-VIE look-through, counts ACRA at Athene's economic share."),
  ('net_reserve_liabilities', 'Net reserve liabilities', 'Policyholder obligations net of reinsurance — the money Athene owes savers and institutions, at its own economic share.'),
  ('noncontrolling_interests', 'Noncontrolling interests', "Third-party (mostly ADIP) equity inside consolidated ACRA vehicles. Was $9.5B a year ago — up 59% in one year."),
 ]),
 ("Apollo's take + runnability", [
  ('apollo_management_fees', 'Management fees to Apollo', 'FY2025 base + sub-allocation + performance fees under the Fee Agreement (0.225% base on the first $103.4B, higher sub-allocation fees for higher-alpha asset classes). Plus $66M sub-advisory passthrough.'),
  ('net_investment_income', 'Net investment income', 'What the portfolio earned in FY2025 (net of the fees above; includes $2.1B earned from related-party investments).'),
  ('funding_agreements_net_reserve_liab', 'Funding agreements outstanding', 'The runnable slice of the liability stack: FABN, FABR, FHLB and repo-style funding agreements. 26.3% of net reserve liabilities, was 21.0% a year ago — the F4 signal.'),
 ]),
]

cards = []
for gtitle, items in GROUPS:
    cs = []
    for m, label, expl in items:
        c = claims[m]
        src = f"{c['source_doc']} · {c['source_location']}"
        cs.append(f'<div class="mcard"><div class="mv">{fmt(m)}</div><div class="ml">{html.escape(label)}</div>'
                  f'<div class="mx">{html.escape(expl)}</div><div class="ms">{html.escape(src)}</div></div>')
    cards.append(f'<div class="mgroup"><h3>{html.escape(gtitle)}</h3><div class="mgrid">{"".join(cs)}</div></div>')
L0CARDS = '\n'.join(cards)

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

TEMPLATE = open(ROOT / 'tools/dashboard_template.html').read()
out = (TEMPLATE
       .replace('__ROWS__', ROWS).replace('__DOCS__', DOCS)
       .replace('__L0CARDS__', L0CARDS)
       .replace('__CAPITAL_FLOW__', CAPITAL_FLOW)
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

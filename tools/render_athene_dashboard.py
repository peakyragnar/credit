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
        short = html.escape(label.split(' (')[0].split(' — ')[0])
        if pct >= 13:
            inner = f'{short} · {pct:.0f}%'
        elif pct >= 6 and len(short) <= 4:
            inner = f'{short} {pct:.0f}%'
        elif pct >= 3:
            inner = f'{pct:.0f}%'
        else:
            inner = ''
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

def usd(metric):
    return float(claims[metric]['value']) / 1e6  # -> $M for USD-unit claims

INV_TOTAL = usd('sis_total_invested_assets')
inv_groups = [
    ('Bonds — issuer credit', usd('sis_issuer_credit_obligations'), 'seg-annuity'),
    ('Bonds — asset-backed (ABS)', usd('sis_abs_total'), 'seg-funding'),
    ('Mortgage loans', usd('sis_mortgages_residential') + usd('sis_mortgages_commercial') + usd('sis_mortgages_mezzanine') - 106.892501, 'seg-acra'),
    ('Schedule BA (funds/other)', usd('sis_schedule_ba_other_invested'), 'seg-athene'),
    ('Cash + short-term', usd('sis_cash_and_st'), 'seg-life'),
    ('Everything else (derivs, stocks, RE…)', INV_TOTAL - usd('sis_issuer_credit_obligations') - usd('sis_abs_total')
       - (usd('sis_mortgages_residential') + usd('sis_mortgages_commercial') + usd('sis_mortgages_mezzanine') - 106.892501)
       - usd('sis_schedule_ba_other_invested') - usd('sis_cash_and_st'), 'seg-ceded'),
]
BOND_TOTAL = usd('bonds_sched_d')
bond_groups = [
    ('Corporate bonds', usd('sis_corporate_bonds'), 'seg-annuity'),
    ('Govt / munis / sovereign', usd('sis_us_govt') + 640.532566 + 34.712448 + 343.244069, 'seg-athene'),
    ('Other issuer credit (funds, single-entity, project fin, loans…)',
       usd('sis_issuer_credit_obligations') - usd('sis_corporate_bonds') - (usd('sis_us_govt') + 640.532566 + 34.712448 + 343.244069), 'seg-life'),
    ('ABS — financial', usd('sis_abs_financial_self_liquidating') + usd('sis_abs_financial_not_self_liquidating'), 'seg-funding'),
    ('ABS — non-financial', usd('sis_abs_nonfinancial'), 'seg-acra'),
]

def bfmt(vm): return f'${vm/1e3:,.1f}B'
bridge_rows = []
for label, beg, acq, disp, end in [
    ('Bonds (Schedule D)', 130962.441664, usd('bonds_acquired_fy2025'), usd('bonds_disposed_fy2025'), usd('bonds_sched_d')),
    ('Mortgages (Schedule B)', 60294.320216, usd('mortgages_acquired_fy2025'), usd('mortgages_disposed_fy2025'), 86745.420032),
    ('Schedule BA', usd('ba_begin_fy2025'), usd('ba_acquired_fy2025'), 4417.190620, usd('sis_schedule_ba_other_invested')),
]:
    other = end - beg - acq + disp
    bridge_rows.append(f'<tr><td>{label}</td><td>{bfmt(beg)}</td><td>+{bfmt(acq)}</td><td>−{bfmt(disp)}</td>'
                       f'<td>{"+" if other>=0 else "−"}{bfmt(abs(other))}</td><td class="nm">{bfmt(end)}</td></tr>')
BRIDGE_TABLE = ('<table class="ptable"><thead><tr><th>Book</th><th>Begin 2025</th><th>Acquired</th><th>Disposed</th>'
                '<th>Itemized net*</th><th>End 2025</th></tr></thead><tbody>' + ''.join(bridge_rows) + '</tbody></table>'
                "<p class=\"cfnote\">*Not a plug: the net of the verification schedules' remaining itemized lines "
                '(discount accrual, FX, realized gains, amortization, OTTI, capitalized interest) — each extracted and '
                'summing exactly to the printed ending balance. Mortgages row shown pre-valuation-allowance (−$0.11B to '
                'statement value; $1 printed-rounding exception logged in runbook/exceptions.md).</p>')

ASSET_SECTION = (
    '<div class="cflabel" style="margin-top:22px"><span class="t">AAIA invested assets — what the money actually is</span>'
    f'<span class="n">total {bfmt(INV_TOTAL)} · statutory, gross</span></div>'
    + stackbar([(l, v, c) for l, v, c in inv_groups], INV_TOTAL)
    + legend([(l, v, c) for l, v, c in inv_groups], INV_TOTAL)
    + '<div class="cflabel" style="margin-top:18px"><span class="t">The $158.9B of "bonds", opened up</span>'
    '<span class="n">foots to Schedule D exactly</span></div>'
    + stackbar(bond_groups, BOND_TOTAL) + legend(bond_groups, BOND_TOTAL)
    + '<div class="callout" style="margin-top:16px"><strong>What the split says:</strong> only 26% of the "bonds" are '
    'plain corporates. 46% is asset-backed securities, and another ~$26B of the issuer-credit bucket is '
    'structured-adjacent (bonds issued by funds, single-entity-backed, project finance). The portfolio is '
    'predominantly structured/private credit wearing a bond label. And the mortgage book is majority '
    '<strong>residential</strong> ($52.1B vs $33.6B commercial) — not the CRE-heavy book one might assume.</div>'
    + '<div class="cflabel" style="margin-top:18px"><span class="t">FY2025 bridges — how each book moved</span>'
    '<span class="n">verification schedules, all footed</span></div>'
    + BRIDGE_TABLE
    + '<div class="callout"><strong>The PBBD verdict (hard question #1, for AAIA): the +21% bond growth is real.</strong> '
    'Note 2 disclosed the entire reclassification: $1.65B (GA) + $0.23B (SA) moved OUT of Schedule D into BA at '
    'adoption — the canonical false signal is absent; adjusting for it, apples-to-apples growth is ~+22.8%, slightly '
    '<em>higher</em> than reported. The growth is genuine origination: $97.5B of bonds and $38.4B of mortgages '
    'acquired in one year (against $71.6B / $12.7B disposed — an actively churned book, ~55% annual disposal rate '
    'on bonds).</div>'
)


# ---- D1/D2/D3: line-level Schedule D analysis (from footed extract) ----
dlines = list(csv.DictReader(open(ROOT / 'extract/athene/sched_d_part1_lines.csv')))
def _iv(x): return int(x) if x not in ('', None) else 0
DTOT = sum(_iv(r['bacv']) for r in dlines)

_band_groups = []
for label, keys, cls in [
    ('AAA', ['1.A'], 'seg-q-aaa'),
    ('AA band', ['1.B','1.C','1.D'], 'seg-q-aa'),
    ('A band', ['1.E','1.F','1.G'], 'seg-q-a'),
    ('BBB+ / BBB', ['2.A','2.B'], 'seg-q-bbb'),
    ('BBB− (the cliff)', ['2.C'], 'seg-q-cliff'),
    ('Below IG', ['3','4','5','6'], 'seg-q-junk'),
]:
    v = sum(_iv(r['bacv']) for r in dlines
            if r['naic_designation'] in keys or (len(keys[0])==1 and (r['naic_designation'] or '?').split('.')[0] in keys))
    _band_groups.append((label, v/1e6, cls))

def _srcb(sym):
    if sym == 'FE': return 'Public rating (FE)'
    if sym in ('PL','PLGI'): return 'Private letter (PL)'
    if sym in ('Z','YE'): return 'Self-assigned (Z/YE)'
    if sym in ('FM','FMR'): return 'Modeled (FM)'
    if not sym: return 'Exempt / SVO-assessed'
    return 'Other'
_src_agg = {}
for r in dlines:
    k = _srcb(r['svo_symbol']); _src_agg[k] = _src_agg.get(k, 0) + _iv(r['bacv'])
_src_groups = [
    ('Public rating (FE)', _src_agg.get('Public rating (FE)',0)/1e6, 'seg-annuity'),
    ('Exempt / SVO-assessed', _src_agg.get('Exempt / SVO-assessed',0)/1e6, 'seg-athene'),
    ('Self-assigned (Z/YE)', _src_agg.get('Self-assigned (Z/YE)',0)/1e6, 'seg-funding'),
    ('Private letter (PL)', _src_agg.get('Private letter (PL)',0)/1e6, 'seg-acra'),
    ('Modeled (FM)', (_src_agg.get('Modeled (FM)',0)+_src_agg.get('Other',0))/1e6, 'seg-ceded'),
]

# yield cross (FE vs PL, same notch, 2024-25 vintages)
_yagg = {}
for r in dlines:
    if r['acquired'][-4:] not in ('2024','2025'): continue
    try: er = float(r['effective_rate'])
    except (ValueError, TypeError): continue
    if er <= 0 or er > 20: continue
    sym = 'PL' if r['svo_symbol'] in ('PL','PLGI') else ('FE' if r['svo_symbol']=='FE' else None)
    if not sym: continue
    k = (r['naic_designation'], sym)
    w = _iv(r['bacv'])
    a = _yagg.setdefault(k, [0.0, 0]); a[0] += er*w; a[1] += w
_yrows = []
for d, eq in [('1.F','A'),('1.G','A−'),('2.A','BBB+'),('2.B','BBB')]:
    fe, pl = _yagg.get((d,'FE')), _yagg.get((d,'PL'))
    if fe and pl and fe[1] > 100e6 and pl[1] > 100e6:
        fy, py = fe[0]/fe[1], pl[0]/pl[1]
        _yrows.append(f'<tr><td>{eq}</td><td>{fy:.2f}%</td><td>{py:.2f}%</td><td class="nm">{py-fy:+.2f}pp</td></tr>')
YIELD_TABLE = ('<table class="ptable" style="max-width:480px"><thead><tr><th>Notch</th><th>Public-rated (FE)</th>'
               '<th>Private letter (PL)</th><th>PL premium</th></tr></thead><tbody>' + ''.join(_yrows) + '</tbody></table>')

# quality-within-source matrix: one quality bar per rating source
_BANDS = [
    ('AAA', lambda d: d == '1.A', 'seg-q-aaa'),
    ('AA', lambda d: d in ('1.B','1.C','1.D'), 'seg-q-aa'),
    ('A', lambda d: d in ('1.E','1.F','1.G'), 'seg-q-a'),
    ('BBB+/BBB', lambda d: d in ('2.A','2.B'), 'seg-q-bbb'),
    ('BBB−', lambda d: d == '2.C', 'seg-q-cliff'),
    ('<IG', lambda d: (d or '?').split('.')[0] in ('3','4','5','6'), 'seg-q-junk'),
]
_matrix_rows = []
for _src_label, _key in [('Public rating (FE)','Public rating (FE)'),
                         ('Exempt / SVO-assessed','Exempt / SVO-assessed'),
                         ('Self-assigned (Z/YE)','Self-assigned (Z/YE)'),
                         ('Private letter (PL)','Private letter (PL)'),
                         ('Modeled (FM) + other', None)]:
    if _key is None:
        _sel = [r for r in dlines if _srcb(r['svo_symbol']) in ('Modeled (FM)','Other')]
    else:
        _sel = [r for r in dlines if _srcb(r['svo_symbol']) == _key]
    _stot = sum(_iv(r['bacv']) for r in _sel)
    if _stot <= 0: continue
    _segs = []
    for _bl, _fn, _cls in _BANDS:
        _v = sum(_iv(r['bacv']) for r in _sel if _fn(r['naic_designation']))
        if _v > 0: _segs.append((_bl, _v/1e6, _cls))
    _matrix_rows.append(
        f'<div class="cflabel" style="margin:10px 0 4px"><span class="t" style="font-size:13px;font-weight:500">{_src_label}</span>'
        f'<span class="n">${_stot/1e9:,.1f}B</span></div>'
        + stackbar(_segs, _stot/1e6))
_qlegend = ('<div class="legend" style="margin-bottom:6px">' + ''.join(
    f'<div class="lg"><span class="dot {c}"></span><span class="lgl">{n}</span></div>'
    for n, c in [('AAA','seg-q-aaa'),('AA','seg-q-aa'),('A','seg-q-a'),
                 ('BBB+/BBB','seg-q-bbb'),('BBB− cliff','seg-q-cliff'),('Below IG','seg-q-junk')]) + '</div>')
MATRIX = (
    '<div class="cflabel" style="margin-top:22px"><span class="t">Quality within each rating source</span>'
    '<span class="n">color = rating band; hover for exact figures</span></div>'
    + _qlegend
    + ''.join(_matrix_rows)
    + '<p class="cfnote">Read: the public-rated (FE) book skews higher-grade and holds most of the cliff paper; '
    'the private-letter (PL) book is ~81% A/BBB with almost no cliff or junk — grades that earn capital relief, '
    'assigned in a channel with no market check. Self-assigned paper carries the largest below-IG share.</p>'
)


# P&L of the held book: income + valuation actions by band and source
def _pnl_rows(sel):
    b = sum(_iv(r['bacv']) for r in sel)
    ir = sum(_iv(r['interest_received']) for r in sel)
    da = sum(_iv(r['interest_due_accrued']) for r in sel)
    ot = sum(_iv(r['otti']) for r in sel)
    un = sum(_iv(r['unrealized_val_change']) for r in sel)
    return b, ir, da, ot, un
_pnl_html = []
for _bl, _fn, _cls in _BANDS:
    sel = [r for r in dlines if _fn(r['naic_designation'])]
    b, ir, da, ot, un = _pnl_rows(sel)
    if b <= 0: continue
    cy = 100*ir/b if b else 0
    _pnl_html.append(f'<tr><td><span class="dot {_cls}" style="margin-right:6px"></span>{_bl}</td>'
                     f'<td>${b/1e9:,.1f}B</td><td>${ir/1e6:,.0f}M</td><td class="nm">{cy:.2f}%</td>'
                     f'<td>${da/1e6:,.0f}M</td><td>${ot/1e6:,.1f}M</td><td>${un/1e6:+,.1f}M</td></tr>')
for _sl, _key in [('— of which PL-graded', 'Private letter (PL)'), ('— of which FE-graded', 'Public rating (FE)')]:
    sel = [r for r in dlines if _srcb(r['svo_symbol']) == _key]
    b, ir, da, ot, un = _pnl_rows(sel)
    cy = 100*ir/b if b else 0
    _pnl_html.append(f'<tr style="color:var(--muted)"><td>{_sl}</td>'
                     f'<td>${b/1e9:,.1f}B</td><td>${ir/1e6:,.0f}M</td><td class="nm">{cy:.2f}%</td>'
                     f'<td>${da/1e6:,.0f}M</td><td>${ot/1e6:,.1f}M</td><td>${un/1e6:+,.1f}M</td></tr>')
PNL_TABLE = (
    '<div class="cflabel" style="margin-top:22px"><span class="t">P&amp;L of the held book, FY2025 — income and valuation actions</span>'
    '<span class="n">positions held at 12/31 only; sold positions land with the Part 4 parse</span></div>'
    '<div class="tbl-scroll"><table class="ptable"><thead><tr><th>Band</th><th>BACV</th><th>Interest received</th>'
    '<th>Cash yield*</th><th>Due &amp; accrued</th><th>OTTI (impairments)</th><th>Unrealized chg</th></tr></thead>'
    '<tbody>' + ''.join(_pnl_html) + '</tbody></table></div>'
    '<p class="cfnote">*Interest received ÷ year-end BACV — approximate (denominator is year-end, book grew all year; '
    'positions bought late-year drag the ratio). Due &amp; accrued = income booked but not yet paid ($1.50B book-wide — '
    'the accrual wedge to watch). OTTI = statutory impairments taken on held positions. Gates: BACV exact; P&amp;L columns '
    'carry structurally-assigned residuals (disposed positions) that the Part 4 parse closes.</p>'
    '<div class="callout"><strong>First read:</strong> impairments on the held book are tiny ($109M on $158.9B — 7bps) '
    'while the capital-gains exhibit shows realized losses on 2025 bond sales (−$77.8M unaffiliated) — whether losses are '
    'being realized via disposals rather than impairments is exactly what the Part 4 (disposals) parse answers.</div>'
)


_nii = 12732.699320; _fwh = 3544.758297 - 130.183473
_cred = 2096.835422 + 8.269553 + 1573.987953
_otti_all = 110.227270 + 51.810227
_spread = _nii - _fwh - _cred - _otti_all
NETSPREAD = (
    '<div class="cflabel" style="margin-top:22px"><span class="t">Net spread — income minus impairments minus cost of funding</span>'
    '<span class="n">AAIA statutory, FY2025 — every line cited</span></div>'
    '<div class="tbl-scroll"><table class="ptable" style="max-width:640px"><tbody>'
    f'<tr><td>Net investment income (after expenses)</td><td class="nm">$12,733M</td></tr>'
    f'<tr><td>− investment results passed to AARe (funds-withheld adjustment, net)</td><td>−$3,415M</td></tr>'
    f'<tr><td>− interest credited to policyholders and deposit contracts<br>'
    '<span class="dim" style="font-size:11.5px">annuity tabular interest $2,105M + deposit-type/FABN interest $1,574M</span></td><td>−$3,679M</td></tr>'
    f'<tr><td>− impairments taken (bonds $110M + mortgages $52M)</td><td>−$162M</td></tr>'
    f'<tr class="sub"><td>≈ Net spread retained at AAIA</td><td class="nm">${_spread:,.0f}M</td></tr>'
    '</tbody></table></div>'
    '<p class="cfnote">Cross-check at group level (GAAP, already banked): NII $17,847M − interest-sensitive contract '
    'benefits $12,089M ≈ $5,758M — same order of magnitude by an independent route. Caveats, logged: the ModCo block\'s '
    'pass-through is embedded in reserve movements (not fully isolated here, unlike the funds-withheld line); the GAAP '
    'benefits line includes index credits and reserve remeasurement; realized G/L and IMR/AVR flows sit outside this '
    'operating view. Good enough for L0/L1 anchoring; the treaty-level spread decomposition is an L2 item.</p>'
)

D1_SECTION = (
    '<div class="cflabel" style="margin-top:26px"><span class="t">D1 — every bond position, extracted and footed</span>'
    f'<span class="n">8,582 rows · both sections foot to the dollar</span></div>'
    '<p class="cfnote">The parser extracted all Schedule D Part 1 line items; book value sums match the printed control '
    'totals exactly ($85,388,493,721 + $73,463,901,478). PPN-symbol identifiers (#, @, *) mark private placements: '
    '<strong>$39.4B — 24.8% of the bond book</strong>.</p>'
    '<div class="cflabel"><span class="t">Credit quality — by agency-equivalent rating</span>'
    f'<span class="n">total {DTOT/1e9:,.1f}B</span></div>'
    + stackbar(_band_groups, DTOT/1e6) + legend(_band_groups, DTOT/1e6)
    + '<div class="cflabel" style="margin-top:16px"><span class="t">Who graded it — rating source (SVO symbol)</span>'
    '<span class="n">the credibility axis</span></div>'
    + stackbar(_src_groups, DTOT/1e6) + legend(_src_groups, DTOT/1e6)
    + '<div class="callout" style="margin-top:16px"><strong>D2 — the cliff is mostly publicly rated (exculpatory, recorded):</strong> '
    'of the $18.5B at BBB−, 76% carries public agency ratings; private letters are only 7.4%. The PL book ($40.1B) '
    'clusters at A/BBB+ instead — where the capital relief is earned.</div>'
    + MATRIX
    + '<div class="cflabel" style="margin-top:16px"><span class="t">D3 — same notch, different grader, different yield</span>'
    '<span class="n">2024–25 vintages, BACV-weighted</span></div>'
    + YIELD_TABLE
    + '<div class="callout"><strong>The open question of F1:</strong> private-letter paper yields +0.6–0.9pp over '
    'publicly-rated paper at the same notch — PL "A" prices between public BBB and BBB−. Either an illiquidity premium '
    '(the industry\'s pitch) or the market disbelieving the letters by 2–3 notches (the NAIC\'s finding). Yield alone '
    'cannot say; impairment outcomes by rating source (period backfill) and cross-holder marks (D4) are the '
    'discriminators. Deliberately unresolved.</div>'
    + PNL_TABLE
    + NETSPREAD
)

# ---- 5b: the disposal machine (Part 4 + Part 5 extracts) ----
import datetime as _dtmod
_NONSALE = re.compile(r'paydown|call|matur|redempt|sink|tender|conversion|exchange|cancel', re.I) if 're' in dir() else None
import re as _re
_NONSALE = _re.compile(r'paydown|call|matur|redempt|sink|tender|conversion|exchange|cancel', _re.I)
def _dload(p, rpcol):
    out = []
    for r in csv.DictReader(open(ROOT / p)):
        row = {'cusip': r['cusip'], 'rp': r[rpcol] == 'Y', 'buyer': r['purchaser'][:34], 'date': r['disposal_date'],
               'consid': int(r['consideration']) if r['consideration'] not in ('', None) else 0,
               'par': int(r['par_value']) if r['par_value'] not in ('', None) else 0,
               'tgl': int(r['total_gl']) if r['total_gl'] not in ('', None) else 0}
        out.append(row)
    return out
_d4 = _dload('extract/athene/sched_d_part4_disposals.csv', 'related_party')
_d5 = _dload('extract/athene/sched_d_part5_roundtrips.csv', 'rp_purchaser')
_all = _d4 + _d5
_rp  = [r for r in _all if r['rp']]
_tp  = [r for r in _all if not r['rp']]
_rp_c = sum(r['consid'] for r in _rp); _tp_c = sum(r['consid'] for r in _tp)
_rp_g = sum(r['tgl'] for r in _rp);    _tp_g = sum(r['tgl'] for r in _tp)
_flip_c = sum(r['consid'] for r in _d5)
_buyers = {}
for r in _rp:
    b = r['buyer']
    _buyers.setdefault(b, [0, 0]); _buyers[b][0] += r['consid']; _buyers[b][1] += 1
_btop = sorted(_buyers.items(), key=lambda x: -x[1][0])[:6]
_brows = ''.join(f'<tr><td>{html.escape(b)}</td><td>${v/1e9:,.2f}B</td><td>{n}</td></tr>' for b, (v, n) in _btop)

# matched pairs (condensed re-computation)
def _pdt(s):
    try: return _dtmod.datetime.strptime(s, '%m/%d/%Y')
    except Exception: return None
_bycus = {}
for r in _all:
    if r['cusip'] != '000000-00-0' and r['par'] > 0 and r['consid'] > 0 and not _NONSALE.search(r['buyer']):
        _bycus.setdefault(r['cusip'], []).append(r)
_npairs, _hi, _lo, _eq, _dlist = 0, 0, 0, 0, []
for cus, rs in _bycus.items():
    rp_ = [r for r in rs if r['rp']]; tp_ = [r for r in rs if not r['rp']]
    if not rp_ or not tp_: continue
    for a in rp_:
        da = _pdt(a['date'])
        if not da: continue
        near = [b for b in tp_ if _pdt(b['date']) and abs((_pdt(b['date'])-da).days) <= 45]
        if not near: continue
        b = min(near, key=lambda b: abs((_pdt(b['date'])-da).days))
        d = 100*a['consid']/a['par'] - 100*b['consid']/b['par']
        _npairs += 1; _dlist.append(d)
        if d > 0.05: _hi += 1
        elif d < -0.05: _lo += 1
        else: _eq += 1
import statistics as _st
_med = _st.median(_dlist) if _dlist else 0

D5B_SECTION = (
    '<h2 id="step5b"><span class="stepchip">⑤b</span> The disposal machine <span class="cnt">— who Athene sells to, and at what price</span></h2>'
    '<hr class="rule">'
    '<p class="cfnote">Every FY2025 bond sale from Schedule D Parts 4 and 5 — consideration reconciles to the printed '
    'total to the dollar ($72,140,293,824). The question this section answers: when the seller and buyer share an owner, '
    'do the prices behave?</p>'
    '<div class="figure"><svg viewBox="0 0 680 300" role="img" aria-label="Disposal flows">' 
    '<defs><marker id="ar5" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
    '<path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>'
    '<rect class="nd neutral" x="30" y="90" width="150" height="52" rx="3"/><text class="t1" x="105" y="111" text-anchor="middle">Wall Street dealers</text><text class="t2" x="105" y="129" text-anchor="middle">Deutsche · Citi · Wells…</text>'
    '<line class="wire" x1="180" y1="116" x2="248" y2="116" marker-end="url(#ar5)"/>'
    '<rect class="nd usn" x="252" y="80" width="176" height="72" rx="3"/><text class="t1u" x="340" y="105" text-anchor="middle">AAIA</text><text class="t2u" x="340" y="123" text-anchor="middle">sold $72.1B of bonds</text><text class="t2u" x="340" y="139" text-anchor="middle">in FY2025</text>'
    '<path class="wire" d="M428 100 H500 V76" marker-end="url(#ar5)"/>'
    '<rect class="nd neutral" x="440" y="20" width="210" height="52" rx="3"/><text class="t1" x="545" y="41" text-anchor="middle">Market buyers — $62.9B</text><text class="t2" x="545" y="59" text-anchor="middle">gains booked: +5bp</text>'
    '<path class="wire" d="M428 132 H500 V156" marker-end="url(#ar5)"/>'
    '<rect class="nd bmn" x="440" y="160" width="210" height="52" rx="3"/><text class="t1b" x="545" y="181" text-anchor="middle">Related parties — $9.2B</text><text class="t2b" x="545" y="199" text-anchor="middle">gains booked: +49bp (10×)</text>'
    '<rect class="box-dash" x="30" y="230" width="620" height="48" rx="3"/>'
    '<text class="t1" x="340" y="250" text-anchor="middle">$26.7B — 37% of all disposals — were same-year round-trips</text>'
    '<text class="t2" x="340" y="268" text-anchor="middle">bought from dealers, sold weeks later, mostly to ACRA sidecar accounts (the street → sidecar pipeline)</text>'
    '</svg></div>'
    '<div class="cflabel" style="margin-top:18px"><span class="t">Top related-party buyers</span><span class="n">889 trades, all named in the filing</span></div>'
    '<div class="tbl-scroll"><table class="ptable" style="max-width:560px"><thead><tr><th>Buyer</th><th>Consideration</th><th>Trades</th></tr></thead>'
    f'<tbody>{_brows}</tbody></table></div>'
    '<div class="cflabel" style="margin-top:18px"><span class="t">The matched-pair test — same bond, family vs market, within 45 days</span>'
    f'<span class="n">{_npairs} clean pairs</span></div>'
    f'<p class="cfnote">Median price difference (related − market): <strong>{_med:+.3f} points ≈ zero</strong> · related paid more in {_hi}, less in {_lo}, equal in {_eq}. '
    'Where the same bond sold to both, prices match — the 10× gain gap is <strong>mix</strong> (seasoned, appreciated bonds routed to affiliates), not rigged prices.</p>'
    + stackbar([('tested & clean', 6, 'seg-annuity'), ('untestable — no market trade to compare (mostly private paper)', 94, 'seg-ceded')], 100)
    + '<div class="callout"><strong>The honest boundary:</strong> the test reaches only ~6% of the $9.2B related-party flow. '
    'The other 94% — predominantly private, illiquid paper — never traded with an outside buyer, so no market check exists '
    '<em>by construction</em>. The overlap is clean; the majority is unverifiable from this filing. Reaching it requires '
    'cross-holder marks (the D4 / BDC-engine work) — which is exactly why that layer exists.</div>'
)

extras = {
 'step1': ('<div style="margin-top:18px"></div>' + CAPITAL_FLOW),
 'step5': ASSET_SECTION + D1_SECTION,
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
sections.insert(5, D5B_SECTION)
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

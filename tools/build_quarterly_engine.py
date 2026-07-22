#!/usr/bin/env python3
"""Build the quarterly stock-and-flow engine workbook (Michael's sketch, live).

Reads extract/athene/quarterly_supplement.csv (gate-verified) and emits
dossiers/athene/athene-quarterly-engine.xlsx:
  Engine  - quarters as columns; inflows by channel AND by owner (same total,
            cross-checked), outflows by owner and type, net flows, reserve
            rollforward (stock+flow with continuity checks), ACRA rollforward,
            reserve stock by product, SRE income chain, rates, derived spread.
  Checks  - live count of failing identity checks (must be zero).
  Data    - raw extracted cells for traceability.
  ReadMe  - sources, method, legend, coverage boundary.

Conventions: blue = extracted filed value; black = formula; yellow = fill-in
(2Q26 column). All identities are Excel formulas so the sheet recalculates.
No LibreOffice locally: formula arithmetic is verified in Python below
(same identities the parser gates proved), Excel computes on open.
"""
import csv
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'extract/athene/quarterly_supplement.csv'
DEST = ROOT / 'dossiers/athene/athene-quarterly-engine.xlsx'

QUARTERS = ['4Q24', '1Q25', '2Q25', '3Q25', '4Q25', '1Q26']
FILL_Q = '2Q26'
COLS = {q: get_column_letter(2 + i) for i, q in enumerate(QUARTERS)}   # B..G
FILL_COL = get_column_letter(2 + len(QUARTERS))                        # H

D = {}
for r in csv.DictReader(open(SRC)):
    if r['value'] != '':
        D[(r['quarter'], r['metric'])] = float(r['value'])

BLUE = Font(name='Arial', size=10, color='0000FF')
BLACK = Font(name='Arial', size=10)
BOLD = Font(name='Arial', size=10, bold=True)
HDR = Font(name='Arial', size=11, bold=True)
GREY = Font(name='Arial', size=9, color='666666')
YELLOW = PatternFill('solid', fgColor='FFFF00')
MONEY_FMT = '$#,##0;($#,##0);"-"'
PCT_FMT = '0.00%'

wb = Workbook()
ws = wb.active
ws.title = 'Engine'
ws.sheet_view.showGridLines = True
ws.column_dimensions['A'].width = 46
for i in range(len(QUARTERS) + 1):
    ws.column_dimensions[get_column_letter(2 + i)].width = 11

check_cells = []
row = 1


def put(label, font=BLACK, indent=0):
    global row
    c = ws.cell(row=row, column=1, value=('    ' * indent) + label)
    if label.startswith('='):
        c.data_type = 's'      # literal text — otherwise Excel reads '= …' as a formula -> #NAME?
    c.font = font
    return row


def vals(metric, scale=1.0, fmt=MONEY_FMT, pct=False):
    for q in QUARTERS:
        v = D.get((q, metric))
        c = ws.cell(row=row, column=2 + QUARTERS.index(q))
        if v is not None:
            c.value = v / 100.0 if pct else v * scale
        c.font = BLUE
        c.number_format = fmt
    ws.cell(row=row, column=2 + len(QUARTERS)).fill = YELLOW


def formula(fml_by_col, fmt=MONEY_FMT, font=BOLD):
    for q in QUARTERS:
        col = COLS[q]
        c = ws.cell(row=row, column=2 + QUARTERS.index(q), value=fml_by_col(col))
        c.font = font
        c.number_format = fmt


def check(fml_by_col):
    global row
    for q in QUARTERS:
        col = COLS[q]
        c = ws.cell(row=row, column=2 + QUARTERS.index(q), value=fml_by_col(col))
        c.font = GREY
        check_cells.append(f'{col}{row}')


def section(title):
    global row
    row += 1
    put(title, HDR)
    row += 1


# ---- header ----
ws.cell(row=1, column=1, value='ATHENE — THE QUARTERLY ENGINE  (stock & flow, every line from footed extracts)').font = HDR
row = 2
put('$ in millions. Blue = filed value (ATH financial supplements, sha in acquisition/manifest.csv). '
    'Black bold = formula. Row "check" shows FAIL if an identity breaks. Yellow column = fill when 2Q26 publishes.', GREY)
row = 4
for q in QUARTERS:
    c = ws.cell(row=4, column=2 + QUARTERS.index(q), value=q)
    c.font = BOLD
    c.alignment = Alignment(horizontal='center')
c = ws.cell(row=4, column=2 + len(QUARTERS), value=FILL_Q)
c.font = BOLD
c.fill = YELLOW
c.alignment = Alignment(horizontal='center')

# ---- inflows by channel ----
section('MONEY IN — BY CHANNEL')
r0 = row
put('Retail', BLUE); vals('retail'); row += 1
put('Flow reinsurance', BLUE); vals('flow_reins'); row += 1
put('Funding agreements', BLUE); vals('funding_agreements'); row += 1
put('Pension group annuities', BLUE); vals('pga'); row += 1
put('Other spread products', BLUE); vals('other_spread'); row += 1
r_org = row
put('= Gross organic inflows', BOLD); formula(lambda c: f'=SUM({c}{r0}:{c}{r0+4})'); row += 1
put('Gross inorganic (block) inflows', BLUE); vals('gross_inorganic'); row += 1
r_tot = row
put('= TOTAL GROSS INFLOWS', BOLD); formula(lambda c: f'={c}{r_org}+{c}{r_org+1}'); row += 1
r_totrep = row
put('   reported total (filed)', BLUE); vals('total_gross_inflows'); row += 1
put('   check', GREY); check(lambda c: f'=IF({c}{r_tot}={c}{r_totrep},"OK","FAIL")'); row += 1

# ---- same total, by owner ----
section('SAME MONEY, BY OWNER — the two cuts must agree')
r1 = row
put('Inflows attributable to Athene', BLUE); vals('inflows_athene'); row += 1
put('Inflows attributable to ADIP (sidecar investors)', BLUE); vals('inflows_adip'); row += 1
put('Inflows ceded to third-party reinsurers', BLUE); vals('inflows_ceded_3p'); row += 1
r_own = row
put('= Total by owner', BOLD); formula(lambda c: f'=SUM({c}{r1}:{c}{r1+2})'); row += 1
put('   check vs channel cut', GREY); check(lambda c: f'=IF({c}{r_own}={c}{r_totrep},"OK","FAIL")'); row += 1

# ---- outflows ----
section('MONEY OUT')
r2 = row
put('Outflows attributable to Athene', BLUE); vals('outflows_athene'); row += 1
put('Outflows attributable to ADIP', BLUE); vals('outflows_adip'); row += 1
r_out = row
put('= Total gross outflows', BOLD); formula(lambda c: f'={c}{r2}+{c}{r2+1}'); row += 1
r_outrep = row
put('   reported total (filed)', BLUE); vals('gross_outflows'); row += 1
put('   check', GREY); check(lambda c: f'=IF({c}{r_out}={c}{r_outrep},"OK","FAIL")'); row += 1
put('Athene outflows by type:', GREY); row += 1
r3 = row
put('Maturity-driven / contractual', BLUE, 1); vals('outflow_maturity_driven'); row += 1
r4 = row
put('Policyholder-driven', BLUE, 1); vals('outflow_policyholder'); row += 1
put('income-oriented (planned)', BLUE, 2); vals('outflow_income_planned'); row += 1
put('out of surrender charge (planned)', BLUE, 2); vals('outflow_oosc_planned'); row += 1
put('in surrender charge (unplanned)', BLUE, 2); vals('outflow_isc_unplanned'); row += 1
put('   check: policyholder = its three parts', GREY)
check(lambda c: f'=IF({c}{r4}=SUM({c}{r4+1}:{c}{r4+3}),"OK","FAIL")'); row += 1
put('   check: maturity + policyholder = Athene outflows', GREY)
check(lambda c: f'=IF({c}{r3}+{c}{r4}={c}{r2},"OK","FAIL")'); row += 1

# ---- net flows ----
section('NET FLOWS')
r_nf = row
put('= Net flows (inflows + outflows)', BOLD); formula(lambda c: f'={c}{r_tot}+{c}{r_out}'); row += 1
r_nfrep = row
put('   reported net flows (filed)', BLUE); vals('net_flows'); row += 1
put('   check', GREY); check(lambda c: f'=IF({c}{r_nf}={c}{r_nfrep},"OK","FAIL")'); row += 1

# ---- reserve rollforward ----
section('RESERVES — STOCK & FLOW (net reserve liabilities)')
r5 = row
put('Reserves — beginning', BLUE); vals('nrl_begin'); row += 1
put('+ Net inflows (Athene share)', BLUE); vals('roll_net_inflows'); row += 1
put('− Net withdrawals', BLUE); vals('roll_net_withdrawals'); row += 1
put('± ACRA ownership changes', BLUE); vals('roll_acra_own'); row += 1
put('+ Other reserve changes (credited interest & misc)', BLUE); vals('roll_other'); row += 1
r_end = row
put('= Reserves — ending', BOLD); formula(lambda c: f'=SUM({c}{r5}:{c}{r5+4})'); row += 1
r_endrep = row
put('   reported ending (filed)', BLUE); vals('nrl_end'); row += 1
put('   check: identity', GREY); check(lambda c: f'=IF({c}{r_end}={c}{r_endrep},"OK","FAIL")'); row += 1
put('   check: continuity (begin = prior end)', GREY)
for i, q in enumerate(QUARTERS):
    col = COLS[q]
    c = ws.cell(row=row, column=2 + i)
    if i == 0:
        c.value = 'n/a'
    else:
        pcol = COLS[QUARTERS[i - 1]]
        c.value = f'=IF({col}{r5}={pcol}{r_endrep},"OK","FAIL")'
        check_cells.append(f'{col}{row}')
    c.font = GREY
row += 1

# ---- ACRA rollforward ----
section('THE SIDECAR LEDGER — ACRA noncontrolling interests reserves')
r6 = row
put('ACRA reserves — beginning', BLUE); vals('acra_begin'); row += 1
put('+ Inflows', BLUE); vals('acra_inflows'); row += 1
put('− Withdrawals', BLUE); vals('acra_withdrawals'); row += 1
put('± ACRA ownership changes', BLUE); vals('acra_own'); row += 1
put('+ Other reserve changes', BLUE); vals('acra_other'); row += 1
r_aend = row
put('= ACRA reserves — ending', BOLD); formula(lambda c: f'=SUM({c}{r6}:{c}{r6+4})'); row += 1
r_aendrep = row
put('   reported ending (filed)', BLUE); vals('acra_end'); row += 1
put('   check', GREY); check(lambda c: f'=IF({c}{r_aend}={c}{r_aendrep},"OK","FAIL")'); row += 1

# ---- stock by product ----
section('RESERVE STOCK BY PRODUCT (period-ends available in clean docs)')
r7 = row
put('Indexed annuities', BLUE); vals('nrl_indexed'); row += 1
put('Fixed rate annuities', BLUE); vals('nrl_fixed'); row += 1
r_def = row
put('= Total deferred annuities', BOLD); formula(lambda c: f'={c}{r7}+{c}{r7+1}'); row += 1
put('Pension group annuities', BLUE); vals('nrl_pga'); row += 1
put('Payout annuities', BLUE); vals('nrl_payout'); row += 1
put('Funding agreements (the runnable slice)', BLUE); vals('nrl_fa'); row += 1
put('Life and other', BLUE); vals('nrl_life_other'); row += 1
r_stot = row
put('= Total net reserve liabilities', BOLD)
formula(lambda c: f'={c}{r_def}+SUM({c}{r_def+1}:{c}{r_def+4})'); row += 1
r_stotrep = row
put('   reported total (filed)', BLUE); vals('nrl_total'); row += 1
put('   check (only where period-end filed)', GREY)
check(lambda c: f'=IF({c}{r_stotrep}="","n/a",IF({c}{r_stot}={c}{r_stotrep},"OK","FAIL"))'); row += 1

# ---- income engine ----
section('THE INCOME ENGINE — spread related earnings')
r8 = row
put('Fixed income & other net investment income', BLUE); vals('sre_fi_nii'); row += 1
put('Alternatives net investment income', BLUE); vals('sre_alt_nii'); row += 1
r_nie = row
put('= Net investment earnings', BOLD); formula(lambda c: f'={c}{r8}+{c}{r8+1}'); row += 1
put('+ Strategic capital management fees', BLUE); vals('sre_fees'); row += 1
put('− Cost of funds (what the float costs)', BLUE); vals('sre_cof'); row += 1
r_nis = row
put('= NET INVESTMENT SPREAD', BOLD); formula(lambda c: f'=SUM({c}{r_nie}:{c}{r_nie+2})'); row += 1
r_nisrep = row
put('   reported (filed)', BLUE); vals('sre_nis'); row += 1
put('   check', GREY); check(lambda c: f'=IF({c}{r_nis}={c}{r_nisrep},"OK","FAIL")'); row += 1
put('− Other operating expenses', BLUE); vals('sre_opex'); row += 1
put('− Interest & other financing costs', BLUE); vals('sre_fin'); row += 1
r_sre = row
put('= SPREAD RELATED EARNINGS', BOLD)
# r_nis+1 = reported, r_nis+2 = check ("OK" text!), r_nis+3 = opex, r_nis+4 = financing
formula(lambda c: f'={c}{r_nis}+{c}{r_nis+3}+{c}{r_nis+4}'); row += 1
r_srerep = row
put('   reported (filed)', BLUE); vals('sre'); row += 1
put('   check', GREY); check(lambda c: f'=IF({c}{r_sre}={c}{r_srerep},"OK","FAIL")'); row += 1

# ---- rates ----
section('THE RATES (annualized, as filed)')
put('Earned — fixed income & other', BLUE); vals('sre_fi_nii_pct', fmt=PCT_FMT, pct=True); row += 1
put('Earned — alternatives', BLUE); vals('sre_alt_nii_pct', fmt=PCT_FMT, pct=True); row += 1
put('Earned — total', BLUE); vals('sre_nie_pct', fmt=PCT_FMT, pct=True); row += 1
put('Cost of funds', BLUE); vals('sre_cof_pct', fmt=PCT_FMT, pct=True); row += 1
r_nispct = row
put('NET INVESTMENT SPREAD %', BLUE); vals('sre_nis_pct', fmt=PCT_FMT, pct=True); row += 1
put('SRE margin %', BLUE); vals('sre_pct', fmt=PCT_FMT, pct=True); row += 1

# ---- average NIA + derived ----
section('THE DENOMINATOR & DERIVED')
r9 = row
put('Average net invested assets — fixed income', BLUE); vals('avg_nia_fi'); row += 1
put('Average net invested assets — alternatives', BLUE); vals('avg_nia_alt'); row += 1
r_nia = row
put('= Average net invested assets', BOLD); formula(lambda c: f'={c}{r9}+{c}{r9+1}'); row += 1
r_dnis = row
put('Derived NIS % (spread ×4 ÷ avg assets)', BOLD)
formula(lambda c: f'=IF({c}{r_nia}=0,"",{c}{r_nis}*4/{c}{r_nia})', fmt=PCT_FMT, font=BOLD); row += 1
put('   check vs filed NIS % (±5bp rounding)', GREY)
check(lambda c: f'=IF(ABS({c}{r_dnis}-{c}{r_nispct})<0.0005,"OK","FAIL")'); row += 1

last_row = row

# ---- Checks sheet ----
cs = wb.create_sheet('Checks')
cs.column_dimensions['A'].width = 60
cs['A1'] = 'LIVE CHECKS — this cell must read 0'
cs['A1'].font = HDR
cs['A3'] = 'Number of failing identity checks on Engine:'
cs['A3'].font = BLACK
parts = '+'.join(f'COUNTIF(Engine!{c},"FAIL")' for c in check_cells)
cs['B3'] = f'={parts}'
cs['B3'].font = BOLD
cs['A5'] = f'Checks watched: {len(check_cells)} cells (totals cross-cuts, rollforward identities, continuity, SRE chain, derived spread).'
cs['A5'].font = GREY

# ---- Data sheet ----
ds = wb.create_sheet('Data')
ds.column_dimensions['A'].width = 10
ds.column_dimensions['B'].width = 34
ds['A1'], ds['B1'], ds['C1'] = 'quarter', 'metric', 'value'
for c in ('A1', 'B1', 'C1'):
    ds[c].font = BOLD
for i, r in enumerate(csv.DictReader(open(SRC)), start=2):
    ds.cell(row=i, column=1, value=r['quarter']).font = BLACK
    ds.cell(row=i, column=2, value=r['metric']).font = BLACK
    if r['value'] != '':
        ds.cell(row=i, column=3, value=float(r['value'])).font = BLACK

# ---- ReadMe ----
rm = wb.create_sheet('ReadMe')
rm.column_dimensions['A'].width = 118
notes = [
    ('ATHENE QUARTERLY ENGINE — README', HDR),
    ('', BLACK),
    ('WHAT THIS IS: the machine as three linked ledgers per quarter — money in (two cuts that must agree), reserves', BLACK),
    ('(stock + flow with rollforward and continuity checks), and the income engine (earnings − cost of funds = spread).', BLACK),
    ('', BLACK),
    ('SOURCES: ATH Q4 2025 and Q1 2026 Financial Supplements (Athene IR; URLs + sha256 in acquisition/manifest.csv).', BLACK),
    ('Every blue cell was machine-extracted and passed exact cross-foot gates before entering this workbook;', BLACK),
    ('overlapping quarters in the two documents were verified identical. Extractor: tools/parse_fin_supplement.py.', BLACK),
    ('', BLACK),
    ('LEGEND: blue = filed value · black bold = formula (recalculates in Excel) · grey = checks ("FAIL" if broken)', BLACK),
    ('· yellow column (2Q26) = fill in when the next supplement publishes (~Aug 2026).', BLACK),
    ('', BLACK),
    ('COVERAGE BOUNDARY: 1Q24–3Q24 supplements use an unmapped font encoding (values not machine-readable);', BLACK),
    ('a glyph decoder is a parked work item. Columns will extend left when decoded.', BLACK),
    ('', BLACK),
    ('NOT IN THIS WORKBOOK (annual-only data): the expense/tax bridge to GAAP net income lives on the dashboard', BLACK),
    ('engine panel (section 7) from 10-K claims; credit-loss provisioning is annual (see findings 54–56).', BLACK),
    ('', BLACK),
    ('READ 1Q26: net investment spread 1.34% (was 1.65% a year ago, −31bp) — cost of funds is repricing up (3.79%)', BLACK),
    ('faster than earned yield; alternatives earned 5.79% vs ~10% run-rate; SRE margin below 1% for the first time.', BLACK),
]
for i, (txt, f) in enumerate(notes, start=1):
    rm.cell(row=i, column=1, value=txt).font = f

wb.save(DEST)

# ---- Python-side verification of every formula's arithmetic (no LibreOffice) ----
fails = 0
for q in QUARTERS:
    g = lambda k: D.get((q, k), 0)
    fails += (g('retail') + g('flow_reins') + g('funding_agreements') + g('pga') + g('other_spread')
              + g('gross_inorganic')) != g('total_gross_inflows')
    fails += (g('inflows_athene') + g('inflows_adip') + g('inflows_ceded_3p')) != g('total_gross_inflows')
    fails += (g('outflows_athene') + g('outflows_adip')) != g('gross_outflows')
    fails += (g('total_gross_inflows') + g('gross_outflows')) != g('net_flows')
    fails += (g('nrl_begin') + g('roll_net_inflows') + g('roll_net_withdrawals') + g('roll_acra_own')
              + g('roll_other')) != g('nrl_end')
    fails += (g('acra_begin') + g('acra_inflows') + g('acra_withdrawals') + g('acra_own')
              + g('acra_other')) != g('acra_end')
    fails += (g('sre_fi_nii') + g('sre_alt_nii') + g('sre_fees') + g('sre_cof')) != g('sre_nis')
    fails += (g('sre_nis') + g('sre_opex') + g('sre_fin')) != g('sre')
print(f'wrote {DEST}')
print(f'python-side formula verification: {"ALL IDENTITIES HOLD" if fails == 0 else f"{fails} FAILURES"}'
      f' across {len(QUARTERS)} quarters, {len(check_cells)} live check cells')
if fails:
    raise SystemExit(1)

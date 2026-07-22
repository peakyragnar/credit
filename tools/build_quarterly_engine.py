#!/usr/bin/env python3
"""Build the engine workbook (Michael's stock-and-flow sheet, live) — two mirrored tabs.

Engine    - quarterly columns (4Q24..1Q26 + yellow 2Q26 fill column)
Engine-FY - the SAME rows, annual columns (FY2023 from 10-K MD&A; FY2024/FY2025
            from the Q4'25 supplement's full-year YTD columns, cross-gated
            against the 10-K), plus a live 'FY25 Σ quarters' audit column.
Checks    - live count of failing identity checks (must read 0)
Data      - raw extracted cells (traceability)
ReadMe    - sources, method, legend, coverage boundary

Blue = filed value · black bold = formula · grey = check · yellow = fill-in.
FY2023 cells are blank where the row is published only in supplements (the
older supplements are glyph-encoded); their checks read n/a, never FAIL.
No LibreOffice locally: formula arithmetic is verified in Python at the end.
"""
import csv
import re
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'dossiers/athene/athene-quarterly-engine.xlsx'

# ---- data ----
QD = {}
for r in csv.DictReader(open(ROOT / 'extract/athene/quarterly_supplement.csv')):
    if r['value'] != '':
        QD[(r['quarter'], r['metric'])] = float(r['value'])
AD = {}
for r in csv.DictReader(open(ROOT / 'extract/athene/annual_engine.csv')):
    AD[(r['year'], r['metric'])] = float(r['value'])

QUARTERS = ['4Q24', '1Q25', '2Q25', '3Q25', '4Q25', '1Q26']
FYS = ['FY2023', 'FY2024', 'FY2025']

FYD = {}
for (p, k), v in QD.items():
    if p in ('FY2024', 'FY2025'):
        FYD[(p, k)] = v
for (y, k), v in AD.items():
    FYD.setdefault((y, k), v)                      # 10-K fills FY2023 (+ anything supplements lack)
for fy, q in (('FY2024', '4Q24'), ('FY2025', '4Q25')):
    for k in ('nrl_indexed', 'nrl_fixed', 'nrl_deferred_total', 'nrl_pga', 'nrl_payout',
              'nrl_fa', 'nrl_life_other', 'nrl_total'):
        if (q, k) in QD:
            FYD[(fy, k)] = QD[(q, k)]              # year-end stock = 4Q period-end

BLUE = Font(name='Arial', size=10, color='0000FF')
BLACK = Font(name='Arial', size=10)
BOLD = Font(name='Arial', size=10, bold=True)
HDR = Font(name='Arial', size=11, bold=True)
GREY = Font(name='Arial', size=9, color='666666')
YELLOW = PatternFill('solid', fgColor='FFFF00')
MONEY_FMT = '$#,##0;($#,##0);"-"'
PCT_FMT = '0.00%'

wb = Workbook()

# ---- pass state (rebound per sheet) ----
ws = None
row = 1
PERIODS = []
COLS = {}
DATA = {}
SHEET = ''
FILL = False          # add yellow fill column (quarterly sheet only)
AUDIT = False         # add Σ-quarters audit columns (FY sheet only)
ANNUALIZE = 4         # NIS%-derivation factor: quarterly ×4, annual ×1
REGISTER = False      # record metric -> row (quarterly pass feeds the audit refs)
GUARD = False         # blank-guard the checks (FY pass: missing FY2023 -> n/a)
METRIC_ROW = {}
check_cells = []


def put(label, font=BLACK, indent=0):
    c = ws.cell(row=row, column=1, value=('    ' * indent) + label)
    if label.startswith('='):
        c.data_type = 's'
    c.font = font
    return row


def vals(metric, fmt=MONEY_FMT, pct=False):
    if REGISTER:
        METRIC_ROW.setdefault(metric, row)
    for i, p in enumerate(PERIODS):
        v = DATA.get((p, metric))
        c = ws.cell(row=row, column=2 + i)
        if v is not None:
            c.value = v / 100.0 if pct else v
        c.font = BLUE
        c.number_format = fmt
    if FILL:
        ws.cell(row=row, column=2 + len(PERIODS)).fill = YELLOW
    if AUDIT:
        qrow = METRIC_ROW.get(metric)
        if qrow:
            ac = ws.cell(row=row, column=2 + len(PERIODS),
                         value=f'=SUM(Engine!C{qrow}:F{qrow})' if not pct else '')
            if pct:
                ac.value = None
            else:
                ac.font = BLACK
                ac.number_format = fmt
                fycol = get_column_letter(1 + len(PERIODS))       # FY2025 column
                acol = get_column_letter(2 + len(PERIODS))
                cc = ws.cell(row=row, column=3 + len(PERIODS),
                             value=f'=IF({fycol}{row}="","n/a",IF({acol}{row}={fycol}{row},"OK","FAIL"))')
                cc.font = GREY
                check_cells.append(f"'{SHEET}'!{get_column_letter(3 + len(PERIODS))}{row}")


def formula(fml_by_col, fmt=MONEY_FMT, font=BOLD):
    for i, p in enumerate(PERIODS):
        col = get_column_letter(2 + i)
        c = ws.cell(row=row, column=2 + i, value=fml_by_col(col))
        c.font = font
        c.number_format = fmt


def check(fml_by_col):
    for i, p in enumerate(PERIODS):
        col = get_column_letter(2 + i)
        f = fml_by_col(col)
        if GUARD:
            refs = re.findall(r'[B-H]\d+', f)
            if refs:
                probe = refs[-1]
                inner = f[1:]
                f = f'=IF({probe}="","n/a",{inner})'
        c = ws.cell(row=row, column=2 + i, value=f)
        c.font = GREY
        check_cells.append(f"'{SHEET}'!{col}{row}")


def section(title):
    global row
    row += 1
    put(title, HDR)
    row += 1


def build_body():
    """All sections; identical row structure on both sheets."""
    global row

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

    section('SAME MONEY, BY OWNER — the two cuts must agree')
    r1 = row
    put('Inflows attributable to Athene', BLUE); vals('inflows_athene'); row += 1
    put('Inflows attributable to ADIP (sidecar investors)', BLUE); vals('inflows_adip'); row += 1
    put('Inflows ceded to third-party reinsurers', BLUE); vals('inflows_ceded_3p'); row += 1
    r_own = row
    put('= Total by owner', BOLD); formula(lambda c: f'=SUM({c}{r1}:{c}{r1+2})'); row += 1
    put('   check vs channel cut', GREY); check(lambda c: f'=IF({c}{r_own}={c}{r_totrep},"OK","FAIL")'); row += 1

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

    section('NET FLOWS')
    r_nf = row
    put('= Net flows (inflows + outflows)', BOLD); formula(lambda c: f'={c}{r_tot}+{c}{r_out}'); row += 1
    r_nfrep = row
    put('   reported net flows (filed)', BLUE); vals('net_flows'); row += 1
    put('   check', GREY); check(lambda c: f'=IF({c}{r_nf}={c}{r_nfrep},"OK","FAIL")'); row += 1

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
    for i, p in enumerate(PERIODS):
        col = get_column_letter(2 + i)
        c = ws.cell(row=row, column=2 + i)
        if i == 0:
            c.value = 'n/a'
        else:
            pcol = get_column_letter(1 + i)
            f = f'=IF({col}{r5}={pcol}{r_endrep},"OK","FAIL")'
            if GUARD:
                f = f'=IF({pcol}{r_endrep}="","n/a",IF({col}{r5}={pcol}{r_endrep},"OK","FAIL"))'
            c.value = f
            check_cells.append(f"'{SHEET}'!{col}{row}")
        c.font = GREY
    row += 1

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

    section('RESERVE STOCK BY PRODUCT (period-ends / year-ends)')
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
    # r_nis+1 = reported, r_nis+2 = check, r_nis+3 = opex, r_nis+4 = financing
    formula(lambda c: f'={c}{r_nis}+{c}{r_nis+3}+{c}{r_nis+4}'); row += 1
    r_srerep = row
    put('   reported (filed)', BLUE); vals('sre'); row += 1
    put('   check', GREY); check(lambda c: f'=IF({c}{r_sre}={c}{r_srerep},"OK","FAIL")'); row += 1

    section('THE RATES (annualized, as filed)')
    put('Earned — fixed income & other', BLUE); vals('sre_fi_nii_pct', fmt=PCT_FMT, pct=True); row += 1
    put('Earned — alternatives', BLUE); vals('sre_alt_nii_pct', fmt=PCT_FMT, pct=True); row += 1
    put('Earned — total', BLUE); vals('sre_nie_pct', fmt=PCT_FMT, pct=True); row += 1
    put('Cost of funds', BLUE); vals('sre_cof_pct', fmt=PCT_FMT, pct=True); row += 1
    r_nispct = row
    put('NET INVESTMENT SPREAD %', BLUE); vals('sre_nis_pct', fmt=PCT_FMT, pct=True); row += 1
    put('SRE margin %', BLUE); vals('sre_pct', fmt=PCT_FMT, pct=True); row += 1

    section('THE DENOMINATOR & DERIVED')
    r9 = row
    put('Average net invested assets — fixed income', BLUE); vals('avg_nia_fi'); row += 1
    put('Average net invested assets — alternatives', BLUE); vals('avg_nia_alt'); row += 1
    r_nia = row
    put('= Average net invested assets', BOLD); formula(lambda c: f'={c}{r9}+{c}{r9+1}'); row += 1
    r_dnis = row
    put(f'Derived NIS % (spread ×{ANNUALIZE} ÷ avg assets)', BOLD)
    formula(lambda c: f'=IF(OR({c}{r_nia}=0,{c}{r_nia}=""),"",{c}{r_nis}*{ANNUALIZE}/{c}{r_nia})',
            fmt=PCT_FMT, font=BOLD); row += 1
    put('   check vs filed NIS % (±5bp rounding)', GREY)
    check(lambda c: f'=IF({c}{r_dnis}="","n/a",IF(ABS({c}{r_dnis}-{c}{r_nispct})<0.0005,"OK","FAIL"))'); row += 1


def sheet_header(title, note, extra_cols=()):
    global row
    ws.cell(row=1, column=1, value=title).font = HDR
    row = 2
    put(note, GREY)
    row = 4
    for i, p in enumerate(PERIODS):
        c = ws.cell(row=4, column=2 + i, value=p)
        c.font = BOLD
        c.alignment = Alignment(horizontal='center')
    for j, h in enumerate(extra_cols):
        c = ws.cell(row=4, column=2 + len(PERIODS) + j, value=h)
        c.font = BOLD
        c.alignment = Alignment(horizontal='center')
        if h == '2Q26':
            c.fill = YELLOW
    row = 5


# ================= pass 1: quarterly =================
ws = wb.active
ws.title = 'Engine'
SHEET = 'Engine'
PERIODS = QUARTERS
DATA = QD
FILL, AUDIT, REGISTER, GUARD, ANNUALIZE = True, False, True, False, 4
ws.column_dimensions['A'].width = 46
for i in range(len(PERIODS) + 1):
    ws.column_dimensions[get_column_letter(2 + i)].width = 11
sheet_header('ATHENE — THE QUARTERLY ENGINE  (stock & flow, every line from footed extracts)',
             '$ in millions. Blue = filed value (ATH financial supplements, sha in acquisition/manifest.csv). '
             'Black bold = formula. "check" rows show FAIL if an identity breaks. Yellow column = fill when 2Q26 publishes.',
             extra_cols=('2Q26',))
build_body()

# ================= pass 2: annual =================
ws = wb.create_sheet('Engine-FY')
SHEET = 'Engine-FY'
PERIODS = FYS
DATA = FYD
FILL, AUDIT, REGISTER, GUARD, ANNUALIZE = False, True, False, True, 1
ws.column_dimensions['A'].width = 46
for i in range(len(PERIODS) + 2):
    ws.column_dimensions[get_column_letter(2 + i)].width = 12
sheet_header('ATHENE — THE ANNUAL ENGINE  (same rows; FY2023 from 10-K, FY2024/25 from Q4 supplement YTD, cross-gated)',
             'Blue = filed value (ahl-10k-fy2025 MD&A + ATH Q4\'25 supplement full-year columns; both sources agree exactly '
             'where they overlap). "FY25 Σq" = live sum over the Engine tab — its check must read OK. Blank FY2023 cells = '
             'row published only in supplements (older ones are glyph-encoded; decoder parked); their checks read n/a.',
             extra_cols=('FY25 Σq', 'src-check'))
build_body()

# ================= Checks / Data / ReadMe =================
cs = wb.create_sheet('Checks')
cs.column_dimensions['A'].width = 60
cs['A1'] = 'LIVE CHECKS — this cell must read 0'
cs['A1'].font = HDR
cs['A3'] = 'Number of failing identity checks across Engine + Engine-FY:'
cs['A3'].font = BLACK
parts = '+'.join(f'COUNTIF({c},"FAIL")' for c in check_cells)
cs['B3'] = f'={parts}'
cs['B3'].font = BOLD
cs['A5'] = (f'Checks watched: {len(check_cells)} cells — totals cross-cuts, rollforward identities, continuity, '
            'SRE chain, derived spread, and the quarterly-vs-annual source audit.')
cs['A5'].font = GREY

ds = wb.create_sheet('Data')
ds.column_dimensions['A'].width = 10
ds.column_dimensions['B'].width = 34
for j, h in enumerate(('period', 'metric', 'value', 'source')):
    ds.cell(row=1, column=1 + j, value=h).font = BOLD
i = 2
for r in csv.DictReader(open(ROOT / 'extract/athene/quarterly_supplement.csv')):
    ds.cell(row=i, column=1, value=r['quarter']).font = BLACK
    ds.cell(row=i, column=2, value=r['metric']).font = BLACK
    if r['value'] != '':
        ds.cell(row=i, column=3, value=float(r['value'])).font = BLACK
    ds.cell(row=i, column=4, value='supplement').font = BLACK
    i += 1
for r in csv.DictReader(open(ROOT / 'extract/athene/annual_engine.csv')):
    ds.cell(row=i, column=1, value=r['year']).font = BLACK
    ds.cell(row=i, column=2, value=r['metric']).font = BLACK
    ds.cell(row=i, column=3, value=float(r['value'])).font = BLACK
    ds.cell(row=i, column=4, value='10-K MD&A').font = BLACK
    i += 1

rm = wb.create_sheet('ReadMe')
rm.column_dimensions['A'].width = 118
notes = [
    ('ATHENE ENGINE WORKBOOK — README', HDR),
    ('', BLACK),
    ('TABS: Engine = quarterly (4Q24–1Q26 + yellow 2Q26 fill column). Engine-FY = the SAME rows annually', BLACK),
    ('(FY2023–FY2025) with a live "FY25 Σ quarters" audit column. Checks must read 0. Data = raw extracted cells.', BLACK),
    ('', BLACK),
    ('SOURCES: ATH Q4 2025 + Q1 2026 Financial Supplements (quarterly + full-year YTD columns) and the AHL 10-K', BLACK),
    ('FY2025 MD&A (annual comparatives incl. FY2023). URLs + sha256 in acquisition/manifest.csv. Every blue cell', BLACK),
    ('was machine-extracted and passed exact cross-foot gates; the two sources were gated equal where they overlap.', BLACK),
    ('Extractors: tools/parse_fin_supplement.py, tools/parse_10k_annual_tables.py.', BLACK),
    ('', BLACK),
    ('LEGEND: blue = filed value · black bold = formula (recalculates in Excel) · grey = checks ("FAIL"/"n/a")', BLACK),
    ('· yellow = fill-in. Blank FY2023 cells: those rows are published only in supplements, and the 2023-era', BLACK),
    ('supplements are glyph-encoded (decoder parked). Blanks are honest gaps, not zeros.', BLACK),
    ('', BLACK),
    ('READ THE TREND: cost of funds $5,650M (FY23) → $7,702M → $10,083M (FY25), +78% in two years, while net', BLACK),
    ('investment earnings grew 49%; NIS margin 1.65% (1Q25) → 1.34% (1Q26); SRE margin below 1% in 1Q26.', BLACK),
    ('Volume is outrunning margin, and the margin is losing.', BLACK),
]
for i, (txt, f) in enumerate(notes, start=1):
    rm.cell(row=i, column=1, value=txt).font = f

wb.save(DEST)

# ---- Python-side verification (no LibreOffice): every identity on both sheets ----
fails = []
for periods, data, tag in ((QUARTERS, QD, 'Q'), (FYS, FYD, 'FY')):
    for p in periods:
        g = lambda k: data.get((p, k))
        def has(*ks):
            return all(g(k) is not None for k in ks)
        def eq(lhs, rhs, name):
            if lhs != rhs:
                fails.append(f'{tag}/{p}/{name}: {lhs} != {rhs}')
        if has('retail', 'flow_reins', 'funding_agreements', 'pga', 'other_spread',
               'gross_inorganic', 'total_gross_inflows'):
            eq(g('retail') + g('flow_reins') + g('funding_agreements') + g('pga') + g('other_spread')
               + g('gross_inorganic'), g('total_gross_inflows'), 'inflow chain')
        if has('inflows_athene', 'inflows_adip', 'inflows_ceded_3p', 'total_gross_inflows'):
            eq(g('inflows_athene') + g('inflows_adip') + g('inflows_ceded_3p'),
               g('total_gross_inflows'), 'owner cut')
        if has('outflows_athene', 'outflows_adip', 'gross_outflows'):
            eq(g('outflows_athene') + g('outflows_adip'), g('gross_outflows'), 'outflow cut')
        if has('total_gross_inflows', 'gross_outflows', 'net_flows'):
            eq(g('total_gross_inflows') + g('gross_outflows'), g('net_flows'), 'net flows')
        if has('nrl_begin', 'roll_net_inflows', 'roll_net_withdrawals', 'roll_other', 'nrl_end'):
            eq(g('nrl_begin') + g('roll_net_inflows') + g('roll_net_withdrawals')
               + (g('roll_acra_own') or 0) + g('roll_other'), g('nrl_end'), 'NRL rollforward')
        if has('acra_begin', 'acra_inflows', 'acra_withdrawals', 'acra_other', 'acra_end'):
            eq(g('acra_begin') + g('acra_inflows') + g('acra_withdrawals')
               + (g('acra_own') or 0) + g('acra_other'), g('acra_end'), 'ACRA rollforward')
        if has('sre_fi_nii', 'sre_alt_nii', 'sre_fees', 'sre_cof', 'sre_nis'):
            eq(g('sre_fi_nii') + g('sre_alt_nii') + g('sre_fees') + g('sre_cof'),
               g('sre_nis'), 'NIS chain')
        if has('sre_nis', 'sre_opex', 'sre_fin', 'sre'):
            eq(g('sre_nis') + g('sre_opex') + g('sre_fin'), g('sre'), 'SRE chain')
print(f'wrote {DEST}')
print(f'python verification: {"ALL IDENTITIES HOLD" if not fails else fails[:5]} '
      f'| live check cells: {len(check_cells)}')
if fails:
    raise SystemExit(1)

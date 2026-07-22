#!/usr/bin/env python3
"""Parse Athene quarterly financial-supplement tables (clean-encoding docs only).

Extracts, per document: net flows by channel + attribution + outflow type;
net-reserve-liability stock by product (two period-ends) and rollforwards
(net + ACRA); spread-related earnings ($ rows, rate rows, avg net invested
assets). Sequential template-locked scan: labels are matched IN ORDER, each
row takes the FIRST five value tokens after its label (the five quarterly
columns precede the delta/YTD columns in the print).

Output: extract/athene/quarterly_supplement.csv (long format).
Gates (all exact unless noted): channel sum -> organic; organic+inorganic ->
total; attribution cuts re-sum to totals; rollforward identity; NRL stock sums;
SRE chain; cross-document overlap quarters must match exactly.

The 2024-era supplements use an unmapped glyph encoding (values unrecoverable
by text extraction) — logged as a coverage note; decoder is a parked item.
"""
import csv
import re
import sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
DOCS = [
    ('q4-2025', 'raw/athene/athene-holding/supplements/ath-supplement-q4-2025.pdf'),
    ('q1-2026', 'raw/athene/athene-holding/supplements/ath-supplement-q1-2026.pdf'),
]

MONEY = re.compile(r'\(?\$?\s?\(?(?<![\d.])(\d[\d,]*)(?![\d.,])\)?|(—)')
QTR = re.compile(r'([1-4])Q’(\d{2})')
RATE = re.compile(r'\(?(\d{1,2}\.\d{2})\)?\s?%|(—)')

FLOW_ROWS = [
    ('retail', 'Retail'), ('flow_reins', 'Flow reinsurance'),
    ('funding_agreements', 'Funding agreements'), ('pga', 'Pension group annuities'),
    ('other_spread', ('Other spread products', 'Other')), ('gross_organic', 'Gross organic inflows'),
    ('gross_inorganic', 'Gross inorganic inflows'), ('total_gross_inflows', 'Total gross inflows'),
    ('gross_outflows', 'Gross outflows'), ('net_flows', 'Net flows'),
    ('inflows_athene', 'Inflows attributable to Athene'), ('inflows_adip', 'Inflows attributable to ADIP'),
    ('inflows_ceded_3p', 'Inflows ceded to third-party reinsurers'),
    ('total_gross_inflows_check', 'Total gross inflows'),
    ('outflows_athene', 'Outflows attributable to Athene'), ('outflows_adip', 'Outflows attributable to ADIP'),
    ('total_gross_outflows_check', 'Total gross outflows'),
    ('outflow_maturity_driven', ('Maturity-driven, contractual-based outflows', 'Maturity-driven')),
    ('outflow_policyholder', 'Policyholder-driven outflows'),
    ('outflow_income_planned', ('Income oriented withdrawals (planned)', 'Income oriented withdrawals')),
    ('outflow_oosc_planned', ('From policies out-of-surrender-charge (planned)', 'From policies out-of-surrender-charge')),
    ('outflow_isc_unplanned', ('From policies in-surrender-charge (unplanned)', 'From policies in-surrender-charge')),
    ('core_outflows', 'Core outflows'),
]
NRL_STOCK_ROWS = [
    ('nrl_indexed', 'Indexed annuities'), ('nrl_fixed', 'Fixed rate annuities'),
    ('nrl_deferred_total', 'Total deferred annuities'), ('nrl_pga', 'Pension group annuities'),
    ('nrl_payout', 'Payout annuities'), ('nrl_fa', 'Funding agreements'),
    ('nrl_life_other', 'Life and other'), ('nrl_total', 'Total net reserve liabilities'),
]
ROLL_ROWS = [
    ('nrl_begin', 'Net reserve liabilities – beginning'), ('roll_gross_inflows', 'Gross inflows'),
    ('roll_block', 'Acquisition and block reinsurance'),
    ('roll_acra_nci', 'Inflows attributable to ACRA noncontrolling interests'),
    ('roll_ceded_3p', 'Inflows ceded to third-party reinsurers'),
    ('roll_net_inflows', 'Net inflows'), ('roll_net_withdrawals', 'Net withdrawals'),
    ('roll_acra_own', 'ACRA ownership changes', True),
    ('roll_other', 'Other reserve changes'), ('nrl_end', 'Net reserve liabilities – ending'),
    ('acra_begin', 'Reserve liabilities – beginning'), ('acra_inflows', 'Inflows'),
    ('acra_withdrawals', 'Withdrawals'),
    ('acra_own', 'ACRA ownership changes', True),
    ('acra_other', 'Other reserve changes'),
    ('acra_end', 'Reserve liabilities – ending'),
]
SRE_D_ROWS = [
    ('sre_fi_nii', 'Fixed income and other net investment income'),
    ('sre_alt_nii', 'Alternative net investment income'),
    ('sre_nie', 'Net investment earnings'), ('sre_fees', 'Strategic capital management fees'),
    ('sre_cof', 'Cost of funds'), ('sre_nis', 'Net investment spread'),
    ('sre_opex', 'Other operating expenses'), ('sre_fin', 'Interest and other financing costs'),
    ('sre', 'Spread related earnings'),
]
SRE_R_ROWS = [(k + '_pct', lbl) for k, lbl in SRE_D_ROWS]
SRE_A_ROWS = [
    ('avg_nia_fi', 'Average net invested assets - fixed income and other'),
    ('avg_nia_alt', 'Average net invested assets - alternatives'),
    ('avg_nia', 'Average net invested assets'),
]

MONTH_Q = {'March 31': '1Q', 'June 30': '2Q', 'September 30': '3Q', 'December 31': '4Q'}


def find_page(reader, title):
    for i, p in enumerate(reader.pages):
        t = ' '.join((p.extract_text() or '').split())
        if t.startswith(title) or t[:120].find(title) >= 0:
            return t
    sys.exit(f'PAGE NOT FOUND: {title}')


def money_after(text, pos, n):
    vals = []
    for m in MONEY.finditer(text, pos):
        tok = m.group(0)
        if m.group(2):
            vals.append(0)
        else:
            v = int(m.group(1).replace(',', ''))
            if '(' in tok:
                v = -v
            vals.append(v)
        if len(vals) == n:
            return vals, m.end()
    sys.exit('ran out of value tokens')


def rates_after(text, pos, n):
    vals = []
    for m in RATE.finditer(text, pos):
        if m.group(2):
            vals.append(None)
        else:
            v = float(m.group(1))
            if '(' in m.group(0):
                v = -v
            vals.append(v)
        if len(vals) == n:
            return vals, m.end()
    sys.exit('ran out of rate tokens')


def scan(text, rows, quarters, mode='money'):
    out = {}
    pos = 0
    for idx, row in enumerate(rows):
        key, label = row[0], row[1]
        optional = len(row) > 2 and row[2]
        opts = label if isinstance(label, tuple) else (label,)
        hits = [(text.find(o, pos), o) for o in opts]
        hits = [(i, o) for i, o in hits if i >= 0]
        if optional:
            # consume only if it appears before the next mandatory label
            nxt = rows[idx + 1]
            nopts = nxt[1] if isinstance(nxt[1], tuple) else (nxt[1],)
            npos = min((text.find(o, pos) for o in nopts if text.find(o, pos) >= 0), default=-1)
            if not hits or (npos >= 0 and min(hits)[0] > npos):
                for q in quarters:
                    out[(q, key)] = 0
                continue
        if not hits:
            sys.exit(f'ROW NOT FOUND: {opts!r} after pos {pos}')
        i, label = min(hits, key=lambda t: (t[0], -len(t[1])))
        j = i + len(label)
        fn = re.match(r'\d[\d,]*', text[j:])   # attached footnote marker(s), e.g. 'agreements1', 'outflows6,12'
        if fn:
            j += fn.end()
        vals, j2 = (money_after if mode == 'money' else rates_after)(text, j, len(quarters))
        pos = j if key.endswith('_pct') is False else j  # cursor moves to label; values may overlap next label region
        pos = i + len(label)
        for q, v in zip(quarters, vals):
            out[(q, key)] = v
    return out


def parse_doc(tag, path):
    r = PdfReader(str(ROOT / path))
    res = {}

    tf = find_page(r, 'Net Flows & Outflows Attributable to Athene by Type')
    qm = QTR.findall(tf[:400])[:5]
    quarters = [f'{a}Q{b}' for a, b in qm]
    if len(quarters) != 5:
        sys.exit(f'{tag}: quarter header parse failed')
    res.update(scan(tf, FLOW_ROWS, quarters))

    tr = find_page(r, 'Net Reserve Liabilities & Rollforwards')
    dm = re.findall(r'(March 31|June 30|September 30|December 31), (\d{4})', tr[:300])[:2]
    stock_periods = [f'{MONTH_Q[m]}{y[2:]}' for m, y in dm]
    head = tr[:tr.find('NET RESERVE LIABILITY ROLLFORWARD')]
    res.update(scan(head, NRL_STOCK_ROWS, stock_periods))
    body = tr[tr.find('NET RESERVE LIABILITY ROLLFORWARD'):]
    res.update(scan(body, ROLL_ROWS, quarters))

    ts = find_page(r, 'Spread Related Earnings')
    dollar_zone = ts[:ts.find('Average net invested assets')]
    # dollar rows come first; rate rows repeat the same labels afterwards
    first = scan(dollar_zone, SRE_D_ROWS, quarters)
    res.update(first)
    rate_zone_start = dollar_zone.find('Fixed income and other net investment income',
                                       dollar_zone.find('Spread related earnings') + 10)
    res.update(scan(dollar_zone[rate_zone_start:], SRE_R_ROWS, quarters, mode='rate'))
    avg_zone = ts[ts.find('Average net invested assets'):]
    res.update(scan(avg_zone, SRE_A_ROWS, quarters))
    return res, quarters, stock_periods


def gate(cond, msg):
    if not cond:
        sys.exit(f'GATE FAIL: {msg}')


def main():
    all_res = {}
    for tag, path in DOCS:
        res, quarters, stock_periods = parse_doc(tag, path)
        # within-doc gates, every quarter
        for q in quarters:
            g = lambda k: res[(q, k)]
            gate(g('retail') + g('flow_reins') + g('funding_agreements') + g('pga') + g('other_spread')
                 == g('gross_organic'), f'{tag} {q} channel sum')
            gate(g('gross_organic') + g('gross_inorganic') == g('total_gross_inflows'), f'{tag} {q} organic+inorganic')
            gate(g('inflows_athene') + g('inflows_adip') + g('inflows_ceded_3p')
                 == g('total_gross_inflows_check') == g('total_gross_inflows'), f'{tag} {q} inflow attribution')
            gate(g('outflows_athene') + g('outflows_adip') == g('total_gross_outflows_check')
                 == g('gross_outflows'), f'{tag} {q} outflow attribution')
            gate(g('total_gross_inflows') + g('gross_outflows') == g('net_flows'), f'{tag} {q} net flows')
            gate(g('nrl_begin') + g('roll_net_inflows') + g('roll_net_withdrawals') + g('roll_acra_own')
                 + g('roll_other') == g('nrl_end'), f'{tag} {q} NRL rollforward identity')
            gate(g('acra_begin') + g('acra_inflows') + g('acra_withdrawals') + g('acra_own')
                 + g('acra_other') == g('acra_end'), f'{tag} {q} ACRA rollforward identity')
            gate(g('sre_nie') == g('sre_fi_nii') + g('sre_alt_nii'), f'{tag} {q} NIE sum')
            gate(g('sre_nis') == g('sre_nie') + g('sre_fees') + g('sre_cof'), f'{tag} {q} NIS chain')
            gate(g('sre') == g('sre_nis') + g('sre_opex') + g('sre_fin'), f'{tag} {q} SRE chain')
            gate(g('avg_nia') == g('avg_nia_fi') + g('avg_nia_alt'), f'{tag} {q} avg NIA sum')
        for q in stock_periods:
            g = lambda k: res[(q, k)]
            gate(g('nrl_indexed') + g('nrl_fixed') == g('nrl_deferred_total'), f'{tag} {q} deferred sum')
            gate(g('nrl_deferred_total') + g('nrl_pga') + g('nrl_payout') + g('nrl_fa') + g('nrl_life_other')
                 == g('nrl_total'), f'{tag} {q} NRL stock sum')
        # cross-doc overlap gate
        for key, v in res.items():
            if key in all_res:
                gate(all_res[key] == v, f'overlap mismatch {key}: {all_res[key]} vs {v}')
        all_res.update(res)
        print(f'{tag}: {len(res)} cells, quarters {quarters}, stock {stock_periods} — all gates pass')

    with open(ROOT / 'extract/athene/quarterly_supplement.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['quarter', 'metric', 'value'])
        for (q, k), v in sorted(all_res.items()):
            w.writerow([q, k, '' if v is None else v])
    print(f'wrote extract/athene/quarterly_supplement.csv ({len(all_res)} cells)')


if __name__ == '__main__':
    main()

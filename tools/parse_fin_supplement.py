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

GAAP_ROWS = [
    ('gaap_premiums', 'Premiums'), ('gaap_product_charges', 'Product charges'),
    ('gaap_nii', 'Net investment income'), ('gaap_inv_gl', 'Investment related gains (losses)'),
    ('gaap_other_rev', 'Other revenues'),
    ('gaap_vie_nii', 'Net investment income'), ('gaap_vie_gl', 'Investment related gains (losses)'),
    ('gaap_total_rev', 'Total revenues'),
    ('gaap_iscb', 'Interest sensitive contract benefits'),
    ('gaap_fpb', 'Future policy and other policy benefits'),
    ('gaap_mrb', 'Market risk benefits remeasurement'),
    ('gaap_dac', 'Amortization of deferred acquisition costs'),
    ('gaap_opex', 'Policy and other operating expenses'),
    ('gaap_total_be', 'Total benefits and expenses'),
    ('gaap_pretax', 'Income before income taxes'),
    ('gaap_tax', 'Income tax expense (benefit)'),
    ('gaap_ni', ('Net income (loss)', 'Net income')),
    ('gaap_ni_nci', 'Net income attributable to noncontrolling interests'),
    ('gaap_ni_ahl', ('Net income (loss) attributable to Athene Holding Ltd. stockholders',
                     'Net income attributable to Athene Holding Ltd. stockholders')),
    ('gaap_pref', 'Preferred stock dividends'),
    ('gaap_pref_red', 'Preferred stock redemption'),
    ('gaap_ni_common', 'common stockholder'),
]
NIA_ROWS = [
    ('nia_corporate', 'Corporate'), ('nia_clo', 'CLO'), ('nia_credit_sub', 'Credit'),
    ('nia_cml', 'CML'), ('nia_rml', 'RML'), ('nia_rmbs', 'RMBS'), ('nia_cmbs', 'CMBS'),
    ('nia_real_estate_sub', 'Real estate'), ('nia_abs', 'ABS'),
    ('nia_alts', 'Alternative investments'),
    ('nia_munis_foreign', 'State, municipal, political subdivisions and foreign government'),
    ('nia_equity_sec', 'Equity securities'), ('nia_short_term', 'Short-term investments'),
    ('nia_us_gov', 'US government and agencies'), ('nia_other_inv_sub', 'Other investments'),
    ('nia_cash', 'Cash and cash equivalents'), ('nia_other', 'Other'),
    ('nia_total', 'Net invested assets'),
]
CQ_ROWS = [
    ('cq_naic1', '1 A-G'), ('cq_naic2', '2 A-C'), ('cq_nondesig_ig', 'Non-designated'),
    ('cq_total_ig', 'Total investment grade'),
    ('cq_naic3', '3 A-C'), ('cq_naic4', '4 A-C'), ('cq_naic5', '5 A-C'), ('cq_naic6', ' 6 '),
    ('cq_nondesig_big', 'Non-designated'), ('cq_total_big', 'Total below investment grade'),
    ('cq_total_desig', 'Total NAIC designated assets'),
]
EQ_ROWS = [
    ('eq_apic', 'Additional paid-in capital'), ('eq_re', 'Retained earnings'),
    ('eq_aoci', 'Accumulated other comprehensive loss'),
    ('eq_ahl_total', ("Total Athene Holding Ltd. stockholders' equity",
                      'Total Athene Holding Ltd. stockholders’ equity')),
    ('eq_nci', 'Noncontrolling interests'), ('eq_total', 'Total equity'),
    ('eq_total_le', 'Total liabilities and equity'),
]

BRIDGE_ROWS = [
    ('br_ni_common', 'common stockholder'),
    ('br_pref_red', 'Preferred stock redemption'),
    ('br_pref', 'Preferred stock dividends'),
    ('br_nci', 'noncontrolling interests'),
    ('br_ni', ('Net income (loss)', 'Net income')),
    ('br_tax', 'Income tax expense (benefit)'),
    ('br_pretax', 'Income before income taxes'),
    ('br_realized_sale', 'Realized gains (losses) on sale'),
    ('br_unreal', 'Unrealized, allowances and other'),
    ('br_reins_fv', 'Change in fair value of reinsurance assets'),
    ('br_offsets', 'Offsets to investment gains'),
    ('br_invgl_net', 'Investment gains (losses), net of offsets'),
    ('br_deriv_ia', 'Change in fair values of derivatives and embedded derivatives'),
    ('br_fa_nonop', 'Non-operating change in funding agreements'),
    ('br_mrb_fv', 'Change in fair value of market risk benefits'),
    ('br_fpb_nonop', 'Non-operating change in liability for future policy benefits'),
    ('br_nonop_liab', 'Non-operating change in insurance liabilities and related derivatives'),
    ('br_integration', 'Integration, restructuring and other non-operating items'),
    ('br_stockcomp', 'Stock compensation expense'),
    ('br_pref2', 'Preferred stock dividends'),
    ('br_nci_pretax', 'Noncontrolling interests - pre-tax income and VIE adjustments'),
    ('br_total_adj', 'Total adjustments to income before income taxes'),
    ('br_sre', 'Spread related earnings'),
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
        tail = text[m.end():m.end() + 5]
        if re.match(r'\s?%|\s?bps', tail):
            continue                                # Q/Q, Y/Y, YTD-delta token — not a value
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
        if re.match(r'\s?bps', text[m.end():m.end() + 5]):
            continue
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
    # 'quarters' may include trailing YTD period labels; None labels = parse-and-discard
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
        fn = re.match(r'\d{1,2}(?:,\d{1,2})?(?![\d,])', text[j:])   # footnote marker(s): 1-2 digits, e.g. 'agreements1', 'outflows6,12'
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
    # YTD pair: for a Q4 doc these are the two FULL YEARS; for a Q1 doc they
    # equal the two 1Q columns (kept under gate labels, checked then dropped)
    ytd = {'q4-2025': ['FY2024', 'FY2025'], 'q1-2026': ['GATE_1Q25', 'GATE_1Q26']}[tag]

    tf = find_page(r, 'Net Flows & Outflows Attributable to Athene by Type')
    qm = QTR.findall(tf[:400])[:5]
    quarters = [f'{a}Q{b}' for a, b in qm] + ytd
    if len(quarters) != 7:
        sys.exit(f'{tag}: quarter header parse failed')
    res.update(scan(tf, FLOW_ROWS, quarters))

    tr = find_page(r, 'Net Reserve Liabilities & Rollforwards')
    dm = re.findall(r'(March 31|June 30|September 30|December 31), (\d{4})', tr[:300])[:2]
    stock_periods = [f'{MONTH_Q[m]}{y[2:]}' for m, y in dm]
    head = tr[:tr.find('NET RESERVE LIABILITY ROLLFORWARD')]
    res.update(scan(head, NRL_STOCK_ROWS, stock_periods))
    body = tr[tr.find('NET RESERVE LIABILITY ROLLFORWARD'):]
    res.update(scan(body, ROLL_ROWS, quarters))

    tg = find_page(r, 'Condensed Consolidated Statements of Income')
    res.update(scan(tg, GAAP_ROWS, quarters))

    tn = find_page(r, 'Net Invested Assets (Management view)')
    ndm = re.findall(r'(March 31|June 30|September 30|December 31), (\d{4})', tn[:300])[:2]
    nia_periods = [f'{MONTH_Q[m]}{y[2:]}' for m, y in ndm]
    res.update(scan(tn, NIA_ROWS, nia_periods))

    tq = find_page(r, 'Credit Quality of Net Invested Assets (Management view)')
    res.update(scan(tq, CQ_ROWS, nia_periods))

    te = find_page(r, 'Condensed Consolidated Balance Sheets, continued')
    ez = te[te.find('Total liabilities'):]
    res.update(scan(ez, EQ_ROWS, nia_periods))

    tb = find_page(r, 'Reconciliation of Earnings Measures')
    tb = tb[tb.find('SPREAD RELATED EARNINGS') + 20:]        # skip the table title
    res.update(scan(tb, BRIDGE_ROWS, quarters))

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
        # within-doc gates, every period (quarters AND full-year YTD columns)
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
        # new-table gates (key-presence guarded; run for every period that has them)
        periods_all = sorted({p for (p, k) in res})
        for q in periods_all:
            g = lambda k: res.get((q, k))
            if g('gaap_total_rev') is not None:
                gate(g('gaap_premiums') + g('gaap_product_charges') + g('gaap_nii') + g('gaap_inv_gl')
                     + g('gaap_other_rev') + g('gaap_vie_nii') + g('gaap_vie_gl')
                     == g('gaap_total_rev'), f'{tag} {q} GAAP revenue sum')
                gate(g('gaap_iscb') + g('gaap_fpb') + g('gaap_mrb') + g('gaap_dac') + g('gaap_opex')
                     == g('gaap_total_be'), f'{tag} {q} GAAP expense sum')
                gate(g('gaap_total_rev') - g('gaap_total_be') == g('gaap_pretax'), f'{tag} {q} pretax')
                gate(g('gaap_pretax') - g('gaap_tax') == g('gaap_ni'), f'{tag} {q} NI')
                gate(g('gaap_ni') - g('gaap_ni_nci') == g('gaap_ni_ahl'), f'{tag} {q} NI-AHL')
                gate(g('gaap_ni_ahl') - g('gaap_pref') + g('gaap_pref_red')
                     == g('gaap_ni_common'), f'{tag} {q} NI-common')
            if g('br_sre') is not None:
                gate(g('br_ni_common') - g('br_pref_red') + g('br_pref') + g('br_nci')
                     == g('br_ni'), f'{tag} {q} bridge NI chain')
                gate(g('br_ni') + g('br_tax') == g('br_pretax'), f'{tag} {q} bridge pretax')
                gate(g('br_realized_sale') + g('br_unreal') + g('br_reins_fv') + g('br_offsets')
                     == g('br_invgl_net'), f'{tag} {q} bridge inv-GL net')
                gate(g('br_deriv_ia') + g('br_fa_nonop') + g('br_mrb_fv') + g('br_fpb_nonop')
                     == g('br_nonop_liab'), f'{tag} {q} bridge non-op liabilities')
                gate(g('br_invgl_net') + g('br_nonop_liab') + g('br_integration') + g('br_stockcomp')
                     + g('br_pref2') + g('br_nci_pretax') == g('br_total_adj'), f'{tag} {q} bridge total adj')
                gate(g('br_pretax') - g('br_total_adj') == g('br_sre'), f'{tag} {q} bridge to SRE')
                if g('sre') is not None:
                    gate(g('br_sre') == g('sre'), f'{tag} {q} bridge SRE == engine SRE')
                if g('gaap_ni_common') is not None:
                    gate(g('br_ni_common') == g('gaap_ni_common'), f'{tag} {q} bridge NI-common == GAAP page')
            if g('nia_total') is not None:
                gate(g('nia_credit_sub') == g('nia_corporate') + g('nia_clo'), f'{tag} {q} NIA credit sub')
                gate(g('nia_real_estate_sub') == g('nia_cml') + g('nia_rml') + g('nia_rmbs') + g('nia_cmbs'),
                     f'{tag} {q} NIA real-estate sub')
                gate(g('nia_other_inv_sub') == g('nia_abs') + g('nia_alts') + g('nia_munis_foreign')
                     + g('nia_equity_sec') + g('nia_short_term') + g('nia_us_gov'), f'{tag} {q} NIA other sub')
                gate(g('nia_total') == g('nia_credit_sub') + g('nia_real_estate_sub')
                     + g('nia_other_inv_sub') + g('nia_cash') + g('nia_other'), f'{tag} {q} NIA total')
            if g('cq_total_desig') is not None:
                gate(g('cq_total_ig') == g('cq_naic1') + g('cq_naic2') + g('cq_nondesig_ig'), f'{tag} {q} CQ IG')
                gate(g('cq_total_big') == g('cq_naic3') + g('cq_naic4') + g('cq_naic5') + g('cq_naic6')
                     + g('cq_nondesig_big'), f'{tag} {q} CQ BIG')
                gate(g('cq_total_desig') == g('cq_total_ig') + g('cq_total_big'), f'{tag} {q} CQ total')
            if g('eq_total') is not None:
                gate(g('eq_apic') + g('eq_re') + g('eq_aoci') == g('eq_ahl_total'), f'{tag} {q} equity AHL sum')
                gate(g('eq_ahl_total') + g('eq_nci') == g('eq_total'), f'{tag} {q} equity total')
        # YTD gates
        gkeys = sorted({k for (p, k) in res if p.startswith('GATE_')})
        for gq in ('1Q25', '1Q26'):
            for k in gkeys:
                if (f'GATE_{gq}', k) in res and (gq, k) in res:
                    gate(res[(f'GATE_{gq}', k)] == res[(gq, k)],
                         f'{tag} YTD column mismatch {gq}/{k}')
        res = {(p, k): v for (p, k), v in res.items() if not p.startswith('GATE_')}
        if ('FY2025', 'net_flows') in res:
            fy_qs = ('1Q25', '2Q25', '3Q25', '4Q25')
            for k in sorted({k for (p, k) in res.items() if False} | {k for (p, k) in res if p == 'FY2025'}):
                if k.endswith('_pct') or k.startswith('avg_nia') or k.startswith('nrl_') and k != 'nrl_begin':
                    continue
                if k in ('nrl_begin', 'nrl_end', 'acra_begin', 'acra_end'):
                    continue        # stocks: YTD begin is Jan-1, not summable
                qs = [res.get((q, k)) for q in fy_qs]
                if all(v is not None for v in qs):
                    gate(sum(qs) == res[('FY2025', k)], f'{tag} FY2025 {k} != sum of quarters')
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

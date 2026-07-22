#!/usr/bin/env python3
"""Extract the annual flows and SRE tables (FY2023/24/25) from the AHL 10-K MD&A.

Output: extract/athene/annual_engine.csv (year,metric,value in $M).
Gates: channel sum -> organic -> total; owner cut re-sums to total; net flows;
SRE chain; FY2025 must equal the sum of the four gated supplement quarters.
"""
import csv
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'raw/athene/athene-holding/ahl-10k-fy2025.htm'
QSRC = ROOT / 'extract/athene/quarterly_supplement.csv'
DEST = ROOT / 'extract/athene/annual_engine.csv'
YEARS = ['FY2025', 'FY2024', 'FY2023']          # print order in the 10-K

FLOW_ROWS = [
    ('retail', 'Retail'), ('flow_reins', 'Flow reinsurance'),
    ('funding_agreements', 'Funding agreements'), ('pga', 'Pension group annuities'),
    ('other_spread', 'Other'), ('gross_organic', 'Gross organic inflows'),
    ('gross_inorganic', 'Gross inorganic inflows'), ('total_gross_inflows', 'Total gross inflows'),
    ('gross_outflows', 'Gross outflows'), ('net_flows', 'Net flows'),
    ('inflows_athene', 'Inflows attributable to Athene'),
    ('inflows_adip', 'Inflows attributable to ACRA noncontrolling interests'),
    ('inflows_ceded_3p', 'Inflows ceded to third-party reinsurers'),
]
SRE_ROWS = [
    ('sre_fi_nii', 'Fixed income and other net investment income'),
    ('sre_alt_nii', 'Alternative net investment income'),
    ('sre_nie', 'Net investment earnings'), ('sre_fees', 'Strategic capital management fees'),
    ('sre_cof', 'Cost of funds'), ('sre_nis', 'Net investment spread'),
    ('sre_opex', 'Other operating expenses'), ('sre_fin', 'Interest and other financing costs'),
    ('sre', 'Spread related earnings'),
]
MONEY = re.compile(r'\(?(?<![\d.])(\d[\d,]*)(?![\d.,])\)?|(—)')


def clean_text():
    raw = open(SRC, errors='ignore').read()
    t = re.sub(r'<[^>]+>', '|', raw)
    t = html.unescape(t)
    return re.sub(r'\|+', '|', t).replace('|', ' ')


def scan(zone, rows):
    out = {}
    pos = 0
    for key, label in rows:
        i = zone.find(label, pos)
        if i < 0:
            sys.exit(f'ROW NOT FOUND: {label!r}')
        j = i + len(label)
        # skip a footnote marker: a lone small integer token right after the label
        vals = []
        for m in MONEY.finditer(zone, j):
            if m.group(2):
                vals.append(0)
                continue
            v = int(m.group(1).replace(',', ''))
            if not vals and v <= 9 and len(m.group(1)) == 1:
                continue                       # footnote digit
            vals.append(-v if '(' in m.group(0) else v)
            if len(vals) == 3:
                break
        for y, v in zip(YEARS, vals):
            out[(y, key)] = v
        pos = i + len(label)
    return out


def main():
    t = clean_text()
    fz = t[t.find('The following table presents the inflows and outflows'):]
    fz = fz[:fz.find('Gross inflows were')] if 'Gross inflows were' in fz else fz[:6000]
    res = scan(fz, FLOW_ROWS)
    sz_i = t.find('The following summarizes our  spread related earnings')
    if sz_i < 0:
        sz_i = t.find('summarizes our  spread related earnings')
    sz = t[sz_i:sz_i + 4000]
    res.update(scan(sz, SRE_ROWS))

    def gate(cond, msg):
        if not cond:
            sys.exit(f'GATE FAIL: {msg}')

    for y in YEARS:
        g = lambda k: res[(y, k)]
        gate(g('retail') + g('flow_reins') + g('funding_agreements') + g('pga') + g('other_spread')
             == g('gross_organic'), f'{y} channel sum')
        gate(g('gross_organic') + g('gross_inorganic') == g('total_gross_inflows'), f'{y} organic+inorganic')
        gate(g('inflows_athene') + g('inflows_adip') + g('inflows_ceded_3p')
             == g('total_gross_inflows'), f'{y} owner cut')
        gate(g('total_gross_inflows') + g('gross_outflows') == g('net_flows'), f'{y} net flows')
        gate(g('sre_nie') == g('sre_fi_nii') + g('sre_alt_nii'), f'{y} NIE sum')
        gate(g('sre_nis') == g('sre_nie') + g('sre_fees') + g('sre_cof'), f'{y} NIS chain')
        gate(g('sre') == g('sre_nis') + g('sre_opex') + g('sre_fin'), f'{y} SRE chain')

    # cross-source gate: FY2025 == sum of the four gated supplement quarters
    Q = {}
    for r in csv.DictReader(open(QSRC)):
        if r['value'] != '':
            Q[(r['quarter'], r['metric'])] = float(r['value'])
    for k in ('retail', 'flow_reins', 'funding_agreements', 'pga', 'total_gross_inflows',
              'gross_outflows', 'net_flows', 'sre_cof', 'sre_nis', 'sre'):
        qsum = sum(Q.get((q, k), 0) for q in ('1Q25', '2Q25', '3Q25', '4Q25'))
        gate(qsum == res[('FY2025', k)], f'FY2025 {k}: quarters sum {qsum} != 10-K {res[("FY2025", k)]}')

    with open(DEST, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['year', 'metric', 'value'])
        for (y, k), v in sorted(res.items()):
            w.writerow([y, k, v])
    print(f'wrote {DEST} ({len(res)} cells) — all gates pass incl. quarters-vs-10-K cross-source on FY2025')


if __name__ == '__main__':
    main()

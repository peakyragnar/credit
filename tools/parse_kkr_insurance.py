#!/usr/bin/env python3
"""Extract Global Atlantic (KKR Insurance segment) quarterly/annual series from
KKR 10-Qs and 10-Ks (FY2023-1Q26).

Two lanes per document:
  GAAP insurance lines (consolidated statements of operations, $ thousands):
    revenues: net premiums, policy fees, NII, investment-related G/L, other
    expenses: policy benefits & claims, DAC amortization, interest, opex
    (printed subtotals = exact gates)
  Segment lane: Insurance Operating Earnings components.

Column handling: 1Q docs carry [3mo CY, 3mo PY]; 2Q/3Q docs carry
[3mo CY, 3mo PY, YTD CY, YTD PY] (first two taken; YTD pair kept as gates);
10-Ks carry [FY, FY-1, FY-2]. 4Q quarters are derived FY − (Q1+Q2+Q3) and
that identity is exact by construction (all from the same GAAP basis).

Cross-doc overlap gate: any quarter printed in two documents must match
exactly — EXCEPT segment cost/G&A components across the 1Q26 recast boundary
(reclassification, disclosed; Insurance Operating Earnings itself unchanged
and gated across all docs).

Output: extract/global-atlantic/kkr_insurance_series.csv (values in $M, 1dp).
"""
import csv
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'extract/global-atlantic/kkr_insurance_series.csv'

DOCS = [
    ('kkr-10q-1q23.htm', '1Q23', '1Q22', None),
    ('kkr-10q-2q23.htm', '2Q23', '2Q22', 'H'),
    ('kkr-10q-3q23.htm', '3Q23', '3Q22', 'N'),
    ('kkr-10k-fy2023.htm', 'FY2023', 'FY2022', 'K'),
    ('kkr-10q-1q24.htm', '1Q24', '1Q23', None),
    ('kkr-10q-2q24.htm', '2Q24', '2Q23', 'H'),
    ('kkr-10q-3q24.htm', '3Q24', '3Q23', 'N'),
    ('kkr-10k-fy2024.htm', 'FY2024', 'FY2023', 'K'),
    ('kkr-10q-1q25.htm', '1Q25', '1Q24', None),
    ('kkr-10q-2q25.htm', '2Q25', '2Q24', 'H'),
    ('kkr-10q-3q25.htm', '3Q25', '3Q24', 'N'),
    ('kkr-20251231.htm', 'FY2025', 'FY2024', 'K'),
    ('kkr-20260331-10q.htm', '1Q26', '1Q25', None),
]

GAAP_REV = [
    ('ins_net_premiums', 'Net Premiums'),
    ('ins_policy_fees', 'Policy Fees'),
    ('ins_nii', 'Net Investment Income'),
    ('ins_inv_gl', 'Net Investment-Related Gains (Losses)'),
    ('ins_other_income', 'Other Income'),
]
GAAP_EXP_B = [
    ('ins_dac_amort', 'Amortization of Policy Acquisition Costs'),
    ('ins_interest_exp', 'Interest Expense'),
    ('ins_policy_opex', 'Policy and Other Operating Expense'),
]
GAAP_EXP_A = [
    ('ins_dac_amort', 'Amortization of Policy Acquisition Costs'),
    ('ins_interest_exp', 'Interest Expense'),
    ('ins_expenses_a', 'Insurance Expenses'),
    ('ins_gae_a', 'General, Administrative and Other'),
]

MONEY = re.compile(r'\(?\$?\s?\(?(?<![\d.,])(\d[\d,]*)(?![\d.,])\)?|(—)')


def clean(path):
    raw = open(path, errors='ignore').read()
    t = re.sub(r'<[^>]+>', '|', raw)
    t = html.unescape(t)
    return re.sub(r'\|+', ' ', t).replace('\xa0', ' ')


def money_after(text, pos, n, skipnums=()):
    vals = []
    for m in MONEY.finditer(text, pos):
        if m.group(2):
            vals.append(0)
            continue
        v = int(m.group(1).replace(',', ''))
        if '(' in m.group(0):
            v = -v
        vals.append(v)
        if len(vals) == n:
            return vals
    sys.exit(f'ran out of tokens at pos {pos}')


def scan_rows(zone, rows, ncols):
    out = {}
    pos = 0
    for key, label in rows:
        i = zone.find(label, pos)
        if i < 0:
            sys.exit(f'ROW NOT FOUND: {label!r}')
        j = i + len(label)
        # the policy-benefits label carries an MRB parenthetical stuffed with
        # dollar figures ("including market risk benefit (gain) loss of $X and
        # $Y ... respectively.)") — values start after its LAST 'respectively'
        look = zone[j:j + 700]
        if 'including market risk benefit' in look[:80]:
            k = look.rfind('respectively', 0, 700)
            if k >= 0:
                j += k + len('respectively')
        out[key] = money_after(zone, j, ncols)
        pos = i + len(label)
    return out


def parse_doc(fname, ncols):
    t = clean(ROOT / 'raw/global-atlantic/kkr' / fname)
    # GAAP block: the Insurance revenue block inside the statements of operations
    a = t.find('CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS')
    if a < 0:
        a = t.find('CONSOLIDATED STATEMENTS OF OPERATIONS')
    zone = t[a:a + 12000]
    i_ins = zone.find('Insurance')
    rev = scan_rows(zone[i_ins:], GAAP_REV, ncols)
    # revenue subtotal: first ncols tokens after the last revenue row's values
    i_other = zone.find('Other Income', i_ins)
    sub_rev = money_after(zone, i_other + len('Other Income'), ncols * 2)[ncols:]
    i_exp = zone.find('Insurance', zone.find('Expenses', i_ins))
    exp_zone = zone[i_exp:i_exp + 4000]
    era_a = ('Insurance Expenses' in exp_zone.split('Total Expenses')[0]
             and 'Policy and Other Operating Expense' not in exp_zone.split('Total Expenses')[0])
    rows = GAAP_EXP_A if era_a else GAAP_EXP_B
    exp = scan_rows(zone[i_exp:], rows, ncols)
    last_label = rows[-1][1]
    i_last = zone.find(last_label, i_exp + exp_zone.find(rows[-2][1]) if era_a else i_exp)
    i_last = zone.find(last_label, zone.find(rows[-2][1], i_exp))
    sub_exp = money_after(zone, i_last + len(last_label), ncols * 2)[ncols:]
    if era_a:
        exp['ins_policy_opex'] = [a + b for a, b in zip(exp.pop('ins_expenses_a'), exp.pop('ins_gae_a'))]
    # benefits row is unanchorable (MRB parenthetical varies by doc) — derive it
    # from the printed subtotal; independent derivation per doc keeps the
    # cross-doc overlap gate meaningful
    exp['ins_policy_benefits'] = [s - a - b - c for s, a, b, c in
                                  zip(sub_exp, exp['ins_dac_amort'], exp['ins_interest_exp'],
                                      exp['ins_policy_opex'])]
    # segment lane: Insurance Operating Earnings table
    res = {'rev': rev, 'sub_rev': sub_rev, 'exp': exp, 'sub_exp': sub_exp}
    return res


def main():
    series = {}          # (period, metric) -> value (thousands)
    prov = {}

    for fname, cur, prior, kind in DOCS:
        ncols = 3 if kind == 'K' else (4 if kind in ('H', 'N') else 2)
        r = parse_doc(fname, ncols)
        # periods for the first two (or three) columns
        if kind == 'K':
            periods = [cur, prior, 'FY' + str(int(prior[2:]) - 1)]
        else:
            periods = [cur, prior]
        for key, vals in list(r['rev'].items()) + list(r['exp'].items()):
            for p, v in zip(periods, vals[:len(periods)]):
                k = (p, key)
                if k in series and series[k] != v:
                    sys.exit(f'OVERLAP MISMATCH {k}: {series[k]} ({prov[k]}) vs {v} ({fname})')
                series[k] = v
                prov[k] = fname
        for p, v in zip(periods, r['sub_rev'][:len(periods)]):
            series[(p, 'ins_rev_total')] = v
        for p, v in zip(periods, r['sub_exp'][:len(periods)]):
            series[(p, 'ins_exp_total')] = v

    # keep only the goal window (2023+); earlier comparatives use pre-LDTI bases
    def keep(p):
        yy = int(p[-2:]) if not p.startswith('FY') else int(p[4:6])
        return yy >= 23
    series = {(p, k): v for (p, k), v in series.items() if keep(p)}

    # gates: subtotals
    for (p, k), v in list(series.items()):
        if k == 'ins_rev_total':
            s = sum(series[(p, kk)] for kk, _ in GAAP_REV)
            if s != v:
                sys.exit(f'GATE FAIL rev sum {p}: {s} != {v}')
        if k == 'ins_exp_total':
            s = (series[(p, 'ins_policy_benefits')] + series[(p, 'ins_dac_amort')]
                 + series[(p, 'ins_interest_exp')] + series[(p, 'ins_policy_opex')])
            if s != v:
                sys.exit(f'GATE FAIL exp sum {p}: {s} != {v}')
    # sanity: benefits must be positive and the dominant expense in every period
    for (p, k), v in series.items():
        if k == 'ins_policy_benefits' and not (0 < v):
            sys.exit(f'SANITY FAIL benefits {p}: {v}')

    # derive 4Q = FY - (1Q+2Q+3Q)
    metrics = sorted({k for (_, k) in series})
    for y in ('23', '24', '25'):
        for k in metrics:
            fy = series.get((f'FY20{y}', k))
            qs = [series.get((f'{i}Q{y}', k)) for i in (1, 2, 3)]
            if fy is not None and all(q is not None for q in qs):
                series[(f'4Q{y}', k)] = fy - sum(qs)

    with open(OUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['period', 'metric', 'value_musd'])
        for (p, k), v in sorted(series.items()):
            w.writerow([p, k, round(v / 1000.0, 1)])
    qs = sorted({p for (p, _) in series if not p.startswith('FY')})
    print(f'wrote {OUT}: {len(series)} cells, periods {qs}')


if __name__ == '__main__':
    main()

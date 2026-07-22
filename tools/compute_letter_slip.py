#!/usr/bin/env python3
"""Letter-slip stress (workstream H): re-grade the PL book at yield-implied
ratings and measure the RBC capital impact.

Method: every PL-rated position in the YE2025 D1 extract slips k notches down
the 20-rung designation ladder (k = 1, 2, 3; the D3 yield cross puts the
market-implied slip at 2-3). C-1 charge delta uses the adopted 2021+ pre-tax
factors (reference/naic_c1_bond_factors_2021.csv, banked from Milliman 11/2021).

Ratio translation is an ADVERSE UPPER BOUND: delta-ACL = 0.5 x delta-C1
(full covariance pass-through; the real covariance square root dampens it).
Documented assumptions, not a restatement of the filed RBC.

Gates: PL selection must equal the banked PL total ($40,149,868,714);
factor ladder must cover every slipped designation.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PL_TOTAL = 40_149_868_714
TAC = 9_503_503_398          # aaia_total_adjusted_capital (banked claim)
ACL = 1_090_950_938          # aaia_authorized_control_level_rbc (banked claim)
D1_TOTAL = 158_852_395_199

LADDER = ['1.A', '1.B', '1.C', '1.D', '1.E', '1.F', '1.G',
          '2.A', '2.B', '2.C', '3.A', '3.B', '3.C',
          '4.A', '4.B', '4.C', '5.A', '5.B', '5.C', '6']


def num(s):
    s = (s or '').strip()
    return int(s) if s and s.lstrip('-').isdigit() else 0


def canon(desig):
    d = (desig or '').strip()
    if d.startswith('6'):
        return '6'
    return d


def main():
    F = {r['designation']: float(r['factor_pretax_pct']) / 100
         for r in csv.DictReader(open(ROOT / 'reference/naic_c1_bond_factors_2021.csv'))}
    rows = list(csv.DictReader(open(ROOT / 'extract/athene/sched_d_part1_lines.csv')))
    pl = [r for r in rows if (r['svo_symbol'] or '').strip() == 'PL']
    pl_sum = sum(num(r['bacv']) for r in pl)
    if pl_sum != PL_TOTAL:
        sys.exit(f'GATE FAIL: PL selection {pl_sum:,} != banked {PL_TOTAL:,}')

    bad = {canon(r['naic_designation']) for r in pl} - set(LADDER)
    if bad:
        sys.exit(f'GATE FAIL: unmapped designations {bad}')

    ig_rungs = set(LADDER[:10])          # 1.A .. 2.C
    book_belowig = sum(num(r['bacv']) for r in rows
                       if canon(r['naic_designation']) not in ig_rungs and num(r['bacv']))
    base_c1 = sum(num(r['bacv']) * F[canon(r['naic_designation'])] for r in pl)

    out = []
    print(f'PL book {pl_sum:,} · base C-1 (pre-tax, PL only) ${base_c1/1e6:,.0f}M '
          f'= {base_c1/pl_sum*100:.2f}% avg charge')
    print(f'baseline: TAC {TAC:,} / ACL {ACL:,} = {TAC/ACL*100:.0f}% ACL ({TAC/ACL/2*100:.0f}% CAL) · '
          f'book below-IG ${book_belowig/1e9:.1f}B = {book_belowig/D1_TOTAL*100:.1f}%')
    for k in (1, 2, 3):
        c1 = 0
        fell_ig = 0
        for r in pl:
            d = canon(r['naic_designation'])
            i = min(LADDER.index(d) + k, len(LADDER) - 1)
            c1 += num(r['bacv']) * F[LADDER[i]]
            if d in ig_rungs and LADDER[i] not in ig_rungs:
                fell_ig += num(r['bacv'])
        d_c1 = c1 - base_c1
        acl_new = ACL + 0.5 * d_c1                     # adverse upper bound
        ratio_acl = TAC / acl_new * 100
        belowig_new = book_belowig + fell_ig
        out.append({'slip_notches': k, 'pl_c1_stressed': round(c1),
                    'delta_c1_pretax': round(d_c1),
                    'acl_upper_bound': round(acl_new),
                    'acl_ratio_pct': round(ratio_acl),
                    'cal_ratio_pct': round(ratio_acl / 2),
                    'pl_fell_below_ig': fell_ig,
                    'book_belowig_pct': round(belowig_new / D1_TOTAL * 100, 1)})
        print(f'slip {k}: C-1 ${c1/1e6:,.0f}M (Δ +${d_c1/1e6:,.0f}M) → ACL bound {acl_new/1e9:.2f}B '
              f'→ {ratio_acl:.0f}% ACL / {ratio_acl/2:.0f}% CAL · PL newly below-IG ${fell_ig/1e9:.1f}B '
              f'→ book below-IG {belowig_new/D1_TOTAL*100:.1f}%')

    with open(ROOT / 'extract/athene/letter_slip_stress.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print('wrote extract/athene/letter_slip_stress.csv')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Cross-year Schedule D Part 1 trend aggregates (workstream C payoff).

Reads the per-year footed line extracts (2023, 2024, 2025) and emits
extract/athene/d1_trends.csv: year,dimension,bucket,n_positions,bacv.

Gate: each year's BACV re-sums to its banked control total within the same
logged tolerance the parser carries (see runbook/exceptions.md).
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YEARS = {
    '2023': ('extract/athene/sched_d_part1_lines_2023.csv', 75_192_880_228, 326_724),
    '2024': ('extract/athene/sched_d_part1_lines_2024.csv', 130_962_441_664, 1),
    '2025': ('extract/athene/sched_d_part1_lines.csv', 158_852_395_199, 0),
}
DEST = ROOT / 'extract/athene/d1_trends.csv'

PPN_CHARS = set('#@*')
NOID = '000000-00-0'


def num(s):
    s = (s or '').strip()
    return int(s) if s and s.lstrip('-').isdigit() else 0


def source_group(sym):
    sym = (sym or '').strip()
    if sym in ('FE',): return 'FE (public agency rating)'
    if sym in ('PL', 'PLGI'): return 'PL (private letter)'
    if sym in ('FM', 'FMR'): return 'FM (financially modeled)'
    if sym == '': return 'none (exempt/blank)'
    return 'self/temporary (Z,YE,E,M,GI...)'


def naic_band(desig):
    d = (desig or '').strip()
    return f'NAIC {d[0]}' if d and d[0] in '123456' else 'NAIC ?'


def id_type(cusip):
    c = (cusip or '').strip()
    if c == NOID: return 'no identifier'
    if any(ch in PPN_CHARS for ch in c): return 'PPN (private placement)'
    return 'CUSIP'


def main():
    out = []
    for year, (path, banked, tol) in YEARS.items():
        rows = list(csv.DictReader(open(ROOT / path)))
        total = sum(num(r['bacv']) for r in rows)
        if abs(total - banked) > tol:
            sys.exit(f'FOOTING FAIL {year}: {total:,} vs banked {banked:,} (tol {tol})')
        dims = {
            'total': lambda r: 'all',
            'naic_band': lambda r: naic_band(r['naic_designation']),
            'rating_source': lambda r: source_group(r['svo_symbol']),
            'id_type': lambda r: id_type(r['cusip']),
            'cliff_2C': lambda r: '2.C (BBB-)' if (r['naic_designation'] or '').strip() == '2.C' else 'other',
        }
        for dim, keyfn in dims.items():
            agg_n, agg_v = defaultdict(int), defaultdict(int)
            for r in rows:
                k = keyfn(r)
                agg_n[k] += 1
                agg_v[k] += num(r['bacv'])
            if sum(agg_v.values()) != total:
                sys.exit(f'FOOTING FAIL {year}/{dim}: buckets do not re-sum')
            for k in sorted(agg_v):
                out.append({'year': year, 'dimension': dim, 'bucket': k,
                            'n_positions': agg_n[k], 'bacv': agg_v[k]})
        print(f'{year}: {len(rows)} rows, {total:,} (banked {banked:,}, tol {tol}) OK')

    with open(DEST, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['year', 'dimension', 'bucket', 'n_positions', 'bacv'])
        w.writeheader()
        w.writerows(out)
    print(f'wrote {DEST} ({len(out)} rows)')

    # headline trends to stdout
    tab = {(r['year'], r['dimension'], r['bucket']): r['bacv'] for r in out}
    tot = {y: tab[(y, 'total', 'all')] for y in YEARS}
    for label, dim, bucket in [('PL (private letter)', 'rating_source', 'PL (private letter)'),
                               ('FE (public rating)', 'rating_source', 'FE (public agency rating)'),
                               ('PPN private', 'id_type', 'PPN (private placement)'),
                               ('no identifier', 'id_type', 'no identifier'),
                               ('BBB- cliff (2.C)', 'cliff_2C', '2.C (BBB-)'),
                               ('NAIC 2', 'naic_band', 'NAIC 2'),
                               ('below IG (3-6)', None, None)]:
        vals = []
        for y in YEARS:
            if dim is None:
                v = sum(tab.get((y, 'naic_band', f'NAIC {i}'), 0) for i in '3456')
            else:
                v = tab.get((y, dim, bucket), 0)
            vals.append(f'{v/1e9:6.1f}B ({v/tot[y]*100:4.1f}%)')
        print(f'{label:22s} ' + ' -> '.join(vals))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Aging + maturity-ladder aggregates from Schedule D Part 1 lines (workstream A).

Reads extract/athene/sched_d_part1_lines.csv, emits extract/athene/d1_aging.csv
(long format: table,bucket,split,n_positions,bacv).

Footing gate: every table's BACV must sum to the footed D1 total EXACTLY.
Rows that can't be bucketed (missing date) go to an 'unknown' bucket, never dropped.
Cross-check gate: id-type split must reproduce finding 38 (PPN + no-ID floor).
"""
import csv
import datetime as dt
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import sys
SUFFIX = sys.argv[1] if len(sys.argv) > 1 else ''
SRC = ROOT / f'extract/athene/sched_d_part1_lines{SUFFIX}.csv'
DEST = ROOT / f'extract/athene/d1_aging{SUFFIX}.csv'

AS_OF = dt.date(2023 if SUFFIX.endswith('2023') else 2024 if SUFFIX.endswith('2024') else 2025, 12, 31)
CONTROLS = {'': 158_852_395_199, '_ael2025': 43_049_162_735,
            '_ael2024': 38_063_028_918, '_ael2023': 37_602_643_077}  # gate-banked BACV per book
D1_TOTAL = CONTROLS[SUFFIX]
F38_NOID_ROWS = 481 if SUFFIX == '' else None   # finding 38 — Athene book only
PPN_CHARS = set('#@*')              # PPN charset quirk (runbook)
NOID = '000000-00-0'

RATING_SOURCE = {                   # SVO administrative symbol -> source group
    'FE': 'FE (public agency rating)',
    'PL': 'PL (private letter)',
    'FM': 'FM (financially modeled)',
}
SELF_SYMS = {'Z', 'YE', 'E', 'M', 'GI'}


def parse_date(s):
    s = (s or '').strip()
    try:
        return dt.datetime.strptime(s, '%m/%d/%Y').date()
    except ValueError:
        return None


def num(s):
    s = (s or '').strip().replace(',', '')
    return int(s) if s and s != '-' else 0


def years_between(a, b):
    return (b - a).days / 365.25


def age_bucket(acq):
    if acq is None:
        return 'unknown'
    y = years_between(acq, AS_OF)
    if y < 1: return '<1y'
    if y < 2: return '1-2y'
    if y < 3: return '2-3y'
    if y < 5: return '3-5y'
    if y < 10: return '5-10y'
    return '>=10y'


def maturity_bucket(mat):
    if mat is None:
        return 'unknown'
    if mat.year >= 9999:
        return 'perpetual/no stated maturity'
    if mat <= AS_OF:
        return 'matured, still held'
    y = years_between(AS_OF, mat)
    if y < 1: return '<1y'
    if y < 3: return '1-3y'
    if y < 5: return '3-5y'
    if y < 7: return '5-7y'
    if y < 10: return '7-10y'
    if y < 20: return '10-20y'
    if y < 30: return '20-30y'
    return '>30y'


def rating_source(sym):
    sym = (sym or '').strip()
    if sym in RATING_SOURCE: return RATING_SOURCE[sym]
    if sym in SELF_SYMS: return 'self/temporary (Z,YE,E,M,GI)'
    if sym == '': return 'none (exempt/blank)'
    return f'other ({sym})'


def id_type(cusip):
    c = (cusip or '').strip()
    if c == NOID: return 'no identifier'
    if any(ch in PPN_CHARS for ch in c): return 'PPN (private placement)'
    return 'CUSIP'


def naic_band(desig):
    d = (desig or '').strip()
    return f'NAIC {d[0]}' if d and d[0] in '123456' else 'NAIC ?'


def main():
    rows = list(csv.DictReader(open(SRC)))
    total = sum(num(r['bacv']) for r in rows)
    if total != D1_TOTAL:
        sys.exit(f'FOOTING FAIL: source lines sum {total:,} != control {D1_TOTAL:,}')

    for r in rows:
        r['_bacv'] = num(r['bacv'])
        r['_acq'] = parse_date(r['acquired'])
        r['_mat'] = parse_date(r['maturity'])
        r['_age_b'] = age_bucket(r['_acq'])
        r['_mat_b'] = maturity_bucket(r['_mat'])
        r['_src'] = rating_source(r['svo_symbol'])
        r['_id'] = id_type(r['cusip'])
        r['_naic'] = naic_band(r['naic_designation'])

    # cross-check vs finding 38 (Athene book only; AEL books skip)
    noid_rows = [r for r in rows if r['_id'] == 'no identifier']
    ppn_bacv = sum(r['_bacv'] for r in rows if r['_id'] == 'PPN (private placement)')
    noid_bacv = sum(r['_bacv'] for r in noid_rows)
    if F38_NOID_ROWS is not None and len(noid_rows) != F38_NOID_ROWS:
        sys.exit(f'CROSS-CHECK FAIL: no-ID rows {len(noid_rows)} != finding-38 {F38_NOID_ROWS}')
    print(f'cross-check f38: PPN {ppn_bacv:,} + no-ID {noid_bacv:,} '
          f'= {ppn_bacv + noid_bacv:,} ({(ppn_bacv + noid_bacv) / total * 100:.1f}%)')

    tables = {
        'age_total':          lambda r: (r['_age_b'], 'all'),
        'age_by_source':      lambda r: (r['_age_b'], r['_src']),
        'age_by_id_type':     lambda r: (r['_age_b'], r['_id']),
        'age_by_naic':        lambda r: (r['_age_b'], r['_naic']),
        'maturity_total':     lambda r: (r['_mat_b'], 'all'),
        'maturity_by_source': lambda r: (r['_mat_b'], r['_src']),
    }
    out = []
    for name, keyfn in tables.items():
        agg_n, agg_v = defaultdict(int), defaultdict(int)
        for r in rows:
            k = keyfn(r)
            agg_n[k] += 1
            agg_v[k] += r['_bacv']
        tsum = sum(agg_v.values())
        if tsum != D1_TOTAL:
            sys.exit(f'FOOTING FAIL: table {name} sums {tsum:,} != control {D1_TOTAL:,}')
        for (bucket, split), v in sorted(agg_v.items()):
            out.append({'table': name, 'bucket': bucket, 'split': split,
                        'n_positions': agg_n[(bucket, split)], 'bacv': v})
        print(f'table {name}: foots to {tsum:,} OK')

    # BACV-weighted average age per rating source and id type (dated rows only)
    for name, key in (('wavg_age_by_source', '_src'), ('wavg_age_by_id_type', '_id'),
                      ('wavg_age_total', None)):
        agg_vy, agg_v = defaultdict(float), defaultdict(int)
        for r in rows:
            if r['_acq'] is None:
                continue
            k = 'all' if key is None else r[key]
            agg_vy[k] += r['_bacv'] * years_between(r['_acq'], AS_OF)
            agg_v[k] += r['_bacv']
        for k in sorted(agg_v):
            if agg_v[k]:
                out.append({'table': name, 'bucket': f'{agg_vy[k] / agg_v[k]:.2f}',
                            'split': k, 'n_positions': '', 'bacv': agg_v[k]})

    with open(DEST, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['table', 'bucket', 'split', 'n_positions', 'bacv'])
        w.writeheader()
        w.writerows(out)
    print(f'wrote {DEST} ({len(out)} rows), as-of {AS_OF}, control {D1_TOTAL:,}')


if __name__ == '__main__':
    main()

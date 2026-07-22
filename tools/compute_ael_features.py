#!/usr/bin/env python3
"""AEL bond-book features per year (2023/2024/2025) from the gated Schedule D extracts.

Same rulers as the Athene A/B/C drills: rating-source mix (PL/FE/self/none),
identifier-private floor (PPN charset #@* or no CUSIP), NAIC bands, weighted
holding age at year-end. Top-level keys stay the YE2025 snapshot (dashboard
backcompat); per-year trend under 'years'.
Output: extract/cross-section/ael_bond_features.json
"""
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUFFIX = {'2025': '_ael2025', '2024': '_ael2024', '2023': '_ael2023'}


def num(s):
    s = (s or '').strip().replace(',', '')
    if not s or s in ('XXX',):
        return 0.0
    neg = s.startswith('(') and s.endswith(')')
    s = s.strip('()')
    try:
        v = float(s)
    except ValueError:
        return 0.0
    return -v if neg else v


def source_group(sym):
    sym = (sym or '').strip().upper()
    if sym in ('PL', 'PLGI'):
        return 'PL'
    if sym.startswith('FE'):
        return 'FE'
    if sym in ('FM', 'FMR'):
        return 'FM'
    if sym in ('Z', 'Z*', 'YE', 'IF'):
        return 'self'
    return 'none' if not sym else 'self'


def is_ppn(cusip):
    core = (cusip or '').replace('-', '')
    return any(c in core for c in '#@*')


def year_features(year):
    path = ROOT / f'extract/athene/sched_d_part1_lines{SUFFIX[year]}.csv'
    asof = date(int(year), 12, 31)
    total = 0.0
    src = {}
    ids = {'cusip': 0.0, 'ppn': 0.0, 'noid': 0.0}
    naic = {}
    aged = 0.0
    aged_wt = 0.0
    for r in csv.DictReader(open(path)):
        v = num(r['bacv'])
        total += v
        src[source_group(r['svo_symbol'])] = src.get(source_group(r['svo_symbol']), 0.0) + v
        cus = (r['cusip'] or '').strip()
        if not cus:
            ids['noid'] += v
        elif is_ppn(cus):
            ids['ppn'] += v
        else:
            ids['cusip'] += v
        d = (r['naic_designation'] or '').strip()
        band = d[0] if d and d[0] in '123456' else '?'
        naic[band] = naic.get(band, 0.0) + v
        acq = (r['acquired'] or '').strip()
        try:
            m, dd, y = (int(x) for x in acq.split('/'))
            age = (asof - date(y, m, dd)).days / 365.25
            if age >= 0:
                aged += v
                aged_wt += v * age
        except (ValueError, AttributeError):
            pass
    return {
        'total': round(total),
        'src': {k: round(v) for k, v in sorted(src.items())},
        'ids': {k: round(v) for k, v in ids.items()},
        'naic': {k: round(v) for k, v in sorted(naic.items())},
        'wavg_age': round(aged_wt / aged, 2) if aged else None,
        'pl_share_pct': round(src.get('PL', 0.0) / total * 100, 1),
        'fe_share_pct': round(src.get('FE', 0.0) / total * 100, 1),
        'floor_pct': round((ids['ppn'] + ids['noid']) / total * 100, 1),
        'below_ig_pct': round(sum(v for k, v in naic.items() if k in '3456') / total * 100, 1),
    }


def main():
    years = {y: year_features(y) for y in SUFFIX}
    out = dict(years['2025'])
    out['years'] = years
    dest = ROOT / 'extract/cross-section/ael_bond_features.json'
    json.dump(out, open(dest, 'w'), indent=1)
    print(f'wrote {dest}')
    for y in ('2023', '2024', '2025'):
        f = years[y]
        print(f"  {y}: total ${f['total']:,} | PL {f['pl_share_pct']}% | FE {f['fe_share_pct']}% "
              f"| floor {f['floor_pct']}% | below-IG {f['below_ig_pct']}% | age {f['wavg_age']}y")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Coarse issuer-concentration aggregates from Schedule D Part 1 (workstream B).

Issuer key = first 6 chars of the CUSIP/PPN (the issuer prefix). This is a
FLOOR on concentration: one corporate family can own many prefixes; resolving
families is the D4 engine's job, not this pass. No-ID rows (000000-00-0) are
one explicit bucket — they are NOT one issuer and are labeled as such.

Footing gate: all buckets sum to the D1 control total exactly.
Output: extract/athene/d1_concentration.csv
"""
import csv
import re
import sys
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'extract/athene/sched_d_part1_lines.csv'
DEST = ROOT / 'extract/athene/d1_concentration.csv'
D1_TOTAL = 158_852_395_199
NOID = '000000'

USG_NAME = re.compile(r'UNITED STATES TREASURY|US TREASURY|U S TREASURY|TREASURY STRIP', re.I)
USG_PREFIX = {'912796', '912797', '912803', '912810', '912828', '91282C', '912834'}


def num(s):
    s = (s or '').strip().replace(',', '')
    return int(s) if s and s != '-' else 0


def main():
    rows = list(csv.DictReader(open(SRC)))
    total = sum(num(r['bacv']) for r in rows)
    if total != D1_TOTAL:
        sys.exit(f'FOOTING FAIL: lines sum {total:,} != control {D1_TOTAL:,}')

    groups = defaultdict(lambda: {'bacv': 0, 'n': 0, 'names': Counter(), 'secs': Counter()})
    for r in rows:
        key = (r['cusip'] or '')[:6] or '??????'
        g = groups[key]
        g['bacv'] += num(r['bacv'])
        g['n'] += 1
        d = ' '.join((r['description'] or '').split())
        if d:
            g['names'][d] += 1
        g['secs'][r['section']] += 1

    def name_of(key, g):
        if key == NOID:
            return 'NO IDENTIFIER (many issuers, unidentifiable by construction)'
        return g['names'].most_common(1)[0][0] if g['names'] else '(no description parsed)'

    def is_usgov(key, g):
        if key in USG_PREFIX:
            return True
        nm = name_of(key, g)
        return bool(USG_NAME.search(nm))

    usg_keys = {k for k, g in groups.items() if is_usgov(k, g)}
    usg_bacv = sum(groups[k]['bacv'] for k in usg_keys)
    noid_bacv = groups.get(NOID, {'bacv': 0})['bacv']

    corp = [(k, g) for k, g in groups.items() if k not in usg_keys and k != NOID]
    corp.sort(key=lambda kg: -kg[1]['bacv'])
    corp_bacv = sum(g['bacv'] for _, g in corp)

    if usg_bacv + noid_bacv + corp_bacv != D1_TOTAL:
        sys.exit('FOOTING FAIL: usgov + noid + corp buckets do not sum to control')

    out = []
    for rank, (k, g) in enumerate(corp[:30], 1):
        sec = g['secs'].most_common(1)[0][0]
        out.append({'table': 'top_issuers', 'rank': rank, 'key': k,
                    'name': name_of(k, g)[:70], 'section': sec,
                    'n_positions': g['n'], 'bacv': g['bacv']})

    def cum(n):
        return sum(g['bacv'] for _, g in corp[:n])

    summary = [
        ('d1_total', D1_TOTAL), ('us_government', usg_bacv),
        ('no_identifier_bucket', noid_bacv), ('non_govt_identified', corp_bacv),
        ('n_issuer_prefixes_non_govt', len(corp)),
        ('top10_bacv', cum(10)), ('top25_bacv', cum(25)), ('top50_bacv', cum(50)),
        ('remainder_below_top30', corp_bacv - cum(30)),
    ]
    for k, v in summary:
        out.append({'table': 'summary', 'rank': '', 'key': k, 'name': '',
                    'section': '', 'n_positions': '', 'bacv': v})

    # gate: top30 + remainder + usgov + noid == control
    if cum(30) + (corp_bacv - cum(30)) + usg_bacv + noid_bacv != D1_TOTAL:
        sys.exit('FOOTING FAIL: emitted buckets do not re-sum to control')

    with open(DEST, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['table', 'rank', 'key', 'name', 'section', 'n_positions', 'bacv'])
        w.writeheader()
        w.writerows(out)

    print(f'foots OK: usgov {usg_bacv/1e9:.1f}B ({len(usg_keys)} prefixes) + no-ID {noid_bacv/1e9:.1f}B '
          f'+ corp {corp_bacv/1e9:.1f}B ({len(corp)} prefixes) = {D1_TOTAL:,}')
    print(f'top10 {cum(10)/1e9:.1f}B ({cum(10)/D1_TOTAL*100:.1f}% of book, '
          f'{cum(10)/corp_bacv*100:.1f}% of non-govt identified) · top25 {cum(25)/1e9:.1f}B')
    for r in out[:12]:
        if r['table'] == 'top_issuers':
            print(f"  #{r['rank']:>2} {r['key']} {r['name'][:48]:<48} {r['bacv']/1e9:6.2f}B  n={r['n_positions']}")
    print(f'wrote {DEST}')


if __name__ == '__main__':
    main()

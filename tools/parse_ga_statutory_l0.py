#!/usr/bin/env python3
"""GA US-carrier statutory L0: total admitted assets, total liabilities,
capital & surplus (identity-derived, gated vs printed where found), premiums —
for FLIC / CWA / Accordia / FAFLIC, year-ends 2022-2025 (each doc carries
CY + PY columns). Also captures each carrier's NAIC cocode from the jurat.

Output: extract/global-atlantic/statutory_l0.csv
Gate: assets − liabilities must equal printed capital & surplus (± $1
statement rounding) wherever the printed C&S line is located.
"""
import csv
import re
import sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'extract/global-atlantic/statutory_l0.csv'

DOCS = [
    ('flic', 'flic-4q2025.pdf', 2025), ('flic', 'flic-4q2023.pdf', 2023),
    ('cwa', 'cwa-4q2025.pdf', 2025), ('cwa', 'cwa-4q2023.pdf', 2023),
    ('accordia', 'accordia-4q2025.pdf', 2025), ('accordia', 'accordia-4q2023.pdf', 2023),
    ('faflic', 'faflic-4q2025.pdf', 2025), ('faflic', 'faflic-4q2023.pdf', 2023),
]
MONEY = re.compile(r'(\(?\d[\d,]{5,}\)?)')


def nums(text, pos, n):
    out = []
    for m in MONEY.finditer(text, pos):
        v = int(re.sub(r'[^\d]', '', m.group(1)))
        if m.group(1).startswith('('):
            v = -v
        out.append(v)
        if len(out) >= n:
            return out
    return out


def page_text(r, marker, max_pages=40):
    for i in range(min(len(r.pages), max_pages)):
        t = ' '.join((r.pages[i].extract_text() or '').split())
        if marker in t[:200]:
            return t
    return None


def main():
    rows = []
    cocodes = {}
    for carrier, fname, cy in DOCS:
        path = ROOT / 'raw/global-atlantic/statutory' / fname
        r = PdfReader(str(path))
        jurat = ' '.join((r.pages[0].extract_text() or '').split())
        m = re.search(r'NAIC Group Code[.\s]*\d+[,\s]+(?:\d+\s+)?NAIC Company Code[.\s]*(\d{5})', jurat)
        if not m:
            m = re.search(r'(\d{5})\s*Employer', jurat) or re.search(r'Company Code[.\s]*(\d{5})', jurat)
        if m:
            cocodes[carrier] = m.group(1)

        ta = page_text(r, 'ASSETS Current Year') or page_text(r, 'ASSETS')
        i = ta.find('Total assets excluding Separate Accounts')
        v = nums(ta, i, 4)
        assets_ex = (v[2], v[3])                     # net admitted CY, PY
        j2 = ta.find('Lines 26 and 27')
        if j2 >= 0:
            v2 = nums(ta, j2, 4)
            total_assets = (v2[2], v2[3]) if len(v2) >= 4 else assets_ex
        else:
            total_assets = assets_ex

        tl = page_text(r, 'LIABILITIES, SURPLUS AND OTHER FUNDS')
        k = tl.find('Total liabilities excluding Separate Accounts')
        vl = nums(tl, k, 2)
        liab_ex = (vl[0], vl[1])
        k2 = tl.find('Total liabilities (Lines')
        if k2 >= 0:
            vl2 = nums(tl, k2, 2)
            total_liab = (vl2[0], vl2[1])
        else:
            total_liab = liab_ex
        # printed C&S for the gate
        printed_cs = None
        m2 = re.search(r'Capital and surplus.{0,120}?(\d[\d,]{5,})\s+(\d[\d,]{5,})', tl[k:])
        if m2:
            printed_cs = (int(m2.group(1).replace(',', '')), int(m2.group(2).replace(',', '')))

        ts = page_text(r, 'SUMMARY OF OPERATIONS')
        p = ts.find('Premiums and annuity considerations')
        vp = nums(ts, p, 2)

        for idx, yr in ((0, cy), (1, cy - 1)):
            a, li = total_assets[idx], total_liab[idx]
            cs = a - li
            if printed_cs and abs(printed_cs[idx] - cs) > 1:
                sys.exit(f'GATE FAIL {carrier} {yr}: A-L {cs:,} vs printed C&S {printed_cs[idx]:,}')
            rows += [
                (carrier, yr, 'total_admitted_assets', a),
                (carrier, yr, 'total_liabilities', li),
                (carrier, yr, 'capital_surplus', cs),
                (carrier, yr, 'premiums_annuity_considerations', vp[idx] if len(vp) > idx else ''),
            ]
        print(f'{fname}: assets CY {total_assets[0]:,} · C&S CY {total_assets[0]-total_liab[0]:,}'
              + (' · printed C&S ok' if printed_cs else ' · printed C&S not located (identity only)'))

    with open(OUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['carrier', 'year', 'metric', 'value'])
        w.writerows(rows)
    print('cocodes:', cocodes)
    print(f'wrote {OUT} ({len(rows)} rows)')


if __name__ == '__main__':
    main()

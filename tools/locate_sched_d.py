#!/usr/bin/env python3
"""Locate Schedule D parts + verification pages in a statutory statement PDF.

Usage: locate_sched_d.py <pdf> [start_page_index]
Tries PDF bookmarks first; falls back to scanning page text headers.
Prints 0-based page indexes (pypdf indexing, as used by parse_sched_d.py SECTIONS).
"""
import re
import sys
from pypdf import PdfReader

MARKS = [
    ('D_VERIFICATION', re.compile(r'SCHEDULE\s+D\s*[-–]\s*VERIFICATION', re.I)),
    ('D_PART1', re.compile(r'SCHEDULE\s+D\s*[-–]\s*PART\s*1\b', re.I)),
    ('D_PART3', re.compile(r'SCHEDULE\s+D\s*[-–]\s*PART\s*3\b', re.I)),
    ('D_PART4', re.compile(r'SCHEDULE\s+D\s*[-–]\s*PART\s*4\b', re.I)),
    ('D_PART5', re.compile(r'SCHEDULE\s+D\s*[-–]\s*PART\s*5\b', re.I)),
    ('D_PART6', re.compile(r'SCHEDULE\s+D\s*[-–]\s*PART\s*6\b', re.I)),
    ('SCHEDULE_DA', re.compile(r'SCHEDULE\s+DA\b', re.I)),
]


def walk_outline(reader):
    out = []

    def rec(items, depth=0):
        for it in items:
            if isinstance(it, list):
                rec(it, depth + 1)
            else:
                try:
                    pg = reader.get_destination_page_number(it)
                except Exception:
                    pg = None
                out.append((it.title, pg, depth))
    try:
        rec(reader.outline)
    except Exception:
        pass
    return out


def main():
    path = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    r = PdfReader(path)
    n = len(r.pages)
    print(f'{path}: {n} pages')

    ol = walk_outline(r)
    dhits = [(t, p) for t, p, _ in ol if t and 'schedule d' in t.lower()]
    if dhits:
        print('--- bookmarks mentioning Schedule D:')
        for t, p in dhits:
            print(f'  p{p}: {t}')
        return

    print('--- no usable bookmarks; scanning page headers...')
    found = {}
    for i in range(start, n):
        try:
            t = r.pages[i].extract_text() or ''
        except Exception:
            continue
        head = t[:400]
        for name, rx in MARKS:
            if rx.search(head):
                found.setdefault(name, []).append(i)
        if i % 500 == 0:
            sys.stderr.write(f'  scanned to p{i}\n')
    for name, pages in found.items():
        runs = []
        for p in pages:
            if runs and p == runs[-1][1] + 1:
                runs[-1] = (runs[-1][0], p)
            else:
                runs.append((p, p))
        print(f'{name}: ' + ', '.join(f'{a}-{b}' if a != b else str(a) for a, b in runs))


if __name__ == '__main__':
    main()

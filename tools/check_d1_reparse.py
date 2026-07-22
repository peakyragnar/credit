#!/usr/bin/env python3
"""Regression gate for the description-fix reparse (quirk #10).

The new sched_d_part1_lines.csv must be IDENTICAL to the committed version in
every column except `description` (which goes empty -> populated). Any drift in
money, dates, designations, or row count/order is a FAIL — the fix touched only
desc extraction, so nothing else may move.
"""
import csv
import io
import subprocess
import sys

NEW = 'extract/athene/sched_d_part1_lines.csv'
old_text = subprocess.run(['git', 'show', f'HEAD:{NEW}'],
                          capture_output=True, text=True, check=True).stdout
old = list(csv.DictReader(io.StringIO(old_text)))
new = list(csv.DictReader(open(NEW)))

if len(old) != len(new):
    sys.exit(f'FAIL: row count {len(old)} -> {len(new)}')

drift = 0
filled = 0
for i, (a, b) in enumerate(zip(old, new)):
    for k in a:
        if k == 'description':
            continue
        if a[k] != b[k]:
            drift += 1
            if drift <= 5:
                print(f'DRIFT row {i} col {k}: {a[k]!r} -> {b[k]!r}')
    if (b['description'] or '').strip():
        filled += 1

if drift:
    sys.exit(f'FAIL: {drift} non-description cells changed')
print(f'OK: {len(new)} rows byte-identical outside description; '
      f'description populated on {filled} ({filled/len(new)*100:.1f}%)')

#!/usr/bin/env python3
"""D1 parser: Schedule D Part 1 (Sections 1+2) line-level extraction with footing gates.

Pipeline stages 4-5 per runbook: deterministic parse + gate against banked control totals.
Output: extract/athene/sched_d_part1_lines.csv, subtotals report, exceptions list.
"""
import csv, re, sys, pathlib
from pypdf import PdfReader

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / 'raw/athene/athene-annuity-life-company/aaia-statutory-4q2025.pdf'
SHA = '6580cd4c9b539f8f7ee17d4c176b2c5b041b5fe8923cf3baf6f5b7ddca1e562a'

SECTIONS = [
    ('ICO', 5835, 5910, 85388493721),   # Section 1: issuer credit obligations
    ('ABS', 5911, 6026, 73463901478),   # Section 2: asset-backed securities
]

CUSIP_RE = re.compile(r'^([0-9A-Z#@*]{6}-[0-9A-Z#@*]{2}-[0-9A-Z#@*])\s')
SUBTOT_RE = re.compile(r'^(\d{7,10})[\s.-]+(.*)')
DESIG_RE = re.compile(r'\.\s*([1-6])\.?\s?([A-G]|\*)?\s*([A-Z]{1,4})?\s*\.{2,}(?=\s|$)')
MONEY_RE = re.compile(r'\.{2,}\s?(\(?\d[\d,]{2,}\)?)\s')
DATE_RE = re.compile(r'(\d{2}/\d{2}/\d{4})')
RATE_RE = re.compile(r'\.{2,}(\d{1,2}\.\d{3})\b')

def num(tok):
    neg = tok.startswith('(')
    v = int(re.sub(r'[^\d]', '', tok) or 0)
    return -v if neg else v

def parse_row(chunk):
    m = CUSIP_RE.match(chunk)
    if not m:
        return None
    cusip = m.group(1)
    rest = chunk[m.end():]
    dm = re.search(r'\.{4,}', rest)
    desc = ' '.join(rest[:dm.start()].split()) if dm else ' '.join(rest[:60].split())
    d = DESIG_RE.search(rest)
    desig = f'{d.group(1)}.{d.group(2)}' if d else ''
    svo = (d.group(3) or '') if d else ''
    tail = rest[d.end():] if d else (rest[dm.end():] if dm else rest)
    # positional cell tokenizer: dot-runs are blank cells; dots+digits are values;
    # stop at the first rate-like cell (d.ddd) which begins the rate/date region
    cells = []
    toks = tail.split()
    i = 0
    while i < len(toks):
        tok = toks[i]
        if re.fullmatch(r'\.{2,}', tok):
            nxt = toks[i + 1] if i + 1 < len(toks) else ''
            if re.fullmatch(r'\(?\d[\d,]*\)?', nxt):
                cells.append(num(nxt)); i += 2; continue   # dots + bare number = ONE split cell
            cells.append(None); i += 1; continue            # true blank cell
        if re.fullmatch(r'\.*\d{1,2}\.\d{3}\.*', tok):
            break                                            # rate region begins
        if re.fullmatch(r'\.*\(?\d[\d,]*\)?\.*', tok):
            core = tok.strip('.')
            cells.append(num(core)); i += 1; continue
        i += 1
    def cell(i):
        return cells[i] if i < len(cells) and cells[i] is not None else ''
    rates = [float(x) for x in RATE_RE.findall(tail)]
    dates = DATE_RE.findall(tail)
    return {
        'cusip': cusip, 'description': desc[:80],
        'naic_designation': desig, 'svo_symbol': svo,
        'actual_cost': cell(0), 'par_value': cell(1),
        'fair_value': cell(2), 'bacv': cell(3),
        'stated_rate': rates[0] if rates else '',
        'effective_rate': rates[1] if len(rates) > 1 else '',
        'acquired': dates[-2] if len(dates) >= 2 else '',
        'maturity': dates[-1] if len(dates) >= 1 else '',
    }

def main():
    r = PdfReader(str(PDF))
    all_rows, subtotals, exceptions = [], [], []
    for sec, p0, p1, banked in SECTIONS:
        bodies = []
        for pg in range(p0, p1 + 1):
            text = r.pages[pg].extract_text() or ''
            hm = list(re.finditer(r'Payment\s+Due\s+at\s+Maturity', text[:3000]))
            body = text[hm[-1].end():] if hm else text
            bodies.append((pg, body))
        if True:
            flat = ' '.join(' '.join(b.split('\n')) for _, b in bodies)
            page_of = []  # map char offset -> page for provenance
            off = 0
            for pg, b in bodies:
                blen = len(' '.join(b.split('\n'))) + 1
                page_of.append((off, pg)); off += blen
            def pg_at(pos):
                last = p0
                for o, pgn in page_of:
                    if pos >= o: last = pgn
                    else: break
                return last
            pg = None
            starts = []
            for m in re.finditer(r'(?:(?<=\s)|^)[0-9A-Z#@*]{6}-[0-9A-Z#@*]{2}-[0-9A-Z#@*](?=[\s.])', flat):
                starts.append(m.start())
            for m in re.finditer(r'(?:(?<=\s)|^)\d{7,10}[.\s-]+(?:Sub|Tot)', flat):
                starts.append(m.start())
            starts = sorted(set(starts))
            chunk_spans = list(zip(starts, starts[1:] + [len(flat)]))
            for a, b in chunk_spans:
                ch = flat[a:b]
                pg = pg_at(a)
                sm = SUBTOT_RE.match(ch)
                if sm:
                    code, rest = sm.group(1), sm.group(2)
                    monies = [num(x) for x in re.findall(r'(?:^|\s)(\(?\d[\d,]{2,}\)?)(?=\s|$)', sm.group(2))]
                    label = ' '.join(re.split(r'\.{3,}', rest)[0].split())
                    subtotals.append({'section': sec, 'page': pg, 'code': code,
                                      'label': label[:90], 'monies': monies})
                    continue
                row = parse_row(ch)
                if row is None:
                    continue
                if row['bacv'] == '' and row['par_value'] == '':
                    exceptions.append({'section': sec, 'page': pg,
                                       'reason': 'row parsed without values',
                                       'chunk': ' '.join(ch.split())[:200]})
                    continue
                row['section'] = sec
                row['page'] = pg
                all_rows.append(row)
        sys.stderr.write(f'{sec}: pages done\n')

    out = ROOT / 'extract/athene/sched_d_part1_lines.csv'
    with open(out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['section','page','cusip','description','naic_designation',
                                          'svo_symbol','actual_cost','par_value','fair_value','bacv',
                                          'stated_rate','effective_rate','acquired','maturity'])
        w.writeheader(); w.writerows(all_rows)

    with open(ROOT / 'extract/athene/sched_d_part1_subtotals.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['section','page','code','label','monies'])
        for s in subtotals:
            w.writerow([s['section'], s['page'], s['code'], s['label'], ';'.join(map(str, s['monies']))])

    # GATES: per-section BACV sum vs banked control totals
    print('=== GATES ===')
    for sec, p0, p1, banked in SECTIONS:
        got = sum(r['bacv'] for r in all_rows if r['section'] == sec and r['bacv'] != '')
        n = sum(1 for r in all_rows if r['section'] == sec)
        status = 'PASS' if got == banked else f'FAIL diff {got - banked:+,}'
        print(f'{sec}: rows={n:,}  BACV sum={got:,}  banked={banked:,}  {status}')
    print(f'subtotal lines captured: {len(subtotals)}')
    print(f'exceptions: {len(exceptions)}')
    with open(ROOT / 'extract/athene/sched_d_part1_exceptions.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['section','page','reason','chunk'])
        w.writeheader(); w.writerows(exceptions)

if __name__ == '__main__':
    main()

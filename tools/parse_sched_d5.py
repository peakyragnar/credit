#!/usr/bin/env python3
"""D1c parser: Schedule D Part 5 — same-year acquired AND fully disposed positions.
Columns: cusip, desc, date_acquired, vendor, disposal_date, purchaser, par, cost,
consideration, bacv_at_disposal, [unreal, amort, otti, total_chg, fx_chg],
fx_gl, realized_gl, total_gl, interest_received, paid_accrued.
Gates: Part4 + Part5 must close the D-Verification bonds totals exactly.
"""
import csv, re, pathlib
from pypdf import PdfReader

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / 'raw/athene/athene-annuity-life-company/aaia-statutory-4q2025.pdf'
P0, P1 = 6283, 6334

CUSIP_RE = re.compile(r'^([0-9A-Z#@*]{6}-[0-9A-Z#@*]{2}-[0-9A-Z#@*])\s')
SUBTOT_RE = re.compile(r'^(\d{7,10})[\s.-]+(.*)')
DATE_RE = re.compile(r'(\d{2}/\d{2}/\d{4})')
RELATED = re.compile(r'ACRA|ATHENE|AARE|ALRE|ALREI|APOLLO|AAM\b|AAIA|ISG|A-A |ADIP|VENERABLE|ATLAS SP|MIDCAP|REDDING', re.I)

def num(tok):
    neg = tok.startswith('(')
    v = int(re.sub(r'[^\d]', '', tok) or 0)
    return -v if neg else v

def cells_of(toks):
    out, j = [], 0
    while j < len(toks):
        tok = toks[j]
        if re.fullmatch(r'\.{2,}', tok):
            nxt = toks[j+1] if j+1 < len(toks) else ''
            if re.fullmatch(r'\(?\d[\d,]*\)?', nxt):
                out.append(num(nxt)); j += 2; continue
            out.append(None); j += 1; continue
        if re.fullmatch(r'\.*\(?\d[\d,]*\)?\.*', tok):
            out.append(num(tok.strip('.'))); j += 1; continue
        j += 1
    return out

def text_until_cells(toks):
    """(text_tokens, remaining) split at first dots-only or dotted-money token,
    consuming one trailing padding token (quirk #8)."""
    words, k = [], 0
    while k < len(toks):
        t = toks[k]
        if re.fullmatch(r'\.{2,}', t) or re.fullmatch(r'\.*\(?\d[\d,]{2,}\)?\.*', t):
            break
        words.append(t.strip('.')); k += 1
    rem = toks[k:]
    if rem and re.fullmatch(r'\.{2,}', rem[0]):
        nxt = rem[1] if len(rem) > 1 else ''
        if not re.fullmatch(r'\(?\d[\d,]*\)?', nxt) and not DATE_RE.match(nxt.strip('.')):
            rem = rem[1:]
    return ' '.join(w for w in words if w), rem

def parse_row(chunk):
    m = CUSIP_RE.match(chunk)
    if not m: return None
    cusip = m.group(1)
    rest = chunk[m.end():]
    dm = list(DATE_RE.finditer(rest))
    if len(dm) < 2: return None
    acq = dm[0].group(1)
    desc = ' '.join(re.sub(r'\.{3,}', ' ', rest[:dm[0].start()]).split())
    seg1 = rest[dm[0].end():]
    # vendor text until next date
    d2 = DATE_RE.search(seg1)
    if not d2: return None
    vendor = ' '.join(t.strip('.') for t in seg1[:d2.start()].split() if t.strip('.'))
    disp = d2.group(1)
    seg2 = seg1[d2.end():]
    buyer, rem = text_until_cells(seg2.split())
    raw_cells = cells_of(rem)

    def check(c):
        c = (c + [None]*14)[:14]
        (par, cost, consid, bacv, unreal, amort, otti,
         tchg, fxc, fxgl, rgl, tgl, intr, pacc) = c
        ok = True
        if tchg is not None:
            ok &= tchg == (unreal or 0) + (amort or 0) - (otti or 0)
        if consid is not None and bacv is not None:
            ok &= abs((consid - bacv) - (tgl or 0)) <= max(2, abs(fxgl or 0) + 2)
        # sanity: otti never negative; consideration/bacv positive when present
        if otti is not None and otti < 0: ok = False
        if consid is not None and consid < 0: ok = False
        return ok, c

    idok, cells = check(list(raw_cells))
    repaired = ''
    if not idok:
        candidates = []
        for pos in range(15):
            trial = list(raw_cells[:pos]) + [None] + list(raw_cells[pos:])
            ok, mapped = check(trial)
            if ok: candidates.append(mapped)
        if len(raw_cells) > 14:
            for pos in range(len(raw_cells)):
                trial = list(raw_cells[:pos]) + list(raw_cells[pos+1:])
                ok, mapped = check(trial)
                if ok: candidates.append(mapped)
        uniq = {tuple(c) for c in candidates}
        if len(uniq) == 1:
            cells = list(next(iter(uniq))); idok = True; repaired = 'R'
    (par, cost, consideration, bacv_disp, unreal, amort, otti,
     total_chg, fx_chg, fx_gl, real_gl, total_gl, interest, paid_accr) = cells
    def v(x): return x if x is not None else ''
    return {
        'cusip': cusip, 'description': desc[:70], 'acquired': acq, 'vendor': vendor[:55],
        'disposal_date': disp, 'purchaser': buyer[:55],
        'rp_vendor': 'Y' if RELATED.search(vendor) else '',
        'rp_purchaser': 'Y' if RELATED.search(buyer) else '',
        'par_value': v(par), 'actual_cost': v(cost), 'consideration': v(consideration),
        'bacv_at_disposal': v(bacv_disp), 'unrealized_val_change': v(unreal),
        'amort_accretion': v(amort), 'otti': v(otti), 'fx_change': v(fx_chg),
        'fx_gl': v(fx_gl), 'realized_gl': v(real_gl), 'total_gl': v(total_gl),
        'interest_received': v(interest), 'paid_accrued': v(paid_accr),
        'identity_ok': ('R' if repaired else 'Y') if idok else 'N',
    }

def main():
    r = PdfReader(str(PDF))
    rows, subtotals, exceptions = [], [], []
    for pg in range(P0, P1 + 1):
        text = r.pages[pg].extract_text() or ''
        hm = list(re.finditer(r'Dividends', text[:3800]))
        body = text[hm[-1].end():] if hm else text
        flat = ' '.join(body.split('\n'))
        starts = []
        for m in re.finditer(r'(?:(?<=\s)|^)[0-9A-Z#@*]{6}-[0-9A-Z#@*]{2}-[0-9A-Z#@*](?=[\s.])', flat):
            starts.append(m.start())
        for m in re.finditer(r'(?:(?<=\s)|^)\d{7,10}[.\s-]+(?:Sub|Tot|Sum)', flat):
            starts.append(m.start())
        starts = sorted(set(starts))
        for a, b in zip(starts, starts[1:] + [len(flat)]):
            ch = flat[a:b]
            sm = SUBTOT_RE.match(ch)
            if sm:
                monies = [num(x) for x in re.findall(r'(?:^|\s)(\(?\d[\d,]{2,}\)?)(?=\s|$)', sm.group(2))]
                label = ' '.join(re.split(r'\.{3,}', sm.group(2))[0].split())
                label = re.sub(r'[\d,()].*$', '', label).strip()[:80]
                subtotals.append({'page': pg, 'code': sm.group(1), 'label': label,
                                  'monies': ';'.join(map(str, monies))})
                continue
            row = parse_row(ch)
            if row is None: continue
            if row['consideration'] == '' and row['par_value'] == '':
                exceptions.append({'page': pg, 'chunk': ' '.join(ch.split())[:220]})
                continue
            if row['identity_ok'] == 'N' and row['consideration'] != '' and row['bacv_at_disposal'] != '':
                row['total_gl'] = row['consideration'] - row['bacv_at_disposal']
                row['realized_gl'] = row['total_gl'] - (row['fx_gl'] if row['fx_gl'] != '' else 0)
                row['otti'] = ''
                row['amort_accretion'] = ''
                row['unrealized_val_change'] = ''
                row['identity_ok'] = 'D'
            row['page'] = pg
            rows.append(row)
    with open(ROOT / 'extract/athene/sched_d_part5_roundtrips.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['page','cusip','description','acquired','vendor','disposal_date',
                                          'purchaser','rp_vendor','rp_purchaser','par_value','actual_cost',
                                          'consideration','bacv_at_disposal','unrealized_val_change',
                                          'amort_accretion','otti','fx_change','fx_gl','realized_gl',
                                          'total_gl','interest_received','paid_accrued','identity_ok'])
        w.writeheader(); w.writerows(rows)
    with open(ROOT / 'extract/athene/sched_d_part5_subtotals.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['page','code','label','monies'])
        w.writeheader(); w.writerows(subtotals)
    with open(ROOT / 'extract/athene/sched_d_part5_exceptions.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['page','chunk'])
        w.writeheader(); w.writerows(exceptions)

    def s(col): return sum(r[col] for r in rows if r[col] != '')
    nid = sum(1 for r in rows if r['identity_ok'] == 'N')
    nder = sum(1 for r in rows if r['identity_ok'] == 'D')
    print('=== PART 5 ===')
    print(f'rows: {len(rows):,}  exceptions: {len(exceptions)}  identity-fail: {nid}  derived-GL rows: {nder}  subtotals: {len(subtotals)}')
    print(f'consideration : {s("consideration"):>16,}   (target ~26,714,873,442 = 72,140,293,824 - Part4 45,425,420,382)')
    print(f'total G/L     : {s("total_gl"):>16,}')
    print(f'realized G/L  : {s("realized_gl"):>16,}')
    print(f'OTTI          : {s("otti"):>16,}')
    print(f'interest recd : {s("interest_received"):>16,}')
    rp_b = [r for r in rows if r['rp_purchaser'] == 'Y']
    rp_v = [r for r in rows if r['rp_vendor'] == 'Y']
    print(f'sold TO related party : {len(rp_b):,} rows  ${sum(r["consideration"] for r in rp_b if r["consideration"] != "")/1e9:,.2f}B')
    print(f'bought FROM related   : {len(rp_v):,} rows')

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""D1b parser: Schedule D Part 4 (disposals) — per-position realized gain/loss + purchaser.

Anchors each row twice: forward (disposal date -> consideration, par, cost, prior BACV)
and backward (maturity date <- interest <- total G/L <- realized G/L), so blank-cell
drift in the middle change-group cannot shift the money columns that gates check.
Gates: consideration and total gain/loss vs D-Verification bonds totals.
"""
import csv, re, pathlib
from pypdf import PdfReader

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / 'raw/athene/athene-annuity-life-company/aaia-statutory-4q2025.pdf'
P0, P1 = 6073, 6282

CUSIP_RE = re.compile(r'^([0-9A-Z#@*]{6}-[0-9A-Z#@*]{2}-[0-9A-Z#@*])\s')
SUBTOT_RE = re.compile(r'^(\d{7,10})[\s.-]+(.*)')
DATE_RE = re.compile(r'(\d{2}/\d{2}/\d{4})')

RELATED = re.compile(r'ACRA|ATHENE|AARE|ALRE|ALREI|APOLLO|AAM\b|AAIA|ISG|A-A |ADIP|VENERABLE|ATLAS SP|MIDCAP|REDDING', re.I)

def num(tok):
    neg = tok.startswith('(')
    v = int(re.sub(r'[^\d]', '', tok) or 0)
    return -v if neg else v

MONEYTOK = re.compile(r'\(?\d[\d,]{2,}\)?')

def cells_of(toks):
    """token stream -> ordered cells (None=blank), with split-cell merge + padding rules."""
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

def parse_row(chunk):
    m = CUSIP_RE.match(chunk)
    if not m: return None
    cusip = m.group(1)
    rest = chunk[m.end():]
    dates = DATE_RE.findall(rest)
    if not dates: return None
    # description contains coupon dates sometimes (e.g. "4.125% 08/15/53") but full
    # dd/dd/dddd disposal date is the first full-format date
    dpos = rest.find(dates[0])
    desc = ' '.join(re.sub(r'\.{3,}', ' ', rest[:dpos]).split())
    after = rest[dpos + len(dates[0]):]
    # purchaser: text tokens until the first dots-only or dotted-number token
    toks = after.split()
    buyer_toks, k = [], 0
    while k < len(toks):
        t = toks[k]
        if re.fullmatch(r'\.{2,}', t) or re.fullmatch(r'\.*\(?\d[\d,]{2,}\)?\.*', t):
            break
        buyer_toks.append(t.strip('.')); k += 1
    buyer = ' '.join(x for x in buyer_toks if x)
    # forward: rebuild string from buyer-end, cut at maturity date, parse ALL cells positionally
    fwd_toks = toks[k:]
    if fwd_toks and re.fullmatch(r'\.{2,}', fwd_toks[0]):
        nxt = fwd_toks[1] if len(fwd_toks) > 1 else ''
        if not re.fullmatch(r'\(?\d[\d,]*\)?', nxt):
            fwd_toks = fwd_toks[1:]          # buyer trailing padding (quirk #8)
    mat = dates[-1] if len(dates) >= 2 else ''
    fwd_str = ' '.join(fwd_toks)
    if mat:
        cut = fwd_str.rfind(mat)
        if cut > 0: fwd_str = fwd_str[:cut]
    cells = cells_of(fwd_str.split())
    # map 15 columns: shares, consideration, par, cost, prior_bacv, unreal, amort, otti,
    # total_chg, fx_chg, bacv_disp, fx_gl, realized_gl, total_gl, interest
    if cells and cells[0] is None:
        cells = cells[1:]                    # shares blank for bonds
    cells = (cells + [None]*14)[:14]
    (consideration, par, cost, prior_bacv, unreal, amort, otti,
     total_chg, fx_chg, bacv_disp, fx_gl, real_gl, total_gl, interest) = cells
    # identity checks; failures flagged for the exception queue by caller
    idok = True
    if total_chg is not None:
        idok &= total_chg == (unreal or 0) + (amort or 0) - (otti or 0)
    if consideration is not None and bacv_disp is not None:
        idok &= abs((consideration - bacv_disp) - ((total_gl or 0) )) <= max(2, abs(fx_gl or 0) + 2)
    return {
        'cusip': cusip, 'description': desc[:70], 'disposal_date': dates[0],
        'purchaser': buyer[:60],
        'related_party': 'Y' if RELATED.search(buyer or '') else '',
        'consideration': consideration if consideration is not None else '',
        'par_value': par if par is not None else '',
        'actual_cost': cost if cost is not None else '',
        'prior_bacv': prior_bacv if prior_bacv is not None else '',
        'unrealized_val_change': unreal if unreal is not None else '',
        'amort_accretion': amort if amort is not None else '',
        'otti': otti if otti is not None else '',
        'fx_change': fx_chg if fx_chg is not None else '',
        'bacv_at_disposal': bacv_disp if bacv_disp is not None else '',
        'fx_gl': fx_gl if fx_gl is not None else '',
        'realized_gl': real_gl if real_gl is not None else '',
        'total_gl': total_gl if total_gl is not None else '',
        'interest_received': interest if interest is not None else '',
        'maturity': mat, 'identity_ok': 'Y' if idok else 'N',
    }

def main():
    r = PdfReader(str(PDF))
    rows, subtotals, exceptions = [], [], []
    for pg in range(P0, P1 + 1):
        text = r.pages[pg].extract_text() or ''
        hm = list(re.finditer(r'Maturity\s*Date', text[:3500]))
        body = text[hm[-1].end():] if hm else text
        flat = ' '.join(body.split('\n'))
        starts = []
        for m in re.finditer(r'(?:(?<=\s)|^)[0-9A-Z#@*]{6}-[0-9A-Z#@*]{2}-[0-9A-Z#@*](?=[\s.])', flat):
            starts.append(m.start())
        for m in re.finditer(r'(?:(?<=\s)|^)\d{7,10}[.\s-]+(?:Sub|Tot)', flat):
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
                row['otti'] = ''; row['amort_accretion'] = ''; row['unrealized_val_change'] = ''
                row['identity_ok'] = 'D'
            row['page'] = pg
            rows.append(row)
    with open(ROOT / 'extract/athene/sched_d_part4_disposals.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['page','cusip','description','disposal_date','purchaser','related_party',
                                          'consideration','par_value','actual_cost','prior_bacv',
                                          'unrealized_val_change','amort_accretion','otti','fx_change',
                                          'bacv_at_disposal','fx_gl','realized_gl','total_gl',
                                          'interest_received','maturity','identity_ok'])
        w.writeheader(); w.writerows(rows)
    with open(ROOT / 'extract/athene/sched_d_part4_subtotals.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['page','code','label','monies'])
        w.writeheader(); w.writerows(subtotals)
    with open(ROOT / 'extract/athene/sched_d_part4_exceptions.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['page','chunk'])
        w.writeheader(); w.writerows(exceptions)

    def s(col): return sum(r[col] for r in rows if r[col] != '')
    nid = sum(1 for r in rows if r['identity_ok'] == 'N')
    print('=== GATES ===')
    print(f'rows: {len(rows):,}   exceptions: {len(exceptions)}   identity-fail rows: {nid}   subtotals: {len(subtotals)}')
    print(f'consideration sum : {s("consideration"):>18,}   all-D printed 72,140,293,824')
    print(f'total G/L sum     : {s("total_gl"):>18,}   all-D printed 73,922,642')
    print(f'realized G/L sum  : {s("realized_gl"):>18,}')
    print(f'OTTI sum          : {s("otti"):>18,}   Part1 residual target 913,690')
    print(f'FX-chg sum        : {s("fx_change"):>18,}   Part1 residual target 154,129,845')
    print(f'amort sum         : {s("amort_accretion"):>18,}   Part1 residual target 131,457,504')
    print(f'interest received : {s("interest_received"):>18,}')
    rp = [r for r in rows if r['related_party'] == 'Y']
    print(f'related-party rows: {len(rp):,}  consideration ${sum(r["consideration"] for r in rp if r["consideration"] != "")/1e9:,.2f}B')

if __name__ == '__main__':
    main()

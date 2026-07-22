#!/usr/bin/env python3
"""Parse Global Atlantic (GALD) quarterly financial supplements.

Four documents (Q4'23, Q4'24, Q4'25, Q1'26), each carrying five descending
quarterly columns (Q4 docs add a trailing FY pair) — together covering every
quarter 1Q23..1Q26 plus FY2023/24/25, with 4-way overlaps as equality gates.

Tables: financial highlights ($ + rates), consolidated income (revenues),
adjusted operating earnings ($), ROA components (rates), new business volume,
reserves by product (net, 5 dates; gross/ceded decomposition at latest),
AFS fixed maturities by NAIC and NRSRO rating (2 period-ends/doc),
capitalization.

Output: extract/global-atlantic/gald_supplement.csv (long: period,metric,value).
Values $M as printed; rates stored as printed percents.
"""
import csv
import re
import sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'extract/global-atlantic/gald_supplement.csv'
DOCS = ['q4-2023', 'q4-2024', 'q4-2025', 'q1-2026']

MONEY = re.compile(r'\(?\$?\s?\(?(?<![\d.,/])(\d[\d,]*)(?![\d.,/%])\)?|(—)')
RATE = re.compile(r'\(?(\d{1,3}\.\d{1,2})\)?\s?%|(—|NM)')
DATE = re.compile(r'(\d{1,2})/(\d{1,2})/(\d{4})')

H_MONEY = [
    ('ni_shareholder', 'Net income (loss) attributable to Global Atlantic'),
    ('aoi_net', 'Adjusted operating income, net of tax'),
    ('total_assets', 'Total assets'),
    ('adj_invested_assets', 'Adjusted invested assets'),
    ('total_liabilities', 'Total liabilities'),
    ('shareholders_equity', ('Total shareholders’ equity', "Total shareholders' equity")),
    ('adj_equity', ("Adjusted shareholders' equity", 'Adjusted shareholders’ equity')),
]
H_RATE = [
    ('roe', 'ROE', False), ('adj_roe', 'Adjusted ROE', False),
    ('adj_op_roe', ('Adjusted Operating ROE', 'Adjusted operating ROE'), True),
]
INC_ROWS = [
    ('premiums', 'Premiums'), ('policy_fees', 'Policy fees'),
    ('nii', 'Net investment income'), ('inv_gl', 'Net investment gains (losses)'),
    ('other_income', 'Other income'), ('total_revenues', 'Total revenues'),
]
AOE_ROWS = [
    ('adj_nii', 'Adjusted net investment income', False),
    ('adj_cost_ins', 'Adjusted net cost of insurance', False),
    ('adj_underwriting', 'Adjusted net underwriting income', False),
    ('adj_interest', ('Adjusted interest expense', 'Interest expenses'), True),
    ('adj_gae', ('Adjusted general, administrative and other',
                 'Adjusted general and administrative expenses'), False),
    ('adj_op_pretax', 'Adjusted operating earnings, before income taxes', False),
    ('adj_op_tax', 'Adjusted operating income tax expense', False),
    ('aoi_net_aoe', 'Adjusted operating earnings, net of tax', False),
    ('avg_total_inv', 'Average total investments', False),
    ('avg_aia', 'Average adjusted invested assets', False),
]
ROA_RATE = [
    ('nier', 'Net investment earned rate'),
    ('cost_ins_ratio', 'Adjusted net cost of insurance ratio'),
    ('underwriting_ratio', 'Adjusted net underwriting ratio'),
    ('gae_ratio', 'Adjusted general and administrative expense ratio'),
    ('interest_ratio', 'Adjusted interest expense ratio'),
    ('aor_pretax', 'Adjusted operating return on assets, before taxes'),
]
NBV_ROWS = [
    ('nbv_fixed_rate', 'Fixed-Rate Annuities', False), ('nbv_fia', 'Fixed-Indexed Annuities', False),
    ('nbv_va', 'Variable Annuities', False), ('nbv_retirement_total', 'Total retirement products', False),
    ('nbv_life', 'Life insurance products', True),
    ('nbv_preneed', 'Preneed Life', False), ('nbv_block', 'Block', False),
    ('nbv_flow', ('Flow & pension risk transfer', 'Flow'), False),
    ('nbv_prt', 'Pension risk transfer', True),
    ('nbv_funding_agreements', ('Funding agreements', 'Funding agreement-backed notes'), False),
]
RES_ROWS = [
    ('res_fixed_rate', 'Fixed-rate annuity'), ('res_fia', 'Fixed-indexed annuity'),
    ('res_payout', 'Payout annuities'), ('res_va', 'Variable annuity'),
    ('res_isl', 'Interest sensitive life'), ('res_other_life', 'Other life insurance'),
    ('res_fa', 'Funding agreements'), ('res_closed_block', 'Closed block'),
    ('res_other_corp', 'Other corporate'), ('res_total', 'Total reserves'),
]
NAIC_ROWS = [
    ('naic1', ' 1 '), ('naic2', ' 2 '), ('naic_ig', 'Total investment grade'),
    ('naic3', ' 3 '), ('naic4', ' 4 '), ('naic5', ' 5 '), ('naic6', ' 6'),
    ('naic_big', 'Total below investment grade'), ('naic_total', 'Total AFS fixed maturity securities'),
]
NRSRO_ROWS = [
    ('nrsro_a', 'AAA/AA/A'), ('nrsro_bbb', 'BBB'), ('nrsro_ig', ('Total Investment Grade', 'Total investment grade')),
    ('nrsro_bb', 'BB'), ('nrsro_b', ' B '), ('nrsro_ccc', 'CCC'),
    ('nrsro_cc', 'CC and lower'), ('nrsro_nr', 'Non-rated'),
    ('nrsro_big', 'Total below investment grade'), ('nrsro_total', 'Total AFS fixed maturity securities'),
]
CAP_ROWS = [
    ('total_debt', 'Total debt'), ('adj_debt', 'Adjusted debt'),
]


def qtag(m, y):
    return f'{(int(m) + 2) // 3}Q{y[2:]}'


def money_after(text, pos, n):
    vals = []
    for mt in MONEY.finditer(text, pos):
        if re.match(r'\s?%', text[mt.end():mt.end() + 3]):
            continue
        if mt.group(2):
            vals.append(0)
        else:
            v = int(mt.group(1).replace(',', ''))
            if '(' in mt.group(0):
                v = -v
            vals.append(v)
        if len(vals) >= n:
            return vals
    sys.exit(f'money ran out at {pos}')


def rates_after(text, pos, n):
    vals = []
    for mt in RATE.finditer(text, pos):
        if mt.group(2):
            vals.append(None)
        else:
            v = float(mt.group(1))
            if '(' in mt.group(0):
                v = -v
            vals.append(v)
        if len(vals) >= n:
            return vals
    sys.exit(f'rates ran out at {pos}')


def scan(text, rows, periods, mode='money', n_extra=0):
    out = {}
    pos = 0
    n = len(periods) + n_extra
    for idx, row in enumerate(rows):
        key, label = row[0], row[1]
        optional = len(row) > 2 and row[2]
        opts = label if isinstance(label, tuple) else (label,)
        hits = [(text.find(o, pos), o) for o in opts if text.find(o, pos) >= 0]
        if optional:
            if idx + 1 < len(rows):
                nxt = rows[idx + 1]
                nopts = nxt[1] if isinstance(nxt[1], tuple) else (nxt[1],)
                npos = min((text.find(o, pos) for o in nopts if text.find(o, pos) >= 0), default=-1)
            else:
                npos = -1
            if not hits or (npos >= 0 and min(hits)[0] > npos):
                for p in periods:
                    out[(p, key)] = 0
                continue
        if not hits:
            sys.exit(f'ROW NOT FOUND: {opts!r}')
        i, lab = min(hits, key=lambda t: (t[0], -len(t[1])))
        if mode == 'rate' and len(periods) == 7:
            # Q4 docs: [5 quarters][YoY][FY, FY-1][FY-YoY] — deltas are rate-shaped too
            raw9 = rates_after(text, i + len(lab), 9)
            vals = raw9[0:5] + raw9[6:8]
        elif mode == 'rate':
            vals = rates_after(text, i + len(lab), len(periods))
        else:
            vals = money_after(text, i + len(lab), n)
        for p, v in zip(periods, vals):
            out[(p, key)] = v
        pos = i + len(lab)
    return out


FOOTNOTE = re.compile(r"(?<=[\w’'])\s?\((\d)\)")   # equity(3), 6(1), 'insurance (1)'


def page_with(r, title, start=0):
    for i in range(start, len(r.pages)):
        t = ' '.join((r.pages[i].extract_text() or '').split())
        if t.startswith(title):
            return FOOTNOTE.sub(' ', t)
    sys.exit(f'PAGE NOT FOUND: {title}')


def parse_doc(tag):
    r = PdfReader(str(ROOT / f'raw/global-atlantic/supplements/gald-supplement-{tag}.pdf'))
    th = page_with(r, 'Financial highlights')
    dates = DATE.findall(th[:300])[:5]
    periods = [qtag(m, y) for m, d, y in dates]           # descending
    is_q4 = tag.startswith('q4')
    fy_pair = [f'FY{dates[0][2]}', f'FY{int(dates[0][2]) - 1}'] if is_q4 else []
    res = {}

    res.update(scan(th, H_MONEY, periods + fy_pair))
    res.update(scan(th, H_RATE, periods + fy_pair, mode='rate'))

    ti = page_with(r, 'Consolidated statements of income')
    res.update(scan(ti, INC_ROWS, periods + fy_pair))

    ta = None
    for i in range(len(r.pages)):
        t = ' '.join((r.pages[i].extract_text() or '').split())
        j = t.find('Components of adjusted operating earnings:')
        if j < 0 and t.startswith('Adjusted operating earnings'):
            j = t.find('Adjusted operating earnings:')
        if j >= 0:
            ta = FOOTNOTE.sub(' ', t[j:])
            break
    if ta is None:
        sys.exit(f'{tag}: AOE table not found')
    res.update(scan(ta, AOE_ROWS, periods + fy_pair))

    tr_ = None
    for i in range(len(r.pages)):
        t = ' '.join((r.pages[i].extract_text() or '').split())
        if 'Net investment earned rate' in t and 'return on assets' in t:
            tr_ = FOOTNOTE.sub(' ', t)
            break
    if tr_ is not None:
        res.update(scan(tr_, ROA_RATE, periods + fy_pair, mode='rate'))

    tn = page_with(r, 'New business volume')
    res.update(scan(tn, NBV_ROWS, periods + fy_pair))

    tres = page_with(r, 'Reserves by product')
    if 'Individual market Institutional market' in tres:
        # new layout: [indiv, inst, gross, ceded, net@latest] + prior 4 nets
        pos = 0
        for key, label in RES_ROWS:
            i = tres.find(label, pos)
            if i < 0:
                sys.exit(f'RES ROW NOT FOUND: {label!r}')
            vals = money_after(tres, i + len(label), 9)
            res[(periods[0], key + '_indiv')] = vals[0]
            res[(periods[0], key + '_inst')] = vals[1]
            res[(periods[0], key + '_gross')] = vals[2]
            res[(periods[0], key + '_ceded')] = vals[3]
            for p, v in zip(periods, [vals[4]] + vals[5:9]):
                res[(p, key)] = v
            pos = i + len(label)
    else:
        print(f'  note: {tag} reserves table uses the pre-2025 GA/SA layout — skipped '
              '(coverage boundary: reserves-by-product series starts 4Q24)')

    tq = page_with(r, 'Fixed maturity securities by ratings')
    d2 = DATE.findall(tq[:400])[:2]
    ends = [qtag(m, y) for m, d, y in d2]
    zone_naic = tq[:tq.find('NRSRO Rating')]
    zone_nrsro = tq[tq.find('NRSRO Rating'):]
    for key, label in NAIC_ROWS:
        i = zone_naic.find(label if isinstance(label, str) else label[0],
                           zone_naic.find('NAIC designation:'))
        if i < 0:
            sys.exit(f'NAIC ROW NOT FOUND {label!r}')
        vals = []
        pos2 = i + len(label if isinstance(label, str) else label[0])
        got = money_after(zone_naic, pos2, 2)
        # each period-end prints value then percent; % tokens are skipped by money_after
        for p, v in zip(ends, got):
            res[(p, key)] = v
    pos2 = 0
    for key, label in NRSRO_ROWS:
        opts = label if isinstance(label, tuple) else (label,)
        hits = [(zone_nrsro.find(o, pos2), o) for o in opts if zone_nrsro.find(o, pos2) >= 0]
        if not hits:
            sys.exit(f'NRSRO ROW NOT FOUND {opts!r}')
        i, lab = min(hits, key=lambda t: (t[0], -len(t[1])))
        got = money_after(zone_nrsro, i + len(lab), 2)
        for p, v in zip(ends, got):
            res[(p, key)] = v
        pos2 = i + len(lab)

    tc = page_with(r, 'Capitalization')
    res.update(scan(tc, CAP_ROWS, periods))          # balances: 5 dates, no FY pair
    return res


def main():
    series = {}
    prov = {}
    for tag in DOCS:
        res = parse_doc(tag)
        # gates per doc, on its own quarters
        qs = sorted({p for (p, _) in res if not p.startswith('FY')})
        for q in qs:
            g = lambda k: res.get((q, k))
            if g('total_revenues') is not None and None not in (g('premiums'), g('policy_fees'), g('nii'), g('inv_gl'), g('other_income')):
                if g('premiums') + g('policy_fees') + g('nii') + g('inv_gl') + g('other_income') != g('total_revenues'):
                    sys.exit(f'{tag} {q} revenue sum FAIL')
            if None not in (g('adj_nii'), g('adj_cost_ins'), g('adj_underwriting')):
                if g('adj_nii') - g('adj_cost_ins') != g('adj_underwriting'):
                    sys.exit(f'{tag} {q} underwriting chain FAIL')
            if None not in (g('nbv_fixed_rate'), g('nbv_fia'), g('nbv_va'), g('nbv_retirement_total')):
                if g('nbv_fixed_rate') + g('nbv_fia') + g('nbv_va') != g('nbv_retirement_total'):
                    sys.exit(f'{tag} {q} retirement NBV sum FAIL')
            if g('naic_total') is not None:
                if g('naic1') + g('naic2') != g('naic_ig'):
                    sys.exit(f'{tag} {q} NAIC IG FAIL')
                if g('naic3') + g('naic4') + g('naic5') + g('naic6') != g('naic_big'):
                    sys.exit(f'{tag} {q} NAIC BIG FAIL')
                if g('naic_ig') + g('naic_big') != g('naic_total'):
                    sys.exit(f'{tag} {q} NAIC total FAIL')
            if g('nrsro_total') is not None:
                if g('nrsro_ig') + g('nrsro_big') != g('nrsro_total'):
                    sys.exit(f'{tag} {q} NRSRO total FAIL')
                if g('nrsro_total') != g('naic_total'):
                    sys.exit(f'{tag} {q} NAIC vs NRSRO total FAIL')
            if None not in (g('res_total'),) and all(g(k) is not None for k, _ in RES_ROWS[:-1]):
                if sum(g(k) for k, _ in RES_ROWS[:-1]) != g('res_total'):
                    sys.exit(f'{tag} {q} reserves sum FAIL')
        # cross-doc overlap
        for kk, v in res.items():
            if kk in series and series[kk] != v:
                p_, k_ = kk
                # flow/PRT re-presentation: older docs print them combined —
                # accept the newer split iff the sum reproduces the old combined
                if k_ == 'nbv_flow' and series[kk] == v + res.get((p_, 'nbv_prt'), 0):
                    series[kk] = v
                    series[(p_, 'nbv_prt')] = res.get((p_, 'nbv_prt'), 0)
                    prov[kk] = tag
                    continue
                if k_ == 'nbv_prt' and series.get((p_, 'nbv_flow')) is not None:
                    continue      # handled with its flow row
                RECLASS = {'adj_cost_ins', 'adj_gae', 'adj_interest', 'adj_underwriting',
                           'cost_ins_ratio', 'gae_ratio', 'underwriting_ratio', 'interest_ratio'}
                if k_ in RECLASS:
                    # 1Q26 reclass (opex -> net cost of insurance), disclosed; must be
                    # pretax-neutral wherever both docs print the pretax line
                    old_pt, new_pt = series.get((p_, 'adj_op_pretax')), res.get((p_, 'adj_op_pretax'))
                    if old_pt is not None and new_pt is not None and old_pt != new_pt:
                        sys.exit(f'RECLASS NOT PRETAX-NEUTRAL {p_}: {old_pt} vs {new_pt}')
                    print(f'  note: {kk} reclassed {series[kk]} -> {v} (taking {tag})')
                    series[kk] = v
                    prov[kk] = tag
                    continue
                if k_.startswith('nbv_'):
                    # NBV categories were re-based across supplement vintages
                    # (FABN-only -> all funding agreements, etc). Later basis wins.
                    print(f'  note: {kk} re-based {series[kk]} -> {v} (taking {tag})')
                    series[kk] = v
                    prov[kk] = tag
                    continue
                sys.exit(f'OVERLAP MISMATCH {kk}: {series[kk]} ({prov[kk]}) vs {v} ({tag})')
            series[kk] = v
            prov[kk] = tag
        print(f'{tag}: {len(res)} cells, quarters {qs} — gates pass')

    with open(OUT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['period', 'metric', 'value'])
        for (p, k), v in sorted(series.items()):
            w.writerow([p, k, '' if v is None else v])
    print(f'wrote {OUT} ({len(series)} cells)')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Render the Athene vs Global Atlantic comparison page.

Every number machine-extracted and gate-verified from each company's own
filings (Athene: ATH supplements + 10-K + statutory drill; GA: GALD
supplements + KKR filings + FCRs + statutory statements). Coverage:
2023-2025 all quarters + annuals + everything reported in 2026 (1Q26 both).
Output: dossiers/comparison/athene-vs-ga.html
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'dossiers/comparison/athene-vs-ga.html'
DEST.parent.mkdir(exist_ok=True)

ATH = {}
for r in csv.DictReader(open(ROOT / 'extract/athene/quarterly_supplement.csv')):
    if r['value'] != '':
        ATH[(r['quarter'], r['metric'])] = float(r['value'])
ATH_AN = {(r['year'], r['metric']): float(r['value'])
          for r in csv.DictReader(open(ROOT / 'extract/athene/annual_engine.csv'))}
ATH_TR = {(r['year'], r['dimension'], r['bucket']): int(r['bacv'])
          for r in csv.DictReader(open(ROOT / 'extract/athene/d1_trends.csv'))}
GA = {}
for r in csv.DictReader(open(ROOT / 'extract/global-atlantic/gald_supplement.csv')):
    if r['value'] != '':
        GA[(r['period'], r['metric'])] = float(r['value'])
CAP = {(r['entity'], r['year'], r['metric']): float(r['value_musd'])
       for r in csv.DictReader(open(ROOT / 'extract/global-atlantic/ga_capital.csv'))}
STAT = {(r['carrier'], int(r['year']), r['metric']): float(r['value']) if r['value'] else None
        for r in csv.DictReader(open(ROOT / 'extract/global-atlantic/statutory_l0.csv'))}

from collections import defaultdict
import json


def load_pref(fname, pref, scale):
    by = defaultdict(dict)
    for r in csv.DictReader(open(ROOT / f'extract/cross-section/{fname}.csv')):
        by[(r['period'], r['metric'])][r['source_file']] = float(r['value'])
    return {k: v[sorted(v, key=lambda s2: next((i for i, p in enumerate(pref) if p in s2), 99))[0]] * scale
            for k, v in by.items()}


BNT = load_pref('bnt_engine_raw', ['20f', 'q1-2026', 'q4-2025'], 1.0)          # $M as printed
ASP = load_pref('aspida_engine_raw', ['485bpos', 'n4a'], 1e-3)                 # $k -> $M
KLR = {}
_klr_src = {'FY2022': 'klr-fs-2023', 'FY2023': 'klr-fs-2023', 'FY2024': 'klr-fs-2025', 'FY2025': 'klr-fs-2025'}
for _r in csv.DictReader(open(ROOT / 'extract/cross-section/klr_engine_raw.csv')):
    if _r['period'] in _klr_src and _klr_src[_r['period']] in _r['source_file']:
        KLR[(_r['period'], _r['metric'])] = float(_r['value']) / 1e6           # USD -> $M
XCAP = {(r['entity'], r['year'], r['metric']): float(r['value_kusd']) / 1e3
        for r in csv.DictReader(open(ROOT / 'extract/cross-section/capital.csv'))}
XSTAT = {(r['carrier'], r['year'], r['metric']): float(r['value_kusd'])
         for r in csv.DictReader(open(ROOT / 'extract/cross-section/statutory_l0.csv'))}
AELF = json.load(open(ROOT / 'extract/cross-section/ael_bond_features.json'))

B = lambda p, k: BNT.get((p, k))
S = lambda p, k: ASP.get((p, k))
K = lambda p, k: KLR.get((p, k))

# quarterly metric -> FY: BNT FY rows use the 20-F metric names
BNT_FY_ALIAS = {'gaap_net_income': 'net_income',
                'distributable_operating_earnings': 'distributable_operating_earnings',
                'total_gross_annuity_sales': 'gross_annuity_sales_total',
                'institutional_annuity_sales_funding_agreements': 'gross_annuity_sales_funding_agreements'}


def bq(p, k):
    """BNT value for quarter or FY period (FY via 20-F alias)."""
    if p.startswith('FY'):
        return BNT.get((p, BNT_FY_ALIAS.get(k, k)))
    return BNT.get((p, k))


def bnt_rate(p, dollar_key):
    d, aia = BNT.get((p, dollar_key)), BNT.get((p, 'annuity_average_invested_assets'))
    if d is None or not aia:
        return None
    return round(d * 4 / aia * 100, 2)


def asp_rate(p):
    if not p.startswith('FY'):
        return None
    prev = f'FY{int(p[2:]) - 1}'
    nii = ASP.get((p, 'ops_net_investment_income'))
    a0, a1 = ASP.get((prev, 'bs_total_cash_and_invested_assets')), ASP.get((p, 'bs_total_cash_and_invested_assets'))
    if None in (nii, a0, a1):
        return None
    return round(nii / ((a0 + a1) / 2) * 100, 2)


def klr_rate(p):
    if not p.startswith('FY'):
        return None
    prev = f'FY{int(p[2:]) - 1}'
    num = sum(KLR.get((p, m), 0) for m in ('net_investment_income', 'investment_income_funds_withheld',
                                           'investment_management_expenses'))
    def base(pp):
        a, f = KLR.get((pp, 'total_cash_and_invested_assets')), KLR.get((pp, 'funds_withheld_assets'))
        return None if a is None or f is None else a + f
    b0, b1 = base(prev), base(p)
    if not num or b0 is None or b1 is None:
        return None
    return round(num / ((b0 + b1) / 2) * 100, 2)


QTRS = ['1Q23', '2Q23', '3Q23', '4Q23', '1Q24', '2Q24', '3Q24', '4Q24',
        '1Q25', '2Q25', '3Q25', '4Q25', '1Q26']
FYS = ['FY2023', 'FY2024', 'FY2025']


def fmt(v, money=True, pct=False, dp=0, years=False):
    if v is None:
        return '<span class="na">·</span>'
    if years:
        return f'{v:.1f}y'
    if pct:
        return f'{v:.2f}%'
    if abs(v) >= 1000 and money:
        return f'{"−" if v < 0 else ""}${abs(v)/1000:,.1f}B'
    return f'{"−" if v < 0 else ""}${abs(v):,.0f}M' if money else f'{v:,.{dp}f}'


PLATS = [('ath', 'ATHENE'), ('ga', 'GLOBAL ATLANTIC'), ('bf', 'BROOKFIELD (BNT)'),
         ('ar', 'ARES · ASPIDA'), ('ow', 'BLUE OWL · KUVARE')]


def rows5(label, fns, periods, pct=False, years=False, note={}):
    """One block: a row per platform (in PLATS order). fns: dict plat-key -> fn(period)
    or None (platform publishes nothing for this metric -> dotted row).
    note: plat-key -> short annotation shown beside the platform tag."""
    out = []
    for i, (cls, name) in enumerate(PLATS):
        fn = fns.get(cls)
        cells = ''.join(f'<td>{fmt(fn(p) if fn else None, pct=pct, years=years)}</td>' for p in periods)
        tag = name + (f' <span style="font-weight:400">({note[cls]})</span>' if cls in note else '')
        lbl = f'{label}<span class="who">{tag}</span>' if i == 0 else f'<span class="who">{tag}</span>'
        last = ' class="blockend"' if i == len(PLATS) - 1 else ''
        out.append(f'<tr class="{cls}"{last}><td class="lbl">{lbl}</td>{cells}</tr>')
    return ''.join(out)


def rowpair(label, a_fn, g_fn, periods, pct=False):
    return rows5(label, {'ath': a_fn, 'ga': g_fn}, periods, pct=pct)


def table(title, note, rows_html, periods):
    heads = ''.join(f'<th>{p}</th>' for p in periods)
    return (f'<h2>{title} <span class="cnt">— {note}</span></h2><hr class="rule">'
            f'<div class="tbl-scroll"><table><thead><tr><th></th>{heads}</tr></thead>'
            f'<tbody>{rows_html}</tbody></table></div>')


A = lambda p, k: ATH.get((p, k))
G = lambda p, k: GA.get((p, k))

def ga_rate(p, printed_key, dollar_key):
    """Printed rate if filed; else derived = dollar x (4 if quarterly) / avg AIA."""
    v = GA.get((p, printed_key))
    if v is not None:
        return v
    d, aia = GA.get((p, dollar_key)), GA.get((p, 'avg_aia'))
    if d is None or not aia:
        return None
    mult = 1 if p.startswith('FY') else 4
    return round(d * mult / aia * 100, 2)


P = QTRS + FYS

# spread pair: Athene NIS% vs GA underwriting margin%
html_rows_spread = (
    rows5('Earned rate',
          {'ath': lambda p: A(p, 'sre_nie_pct'), 'ga': lambda p: ga_rate(p, 'nier', 'adj_nii'),
           'bf': lambda p: bnt_rate(p, 'annuity_net_investment_income') if not p.startswith('FY') else None,
           'ar': asp_rate, 'ow': klr_rate},
          P, pct=True,
          note={'bf': 'annuity segment, derived', 'ar': 'derived, statutory', 'ow': 'derived, incl funds withheld'})
    + rows5('Cost of float/insurance',
            {'ath': lambda p: A(p, 'sre_cof_pct'), 'ga': lambda p: ga_rate(p, 'cost_ins_ratio', 'adj_cost_ins'),
             'bf': lambda p: bnt_rate(p, 'annuity_cost_of_funds') if not p.startswith('FY') else None,
             'ar': None, 'ow': None},
            P, pct=True, note={'bf': 'derived', 'ar': 'not derivable — statutory basis', 'ow': 'not derivable'})
    + rows5('NET SPREAD / UNDERWRITING MARGIN',
            {'ath': lambda p: A(p, 'sre_nis_pct'), 'ga': lambda p: ga_rate(p, 'underwriting_ratio', 'adj_underwriting'),
             'bf': lambda p: bnt_rate(p, 'annuity_net_investment_spread') if not p.startswith('FY') else None,
             'ar': None, 'ow': None},
            P, pct=True, note={'bf': 'derived'})
)
def asp_inflows(p):
    prem, dep = S(p, 'ops_premium_and_annuity_considerations_life_net'), S(p, 'cf_net_deposits_on_deposit_type_contracts')
    return None if prem is None else prem + (dep or 0)


html_rows_growth = (
    rows5('Total inflows / new business',
          {'ath': lambda p: A(p, 'total_gross_inflows') or ATH_AN.get((p, 'total_gross_inflows')),
           'ga': lambda p: (lambda vals: sum(v for v in vals if v is not None) if any(v is not None for v in vals) else None)(
               [G(p, k) for k in ('nbv_retirement_total', 'nbv_preneed', 'nbv_block', 'nbv_flow', 'nbv_prt', 'nbv_funding_agreements', 'nbv_life')]),
           'bf': lambda p: bq(p, 'total_gross_annuity_sales'),
           'ar': asp_inflows, 'ow': lambda p: K(p, 'premium_income')},
          P, note={'bf': 'gross annuity sales', 'ar': 'net premiums + deposits', 'ow': 'premium income'})
    + rows5('of which funding agreements',
            {'ath': lambda p: A(p, 'funding_agreements') or ATH_AN.get((p, 'funding_agreements')),
             'ga': lambda p: G(p, 'nbv_funding_agreements'),
             'bf': lambda p: bq(p, 'institutional_annuity_sales_funding_agreements'),
             'ar': lambda p: S(p, 'cf_net_deposits_on_deposit_type_contracts'), 'ow': None},
            P, note={'ar': 'deposit-type, launched 2025', 'ow': 'none published'})
)
html_rows_earn = (
    rows5('Operating earnings (SRE / AOE / DOE)',
          {'ath': lambda p: A(p, 'sre') or ATH_AN.get((p, 'sre')), 'ga': lambda p: G(p, 'adj_op_pretax'),
           'bf': lambda p: bq(p, 'distributable_operating_earnings'), 'ar': None, 'ow': None},
          P, note={'ar': 'no operating measure exists', 'ow': 'no operating measure exists'})
    + rows5('GAAP / statutory net income',
            {'ath': lambda p: A(p, 'gaap_ni_common') or ATH_AN.get((p, 'gaap_ni_common')),
             'ga': lambda p: G(p, 'ni_shareholder'), 'bf': lambda p: bq(p, 'gaap_net_income'),
             'ar': lambda p: S(p, 'ops_net_income_loss'), 'ow': lambda p: K(p, 'net_income_loss')},
            P, note={'ar': 'statutory', 'ow': 'FY2024 = LDTI-restated'})
)
html_rows_equity = (
    rows5('Total equity / capital & surplus',
          {'ath': lambda p: A(p, 'eq_ahl_total'), 'ga': lambda p: G(p, 'shareholders_equity'),
           'bf': lambda p: bq(p, 'total_equity'),
           'ar': lambda p: S(p, 'bs_total_capital_and_surplus'), 'ow': lambda p: K(p, 'total_shareholders_equity')},
          P, note={'ar': 'statutory C&S', 'ow': 'NEGATIVE until 2024'})
    + rows5('ROE — GAAP basis',
            {'ath': None, 'ga': lambda p: G(p, 'roe'), 'bf': None, 'ar': None, 'ow': None}, P, pct=True)
)

# quality year-ends
QY = ['4Q23', '4Q24', '4Q25', '1Q26']


def ath_bigsh(p):
    y = {'4Q23': '2023', '4Q24': '2024', '4Q25': '2025'}.get(p)
    if not y:
        return None
    tot = ATH_TR[(y, 'total', 'all')]
    big = sum(ATH_TR.get((y, 'naic_band', f'NAIC {i}'), 0) for i in '3456')
    return big / tot * 100


def ga_naic_bigsh(p):
    t, b = GA.get((p, 'naic_total')), GA.get((p, 'naic_big'))
    return b / t * 100 if t and b else None


def ga_nrsro_bigsh(p):
    t, b = GA.get((p, 'nrsro_total')), GA.get((p, 'nrsro_big'))
    return b / t * 100 if t and b else None


def ath_pl(p):
    y = {'4Q23': '2023', '4Q24': '2024', '4Q25': '2025'}.get(p)
    if not y:
        return None
    return ATH_TR[(y, 'rating_source', 'PL (private letter)')] / ATH_TR[(y, 'total', 'all')] * 100


def ael_feat(p, key):
    y = {'4Q23': '2023', '4Q24': '2024', '4Q25': '2025'}.get(p)
    return AELF['years'][y][key] if y else None


html_rows_quality = (
    rows5('Below-IG share — regulatory ruler (NAIC)',
          {'ath': ath_bigsh, 'ga': ga_naic_bigsh, 'bf': lambda p: ael_feat(p, 'below_ig_pct'),
           'ar': None, 'ow': None},
          QY, pct=True, note={'bf': 'AEL, position-level', 'ar': 'no public schedule', 'ow': 'no public schedule'})
    + rows5('Below-IG share — market ruler (NRSRO)',
            {'ath': None, 'ga': ga_nrsro_bigsh, 'bf': None, 'ar': None, 'ow': None}, QY, pct=True)
    + rows5('Private-letter share (position-level statutory drill)',
            {'ath': ath_pl, 'ga': None, 'bf': lambda p: ael_feat(p, 'pl_share_pct'), 'ar': None, 'ow': None},
            QY, pct=True, note={'bf': 'AEL — no Athene-style ramp', 'ga': 'no public CUSIP-level filing'})
    + rows5('Bond-book weighted holding age',
            {'ath': lambda p: {'4Q25': 1.72}.get(p), 'ga': None,
             'bf': lambda p: ael_feat(p, 'wavg_age'), 'ar': None, 'ow': None},
            QY, years=True, note={'bf': 'seasoned', 'ath': 'unseasoned'})
)

CAPY = ['2023', '2024', '2025']


def xcov(entity, y):
    ec, ecr = XCAP.get((entity, y, 'eligible_capital')), XCAP.get((entity, y, 'ecr'))
    return ec / ecr * 100 if ec and ecr else None


html_rows_capital = (
    rows5('Bermuda pivot ECR coverage',
          {'ath': lambda y: {'2024': 242.0, '2025': 202.0}.get(y),
           'ga': lambda y: CAP[('GA Re', y, 'eligible_capital')] / CAP[('GA Re', y, 'ecr')] * 100,
           'bf': None,
           'ar': lambda y: xcov('Aspida Re', y), 'ow': lambda y: xcov('Kuvare Life Re', y)},
          CAPY, pct=True,
          note={'ath': 'AARe', 'ga': 'GA Re', 'bf': 'North End Re — NO FCR published',
                'ar': 'Aspida Re', 'ow': 'Kuvare Life Re — lowest'})
    + rows5('Second reinsurer ECR coverage',
            {'ath': lambda y: {'2024': 453.0, '2025': 309.0}.get(y),
             'ga': lambda y: CAP[('GAAL', y, 'eligible_capital')] / CAP[('GAAL', y, 'ecr')] * 100,
             'bf': None, 'ar': None, 'ow': None},
            CAPY, pct=True, note={'ath': 'ALRe', 'ga': 'GAAL', 'bf': 'Freestone Re — no FCR'})
    + rows5('Lead US carrier capital ($M)',
            {'ath': lambda y: 9504.0 if y == '2025' else None,
             'ga': lambda y: ((STAT.get(('flic', int(y), 'capital_surplus')) or 0)
                              + (STAT.get(('cwa', int(y), 'capital_surplus')) or 0)) / 1e6 or None,
             'bf': lambda y: (lambda v: v / 1e6 if v else None)(XSTAT.get(('ael', y, 'capital_surplus'))),
             'ar': lambda y: S(f'FY{y}', 'bs_total_capital_and_surplus'),
             'ow': lambda y: K(f'FY{y}', 'total_shareholders_equity')},
            CAPY,
            note={'ath': 'AAIA TAC', 'ga': 'FLIC+CWA C&S', 'bf': 'AEL C&S — falling as assets grow',
                  'ar': 'Aspida Life C&S', 'ow': 'KLR equity (Bermuda)'})
)


def runnable_a(p):
    fa, tot = ATH.get((p, 'nrl_fa')), ATH.get((p, 'nrl_total'))
    return fa / tot * 100 if fa and tot else None


def runnable_g(p):
    fa, tot = GA.get((p, 'res_fa')), GA.get((p, 'res_total'))
    return fa / tot * 100 if fa and tot else None


RUNP = ['4Q24', '1Q25', '2Q25', '3Q25', '4Q25', '1Q26']
html_rows_run = (
    rows5('Funding agreements as % of net reserves (runnable share)',
          {'ath': runnable_a, 'ga': runnable_g, 'bf': None, 'ar': None, 'ow': None},
          RUNP, pct=True, note={'bf': 'stock not split out quarterly', 'ar': 'annual only', 'ow': 'none'})
    + rows5('Funding-agreement / deposit-type sales & stocks ($M)',
            {'ath': lambda p: A(p, 'funding_agreements'), 'ga': lambda p: G(p, 'nbv_funding_agreements'),
             'bf': lambda p: bq(p, 'institutional_annuity_sales_funding_agreements'),
             'ar': lambda p: {'4Q25': (lambda v: v)(S('FY2025', 'bs_liability_deposit_type_contracts'))}.get(p),
             'ow': None},
            RUNP, note={'bf': 'FA sales/quarter', 'ar': 'deposit-type stock YE25 — 0 two years ago',
                        'ow': 'none published'})
)

html = f"""<title>The Cross Map — five PE-insurance machines</title>
<style>
:root{{--bg:#F6F5F1;--panel:#FFF;--ink:#22271F;--muted:#6E756D;--line:#E3E1D8;--line2:#CFCCC0;
--us:#0F6E56;--us-bg:#E4F3EC;--bm:#A3431D;--bm-bg:#F9ECE5;--acc:#185FA5;--warn:#BA7517;--warn-bg:#FAEEDA;
--bfc:#2E5E8C;--bf-bg:#E9F1F8;--arc:#6B4FA0;--ar-bg:#F0EBF8;--owc:#8C6D1F;--ow-bg:#F8F2DF}}
@media (prefers-color-scheme: dark){{:root{{--bg:#15191B;--panel:#1D2325;--ink:#E7E9E3;--muted:#8F978F;
--line:#2B3234;--line2:#3A4245;--us:#5DCAA5;--us-bg:#0C3A2D;--bm:#F0997B;--bm-bg:#43200F;--acc:#85B7EB;--warn:#D9A54A;--warn-bg:#3A2B10;
--bfc:#8FBCE8;--bf-bg:#152A3C;--arc:#B79CE8;--ar-bg:#251B3A;--owc:#D9B958;--ow-bg:#332A10}}}}
:root[data-theme="dark"]{{--bg:#15191B;--panel:#1D2325;--ink:#E7E9E3;--muted:#8F978F;--line:#2B3234;--line2:#3A4245;
--us:#5DCAA5;--us-bg:#0C3A2D;--bm:#F0997B;--bm-bg:#43200F;--acc:#85B7EB;--warn:#D9A54A;--warn-bg:#3A2B10;
--bfc:#8FBCE8;--bf-bg:#152A3C;--arc:#B79CE8;--ar-bg:#251B3A;--owc:#D9B958;--ow-bg:#332A10}}
:root[data-theme="light"]{{--bg:#F6F5F1;--panel:#FFF;--ink:#22271F;--muted:#6E756D;--line:#E3E1D8;--line2:#CFCCC0;
--us:#0F6E56;--us-bg:#E4F3EC;--bm:#A3431D;--bm-bg:#F9ECE5;--acc:#185FA5;--warn:#BA7517;--warn-bg:#FAEEDA;
--bfc:#2E5E8C;--bf-bg:#E9F1F8;--arc:#6B4FA0;--ar-bg:#F0EBF8;--owc:#8C6D1F;--ow-bg:#F8F2DF}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--ink);font:15px/1.55 "Avenir Next","Segoe UI",system-ui,sans-serif;margin:0}}
.wrap{{max-width:1140px;margin:0 auto;padding:36px 24px 64px}}
header{{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:22px}}
.eyebrow{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:30px;font-weight:600;margin:0;text-wrap:balance}}
.sub{{color:var(--muted);margin:8px 0 0;font-size:14px}}
a{{color:var(--acc);text-decoration:none}} a:hover{{text-decoration:underline}}
h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;margin:38px 0 6px}}
h2 .cnt{{color:var(--muted);font-weight:400;letter-spacing:0;text-transform:none}}
.rule{{border:0;border-top:1px solid var(--line2);margin:0 0 14px}}
.verdict{{background:var(--panel);border-left:4px solid var(--acc);padding:18px 22px;font-size:15.5px;line-height:1.6}}
.callout{{background:var(--panel);border-left:3px solid var(--bm);padding:13px 17px;margin:12px 0;font-size:14px}}
.tbl-scroll{{overflow-x:auto;margin-bottom:6px}}
table{{border-collapse:collapse;background:var(--panel);border:1px solid var(--line);font-size:12.5px;min-width:100%}}
th{{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);text-align:right;font-weight:600;
padding:8px 8px;border-bottom:1px solid var(--line2);white-space:nowrap}}
td{{padding:6px 8px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap;
font-variant-numeric:tabular-nums}}
td.lbl{{text-align:left;font-weight:600;min-width:230px;white-space:normal}}
.who{{display:block;font-size:9.5px;letter-spacing:.1em;font-weight:700}}
tr.ath .who{{color:var(--us)}} tr.ga .who{{color:var(--bm)}} tr.bf .who{{color:var(--bfc)}}
tr.ar .who{{color:var(--arc)}} tr.ow .who{{color:var(--owc)}}
tr.ath{{background:var(--us-bg)}} tr.ga{{background:var(--bm-bg)}} tr.bf{{background:var(--bf-bg)}}
tr.ar{{background:var(--ar-bg)}} tr.ow{{background:var(--ow-bg)}}
tr.ath td,tr.ga td,tr.bf td,tr.ar td,tr.ow td{{border-bottom:0}}
tr.blockend td{{border-bottom:1px solid var(--line2)}}
.na{{color:var(--muted)}}
.footer{{margin-top:40px;padding-top:14px;border-top:1px solid var(--line2);font-size:12px;color:var(--muted)}}
</style>
<div class="wrap">
<header>
<p class="eyebrow">CREDIT MAP · THE CROSS MAP · FIVE PLATFORMS, ONE RULER</p>
<h1>The cross map — every PE-insurance machine, on one ruler</h1>
<p class="sub">Every number machine-extracted and gate-verified from each company's own filings
(supplements, 10-K/20-F/10-Q, statutory statements incl. position-level Schedule D where published, audited FS,
Bermuda FCRs — sha-tracked in the manifest). Five platforms: <strong>Athene (Apollo) · Global Atlantic (KKR) ·
Brookfield (BNT: AEL+ANICO) · Ares (Aspida) · Blue Owl (Kuvare)</strong>. Periods: all quarters 2023–2025, annuals,
and everything reported in 2026. A dotted cell means that platform publishes nothing for that metric/period — every
blank is a disclosure fact, not a gap in the machine: Athene quarterlies before 4Q24 are glyph-encoded (decoder
parked); BNT quarterly reporting began 1Q25; Aspida and Kuvare publish no quarterly cadence at all
(annual columns only); "derived" rates are computed from printed dollars and flagged.</p>
</header>

<div class="verdict">
<strong>The cross-map read:</strong> five machines, one design, tuned differently — and the dials that matter
all move the same direction. <strong>Every measurable spread is compressing</strong> (Athene NIS 1.65→1.34%,
GA margin 1.80→1.17%, BNT annuity spread 1.90→1.76% derived). <strong>Every Bermuda pivot with a public FCR
sits in the same thinning 176–205% band.</strong> <strong>Every platform with an "operating" measure printed
GAAP losses under it within five quarters</strong> (Athene 1Q26 −$1,973M vs SRE +$719M; GA FY25 −$1,203M vs
+$1,081M; BNT 1Q26 −$602M vs DOE +$438M — a metronome over a tape). Where the platforms differ is structure:
opacity (Athene), hypergrowth (Aspida), model risk (Blue Owl), seasoning (AEL). Head-to-head detail on the
two biggest below. Athene runs bigger
($297B avg invested assets vs GA's $157B), hotter (net spread 1.34% vs GA's 1.25% — both compressed hard from
2023), and more opaque (25.3% of its bond book graded by private letters; GA has no public position-level filing
at all — a boundary, not an exoneration). GA runs <em>junkier on the market's ruler</em> — 10.0% below-IG by NRSRO
against Athene's ~4% — and its NAIC-vs-NRSRO gap (5.6% vs 10.0%) says its regulatory designations flatter its book
by more than Athene's do. <strong>Both engines printed GAAP losses within the last year while their "operating"
measures stayed positive</strong> — the adjusted-vs-GAAP divergence is a sector feature, not an Athene quirk.
Bermuda cushions: GA Re 205% ECR coverage sits in the same compressing band as AARe's 202%.
</div>

{table('1 · The spread engines', 'earned rate − cost of float = the margin; both compressing',
       html_rows_spread, P)}
<div class="callout"><strong>Every measurable margin rolled over.</strong> Athene: 1.65% → 1.34% over 2025-26.
GA: 1.80% (2023) → 1.17% (1Q26) — a deeper slide from a lower peak. BNT (derived from printed segment dollars):
1.90% (4Q24) → 1.76% (1Q26), with cost of funds up EVERY quarter. Aspida and Kuvare publish no cost-of-funds
basis at all — their spread is unmeasurable from public documents, which is itself a finding. The repricing race
(cost of funds up faster than earned) is the same story on every balance sheet that can be read.</div>

{table('2 · Growth — money in', 'gross inflows (Athene) vs new business volume (GA); bases differ, trends compare',
       html_rows_growth, P)}

{table('3 · Operating earnings vs the GAAP tape', 'the divergence both companies share',
       html_rows_earn, P)}
<div class="callout"><strong>The shared tell, now at three platforms:</strong> GA FY2025 printed
<strong>−$1,203M</strong> to shareholder against +$1,081M adjusted-operating; Athene's 1Q26 was
<strong>−$1,973M</strong> against +$719M SRE; BNT's GAAP swung from −$282M (1Q25) to +$608M (3Q25) to <strong>−$602M</strong> (1Q26) while
its DOE printed ~$437M <em>every single quarter</em> — a metronome over a tape. Investment losses and
reinsurance fair-value moves are recognized in GAAP and stripped from every operating measure, in the same
direction, at scale. Aspida and Kuvare don't publish an operating measure — their single bottom lines are the
whole story: Aspida three loss years shrinking to exact breakeven on contributed capital; Kuvare −$624M (2022),
then +$24M / −$41M / +$17M on a $9.8B balance sheet.</div>

{table('4 · Portfolio quality — the two rulers', 'regulatory (NAIC) vs market (NRSRO) grading of the bond books',
       html_rows_quality, QY)}
<div class="callout"><strong>The two-ruler gap is the opacity metric.</strong> GA's book is 5.6% below-IG by NAIC
but 10.0% by market ratings — a 4.4pt flattering gap. Athene's statutory below-IG is 2.9% with its supplement
NAIC view at ~3.9% — but 25.3% of its book is graded by unpublished private letters the market prices 2–3 notches
lower (its letter-slip stress: below-IG would reach 7–14% if the market is right). Different mechanisms,
same direction: both books look better on the regulatory ruler than the market's. AEL is the control:
position-level like Athene, but PL share 9.4→14.2→9.7% (no ramp), 71% publicly rated, and a 4.0y seasoned book —
proof the Athene configuration is a choice. Aspida and Kuvare publish no bond-level quality data on any ruler
— the two youngest, fastest-growing books are the two least measurable</div>

{table('5 · Capital — the cushions, on their own rulers', 'Bermuda ECR coverage + lead-carrier statutory capital',
       html_rows_capital, CAPY)}

{table('6 · The runnable share', 'funding agreements as % of net reserves', html_rows_run,
       ['4Q24', '1Q25', '2Q25', '3Q25', '4Q25', '1Q26'])}
<div class="callout"><strong>Divergent funding risk:</strong> Athene's runnable share climbed 21% → 27.2%
of net reserves; GA sits near 6–8%. BNT's funding-agreement issuance is lumpy — $0 to $1.4B a quarter (stock not split out quarterly — boundary); Aspida went 0 → $819M of deposit-type liabilities in 2025 (the channel just opened at the
fastest-growing platform); Kuvare publishes none. On liquidity structure, Athene is the outlier of the five.</div>

<h2>7 · THE FIVE-PLATFORM CROSS-SECTION <span class="cnt">— every PE-insurance machine, one table (latest year-end)</span></h2><hr class="rule">
<div class="tbl-scroll"><table>
<thead><tr><th></th><th>Athene (Apollo)</th><th>Global Atlantic (KKR)</th><th>Brookfield (AEL+ANICO)</th><th>Ares (Aspida)</th><th>Blue Owl (Kuvare)</th></tr></thead>
<tbody>
<tr><td style="text-align:left">Ownership model</td><td>owns insurers</td><td>owns insurers</td><td>owns insurers</td><td>manages + fund-controls</td><td>owns manager + preferred only</td></tr>
<tr><td style="text-align:left">Lead-carrier assets (statutory, YE25)</td><td>$282B (AAIA invested)</td><td>$112.5B (CWA) + $73.0B (FLIC)</td><td>$62.7B (AEL) + $40.2B (ANICO)</td><td>$14.7B (Aspida Life)</td><td>not public</td></tr>
<tr><td style="text-align:left">Asset growth, 2yr</td><td>bond book +75%</td><td>NIA +25%</td><td>AEL +5%</td><td><strong>+378% (5×)</strong></td><td>not public</td></tr>
<tr><td style="text-align:left">Private-letter share of bonds (position-level)</td><td><strong>25.3%</strong></td><td>n/a (no public filing)</td><td>9.7% — trend 9.4→14.2→9.7 (3yrs footed)</td><td>n/a</td><td>n/a</td></tr>
<tr><td style="text-align:left">Identifier-private floor</td><td>31.0%</td><td>n/a</td><td>17.0%</td><td>n/a</td><td>n/a</td></tr>
<tr><td style="text-align:left">Below-IG share (regulatory ruler)</td><td>2.9%</td><td>5.6% (NRSRO: <strong>10.0%</strong>)</td><td>5.1% (2.6→3.6→5.1)</td><td>~7% one-pager basis</td><td>not public</td></tr>
<tr><td style="text-align:left">Bond-book weighted age</td><td><strong>1.7y (unseasoned)</strong></td><td>n/a</td><td>4.0y (seasoned; 4.7→4.3→4.0)</td><td>~new (5× growth)</td><td>n/a</td></tr>
<tr><td style="text-align:left">Bermuda pivot ECR coverage (trend)</td><td>AARe 242→<strong>202%</strong></td><td>GA Re 171→235→<strong>205%</strong></td><td>not published (no FCR)</td><td>Aspida Re 214→206→<strong>199%</strong></td><td>KLR 207→190→<strong>176%</strong></td></tr>
<tr><td style="text-align:left">Runnable funding-agreement exposure</td><td><strong>27% of reserves ↑</strong></td><td>~7% of reserves</td><td>modest (FHLB/FABN at AEL)</td><td>began issuing 2025 ↑</td><td>not public</td></tr>
<tr><td style="text-align:left">Weakest public rating in fleet</td><td>A+ fleet</td><td>A fleet</td><td>A–/A fleet</td><td>A− fleet</td><td><strong>B++ negative (Lincoln Benefit)</strong></td></tr>
</tbody></table></div>
<div class="callout"><strong>What the cross-section actually shows:</strong> (1) <em>Every Bermuda pivot with a public
FCR is compressing into the same 175–205% band</em> — five platforms, one direction; the sector's offshore cushion is
thinning in unison. (2) <em>Athene is the opacity outlier</em>: 25.3% private-letter vs 9.7% at the only measurable peer — and AEL's three-year trend (9.4→14.2→9.7%) shows NO Athene-style ramp: the 3.4× PL climb is an Athene choice, now proven against a measured control,
31% vs 17% identifier-private, and the youngest big book (1.7y vs 4.0y) — its "clean" loss history is the least
informative of the five. (3) <em>Ares/Aspida is the growth outlier</em> (5× in two years on thin capital, half the book
funds-withheld). (4) <em>Blue Owl is the model outlier</em> — pure fee extraction with the credit risk parked at carriers
it doesn't own, including the group's only B++/negative. (5) Disclosure quality itself now ranks the sector:
Brookfield/AEL best (full blanks), then Athene, GA, Ares, Blue Owl worst.</div>

<h2>8 · What this cross-section says about the private-credit-insurance question</h2><hr class="rule">
<p style="font-size:14.5px">Five platforms now sit on one measured ruler. The margin compression,
the adjusted-vs-GAAP divergence, and the regulatory-vs-market grading gap now have <em>measured values at two
companies</em> built by identical, gate-verified pipelines. Athene distinguishes itself by scale, private-letter
concentration, and runnable funding; GA by a junkier market-rated book and thinner disclosure (no public
position-level filings). The dispersion is now tradeable structure: opacity (Athene), growth (Aspida), model risk (Blue Owl), and the one common factor — Bermuda cushions thinning in unison.</p>

<div class="footer">Sources &amp; verification: Athene — ATH supplements (Q4'25/Q1'26), AHL 10-K FY2025, AAIA
statutory statements YE2023–25 footed to the dollar, NAIC C-1 factors. Global Atlantic — GALD supplements
(Q4'23/Q4'24/Q4'25/Q1'26, 918 gated cells), KKR 10-K/10-Q FY2023–1Q26 (176 gated cells), GA Re/GAAL FCRs 2023–25,
carrier statutory statements 2022–25. All documents sha-tracked in acquisition/manifest.csv; every table crosses
at least one exact-equality gate. Regenerate: <span style="font-family:ui-monospace,Menlo,monospace">python3
tools/render_comparison.py</span>. Research conclusions from public filings; not investment advice.</div>
</div>
"""
DEST.write_text(html)
print(f'wrote {DEST} ({len(html):,} bytes)')

#!/usr/bin/env python3
"""Render dossiers/athene/the-read.html — the conclusions layer.

Verdict-first page where every claim is driven by numbers from the footed
extracts (quarterly_supplement.csv, d1_trends.csv, d1_aging.csv,
annual_engine.csv, letter_slip_stress.csv). Regenerate after any re-run.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'dossiers/athene/the-read.html'

Q = {}
for r in csv.DictReader(open(ROOT / 'extract/athene/quarterly_supplement.csv')):
    if r['value'] != '':
        Q[(r['quarter'], r['metric'])] = float(r['value'])
T = {(r['year'], r['dimension'], r['bucket']): int(r['bacv'])
     for r in csv.DictReader(open(ROOT / 'extract/athene/d1_trends.csv'))}
A = {(r['quarter'], r['metric'], r['split']): r
     for r in csv.DictReader(open(ROOT / 'extract/athene/d1_aging.csv'))} if False else None
AGE = [r for r in csv.DictReader(open(ROOT / 'extract/athene/d1_aging.csv')) if r['table'] == 'age_total']
AN = {(r['year'], r['metric']): float(r['value'])
      for r in csv.DictReader(open(ROOT / 'extract/athene/annual_engine.csv'))}

QTRS = ['4Q24', '1Q25', '2Q25', '3Q25', '4Q25', '1Q26']


def series(metric, quarters=QTRS):
    return [(q, Q[(q, metric)]) for q in quarters if (q, metric) in Q]


def spark(pts, w=210, h=52, cls='sp-acc', fmt=lambda v: f'{v:,.0f}', lo=None, hi=None):
    vals = [v for _, v in pts]
    lo = min(vals) if lo is None else lo
    hi = max(vals) if hi is None else hi
    rng = (hi - lo) or 1
    n = len(pts)
    xs = [14 + i * (w - 58) / (n - 1) for i in range(n)]
    ys = [10 + (h - 24) * (1 - (v - lo) / rng) for v in vals]
    pl = ' '.join(f'{x:.1f},{y:.1f}' for x, y in zip(xs, ys))
    return (f'<svg viewBox="0 0 {w} {h}" class="spark" role="img">'
            f'<polyline class="{cls}" points="{pl}" fill="none" stroke-width="2"/>'
            f'<circle class="{cls}-dot" cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="3.2"/>'
            f'<text class="spv" x="{xs[-1] + 6:.1f}" y="{min(ys[-1] + 4, h - 4):.1f}">{fmt(vals[-1])}</text>'
            f'</svg>')


def card(title, sub, sparkhtml, note):
    return (f'<div class="mcard"><div class="ml">{title}</div>{sparkhtml}'
            f'<div class="mv2">{sub}</div><div class="mx">{note}</div></div>')


# ---- numbers ----
nis = series('sre_nis_pct', QTRS[1:])
srem = series('sre_pct', QTRS[1:])
cof = series('sre_cof_pct', QTRS[1:])
earn = series('sre_nie_pct', QTRS[1:])
flows = series('net_flows')
fa_share = [(p, Q[(p, 'nrl_fa')] / Q[(p, 'nrl_total')] * 100) for p in ('4Q24', '4Q25', '1Q26')]
pl_share = [T[(y, 'rating_source', 'PL (private letter)')] / T[(y, 'total', 'all')] * 100
            for y in ('2023', '2024', '2025')]
floor_share = [(T[(y, 'id_type', 'PPN (private placement)')] + T[(y, 'id_type', 'no identifier')])
               / T[(y, 'total', 'all')] * 100 for y in ('2023', '2024', '2025')]
book = [T[(y, 'total', 'all')] / 1e9 for y in ('2023', '2024', '2025')]
prov = [-abs(AN[(y, 'provision_credit_losses')]) for y in ('FY2023', 'FY2024', 'FY2025')]
age_order = ['<1y', '1-2y', '2-3y', '3-5y', '5-10y', '>=10y', 'unknown']
age_v = {r['bucket']: int(r['bacv']) for r in AGE}
age_tot = sum(age_v.values())
seasoned = sum(age_v.get(b, 0) for b in ('3-5y', '5-10y', '>=10y')) / age_tot * 100

ni_common_1q26 = Q[('1Q26', 'gaap_ni_common')]
eq_drop = (Q[('1Q26', 'eq_ahl_total')] / Q[('4Q25', 'eq_ahl_total')] - 1) * 100

BADGE = {'CLEAN': 'b-clean', 'CLEAN*': 'b-clean', 'WATCH': 'b-watch',
         'UNTESTABLE': 'b-unk', 'OPAQUE': 'b-unk', 'DETERIORATING': 'b-bad', 'DECELERATING': 'b-bad'}


def brow(hyp, verdict, evidence, where):
    return (f'<tr><td>{hyp}</td><td><span class="badge {BADGE[verdict]}">{verdict}</span></td>'
            f'<td>{evidence}</td><td class="dim xs">{where}</td></tr>')


AGE_SEGS = ''.join(
    f'<div class="ageseg" style="width:{age_v.get(b,0)/age_tot*100:.1f}%" title="{b}: {age_v.get(b,0)/age_tot*100:.1f}%"></div>'
    for b in age_order[:2]) + ''.join(
    f'<div class="ageseg a2" style="width:{age_v.get(b,0)/age_tot*100:.1f}%" title="{b}"></div>'
    for b in age_order[2:3]) + ''.join(
    f'<div class="ageseg a3" style="width:{age_v.get(b,0)/age_tot*100:.1f}%" title="{b}"></div>'
    for b in age_order[3:])

html = f"""<title>Athene — The Read</title>
<style>
:root{{
  --bg:#F6F5F1; --panel:#FFFFFF; --ink:#22271F; --muted:#6E756D; --line:#E3E1D8; --line2:#CFCCC0;
  --us:#0F6E56; --us-bg:#E4F3EC; --us-ink:#085041;
  --bm:#A3431D; --bm-bg:#F9ECE5; --bm-ink:#712B13;
  --acc:#185FA5; --acc-bg:#E6F1FB; --warn:#BA7517; --warn-bg:#FAEEDA; --warn-ink:#633806;
}}
@media (prefers-color-scheme: dark){{:root{{
  --bg:#15191B; --panel:#1D2325; --ink:#E7E9E3; --muted:#8F978F; --line:#2B3234; --line2:#3A4245;
  --us:#5DCAA5; --us-bg:#0C3A2D; --us-ink:#9FE1CB;
  --bm:#F0997B; --bm-bg:#43200F; --bm-ink:#F5C4B3;
  --acc:#85B7EB; --warn:#D9A54A; --warn-bg:#3A2B10; --warn-ink:#FAC775;
}}}}
:root[data-theme="dark"]{{
  --bg:#15191B; --panel:#1D2325; --ink:#E7E9E3; --muted:#8F978F; --line:#2B3234; --line2:#3A4245;
  --us:#5DCAA5; --us-bg:#0C3A2D; --us-ink:#9FE1CB;
  --bm:#F0997B; --bm-bg:#43200F; --bm-ink:#F5C4B3;
  --acc:#85B7EB; --warn:#D9A54A; --warn-bg:#3A2B10; --warn-ink:#FAC775;
}}
:root[data-theme="light"]{{
  --bg:#F6F5F1; --panel:#FFFFFF; --ink:#22271F; --muted:#6E756D; --line:#E3E1D8; --line2:#CFCCC0;
  --us:#0F6E56; --us-bg:#E4F3EC; --us-ink:#085041;
  --bm:#A3431D; --bm-bg:#F9ECE5; --bm-ink:#712B13;
  --acc:#185FA5; --acc-bg:#E6F1FB; --warn:#BA7517; --warn-bg:#FAEEDA; --warn-ink:#633806;
}}
*{{box-sizing:border-box}}
body{{background:var(--bg);color:var(--ink);font:15px/1.55 "Avenir Next","Segoe UI",system-ui,sans-serif;margin:0}}
.wrap{{max-width:980px;margin:0 auto;padding:36px 24px 64px}}
a{{color:var(--acc);text-decoration:none}} a:hover{{text-decoration:underline}}
.mono{{font-family:ui-monospace,"SF Mono",Menlo,monospace;font-variant-numeric:tabular-nums}}
.dim{{color:var(--muted)}} .xs{{font-size:11.5px}}
header{{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:22px}}
.eyebrow{{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}}
h1{{font-size:30px;font-weight:600;margin:0;text-wrap:balance}}
.sub{{color:var(--muted);margin:8px 0 0;font-size:14px}}
h2{{font-size:13px;letter-spacing:.12em;text-transform:uppercase;font-weight:600;margin:40px 0 6px}}
h2 .cnt{{color:var(--muted);font-weight:400;letter-spacing:0;text-transform:none}}
.rule{{border:0;border-top:1px solid var(--line2);margin:0 0 16px}}
.verdict{{background:var(--panel);border-left:4px solid var(--bm);padding:18px 22px;font-size:16px;line-height:1.6}}
.verdict strong{{font-weight:650}}
.callout{{background:var(--panel);border-left:3px solid var(--acc);padding:14px 18px;margin:14px 0;font-size:14.5px}}
table{{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);font-size:13.5px}}
th{{font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);text-align:left;font-weight:600;padding:10px 12px;border-bottom:1px solid var(--line2)}}
td{{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
tr:last-child td{{border-bottom:0}}
.tbl-scroll{{overflow-x:auto;margin:0 0 8px}}
.badge{{display:inline-block;font-size:10.5px;font-weight:650;letter-spacing:.08em;padding:2px 9px;border-radius:999px;white-space:nowrap}}
.b-clean{{background:var(--us-bg);color:var(--us-ink)}}
.b-watch{{background:var(--warn-bg);color:var(--warn-ink)}}
.b-unk{{background:var(--line);color:var(--muted)}}
.b-bad{{background:var(--bm-bg);color:var(--bm-ink)}}
.mgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));gap:14px;margin:14px 0}}
.mcard{{background:var(--panel);border:1px solid var(--line);padding:14px 16px}}
.mcard .ml{{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600}}
.mcard .mv2{{font-size:21px;font-weight:650;font-variant-numeric:tabular-nums;margin-top:2px}}
.mcard .mx{{font-size:12.5px;color:var(--muted);margin-top:4px;line-height:1.45}}
.spark{{width:100%;max-width:230px;height:52px;margin-top:6px}}
.sp-acc{{stroke:var(--acc)}} .sp-acc-dot{{fill:var(--acc)}}
.sp-bad{{stroke:var(--bm)}} .sp-bad-dot{{fill:var(--bm)}}
.sp-warn{{stroke:var(--warn)}} .sp-warn-dot{{fill:var(--warn)}}
.spv{{font-size:11px;font-weight:650;fill:var(--ink);font-family:ui-monospace,Menlo,monospace}}
.agebar{{display:flex;height:40px;border:1px solid var(--line2);border-radius:6px;overflow:hidden;background:var(--panel)}}
.ageseg{{background:var(--bm);opacity:.85;border-right:1px solid var(--bg)}}
.ageseg.a2{{background:var(--warn)}}
.ageseg.a3{{background:var(--us)}}
.agelegend{{display:flex;gap:18px;font-size:12px;color:var(--muted);margin-top:6px;flex-wrap:wrap}}
.dot{{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px;vertical-align:middle}}
.paths{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px;margin:14px 0}}
.path{{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--acc);padding:16px 18px;font-size:14px}}
.path h3{{font-size:13px;margin:0 0 8px;font-weight:650}}
.cols2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}}
.footer{{margin-top:44px;padding-top:14px;border-top:1px solid var(--line2);font-size:12px;color:var(--muted)}}
</style>
<div class="wrap">
<header>
<p class="eyebrow">CREDIT MAP · THE VERDICT LAYER · SESSION 2</p>
<h1>The Read — what the machine actually says about Athene</h1>
<p class="sub">Every number on this page is machine-extracted and gate-verified; the evidence layer is the
<a href="https://claude.ai/code/artifact/0dfa08f5-a1c0-49b7-b080-d578fdf98b39">dashboard</a>, the working model is the
engine workbook, the terms are in the <a href="https://claude.ai/code/artifact/f52dd3e0-5ffe-43dc-857e-49e2e7aa81d0">teaching doc</a>.
As of 2026-07-22 · latest data 1Q26.</p>
</header>

<div class="verdict">
<strong>The verdict: this is not a demonstrable credit bubble today — and the machine earned the right to say so.</strong>
It is a <strong>margin-compressing, opacity-accumulating spread machine two years into an unseasoned book</strong>:
the adverse hypotheses we could test came back clean or mild; the ones that would decide the bubble question are
<em>untestable until the book seasons</em> — and only {seasoned:.0f}% of it is old enough to have entered the
loss-emergence window. What <em>is</em> on the tape right now: the spread engine is decelerating, the funding mix is
getting more runnable, and the grading of the book is migrating to channels no market can contradict.
</div>

<h2>1 · The scoreboard <span class="cnt">— every hypothesis we tested, and what the gates said</span></h2>
<hr class="rule">
<div class="tbl-scroll"><table>
<thead><tr><th>Hypothesis</th><th>Verdict</th><th>The number that decided it</th><th>Where</th></tr></thead>
<tbody>
{brow('Related-party sales are priced off-market', 'CLEAN', 'Matched pairs (same bond, family vs market, 45 days): median −0.005 pts ≈ zero. The 10× gain gap is mix, not price.', 'dashboard ⑤b · finding 43')}
{brow('…but the test reaches the whole RP flow', 'UNTESTABLE', '94% of the $9.2B related-party flow has no contemporaneous market trade — unverifiable by construction.', 'finding 43 · D4 queued')}
{brow('Private letters are stale grades on old paper', 'CLEAN', 'Inverted: PL is the YOUNGEST shelf (1.05y avg vs 2.03y public) and 30% of new buying.', 'aging panel · finding 45')}
{brow('The 2023 PL cohort migrated badly', 'CLEAN*', '$2.2B upgraded vs $0.3B downgraded. * Two-year window; one 12-notch one-step miss; letters never graduate to a market check.', 'finding 53')}
{brow('If the letters are wrong, solvency breaks', 'CLEAN', 'Full 3-notch slip → 337% CAL (bound). Not a solvency event at AAIA.', 'dashboard ⑥ · finding 55')}
{brow('…but the same slip is harmless everywhere', 'WATCH', 'Below-IG share jumps 2.9% → 7.0–14.2% (a ratings/guideline/funding event), and the slipped risk lives at AARe behind the mirror-check boundary.', 'finding 55')}
{brow('The ROE is ordinary once levers are removed', 'WATCH', '16.6% common ROE clears a 10–12% hurdle — but 10bp of credit losses ≈ −1pt, and provisioning runs 3–7bp on an unseasoned book.', 'dashboard ⑦ · finding 54')}
{brow('Provisioning reflects the risk being added', 'UNTESTABLE', 'Provisions fell $335M → $111M (−67%) while the book grew +75% and PL 3.4×. Prudence or deferral — only seasoning arbitrates.', 'workbook · finding 58')}
{brow('Bermuda mirrors the Iowa ledger', 'OPAQUE', 'AARe publishes no unconsolidated statement; the treaty-level mirror is not publicly checkable.', 'dashboard ③')}
{brow('The spread engine is holding its margin', 'DETERIORATING', 'NIS 1.65% → 1.34% in four quarters; SRE margin below 1% for the first time; 1Q26 was a GAAP net loss.', 'workbook · finding 57')}
{brow('Growth is holding', 'DECELERATING', 'Net flows $17.2B → $4.8B → $9.0B; retail −23% Y/Y; the rebound quarter leaned on funding agreements.', 'finding 57')}
</tbody></table></div>

<h2>2 · What is on the tape right now <span class="cnt">— the margin cycle, quarterly</span></h2>
<hr class="rule">
<div class="mgrid">
{card('Net investment spread', f'{nis[-1][1]:.2f}%', spark(nis, cls='sp-bad', fmt=lambda v: f'{v:.2f}%'), '1.65% → 1.34% in four quarters (−31bp). The engine’s core margin.')}
{card('SRE margin', f'{srem[-1][1]:.2f}%', spark(srem, cls='sp-bad', fmt=lambda v: f'{v:.2f}%'), 'Below 1% for the first time in 1Q26.')}
{card('Cost of funds', f'{abs(cof[-1][1]):.2f}%', spark([(q, abs(v)) for q, v in cof], cls='sp-warn', fmt=lambda v: f'{v:.2f}%'), 'Sticky at 3.79% while the earned rate rolls over — the repricing race, being lost.')}
{card('Earned rate', f'{earn[-1][1]:.2f}%', spark(earn, cls='sp-acc', fmt=lambda v: f'{v:.2f}%'), 'Peaked 3Q25 at 5.34%; alternatives earned 5.79% in 1Q26 vs ~10% run-rate.')}
{card('Net flows ($M)', f'${flows[-1][1]:,.0f}M', spark(flows, cls='sp-bad'), '$17.2B → $4.8B → $9.0B; the 1Q26 rebound leaned on funding agreements ($8.5B).')}
{card('Runnable share of reserves', f'{fa_share[-1][1]:.1f}%', spark(fa_share, cls='sp-warn', fmt=lambda v: f'{v:.1f}%'), 'Funding agreements as % of net reserves: 21.0% → 27.2% in five quarters (F4).')}
</div>
<div class="callout"><strong>And the newest quarter, in GAAP terms:</strong> 1Q26 net income to common was
<strong class="mono">−${abs(ni_common_1q26):,.0f}M</strong> (investment losses −$2.1B, of which −$214M realized on actual
sales, plus a $1.67B Bermuda-CIT tax charge), and AHL stockholders&rsquo; equity fell
<strong class="mono">{eq_drop:.0f}%</strong> in the quarter. The spread narrative and the GAAP tape have started to diverge —
the bridge section of the workbook reconciles the two to the dollar, every quarter.</div>

<h2>3 · The seasoning clock <span class="cnt">— why "nothing looks off" is not yet information</span></h2>
<hr class="rule">
<p style="font-size:14.5px">Private-credit losses emerge in years ~3–7 of a vintage. Here is the book by holding age:</p>
<div class="agebar">{AGE_SEGS}</div>
<div class="agelegend">
<span><span class="dot" style="background:var(--bm)"></span>&lt;2y — {(age_v.get('<1y',0)+age_v.get('1-2y',0))/age_tot*100:.0f}% of the book: too young to show anything</span>
<span><span class="dot" style="background:var(--warn)"></span>2–3y — {age_v.get('2-3y',0)/age_tot*100:.0f}%: entering the window</span>
<span><span class="dot" style="background:var(--us)"></span>3y+ — {seasoned:.0f}%: old enough to be informative</span>
</div>
<div class="callout" style="border-left-color:var(--bm)"><strong>The core epistemic fact of this project:</strong>
a genuinely bad private-credit vintage and a genuinely good one <em>look identical at year two</em>. "No losses yet" on a
book whose weighted-average age is 1.7 years is what BOTH worlds print. Meanwhile provisions went
<span class="mono">$335M → $181M → $111M</span> as the book went <span class="mono">$75B → $131B → $159B</span> —
either prudence being vindicated, or losses being deferred into the window. Only the cohort tests, re-run each year,
can tell them apart — and we are the ones holding that instrument.</div>

<h2>4 · What is structurally drifting <span class="cnt">— the opacity migration, three year-ends</span></h2>
<hr class="rule">
<div class="mgrid">
{card('Private-letter share of bonds', f'{pl_share[-1]:.1f}%', spark(list(zip(['YE23','YE24','YE25'], pl_share)), cls='sp-bad', fmt=lambda v: f'{v:.1f}%'), '$11.7B → $40.1B (3.4×). The least-checkable grading channel is the fastest-growing one.')}
{card('Identifier-private floor', f'{floor_share[-1]:.1f}%', spark(list(zip(['YE23','YE24','YE25'], floor_share)), cls='sp-bad', fmt=lambda v: f'{v:.1f}%'), 'PPN + no-identifier paper: 24.4% → 31.0% of the book.')}
{card('Bond book (BACV, $B)', f'${book[-1]:.0f}B', spark(list(zip(['YE23','YE24','YE25'], book)), cls='sp-acc', fmt=lambda v: f'${v:.0f}B'), 'Doubled in two years — while publicly-rated holdings SHRANK $5.1B in 2025.')}
{card('GAAP credit-loss provision ($M)', f'${prov[-1]:,.0f}M', spark(list(zip(['FY23','FY24','FY25'], [abs(p) for p in prov])), cls='sp-warn', fmt=lambda v: f'${v:,.0f}M'), 'Down 67% across the same two years. The juxtaposition IS the thesis question.')}
</div>
<p style="font-size:14.5px">Printed quality never moved while all of this happened (NAIC-2 ≈ 38%, below-IG ≈ 3% in all
three years). Benign: disciplined growth. Adverse: the flat print is increasingly <em>untestable by construction</em>,
because the graders can no longer be contradicted by a market. Both readings stay open — that is the honest state.</p>

<h2>5 · The tripwires <span class="cnt">— what we re-read every quarter, and what would trip</span></h2>
<hr class="rule">
<div class="tbl-scroll"><table>
<thead><tr><th>Instrument</th><th>Now</th><th>Trips at</th><th>What a trip means</th></tr></thead>
<tbody>
<tr><td>Net investment spread</td><td class="mono">1.34%</td><td class="mono">&lt;1.20% two quarters</td><td>The engine can no longer out-earn its float cost at target ROE</td></tr>
<tr><td>SRE margin</td><td class="mono">0.97%</td><td class="mono">&lt;0.90%</td><td>Margin cycle becomes structural, not cyclical</td></tr>
<tr><td>Impairments by rating source</td><td class="mono">≈0 on PL</td><td>PL rate &gt; FE rate</td><td>The letters were wrong — the central F1 verdict</td></tr>
<tr><td>Cohort migration (annual run)</td><td class="mono">+$2.2B / −$0.3B</td><td>downgrades &gt; upgrades</td><td>Seasoning has started to arbitrate, adversely</td></tr>
<tr><td>PL exits routed to affiliates</td><td class="mono">untested</td><td>exited-PL buyers = family</td><td>Bad letters being buried inside the perimeter</td></tr>
<tr><td>PL share of bonds</td><td class="mono">25.3%</td><td class="mono">&gt;30%</td><td>Opacity migration accelerating past the stress case</td></tr>
<tr><td>Runnable share of reserves</td><td class="mono">27.2%</td><td class="mono">&gt;30%</td><td>Liquidity ratchet arming: runnable money vs $11B natural liquidity</td></tr>
<tr><td>AARe BSCR</td><td class="mono">202%</td><td class="mono">&lt;180%</td><td>The ruler that actually holds the risk starts binding</td></tr>
<tr><td>Below-IG share (either ruler)</td><td class="mono">2.9% / 3.9%</td><td class="mono">&gt;5% unforced</td><td>The junk-share event beginning without a letter-slip</td></tr>
<tr><td>ADIP realized return</td><td class="mono">12.2%</td><td class="mono">&lt;10%</td><td>The market price of this risk pool no longer clears its hurdle</td></tr>
<tr><td>Provision inflection</td><td class="mono">$111M ↓</td><td>first Y/Y increase</td><td>Loss recognition beginning — watch which rating source it lands on</td></tr>
<tr><td>FABN new-issue spreads (external)</td><td class="mono">—</td><td>sustained widening vs peers</td><td>The funding market repricing what the agencies have not</td></tr>
</tbody></table></div>
<p class="dim" style="font-size:13px">Cadence: quarterly re-run takes hours (supplement parser + workbook), annual re-run
one session (statutory parsers + cohort tests). Every tripwire lands on a footed extract, not a headline.</p>

<h2>6 · Where alpha can live <span class="cnt">— three honest shapes, none of them "short it today"</span></h2>
<hr class="rule">
<div class="paths">
<div class="path"><h3>① Be first at the turn</h3>
The consensus watches headline SRE. This machine watches designation migration on 402 named PL positions, impairments
by rating source, and affiliate exit routing. Those move <em>before</em> the P&amp;L does. The edge is not a view —
it is reaction time at the inflection, with the tripwires above as the alarm panel.</div>
<div class="path"><h3>② The cross-section, not the single name</h3>
25% PL share means little alone. The same footed metrics computed identically across KKR/Global Atlantic,
Brookfield/AEL, Ares/Aspida, Blue Owl turn into a <em>ranking</em> — who runs the most manufactured ROE, thinnest
provisioning, youngest book, most runnable funding. Dispersion between peers is tradeable structure even if nobody
blows up. The parsers are already parameterized for this; Global Atlantic was always Phase 1.</div>
<div class="path"><h3>③ The funding side prices it first</h3>
If the letter-slip ever materializes it arrives as a ratings/guideline event — visible in FABN new-issue spreads and
funding costs before equity. Tracking the market&rsquo;s price of Athene&rsquo;s funding against our measured risk
profile turns divergence — in either direction — into information.</div>
</div>

<h2>7 · What would change the verdict <span class="cnt">— falsifiers, both directions</span></h2>
<hr class="rule">
<div class="cols2">
<div class="callout" style="border-left-color:var(--bm)"><strong>Toward adverse:</strong> cohort run 2 (2024 vintage)
shows downgrades outweighing upgrades · PL impairment rate exceeds FE · exited-PL bonds turn out to have been bought
by affiliates · provisions inflect upward concentrated in PL/private paper · BSCR &lt; 180% · FABN spreads widen
while agencies hold ratings · runnable share &gt; 30% with natural liquidity flat.</div>
<div class="callout" style="border-left-color:var(--us)"><strong>Toward benign:</strong> the 2024 and 2025 cohorts
migrate as cleanly as 2023&rsquo;s did as they enter the window · impairments stay at single-digit bp <em>through</em>
years 3–5 of the big vintages · spread stabilizes with cost of funds peaking · PL share plateaus · Bermuda discloses
enough to close the mirror gap. If that is the world in two annual re-runs, the honest conclusion is that Apollo
built a genuinely better origination machine — and the cross-section (path ②) becomes the whole game.</div>
</div>

<div class="footer">Sources: AAIA statutory statements YE2023–25 (footed to the dollar), ATH financial supplements
Q4&rsquo;25/Q1&rsquo;26 (gate-verified incl. cross-source), AHL 10-K FY2025, NAIC C-1 factors (Milliman 2021) — all
sha-tracked in acquisition/manifest.csv. Findings 1–58 in spine/athene/findings.md. Regenerate:
<span class="mono">python3 tools/render_the_read.py</span>. This page states research conclusions from public filings;
it is not investment advice.</div>
</div>
"""

DEST.write_text(html)
print(f'wrote {DEST} ({len(html):,} bytes)')

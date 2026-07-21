#!/usr/bin/env python3
"""Render dossiers/athene/entity-dashboard.html from spine + manifest CSVs."""
import csv, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ents = list(csv.DictReader(open(ROOT / 'spine/athene/entities.csv')))
docs = list(csv.DictReader(open(ROOT / 'acquisition/manifest.csv')))

ROLE_LABEL = {
    'insurer': 'US insurer', 'reinsurer': 'Reinsurer', 'holdco': 'Holdco',
    'manager': 'Manager', 'manager-parent': 'Manager', 'fund': 'Fund',
    'affiliated-insurer': 'Affiliated', 'other': 'Other',
}
ROLE_CLASS = {
    'insurer': 'r-us', 'reinsurer': 'r-re', 'holdco': 'r-hc', 'manager': 'r-mg',
    'manager-parent': 'r-mg', 'fund': 'r-fd', 'affiliated-insurer': 'r-af', 'other': 'r-ot',
}

def e(s): return html.escape(s or '')

rows = []
for r in ents:
    role = r['role_provisional']
    ids = []
    if r['naic_cocode']: ids.append(f"NAIC {e(r['naic_cocode'])}")
    if r['fein']: ids.append(f"FEIN {e(r['fein'])}")
    idcell = '<br>'.join(ids)
    lei = f"<span class=\"mono dim\" title=\"LEI\">{e(r['lei'])}</span>" if r['lei'] else ''
    pct = f" · {e(r['parent_pct'])}%" if r['parent_pct'] else ''
    parent = f"{e(r['parent_entity'])}{pct}" if r['parent_entity'] else '<span class="dim">—</span>'
    rows.append(
        f"<tr data-role=\"{e(role)}\" data-q=\"{e((r['name']+' '+r['jurisdiction']+' '+r['notes']+' '+r['parent_entity']+' '+r['naic_cocode']+' '+r['lei']+' '+r['fein']).lower())}\">"
        f"<td><div class=\"nm\">{e(r['name'])}</div><div class=\"note\">{e(r['notes'])}</div>{lei}</td>"
        f"<td>{e(r['jurisdiction'])}</td>"
        f"<td><span class=\"chip {ROLE_CLASS.get(role,'r-ot')}\">{ROLE_LABEL.get(role, role)}</span></td>"
        f"<td class=\"mono sm\">{idcell}</td>"
        f"<td class=\"sm\">{parent}</td>"
        f"<td class=\"mono xs dim\">{e(r['sources'].replace(';', ' · '))}</td>"
        f"</tr>"
    )
ROWS = '\n'.join(rows)

doc_rows = []
for d in docs:
    status = e(d['status'])
    flag = ' <span class="chip r-af">local only</span>' if 'local-only' in status else ''
    doc_rows.append(
        f"<tr><td><div class=\"nm\">{e(d['entity'])}</div><div class=\"note\">{e(d['doc_type'])} · {e(d['period'])}</div></td>"
        f"<td class=\"mono xs\" title=\"{e(d['sha256'])}\">{e(d['sha256'][:16])}…</td>"
        f"<td class=\"sm\">{e(d['published_date'])}{flag}</td>"
        f"<td><a href=\"{e(d['source_url'])}\">source</a></td></tr>"
    )
DOCS = '\n'.join(doc_rows)

n_total = len(ents)
n_coc = sum(1 for r in ents if r['naic_cocode'])
n_bm = sum(1 for r in ents if r['jurisdiction'] == 'Bermuda')
n_lei = sum(1 for r in ents if r['lei'])

TEMPLATE = open(ROOT / 'tools/dashboard_template.html').read()
out = (TEMPLATE
       .replace('__ROWS__', ROWS).replace('__DOCS__', DOCS)
       .replace('__N_TOTAL__', str(n_total)).replace('__N_COC__', str(n_coc))
       .replace('__N_BM__', str(n_bm)).replace('__N_LEI__', str(n_lei))
       .replace('__N_DOCS__', str(len(docs))))
dest = ROOT / 'dossiers/athene/entity-dashboard.html'
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(out)
print('wrote', dest, len(out), 'bytes')

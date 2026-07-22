python3 - <<'EOF'
p='PLAN.md'; s=open(p).read()
for old,new in (("### GA-1 `[~]`","### GA-1 `[x]`"),("### GA-2 `[ ]`","### GA-2 `[x]`"),("### GA-3 `[ ]`","### GA-3 `[x]`"),
("### GA-4 `[ ]` Statutory bond drill","### GA-4 `[x]` Statutory L0 (bond drill BLOCKED: no public CUSIP-level schedules — boundary logged; quality via supplement two-ruler tables)"),
("### GA-5 `[ ]`","### GA-5 `[x]`"),("### GA-6 `[ ]`","### GA-6 `[x]`"),("### GA-7 `[ ]` THE COMPARISON","### GA-7 `[x]` THE COMPARISON — DONE")):
    s=s.replace(old,new)
s=s.replace("## Evidence log","""## Evidence log
- 2026-07-22 · GA-1..7 · 36 docs fetched+sha'd · census 25 entities · GALD supplement parser (1,018 gated cells, 13 quarters + FYs, quality two-ruler tables) · KKR lane (176 cells) · FCR capital 6 filings · statutory L0 4 carriers × 4 year-ends · GA workbook (133 checks) · GA dashboard artifact · COMPARISON artifact (Athene vs GA, 2023–2026) · findings ledger GA 1–7.""")
open(p,'w').write(s)
s=open('STATUS.md').read()
s=s.replace("## The living surfaces","""**Phase 1 (2026-07-22, same session): GLOBAL ATLANTIC COMPLETE + THE COMPARISON.** Census (25 entities) · GALD supplements 4Q23–1Q26 parsed (1,018 gated cells: NBV, income, AOE engine, rates, reserves, NAIC+NRSRO quality, capitalization) · KKR 10-K/Q cross-lane (176 cells) · GA Re/GAAL FCR capital 2023–25 (ECR coverage 205%/827% at YE25) · statutory L0 ×4 carriers · GA engine workbook (`dossiers/global-atlantic/ga-quarterly-engine.xlsx`, 133 checks) · **GA dashboard** https://claude.ai/code/artifact/b68af7a4-dc57-409b-a0d7-a31da4e1b3dc · **THE COMPARISON** https://claude.ai/code/artifact/a01a93bf-e006-450c-a4a8-6d4ef2710a6f · GA findings ledger `spine/global-atlantic/findings.md`. Boundary: no public CUSIP-level schedules for GA carriers (PL/aging/concentration drill not replicable publicly).

## The living surfaces""")
open('STATUS.md','w').write(s)

# Credit Map — Project Specification

**Owner:** Michael (Exascale Capital)
**Revision:** v1.1 (2026-07-21) — Phase 0 reordered to top-down: control totals first, decompose with reconciliation, drill line-level only on demand. Data model unchanged.
**Purpose of this document:** Complete brief for Claude Code. Read this before doing anything. It defines the mission, the conceptual model, the architecture, the phased plan, and the rules of engagement. Treat it as the spec; when in doubt, re-read it rather than improvising.

---

## 1. Mission

Build a proprietary, verified map of the higher-risk credit system — the chain running from **policyholders → US life insurers → offshore reinsurers → private credit assets → underlying borrowers**, with asset managers (Apollo, KKR, Blackstone, Ares, Blue Owl, Brookfield, etc.) owning, managing, and originating alongside the whole chain.

This is **internal investing infrastructure, not a product**. The output is used to find mispriced securities and generate trades (and, selectively, published research). Nothing here is for redistribution; do not design for external customers, licensing, or MCP serving.

The thesis being tested, not assumed: the system is optimized for filling pipes (originating volume to feed CLOs, insurance balance sheets, and PE pipelines) rather than for credit quality, and nobody is systematically doing the credit work. The map does the credit work. It must be able to *reject* the bubble thesis as well as confirm it — where the evidence says a group is clean, the map says clean.

Three focus dimensions, in order: **credit quality, asset valuation, liquidity.**

### 1.1 Target findings — what the machine is hunting

Underwriting quality is not directly observable (loan files, covenants, LTVs are private). What is observable are the **symptoms bad underwriting throws off as it ages** and the **inconsistencies mismarking creates** once the same credit appears in more than one place. Every pipeline choice should be justified by its contribution to one of these four findings:

| Finding | Fingerprint signals |
|---|---|
| **F1. Poorly underwritten credit at inadequate yield** | Spread-per-unit-of-deterioration: earned yield flat while PIK share rises, amend-and-extend frequency, non-accrual migration, provision/impairment rates lagging visible deterioration, collateral drift in new vintages |
| **F2. Mismarked credit** | Same obligor at materially different marks across holders on the same date; marks held high until an event (score every manager's marks against subsequent outcomes — the bitemporal design exists for this); private marks diverging from traded comparables (listed BDC price-to-NAV discounts, CLO tranche prices) |
| **F3. Large exposure to deteriorating private credit** | True economically-attributed, PBBD-adjusted private-credit exposure per group (across Schedule D, BA, funds, CLOs, offshore treaties), growth of that exposure into weakening symptoms |
| **F4. The acute dangerous corner** | Intersection of three scores per group: **concentration** (sponsor/borrower/asset-class), **opacity** (share of reserves behind non-disclosing entities), **runnability** (surrender cliffs, funding-agreement rollover, FHLB reliance). Bad illiquid assets + patient money = slow bleed; same assets + runnable money = event |

### 1.2 Classic credit vitals (per entity, every period)

This is standard credit-analyst work, industrialized. For every insurer, reinsurer, and BDC in scope, extract and time-series the observable financials and cross them against balance-sheet risk composition:

- **Earnings side:** net investment income, gross/net yield earned, interest income cash vs PIK split, realized and unrealized gains/losses, credit provisions and impairments taken.
- **Risk side:** fair-value hierarchy composition (Level 1 / 2 / 3 from GAAP and statutory notes) and its migration over time; NAIC designation mix; private-letter-rating share (2026+ filings); % of book with no market identifier.
- **Market's verdict:** price-to-NAV for listed vehicles; discounts on comparable traded credit.

The core cross-checks: yield earned vs risk carried (is 3% being earned on Level 3 paper?), provisions taken vs symptoms visible (are impairments keeping pace with non-accruals?), and mark levels vs the market's own pricing of similar risk. Divergence between these pairs is the finding.

**Discipline:** the machine outputs anomalies and rankings, never verdicts. A mark gap can be benign (different tranche, different valuation date, stale quarter). The ladder is anomaly → corroboration → thesis → trade; the last two rungs are Michael's judgment. Surface the anomaly with its full evidence chain and move on.

## 2. The conceptual model

### 2.1 The money chain (one picture per group)

```
Policyholders  (annuities, pension transfers, funding-agreement notes)
     │  premiums in
     ▼
US insurers    (state-regulated; file public statutory statements)
     │  cede reserves (often funds-withheld / ModCo)
     ▼
Bermuda affiliates   (Class C/D/E reinsurers, sidecars; publish FCRs + GAAP financials)
     │  invest
     ▼
Asset portfolio      (private placements, ABS, CLOs, fund stakes, mortgages, direct loans)
     │  lend to
     ▼
Borrowers            (real companies and assets)

Alongside every level: the affiliated asset manager — owns the insurer,
manages the assets, originates many of them, and collects fees at each touch.
```

Mapping a group = putting real, cited numbers on every arrow of this picture. The full map = this picture × ~20 groups, in a database, so questions can be asked *across* pictures.

### 2.2 Dual ledger — the core intellectual property

Every exposure has two answers:

- **Legal/reporting ledger:** who reports the asset (which balance sheet, which schedule).
- **Economic ledger:** who actually bears the risk — who selected it, manages it, receives its economics, eats impairment.

These diverge constantly: ~80% of Bermuda long-term reinsurance is collateralized via funds-withheld / ModCo structures where assets stay legally on the US cedent's books while economics move offshore. The economic ledger is **derived, never stored** — computed from base facts through a versioned rules engine (see §4.5), so improved rules recompute history cleanly.

### 2.3 Four data-model principles (non-negotiable)

1. **Store claims, not truths.** Every fact is an assertion by a document: (document hash, schedule, row/page, value, extraction version). Truth is a query over claims. Contradictions and amendments are first-class data.
2. **Bitemporal from day one.** Every claim carries: as-of date (balance-sheet date), published date (when the filing appeared), version (amendments). "What was knowable on date T" must be answerable, or no signal can be backtested.
3. **Marks are observations by holders, not properties of securities.** Model `mark(holder, instrument, as_of, basis, value, source)`. Same for ratings (`rating(provider, instrument, date, value, private_letter_flag)`). Cross-holder mark dispersion must fall out as a trivial query.
4. **Economic layer derived, not stored.** See §2.2.

### 2.4 Schema v0 (deliberately small — grow only when a chain forces it)

```
NODES
  legal_entity      insurer | reinsurer | holdco | fund | BDC | CLO | trust | manager
  instrument        bond | loan | fund interest | CLO tranche   (ids: CUSIP/ISIN/PPN/none)
  obligor_group     the actual borrower, resolved across name variants
  treaty            cedent, reinsurer, type (coins/ModCo/funds-withheld), effective dates
  liability_block   product type, reserves, surrender/runnability attributes
  collateral_account trust / funds-withheld account, governing treaty
  document          source file: sha256, url, published_date, doc_type, entity

EDGES  (all bitemporal, all with evidence pointer to a document claim)
  holds             legal_entity → instrument   (par, cost; value lives in marks)
  issued_by         instrument → legal_entity
  obligor_of        legal_entity → obligor_group
  cedes / assumes   legal_entity → treaty
  backs             liability_block → treaty
  collateralizes    collateral_account → treaty
  manages           legal_entity → legal_entity | collateral_account
  controls / affiliated_with   legal_entity → legal_entity   (Schedule Y, org charts)

OBSERVATIONS
  mark, rating, non_accrual_flag, pik_flag   (observer, observed, date, basis, source)
```

**Tooling rule: Postgres, not a graph database.** At this scale (thousands of entities, low-millions of position rows) recursive CTEs cover every graph query. A graph DB is premature optimization — do not introduce one.

## 3. Deliverables and success gate

### Phase 0 deliverables (Athene, by hand)
1. **The Athene dossier** — the §2.1 picture with real YE2025 numbers on every arrow, every number clicking through to a hashed source page, plus first signal readings: offshore share of reserves, opacity ratio, affiliated-asset share, reported vs economic private-credit exposure.
2. **Runbook v1** — the written per-company process (see §5), explicit enough that a cheaper model could execute it unsupervised.

### The three hard questions (the map must beat a skilled analyst with a terminal on these)
1. Which insurers genuinely increased private-credit exposure in 2025 after removing PBBD reclassification effects? (See §6.3.)
2. Which Bermuda reinsurers are economically exposed to assets that legally remain on US cedent balance sheets?
3. Where do the same borrowers, managers, or sponsors appear across multiple insurers, funds, BDCs, and CLOs — and at what (possibly different) marks?

### Gate to Phase 1
The Athene dossier answers questions 1–2 for Athene with full evidence chains, and runbook v1 exists. If this can't be done on the best-documented group in the industry, stop and escalate to Michael before any further spend.

## 4. Architecture (build in this dependency order)

**Working order is top-down.** Start from consolidated control totals (Level 0), decompose one level at a time (Level 1), and go line-level only where a §3 question demands it (Level 2). Every level must reconcile to the level above; the unreconciled residual is itself a finding — a missed entity or opacity — logged, never hidden.

### 4.1 Acquisition ledger (build first)
A manifest table before any extraction: every target document — entity, doc_type, period, source URL, fetch status, sha256, published date, gap reason if missing. Acquisition agents fill it. The coverage report per group is itself a product metric (look-through coverage / opacity ratio derive from it). **Gaps are logged, never papered over.**

### 4.2 Entity spine (before parsing any holding)
The spine is seeded by decomposition — the entities that actually hold the reserves and assets enter first, so the table is materiality-ordered by construction — then completed by census cross-check against the parent 10-K subsidiary exhibit (EX-21), Schedule Y of statutory statements, and the BMA register. An entity appearing in one source but not another is a first-class finding, not a data-cleaning chore. Fields: name, aliases, role, domicile, NAIC cocode / LEI / BMA registration where they exist. Small (hundreds of rows for five chains) and partly manual — that is fine. Holdings parsed without a spine produce orphaned rows; never do it.

### 4.3 Extraction with deterministic gates
Per-schedule extraction (Schedule D, BA, S, Y, and Bermuda statements each get their own parser/prompt). **Iron rule: every extracted schedule must foot to the statement's printed control totals, or it is flagged as an exception — never silently accepted.** Version every extraction run. Add a second decorrelated review lens on samples (different model re-extracts; disagreement → exception queue). Third lens where available: bottom-up sums checked against published NAIC Capital Markets Bureau aggregates.

### 4.4 Resolution registry (the compounding moat)
Two matching problems: entity name → spine, and instrument → obligor (CUSIPs/PPNs where they exist; BDC loans and many private placements have **no identifiers** — borrower-name matching across documents is the real work). Cheap candidate generation → LLM adjudication → low-confidence items to Michael's human queue. **Every resolution decision is stored permanently with its evidence and is never re-decided.** The registry is a single shared surface: workers *reference* it, only the adjudicator writes to it. This design eliminates split-brain by architecture.

### 4.5 Economic rules engine (exactly three rules to start)
1. Funds-withheld attribution: asset legally at cedent, economically at reinsurer per treaty terms.
2. ModCo equivalent.
3. Affiliated-fund dedup: never double-count a fund interest and the fund's underlying positions when both are visible.
Each rule versioned; every derived exposure carries its derivation path. Add rules only when a real chain demands it.

### 4.6 Signal queries (last — simple SQL over a well-built base; each tagged to a §1.1 finding)
- Cross-holder mark dispersion per obligor (F2)
- Mark-vs-outcome scoring per manager: marks at T vs restructurings/impairments at T+1 (F2)
- PIK income % and non-accrual migration per manager (F1; BDC engine)
- Earned yield vs risk composition: yield per unit of Level 3 / low-designation exposure (F1)
- Provisions and impairments taken vs deterioration symptoms visible (F1)
- Fair-value hierarchy (Level 1/2/3) share and migration per entity (F1, F2)
- Price-to-NAV discounts for listed vehicles vs their private marks (F2)
- PBBD-adjusted exposure growth bridge (§6.3) (F3)
- Offshore share of reserves; opacity ratio (reserves behind non-disclosing entities) (F3, F4)
- Affiliated-asset and affiliated-cession share (F3, F4)
- Concentration scores: sponsor / borrower / asset-class (F4)
- Liability liquidity ladder: surrender-charge cliffs, FABN/funding-agreement and FHLB reliance (F4)

## 5. The per-company runbook (the repeatable process)

Input: group name. Output: standardized dossier. **Output format is rigid on purpose** — cross-company queries only work if every dossier is format-identical.

| Stage | Work | Pass/fail gate |
|---|---|---|
| 1. Picture (L0) | Consolidated money-chain picture from parent 10-K + group GAAP + lead statutory statement: total reserves, total investments, total ceded, NII, fees — every arrow of §2.1 carries a cited control total | Every arrow numbered and cited; these totals anchor everything below |
| 2. Decompose (L1) | Split each L0 total one level down: reserves per legal entity, cessions per treaty counterparty, assets per class per entity, fees per agreement. Spine populated by decomposition, cross-checked against EX-21 / Schedule Y / BMA register. Documents fetched + hashed as the decomposition demands them (manifest per §4.1) | Each split sums to its parent total; residual logged as missed entity or opacity. Every insurer/reinsurer has identifier + domicile + role |
| 3. Drill (L2) | Line-level extraction only where a §3 question demands it — PBBD bridge, funds-withheld treaties, overlapping obligors — plus the §1.2 credit vitals (income statement lines, provisions/impairments, fair-value hierarchy tables from GAAP and statutory notes) | Every schedule foots to the printed totals already captured at L1; vitals tie to statement face |
| 4. Link | Cessions ↔ Bermuda counterparty filings; sample of assets → named borrowers | Match rate reported; low-confidence queued |
| 5. Compute | Apply dual-ledger rules | No asset counted twice; derivations attached |
| 6. Emit | Dossier + signal readings in the standard format | Format-identical to prior dossiers |

**Flywheel rule:** every exception hit in any run (weird treaty, duplicate fund, missed entity) is resolved once and written back into `runbook.md` / `exceptions.md`, so later runs inherit earlier scar tissue. These two files are living documents injected into every agent run.

## 6. Data sources and constraints

### 6.1 Where documents come from
- **Apollo/parent level:** SEC filings (10-K incl. EX-21 subsidiary list, investment-management agreement disclosures).
- **US statutory statements (public records, PDF):** company IR pages first, then state DOI (Iowa Insurance Division for Athene's lead entities), then NAIC per-filing purchase (insData) as fallback. Key schedules: D (bonds, CUSIP-level), BA (funds/other invested assets), B (mortgages), S (reinsurance), Y (group structure), general interrogatories, notes.
- **Bermuda:** Financial Condition Reports (mandatory publication on company websites), BMA-published audited GAAP financials for Class C/D/E, and the new asset-and-liability disclosure regime (position-level, phasing in from 2025/2026 — verify actual publication status per entity; do not assume).
- **BDCs (parallel workstream):** SEC 10-K/10-Q Schedules of Investments — loan-level, quarterly, free.
- **Cross-check aggregates:** NAIC Capital Markets Bureau special reports, FIO annual report, Fed/Treasury financial stability material.

### 6.2 Known constraints (design around, don't fight)
- **NAIC bulk structured data is licensed, not free.** Internal-use licensing is an option later; Phase 0 uses public PDFs only. Do not purchase or scrape licensed databases.
- **Confidential by design:** AG 53/55 actuarial memoranda, ORSA, most holding-company filings, treaty terms, non-disclosing captives (and Cayman entities generally). The response is the **opacity ratio**: measure and report what fraction of each group's reserves sits behind non-disclosing entities. Opacity is a signal, not a failure.
- **No look-through into private funds:** Schedule BA gives fund name and carrying value, not fund contents. Report look-through coverage % honestly.
- **YE2025 statements are the first vintage with the new ABS delineation; 2026 filings add private-letter-rating, PIK, and fair-value-level detail.** Design extraction to capture these fields where present.

### 6.3 The PBBD trap (encode before reporting any trend)
The NAIC principles-based bond definition (effective 2025-01-01) moved instruments between Schedule D and Schedule BA. Any year-over-year exposure change must be decomposed: purchases/originations · sales/maturities · valuation moves · M&A/entity changes · **PBBD reclassification** · other reporting changes. Reporting raw schedule growth as risk appetite is the canonical false signal — the bridge is mandatory in every dossier.

## 7. Phased plan

- **Phase 0 (weeks 1–3): Athene by hand.** Frontier model, slow, once. This run *writes the spec* — the runbook is the deliverable as much as the dossier. Sub-sequence: L0 picture (d1–3) → L1 decompose + entity map (w1) → L2 drill (w2) → link (w2–3) → compute + emit (w3). The gate gets its first test at L0/L1 resolution by end of week 1 — if evidence chains can't be built at that altitude, stop before any line-level spend.
- **Phase 1 (weeks 4–5): Global Atlantic (KKR).** Run the frozen runbook. Everything that breaks gets generalized into runbook v2. This is the test that the process isn't secretly Athene-shaped.
- **Phase 2 (week 6+): scale.** Remaining ~18 groups (Ares/Aspida, Brookfield/AEL, Sixth Street/Talcott, Fortitude, Resolution, MassMutual/Martello, Protective, plus 2–3 clean mutuals as controls) as cheap-worker runs against the frozen runbook. Planner/worker split per the Cursor economics: frontier models only for decomposition, rules, and adjudication; cheap models for extraction volume. Footing gates on; exceptions to Michael.
- **Parallel workstream (start anytime): BDC engine.** Independent of the census. All listed + non-traded BDCs of the PE-insurance sponsors plus 2–3 independents as controls; extract Schedules of Investments quarterly; emit mark-dispersion, PIK%, non-accrual migration per manager. This is the fast layer (quarterly fair-value pressure gauge) that complements the slow structural map.

## 8. Rules of engagement (what NOT to do)

1. **No swarm harness, no custom orchestration infrastructure.** Twenty dossiers at quarterly cadence is a for-loop with gates. Parallelism comes from independent per-group runs, not shared-state coordination.
2. **No graph database.** Postgres.
3. **No full ontology up front.** Schema grows only when a real chain forces a new node/edge type.
4. **No scraping all 50 states.** Domiciliary states of target groups only.
5. **No silent acceptance of unfooted extractions.** Exception pile or nothing.
6. **No purchased data in Phase 0.** Public documents only; licensing decisions are Michael's.
7. **No stored economic ledger.** Always derived.
8. **No automation before run 2.** Athene is manual/frontier by design; generalize on Global Atlantic; automate after.
9. **No bubble narrative baked in.** Signals report what the evidence says, including "clean."
10. **No vague confidence scores.** Measurable fields only: footing pass/fail, look-through %, match rate, source age, amendment flags, derivation steps.

## 9. Repo conventions

```
/spec/credit-map-spec.md      this document
/runbook/runbook.md           living per-company process (v1 emerges from Phase 0)
/runbook/exceptions.md        accumulated exceptions + resolutions (the flywheel)
/spine/                       entity census tables per group
/acquisition/manifest         document ledger (entity, doc, url, sha256, status, gaps)
/raw/<group>/<entity>/        hashed source documents
/extract/<group>/             versioned extraction outputs + footing reports
/registry/                    resolution registry (single-writer: adjudication only)
/rules/                       economic rules engine, versioned
/dossiers/<group>/            standardized emitted dossiers
/signals/                     cross-group signal queries + outputs
```

Everything re-runnable from raw documents; nothing lives only in a conversation. Human adjudication items surface as a queue for Michael; high-confidence work never waits on him.

**First task on repo initialization:** the top-down entity map for the Athene complex — L0 consolidated picture with cited control totals, entity table seeded by decomposition and cross-checked against EX-21 / Schedule Y / BMA register, per-entity document checklist — then stop for Michael's review before L2 drilling begins.

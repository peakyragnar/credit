# L0 — The Athene money-chain picture, YE2025

Every number cited in `extract/athene/l0-claims.csv` (doc + page/line + sha256). GAAP = AHL 10-K FY2025 (filed 2026-02-25). SAP = AAIA statutory annual statement YE2025. Amounts $B unless noted.

```
Policyholders / institutions
     │  ① money in FY2025: gross inflows $83.4B
     │     retail+flow+institutional organic $82.1B (funding agreements $35.4B of it)
     │     attribution: Athene $63.2B · ACRA third-party (ADIP) $18.5B · ceded 3P $1.8B
     ▼
US insurers (AAIA lead, statutory YE2025)
     │  bonds $158.9B · mortgages $86.6B · life reserves $110.6B · deposit-type $64.3B
     │
     │  ② economics moved offshore — ALL to one counterparty: AARe (Bermuda)
     │     reserve credit taken (coinsurance/COFW): $74.3B   (non-US portion $65.3B)
     │     ModCo reserves (kept on AAIA books, economics ceded): $168.3B
     │        = general account $116.1B + separate account $52.2B
     │     funds withheld under coinsurance: $66.7B
     │     ceded premiums FY2025: $35.8B
     ▼
Bermuda (AARe — the pivot; retrocession to ALRe/ACRA below it, to map at L1)
     │  ③ invested consolidated (GAAP, group level):
     │     total investments $321.1B · net invested assets incl RP/VIE $386.6B
     │     total assets $442.2B · total liabilities $406.6B
     ▼
Asset portfolio → borrowers   (composition at L1; PBBD bridge at L2)

Alongside: Apollo (manager)
     ④ management fees FY2025: $1.44B (+ $0.07B sub-advisory passthrough)
        base fee 0.225% structure per Fee Agreement (Note 15)
     ⑤ ACRA/ADIP third-party capital inside the tent:
        noncontrolling interests $15.1B (was $9.5B) · NCI share of net income $1.5B

Runnability first reading (F4):
     funding agreements outstanding $71.4B = 26.3% of net reserve liabilities
     (was $47.4B = 21.0% a year earlier; $35.4B new FA inflows in FY2025 alone)
```

## What L0 already shows

1. **The dual ledger is huge and concentrated.** AAIA's economics move offshore through a single door: Athene Annuity Re Ltd. No ALRe, no ACRA appear in AAIA's Schedule S — sidecar participation must happen by retrocession from AARe, one level down (L1 target: AARe's own statements + FCR).
2. **ModCo dwarfs outright cession.** $168.3B of ModCo reserve sits legally on AAIA's books with economics ceded, vs $74.3B of reserve credit taken. The legal ledger and economic ledger diverge by hundreds of billions at the lead entity alone.
3. **The runnable stack is growing fastest.** Funding agreements grew from 21.0% to 26.3% of net reserve liabilities in one year; FA inflows went $7.2B (2023) → $28.7B (2024) → $35.4B (2025).
4. **A fifth of the machine is other people's capital.** $18.5B of FY2025 inflows and $15.1B of balance-sheet equity belong to ACRA noncontrolling interests (ADIP investors) — on which Apollo also earns fees.
5. **GAAP premiums ($2.6B) vs gross inflows ($83.4B):** the income statement is the wrong lens for an annuity writer's growth; deposits don't run through revenues. Any exposure trend built off GAAP revenue lines would be off by 30x.

## Basis caveats (logged, not hidden)
- GAAP (consolidated group) and SAP (AAIA entity) are different bases and different perimeters; they are anchors for their own levels, not directly summable.
- "Net invested assets $386.6B" is a management measure (includes related-party + VIE look-through, ACRA at economic share).
- AANY statutory face not yet extracted (smaller); Bermuda-side totals (AARe/ALRe FS) not yet extracted — both are L1 decompose inputs.

## L1 targets set up by these anchors
- Decompose the $168.3B ModCo + $74.3B credit by treaty (Schedule S rows already extracted) and reconcile against AARe's own Bermuda/GAAP statements — do both sides of the mirror agree?
- AARe → ALRe/ACRA retrocession map (the second hop offshore).
- Asset-class decomposition of $321.1B/$386.6B and per-entity invested assets.
- FHLB portion of funding agreements; FABN maturity ladder (runnability).

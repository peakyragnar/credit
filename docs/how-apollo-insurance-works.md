# How Apollo/Athene Insurance Works — a teaching note

**Purpose:** plain-English mental model of what Athene actually is, so the numbers in the dossier mean something. Read top to bottom once; after that it's a reference. Nothing here is a finding — it's the background you need before the findings make sense.

---

## 0. The one question this note answers

> Is the Athene flow — policyholders → US insurer → Bermuda reinsurer → private credit → borrowers, with Apollo alongside — *how insurance works*, or just *one way* to do it?

**One way.** And a specific, relatively new, aggressive one. All insurance shares a single engine (Section 1). But there are several different businesses built on that engine (Section 2), and within the one Athene is in, there's a spectrum from conservative to aggressive — Athene sits at the far aggressive end on purpose (Sections 3–4). If you remember nothing else: **the basic engine is universal; almost every distinctive thing about Athene is a deliberate choice, not a necessity.**

---

## 1. The engine every insurer shares: take money now, pay later, keep the gap

Strip away all the jargon and every insurer on earth does the same three things:

```
   ┌─────────────┐     money now      ┌─────────────┐
   │  Customers  │ ─────────────────▶ │   Insurer   │
   └─────────────┘                    └─────────────┘
                                             │
                          invests the money  │  (the "float")
                                             ▼
                                      ┌─────────────┐
                                      │   Assets    │  earns a return
                                      └─────────────┘
                                             │
   ┌─────────────┐    money later (claims,   │
   │  Customers  │ ◀── benefits, payouts) ───┘
   └─────────────┘
```

1. **Collect money now** (premiums or deposits).
2. **Pay money later** (claims, benefits, or the savings back with interest).
3. **Invest the money in between** — the pile of not-yet-paid-out cash is the **float**.

The insurer makes money two ways: **underwriting** (did I collect more than I paid out?) and **investment** (what did I earn on the float in the meantime?). Every insurer is some blend of "underwriter" and "investor." *Which blend* is what splits the industry into different businesses.

---

## 2. The four businesses built on that engine

Same engine, very different machines bolted onto it:

```
                          UNDERWRITING-DRIVEN  ◀──────────────▶  INVESTMENT-DRIVEN
                          (profit from risk)                    (profit from spread)

  ┌────────────────┐   ┌────────────────┐   ┌────────────────┐   ┌────────────────┐
  │  A. P&C        │   │  B. Protection │   │  C. Spread /   │   │  D. PE-        │
  │  insurance     │   │  life          │   │  annuity       │   │  insurance     │
  │                │   │                │   │  (traditional) │   │  ← ATHENE      │
  ├────────────────┤   ├────────────────┤   ├────────────────┤   ├────────────────┤
  │ car, home,     │   │ term & whole   │   │ fixed/indexed  │   │ same products  │
  │ liability      │   │ life           │   │ annuities      │   │ as C, but      │
  │                │   │                │   │                │   │ supercharged   │
  │ risk: claims   │   │ risk: death    │   │ risk: mostly   │   │ (Section 3)    │
  │  vs premiums   │   │  timing        │   │  the spread    │   │                │
  │                │   │                │   │                │   │                │
  │ e.g. GEICO,    │   │ e.g. Northwest │   │ e.g. a plain   │   │ e.g. Athene,   │
  │  Berkshire     │   │  -ern Mutual,  │   │  stock life    │   │  Global Atl.,  │
  │                │   │  MassMutual    │   │  annuity book  │   │  Aspida...     │
  └────────────────┘   └────────────────┘   └────────────────┘   └────────────────┘
```

**A. Property & Casualty** — car, home, business liability. The money-out is *unpredictable* (an accident could happen tomorrow), so the float must be invested **conservatively and liquid**. Profit comes mainly from **underwriting** — pricing risk better than the next insurer. This is Warren Buffett's Berkshire model. *Athene is not this at all.*

**B. Protection life** — term and whole life, sold mostly by old mutual companies owned by their policyholders. The risk is **mortality** (when people die). They invest for **decades, conservatively** (investment-grade bonds), and compete on underwriting and patient compounding. Slow and boring by design. *Athene is not this either.*

**C. Spread / annuity business (traditional)** — here's the pivot. An **annuity is not really insurance against a disaster — it's a savings product.** You hand the insurer money; they promise to pay you a set interest rate for a set time; you get it back later. The insurer's profit is the **spread**: what they earn investing your money *minus* what they promised to pay you.

```
   you get promised:        3%
   insurer earns:           5%   on your money
   ─────────────────────────────
   the SPREAD (profit):     2%   ← this is the whole game
```

This is already **more of an asset-management business than an insurance business** — a bank-like spread machine wearing an insurance wrapper. A *traditional* annuity writer runs it conservatively: invest-grade public bonds, full capital held at home, money managed at arm's length.

**D. PE-insurance — where Athene lives.** Take business C and push every lever to its limit. Same annuity products, same spread engine — but re-engineered by an affiliated private-equity firm (Apollo) to make the spread wider, the balance sheet bigger, and the capital go further. *That re-engineering is the next section, and it's the whole reason this project exists.*

So the flow you learned is **model D specifically.** Roughly 20 groups run it (Apollo/Athene, KKR/Global Atlantic, Blackstone, Ares, Brookfield, etc. — our target list). It barely existed before ~2009 (Apollo founded Athene in 2009). Regulators call it "asset-intensive reinsurance"; critics call it the "Bermuda triangle." It is one model among four, and the newest.

---

## 3. The four levers that turn business C into business D

A traditional annuity writer and Athene sell the *same product*. Athene is different because Apollo pulls four levers at once. Each lever widens profit — and each one creates one of the risks we hunt.

```
  LEVER                    TRADITIONAL           ATHENE / PE-INSURANCE        creates
  ─────────────────────────────────────────────────────────────────────────────────
  1. What you invest in    investment-grade      private credit the          ← F1 credit
                           public bonds          affiliate ORIGINATES          quality
                                                  (higher yield, illiquid,
                                                   hard to mark, opaque)      ← F2 marks

  2. Where capital sits    onshore, full         Bermuda reinsurer, lighter  ← F4 opacity
                           US capital rules       capital + tax rules

  3. Who manages money     third party,          the affiliate (Apollo)       (fees at
                           arm's length          owns insurer, picks assets,   every step)
                                                  originates them, marks them,
                                                  earns fees on all of it

  4. How you fund it       sticky retail         retail annuities PLUS        ← F4 run-
                           annuities             institutional funding          nability
                                                  (FABN) that can leave
                                                  on a schedule
```

**Lever 1 — asset side: originate-to-hold private credit.** Instead of buying public bonds anyone can price, invest in private loans, asset-backed deals, and fund stakes that **Apollo itself originates**. Higher yield → wider spread. But these assets are illiquid, have no market price (so their value is an *opinion*, not a quote), and are often behind non-disclosing entities. → This is why we hunt **F1 (bad credit at low yield)** and **F2 (mismarked credit)**.

**Lever 2 — capital side: reinsure to Bermuda.** A US insurer must hold a thick capital cushion under US rules. Reinsure the business to an affiliated Bermuda company and the same book needs *less* capital and pays *less* tax — freeing capital to write even more. Note: reinsurance itself is normal and healthy; the twist here is reinsuring to a company **you own**, for capital/tax efficiency, not to transfer risk to an outside party. → This is why we measure **F4 opacity** (how much sits behind lightly-disclosed offshore entities).

**Lever 3 — ownership: the affiliate does everything.** In the traditional model the insurer and its asset manager are separate, dealing at arm's length. Here **Apollo owns the insurer, chooses the investments, originates many of them, decides what they're worth, and collects a fee at every touch** ($1.44B in FY2025). Great business for Apollo. The conflict is structural: the same firm that profits from *volume* also grades its own homework on *quality*. → This is the core reason the whole thesis ("optimized for filling pipes, not credit quality") is even plausible.

**Lever 4 — funding side: institutional money (FABN).** Alongside sticky retiree annuities, raise big money fast by selling **funding-agreement-backed notes** to bond investors — borrowing dressed as insurance (see glossary). It scales fast but it's **not sticky**: it has maturity dates and must be rolled over; if markets freeze or your credit looks shaky, it must be repaid *on schedule*. → This is why we score **F4 runnability**: bad illiquid assets + patient money = slow bleed; the *same assets + runnable money = an event.*

---

## 4. Athene's actual flow, with the levers labelled

Now the picture you've seen, annotated with which lever is doing what — and the real YE2025 numbers from the dossier:

```
   Policyholders + institutions
        │  $83.4B in during 2025   ← Lever 4: $35.4B of it is funding
        │                             agreements (institutional, runnable)
        ▼
   ┌──────────────────────────────────────────┐
   │  US insurer: Athene Annuity & Life (Iowa) │   the licensed face;
   │  "AAIA" — where your contract legally sits │   sells the annuities
   └──────────────────────────────────────────┘
        │
        │  ← Lever 2: cede the economics to Bermuda
        │     $168B held as ModCo + $74B ceded outright,
        │     ALL to one affiliate:
        ▼
   ┌──────────────────────────────────────────┐
   │  Bermuda reinsurer: Athene Annuity Re     │   lighter capital + tax;
   │  "AARe" — also, oddly, AAIA's OWNER        │   where the economics pool
   └──────────────────────────────────────────┘
        │
        │  ← Lever 1: invest in private credit
        │     $321B portfolio, much of it Apollo-originated
        ▼
   ┌──────────────────────────────────────────┐
   │  Assets → real borrowers (companies,       │
   │  real estate, asset-backed deals)          │
   └──────────────────────────────────────────┘

   Alongside EVERY arrow:  Apollo (Lever 3)
   ── owns the insurer, owns the reinsurer, picks + originates the
      assets, marks them, and collects fees ($1.44B in 2025) ──
```

The "US → Bermuda → US sandwich" that confused earlier (AARe is both AAIA's *parent* and its *reinsurer*) is just Lever 2 taken to its structural conclusion: the Bermuda reinsurer isn't a sibling the US insurer *does business with* — it's been placed *above* the US insurer in the ownership chain, so ownership, dividends, and reinsurance economics all pool in the same lightly-disclosed Bermuda company.

---

## Deep dive: how a funding agreement works — debt in an insurance costume

Funding agreements are ~42% of Athene's annual inflow, so they earn their own walk-through. The one-liner: **a funding agreement is the insurer borrowing from the bond market, dressed as an insurance liability.** It raises cash, buys assets, keeps the spread — in substance, a bond issue.

### It runs the opposite way to a securitization

A **securitization** *starts* with cash-flowing assets and issues bonds against them (investors receive the assets' cash flows and bear their performance). A **funding agreement** runs the other way — raise the cash first, buy the assets after:

- **Securitization:** assets earning ~10% come *first* → issue bonds against them → investors get the asset cash flows.
- **Funding agreement:** issue the note *first* → raise cash → buy assets (~7%) → pay noteholder a *fixed* ~5% → keep the spread.

The noteholder gets a **fixed rate**, never a share of the returns — Athene keeps all the upside and bears all the losses, the opposite of a securitization's risk transfer. (Securitization *does* live here — but on the asset side: Apollo originates loans, packages them into CLOs/ABS, and Athene buys the tranches as assets.)

### The mechanics

```
Bond investors (money funds, bond funds, banks)
   │  ① buy notes (CUSIP, coupon, maturity — trades like a corporate bond)
   ▼
Athene Global Funding  (bankruptcy-remote trust)
   │  ② uses the cash to buy a funding agreement from the insurer
   ▼
Athene insurer (AAIA / Bermuda)
   │  ③ issues the funding agreement = insurance contract, fixed rate + principal
   │  ④ takes the cash, invests it in private credit
   ▼
Assets earn ~7% — the spread over the note coupon is the profit
```

### Why the insurance costume is valuable

There is **no insurance risk** in a plain funding agreement — no mortality, no contingency, a pure "pay 5% and return principal" obligation. But because a licensed insurer issues it under statutes that authorize funding agreements, the law treats it as insurance:

1. **Booked as an insurance liability, not debt** (statutory "deposit-type contracts"; GAAP "interest-sensitive contract liabilities") — why the balance sheet shows only $7.8B of "debt" against $71.4B of funding agreements.
2. **The holder gets policyholder priority** in insolvency — senior to the holding company's own bondholders — and the insurer's high rating gives the notes a strong rating and cheap funding.
3. **Capital is held under insurance rules (RBC)**, not bank/debt rules.

Bond-like economics, insurance seniority and treatment. That's the appeal — and why regulators eye it as classification arbitrage.

### Whose balance sheet is it on? (the dual ledger)

A funding agreement is **legally** always a liability of the issuing US insurer (AAIA) — only a licensed insurer can issue one. Through reinsurance its **economics** can move to AARe (Bermuda) or the ACRA sidecar (ADIP's capital). Under ModCo the liability stays *legally* on AAIA while the economics sit offshore — so "whose balance sheet?" has two answers at once. ADIP never holds it directly; ADIP investors are exposed via equity in ACRA.

| | Where a funding agreement sits |
|---|---|
| **Legal ledger** (who reports it) | AAIA — the US insurer, always |
| **Economic ledger** (who bears it) | AARe, or the ACRA sidecar (ADIP's capital), if reinsured |

### The catch — runnability (F4)

Unlike a retiree's annuity (surrender charges, tax penalties, sticky), funding agreements are **wholesale, dated, and rate-sensitive**. They have maturities and must be **rolled over** — new notes issued to repay maturing ones. If markets freeze or Athene's credit looks shaky, buyers won't roll, and Athene must repay cash *on schedule* — forcing sales of possibly-illiquid private credit into a bad market. That's the run. Not hypothetical: a Fed study documented an $18B run on life-insurer funding agreements in 2007, ~40% self-fulfilling. And it's the fastest-growing slice of Athene's funding — $35.4B issued in 2025, outstanding up from $47.4B to $71.4B in a year (21% → 26% of net reserves).

## 5. What this means for the credit work

None of the four levers is illegal or even necessarily wrong. Reinsurance, annuities, private credit, and funding agreements are all legitimate tools. The **thesis being tested** is whether pulling all four at once — under an owner that profits from volume — has quietly degraded credit quality while the disclosure that would reveal it moved offshore.

That's why the map is built the way it is:

- Lever 1 makes asset values *opinions* → we hunt mismarks (**F2**) and yield-vs-quality gaps (**F1**).
- Lever 2 moves the truth offshore → we measure how much is hidden (**F4 opacity**) and rebuild the economic ledger from treaties.
- Lever 3 means one firm grades its own homework → every number it reports is a *claim* to be checked against an independent source, never a truth.
- Lever 4 makes the funding runnable → we score how fast the money can leave (**F4 runnability**).

**The honest counter-case matters too:** a well-run PE-insurer genuinely can earn a wider spread safely — Apollo really is good at origination, and private credit really can out-yield public bonds for the same risk. The map has to be able to conclude "this group is clean" where the evidence says so. We are testing the levers, not assuming they've been abused.

---

## Glossary (the terms you'll keep hitting)

| Term | Plain meaning |
|---|---|
| **Float** | The pile of customer money the insurer holds before it has to pay it back; what gets invested. |
| **Spread** | Investment return earned *minus* interest promised to the customer. The core profit of an annuity writer. |
| **Annuity** | A savings product, not disaster insurance: give money now, get a promised rate, get it back later. |
| **Funding agreement / FABN** | Borrowing dressed as insurance: a trust sells notes to bond investors, hands the cash to the insurer, and the insurer issues an insurance contract (the funding agreement) in return. Legally an insurance liability, economically a bond. **Not sticky** — has maturities, must be rolled over. FABR (repo version) and FHLB advances are cousins. |
| **Reinsurance** | One insurer offloads risk (and reserves) to another. Normal — *unless* the reinsurer is one you own, offshore, for capital/tax efficiency. |
| **Ceding** | The act of passing business to a reinsurer. The US insurer "cedes" to Bermuda. |
| **Reserves** | The insurer's estimate of **what it owes policyholders** — a *liability*, not a stash of cash. The terminology trap: in everyday use "reserve" means money you've set aside (an asset), but insurance uses the word for the *obligation* that money is set aside to cover. The actual money held to pay it is the separate **invested assets** line. So "$271B of reserves" means "we owe policyholders $271B" — backed by ~$321B of invested assets, with the excess being the capital cushion. The central liability number. |
| **ModCo (modified coinsurance)** | A reinsurance form where the *assets stay legally on the US insurer's books* but the economics belong to the reinsurer. The single biggest reason the legal ledger and the economic ledger diverge — $168B of it at AAIA alone. |
| **Funds withheld** | Similar idea: the ceding insurer physically keeps the assets as collateral for reinsurance it has ceded. Onshore legally, offshore economically. |
| **Treaty** | The reinsurance *contract* — one legal agreement transferring a block of business from a ceding insurer to a reinsurer. The "$168B ceded offshore" is the sum of ~29 separate AAIA→AARe treaties layered over the years; each specifies the block, effective date, structure, and how money/risk split. |
| **FCR** (Financial Condition Report) | Bermuda's mandatory annual public report for a reinsurer — the offshore equivalent of a US statutory statement. The *one* public window into the Bermuda entities' capital (it's how we got AARe's EBS $30.6B vs ECR $15.2B). Filed as a *sub-group* (AARe+ALRe+ALReI combined), so it gives aggregate capital, not treaty-level detail — and the ACRA sidecars are excluded entirely. |
| **Reinsurance treaty codes** (Schedule S) | Two parts, `STRUCTURE / BUSINESS`. Structure: **CO** = straight coinsurance (assets + reserves move to reinsurer), **MCO** = modified coinsurance (assets + reserves stay on the cedent's books, economics passed over), **COFW** = coinsurance with funds withheld (reinsurer assumes reserves; cedent physically holds the assets as collateral). Business: **/I** = individual (retail), **/G** = group (institutional). Separate reserve-type tag: **IA** individual annuities, **FA** funding agreements/deposit-type, **VA** variable annuities, **OA/OL** other. So `MCO/I · FA` = ModCo treaty, individual business, funding-agreement reserves. |
| **ModCo vs COFW — the difference** | Both keep the assets physically at the US cedent while moving the economics offshore; the difference is where the *reserve* legally sits. **ModCo:** reserve *and* assets both stay on the cedent's books; the reinsurer's economics arrive via a periodic ModCo settlement ("I keep everything and settle up with you"). **COFW:** the reserve legally *moves* to the reinsurer — so the cedent takes a bigger US reserve credit — but the cedent physically *withholds* the assets as collateral, which the reinsurer carries as a funds-withheld receivable ("you've taken the liability, I'm keeping the money and owe it to you"). Both are dual-ledger (assets onshore, risk offshore), so both feed opacity equally. **Observable tell** in Schedule S: ModCo fills the *ModCo-reserve* column; COFW fills the *reserve-credit-taken + funds-withheld* columns. Athene's 2018–early-2024 blocks are ModCo; the big July-2024 block switched to COFW under the reciprocal-jurisdiction regime — a fingerprint of when each block was ceded and which regime was in force. |
| **Private credit** | Loans and credit assets not traded on public markets — no market price, so value is an estimate. Athene's asset engine, Apollo-originated. |
| **Statutory (SAP) vs GAAP** | Two accounting languages: SAP is what US insurers file with state regulators (conservative, entity-level); GAAP is the investor-facing consolidated version. They don't tie exactly — different rules, different perimeters. |
| **ACRA** (Athene Co-Invest Reinsurance Affiliate) | Bermuda sidecar reinsurers that reinsure a slice (historically ~a third) of every new deal Athene writes. Owned *jointly* by Athene and outside investors, so the economics of that slice are shared. Several vintages (1A/1B, 2A/2B). |
| **ADIP** (Apollo/Athene Dedicated Investment Program) | The Apollo-managed fund that raises capital from big institutions (sovereign funds, pensions) and invests it as **equity** into ACRA, alongside Athene's own. These investors share the reinsurance profit *and* losses — **no guaranteed return** — and appear on Athene's balance sheet as noncontrolling interests (~$15B). Apollo earns fees + carry on this outside capital. Because equity is a thin layer under a much larger asset book, each dollar of ADIP equity supports a *multiple* of itself in reinsured business (leverage) — growing Apollo's fee-earning AUM, and serving as the first, thin cushion before credit losses reach policyholders. |
| **Noncontrolling interests (NCI)** | The equity-accounting line for outside investors' stakes in consolidated subsidiaries — here, mostly ADIP investors' equity in ACRA (~$15.1B). An *equity* line, so it absorbs losses; not to be confused with the policyholder *liabilities* it helps back. |
| **Bermuda / BMA** | Bermuda Monetary Authority — the offshore regulator with lighter capital rules and less public disclosure than US states. Where AARe reports. |
| **TAC** (Total Adjusted Capital) | US measure of *what capital you have*: statutory capital & surplus plus prescribed add-backs (e.g., the asset valuation reserve). Compared against the RBC thresholds. AAIA: $9.5B. |
| **RBC ladder — ACL / CAL** | The US required-capital system, a ladder of trigger points. **ACL** (Authorized Control Level) = the level at which the regulator *may seize control*. **CAL** (Company Action Level) = 2× ACL, the first tripwire (insurer must file a corrective plan); below sit RAL (1.5×) and MCL (0.7×, mandatory seizure). RBC ratios get quoted against either denominator — 871% of ACL is the same balance sheet as 436% of CAL. Always check which. |
| **ECR / MMS / BSCR / TCL** | Bermuda's required-capital vocabulary. **BSCR** = the risk model (factor charges on assets/liabilities — Bermuda's RBC). **ECR** (Enhanced Capital Requirement) = the required-capital number it produces. **MMS** = a crude minimum floor. **TCL** = 120% of ECR, the "comfortably above" target. "ECR-binding" means ECR > MMS, so ECR is the constraint that matters. |
| **NAIC designation** | The regulatory credit-quality grade (1–6) on every bond a US insurer holds: 1 ≈ AAA→A−, 2 ≈ BBB range, 3–6 = below investment grade down to default. Letter modifiers are exact agency-rating equivalents: 1.A=AAA, 1.B=AA+, 1.C=AA, 1.D=AA−, 1.E=A+, 1.F=A, 1.G=A− · 2.A=BBB+, 2.B=BBB, 2.C=BBB− · 3.A/B/C=BB+/BB/BB− · 4.A/B/C=B+/B/B− · 5.A/B/C=CCC+/CCC/CCC− · 6=default-adjacent. Crucially, the designation **sets the RBC capital charge** — higher designation = less capital required — which builds in the incentive to obtain the best designation defensible ("ratings shopping"). AAIA's bond book: 59.3% NAIC-1, 37.8% NAIC-2, 2.9% below-IG. |
| **SVO / SVO symbol** | The Securities Valuation Office is the NAIC's in-house securities-analysis unit; the symbol on each bond row records *where its designation came from* — the credibility axis. **FE** (filing exempt) = derived from a public agency rating, market-disciplined (49.3% of AAIA's book). **PL** = derived from a *private letter* rating, unpublished, no market check — the channel the NAIC found inflated up to six notches (25.3%). **Z/YE** = insurer self-assigned pending SVO review (~7%). **FM** = financially modeled structured paper. The designation says "how safe"; the symbol says "who says so." |
| **Bermuda Class E / Class C** | BMA license tiers for long-term insurers, roughly by size. **Class E** = the top commercial tier (assets >$500M): AARe, ALRe. **Class C** = a smaller/lower tier — yet the multi-billion ACRA sidecars sit there; why is an open item, logged not guessed. |
| **Holding age / seasoning** | Holding age = how long a bond has been on *this insurer's* books (Schedule D's "date acquired"). **Seasoned** = held long enough to have a track record: payments made, marks moved, ratings migrated. AAIA's book: 54% bought within the last 12 months — long-dated paper, almost none of it seasoned. Trap: "acquired" resets when an affiliate transfers the bond, so *young* can mean "recently moved," not "recently made." |
| **Maturity ladder** | The book laid out by *when the money actually comes back*. AAIA's ladder is long: 70% repays beyond 10 years, ~1% inside a year — so cash for surrenders and rollovers must come from selling assets or from new inflows, not from bonds maturing on their own. |
| **Issuer prefix (CUSIP6)** | The first 6 characters of a CUSIP or PPN identify the *issuer*; the last 3 identify the specific security. Grouping by prefix gives issuer-level concentration without needing to read names — but it's a **floor**: one corporate family can issue under many prefixes (AMAPS 1 and AMAPS 2 are separate prefixes, same family). Resolving prefixes into families is entity-resolution work (the D4 engine). |
| **ROE / cost-of-equity hurdle** | Return on equity = profit available to the owner ÷ the owner's capital at risk. It only means something against a **hurdle**: the return investors could demand elsewhere for similar risk (~10–12% for a levered spread balance sheet). ROE above hurdle = the business creates value; the analytical question is always *which inputs manufacture the excess* — numerator (are losses fully counted?) or denominator (is required capital genuinely that small?). |
| **AOCI** (accumulated other comprehensive income) | The equity line where unrealized bond marks park without touching profit. Rates up → bond prices down → AOCI goes negative (a "hole" in equity) without any loss being *recognized*. AHL's hole: −$5.5B → −$2.6B over 2025, which flattered equity growth. "Ex-AOCI" ROE strips this noise — and is also the honest denominator, since the hole is real money if assets ever must be sold. |
| **NCI / ADIP's realized return** | The sidecar investors' actual earned return: their profit share ÷ their equity. It is the closest thing to a *market price for bearing this exact risk pool* — sophisticated LPs accepted ~12% — which makes it a live benchmark for what the risk is worth. |

---

*Companion to `spec/credit-map-spec.md`. The findings F1–F4 referenced here are defined in spec §1.1.*

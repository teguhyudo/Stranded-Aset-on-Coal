# Editorial Review: "Stranded Coal and Bank Fragility: Evidence from Indonesia"

**Reviewer role:** Senior Editor, field journal in Environmental and Resource Economics
**Review date:** March 2026
**Manuscript status:** Major Revision Required

---

## Summary Judgment

This manuscript tackles a genuinely important and timely question: how does coal stranded asset risk propagate through Indonesia's banking sector? The topic is policy-relevant and the data construction effort is commendable — particularly the bipartite bank-coal exposure network built from hand-collected annual report disclosures. Indonesia is a well-chosen case: as the world's largest thermal coal exporter, it offers a high-stakes test of the coal-banking nexus that has broader applicability to other commodity-dependent emerging economies.

Despite these strengths, I cannot recommend acceptance in the current form. The manuscript has several interconnected problems: (1) **critical internal inconsistencies** in key data, (2) a promised "sovereign nexus" that is never formally analyzed, (3) **reference list errors** of a kind that will concern reviewers, (4) methodological weaknesses that are not adequately acknowledged, and (5) the absence of a formal theoretical framework expected at top field journals. The paper is closest to publishable at a strong applied journal (e.g., *Energy Economics*, *Journal of Environmental Economics and Management*, *World Development*) if these issues are addressed. For the most selective journals in the field, a more substantial theoretical contribution is needed.

The authors should treat this as a **major revision**. The core empirical contribution is solid and worth developing. What follows is a detailed account of what must be fixed.

---

## I. Critical Internal Inconsistencies — Must Resolve Before Resubmission

### 1.1 The BYAN Cost Data Contradiction

This is the most serious problem in the paper and must be resolved before the manuscript can proceed. There is a direct, irreconcilable contradiction between the main text and the appendix results table regarding Bayan Resources (BYAN).

- **Main text (Section 5.1):** "Breakeven costs... range from under $22 per tonne for ADRO's low-cost Kalimantan operations to over $192 per tonne for BYAN's higher-grade deposits."
- **Main text (Section 5.2):** "Low-cost producers like BUMI ($21.9/t) and BYAN ($51.6/t) retain positive NPV under 2°C but face substantial value erosion under 1.5°C."
- **Appendix C (Table A-C1):** BYAN breakeven = **$230.9/t**, NPV_BAU = **−$7,173M** (already negative under BAU), classified as the 8th-largest stranded value company.

These are not rounding errors or minor discrepancies. The main text says BYAN is among the *lowest-cost* producers at $51.6/t; the appendix table says it is the *most expensive* producer in the sample at $230.9/t with an already-unviable operation under BAU. These cannot both be true.

BYAN's market capitalisation of approximately $31 billion — described in the paper as the largest in the coal sector — is utterly inconsistent with an operation already generating a negative $7 billion NPV under business-as-usual. Either the cost calculation for BYAN is wrong (likely an issue with the cost_of_revenue/production_volume calculation given that BYAN's revenue includes substantial freight and logistics that inflate the per-unit cost denominator, or a currency scaling error), or the main text was not updated after the model was revised.

**Additional inconsistency in cost ranges:** Section 5.1 states that breakeven costs range from $21.9/t (BUMI) to $151.1/t (HRUM). But the appendix table shows HRUM at $87.5/t and BYAN at $230.9/t. The stated range endpoints contradict the table.

**Required action:** The authors must audit the cost data and model outputs for BYAN and re-examine where these discrepancies arise. The main text must be reconciled with the appendix tables. Given BYAN's prominence (largest market cap, cited extensively), any error here affects the credibility of the entire empirical contribution.

### 1.2 Equation Inconsistency: Main Text vs. Appendix NPV Formula

The main text NPV formula (Equation 2) includes a tax term:

$$NPV_i^s = \sum_{t=1}^{T_i} \frac{Q_{i,t}^s \cdot (P_t^s - C_{i,t}) - \tau \cdot \max(0, Q_{i,t}^s \cdot P_t^s - C_{i,t} \cdot Q_{i,t}^s)}{(1 + r_i^s)^t}$$

The appendix formula (Eq. B.1) simplifies this to:

$$\text{NPV}_{i,s} = \sum_{t=1}^{T_i} \frac{(P_{s,t} - C_i) \cdot Q_i \cdot (1 - \tau)}{(1 + r_i)^t}$$

These are algebraically equivalent when $P > C$, but the appendix version also removes the time subscripts on $Q$ and $C$ (the appendix holds both constant), the scenario subscript on the WACC $r_i$, and the $\max(0,\cdot)$ term. These simplifications are meaningful: the main text implies time-varying production and costs (with 2% annual cost inflation referenced) and scenario-specific discount rates, while the appendix implements a flat model. The authors need to specify clearly which version was actually computed. If costs are indeed constant (as in the appendix), the 2% cost inflation mentioned in Section 5.2 was not implemented.

---

## II. Narrative and Framing

### 2.1 The Missing Sovereign Nexus

The paper's central framing — the **"coal-banking-sovereign nexus"** — is compelling and potentially its most important intellectual contribution. Yet it is not delivered. The sovereign dimension is described qualitatively in Section 3.3 (fiscal dependence on coal revenue), mentioned in the policy implications, and detailed mechanically in Appendix B, but **there are no results for the sovereign channel in the main text**. The macro-transmission model (Model 3 in the appendix) appears to have been dropped from the main text, leaving the paper's title promise unfulfilled.

The authors face a choice:
- **Option A (Preferred):** Restore the sovereign channel results, showing the feedback loop: coal stranding → bank credit losses → potential sovereign-bank feedback. This is the paper's most original contribution and what distinguishes it from other stranded asset studies. The Appendix B formulae for the fiscal, credit, and market channels are already written.
- **Option B (Alternative):** Narrow the framing to the "coal-banking nexus," removing the "sovereign" from the title, framing, and key claims. This is a weaker contribution but an honest one.

The current hybrid — promising a sovereign nexus but not delivering it — is the worst of both worlds.

### 2.2 The "Overvaluation" Claim Requires More Careful Treatment

Section 5.3.4 states that Indonesian coal equities "appear substantially overvalued" by approximately 61% relative to climate-adjusted fair value. This is a strong market efficiency claim that the methodology does not fully support.

The aggregate market capitalisation ($116B) reflects near-term earnings expectations, option value, diversification beyond coal (several companies are diversified), and market participants' own probability assessments. The "overvaluation" framing implicitly assumes that the authors' scenario probabilities (30/40/30) are correct and that markets should price on this basis. This is not established. A more defensible framing is: "under the assumption that climate scenarios are priced with these weights, our estimated stranded values would imply a substantial discount to current market values." The stronger market-efficiency claim requires either a Fama-French style regression showing coal companies do not earn a climate risk premium (as Bolton & Kacperczyk find for US markets) or more modest language.

---

## III. Methodology

### 3.1 The Domestic Market Obligation (DMO) Omission

The paper provides an excellent description of Indonesia's DMO in Section 3.1 — requiring producers to sell 25% of output domestically at a capped price of $70/tonne — yet this price floor is **not incorporated in the NPV model**. This is a material omission.

Under the 1.5°C scenario, with export prices of $70/tonne at 2030 and $15/tonne by 2050, the domestic DMO price ($70/tonne) would *exceed* the scenario export price after 2030. For companies with substantial domestic sales, this creates a mixed-price revenue stream that is significantly more favourable than the scenario export price alone. The NPV formula applies a single price path to all production, which overstates stranded values for firms with high domestic market shares.

More importantly, the DMO creates a policy-contingent floor that would be itself under political pressure in a serious climate transition — the government would face a stark fiscal-industrial trade-off between maintaining the DMO (propping up uneconomic mines) and meeting climate commitments. This is precisely the coal-banking-sovereign nexus the paper purports to study. The omission is both a modelling gap and a missed opportunity.

**Required action:** Either incorporate DMO pricing for the domestic portion of output (using disclosed domestic sales shares where available) or provide a sensitivity analysis showing the impact of a DMO price floor on aggregate stranded values. This analysis would also enrich the policy discussion.

### 3.2 Uniform Mine Life Assumption

All firms receive a default mine life of $T_i = 20$ years, corresponding to the standard IUP concession duration. The paper acknowledges that JORC-compliant reserve data are unavailable, which is a genuine limitation. However, the sensitivity of results to mine life is understated. The tornado analysis (Figure 10) is the correct place for this, but mine life should appear as one of the highest-sensitivity parameters in a correctly-specified model — it enters linearly in the DCF summation.

Consider: a firm with $T = 20$ versus $T = 10$ has NPVs that differ by roughly 40-50% at standard discount rates (the difference in annuity factors for 10 vs 20 years at 10% WACC is approximately (6.14 − 3.79)/6.14 = 38%). For stranded values, which are NPV differences, this uncertainty is propagated fully. Given the heterogeneity in Indonesian coal concessions (some firms have been producing for decades with limited remaining reserves; others have decades of production ahead), this uniform assumption introduces substantial and unacknowledged cross-sectional bias.

**Required action:** Conduct a robustness check using alternative mine life assumptions (10, 15, 25 years) and discuss the results. Where annual reports disclose remaining IUP terms or reserve life indices, use these. Report mine life uncertainty explicitly in the tornado diagram.

### 3.3 Default Classification: NPV < 0 is Not Default

The classification of coal companies as "default" when NPV < 0 conflates economic non-viability of new production with inability to service existing debt. A firm can have a negative forward-looking NPV but still generate sufficient cash flow from existing operations to meet near-term debt obligations, particularly when:
- Existing debt is long-dated (maturity in 5-10 years)
- The firm holds substantial cash reserves (several companies in the sample have cash-to-debt ratios above 0.5)
- The firm can restructure operations (reduce output, sell assets)

Standard credit risk frameworks (Merton model, KMV) derive default probability from the relationship between asset value and debt face value, not from the sign of the forward-looking operational NPV. The paper's approach is a reasonable simplification for a stress test, but the authors should: (i) acknowledge this limitation more prominently, (ii) show that results are qualitatively robust to an alternative specification that incorporates the firm's current liquidity position (e.g., classifying as "default" only firms with NPV < 0 **and** cash/debt below a threshold), and (iii) note that for event-horizon purposes, a 5-year rather than full-mine-life NPV might be more appropriate for bank credit risk estimation.

### 3.4 The LGD for Distressed Firms is Ad Hoc

The formula LGD = 0.30 × (SV/A) for distressed firms lacks theoretical justification. The 30% multiplier is not standard in any credit risk framework (the Basel Foundation IRB LGD for senior unsecured corporate is 45%; for secured corporate it is 25-40%). The scaling by SV/A is not standard practice and could produce LGD > 1 for firms where SV > A (which the paper reports for several firms, e.g., GEMS at 395% of assets under 2°C). No cap appears to be imposed in the formula as written.

**Required action:** Justify the 30% multiplier with reference to Indonesian banking practice or calibration from comparable default episodes (e.g., the 2015-2016 coal downturn). Consider using Basel standard LGDs (45% unsecured, 25% secured) instead, since the paper doesn't have empirical LGD data. The distressed LGD should also be capped at 45%.

### 3.5 Static RWA Assumption Biases CAR Impact Downward

The CAR calculation holds RWA constant at its pre-stress level. This underestimates the CAR impact for two reasons. First, defaulted and distressed loans migrate to higher Basel risk weight categories (150% for defaulted exposures), which increases RWA. Second, provisioning requirements for newly identified NPLs reduce CET1 capital directly. The paper's conservative framing (calling this an "upper bound" due to the absence of CKPN offset) is misleading — it is simultaneously an upper bound on loss (by ignoring CKPN absorption) and a lower bound on CAR impact (by ignoring RWA migration). These offsetting biases make the net direction unclear and should be acknowledged.

### 3.6 Indirect Loss NPL Shocks Are Unjustified

The scenario-dependent NPL shocks applied to residual mining loans (0.5%, 5%, 15% for BAU, 2°C, 1.5°C) are described only as "calibrated to the share of stranded firms in the sector." The derivation is not provided and the 15 percentage point NPL shock for 1.5°C is extremely large — it would be unprecedented in Indonesian banking history (sector-wide mining NPLs peaked at 7.7% during the severe 2015-2016 coal price downturn). If this shock is applied to the residual mining portfolio (which includes nickel, gold, etc. — not just coal), it is clearly excessive and will substantially overstate indirect losses. The sensitivity analysis in Section 8.4 only varies the generic LGD, not these NPL shocks.

**Required action:** Either derive the NPL shocks more rigorously from the fraction of the broader mining portfolio that is coal-exposed and the severity of the scenario price decline, or drop the indirect loss component and acknowledge this as a conservative lower bound. At minimum, include NPL shock variation in the robustness analysis.

### 3.7 Network Clustering Coefficient: Specification Required

Section 6.4 reports a bipartite network clustering coefficient of 0.68. The standard clustering coefficient is defined for unipartite networks. For bipartite networks, multiple competing measures exist (Opsahl 2009, Latapy et al. 2008, Zhang et al. 2008), and they can give substantially different values for the same network. The paper does not specify which measure is used. The comparison to "0.35 in a randomly wired network" needs to specify the null model (Erdős–Rényi with same density? Configuration model preserving degree sequence?). Without these specifications, the clustering comparison is not interpretable.

---

## IV. Reference List Audit

I have conducted a careful check of the reference list. Several entries have errors that must be corrected before resubmission.

### Critical Errors

**1. Missing references cited in the main text.** Three papers cited in Section 2 do not appear in the bibliography:

- **Tong et al. (2021):** Cited for the claim that existing coal plants would exhaust the 1.5°C budget. The closest real paper is Tong et al. (2019), *Nature* 572:373–377 ("Committed emissions from existing energy infrastructure jeopardize 1.5°C climate target"). If the authors mean the 2019 paper, the year is wrong. If there is a 2021 follow-up, it should be cited with full details.
- **Cui et al. (2021):** Cited for a mine-level global coal supply curve identifying Southeast Asian coal as cost-disadvantaged. This may be Cui et al. (2021), *iScience* ("A plant-by-plant strategy for high-ambition coal power phaseout in China"), or another paper. The exact citation must be provided with journal, volume, and pages.
- **Battiston et al. (2021):** Cited for extending systemic risk analysis to climate policy-relevant contexts. Battiston has many papers; a 2021 paper on climate systemic risk exists but must be cited precisely.

These missing references suggest the literature review was not fully reconciled with the bibliography. Journal editors and reviewers will notice this immediately.

**2. Year mismatch: `Burke2023`** The BibTeX key is `Burke2023` but the entry has `year = {2018}` and the correct paper (Burke & Kurniawati, *Energy Policy* 116, 2018) was published in 2018, not 2023. The text cites this as \citet{Burke2023} to support claims about Indonesia's "energy policy landscape" in Section 2.3 — but the actual paper is about *electricity subsidy reform* and is from 2018. Both the citation key and the description of the paper in the text appear to be errors.

**3. Year mismatch: `Adrian2019`** Key says 2019 but entry has `year = {2016}`, `volume = {106}` in *AER*. The "CoVaR" paper by Adrian & Brunnermeier was published in *AER* 2016. Use `year = {2016}`.

**4. Year mismatch: `Acharya2017`** Key says 2017 but entry has `year = {2015}` and journal is *Journal of Financial Economics* 115(2). The actual paper "The 'Greatest' Carry Trade Ever?" by Acharya & Steffen is from 2015. The citation key should be `Acharya2015`. More substantively, this paper is about the Eurozone sovereign-bank nexus (banks loading up on domestic sovereign bonds), not about resource dependence or commodity exporters. Citing it as a reference for the "sovereign-bank nexus in resource-dependent economies" misrepresents the paper's contribution.

**5. `CarbonTracker2022` is misdated.** The landmark Carbon Tracker "Unburnable Carbon" report by James Leaton was published in **2011–2013**, not 2022. Carbon Tracker did publish documents in 2022, but the foundational "Unburnable Carbon" framing report that is cited for the "carbon bubble" thesis is from 2011/2012 (Leaton, J., *Unburnable Carbon: Are the World's Financial Markets Carrying a Carbon Bubble?*, Carbon Tracker Initiative, 2012). The 2022 date is incorrect for the document being described. This should be corrected to the appropriate year, or replaced with a specific 2022 Carbon Tracker publication that is actually being referenced.

**6. `sonny2016` is an unpublished manuscript.** The entry reads `note = {Manuscript}`. Citing an unpublished manuscript as a primary comparator for the paper's estimates (referred to repeatedly in Sections 2 and 8) weakens the contribution. If this is a working paper, it should be cited as such with an institutional affiliation and URL. If it has since been published, provide the journal reference. Reviewers will ask whether the findings are reproducible.

### Minor Errors

- **`IMF2025IndonesiaStress`:** No report number given. IMF Country Reports carry report numbers; this should be added if available, or the citation should note it is "forthcoming" if the report was not yet published at the time of writing.
- **`GennaiGoldin2014`:** The BibTeX key garbles the author name. The actual authors are Gennaioli, Martin & Rossi (2014), *Journal of Finance*. The key should be `Gennaioli2014` or similar. This key does not appear to be cited in the main text; if the paper is not used, remove it from the bibliography.
- **`Brunnermeier2014`:** "Predatory Short Selling" (Brunnermeier & Oehmke, *Review of Finance*, 2014) is about short selling markets and appears to have no connection to the content of this paper. If it is not cited in the text, remove it. If it is cited, the relevance must be explained.
- **`Sims1980` and `Lutkepohl2005`:** These are VAR and time series references that do not appear in the main text (they were apparently part of the removed Model 3 macro section). If they are not cited in the text, remove them from the bibliography.
- **`BoE2019`:** Cited as "The 2021 Biennial Exploratory Scenario" published in 2019 — a 2019 discussion paper about a 2021 scenario. The Bank of England's Climate Biennial Exploratory Scenario (CBES) final results were published in 2022. The citation should be clarified: either cite the 2019 discussion paper announcing the scenario design, or the 2022 results report — not both under the same key with inconsistent dates.

---

## V. Theoretical Framework

The paper is fundamentally empirical and applied, which is a legitimate mode for this field. However, the absence of any formal theoretical underpinning is a weakness for selective journals, and it affects the paper's contribution in two ways.

### 5.1 Why Don't Banks Already Price Transition Risk?

The entire policy case rests on the implicit claim that Indonesian banks are underpricing coal transition risk. But the paper never explains *why*. This is not a trivial question. Rational banks with access to NGFS scenarios and IEA projections should already be incorporating some probability of coal price declines into their loan pricing. Possible explanations include:

- **Short-termism / horizon mismatch:** Bank loan officers optimise over 3-5 year horizons; stranding occurs over 20+ years. This connects to Carney's "tragedy of the horizon" but is never formalized.
- **Implicit sovereign guarantees:** Indonesian coal miners, particularly state-owned PTBA, may benefit from implicit government support that reduces the effective PD from banks' perspective.
- **Information asymmetries:** Banks may lack the technical tools to assess coal stranding risk — precisely the gap this paper fills. But if so, the policy recommendation should focus on disclosure and capacity building, not capital add-ons.
- **Regulatory forbearance incentives:** Indonesian banks may have experienced that supervisors tolerate NPL deterioration in systemically important sectors.

Without addressing this question, the paper documents a risk but cannot explain whether it is priced or underpriced. At minimum, a discussion paragraph comparing Indonesian coal loan spreads to climate-aware benchmarks (e.g., international coal bonds) would strengthen the case.

### 5.2 Scenario Probability Weights Are Unjustified

The expected stranded value is computed using subjective probability weights ($\pi_{BAU} = 0.30$, $\pi_{2C} = 0.40$, $\pi_{1.5C} = 0.30$) described as "the authors' assessment." This is not a defensible scientific basis for computing a single-number expected value that drives major policy recommendations. The weights should either be: (i) derived from a formal model (e.g., a calibrated integrated assessment model probability distribution), (ii) explicitly extracted from prediction markets or expert elicitation surveys with citations, or (iii) treated purely as scenario parameters with the expected value presented as a sensitivity table. The current framing gives the probability-weighted estimate an unearned precision. The tornado analysis shows that scenario weights have "the smallest variation" among parameters — but this depends on the weights themselves, and if markets assign 80%+ probability to BAU, the expected stranded value is far smaller.

---

## VI. Specific Suggestions for Improvement

The following suggestions are within scope for the revision and would meaningfully strengthen the paper:

1. **Restore or drop Model 3.** Appendix B already contains the full derivation of the fiscal, credit, and market channels. Adding even a minimal results section showing the GDP impact decomposition across scenarios would deliver on the "sovereign nexus" promise and produce a substantially stronger paper. If the results look implausible (as sometimes happens when macro multipliers are applied additively), that is itself a finding worth discussing.

2. **Incorporate the DMO price floor.** Even a simple sensitivity analysis showing stranded values with and without the DMO cap applied to 25% of domestic production would address a real limitation and add to the policy discussion on the DMO's role in the coal transition.

3. **Add a time-to-distress analysis.** Rather than asking "what are losses at the NPV horizon?", ask "under what coal price trajectory does each bank's coal portfolio first breach a NPL threshold?" This dynamic question is more policy-relevant and can be answered with the existing data and a simple simulation over the price path interpolation function.

4. **Table comparison (Tab. 8) needs expanding.** The comparison table with prior studies is useful but should include the methodology column for all comparators (what data, what cost approach, what coverage) and distinguish between stranded reserve value (physical), stranded equity value (financial), and stranded banking exposure. The comparison between the authors' $79.7B (2°C) and Rishanty's $35B investor risk figure is currently explained in prose; a structured table column comparing methodological scope would be more informative.

5. **The supply cost curve should account for calorific value.** Indonesian coal spans 4,000–6,000 kcal/kg. When constructing the supply curve, breakeven prices should be normalised to a standard calorific value (e.g., 6,000 kcal GAR, the Newcastle benchmark) to make firms comparable. A low-grade sub-bituminous producer at $50/tonne may be more or less viable than a high-grade bituminous producer at $80/tonne, depending on the calorific premium. The current curve arrays all producers on a per-tonne basis, which is not economically equivalent.

6. **Network analysis needs strengthening.** The bipartite network is the paper's most distinctive methodological contribution, but the analysis is thin: essentially a descriptive measure (clustering coefficient) and a visualisation. At minimum, compute the bipartite network's robustness to targeted removal of the highest-degree coal companies (a standard network resilience measure). This would quantify how much of the banking system's coal exposure is idiosyncratic to a few large borrowers versus distributed across many.

---

## VII. Minor Issues

- **Section title 2.1** reads "Stranded Assets on Carbon" — presumably should be "Stranded Carbon Assets" or "The Stranded Assets Literature."
- **Section 3 → Appendix B cross-reference mismatch:** Appendix B opens "This appendix provides full derivations and parameter specifications for the three models presented in Sections~\ref{sec:model1}--\ref{sec:model3}" — but Model 3 is not in the main text. The cross-reference will generate a LaTeX warning and confuse readers.
- **Redundancy between Sections 5.3.4 and 8.4:** The discussion of the probability-weighted expected stranded value and its market valuation implications appears substantively in both the Model 1 results (5.3.4) and the Policy Implications section (8). This should be consolidated.
- **JETP section (3.4):** The description of JETP as "announced at COP27" is correct but it was first announced at COP26 in Glasgow (November 2021) and formalised at COP27. The chronology should be precise.
- **Bibtex formatting:** `CarbonTracker2022` is formatted as `@article` but is a report (`note = {Carbon Tracker Initiative Report}`). Use `@techreport`.
- **The paper cites \citet{Daumas2024}** as a "comprehensive survey" finding that "empirical evidence grounded in actual firm-level data remains scarce, particularly for emerging markets." This accurately characterises the gap the paper fills and is one of the stronger motivating citations.

---

## VIII. Overall Recommendation

**Decision: Major Revision**

The paper addresses a genuine and important gap in the literature. The core contributions — the bipartite bank-coal exposure network and the bottom-up stress test — are original and policy-relevant. The writing is generally clear and professional.

However, the paper cannot be accepted without addressing the BYAN data inconsistency (which affects the credibility of the key empirical results), the missing and erroneous references (which will be caught immediately by specialist reviewers), and the incomplete delivery on the sovereign nexus promise. The methodological issues (DMO omission, default classification, LGD specification, mine life uniformity) are significant but individually addressable.

If the authors can resolve these issues in revision, the paper has a realistic path to publication at a strong applied journal in environmental economics or energy economics. For the top theoretical journals in the field, a more formal analytical framework showing why climate risk is mispriced in Indonesian coal lending markets would be necessary to clear the bar.

I look forward to reviewing a revised manuscript.

---

## Summary of Required Actions (Priority Order)

| Priority | Issue | Location |
|----------|-------|----------|
| **Critical** | Resolve BYAN cost data contradiction (main text vs. appendix table) | Sec. 5, App. C |
| **Critical** | Add missing references: Tong2021, Cui2021, Battiston2021 | Bib |
| **Critical** | Fix year mismatches: Burke2023/2018, Adrian2019/2016, Acharya2017/2015, CarbonTracker2022 | Bib |
| **Critical** | Deliver or drop Model 3 sovereign results | Sec. 7 / App. B |
| **High** | Incorporate DMO price floor in NPV model or sensitivity analysis | Sec. 5 |
| **High** | Justify or revise indirect loss NPL shocks (esp. 15% for 1.5°C) | Sec. 6.2 |
| **High** | Address mine life uniformity with sensitivity analysis | Sec. 5 |
| **High** | Clarify bipartite clustering coefficient specification | Sec. 6.4 |
| **High** | Justify LGD for distressed firms; add cap | Eq. 3 |
| **Medium** | Clarify NPV equation: flat vs. growing costs; scenario-specific WACC | Eq. 2 |
| **Medium** | Moderate the "overvaluation" claim | Sec. 5.3.4 |
| **Medium** | Explain why banks do not already price transition risk | Sec. 2/8 |
| **Medium** | Add calorific-value normalisation to supply cost curve | Sec. 5.1 |
| **Low** | Fix section title 2.1; consolidate redundant material in 5.3.4/8 | Throughout |
| **Low** | Remove unused bib entries (Sims1980, Lutkepohl2005, Brunnermeier2014, GennaiGoldin2014) | Bib |

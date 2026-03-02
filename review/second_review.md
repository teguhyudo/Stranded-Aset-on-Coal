# Second Review: "Stranded Coal and Bank Fragility: Evidence from Indonesia"

**Reviewer role:** Senior Editor, field journal in Environmental and Resource Economics
**Review date:** March 2026
**Manuscript status:** Second review following Major Revision
**Decision:** Minor Revision (Conditional Accept)

---

## Summary Judgment

I thank the authors for a thorough and responsive revision. The manuscript has improved substantially. The critical internal inconsistencies that marred the first submission --- the BYAN cost data contradiction, the equation mismatch between main text and appendix, the missing references --- have been resolved. Model 3 (macro-financial transmission) has been restored to the main text, delivering on the "coal-banking-sovereign nexus" promise that is the paper's most distinctive framing. The robustness analysis has been significantly expanded, including mine life sensitivity, DMO price floor analysis, alternative default classification, NPL shock variation, and network targeted removal. These additions meaningfully strengthen the empirical contribution.

The paper is now close to publishable. What follows are the remaining issues that must be addressed before acceptance, organised by priority.

---

## I. Issues Resolved from First Review

I confirm that the following critical and high-priority issues from the first review have been adequately addressed:

| Issue | Status | Assessment |
|-------|--------|------------|
| BYAN cost data contradiction | **Resolved** | Annual report costs used consistently ($51.0/t). Appendix C regenerated. |
| NPV equation mismatch (Eq 2 vs Appendix B.1) | **Resolved** | Both now show identical specification: constant costs, 2% production decline, single WACC. |
| Missing references (Tong, Cui, Battiston) | **Resolved** | All three now properly cited with correct years (2019, 2019, 2021). |
| Year mismatches (Burke, Adrian, Acharya, CarbonTracker) | **Resolved** | All corrected. CarbonTracker now dated 2012. |
| Model 3 sovereign nexus results missing | **Resolved** | Section 7 now in main text with full channel decomposition. Major improvement. |
| DMO price floor omission | **Resolved** | Sensitivity analysis in Sec 8.4 (2.7--7.4% SV reduction). Discussed as policy buffer. |
| Mine life uniformity | **Resolved** | T = {10, 15, 20, 25} sensitivity in Table 9, Panel B. |
| Default classification caveat | **Resolved** | Merton model discussion added; alternative dual-criterion tested (NPV < 0 AND cash/debt < 0.5). |
| NPL shock justification | **Resolved** | Historical comparison (7.7% peak) and sensitivity analysis (0% to 15%) included. |
| Clustering coefficient specification | **Resolved** | Now references Roncoroni (2021) methodology with configuration model null. |
| Overvaluation claim | **Resolved** | Reframed as conditional on scenario weights and methodology. Much more defensible. |
| Section 2.1 title | **Resolved** | Now "The Stranded Assets Literature." |
| JETP chronology | **Resolved** | COP26 announcement, COP27 formalisation. |
| Sonny (2016) status | **Resolved** | Now cited as working paper with institutional affiliation. |

The quality of the data audit is evident. The ADRO exclusion (reclassified as metallurgical coal holding company post-2024 restructuring) is well-justified and properly footnoted. The HRUM limitation ($235/t includes nickel COGS) is transparently flagged. These are exactly the kinds of data quality decisions that build reviewer confidence.

---

## II. Remaining Issues Requiring Attention

### 2.1 ABMM Anomalous Breakeven: $2,244.9/t (Medium Priority)

Appendix C (Table A-C1) reports ABMM with a breakeven of $2,244.9/t and a BAU NPV of -$6,291M. This is an obvious data quality issue --- no thermal coal producer has an all-in cost exceeding $2,000/t. The firm produces only 0.66 Mt and contributes negligibly to aggregate results ($101.7M SV under 2C, or 0.17% of the total). However, having resolved the BYAN data issue so carefully, leaving an equally anomalous cost figure unexplained risks the same kind of internal credibility problem.

**Required action:** Either (a) investigate and correct the cost figure (likely a reporting scale error --- if ABMM reports COGS in IDR thousands while the code expects IDR millions, the cost would inflate by ~1,000x), or (b) exclude ABMM from the NPV sample (reducing to 25 firms) with a footnote explaining the data quality exclusion, analogous to the ADRO treatment. Given the negligible production share, exclusion is the cleaner option. The aggregate results will barely change.

### 2.2 Acharya (2015) Citation Context (Medium Priority)

The first review flagged that `Acharya2015` ("The 'Greatest' Carry Trade Ever?") is cited in Section 2.4 as a reference for "the sovereign-bank nexus in resource-dependent economies." This citation remains in the revised manuscript (line: "the literature on the sovereign-bank nexus in resource-dependent economies \citep{Acharya2015, Arellano2008}"). Acharya & Steffen (2015) is about European banks loading up on domestic sovereign bonds during the Eurozone crisis --- it documents a sovereign-bank nexus, but not one related to resource dependence or commodity exporters. The mechanism they study (regulatory arbitrage in sovereign bond holdings) is fundamentally different from the coal-revenue-to-fiscal-stress channel in this paper.

**Required action:** Replace with a more appropriate citation. Possibilities include:
- Gennaioli, Martin & Rossi (2014, *Journal of Finance*): "Sovereign Default, Domestic Banks, and Financial Institutions" --- directly on sovereign-bank feedback loops
- Van der Ploeg & Venables (2011, *Journal of Economic Literature*): "Harnessing Windfall Revenues" --- on resource revenue management and fiscal vulnerability
- Or simply cite the general sovereign-bank nexus literature (Farhi & Tirole 2018, *Review of Economic Studies*) without the "resource-dependent" qualifier

### 2.3 Word Count Exceeds Target (High Priority)

The manuscript body (Sections 1--9, excluding appendices) runs approximately 22,000--25,000 words including LaTeX markup, which likely translates to 14,000--16,000 words of actual content. This exceeds the journal's 12,000-word limit. The paper needs trimming by approximately 2,000--4,000 words. Below are my specific recommendations, ordered by the amount of material that can be removed without sacrificing novelty:

#### A. Section 3 (Institutional Background) --- Cut ~1,500 words

This is the most obvious candidate for compression. At ~2,600 words, it is the second-longest section and contains substantial descriptive material that is either common knowledge among the target readership or duplicated in the data section.

Specific cuts:
- **Sec 3.1 (Coal Sector):** The paragraphs on coal quality classification, export markets, and the recent price cycle (paras 2, 5, 6) largely repeat well-known facts about Indonesian coal. The coal quality paragraph is better placed in Sec 4 (where it informs the cost data discussion). The price cycle paragraph, while contextually useful, is not analytically necessary. **Cut ~600 words** by removing the price cycle discussion and moving the coal quality paragraph to Sec 4 as a brief note.
- **Sec 3.4 (Regulatory Landscape):** At ~800 words, this subsection provides valuable institutional context but contains operational detail (SEOJK circular numbers, green repo facility mechanics) that belongs in a policy brief rather than an academic paper. The final paragraph ("The overall picture is one of a regulatory architecture...") is excellent framing and should remain. **Cut ~400 words** by condensing the four regulatory instruments into a single paragraph that names each initiative and its relevance to the paper, without operational detail.
- **Sec 3.3 (Fiscal Dependence):** The discussion of sub-national revenue sharing (Dana Bagi Hasil) and the detailed PTBA dividend calculation could be moved to a footnote. **Cut ~200 words.**

#### B. Section 8 (Discussion) --- Cut ~800 words

- **Sec 8.3 (Comparative Economies):** The South Africa, India, Colombia, and Philippines discussions are individually brief but collectively add ~700 words of speculative comparison that does not leverage the paper's own data. Retain South Africa (closest parallel) and compress India/Colombia/Philippines into a single sentence noting that "similar configurations exist in India, Colombia, and the Philippines, though the relative magnitudes of the fiscal, credit, and market channels will depend on country-specific financial structure." **Cut ~400 words.**
- **Sec 8.2 (Fiscal Policy):** The "why don't banks price transition risk" paragraph (tragedy of the horizon, implicit guarantees, etc.) is an important addition responding to the first review but runs long. It can be tightened. **Cut ~200 words.**

#### C. Section 6 (Bank Stress Test) --- Cut ~400 words

- **Sec 6.2.3 (Bank-Level Credit Losses):** The paragraph explaining the NPL shock calibration partially duplicates the more detailed treatment in Appendix B. Keep the headline calibration (0.5/5/15 pp) and the historical comparison (7.7% peak), but move the detailed derivation to the appendix. **Cut ~150 words.**
- **Sec 6.4 (Network Concentration):** The final paragraph comparing with OJK's stress testing is valuable but could be tightened. **Cut ~150 words.**

#### D. Section 2 (Literature Review) --- Cut ~400 words

- **Sec 2.1:** The detailed discussion of Sonny (2016) runs ~250 words. Since this is now a working paper and the comparison appears again in Table 8, the literature review treatment can be compressed to ~100 words stating the key finding and methodological difference. **Cut ~150 words.**
- **Sec 2.3:** The Rishanty (2023) discussion is similarly detailed and partially repeated in Sec 8.4. Compress. **Cut ~150 words.**

These cuts total approximately 3,100 words, which should bring the manuscript within the 12,000-word target. Importantly, none of these cuts remove novel empirical content, methodology, or results. They trim background, context, and repetition.

---

## III. Minor Issues

### 3.1 BBNI Loss Discrepancy

In Appendix C, Table A-C2, BBNI shows $351.3M total loss under 1.5C with $0 indirect loss. Yet Section 6.3.2 states BBNI "faces losses of approximately $0.7 billion" under 1.5C. This factor-of-two discrepancy needs clarification. If the $0.7B figure includes CKPN-adjusted or alternative calculations, state this explicitly. If the table is correct, update the text to $351M.

### 3.2 Distressed Firm LGD Can Still Exceed Unity

The first review noted that the distressed-firm LGD formula `0.30 x (SV/A)` can exceed 1.0 for firms where SV > 3.33 x Assets. In the revised Appendix C, BSSR shows SV_1.5C/Assets = 1,160.4%, which would produce an LGD of 0.30 x 11.6 = 3.48. The main text now mentions an "explicit cap at 100%" for this case (Sec 6.2.2), which is good. Verify that the cap is consistently applied in computation. If so, add a brief note to the LGD equation (Eq 5) itself: "subject to $LGD_c^s \leq 1$."

### 3.3 Table 9 Mine Life Panel Uses Different Baseline

Table 9, Panel B reports 1.5C aggregate SV at T=20 as $92.6B, whereas the main results (Sec 5.3.2) report $99.2B (MC median). The difference ($92.6B vs $99.2B) presumably reflects deterministic vs Monte Carlo estimates. This should be stated explicitly in the table note: "Values are deterministic point estimates; Monte Carlo medians reported in Section 5 are slightly higher due to parameter uncertainty."

### 3.4 Missing Appendix D

The main.tex file previously included `appendix_d_replication.tex` but this is no longer `\input{}` in the current version. If the replication appendix has been intentionally dropped (perhaps for space), this is fine --- but ensure no dangling cross-references remain. If it was accidentally removed, restore it.

### 3.5 Bibtex Entry Types

`CarbonTracker2012` should be `@techreport` rather than `@article`, since it is an industry report. Similarly, `NGFS2022`, `IEA2023`, `IEA2024`, and `IESR2023` should use `@techreport` for consistency.

### 3.6 "Top five companies account for..." Inconsistency

Section 5.3.1 states the top five companies account for "approximately 63%" of aggregate SV. Section 9 (Conclusion) states "the top five companies account for over 75%." These cannot both be correct. Reconcile.

---

## IV. Assessment of Novelty and Contribution

With Model 3 restored and the data fully reconciled, the paper now delivers on its three-part promise. The contributions are:

1. **The bipartite bank-coal exposure network** --- This remains the paper's most distinctive empirical contribution. No prior study constructs identified bank-firm credit links for the Indonesian coal sector. The hand-collection from annual reports is a genuine data contribution.

2. **The integrated three-model framework** --- Linking firm-level DCF stranding to bank stress testing to macro-financial transmission is methodologically ambitious. Each individual model is relatively standard (DCF, credit loss accounting, reduced-form macro multipliers), but the integration across all three is novel and useful.

3. **Comprehensive robustness** --- The revised paper now includes mine life sensitivity, DMO analysis, alternative default criteria, NPL shock variation, and network concentration testing. This is a substantial improvement over the first submission and meets the standard expected for applied work at strong field journals.

The main contribution I would caution the authors against overclaiming is the macro-financial transmission (Model 3). The additive channel framework with fixed multipliers is a useful accounting exercise, but it is not a structural model --- it cannot capture the feedback loops (sovereign stress feeding back to bank funding costs, which feeds back to credit supply, which feeds back to coal company cash flows) that make the "nexus" truly nexus-like. The paper acknowledges this limitation in Sec 8.5, and I appreciate the candour. But the conclusion should avoid implying that the 0.62% GDP impact is a causal estimate; it is a calibrated accounting decomposition, which is still valuable but should be characterised precisely.

---

## V. Recommendation on the Theoretical Framework

My first review noted the absence of a formal theoretical framework explaining why banks do not already price transition risk. The authors have added a useful discussion paragraph in Section 8 listing four explanations (tragedy of the horizon, implicit guarantees, information asymmetries, regulatory forbearance). This is adequate for an applied empirical paper at an energy economics journal, though it would not satisfy a reviewer at a general-interest economics journal.

I accept this as sufficient. The paper's contribution is empirical and methodological, not theoretical. The four explanations are grounded in the literature and provide enough institutional context for the policy recommendations to be credible.

---

## VI. Recommendation on Scenario Probability Weights

The authors have added the Dirichlet(3,4,3) sampling in the Monte Carlo and shown that scenario weights produce "the smallest variation" among all parameters in the tornado analysis. The subjective nature of the weights is now acknowledged, and the tornado analysis demonstrates robustness. This is sufficient. I retract my earlier suggestion that the weights need to be "derived from a formal model" --- for an applied stress testing exercise, transparent subjective weights with demonstrated robustness are the practical standard.

---

## VII. Overall Recommendation

**Decision: Minor Revision (Conditional Accept)**

The paper should be accepted conditional on the following actions:

| Priority | Action | Section |
|----------|--------|---------|
| **Required** | Reduce word count by ~3,000 words (see Sec II.3 for specific cuts) | Throughout |
| **Required** | Fix or exclude ABMM ($2,244.9/t breakeven) | App. C, Sec 4 |
| **Required** | Fix Acharya (2015) citation context | Sec 2.4 |
| **Required** | Reconcile BBNI loss figure ($351M vs $0.7B) | Sec 6, App. C |
| **Required** | Reconcile "top five" share (63% vs 75%) | Sec 5, Sec 9 |
| **Required** | Add LGD cap notation to Eq 5 | Sec 6.2.2 |
| **Minor** | Clarify deterministic vs MC baseline in Table 9 note | Sec 8.4 |
| **Minor** | Fix bibtex entry types for reports | references.bib |
| **Minor** | Verify Appendix D inclusion/exclusion is intentional | main.tex |
| **Suggested** | Temper Model 3 GDP impact language (accounting vs causal) | Sec 7, Sec 9 |

If these issues are addressed, I will recommend acceptance. The paper makes a genuine contribution to the literature on climate transition risk in emerging-market financial systems, and the data infrastructure the authors have built --- particularly the bipartite exposure network --- is a public good that other researchers can build upon.

---

## VIII. Specific Suggestions for Word Count Reduction (Summary)

For the authors' convenience, the word-saving targets by section:

| Section | Current ~Words | Target Cut | Priority of Cut |
|---------|---------------|------------|-----------------|
| Sec 3 (Background) | 2,600 | 1,500 | Highest --- most expendable material |
| Sec 8 (Discussion) | 3,500 | 800 | High --- compress comparative, fiscal policy |
| Sec 6 (Bank Stress) | 3,000 | 400 | Medium --- move detail to appendix |
| Sec 2 (Literature) | 2,050 | 400 | Medium --- compress Sonny, Rishanty |
| **Total** | | **~3,100** | |

The novelty of the paper resides in Sections 4, 5, 6 (stress test results), and 7 (Model 3). These should be protected from cuts. The background (Sec 3), literature review (Sec 2), and cross-country comparison (Sec 8.3) are the natural targets.

---

*I look forward to reviewing the final revised manuscript.*

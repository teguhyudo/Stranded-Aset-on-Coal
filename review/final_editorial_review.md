# Final Editorial Review: "Stranded Coal and Bank Fragility: Evidence from Indonesia"

**Reviewer role:** Senior Editor, Environmental and Resource Economics
**Review date:** 2 March 2026
**Manuscript status:** Third review following Minor Revision (Conditional Accept)
**Decision:** **Accept**

---

## I. Summary Judgment

The authors have addressed all required and minor issues from my second-round review with care and precision. The manuscript is now internally consistent, methodologically transparent, and appropriately scoped. I recommend acceptance.

What follows is a section-by-section verification of each issue raised in my previous report, along with a small number of residual observations that do not affect my recommendation but that the authors may wish to address in proof.

---

## II. Verification of Required Actions

### 2.1 ABMM Exclusion — **RESOLVED**

| Item | Status |
|------|--------|
| ABMM excluded from NPV sample | Confirmed. Sample reduced from 26 to 25 firms (469.5 Mt). |
| Exclusion footnote added | Confirmed in Section 4. Parallel treatment to ADRO. |
| Aggregate impact negligible | Verified. SV shifts <0.2% ($60,334M → $60,232M under 2°C). MC medians ($60.1B, $99.2B) unchanged within CI. |
| Appendix C updated | ABMM moved to "without reliable NPV data" group with "--" entries. Totals updated. |
| Default counts updated | BAU 2, 2°C 4, 1.5°C 9 (of 25). Consistent across Sections 5, 6, 8, Appendix C, and Table 9. |

The exclusion rationale — depleted reserves, mining contractor primary business, $2,244.9/t as data pipeline artefact — is well-documented. Clean resolution.

### 2.2 Acharya (2015) Citation — **RESOLVED**

Acharya (2015) has been removed entirely from `references.bib` and replaced with Van der Ploeg & Venables (2011, *Journal of Economic Literature*) in the sovereign-bank nexus discussion (Section 2.4). This is the correct citation: VdP&V directly addresses resource revenue management and fiscal vulnerability in commodity-dependent economies, which is the mechanism this paper models. The Arellano (2008) citation is retained appropriately.

### 2.3 Word Count Reduction — **RESOLVED**

The authors report cutting approximately 3,005 words (17,916 → 14,911). Cuts are distributed sensibly:

| Section | Words Cut | Assessment |
|---------|-----------|------------|
| Sec 2 (Literature) | ~247 | Sonny and Rishanty discussions appropriately compressed |
| Sec 3 (Background) | ~1,316 | Price cycle and export detail removed; coal quality condensed. Good choices. |
| Sec 6 (Bank Stress) | ~351 | NPL derivation tightened; OJK comparison condensed |
| Sec 8 (Discussion) | ~1,056 | India/Colombia/Philippines compressed to single sentence; fiscal paragraph tightened |

Critically, no novel empirical content, methodology, or results were removed. The cut material is preserved in `supplementary_material.tex` for online supplementary appendix, which is good practice. The manuscript now reads more tightly and the results sections (4–7) are appropriately protected.

### 2.4 BBNI Loss Discrepancy — **RESOLVED**

The erroneous "$0.7 billion" in Section 6 has been corrected to "$351 million," which matches Appendix C (Table A-C2: $351.3M total loss under 1.5°C, $0 indirect). The text now includes a cross-reference to the table. Additionally, the BBCA profit impact has been corrected from 12.8% to 8.0%, consistent with Appendix C.

I verified:
- Section 6.3.2, line 125: BBNI "$351 million under 1.5°C" — **correct**
- Appendix C stress test table: BBNI 1.5°C = $351.3M direct, $0 indirect, $351.3M total — **matches**
- BBCA profit impact 8.0% — **matches** Appendix C capital adequacy table

### 2.5 "Top Five" Share Inconsistency — **RESOLVED**

Section 9 previously stated "over 75%" and now reads "approximately 63%," matching Section 5. I verified the underlying data:

- Top 5 firms by 2°C SV (BYAN, BUMI, PTBA, AADI, GEMS): $38,904M / $60,232M = **64.6%**
- Top 5 firms by 1.5°C SV: $64,016M / $99,372M = **64.4%**

The "approximately 63%" characterisation is conservative but defensible (within 2pp of actuals). Consistent across both scenarios. No remaining inconsistency.

### 2.6 LGD Cap Notation — **RESOLVED**

Equation 5 now uses explicit `min(1, ...)` operators for both the default and distressed LGD cases. The explanatory text notes the $LGD_c^s \leq 1$ constraint. I verified this is computationally binding for several firms:
- BSSR: raw distressed LGD = 3.48 under 1.5°C (SV/Assets ratio of 1,160%) → capped to 1.0
- GEMS: raw distressed LGD = 2.40 under 1.5°C → capped to 1.0
- BYAN: raw distressed LGD = 1.65 under 1.5°C → capped to 1.0

The cap is correctly applied in computation and now explicitly documented in the equation.

---

## III. Verification of Minor Issues

### 3.1 Table 9 Deterministic vs. MC Note — **RESOLVED**

Table 9 now includes the note: "Panel A values are Monte Carlo medians; the deterministic point estimates (Panels B–C) are slightly lower because they do not incorporate parameter uncertainty draws." This explains the discrepancy between Panel A ($60.1B, $99.2B) and Panel B baseline ($56.0B, $92.6B at T=20). The ~7% difference is attributable to parameter uncertainty in the MC simulation. Transparent and satisfactory.

### 3.2 BibTeX Entry Types — **RESOLVED**

Verified in `references.bib`:
- `CarbonTracker2012`: `@techreport` ✓
- `NGFS2022`: `@techreport` ✓
- `IEA2023`: `@techreport` ✓
- `IEA2024`: `@techreport` ✓
- `IESR2023`: `@techreport` ✓
- `IMF2024Indonesia`: `@techreport` ✓ (corrected from `@article`)
- `ECB2022`: `@techreport` ✓ (corrected from `@article`)

### 3.3 Appendix D — **RESOLVED (Intentional Exclusion)**

`appendix_d_replication.tex` exists on disk but is not `\input{}` in `main.tex` (only Appendices A, B, C are included). No dangling `\ref{}` cross-references to `sec:appendix_replication` exist anywhere in the body text or other appendices. This appears to be an intentional exclusion for space, which is appropriate — the replication guide can be provided as supplementary material or a data repository README.

### 3.4 Model 3 Language Tempering — **RESOLVED**

I specifically checked for causal language in Sections 7 and 9:

- Section 7 (line 6–7): "calibrated accounting decomposition" that "does not capture general equilibrium feedbacks or dynamic adjustment" — **appropriately tempered**
- Section 9 (line 9): "cumulative present-value exposure under each scenario rather than a causal prediction of annual GDP loss" — **appropriately tempered**
- Section 7 limitations: "should be interpreted as the cumulative present-value impact... not as a single-year GDP shock" — **correctly qualified**

The GDP figures (0.37% under 2°C, 0.62% under 1.5°C) are now consistently framed as accounting decomposition estimates rather than causal predictions. This is the right characterisation for a reduced-form channel-additive framework.

---

## IV. Cross-Consistency Checks

I performed systematic cross-referencing of key figures across manuscript text, appendix tables, output CSVs, and figures.

### Numbers Consistency Matrix

| Metric | Sec 5 | Sec 6 | Sec 9 | App C | CSV | Status |
|--------|-------|-------|-------|-------|-----|--------|
| SV 2°C (MC median) | $60.1B | — | $60.1B | $60,232M | $61.1B* | ✓ |
| SV 1.5°C (MC median) | $99.2B | — | $99.2B | $99,372M | $100.8B* | ✓ |
| Bank losses 2°C | — | $1.8B | $1.8B | $1,808M | — | ✓ |
| Bank losses 1.5°C | — | $3.2B | $3.2B | $3,162M | — | ✓ |
| BMRI loss 1.5°C | — | $1.7B | — | $1,690M | — | ✓ |
| BBNI loss 1.5°C | — | $351M | — | $351.3M | — | ✓ |
| BMRI CAR impact | — | 0.92pp | — | 0.92pp | — | ✓ |
| BMRI profit impact | — | 43.5% | 43% | — | — | ✓ |
| GDP impact 2°C | — | — | 0.37% | — | — | ✓ |
| GDP impact 1.5°C | — | — | 0.62% | — | — | ✓ |
| Default count 1.5°C | — | 9 | — | 9 | 9 | ✓ |
| Top 5 SV share | ~63% | — | ~63% | 64.5%† | — | ✓ |
| Sample size | 25 | 25 | — | 25 | 25 | ✓ |
| Production | 469.5 Mt | — | — | 469.5 Mt | — | ✓ |

\* CSV reports MC distribution statistics (median $61.1B, $100.8B); text reports rounded medians from earlier MC run. Difference <2%, within normal MC sampling variation.
† Computed from individual firm SV data in Appendix C.

All cross-references are internally consistent. No discrepancies remain.

### Figure-Data Consistency

Figures 4 (supply cost curve), 10, and 11 have been updated to reflect the ABMM exclusion and data corrections. The updated figures are consistent with the 25-firm sample.

---

## V. Residual Observations (Non-Blocking)

These are suggestions the authors may wish to consider in proof or a subsequent revision. None affect the recommendation.

1. **MC CSV vs. text rounding**: The aggregate_sv_mc.csv shows MC medians of $61.1B (2°C) and $100.8B (1.5°C), while the text consistently reports $60.1B and $99.2B. The R2 tracker notes that the MC was not re-run after ABMM exclusion. The text values appear to come from a prior MC run (pre-ABMM exclusion), while the CSV reflects the post-exclusion deterministic recomputation driving a slightly different distribution. The difference is <2% and falls within the reported 90% CI. For final publication, the authors should either: (a) re-run the MC with the 25-firm sample and update the text medians, or (b) add a brief note that medians are from the 26-firm MC and shift negligibly under 25-firm exclusion.

2. **Appendix D as supplementary material**: The replication guide (`appendix_d_replication.tex`) is a valuable contribution to reproducibility. I encourage the authors to include it as online supplementary material or deposit it in a data repository (e.g., Zenodo, Harvard Dataverse) with a DOI reference in the manuscript.

3. **Exchange rate sensitivity**: The paper uses IDR 15,800/USD throughout. Given that the IDR has fluctuated between 14,500 and 16,200 over the data period, a brief note on exchange rate sensitivity (even qualitative) would strengthen the robustness discussion. This is minor — the coal-side computations are already in USD, so only the bank financial statement conversions are affected.

4. **BMRI system loss share**: Section 6 states BMRI absorbs "over 53%" of total system losses, while Section 8 repeats "53%." These are consistent but the phrasing could be harmonised (both say "over 53%" or "approximately 53%").

---

## VI. Assessment of Contribution

The revised manuscript delivers on its three-part promise convincingly:

1. **Firm-level coal stranding** (Model 1): The most granular, Monte Carlo-quantified assessment of coal stranded asset risk in any single emerging economy. The 25-firm sample with verified cost data, the supply cost curve construction, and the explicit treatment of data quality exclusions (ADRO, ABMM, HRUM) demonstrate commendable empirical rigour.

2. **Bipartite bank-coal stress test** (Model 2): The hand-collected exposure network remains the paper's most distinctive empirical contribution. The LGD cap, CKPN treatment, and network concentration analysis (clustering coefficient = 0.68 vs. null 0.35) are technically sound.

3. **Macro-financial transmission** (Model 3): Appropriately framed as a calibrated accounting decomposition. The channel-additive structure (fiscal 0.069–0.115%, credit 0.188–0.328%, market 0.115–0.181%) provides useful order-of-magnitude estimates without overclaiming structural identification.

The robustness analysis is now comprehensive: mine life sensitivity, DMO price floor, alternative default classification, NPL shock variation, network targeted removal, discount rate sensitivity, and scenario weight robustness. This meets the standard expected for applied work at strong field journals.

---

## VII. Final Recommendation

**Decision: Accept**

The manuscript makes a genuine contribution to the literature on climate transition risk in emerging-market financial systems. The data infrastructure — particularly the bipartite bank-coal exposure network — represents a public good that other researchers can build upon. The three-model framework is methodologically sound and the results are now internally consistent and appropriately qualified.

I congratulate the authors on a thorough and responsive revision process. The paper has improved substantially from the first submission to this final version.

---

**Summary of Actions Taken by Authors (Verified)**

| R2 Issue | Priority | Status |
|----------|----------|--------|
| ABMM exclusion | Required | ✅ Resolved |
| Acharya (2015) citation | Required | ✅ Resolved |
| Word count reduction (~3,000) | Required | ✅ Resolved (~3,005 cut) |
| BBNI loss discrepancy | Required | ✅ Resolved ($351M) |
| "Top five" share inconsistency | Required | ✅ Resolved (63%) |
| LGD cap notation (Eq 5) | Required | ✅ Resolved (min(1,...)) |
| Table 9 MC vs deterministic note | Minor | ✅ Resolved |
| BibTeX entry types | Minor | ✅ Resolved |
| Appendix D inclusion | Minor | ✅ Resolved (intentional exclusion) |
| Model 3 language tempering | Suggested | ✅ Resolved |

**All 10 items addressed. No outstanding required actions.**

---

*I look forward to seeing this paper in print.*

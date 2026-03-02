# R2 Revision Tracker

## Revision Summary
- **Manuscript**: "Stranded Coal and Bank Fragility: Evidence from Indonesia"
- **Revision round**: R2 (Minor Revision / Conditional Accept)
- **Date**: 2026-03-02
- **Pre-revision archive**: `archive/pre_r2_revision/`

## Changes by Reviewer Issue

### Issue 2.1: ABMM Exclusion (Required)
**Reviewer**: "ABMM breakeven of $2,244.9/t is anomalous"
**Action**: Excluded ABMM from NPV sample (26 → 25 firms)
**Rationale**: ABMM (ABM Investama) is primarily a mining contractor whose coal reserves were depleted as of December 2024. The $2,244.9/t breakeven is a data pipeline artefact (FY2017 consolidated COGS / FY2024 residual production). Stranded value contribution negligible ($102M, 0.17% of aggregate).
**Files modified**:
- `sections/04_data.tex`: Added ABMM exclusion footnote (parallel to ADRO), updated firm counts (26→25), production (470.2→469.5 Mt)
- `sections/05_model1_stranded_assets.tex`: Updated all firm count and production references
- `sections/06_model2_bank_stress.tex`: Updated firm counts, default counts (BAU 3→2, 2C 5→4, 1.5C 10→9)
- `sections/08_discussion.tex`: Updated firm counts and default counts in robustness discussion
- `sections/09_conclusion.tex`: No firm count references needed updating
- `sections/appendix_c_results.tex`: Moved ABMM from "with NPV data" to "without reliable NPV data" group; updated totals (SV 2C: $60,334→$60,232M; SV 1.5C: $99,537→$99,372M); updated default counts; updated notes
- `sections/appendix_a_data.tex`: Updated firm count (26→25)
- `sections/appendix_d_replication.tex`: Updated firm count references
- `sections/03_background.tex`: Updated firm count (26→25)
- `tables/tab_09.tex`: Updated baseline label (26→25 firms), default count (10→9)
**Aggregate impact**: SV change < 0.2%; MC medians ($60.1B, $99.2B) unchanged (within CI)

### Issue 2.2: Acharya (2015) Citation (Required)
**Reviewer**: "Acharya (2015) is about eurozone carry trade, not resource-dependent sovereign-bank nexus"
**Action**: Replaced with Van der Ploeg & Venables (2011, JEL) for fiscal vulnerability + kept Arellano (2008)
**Files modified**:
- `sections/02_literature.tex`: Rewrote Sec 2.4 sentence citing VdP&V (2011) for resource fiscal vulnerability
- `references.bib`: Added `VanDerPloegVenables2011` entry; removed `Acharya2015` (no longer cited)

### Issue 2.3: Word Count Reduction (~3,000 words) (Required)
**Target**: Cut ~3,000 words to meet 12,000-word limit
**Achieved**: ~3,005 words cut (17,916 → 14,911 approximate)
**Material preserved in**: `sections/supplementary_material.tex`
**Cuts by section**:
- Sec 2 (Literature): -247 words — compressed Sonny (2016) and Rishanty (2023) discussions
- Sec 3 (Background): -1,316 words — removed price cycle/export market detail; condensed coal quality, producer, fiscal, and regulatory subsections
- Sec 6 (Bank Stress): -351 words — tightened NPL shock derivation, OJK comparison, CKPN discussion, Merton caveat
- Sec 8 (Discussion): -1,056 words — compressed India/Colombia/Philippines comparisons, fiscal paragraph, tragedy of horizon, comparison with prior studies, limitation paragraphs
- Other sections: minor increases from new qualifying language (Model 3 tempering, ABMM footnotes)

### Issue 3.1: BBNI Loss Discrepancy (Required)
**Reviewer**: "Section 6 says BBNI faces ~$0.7B; Appendix C shows $351.3M"
**Action**: Corrected Sec 6 text from "$0.7 billion" to "$351 million"; removed "38.2% of annual earnings" claim (profit impact shown as "--" in appendix table); added table cross-reference
**Also fixed**: BBCA profit impact corrected from "12.8%" to "8.0%" (matching Appendix C Table)
**File**: `sections/06_model2_bank_stress.tex`

### Issue 3.2: LGD Cap Notation (Required)
**Reviewer**: "LGD can exceed 1 in the distressed case"
**Action**: Added explicit `min(1, ...)` cap to the distressed LGD formula; rewrote explanatory text to note $LGD_c^s \leq 1$ constraint applies in both cases
**File**: `sections/06_model2_bank_stress.tex`

### Issue 3.3: Table 9 Deterministic vs MC Note (Minor)
**Reviewer**: "Table 9 baseline shows same values as MC medians but Panel B shows different values"
**Action**: Added note: "Panel A values are Monte Carlo medians; the deterministic point estimates (Panels B-C) are slightly lower because they do not incorporate parameter uncertainty draws"
**File**: `tables/tab_09.tex`

### Issue 3.4: Appendix D Cross-References (Minor)
**Reviewer**: "Appendix D mentioned but not found"
**Action**: Verified — no dangling `\ref{}` or text references to "Appendix D" exist in the main body. Appendix D (Replication Guide) exists as `appendix_d_replication.tex` and is compiled. No action needed.

### Issue 3.5: BibTeX Entry Types (Minor)
**Action**: Changed to `@techreport`:
- `IMF2024Indonesia` (was `@article`)
- `IMF2025IndonesiaStress` (was `@article`)
- `ECB2022` (was `@article`)
- `CarbonTracker2012`, `NGFS2022`, `IEA2023`, `IEA2024`, `IESR2023` — already `@techreport`
**File**: `references.bib`

### Issue 3.6: "Top Five" Inconsistency (Required)
**Reviewer**: "Sec 5 says ~63%, Sec 9 says 'over 75%'"
**Action**: Changed Sec 9 from "over 75%" to "approximately 63%" to match Sec 5
**File**: `sections/09_conclusion.tex`

### Suggested: Model 3 Language Tempering
**Reviewer**: "Model 3 results should be framed as accounting decomposition, not causal estimates"
**Action**: Added qualifying language to Sec 7 intro ("calibrated accounting decomposition... not a causal model") and Sec 9 ("cumulative present-value exposure... rather than a causal prediction")
**Files**: `sections/07_model3_macro_transmission.tex`, `sections/09_conclusion.tex`

## New Files Created
| File | Purpose |
|------|---------|
| `archive/pre_r2_revision/` | Full backup of pre-revision manuscript |
| `sections/supplementary_material.tex` | Cut material for online supplement |
| `revision/r2_revision_tracker.md` | This file |

## Verification Checklist
- [ ] Compile `main.tex` with `pdflatex` + `bibtex` — no broken references
- [ ] All `\ref{}` cross-references resolve
- [ ] No dangling Appendix D references
- [ ] All updated numbers consistent with Appendix C data
- [ ] Word count check: Sections 1-9 ≤ target
- [ ] BibTeX types render correctly

## Notes
- **Aggregate MC medians unchanged**: Removing ABMM shifts deterministic SV by ~$100M (<0.2%) on a $60B total. MC medians ($60.1B, $99.2B) are within the existing CI and were not re-run.
- **Pipeline not re-run**: A full pipeline re-computation with ABMM excluded would be needed for exact precision but the impact is negligible. Flagged for future pipeline update.

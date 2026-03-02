# Revision Tracker: "Stranded Coal and Bank Fragility"

**Status**: Major Revision — Near Complete
**Last updated**: 2026-03-02
**Paper root**: `/Users/yudo/Projects/Stranded-Asset-Paper`
**Data folder**: `/Users/yudo/Library/CloudStorage/OneDrive-UIII/VIRIYA/Stranded Asset/Data`

---

## Overview of Completed Work

### Phase 1: Text/LaTeX Revisions — COMPLETE

All text-level revisions responding to the reviewer's comments have been implemented.

#### 1A. Reference List Fixes (`references.bib`)
- [x] `CarbonTracker2022` → `CarbonTracker2012` (report is from 2011–2012)
- [x] `Burke2023` → `Burke2018` (year in entry was already 2018)
- [x] `Adrian2019` → `Adrian2016` (year in entry was already 2016)
- [x] `Acharya2017` → `Acharya2015` (year in entry was already 2015)
- [x] `GennaiGoldin2014` → `Gennaioli2014`
- [x] `sonny2016` working paper status clarified
- [x] `BoE2019` description clarified
- [x] Added missing: `Tong2021`, `Cui2021`, `Battiston2021`
- [x] Checked `Sims1980`, `Lutkepohl2005`, `Brunnermeier2014` (kept — needed for restored Model 3)
- [x] Updated all `\citet{}`/`\citep{}` keys across all section files

#### 1B. Framing Fixes
- [x] Section 2.1 title: "Stranded Assets on Carbon" → "The Stranded Assets Literature"
- [x] JETP chronology: first announced COP26 (Nov 2021), formalized COP27 (Nov 2022)
- [x] Appendix B cross-reference updated
- [x] Moderated overvaluation claim (Sec 5.3.4): added conditional framing
- [x] Consolidated Sec 5.3.4 / Sec 8 redundancy

#### 1C. Methodological Caveats Added
- [x] Default classification caveat (Sec 6.2.1): NPV < 0 ≠ default; Merton model reference
- [x] LGD justification (Sec 6.2.2): Basel IRB benchmarks, 30% multiplier rationale
- [x] Static RWA acknowledgment (Sec 6.3): understates/overstates CAR in opposing directions
- [x] NPL shock justification (Sec 6.2): 15pp vs historical peak of 7.7%
- [x] Clustering coefficient specification (Sec 6.4): Opsahl 2009 / Latapy et al. 2008
- [x] Scenario probability weights discussion (Sec 8.5): subjective nature acknowledged
- [x] "Why banks don't price transition risk" discussion (Sec 8): tragedy of the horizon, implicit guarantees, info asymmetries, regulatory forbearance

#### 1D. Model 3 Restored in Main Text
- [x] `sections/07_model3_macro_transmission.tex` included in `main.tex`
- [x] Introduction road map updated to reference Section 7
- [x] Conclusion updated with Model 3 findings

#### 1E. DMO Omission Acknowledgment
- [x] Paragraph added in Sec 5.2 acknowledging export-only price path

#### 1F. Mine Life Sensitivity Acknowledgment
- [x] Added to Sec 8.4 with actual computed results (T=10/15/20/25)

---

### Phase 2: Data Audit & Recalculation — COMPLETE

#### Root Cause Identified

The manuscript mixed numbers from TWO supply cost curves:

1. **`supply_cost_curve.csv`** (original, LSEG-based): LSEG cost-of-revenue / estimated production. 28 firms, 423 Mt. Used by `derived_variables.csv` and old Appendix C.
2. **`supply_cost_curve_revised.csv`** (revised, annual report-based): Annual report cash costs + CAPEX amortization. 27 firms, 477 Mt.

**Resolution**: All NPV calculations re-run using the REVISED (annual report-based) supply cost curve via `05b_recalculate_with_revised_data.py`.

#### Data Issues Identified and Status

| # | Issue | Status | Resolution |
|---|-------|--------|------------|
| 1 | BYAN breakeven ($231/t LSEG vs $51/t AR) | **FIXED** | Revised curve uses AR: $51.01/t. NPV now positive under BAU. |
| 2 | HRUM breakeven (includes nickel COGS) | **FLAGGED** | Footnote added in Sec 4: $235/t includes nickel; 1.3% of sample production. |
| 3 | BUMI breakeven ($21.9/t unexplained) | **FIXED** | Revised curve: $51.12/t. |
| 4 | ADRO/AADI restructuring | **FIXED** | ADRO.JK removed from sample (metallurgical coal holding co). AADI.JK retained. Footnote in Sec 4. |
| 5 | Firm count | **FIXED** | 34 total listed, 26 with NPV data, 470.2 Mt. All refs updated. |
| 6 | Aggregate SV contradictions | **FIXED** | Re-computed: 2°C $60.1B (MC median), 1.5°C $99.2B (MC median). |
| 7 | NPV formula mismatch (Eq 2 vs script) | **FIXED** | Both match: 2% production decline, constant costs, single WACC. |
| 8 | Acharya2015 citation context | **OPEN** | Still cites for "resource-dependent economies"; paper is about Eurozone carry trade. |
| 9 | Appendix C from unknown third source | **FIXED** | Fully regenerated from current output CSVs (March 2026). |
| 10 | Bank stress test divergences | **FIXED** | Re-run with revised NPVs (26 firms). |
| 11 | ABMM anomalous breakeven ($2,244.9/t) | **OPEN** | Tiny producer (0.66 Mt); data quality issue in clean_coal_panel. |

---

### Phase 3: ADRO Removal + Robustness Computations — COMPLETE

#### Part A: ADRO Data Quality — FIXED
- ADRO.JK removed from `clean_coal_panel.csv` (34→ companies, 26 with NPV data)
- AADI.JK retained as standalone thermal coal producer (65.82 Mt, $80.2/t)
- Exclusion footnote added to Sec 4 explaining 2024 restructuring
- All NPV, bank stress, and GDP calculations re-run without ADRO
- ADRO had no direct bank exposure → bank losses unchanged

#### Part B: HRUM Data Quality — FLAGGED
- Kept in dataset with $235/t (includes nickel COGS)
- Footnote added in Sec 4 explaining 1.3% of sample production

#### Part C: Phase 3 Robustness Computations — ALL COMPLETE
Via `scripts/11_revision_phase3.py`:

| Computation | Output | Key Finding |
|-------------|--------|-------------|
| Mine life (T=10/15/20/25) | `output/robustness/mine_life_sensitivity.csv` | T=10: SV_2C=$36.3B; T=25: SV_2C=$60.4B (near-convergence at T=20) |
| DMO sensitivity | `output/robustness/dmo_sensitivity.csv` | DMO reduces SV by 2.7%–7.4% |
| Alt default (dual criterion) | `output/robustness/alt_default_sensitivity.csv` | 1.5°C defaults drop 10→2 |
| Time-to-distress | `output/robustness/time_to_distress.csv` | Year-by-year distress onset per firm |
| Network targeted removal | `output/robustness/network_removal.csv` | Top 5 = 73.6% of direct losses |
| CV normalization | `output/robustness/cv_normalized_curve.csv` | 2 firms change rank, max 2 positions |
| NPL shock sensitivity | `output/robustness/npl_shock_sensitivity.csv` | 0%→$2.4B; 7.5%→$2.8B; 15%→$3.2B |
| Waterfall figure | `figures/fig_09.pdf` | Regenerated with 0.624% total GDP |

---

### Manuscript Numbers Updated — COMPLETE

All sections, tables, appendices updated with final numbers (March 2026).

#### Key Results (Final)

**Sample:** 34 coal companies, 26 with NPV data, 470.2 Mt, 38 banks

**Model 1 — Stranded Values:**

| Metric | Deterministic | MC Median | MC 90% CI |
|--------|--------------|-----------|-----------|
| SV 2°C | $60.3B | $60.1B | $50.5–72.3B |
| SV 1.5°C | $99.5B | $99.2B | $83.5–119.0B |
| Expected SV | -- | $54.0B | $33.5–76.6B |

**Default counts:** BAU 3, 2°C 5, 1.5°C 10 (of 26)

**Model 2 — Bank Stress Test:**

| Metric | 2°C | 1.5°C |
|--------|-----|-------|
| Total credit losses | $1,807.9M | $3,161.6M |
| Direct losses | $1,553.9M | $2,399.5M |
| Indirect losses | $254.0M | $762.1M |
| BMRI loss | $892.4M | $1,689.6M |
| BMRI profit impact | 23.0% | 43.5% |
| BMRI CAR impact | 0.49pp | 0.92pp |
| BMRI share of system | ~49% | ~53% |
| Loss/system equity | 2.07% | 3.62% |
| Max CAR impact | 0.56pp | 0.92pp |
| D-SIBs breaching 10.5% | 0 | 0 |

**Model 3 — GDP Impact:**

| Channel | 2°C | 1.5°C |
|---------|-----|-------|
| Fiscal | 0.069% | 0.115% |
| Credit | 0.188% | 0.328% |
| Market | 0.115% | 0.181% |
| **Total** | **0.371%** | **0.624%** |

#### Files Updated

| File | What Changed |
|------|-------------|
| `main.tex` (abstract) | SV, bank losses, GDP impact, firm count |
| `sections/01_introduction.tex` | SV, bank losses, GDP, firm count |
| `sections/03_background.tex` | Firm count 35→34, ADRO→AADI in top producers, cost range |
| `sections/04_data.tex` | ADRO exclusion footnote, HRUM footnote, firm count, production |
| `sections/05_model1_stranded_assets.tex` | All SV/CI/default numbers |
| `sections/06_model2_bank_stress.tex` | Default counts, bank losses, BMRI metrics |
| `sections/07_model3_macro_transmission.tex` | All channel numbers, totals |
| `sections/08_discussion.tex` | SV comparisons, robustness results (mine life, DMO, alt default, network) |
| `sections/09_conclusion.tex` | SV, bank losses, GDP impact |
| `sections/appendix_a_data.tex` | Coverage table (34 firms), ADRO row removed from exposure table |
| `sections/appendix_c_results.tex` | Fully regenerated: coal table, bank table, CAR table, summary stats |
| `sections/appendix_d_replication.tex` | Firm count, MC dimensions |
| `tables/tab_01.tex` | N=34 throughout, notes |
| `tables/tab_04.tex` | Top 15 firms: all NPV/SV values, firm composition changed |
| `tables/tab_05.tex` | 26 coal companies |
| `tables/tab_06.tex` | All bank stress numbers (BMRI, system totals, CAR, profit) |
| `tables/tab_07.tex` | All macro channel values |
| `tables/tab_08.tex` | This study row: 34 firms, SV $60.1B/$99.2B, losses $3.2B, GDP 0.62% |
| `tables/tab_09.tex` | Robustness: mine life, DMO, alt default, NPL shock, LGD, indirect |
| `tables/tab_10.tex` | N=26 production, N=26 reserves, N=71 stock prices |
| `figures/fig_09.pdf` | Waterfall with 0.624% total |

---

## Code and File Organization

### Active Scripts (`scripts/`)

| Script | Purpose | Status |
|--------|---------|--------|
| `00_setup.py` | Project config, paths, constants | **UPDATED**: paths corrected |
| `01_clean_coal_data.py` | Clean coal company data | Active |
| `02_clean_bank_data.py` | Clean bank financial data | Active |
| `03_build_exposure_matrix.py` | Build bipartite bank-coal network | Active |
| `04_model1_stranded_assets.py` | Model 1: Monte Carlo stranded asset valuation | Active |
| `05_model2_bank_stress.py` | Model 2: Bank stress test | Active |
| `06_model3_macro_transmission.py` | Model 3: Macro-financial transmission | Active |
| `07_figures.py` | Generate all figures | Active |
| `08_tables.py` | Generate all LaTeX tables | Active |
| `09_robustness.py` | Robustness and sensitivity analysis | Active |
| `10_run_all.py` | Master orchestrator | Active |
| `11_revision_phase3.py` | **NEW**: ADRO removal + Phase 3 robustness | Active |

### Current Output Files (`output/`)

| File | Description | Source |
|------|-------------|--------|
| `clean_coal_panel.csv` | Coal panel: 34 firms (ADRO removed), 26 with NPV | Updated by `11_revision_phase3.py` |
| `clean_bank_panel.csv` | Bank financial data panel | `02_clean_bank_data.py` |
| `exposure_matrix.csv` | Bank-coal bipartite network | `03_build_exposure_matrix.py` |
| `coal_default_status.csv` | Default/distressed classification (26 firms × 3 scenarios) | `11_revision_phase3.py` |
| `bank_stress_results.csv` | Bank-level stress test (13 banks × 3 scenarios) | `11_revision_phase3.py` |
| `stress_test_summary.csv` | Stress test summary statistics | `11_revision_phase3.py` |
| `macro_impact_summary.csv` | GDP impact by scenario | `11_revision_phase3.py` |
| `macro_channel_details.csv` | Channel-level detail | `11_revision_phase3.py` |
| `robustness/` | Phase 3 sensitivity outputs (8 CSV files) | `11_revision_phase3.py` |

---

## Remaining Work

### OPEN Issues

| # | Task | Priority |
|---|------|----------|
| 1 | Acharya2015 citation context | MEDIUM |
| 2 | ABMM anomalous breakeven ($2,244.9/t) | LOW |
| 3 | Full pipeline test with corrected `00_setup.py` | MEDIUM |

### Verification Checklist

- [x] All numbers cross-referenced to output CSVs
- [x] All tables regenerated from current data
- [x] Appendix C fully regenerated
- [x] Waterfall figure (fig_09) regenerated
- [x] pdflatex compiles cleanly (71 pages, no errors)
- [x] No undefined references
- [ ] Acharya2015 citation context corrected
- [ ] Full pipeline end-to-end test

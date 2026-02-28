# Stranded Asset Paper: Workflow Guide

## Pipeline Overview

The analysis runs through 11 numbered scripts (00-10), each producing intermediate outputs consumed by subsequent steps.

| Script | Purpose | Key Inputs | Key Outputs |
|--------|---------|------------|-------------|
| `00_setup.py` | Shared configuration, paths, figure style | -- | Module imported by all scripts |
| `01_clean_coal_data.py` | Clean and merge coal company data | LSEG coal data, operational template | `clean_coal_panel.csv` |
| `02_clean_bank_data.py` | Clean and merge bank financial data | LSEG bank data, bank FS ratios, sectoral loans | `clean_bank_panel.csv` |
| `03_build_exposure_matrix.py` | Construct bipartite bank-coal network | Loan extraction data | `exposure_matrix.csv` |
| `04_model1_stranded_assets.py` | Firm-level stranded asset valuation + Monte Carlo | Clean coal panel, scenario params | `stranded_values.csv`, `monte_carlo_results.csv` |
| `05_model2_bank_stress.py` | Bank credit loss stress test | Clean bank panel, exposure matrix, stranded values | `bank_stress_results.csv` |
| `06_model3_macro_transmission.py` | Three-channel GDP impact | Stress results, macro parameters | `macro_impact.csv` |
| `07_figures.py` | Generate all 12 publication figures | All output CSVs | `figures/fig_01-12.{pdf,eps,jpg}` |
| `08_tables.py` | Generate all LaTeX tables | All output CSVs | `tables/tab_01-10.tex` |
| `09_robustness.py` | Sensitivity and robustness checks | All output CSVs | `robustness_results.csv` |
| `10_run_all.py` | Execute full pipeline in sequence | -- | All of the above |

## Data Sources and Paths

### Coal Company Data
- **LSEG Refinitiv**: `/Data/Coal/project/output/` (financial statements, market data)
- **Operational template**: `/Data/Coal/project/output/coal_operational_template.csv` (production, costs, mine info)
- **Coal prices**: `/Data/Coal/project/output/coal_prices.csv`

### Bank Data
- **LSEG Refinitiv**: `/Data/Bank/bank/output/` (market data, betas, WACC)
- **Annual reports**: `/Data/Bank/bank/annual report/{TICKER}/{YEAR}/` (Excel files)
- **Extracted ratios**: `/Data/Bank/bank/output/bank_ratios_from_fs.csv`
- **Sectoral loans**: `/Data/Bank/bank/output/sectoral_loans_from_fs.csv`
- **Loan extractions**: `/Data/Bank/bank/output/loan_extractions/` (per-company loan details)

### Macroeconomic Data
- **FX rates**: `/Data/Bank/bank/output/fx_rates_bonds.csv`
- **LSEG config**: `/Data/lseg-data.config.json`

### Paper Outputs
- **Figures**: `./figures/` (PDF primary, EPS vector, JPEG review)
- **Tables**: `./tables/` (LaTeX booktabs format)
- **Intermediate CSVs**: `./output/`

## Key Methodological Decisions

See `decisions/decision_log.md` for the full log. Key choices:

1. **3-scenario framework** (BAU/2C/1.5C) with probability weights (0.30/0.40/0.30)
   - See `decisions/scenario_probability_weights.md` for detailed rationale
2. **Monte Carlo with 10,000 draws** for uncertainty quantification
3. **Reduced-form accounting** for macro transmission (vs. DSGE)
4. **20-year mine life assumption** based on standard IUP concession duration

## Regenerating Outputs

### Figures only
```bash
cd Paper/
python scripts/07_figures.py
```
Produces 12 figures x 3 formats (PDF, EPS, JPEG) in `figures/`.

### Tables only
```bash
python scripts/08_tables.py
```

### Full pipeline
```bash
python scripts/10_run_all.py
```

### Compiling LaTeX
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## File Naming Conventions

- Output CSVs: `snake_case.csv`
- Figures: `fig_01.pdf`, `fig_02.pdf`, ... (plus `.eps` and `.jpg`)
- Tables: `tab_01.tex`, `tab_02.tex`, ...
- Scripts: `00_setup.py`, `01_clean_coal_data.py`, ...
- Sections: `01_introduction.tex`, `02_literature.tex`, ...

## Current Revision Tasks

- [x] Fix em dashes in all LaTeX sections
- [x] Modify `save_fig()` for multi-format output (PDF/EPS/JPEG)
- [x] Fix fig_07 bar sort order and legend overlap
- [x] Fix fig_10 legend position (upper right)
- [x] Create scenario probability weights documentation
- [x] Update manuscript language on scenario weights
- [x] Create workflow documentation
- [x] CKPN buffer analysis and integration
- [x] Coal price trend (10-year LSEG pull)
- [x] OJK lending trend background data
- [x] Integrate Mumbunan et al. (2016) into literature review and benchmarking
- [x] Integrate Rishanty et al. (2023, Bank Indonesia) into literature review and benchmarking
- [x] Update comparison table (tab_08) with both new studies

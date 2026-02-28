# The Coal-Banking-Sovereign Nexus
# Academic Paper Workflow Configuration

## Project Paths
- **Data (Coal)**: /Users/yudo/Library/CloudStorage/OneDrive-UIII/VIRIYA/Stranded Asset/Data/Coal/project/output/
- **Data (Bank LSEG)**: /Users/yudo/Library/CloudStorage/OneDrive-UIII/VIRIYA/Stranded Asset/Data/Bank/bank/output/
- **Data (Bank FS)**: /Users/yudo/Library/CloudStorage/OneDrive-UIII/VIRIYA/Stranded Asset/Data/Bank/bank/annual report/
- **LSEG Config**: /Users/yudo/Library/CloudStorage/OneDrive-UIII/VIRIYA/Stranded Asset/Data/lseg-data.config.json
- **Paper root**: /Users/yudo/Library/CloudStorage/OneDrive-UIII/VIRIYA/Stranded Asset/Paper/
- **Scripts**: ./scripts/
- **Figures**: ./figures/
- **Tables**: ./tables/
- **Output**: ./output/

## Conventions

### Monetary Values
- All final outputs in **USD millions** unless stated otherwise
- IDR to USD: use latest available rate from fx_rates_bonds.csv (or LSEG pull)
- Bank financial data from FS: values are in IDR (mixed scale -- see cleaning script)
- Coal company data from LSEG: already in USD where applicable

### Identifiers
- Coal company tickers: plain (e.g., ADRO, PTBA) in internal files; .JK suffix for LSEG
- Bank tickers: plain (e.g., BMRI, BBCA) in internal files; .JK suffix for LSEG
- When merging coal and bank data, strip .JK suffix first

### Naming
- Output CSVs: snake_case (e.g., clean_coal_panel.csv)
- Figures: fig_01.pdf, fig_02.pdf, ...
- Tables: tab_01.tex, tab_02.tex, ...
- Scripts: numbered prefix (00_, 01_, ..., 10_)

## Figure Standards
- **Format**: PDF vector (matplotlib savefig with bbox_inches='tight', dpi=300 for raster fallback)
- **Font**: Serif (Times New Roman or Computer Modern), minimum 8pt in figures
- **Color palette**: Seaborn 'colorblind' (colorblind-safe)
- **Width**: Full width = 6.5 inches; half width = 3.1 inches
- **Background**: White, no grid unless essential for reading
- **Axes**: Always labeled with units; no redundant titles if caption covers it
- **Legend**: Outside plot area or upper-right, no box frame

## Table Standards
- **Style**: booktabs (toprule, midrule, bottomrule) -- no vertical lines
- **Numbers**: Right-aligned, decimal-aligned where possible (siunitx S column)
- **Significance**: * p<0.10, ** p<0.05, *** p<0.01
- **Notes**: Below table, explaining abbreviations, data sources, and sample size
- **Large tables**: Use pdflscape for landscape; longtable for multi-page in appendix

## Citation Management
- **System**: BibTeX with natbib (authoryear)
- **Style**: elsarticle-harv (Elsevier Harvard) or apalike fallback
- **In-text**: \citet{} for textual, \citep{} for parenthetical
- **File**: references.bib in Paper root

## Decision Log Protocol
All methodological choices recorded in decisions/decision_log.md:
- Date | Decision | Alternatives | Rationale | Impact

## Quality Checklist (per section)
- [ ] All numbers cross-referenced to source data
- [ ] All equations numbered and referenced in text
- [ ] All figures have descriptive captions with data source note
- [ ] All tables have notes explaining abbreviations
- [ ] All claims supported by data or citations
- [ ] Robustness check exists for every key result
- [ ] No orphan figures/tables (all referenced in text)

## Scenario Parameters
| Scenario | Coal Price 2030 | Coal Price 2050 | Carbon Price 2030 | Probability |
|----------|----------------|-----------------|-------------------|-------------|
| BAU      | $120/t         | $85/t           | $10/tCO2          | 0.30        |
| 2C Paris | $90/t          | $35/t           | $50/tCO2          | 0.40        |
| 1.5C NZE | $70/t          | $15/t           | $130/tCO2         | 0.30        |

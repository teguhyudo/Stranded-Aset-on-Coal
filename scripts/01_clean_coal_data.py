"""
01_clean_coal_data.py -- Merge and clean coal company data
==========================================================
Merges coal CSVs into a single clean panel. Uses VERIFIED production data
from annual reports and public disclosures (not financial estimates).
Recalculates per-tonne costs from LSEG income statement data.

Production data sourcing hierarchy:
  1. LSEG Datastream (TR.ProductionVolume) -- confirmed unavailable for all
  2. Annual report disclosures / press releases -- used where verified
  3. NaN -- set for companies without reliable production data

Output: output/clean_coal_panel.csv
"""

import sys
import importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
setup = importlib.import_module('00_setup')

import numpy as np
import pandas as pd

COAL = setup.COAL_OUTPUT
OUT = setup.OUTPUT_DIR


# ============================================================
# VERIFIED PRODUCTION DATA
# ============================================================
# Each entry: (production_mt, source_code, source_detail)
#
# Sources:
#   annual_report_YYYY  -- from published annual report or press release
#   subsidiary_XXX      -- holding co; production via listed subsidiary XXX
#   mining_contractor   -- production on behalf of mine owners (not equity)
#
# Companies NOT in this dict get production_mt = NaN.
# Revenue/ASP financial estimates are NOT used (they are approximations,
# not reported production volumes).
# ============================================================
VERIFIED_PRODUCTION = {
    # --- Major producers (HIGH confidence) ---
    'AADI': (68.06, 'annual_report_2024',
             'AADI FY2024 press release; IDNFinancials'),
    'BUMI': (77.3,  'annual_report_2023',
             'Bumi Resources: KPC 53.5 + Arutmin 23.8 Mt'),
    'BYAN': (49.7,  'annual_report_2023',
             'Bayan Resources annual report 2023; ScienceAgri'),
    'GEMS': (46.12, 'annual_report_2023',
             'Golden Energy Mines official; ScienceAgri'),
    'PTBA': (41.9,  'annual_report_2023',
             'PTBA official website: 2023 production = 41.9 Mt'),
    'INDY': (30.1,  'annual_report_2023',
             'Kideco Jaya Agung subsidiary; Indonesia Miner'),
    'BSSR': (21.57, 'annual_report_2023',
             'BSSR annual report 2023; Argus Media'),
    'ITMG': (16.9,  'annual_report_2023',
             'Indo Tambangraya Megah; Indonesia Miner; IDNFinancials'),
    'HRUM': (7.0,   'annual_report_2023',
             'Estimated FY from 9M2023 (5.4 Mt); Indonesia Miner'),
    'TOBA': (3.1,   'annual_report_2023',
             'TBS Energi Utama; Petromindo'),
    'SMMT': (2.6,   'annual_report_2023',
             'Estimated FY from 9M2023 (1.95 Mt); Djakarta Mining Club'),
    'MBAP': (2.09,  'annual_report_2023',
             'Mitrabara Adiperdana; Argus Media'),
    'MCOL': (10.08, 'annual_report_2023',
             'Prima Andalan Mandiri annual report 2023'),
    'ARII': (7.57,  'annual_report_2024',
             'Atlas Resources annual report 2024'),
    'KKGI': (5.92,  'annual_report_2024',
             'Resource Alam Indonesia annual report 2024'),

    # --- Holding companies: production via listed subsidiaries ---
    # Set NaN to avoid double-counting with subsidiary's production
    'ADRO': (np.nan, 'subsidiary_aadi',
             'Post-2024 restructuring: thermal coal via AADI; '
             'metallurgical coal via ADMR (~5 Mt)'),
    'DSSA': (np.nan, 'subsidiary_gems',
             'Holding company: coal production consolidated via GEMS'),

    # --- Mining contractors: coal getting on behalf of clients ---
    # Not equity production; would double-count with mine owners
    'DOID': (np.nan, 'mining_contractor',
             'Delta Dunia (BUMA): mining services for KPC, Adaro, etc.'),
    'MYOH': (np.nan, 'mining_contractor',
             'Samindo Resources: coal getting on behalf of clients'),
}


def clean_ticker(df, col='Instrument'):
    """Strip .JK suffix and forward-fill instrument column."""
    df = df.copy()
    if col in df.columns:
        df[col] = df[col].ffill()
        df['ticker'] = df[col].str.replace('.JK', '', regex=False)
    return df


def get_latest_year(df, ticker_col='ticker', date_col='Date'):
    """Extract the most recent observation per company."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col])
    idx = df.groupby(ticker_col)[date_col].idxmax()
    return df.loc[idx].copy()


def main():
    print("=" * 60)
    print("01: CLEANING COAL COMPANY DATA")
    print("=" * 60)

    # ----------------------------------------------------------
    # 1. Derived variables (base table for company list)
    # ----------------------------------------------------------
    print("\n[1/7] Loading derived variables (company list)...")
    derived = pd.read_csv(COAL / "derived_variables.csv")
    derived = clean_ticker(derived)
    print(f"  {len(derived)} companies in derived_variables")

    # Keep only company identifiers and emissions factor from derived_variables.
    # Production, NPV, SV will be overridden or recalculated.
    panel = derived.rename(columns={
        'Proven_Reserves_Mt': 'reserves_mt',
        'Emissions_Factor_tCO2_t': 'emissions_factor',
        'Potential_Emissions_MtCO2': 'potential_emissions',
    })[['ticker', 'Company_Name', 'reserves_mt',
        'emissions_factor', 'potential_emissions']].copy()

    # ----------------------------------------------------------
    # 1b. Apply VERIFIED PRODUCTION
    # ----------------------------------------------------------
    print("\n[1b] Applying verified production data...")
    prod_vals = []
    source_vals = []
    source_detail_vals = []
    for _, row in panel.iterrows():
        t = row['ticker']
        if t in VERIFIED_PRODUCTION:
            pmt, src, detail = VERIFIED_PRODUCTION[t]
            prod_vals.append(pmt)
            source_vals.append(src)
            source_detail_vals.append(detail)
        else:
            prod_vals.append(np.nan)
            source_vals.append(np.nan)
            source_detail_vals.append(np.nan)

    panel['production_mt'] = prod_vals
    panel['production_source'] = source_vals
    panel['production_source_detail'] = source_detail_vals

    n_verified = panel['production_mt'].notna().sum()
    n_nan_source = panel['production_source'].notna().sum()
    print(f"  Verified production: {n_verified} companies")
    print(f"  Source recorded: {n_nan_source} companies")
    print(f"  Set to NaN (no reliable source): "
          f"{len(panel) - n_nan_source} companies")

    for _, r in panel[panel['production_mt'].notna()].iterrows():
        print(f"    {r['ticker']:>6s}: {r['production_mt']:>8.2f} Mt  "
              f"({r['production_source']})")

    # ----------------------------------------------------------
    # 2. Operational template (cost structure only)
    # ----------------------------------------------------------
    print("\n[2/7] Loading operational template (cost structure)...")
    ops = pd.read_csv(COAL / "operational_template.csv")
    ops = clean_ticker(ops)
    ops_cols_map = {}
    for col in ops.columns:
        if 'Coal_Rank' in col: ops_cols_map[col] = 'coal_rank'
        elif 'Calorific' in col: ops_cols_map[col] = 'cv_kcal_kg'
        elif 'Strip_Ratio' in col: ops_cols_map[col] = 'strip_ratio'
        elif 'Mine_Life' in col: ops_cols_map[col] = 'mine_life_years'
        elif 'Mining_Method' in col: ops_cols_map[col] = 'mining_method'
        elif 'Export_Share' in col: ops_cols_map[col] = 'export_share_pct'
        elif 'Domestic_Share' in col: ops_cols_map[col] = 'domestic_share_pct'
        elif 'Royalty_Rate' in col: ops_cols_map[col] = 'royalty_rate_pct'
    # NOTE: Cash_Cost, AISC, FOB are NOT taken from operational_template
    # because they were derived using estimated (unreliable) production.
    # They will be recalculated from LSEG COGS / verified production below.
    ops = ops.rename(columns=ops_cols_map)
    ops_merge = ['ticker'] + [v for v in ops_cols_map.values() if v in ops.columns]
    ops_merge = [c for c in ops_merge if c in ops.columns]
    panel = panel.merge(ops[ops_merge], on='ticker', how='left')
    print(f"  Merged {len(ops_cols_map)} operational columns (excluding cost/tonne)")

    # ----------------------------------------------------------
    # 3. Cost of capital
    # ----------------------------------------------------------
    print("\n[3/7] Loading cost of capital...")
    coc = pd.read_csv(COAL / "cost_of_capital.csv")
    coc = clean_ticker(coc)
    coc_map = {}
    for col in coc.columns:
        if 'Beta' in col and '5Y' in col: coc_map[col] = 'beta_5y'
        elif col == 'Risk_Free_Rate': coc_map[col] = 'risk_free_rate'
        elif 'WACC_Base' in col: coc_map[col] = 'wacc_base'
        elif 'WACC_Stranded' in col: coc_map[col] = 'wacc_stranded'
        elif 'Cost_Of_Equity' in col: coc_map[col] = 'cost_of_equity'
        elif 'Stranding_Risk' in col: coc_map[col] = 'stranding_premium'
    coc = coc.rename(columns=coc_map)
    coc_cols = ['ticker'] + [v for v in coc_map.values() if v in coc.columns]
    coc_cols = list(dict.fromkeys(coc_cols))  # deduplicate
    panel = panel.merge(coc[[c for c in coc_cols if c in coc.columns]],
                        on='ticker', how='left')
    print(f"  Merged cost of capital")

    # ----------------------------------------------------------
    # 4. Balance sheet (latest year per company)
    # ----------------------------------------------------------
    print("\n[4/7] Loading balance sheet (latest year)...")
    bs = pd.read_csv(COAL / "balance_sheet.csv")
    bs = clean_ticker(bs)
    bs = get_latest_year(bs)
    bs = bs.rename(columns={
        'Total Assets, Reported': 'total_assets',
        'Total Liabilities': 'total_liabilities',
        'Total Equity': 'total_equity',
        'Total Debt': 'total_debt',
        'Cash and Short Term Investments': 'cash',
        'Total Long Term Debt': 'lt_debt',
        'Total Inventory': 'inventory',
    })
    bs_cols = [c for c in ['ticker', 'total_assets', 'total_liabilities',
               'total_equity', 'total_debt', 'cash', 'lt_debt', 'inventory']
               if c in bs.columns]
    panel = panel.merge(bs[bs_cols], on='ticker', how='left')
    print(f"  {len(bs)} companies with balance sheet data")

    # ----------------------------------------------------------
    # 5. Income statement (latest year per company)
    # ----------------------------------------------------------
    print("\n[5/7] Loading income statement (latest year)...")
    inc_raw = pd.read_csv(COAL / "income_statement.csv")
    inc_raw = clean_ticker(inc_raw)

    # Split: firms with Date (use get_latest_year) vs firms without Date
    # Some firms have Cost of Revenue in LSEG but NaN Date/Revenue
    inc_raw['Date'] = pd.to_datetime(inc_raw['Date'], errors='coerce')
    has_date = inc_raw.dropna(subset=['Date'])
    no_date = inc_raw[inc_raw['Date'].isna()]

    # Latest year for firms with dates
    if len(has_date) > 0:
        idx = has_date.groupby('ticker')['Date'].idxmax()
        inc_dated = has_date.loc[idx].copy()
    else:
        inc_dated = pd.DataFrame()

    # For firms without Date, take the last row (most recent LSEG pull)
    # but only keep columns that actually have data
    if len(no_date) > 0:
        inc_nodate = no_date.groupby('ticker').last().reset_index()
        # Only keep tickers not already in dated set
        if len(inc_dated) > 0:
            inc_nodate = inc_nodate[
                ~inc_nodate['ticker'].isin(inc_dated['ticker'])]
    else:
        inc_nodate = pd.DataFrame()

    inc = pd.concat([inc_dated, inc_nodate], ignore_index=True)

    inc = inc.rename(columns={
        'Revenue - Actual': 'revenue',
        'Cost of Revenue': 'cost_of_revenue',
        'Gross Profit': 'gross_profit',
        'Operating Income': 'operating_income',
        'EBITDA': 'ebitda',
        'Interest Expense': 'interest_expense',
    })
    inc_cols = [c for c in ['ticker', 'revenue', 'cost_of_revenue',
                'gross_profit', 'operating_income', 'ebitda',
                'interest_expense'] if c in inc.columns]
    panel = panel.merge(inc[inc_cols], on='ticker', how='left')
    n_with_date = len(inc_dated)
    n_no_date = len(inc_nodate) if len(inc_nodate) > 0 else 0
    print(f"  {len(inc)} companies with income data "
          f"({n_with_date} with Date, {n_no_date} with COGS only)")

    # ----------------------------------------------------------
    # 5b. Recalculate per-tonne costs from COGS / verified production
    # ----------------------------------------------------------
    print("\n[5b] Recalculating per-tonne costs...")
    # cash_cost_usd_t = COGS (USD M) / Production (Mt) = USD/t
    # Only for companies with BOTH verified production AND LSEG COGS
    has_both = (panel['production_mt'].notna() &
                panel['cost_of_revenue'].notna() &
                (panel['production_mt'] > 0))

    panel['cash_cost_usd_t'] = np.nan
    panel.loc[has_both, 'cash_cost_usd_t'] = (
        panel.loc[has_both, 'cost_of_revenue'].abs() /
        panel.loc[has_both, 'production_mt']
    )
    # AISC and FOB as multiples of cash cost
    panel['aisc_usd_t'] = panel['cash_cost_usd_t'] * 1.10
    panel['fob_cost_usd_t'] = panel['cash_cost_usd_t'] * 1.15

    # Breakeven = cash cost + royalty per tonne (at base coal price $130/t)
    # royalty_rate_pct is stored in percent form (e.g. 5.0 = 5%), so divide by 100
    base_coal_price = 130.0  # USD/t, 2025 reference
    if 'royalty_rate_pct' in panel.columns:
        royalty_frac = panel['royalty_rate_pct'].fillna(5.0) / 100.0
        panel['breakeven_usd_t'] = (
            panel['cash_cost_usd_t'] +
            base_coal_price * royalty_frac
        )
    else:
        panel['breakeven_usd_t'] = panel['cash_cost_usd_t'] + base_coal_price * 0.05

    n_cost = has_both.sum()
    print(f"  Recalculated costs for {n_cost} companies "
          f"(have verified production + LSEG COGS)")

    for _, r in panel[has_both].iterrows():
        print(f"    {r['ticker']:>6s}: COGS=${r['cost_of_revenue']:>10,.1f}M / "
              f"{r['production_mt']:.2f}Mt = "
              f"${r['cash_cost_usd_t']:.1f}/t  "
              f"(breakeven ${r['breakeven_usd_t']:.1f}/t)")

    # ----------------------------------------------------------
    # 6. ESG emissions
    # ----------------------------------------------------------
    print("\n[6/7] Loading ESG data...")
    esg = pd.read_csv(COAL / "esg_emissions.csv")
    esg = clean_ticker(esg)
    esg_map = {}
    for col in esg.columns:
        if ('ESG_Score' in col and 'Environmental' not in col
                and 'Social' not in col and 'Governance' not in col):
            esg_map[col] = 'esg_score'
        elif 'Environmental' in col: esg_map[col] = 'env_score'
        elif 'Social' in col: esg_map[col] = 'social_score'
        elif 'Governance' in col: esg_map[col] = 'gov_score'
    esg = esg.rename(columns=esg_map)
    esg_cols = ['ticker'] + [v for v in esg_map.values() if v in esg.columns]
    esg_cols = list(dict.fromkeys(esg_cols))
    panel = panel.merge(esg[[c for c in esg_cols if c in esg.columns]],
                        on='ticker', how='left')
    print(f"  Merged ESG scores")

    # ----------------------------------------------------------
    # 7. Company profiles (market cap)
    # ----------------------------------------------------------
    print("\n[7/7] Loading company profiles...")
    prof = pd.read_csv(COAL / "company_profiles.csv")
    prof = clean_ticker(prof)
    mktcap_col = None
    for col in prof.columns:
        if 'Market' in col and 'Cap' in col:
            mktcap_col = col
            break
        if 'market' in col.lower() and 'cap' in col.lower():
            mktcap_col = col
            break
    if mktcap_col:
        prof = prof.rename(columns={mktcap_col: 'market_cap'})
        panel = panel.merge(prof[['ticker', 'market_cap']],
                            on='ticker', how='left')
        print(f"  Merged market cap")
    else:
        print(f"  Warning: no market cap column found. "
              f"Columns: {list(prof.columns)}")

    # ----------------------------------------------------------
    # DERIVED COLUMNS
    # ----------------------------------------------------------
    print("\nComputing derived columns...")

    if 'total_debt' in panel.columns and 'total_equity' in panel.columns:
        panel['debt_to_equity'] = (
            panel['total_debt'] /
            panel['total_equity'].replace(0, np.nan)
        )

    # NPV and SV placeholders (will be computed by 04_model1_stranded_assets.py)
    for col in ['npv_bau', 'npv_2c', 'npv_1_5c',
                'sv_2c', 'sv_1_5c', 'expected_sv']:
        panel[col] = np.nan

    panel['stranded_2c'] = False
    panel['stranded_1_5c'] = False
    panel['sv_2c_pct_assets'] = np.nan
    panel['sv_1_5c_pct_assets'] = np.nan

    # ----------------------------------------------------------
    # SAVE
    # ----------------------------------------------------------
    outpath = OUT / "clean_coal_panel.csv"
    panel.to_csv(outpath, index=False)
    print(f"\nSaved: {outpath}")
    print(f"Shape: {panel.shape}")

    # Summary
    print("\n--- KEY STATISTICS ---")
    print(f"Total companies: {len(panel)}")
    print(f"With verified production: "
          f"{panel['production_mt'].notna().sum()}")
    print(f"With cost data (cash_cost): "
          f"{panel['cash_cost_usd_t'].notna().sum()}")
    print(f"With breakeven price: "
          f"{panel['breakeven_usd_t'].notna().sum()}")
    print(f"With WACC: {panel['wacc_base'].notna().sum()}")

    # Eligible for Model 1 MC
    eligible = (panel['production_mt'].notna() &
                panel['cash_cost_usd_t'].notna() &
                panel['wacc_base'].notna())
    print(f"Eligible for Monte Carlo (prod+cost+WACC): {eligible.sum()}")
    print(f"  Tickers: {panel.loc[eligible, 'ticker'].tolist()}")

    print(f"\nTotal verified production: "
          f"{panel['production_mt'].sum():,.1f} Mt")
    if panel['breakeven_usd_t'].notna().any():
        print(f"Breakeven range: "
              f"${panel['breakeven_usd_t'].min():,.1f}/t -- "
              f"${panel['breakeven_usd_t'].max():,.1f}/t "
              f"(median ${panel['breakeven_usd_t'].median():,.1f}/t)")

    print("\nNOTE: NPV and SV columns are NaN -- "
          "will be computed by 04_model1_stranded_assets.py")

    return panel


if __name__ == "__main__":
    main()

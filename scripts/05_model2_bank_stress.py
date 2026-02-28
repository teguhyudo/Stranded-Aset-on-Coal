"""
05_model2_bank_stress.py -- Model 2: Banking Sector Climate Stress Test
========================================================================
Estimates credit losses to Indonesian banks from coal asset stranding
under BAU, 2C, and 1.5C climate scenarios.

Steps:
  1. Determine coal company default/distress status per scenario
  2. Calculate direct credit losses from bank-coal exposures
  3. Calculate indirect losses from broader mining portfolios
  4. Compute capital adequacy (CAR) and profitability impacts
  5. Flag banks breaching OJK minimum CAR and D-SIB buffers

Inputs:
  - clean_coal_panel.csv
  - clean_bank_panel.csv
  - exposure_matrix.csv

Outputs:
  - coal_default_status.csv
  - bank_stress_results.csv
  - stress_test_summary.csv
"""

import sys, importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
setup = importlib.import_module('00_setup')

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================
# CONSTANTS
# ============================================================
OUTPUT_DIR      = setup.OUTPUT_DIR
SCENARIOS       = setup.SCENARIOS
CORPORATE_TAX   = setup.CORPORATE_TAX_RATE
LGD_GENERIC     = setup.LGD_GENERIC       # 0.45
OJK_CAR_MIN     = setup.OJK_CAR_MINIMUM   # 0.08
DSIB_CAR_BUFFER = setup.DSIB_CAR_BUFFER    # 0.105

# Scenario-specific NPL shock for indirect mining loans
DELTA_NPL = {
    'BAU':  0.005,   # 0.5 pp
    '2C':   0.05,    # 5 pp
    '1.5C': 0.15,    # 15 pp
}

SCENARIO_LABELS = {k: v['label'] for k, v in SCENARIOS.items()}

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("MODEL 2: BANKING SECTOR CLIMATE STRESS TEST")
print("=" * 70)

# --- Coal company data ---
coal = pd.read_csv(OUTPUT_DIR / 'clean_coal_panel.csv')
print(f"\nLoaded coal panel: {len(coal)} companies")

# --- Bank data (use most recent year per bank) ---
bank_raw = pd.read_csv(OUTPUT_DIR / 'clean_bank_panel.csv')
bank = (bank_raw
        .sort_values('year', ascending=False)
        .drop_duplicates(subset='ticker', keep='first')
        .copy())
print(f"Loaded bank panel: {len(bank)} banks (latest year per bank)")

# --- Exposure matrix (bank x coal, USD millions) ---
exposure = pd.read_csv(OUTPUT_DIR / 'exposure_matrix.csv', index_col=0)
# Fill NaN with 0 (missing exposures = no exposure)
exposure = exposure.fillna(0.0)
# Remove TOTAL column if present; we will recompute sums
if 'TOTAL' in exposure.columns:
    exposure = exposure.drop(columns='TOTAL')
# Remove UNATTRIBUTED row for bank-level analysis
if 'UNATTRIBUTED' in exposure.index:
    exposure = exposure.drop(index='UNATTRIBUTED')

print(f"Loaded exposure matrix: {exposure.shape[0]} banks x {exposure.shape[1]} coal companies")

# Coal tickers present in both the coal panel and the exposure matrix
coal_tickers_in_exposure = [c for c in exposure.columns if c in coal['ticker'].values]
print(f"Coal companies with both NPV data and bank exposures: "
      f"{len(coal_tickers_in_exposure)}")

# ============================================================
# STEP 1: COAL COMPANY DEFAULT STATUS
# ============================================================
print("\n" + "-" * 70)
print("STEP 1: Coal Company Default / Distress Classification")
print("-" * 70)

npv_cols  = {'BAU': 'npv_bau', '2C': 'npv_2c', '1.5C': 'npv_1_5c'}
sv_cols   = {'2C': 'sv_2c', '1.5C': 'sv_1_5c'}  # No stranded value under BAU

records = []
for _, row in coal.iterrows():
    ticker = row['ticker']
    total_debt   = row.get('total_debt', np.nan)
    total_equity = row.get('total_equity', np.nan)
    total_assets = row.get('total_assets', np.nan)

    # Sanitise
    total_debt   = total_debt   if pd.notna(total_debt)   else 0.0
    total_equity = total_equity if pd.notna(total_equity) else 0.0
    total_assets = total_assets if pd.notna(total_assets) else 0.0

    for scen in ['BAU', '2C', '1.5C']:
        npv_val = row.get(npv_cols[scen], np.nan)
        sv_val  = row.get(sv_cols.get(scen, None), np.nan) if scen in sv_cols else 0.0
        sv_val  = sv_val if pd.notna(sv_val) else 0.0

        if pd.isna(npv_val):
            # No NPV computed -- treat as performing (conservative)
            records.append({
                'coal_ticker': ticker, 'scenario': scen,
                'status': 'NO_DATA', 'lgd': 0.0,
                'npv': np.nan, 'stranded_value': sv_val,
            })
            continue

        if npv_val < 0:
            # DEFAULT: negative NPV means project is unviable
            lgd = min(1.0, abs(npv_val) / max(total_debt, 1.0))
            status = 'DEFAULT'
        elif sv_val > 0.5 * total_equity and total_equity > 0:
            # DISTRESSED: positive NPV but large stranded value
            lgd = 0.3 * sv_val / max(total_assets, 1.0)
            status = 'DISTRESSED'
        else:
            # PERFORMING
            lgd = 0.0
            status = 'PERFORMING'

        records.append({
            'coal_ticker': ticker, 'scenario': scen,
            'status': status, 'lgd': lgd,
            'npv': npv_val, 'stranded_value': sv_val,
        })

coal_status = pd.DataFrame(records)

# Print summary
print("\nDefault/Distress counts by scenario:")
for scen in ['BAU', '2C', '1.5C']:
    sub = coal_status[coal_status['scenario'] == scen]
    counts = sub['status'].value_counts()
    print(f"  {scen:5s}: {dict(counts)}")

# Save
coal_status.to_csv(OUTPUT_DIR / 'coal_default_status.csv', index=False)
print(f"\nSaved: coal_default_status.csv ({len(coal_status)} rows)")

# Build quick lookup: (coal_ticker, scenario) -> lgd
lgd_lookup = coal_status.set_index(['coal_ticker', 'scenario'])['lgd'].to_dict()

# ============================================================
# STEP 2: DIRECT CREDIT LOSSES PER BANK
# ============================================================
print("\n" + "-" * 70)
print("STEP 2: Direct Credit Losses (bank-coal bipartite network)")
print("-" * 70)

direct_loss_records = []
for bank_ticker in exposure.index:
    for scen in ['BAU', '2C', '1.5C']:
        loss = 0.0
        for coal_ticker in exposure.columns:
            exp_val = exposure.loc[bank_ticker, coal_ticker]
            if exp_val <= 0:
                continue
            lgd = lgd_lookup.get((coal_ticker, scen), 0.0)
            loss += exp_val * lgd
        direct_loss_records.append({
            'bank_ticker': bank_ticker,
            'scenario': scen,
            'direct_loss': loss,
        })

direct_losses = pd.DataFrame(direct_loss_records)
print(f"Computed direct losses for {exposure.shape[0]} banks x 3 scenarios")

# ============================================================
# STEP 3: INDIRECT CREDIT LOSSES (broader mining portfolio)
# ============================================================
print("\n" + "-" * 70)
print("STEP 3: Indirect Credit Losses (residual mining portfolio)")
print("-" * 70)

# Total direct exposure per bank from the exposure matrix
bank_total_direct_exposure = exposure.sum(axis=1)

indirect_loss_records = []
for bank_ticker in exposure.index:
    bank_row = bank[bank['ticker'] == bank_ticker]
    if bank_row.empty:
        # Bank not in panel -- no indirect loss computable
        for scen in ['BAU', '2C', '1.5C']:
            indirect_loss_records.append({
                'bank_ticker': bank_ticker, 'scenario': scen,
                'indirect_loss': 0.0,
                'indirect_mining_exposure': 0.0,
            })
        continue

    bank_row = bank_row.iloc[0]
    mining_loans = bank_row.get('mining_loans_usd_m', np.nan)
    mining_loans = mining_loans if pd.notna(mining_loans) else 0.0

    # Residual mining exposure not captured in bipartite network
    direct_total = bank_total_direct_exposure.get(bank_ticker, 0.0)
    indirect_mining = max(0.0, mining_loans - direct_total)

    for scen in ['BAU', '2C', '1.5C']:
        delta_npl = DELTA_NPL[scen]
        loss = indirect_mining * delta_npl * LGD_GENERIC
        indirect_loss_records.append({
            'bank_ticker': bank_ticker, 'scenario': scen,
            'indirect_loss': loss,
            'indirect_mining_exposure': indirect_mining,
        })

indirect_losses = pd.DataFrame(indirect_loss_records)

# Show banks with material indirect exposure
banks_with_indirect = indirect_losses[
    indirect_losses['indirect_mining_exposure'] > 0
]['bank_ticker'].unique()
print(f"Banks with residual mining exposure beyond bipartite network: "
      f"{len(banks_with_indirect)}")

# ============================================================
# STEP 4: TOTAL LOSS & CAPITAL IMPACT
# ============================================================
print("\n" + "-" * 70)
print("STEP 4: Total Losses, CAR Impact, and Profitability Impact")
print("-" * 70)

# Merge direct + indirect
stress = direct_losses.merge(
    indirect_losses[['bank_ticker', 'scenario', 'indirect_loss',
                     'indirect_mining_exposure']],
    on=['bank_ticker', 'scenario'],
    how='left',
)
stress['indirect_loss'] = stress['indirect_loss'].fillna(0.0)
stress['total_loss'] = stress['direct_loss'] + stress['indirect_loss']

# Merge bank financials
ckpn_cols = ['loan_allowance_usd_m', 'provision_expense_usd_m']
avail_ckpn = [c for c in ckpn_cols if c in bank.columns]
bank_financials = bank[['ticker', 'total_assets_usd_m', 'total_equity_usd_m',
                         'gross_loans_usd_m', 'net_income_usd_m', 'roa', 'roe',
                         'nim', 'npl_gross', 'market_cap_usd_m',
                         'size_category', 'mining_loans_usd_m',
                         'tier1_ratio', 'total_car',
                         'reported_car', 'car_source'] + avail_ckpn].copy()
bank_financials = bank_financials.rename(columns={'ticker': 'bank_ticker'})

stress = stress.merge(bank_financials, on='bank_ticker', how='left')

# --- Estimate RWA ---
# RWA ~ gross_loans / 0.65 (loans are ~65% of total assets, 100% risk weight)
# Fallback: total_assets * 0.8
stress['rwa'] = np.where(
    stress['gross_loans_usd_m'].notna() & (stress['gross_loans_usd_m'] > 0),
    stress['gross_loans_usd_m'] / 0.65,
    stress['total_assets_usd_m'] * 0.80
)

# --- CAR Impact ---
# Use reported_car from public sources (annual reports, OJK, LSEG Tier 1).
# Fall back to equity/RWA proxy only if no reported CAR is available.
stress['CAR_before'] = np.where(
    stress['reported_car'].notna() & (stress['reported_car'] > 0),
    stress['reported_car'],
    stress['total_equity_usd_m'] / stress['rwa']
)
# Propagate car_source: if using the proxy, mark it
stress['car_source'] = np.where(
    stress['reported_car'].notna() & (stress['reported_car'] > 0),
    stress['car_source'],
    'equity_rwa_proxy'
)

# --- CKPN Buffer ---
# If loan_allowance data is available, compute net loss after CKPN absorption.
# Banks with existing CKPN buffers can absorb some credit losses before capital
# is impacted. For banks without data, use industry-average CKPN-to-loans ratio.
if 'loan_allowance_usd_m' in stress.columns:
    # Industry-average CKPN-to-loans ratio for banks missing data (typical ~2.5%)
    known = stress[stress['loan_allowance_usd_m'].notna() & (stress['loan_allowance_usd_m'] > 0)]
    if len(known) > 0 and known['gross_loans_usd_m'].sum() > 0:
        avg_ckpn_ratio = (known['loan_allowance_usd_m'].sum()
                          / known['gross_loans_usd_m'].sum())
    else:
        avg_ckpn_ratio = 0.025  # conservative default
    stress['ckpn_buffer'] = np.where(
        stress['loan_allowance_usd_m'].notna() & (stress['loan_allowance_usd_m'] > 0),
        stress['loan_allowance_usd_m'],
        stress['gross_loans_usd_m'].fillna(0) * avg_ckpn_ratio
    )
    stress['loss_after_ckpn'] = np.maximum(0, stress['total_loss'] - stress['ckpn_buffer'])
    print(f"  CKPN buffer applied. Avg ratio: {avg_ckpn_ratio:.4f}")
    print(f"  Total loss before CKPN: ${stress['total_loss'].sum():,.1f}M")
    print(f"  Total loss after CKPN:  ${stress['loss_after_ckpn'].sum():,.1f}M")
else:
    stress['ckpn_buffer'] = 0.0
    stress['loss_after_ckpn'] = stress['total_loss']

# CAR_after = CAR_before - (total_loss / RWA)
# Losses reduce equity (numerator of CAR), so impact = loss / RWA
# Report both with and without CKPN buffer
stress['CAR_impact'] = stress['total_loss'] / stress['rwa']
stress['CAR_after'] = stress['CAR_before'] - stress['CAR_impact']
stress['CAR_impact_after_ckpn'] = stress['loss_after_ckpn'] / stress['rwa']
stress['CAR_after_with_ckpn'] = stress['CAR_before'] - stress['CAR_impact_after_ckpn']

# --- Breach flags ---
stress['car_breach_ojk'] = stress['CAR_after'] < OJK_CAR_MIN
stress['car_breach_dsib'] = (
    (stress['CAR_after'] < DSIB_CAR_BUFFER) &
    (stress['size_category'] == 'DSIB')
)

# --- ROA Impact ---
stress['ROA_before'] = stress['roa']
stress['ROA_after'] = np.where(
    stress['total_assets_usd_m'].notna() & (stress['total_assets_usd_m'] > 0),
    (stress['net_income_usd_m'].fillna(0) - stress['total_loss']) / stress['total_assets_usd_m'],
    np.nan
)
stress['ROA_impact'] = stress['ROA_before'] - stress['ROA_after']

# --- Profitability Impact (Step 5) ---
stress['profit_impact_pct'] = np.where(
    stress['net_income_usd_m'].notna() & (stress['net_income_usd_m'] > 0),
    (stress['total_loss'] / stress['net_income_usd_m']) * 100.0,
    np.nan
)

# Loss as % of equity
stress['loss_pct_equity'] = np.where(
    stress['total_equity_usd_m'].notna() & (stress['total_equity_usd_m'] > 0),
    (stress['total_loss'] / stress['total_equity_usd_m']) * 100.0,
    np.nan
)

# ============================================================
# SAVE BANK STRESS RESULTS
# ============================================================
output_cols = [
    'bank_ticker', 'scenario', 'size_category',
    'direct_loss', 'indirect_loss', 'total_loss',
    'ckpn_buffer', 'loss_after_ckpn',
    'indirect_mining_exposure',
    'total_equity_usd_m', 'total_assets_usd_m', 'gross_loans_usd_m',
    'mining_loans_usd_m', 'net_income_usd_m', 'rwa',
    'CAR_before', 'CAR_after', 'CAR_impact',
    'CAR_impact_after_ckpn', 'CAR_after_with_ckpn', 'car_source',
    'ROA_before', 'ROA_after', 'ROA_impact',
    'car_breach_ojk', 'car_breach_dsib',
    'profit_impact_pct', 'loss_pct_equity',
]
# Only keep columns that actually exist
output_cols = [c for c in output_cols if c in stress.columns]
stress_out = stress[output_cols].copy()
stress_out.to_csv(OUTPUT_DIR / 'bank_stress_results.csv', index=False)
print(f"\nSaved: bank_stress_results.csv ({len(stress_out)} rows)")

# ============================================================
# STEP 5: AGGREGATE SUMMARY
# ============================================================
print("\n" + "-" * 70)
print("STEP 5: Aggregate Stress Test Summary")
print("-" * 70)

summary_records = []
for scen in ['BAU', '2C', '1.5C']:
    s = stress[stress['scenario'] == scen]
    coal_s = coal_status[coal_status['scenario'] == scen]

    n_default   = (coal_s['status'] == 'DEFAULT').sum()
    n_distress  = (coal_s['status'] == 'DISTRESSED').sum()
    n_performing = (coal_s['status'] == 'PERFORMING').sum()

    total_direct   = s['direct_loss'].sum()
    total_indirect = s['indirect_loss'].sum()
    total_losses   = s['total_loss'].sum()
    total_equity   = s['total_equity_usd_m'].sum()

    n_ojk_breach  = s['car_breach_ojk'].sum()
    n_dsib_breach = s['car_breach_dsib'].sum()

    # Equity at risk: sum of equity for banks that breach OJK CAR
    equity_at_risk = s.loc[s['car_breach_ojk'], 'total_equity_usd_m'].sum()

    # Average CAR impact (across banks with data)
    avg_car_impact = s['CAR_impact'].mean()
    max_car_impact = s['CAR_impact'].max()

    # Average profit impact
    avg_profit_impact = s['profit_impact_pct'].mean()
    max_profit_impact = s['profit_impact_pct'].max()

    # Losses as % of system equity
    loss_pct_system_equity = (total_losses / total_equity * 100
                              if total_equity > 0 else np.nan)

    summary_records.append({
        'scenario': scen,
        'scenario_label': SCENARIO_LABELS[scen],
        'n_coal_default': n_default,
        'n_coal_distressed': n_distress,
        'n_coal_performing': n_performing,
        'total_direct_loss_usd_m': round(total_direct, 2),
        'total_indirect_loss_usd_m': round(total_indirect, 2),
        'total_loss_usd_m': round(total_losses, 2),
        'total_bank_equity_usd_m': round(total_equity, 2),
        'loss_pct_system_equity': round(loss_pct_system_equity, 4),
        'n_banks_breach_ojk_car': int(n_ojk_breach),
        'n_banks_breach_dsib_buffer': int(n_dsib_breach),
        'equity_at_risk_usd_m': round(equity_at_risk, 2),
        'avg_car_impact_pp': round(avg_car_impact * 100, 4),
        'max_car_impact_pp': round(max_car_impact * 100, 4),
        'avg_profit_impact_pct': round(avg_profit_impact, 2)
                           if pd.notna(avg_profit_impact) else np.nan,
        'max_profit_impact_pct': round(max_profit_impact, 2)
                           if pd.notna(max_profit_impact) else np.nan,
    })

summary = pd.DataFrame(summary_records)
summary.to_csv(OUTPUT_DIR / 'stress_test_summary.csv', index=False)
print(f"Saved: stress_test_summary.csv ({len(summary)} rows)")

# ============================================================
# DETAILED RESULTS PRINTOUT
# ============================================================
print("\n" + "=" * 70)
print("STRESS TEST RESULTS")
print("=" * 70)

# --- Coal default summary ---
print("\n--- Coal Company Default Status ---")
for scen in ['BAU', '2C', '1.5C']:
    sub = coal_status[coal_status['scenario'] == scen]
    n_def  = (sub['status'] == 'DEFAULT').sum()
    n_dist = (sub['status'] == 'DISTRESSED').sum()
    n_perf = (sub['status'] == 'PERFORMING').sum()
    n_nodata = (sub['status'] == 'NO_DATA').sum()
    avg_lgd = sub.loc[sub['lgd'] > 0, 'lgd'].mean()
    avg_lgd_str = f"{avg_lgd:.2%}" if pd.notna(avg_lgd) else "n/a"
    print(f"  {scen:5s}: {n_def} default, {n_dist} distressed, "
          f"{n_perf} performing, {n_nodata} no data  |  avg LGD (non-zero): {avg_lgd_str}")

# --- Bank losses by scenario ---
print("\n--- Total Bank Losses by Scenario (USD millions) ---")
for scen in ['BAU', '2C', '1.5C']:
    row = summary[summary['scenario'] == scen].iloc[0]
    print(f"  {scen:5s}: Direct = ${row['total_direct_loss_usd_m']:,.1f}m  |  "
          f"Indirect = ${row['total_indirect_loss_usd_m']:,.1f}m  |  "
          f"TOTAL = ${row['total_loss_usd_m']:,.1f}m  "
          f"({row['loss_pct_system_equity']:.2f}% of system equity)")

# --- CAR breaches ---
print("\n--- Capital Adequacy Breaches ---")
for scen in ['BAU', '2C', '1.5C']:
    row = summary[summary['scenario'] == scen].iloc[0]
    print(f"  {scen:5s}: {row['n_banks_breach_ojk_car']} banks breach OJK minimum (8%), "
          f"{row['n_banks_breach_dsib_buffer']} D-SIBs breach buffer (10.5%)  |  "
          f"Avg CAR impact: {row['avg_car_impact_pp']:.2f} pp, "
          f"Max: {row['max_car_impact_pp']:.2f} pp")

# --- Top 5 most affected banks per scenario ---
print("\n--- Top 5 Most Affected Banks (by total loss) ---")
for scen in ['BAU', '2C', '1.5C']:
    s = stress[stress['scenario'] == scen].nlargest(5, 'total_loss')
    print(f"\n  {scen} ({SCENARIO_LABELS[scen]}):")
    print(f"  {'Bank':<8s}  {'Total Loss':>12s}  {'% Equity':>10s}  "
          f"{'% Net Inc':>10s}  {'CAR Before':>10s}  {'CAR After':>10s}  {'Breach':>7s}")
    print(f"  {'-'*8}  {'-'*12}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*7}")
    for _, r in s.iterrows():
        breach = ""
        if r.get('car_breach_ojk', False):
            breach = "OJK"
        elif r.get('car_breach_dsib', False):
            breach = "D-SIB"
        loss_eq = f"{r['loss_pct_equity']:.2f}%" if pd.notna(r.get('loss_pct_equity')) else "n/a"
        prof_imp = f"{r['profit_impact_pct']:.1f}%" if pd.notna(r.get('profit_impact_pct')) else "n/a"
        car_b = f"{r['CAR_before']:.2%}" if pd.notna(r.get('CAR_before')) else "n/a"
        car_a = f"{r['CAR_after']:.2%}" if pd.notna(r.get('CAR_after')) else "n/a"
        print(f"  {r['bank_ticker']:<8s}  ${r['total_loss']:>10,.1f}m  {loss_eq:>10s}  "
              f"{prof_imp:>10s}  {car_b:>10s}  {car_a:>10s}  {breach:>7s}")

# --- Profitability impact ---
print("\n--- Profitability Impact Summary ---")
for scen in ['BAU', '2C', '1.5C']:
    s = stress[stress['scenario'] == scen]
    banks_wiped = (s['profit_impact_pct'] > 100).sum()
    banks_material = ((s['profit_impact_pct'] > 10) & (s['profit_impact_pct'] <= 100)).sum()
    print(f"  {scen:5s}: {banks_wiped} banks lose >100% net income, "
          f"{banks_material} banks lose 10-100% net income")

print("\n" + "=" * 70)
print("Model 2 complete. Output files:")
print(f"  1. {OUTPUT_DIR / 'coal_default_status.csv'}")
print(f"  2. {OUTPUT_DIR / 'bank_stress_results.csv'}")
print(f"  3. {OUTPUT_DIR / 'stress_test_summary.csv'}")
print("=" * 70)

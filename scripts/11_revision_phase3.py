"""
11_revision_phase3.py -- Phase 3 Revisions: ADRO Removal + Robustness Computations
====================================================================================
Implements:
  Part A: Remove ADRO from coal panel (reclassified as metallurgical coal holding co)
  Part B: Re-run bank stress test (Model 2) and macro model (Model 3)
  Part C: Phase 3 robustness computations (C1-C8)

All outputs go to the paper's output/ directory.
"""

import sys, importlib, os, warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
setup = importlib.import_module('00_setup')

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

OUTPUT_DIR = setup.OUTPUT_DIR
SCENARIOS = setup.SCENARIOS
CORPORATE_TAX = setup.CORPORATE_TAX_RATE
LGD_GENERIC = setup.LGD_GENERIC
OJK_CAR_MIN = setup.OJK_CAR_MINIMUM
DSIB_CAR_BUFFER = setup.DSIB_CAR_BUFFER
FX_IDR_USD = setup.FX_IDR_USD

# NPV calculation parameters (from 05b)
PRODUCTION_DECLINE = 0.02
START_YEAR = 2025
MC_DRAWS = 10_000
MC_SEED = 42
DIRICHLET_ALPHA = (3, 4, 3)

# Macro parameters
INDONESIA_GDP_USD_B = 1319
FISCAL_MULTIPLIER = 0.7
CREDIT_GDP_ELASTICITY = 0.06
WEALTH_EFFECT = 0.03
CREDIT_MULTIPLIER = 8
PTBA_DIVIDEND_YIELD = 0.07
DEFAULT_ROYALTY_RATE_PCT = 5.0

# Scenario NPL shocks
DELTA_NPL = {'BAU': 0.005, '2C': 0.05, '1.5C': 0.15}

# NPV scenario configs (matching 05b)
NPV_SCENARIOS = {
    "Baseline_BAU": {
        "coal_price_2025": 130, "coal_price_2030": 120,
        "coal_price_2035": 110, "coal_price_2040": 100,
        "coal_price_2050": 85, "probability": 0.30,
    },
    "Scenario_2C": {
        "coal_price_2025": 130, "coal_price_2030": 90,
        "coal_price_2035": 70, "coal_price_2040": 55,
        "coal_price_2050": 35, "probability": 0.40,
    },
    "Scenario_1_5C": {
        "coal_price_2025": 130, "coal_price_2030": 70,
        "coal_price_2035": 45, "coal_price_2040": 30,
        "coal_price_2050": 15, "probability": 0.30,
    },
}


def interpolate_price(year, scenario):
    milestones = {
        2025: scenario["coal_price_2025"],
        2030: scenario["coal_price_2030"],
        2035: scenario["coal_price_2035"],
        2040: scenario["coal_price_2040"],
        2050: scenario["coal_price_2050"],
    }
    years = sorted(milestones.keys())
    if year <= years[0]:
        return milestones[years[0]]
    if year >= years[-1]:
        return milestones[years[-1]]
    for i in range(len(years) - 1):
        if years[i] <= year <= years[i + 1]:
            t = (year - years[i]) / (years[i + 1] - years[i])
            return milestones[years[i]] * (1 - t) + milestones[years[i + 1]] * t
    return milestones[2030]


def calculate_npv(Q, opex_per_t, capex_initial, T, royalty_rate,
                  discount_rate, scenario):
    if pd.isna(Q) or Q <= 0 or pd.isna(opex_per_t):
        return np.nan
    npv = -capex_initial if not pd.isna(capex_initial) and capex_initial > 0 else 0.0
    for t in range(1, int(T) + 1):
        year = START_YEAR + t
        Q_t = Q * ((1 - PRODUCTION_DECLINE) ** (t - 1))
        P_t = interpolate_price(year, scenario)
        revenue = P_t * Q_t
        royalty = royalty_rate * revenue
        opex = opex_per_t * Q_t
        ebt = revenue - opex - royalty
        tax = max(0, ebt * CORPORATE_TAX)
        fcf = ebt - tax
        npv += fcf / ((1 + discount_rate) ** t)
    return round(npv, 2)


def calculate_npv_with_dmo(Q, opex_per_t, capex_initial, T, royalty_rate,
                           discount_rate, scenario, export_pct=0.75, dmo_price=70):
    """NPV with DMO price floor on domestic portion."""
    if pd.isna(Q) or Q <= 0 or pd.isna(opex_per_t):
        return np.nan
    domestic_pct = 1 - export_pct
    npv = -capex_initial if not pd.isna(capex_initial) and capex_initial > 0 else 0.0
    for t in range(1, int(T) + 1):
        year = START_YEAR + t
        Q_t = Q * ((1 - PRODUCTION_DECLINE) ** (t - 1))
        P_export = interpolate_price(year, scenario)
        P_domestic = max(P_export, dmo_price)
        P_blended = export_pct * P_export + domestic_pct * P_domestic
        revenue = P_blended * Q_t
        royalty = royalty_rate * revenue
        opex = opex_per_t * Q_t
        ebt = revenue - opex - royalty
        tax = max(0, ebt * CORPORATE_TAX)
        fcf = ebt - tax
        npv += fcf / ((1 + discount_rate) ** t)
    return round(npv, 2)


# ============================================================
# PART A: REMOVE ADRO FROM COAL PANEL
# ============================================================
print("=" * 70)
print("PART A: Remove ADRO from Coal Panel")
print("=" * 70)

coal = pd.read_csv(OUTPUT_DIR / 'clean_coal_panel.csv')
print(f"Original coal panel: {len(coal)} companies")
print(f"Original firms with NPV: {coal['npv_bau'].notna().sum()}")
print(f"Original total production: {coal['production_mt'].sum():.1f} Mt")

# Show ADRO before removal
adro = coal[coal['ticker'] == 'ADRO']
if not adro.empty:
    r = adro.iloc[0]
    print(f"\nADRO data being removed:")
    print(f"  Production: {r['production_mt']} Mt")
    print(f"  Breakeven: ${r['breakeven_usd_t']}/t")
    print(f"  NPV_BAU: ${r['npv_bau']:,.1f}M")
    print(f"  SV_2C: ${r['sv_2c']:,.1f}M, SV_1.5C: ${r['sv_1_5c']:,.1f}M")
    print(f"  Market Cap (IDR): {r['market_cap']:,.0f}")
    print(f"  Revenue: ${r['revenue']:,.1f}M")

# Remove ADRO
coal = coal[coal['ticker'] != 'ADRO'].copy()
print(f"\nAfter removal: {len(coal)} companies")
print(f"Firms with NPV: {coal['npv_bau'].notna().sum()}")
print(f"Total production: {coal['production_mt'].sum():.1f} Mt")

# Fix AADI revenue (data quality issue: stored as 5.3084 instead of ~5319.6)
aadi_mask = coal['ticker'] == 'AADI'
if aadi_mask.any():
    aadi_row = coal.loc[aadi_mask].iloc[0]
    computed_revenue = aadi_row['cost_of_revenue'] + aadi_row['gross_profit']
    if aadi_row['revenue'] < 100:  # clearly wrong if < $100M for 65 Mt producer
        print(f"\nFixing AADI revenue: {aadi_row['revenue']:.4f} -> {computed_revenue:.1f}")
        coal.loc[aadi_mask, 'revenue'] = computed_revenue

# Save updated coal panel
coal.to_csv(OUTPUT_DIR / 'clean_coal_panel.csv', index=False)
print(f"\nSaved updated clean_coal_panel.csv ({len(coal)} companies)")

# Report new aggregates
valid_coal = coal[coal['npv_bau'].notna()]
print(f"\n--- Updated Aggregates ---")
print(f"  Firms with NPV: {len(valid_coal)}")
print(f"  Total production: {coal['production_mt'].sum():.1f} Mt")
print(f"  Aggregate SV 2C: ${valid_coal['sv_2c'].sum():,.1f}M (${valid_coal['sv_2c'].sum()/1000:.1f}B)")
print(f"  Aggregate SV 1.5C: ${valid_coal['sv_1_5c'].sum():,.1f}M (${valid_coal['sv_1_5c'].sum()/1000:.1f}B)")
print(f"  Expected SV: ${valid_coal['expected_sv'].sum():,.1f}M (${valid_coal['expected_sv'].sum()/1000:.1f}B)")

# Default counts
for scen, col in [('BAU', 'npv_bau'), ('2C', 'npv_2c'), ('1.5C', 'npv_1_5c')]:
    neg = (valid_coal[col] < 0).sum()
    pos = (valid_coal[col] >= 0).sum()
    print(f"  {scen}: {neg} negative NPV (default), {pos} positive")


# ============================================================
# RE-RUN MONTE CARLO for 26 firms (excluding ADRO)
# ============================================================
print("\n" + "=" * 70)
print("RE-RUNNING MONTE CARLO (26 firms, excluding ADRO)")
print("=" * 70)

rng = np.random.default_rng(MC_SEED)

firms_data = []
for _, row in valid_coal.iterrows():
    # Get firm parameters for NPV recalculation
    Q = row['production_mt']
    cost = row.get('cash_cost_usd_t', np.nan)
    if pd.isna(cost) or pd.isna(Q) or Q <= 0:
        continue
    T = row.get('mine_life_years', 20)
    if pd.isna(T):
        T = 20
    royalty_rate = row.get('royalty_rate_pct', 5.0) / 100.0
    wacc = row.get('wacc_stranded', 0.122)
    if pd.isna(wacc):
        wacc = 0.122
    capex = 0  # Already embedded in breakeven for revised data

    firms_data.append({
        'ticker': row['ticker'],
        'Q': Q, 'cost': cost, 'capex': capex,
        'T': T, 'royalty': royalty_rate, 'wacc': wacc,
    })

print(f"  Firms in MC: {len(firms_data)}")

mc_sv_2c = []
mc_sv_15 = []
mc_esv = []

for draw in range(MC_DRAWS):
    weights = rng.dirichlet(DIRICHLET_ALPHA)
    wacc_shock = rng.uniform(-0.02, 0.02)
    prod_shock = rng.uniform(-0.10, 0.10)
    cost_shock = rng.uniform(-0.15, 0.15)

    total_sv_2c = 0
    total_sv_15 = 0

    for firm in firms_data:
        Q_draw = firm['Q'] * (1 + prod_shock)
        cost_draw = firm['cost'] * (1 + cost_shock)
        wacc_draw = max(0.04, firm['wacc'] + wacc_shock)

        npv_bau = calculate_npv(Q_draw, cost_draw, firm['capex'], firm['T'],
                                firm['royalty'], wacc_draw, NPV_SCENARIOS['Baseline_BAU'])
        npv_2c = calculate_npv(Q_draw, cost_draw, firm['capex'], firm['T'],
                               firm['royalty'], wacc_draw, NPV_SCENARIOS['Scenario_2C'])
        npv_15 = calculate_npv(Q_draw, cost_draw, firm['capex'], firm['T'],
                               firm['royalty'], wacc_draw, NPV_SCENARIOS['Scenario_1_5C'])

        if not pd.isna(npv_bau):
            sv2 = max(0, npv_bau - npv_2c) if not pd.isna(npv_2c) else 0
            sv15 = max(0, npv_bau - npv_15) if not pd.isna(npv_15) else 0
            total_sv_2c += sv2
            total_sv_15 += sv15

    esv_draw = weights[1] * total_sv_2c + weights[2] * total_sv_15
    mc_sv_2c.append(total_sv_2c)
    mc_sv_15.append(total_sv_15)
    mc_esv.append(esv_draw)

mc_sv_2c = np.array(mc_sv_2c)
mc_sv_15 = np.array(mc_sv_15)
mc_esv = np.array(mc_esv)

print(f"\n  {'Metric':<30s} {'Median':>12s} {'5th pct':>12s} {'95th pct':>12s}")
print("  " + "-" * 66)
for label, arr in [("SV 2C ($B)", mc_sv_2c / 1000),
                   ("SV 1.5C ($B)", mc_sv_15 / 1000),
                   ("Expected SV ($B)", mc_esv / 1000)]:
    med = np.median(arr)
    p5 = np.percentile(arr, 5)
    p95 = np.percentile(arr, 95)
    print(f"  {label:<30s} {med:>12.1f} {p5:>12.1f} {p95:>12.1f}")


# ============================================================
# PART B: RE-RUN MODEL 2 (BANK STRESS TEST)
# ============================================================
print("\n" + "=" * 70)
print("PART B: Re-run Model 2 (Bank Stress Test)")
print("=" * 70)

# Reload updated coal panel
coal = pd.read_csv(OUTPUT_DIR / 'clean_coal_panel.csv')

# Bank data
bank_raw = pd.read_csv(OUTPUT_DIR / 'clean_bank_panel.csv')
bank = (bank_raw
        .sort_values('year', ascending=False)
        .drop_duplicates(subset='ticker', keep='first')
        .copy())
print(f"Loaded bank panel: {len(bank)} banks")

# Exposure matrix
exposure = pd.read_csv(OUTPUT_DIR / 'exposure_matrix.csv', index_col=0)
exposure = exposure.fillna(0.0)
if 'TOTAL' in exposure.columns:
    exposure = exposure.drop(columns='TOTAL')
if 'UNATTRIBUTED' in exposure.index:
    exposure = exposure.drop(index='UNATTRIBUTED')
print(f"Exposure matrix: {exposure.shape[0]} banks x {exposure.shape[1]} coal companies")

# NPV/SV column mapping
npv_cols = {'BAU': 'npv_bau', '2C': 'npv_2c', '1.5C': 'npv_1_5c'}
sv_cols = {'2C': 'sv_2c', '1.5C': 'sv_1_5c'}

# Step 1: Coal default classification
records = []
for _, row in coal.iterrows():
    ticker = row['ticker']
    total_debt = row.get('total_debt', 0) if pd.notna(row.get('total_debt', np.nan)) else 0.0
    total_equity = row.get('total_equity', 0) if pd.notna(row.get('total_equity', np.nan)) else 0.0
    total_assets = row.get('total_assets', 0) if pd.notna(row.get('total_assets', np.nan)) else 0.0

    for scen in ['BAU', '2C', '1.5C']:
        npv_val = row.get(npv_cols[scen], np.nan)
        sv_val = row.get(sv_cols.get(scen, None), np.nan) if scen in sv_cols else 0.0
        sv_val = sv_val if pd.notna(sv_val) else 0.0

        if pd.isna(npv_val):
            records.append({
                'coal_ticker': ticker, 'scenario': scen,
                'status': 'NO_DATA', 'lgd': 0.0,
                'npv': np.nan, 'stranded_value': sv_val,
            })
            continue

        if npv_val < 0:
            lgd = min(1.0, abs(npv_val) / max(total_debt, 1.0))
            status = 'DEFAULT'
        elif sv_val > 0.5 * total_equity and total_equity > 0:
            lgd = 0.3 * sv_val / max(total_assets, 1.0)
            status = 'DISTRESSED'
        else:
            lgd = 0.0
            status = 'PERFORMING'

        records.append({
            'coal_ticker': ticker, 'scenario': scen,
            'status': status, 'lgd': lgd,
            'npv': npv_val, 'stranded_value': sv_val,
        })

coal_status = pd.DataFrame(records)

print("\nDefault/Distress counts by scenario:")
for scen in ['BAU', '2C', '1.5C']:
    sub = coal_status[coal_status['scenario'] == scen]
    counts = sub['status'].value_counts()
    print(f"  {scen:5s}: {dict(counts)}")

coal_status.to_csv(OUTPUT_DIR / 'coal_default_status.csv', index=False)
print(f"Saved: coal_default_status.csv ({len(coal_status)} rows)")

lgd_lookup = coal_status.set_index(['coal_ticker', 'scenario'])['lgd'].to_dict()

# Step 2: Direct credit losses
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
            'bank_ticker': bank_ticker, 'scenario': scen, 'direct_loss': loss,
        })
direct_losses = pd.DataFrame(direct_loss_records)

# Step 3: Indirect losses
bank_total_direct_exposure = exposure.sum(axis=1)
indirect_loss_records = []
for bank_ticker in exposure.index:
    bank_row = bank[bank['ticker'] == bank_ticker]
    if bank_row.empty:
        for scen in ['BAU', '2C', '1.5C']:
            indirect_loss_records.append({
                'bank_ticker': bank_ticker, 'scenario': scen,
                'indirect_loss': 0.0, 'indirect_mining_exposure': 0.0,
            })
        continue
    bank_row = bank_row.iloc[0]
    mining_loans = bank_row.get('mining_loans_usd_m', 0)
    mining_loans = mining_loans if pd.notna(mining_loans) else 0.0
    direct_total = bank_total_direct_exposure.get(bank_ticker, 0.0)
    indirect_mining = max(0.0, mining_loans - direct_total)

    for scen in ['BAU', '2C', '1.5C']:
        delta_npl = DELTA_NPL[scen]
        loss = indirect_mining * delta_npl * LGD_GENERIC
        indirect_loss_records.append({
            'bank_ticker': bank_ticker, 'scenario': scen,
            'indirect_loss': loss, 'indirect_mining_exposure': indirect_mining,
        })
indirect_losses = pd.DataFrame(indirect_loss_records)

# Step 4: Total loss & capital impact
stress = direct_losses.merge(
    indirect_losses[['bank_ticker', 'scenario', 'indirect_loss', 'indirect_mining_exposure']],
    on=['bank_ticker', 'scenario'], how='left',
)
stress['indirect_loss'] = stress['indirect_loss'].fillna(0.0)
stress['total_loss'] = stress['direct_loss'] + stress['indirect_loss']

# Merge bank financials
ckpn_cols_list = ['loan_allowance_usd_m', 'provision_expense_usd_m']
avail_ckpn = [c for c in ckpn_cols_list if c in bank.columns]
bank_fin_cols = ['ticker', 'total_assets_usd_m', 'total_equity_usd_m',
                 'gross_loans_usd_m', 'net_income_usd_m', 'roa', 'roe',
                 'nim', 'npl_gross', 'market_cap_usd_m',
                 'size_category', 'mining_loans_usd_m',
                 'tier1_ratio', 'total_car',
                 'reported_car', 'car_source'] + avail_ckpn
bank_fin_cols = [c for c in bank_fin_cols if c in bank.columns]
bank_financials = bank[bank_fin_cols].copy()
bank_financials = bank_financials.rename(columns={'ticker': 'bank_ticker'})

stress = stress.merge(bank_financials, on='bank_ticker', how='left')

# RWA estimate
stress['rwa'] = np.where(
    stress['gross_loans_usd_m'].notna() & (stress['gross_loans_usd_m'] > 0),
    stress['gross_loans_usd_m'] / 0.65,
    stress['total_assets_usd_m'] * 0.80
)

# CAR
stress['CAR_before'] = np.where(
    stress['reported_car'].notna() & (stress['reported_car'] > 0),
    stress['reported_car'],
    stress['total_equity_usd_m'] / stress['rwa']
)
stress['car_source_final'] = np.where(
    stress['reported_car'].notna() & (stress['reported_car'] > 0),
    stress['car_source'], 'equity_rwa_proxy'
)

# CKPN buffer
if 'loan_allowance_usd_m' in stress.columns:
    known = stress[stress['loan_allowance_usd_m'].notna() & (stress['loan_allowance_usd_m'] > 0)]
    if len(known) > 0 and known['gross_loans_usd_m'].sum() > 0:
        avg_ckpn_ratio = known['loan_allowance_usd_m'].sum() / known['gross_loans_usd_m'].sum()
    else:
        avg_ckpn_ratio = 0.025
    stress['ckpn_buffer'] = np.where(
        stress['loan_allowance_usd_m'].notna() & (stress['loan_allowance_usd_m'] > 0),
        stress['loan_allowance_usd_m'],
        stress['gross_loans_usd_m'].fillna(0) * avg_ckpn_ratio
    )
    stress['loss_after_ckpn'] = np.maximum(0, stress['total_loss'] - stress['ckpn_buffer'])
else:
    stress['ckpn_buffer'] = 0.0
    stress['loss_after_ckpn'] = stress['total_loss']

stress['CAR_impact'] = stress['total_loss'] / stress['rwa']
stress['CAR_after'] = stress['CAR_before'] - stress['CAR_impact']
stress['CAR_impact_after_ckpn'] = stress['loss_after_ckpn'] / stress['rwa']
stress['CAR_after_with_ckpn'] = stress['CAR_before'] - stress['CAR_impact_after_ckpn']

stress['car_breach_ojk'] = stress['CAR_after'] < OJK_CAR_MIN
stress['car_breach_dsib'] = (
    (stress['CAR_after'] < DSIB_CAR_BUFFER) &
    (stress['size_category'] == 'DSIB')
)

stress['ROA_before'] = stress['roa']
stress['ROA_after'] = np.where(
    stress['total_assets_usd_m'].notna() & (stress['total_assets_usd_m'] > 0),
    (stress['net_income_usd_m'].fillna(0) - stress['total_loss']) / stress['total_assets_usd_m'],
    np.nan
)
stress['ROA_impact'] = stress['ROA_before'] - stress['ROA_after']
stress['profit_impact_pct'] = np.where(
    stress['net_income_usd_m'].notna() & (stress['net_income_usd_m'] > 0),
    (stress['total_loss'] / stress['net_income_usd_m']) * 100.0, np.nan
)
stress['loss_pct_equity'] = np.where(
    stress['total_equity_usd_m'].notna() & (stress['total_equity_usd_m'] > 0),
    (stress['total_loss'] / stress['total_equity_usd_m']) * 100.0, np.nan
)

# Save bank stress results
output_cols = [
    'bank_ticker', 'scenario', 'size_category',
    'direct_loss', 'indirect_loss', 'total_loss',
    'ckpn_buffer', 'loss_after_ckpn', 'indirect_mining_exposure',
    'total_equity_usd_m', 'total_assets_usd_m', 'gross_loans_usd_m',
    'mining_loans_usd_m', 'net_income_usd_m', 'rwa',
    'CAR_before', 'CAR_after', 'CAR_impact',
    'CAR_impact_after_ckpn', 'CAR_after_with_ckpn', 'car_source_final',
    'ROA_before', 'ROA_after', 'ROA_impact',
    'car_breach_ojk', 'car_breach_dsib',
    'profit_impact_pct', 'loss_pct_equity',
]
output_cols = [c for c in output_cols if c in stress.columns]
stress_out = stress[output_cols].copy()
# Rename car_source_final back to car_source for compatibility
if 'car_source_final' in stress_out.columns:
    stress_out = stress_out.rename(columns={'car_source_final': 'car_source'})
stress_out.to_csv(OUTPUT_DIR / 'bank_stress_results.csv', index=False)

# Stress test summary
SCENARIO_LABELS = {k: v['label'] for k, v in SCENARIOS.items()}
summary_records = []
for scen in ['BAU', '2C', '1.5C']:
    s = stress[stress['scenario'] == scen]
    coal_s = coal_status[coal_status['scenario'] == scen]
    n_default = (coal_s['status'] == 'DEFAULT').sum()
    n_distress = (coal_s['status'] == 'DISTRESSED').sum()
    n_performing = (coal_s['status'] == 'PERFORMING').sum()
    total_direct = s['direct_loss'].sum()
    total_indirect = s['indirect_loss'].sum()
    total_losses = s['total_loss'].sum()
    total_equity = s['total_equity_usd_m'].sum()
    n_ojk_breach = s['car_breach_ojk'].sum()
    n_dsib_breach = s['car_breach_dsib'].sum()
    avg_car_impact = s['CAR_impact'].mean()
    max_car_impact = s['CAR_impact'].max()
    avg_profit_impact = s['profit_impact_pct'].mean()
    max_profit_impact = s['profit_impact_pct'].max()
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
        'avg_car_impact_pp': round(avg_car_impact * 100, 4),
        'max_car_impact_pp': round(max_car_impact * 100, 4),
        'avg_profit_impact_pct': round(avg_profit_impact, 2) if pd.notna(avg_profit_impact) else np.nan,
        'max_profit_impact_pct': round(max_profit_impact, 2) if pd.notna(max_profit_impact) else np.nan,
    })

summary_df = pd.DataFrame(summary_records)
summary_df.to_csv(OUTPUT_DIR / 'stress_test_summary.csv', index=False)

print("\n--- Stress Test Summary ---")
for _, row in summary_df.iterrows():
    print(f"  {row['scenario']:5s}: Direct=${row['total_direct_loss_usd_m']:,.1f}M "
          f"Indirect=${row['total_indirect_loss_usd_m']:,.1f}M "
          f"Total=${row['total_loss_usd_m']:,.1f}M "
          f"({row['loss_pct_system_equity']:.2f}% equity) "
          f"Defaults={row['n_coal_default']} "
          f"Max CAR={row['max_car_impact_pp']:.2f}pp "
          f"Max Profit={row['max_profit_impact_pct']:.1f}%")

# BMRI details
for scen in ['2C', '1.5C']:
    bmri = stress[(stress['bank_ticker'] == 'BMRI') & (stress['scenario'] == scen)]
    if not bmri.empty:
        b = bmri.iloc[0]
        print(f"\n  BMRI {scen}: loss=${b['total_loss']:,.1f}M "
              f"profit_impact={b['profit_impact_pct']:.1f}% "
              f"CAR_impact={b['CAR_impact']*100:.2f}pp "
              f"CAR_before={b['CAR_before']:.2%} CAR_after={b['CAR_after']:.2%}")


# ============================================================
# PART B.2: RE-RUN MODEL 3 (MACRO-FINANCIAL TRANSMISSION)
# ============================================================
print("\n" + "=" * 70)
print("PART B.2: Re-run Model 3 (Macro-Financial Transmission)")
print("=" * 70)

# Market cap conversion
if 'market_cap' in coal.columns:
    coal['market_cap_usd_m'] = coal['market_cap'] / FX_IDR_USD / 1e6
elif 'market_cap_usd_m' not in coal.columns:
    coal['market_cap_usd_m'] = np.nan

if 'revenue' not in coal.columns:
    coal['revenue'] = 0.0
else:
    coal['revenue'] = pd.to_numeric(coal['revenue'], errors='coerce').fillna(0.0)

if 'royalty_rate_pct' not in coal.columns:
    coal['royalty_rate_pct'] = DEFAULT_ROYALTY_RATE_PCT
else:
    coal['royalty_rate_pct'] = pd.to_numeric(coal['royalty_rate_pct'], errors='coerce').fillna(DEFAULT_ROYALTY_RATE_PCT)

for col in ['npv_bau', 'npv_2c', 'npv_1_5c', 'sv_2c', 'sv_1_5c']:
    if col in coal.columns:
        coal[col] = pd.to_numeric(coal[col], errors='coerce')

bau_price_2030 = SCENARIOS['BAU']['coal_prices'][2030]
scenario_configs = {}
for scen_key in ['2C', '1.5C']:
    scen_price_2030 = SCENARIOS[scen_key]['coal_prices'][2030]
    price_decline_pct = 1.0 - (scen_price_2030 / bau_price_2030)
    scenario_configs[scen_key] = {
        'label': SCENARIOS[scen_key]['label'],
        'price_2030': scen_price_2030,
        'price_decline_pct': price_decline_pct,
    }

gdp_usd_m = INDONESIA_GDP_USD_B * 1000
bank_stress = stress_out.copy()
# Rename car_source back if needed
if 'car_source' in bank_stress.columns:
    pass

macro_results = []
for scen_key, scfg in scenario_configs.items():
    price_decline = scfg['price_decline_pct']

    # FISCAL
    coal['revenue_loss'] = coal['revenue'] * price_decline
    tax_loss = (coal['revenue_loss'] * CORPORATE_TAX).sum()
    coal['royalty_loss'] = coal['revenue_loss'] * coal['royalty_rate_pct'] / 100.0
    royalty_loss = coal['royalty_loss'].sum()

    ptba_mask = coal['ticker'] == 'PTBA'
    ptba_dividend_loss = 0.0
    if ptba_mask.any():
        ptba_row = coal.loc[ptba_mask].iloc[0]
        ptba_mkt_cap = ptba_row.get('market_cap_usd_m', 0.0)
        if pd.notna(ptba_mkt_cap) and ptba_mkt_cap > 0:
            ptba_dividend_loss = ptba_mkt_cap * PTBA_DIVIDEND_YIELD * price_decline

    total_fiscal_loss = tax_loss + royalty_loss + ptba_dividend_loss
    fiscal_gdp_impact = (total_fiscal_loss / gdp_usd_m) * FISCAL_MULTIPLIER * 100

    # CREDIT
    scen_stress = bank_stress[bank_stress['scenario'] == scen_key]
    total_bank_losses = scen_stress['total_loss'].sum()
    total_bank_lending = bank['gross_loans_usd_m'].dropna().sum()
    credit_contraction = total_bank_losses * CREDIT_MULTIPLIER
    credit_contraction_pct = (credit_contraction / total_bank_lending * 100
                              if total_bank_lending > 0 else 0.0)
    credit_gdp_impact = credit_contraction_pct * CREDIT_GDP_ELASTICITY

    # MARKET
    sv_col = f'sv_{scen_key.lower().replace(".", "_")}'
    coal_market_loss = 0.0
    for _, row in coal.iterrows():
        mkt_cap = row.get('market_cap_usd_m', np.nan)
        npv_bau = row.get('npv_bau', np.nan)
        sv = row.get(sv_col, np.nan)
        if pd.isna(mkt_cap) or mkt_cap <= 0 or pd.isna(sv) or pd.isna(npv_bau):
            continue
        if npv_bau <= 0:
            loss_frac = min(abs(sv) / abs(npv_bau), 1.0) if npv_bau != 0 else 1.0
        else:
            loss_frac = min(sv / npv_bau, 1.0)
        company_loss = min(mkt_cap * loss_frac, mkt_cap)
        coal_market_loss += company_loss

    bank_market_loss = 0.0
    for _, brow in scen_stress.iterrows():
        btk = brow['bank_ticker']
        bloss = brow['total_loss']
        if pd.isna(bloss) or bloss <= 0:
            continue
        bmatch = bank[bank['ticker'] == btk]
        if bmatch.empty:
            continue
        brow_panel = bmatch.iloc[0]
        b_equity = brow_panel.get('total_equity_usd_m', np.nan)
        b_mktcap = brow_panel.get('market_cap_usd_m', np.nan)
        if pd.isna(b_equity) or b_equity <= 0 or pd.isna(b_mktcap) or b_mktcap <= 0:
            continue
        equity_loss_frac = min(bloss / b_equity, 1.0)
        bank_market_loss += b_mktcap * equity_loss_frac

    total_market_loss = coal_market_loss + bank_market_loss
    market_gdp_impact = (total_market_loss / gdp_usd_m) * WEALTH_EFFECT * 100
    total_gdp_impact = fiscal_gdp_impact + credit_gdp_impact + market_gdp_impact

    print(f"\n  {scen_key}: Fiscal={fiscal_gdp_impact:.4f}% "
          f"Credit={credit_gdp_impact:.4f}% "
          f"Market={market_gdp_impact:.4f}% "
          f"TOTAL={total_gdp_impact:.4f}%")

    macro_results.append({
        'scenario': scen_key,
        'scenario_label': scfg['label'],
        'price_decline_pct': price_decline * 100,
        'tax_loss_usd_m': tax_loss,
        'royalty_loss_usd_m': royalty_loss,
        'ptba_dividend_loss_usd_m': ptba_dividend_loss,
        'total_fiscal_loss_usd_m': total_fiscal_loss,
        'fiscal_gdp_impact_pct': fiscal_gdp_impact,
        'bank_capital_loss_usd_m': total_bank_losses,
        'credit_contraction_usd_m': credit_contraction,
        'credit_contraction_pct': credit_contraction_pct,
        'credit_gdp_impact_pct': credit_gdp_impact,
        'coal_market_loss_usd_m': coal_market_loss,
        'bank_market_loss_usd_m': bank_market_loss,
        'total_market_loss_usd_m': total_market_loss,
        'market_gdp_impact_pct': market_gdp_impact,
        'total_gdp_impact_pct': total_gdp_impact,
    })

macro_results_df = pd.DataFrame(macro_results)

# Save macro_channel_details.csv
channel_rows = []
for r in macro_results:
    scen = r['scenario']
    label = r['scenario_label']
    channel_rows.append({'scenario': scen, 'scenario_label': label,
        'channel': 'Fiscal', 'sub_channel': 'Corporate Tax',
        'loss_usd_m': r['tax_loss_usd_m'],
        'gdp_impact_pct': r['tax_loss_usd_m'] / gdp_usd_m * FISCAL_MULTIPLIER * 100})
    channel_rows.append({'scenario': scen, 'scenario_label': label,
        'channel': 'Fiscal', 'sub_channel': 'Royalty',
        'loss_usd_m': r['royalty_loss_usd_m'],
        'gdp_impact_pct': r['royalty_loss_usd_m'] / gdp_usd_m * FISCAL_MULTIPLIER * 100})
    channel_rows.append({'scenario': scen, 'scenario_label': label,
        'channel': 'Fiscal', 'sub_channel': 'PTBA Dividend',
        'loss_usd_m': r['ptba_dividend_loss_usd_m'],
        'gdp_impact_pct': r['ptba_dividend_loss_usd_m'] / gdp_usd_m * FISCAL_MULTIPLIER * 100})
    channel_rows.append({'scenario': scen, 'scenario_label': label,
        'channel': 'Credit', 'sub_channel': 'Bank Deleveraging',
        'loss_usd_m': r['credit_contraction_usd_m'],
        'gdp_impact_pct': r['credit_gdp_impact_pct']})
    channel_rows.append({'scenario': scen, 'scenario_label': label,
        'channel': 'Market', 'sub_channel': 'Coal Equity',
        'loss_usd_m': r['coal_market_loss_usd_m'],
        'gdp_impact_pct': r['coal_market_loss_usd_m'] / gdp_usd_m * WEALTH_EFFECT * 100})
    channel_rows.append({'scenario': scen, 'scenario_label': label,
        'channel': 'Market', 'sub_channel': 'Bank Equity',
        'loss_usd_m': r['bank_market_loss_usd_m'],
        'gdp_impact_pct': r['bank_market_loss_usd_m'] / gdp_usd_m * WEALTH_EFFECT * 100})

channel_details = pd.DataFrame(channel_rows)
channel_details.to_csv(OUTPUT_DIR / 'macro_channel_details.csv', index=False)

# Save macro_impact_summary.csv
macro_summary = macro_results_df[[
    'scenario', 'scenario_label', 'price_decline_pct',
    'total_fiscal_loss_usd_m', 'fiscal_gdp_impact_pct',
    'credit_contraction_usd_m', 'credit_gdp_impact_pct',
    'total_market_loss_usd_m', 'market_gdp_impact_pct',
    'total_gdp_impact_pct',
    'tax_loss_usd_m', 'royalty_loss_usd_m', 'ptba_dividend_loss_usd_m',
    'bank_capital_loss_usd_m', 'credit_contraction_pct',
    'coal_market_loss_usd_m', 'bank_market_loss_usd_m',
]].copy()
macro_summary.to_csv(OUTPUT_DIR / 'macro_impact_summary.csv', index=False)

print("\nSaved: macro_channel_details.csv, macro_impact_summary.csv")


# ============================================================
# PART C: PHASE 3 ROBUSTNESS COMPUTATIONS
# ============================================================
print("\n" + "=" * 70)
print("PART C: Phase 3 Robustness Computations")
print("=" * 70)

# Ensure robustness directory exists
robustness_dir = OUTPUT_DIR / 'robustness'
robustness_dir.mkdir(parents=True, exist_ok=True)

# Get firm data for NPV recalculations
valid_coal = coal[coal['npv_bau'].notna()].copy()

def get_firm_params(row):
    Q = row['production_mt']
    cost = row.get('cash_cost_usd_t', np.nan)
    if pd.isna(cost) or pd.isna(Q) or Q <= 0:
        return None
    T = row.get('mine_life_years', 20)
    if pd.isna(T):
        T = 20
    royalty_rate = row.get('royalty_rate_pct', 5.0) / 100.0
    wacc = row.get('wacc_stranded', 0.122)
    if pd.isna(wacc):
        wacc = 0.122
    return {
        'ticker': row['ticker'], 'Q': Q, 'cost': cost, 'capex': 0,
        'T': T, 'royalty': royalty_rate, 'wacc': wacc,
        'cv': row.get('cv_kcal_kg', np.nan),
        'cash': row.get('cash', 0) if pd.notna(row.get('cash', np.nan)) else 0,
        'total_debt': row.get('total_debt', 0) if pd.notna(row.get('total_debt', np.nan)) else 0,
        'total_equity': row.get('total_equity', 0) if pd.notna(row.get('total_equity', np.nan)) else 0,
        'total_assets': row.get('total_assets', 0) if pd.notna(row.get('total_assets', np.nan)) else 0,
        'breakeven': row.get('breakeven_usd_t', np.nan),
    }


# ── C1: Mine Life Robustness (T=10, 15, 20, 25) ──
print("\n--- C1: Mine Life Robustness ---")
mine_life_results = []
for T_test in [10, 15, 20, 25]:
    total_sv_2c = 0
    total_sv_15 = 0
    n_default_bau = 0
    n_default_2c = 0
    n_default_15 = 0

    for _, row in valid_coal.iterrows():
        fp = get_firm_params(row)
        if fp is None:
            continue
        npv_bau = calculate_npv(fp['Q'], fp['cost'], fp['capex'], T_test,
                                fp['royalty'], fp['wacc'], NPV_SCENARIOS['Baseline_BAU'])
        npv_2c = calculate_npv(fp['Q'], fp['cost'], fp['capex'], T_test,
                               fp['royalty'], fp['wacc'], NPV_SCENARIOS['Scenario_2C'])
        npv_15 = calculate_npv(fp['Q'], fp['cost'], fp['capex'], T_test,
                               fp['royalty'], fp['wacc'], NPV_SCENARIOS['Scenario_1_5C'])

        if not pd.isna(npv_bau):
            sv2 = max(0, npv_bau - npv_2c) if not pd.isna(npv_2c) else 0
            sv15 = max(0, npv_bau - npv_15) if not pd.isna(npv_15) else 0
            total_sv_2c += sv2
            total_sv_15 += sv15
            if npv_bau < 0: n_default_bau += 1
            if not pd.isna(npv_2c) and npv_2c < 0: n_default_2c += 1
            if not pd.isna(npv_15) and npv_15 < 0: n_default_15 += 1

    mine_life_results.append({
        'mine_life_years': T_test,
        'sv_2c_usd_b': round(total_sv_2c / 1000, 1),
        'sv_1_5c_usd_b': round(total_sv_15 / 1000, 1),
        'n_default_bau': n_default_bau,
        'n_default_2c': n_default_2c,
        'n_default_1_5c': n_default_15,
    })
    print(f"  T={T_test}: SV_2C=${total_sv_2c/1000:.1f}B, "
          f"SV_1.5C=${total_sv_15/1000:.1f}B, "
          f"Defaults: BAU={n_default_bau}, 2C={n_default_2c}, 1.5C={n_default_15}")

pd.DataFrame(mine_life_results).to_csv(robustness_dir / 'mine_life_sensitivity.csv', index=False)


# ── C2: DMO Sensitivity ──
print("\n--- C2: DMO Sensitivity ---")
dmo_results = []
for dmo_label, dmo_price, export_pct in [("No DMO (baseline)", None, 1.0),
                                           ("DMO $70/t on 25%", 70, 0.75)]:
    total_sv_2c = 0
    total_sv_15 = 0

    for _, row in valid_coal.iterrows():
        fp = get_firm_params(row)
        if fp is None:
            continue
        if dmo_price is None:
            npv_bau = calculate_npv(fp['Q'], fp['cost'], fp['capex'], fp['T'],
                                    fp['royalty'], fp['wacc'], NPV_SCENARIOS['Baseline_BAU'])
            npv_2c = calculate_npv(fp['Q'], fp['cost'], fp['capex'], fp['T'],
                                   fp['royalty'], fp['wacc'], NPV_SCENARIOS['Scenario_2C'])
            npv_15 = calculate_npv(fp['Q'], fp['cost'], fp['capex'], fp['T'],
                                   fp['royalty'], fp['wacc'], NPV_SCENARIOS['Scenario_1_5C'])
        else:
            npv_bau = calculate_npv_with_dmo(fp['Q'], fp['cost'], fp['capex'], fp['T'],
                                             fp['royalty'], fp['wacc'], NPV_SCENARIOS['Baseline_BAU'],
                                             export_pct, dmo_price)
            npv_2c = calculate_npv_with_dmo(fp['Q'], fp['cost'], fp['capex'], fp['T'],
                                            fp['royalty'], fp['wacc'], NPV_SCENARIOS['Scenario_2C'],
                                            export_pct, dmo_price)
            npv_15 = calculate_npv_with_dmo(fp['Q'], fp['cost'], fp['capex'], fp['T'],
                                            fp['royalty'], fp['wacc'], NPV_SCENARIOS['Scenario_1_5C'],
                                            export_pct, dmo_price)

        if not pd.isna(npv_bau):
            sv2 = max(0, npv_bau - npv_2c) if not pd.isna(npv_2c) else 0
            sv15 = max(0, npv_bau - npv_15) if not pd.isna(npv_15) else 0
            total_sv_2c += sv2
            total_sv_15 += sv15

    dmo_results.append({
        'specification': dmo_label,
        'sv_2c_usd_b': round(total_sv_2c / 1000, 1),
        'sv_1_5c_usd_b': round(total_sv_15 / 1000, 1),
    })
    print(f"  {dmo_label}: SV_2C=${total_sv_2c/1000:.1f}B, SV_1.5C=${total_sv_15/1000:.1f}B")

pd.DataFrame(dmo_results).to_csv(robustness_dir / 'dmo_sensitivity.csv', index=False)


# ── C3: Alternative Default Specification ──
print("\n--- C3: Alternative Default Specification ---")
alt_default_results = []
for spec_label, use_cash_test in [("Baseline (NPV<0)", False),
                                   ("NPV<0 AND cash/debt<0.5", True)]:
    n_def = {'BAU': 0, '2C': 0, '1.5C': 0}

    for _, row in valid_coal.iterrows():
        fp = get_firm_params(row)
        if fp is None:
            continue
        for scen, npv_col in [('BAU', 'npv_bau'), ('2C', 'npv_2c'), ('1.5C', 'npv_1_5c')]:
            npv_val = row.get(npv_col, np.nan)
            if pd.isna(npv_val):
                continue
            if npv_val < 0:
                if use_cash_test:
                    cash_debt_ratio = fp['cash'] / max(fp['total_debt'], 1.0)
                    if cash_debt_ratio < 0.5:
                        n_def[scen] += 1
                else:
                    n_def[scen] += 1

    alt_default_results.append({
        'specification': spec_label,
        'n_default_bau': n_def['BAU'],
        'n_default_2c': n_def['2C'],
        'n_default_1_5c': n_def['1.5C'],
    })
    print(f"  {spec_label}: BAU={n_def['BAU']}, 2C={n_def['2C']}, 1.5C={n_def['1.5C']}")

pd.DataFrame(alt_default_results).to_csv(robustness_dir / 'alt_default_sensitivity.csv', index=False)


# ── C4: Time-to-Distress ──
print("\n--- C4: Time-to-Distress ---")
distress_records = []
for _, row in valid_coal.iterrows():
    fp = get_firm_params(row)
    if fp is None:
        continue
    for scen_name, scenario in NPV_SCENARIOS.items():
        scen_label = scen_name.replace('Baseline_', '').replace('Scenario_', '')
        cumulative_npv = 0
        distress_year = None
        for t in range(1, int(fp['T']) + 1):
            year = START_YEAR + t
            Q_t = fp['Q'] * ((1 - PRODUCTION_DECLINE) ** (t - 1))
            P_t = interpolate_price(year, scenario)
            revenue = P_t * Q_t
            royalty = fp['royalty'] * revenue
            opex = fp['cost'] * Q_t
            ebt = revenue - opex - royalty
            tax = max(0, ebt * CORPORATE_TAX)
            fcf = ebt - tax
            pv_fcf = fcf / ((1 + fp['wacc']) ** t)
            cumulative_npv += pv_fcf
            if cumulative_npv < 0 and distress_year is None:
                distress_year = year
        distress_records.append({
            'ticker': fp['ticker'],
            'scenario': scen_label,
            'distress_year': distress_year,
            'years_to_distress': (distress_year - START_YEAR) if distress_year else None,
        })

distress_df = pd.DataFrame(distress_records)
distress_df.to_csv(robustness_dir / 'time_to_distress.csv', index=False)

# Summary
for scen in ['BAU', '2C', '1_5C']:
    sub = distress_df[distress_df['scenario'] == scen]
    distressed = sub[sub['distress_year'].notna()]
    if len(distressed) > 0:
        print(f"  {scen}: {len(distressed)} firms reach distress, "
              f"median year={distressed['distress_year'].median():.0f}, "
              f"median years={distressed['years_to_distress'].median():.0f}")
    else:
        print(f"  {scen}: 0 firms reach distress within mine life")


# ── C5: Network Targeted Removal ──
print("\n--- C5: Network Targeted Removal ---")
# Get total exposure per coal company
exposure_full = pd.read_csv(OUTPUT_DIR / 'exposure_matrix.csv', index_col=0)
exposure_full = exposure_full.fillna(0.0)
if 'TOTAL' in exposure_full.columns:
    exposure_full = exposure_full.drop(columns='TOTAL')
if 'UNATTRIBUTED' in exposure_full.index:
    exposure_no_unattr = exposure_full.drop(index='UNATTRIBUTED')
else:
    exposure_no_unattr = exposure_full

coal_exposure_totals = exposure_no_unattr.sum(axis=0).sort_values(ascending=False)
top_coal = coal_exposure_totals.head(10)
print(f"  Top coal firms by bank exposure: {dict(top_coal.head(5).round(1))}")

removal_results = []
for n_remove in [0, 1, 2, 3, 5]:
    firms_to_remove = list(top_coal.head(n_remove).index)

    # Recompute stress test with these firms removed from defaults
    total_loss_15 = 0
    for bank_ticker in exposure_no_unattr.index:
        for coal_ticker in exposure_no_unattr.columns:
            if coal_ticker in firms_to_remove:
                continue
            exp_val = exposure_no_unattr.loc[bank_ticker, coal_ticker]
            if exp_val <= 0:
                continue
            lgd = lgd_lookup.get((coal_ticker, '1.5C'), 0.0)
            total_loss_15 += exp_val * lgd

    removal_results.append({
        'n_removed': n_remove,
        'firms_removed': ', '.join(firms_to_remove) if firms_to_remove else 'None',
        'direct_loss_1_5c_usd_m': round(total_loss_15, 1),
    })
    baseline_loss = removal_results[0]['direct_loss_1_5c_usd_m'] if n_remove == 0 else removal_results[0]['direct_loss_1_5c_usd_m']
    reduction_pct = (1 - total_loss_15 / baseline_loss) * 100 if baseline_loss > 0 else 0
    print(f"  Remove top {n_remove}: direct loss=${total_loss_15:,.1f}M "
          f"(reduction: {reduction_pct:.1f}%)")

pd.DataFrame(removal_results).to_csv(robustness_dir / 'network_removal.csv', index=False)


# ── C7: Calorific Value Normalization ──
print("\n--- C7: CV Normalization (6000 kcal/kg GAR) ---")
cv_results = []
for _, row in valid_coal.iterrows():
    fp = get_firm_params(row)
    if fp is None or pd.isna(fp['cv']):
        continue
    be_adjusted = fp['breakeven'] * (6000 / fp['cv']) if fp['cv'] > 0 else fp['breakeven']
    cv_results.append({
        'ticker': fp['ticker'],
        'cv_kcal_kg': fp['cv'],
        'breakeven_original': fp['breakeven'],
        'breakeven_cv_adjusted': round(be_adjusted, 2),
        'rank_change': 0,  # will compute after sorting
    })

cv_df = pd.DataFrame(cv_results)
cv_df = cv_df.sort_values('breakeven_original').reset_index(drop=True)
cv_df['rank_original'] = range(1, len(cv_df) + 1)
cv_df = cv_df.sort_values('breakeven_cv_adjusted').reset_index(drop=True)
cv_df['rank_adjusted'] = range(1, len(cv_df) + 1)
cv_df = cv_df.sort_values('ticker')
# Merge ranks
orig_ranks = cv_df.sort_values('breakeven_original').reset_index(drop=True)
orig_ranks['rank_original'] = range(1, len(orig_ranks) + 1)
adj_ranks = cv_df.sort_values('breakeven_cv_adjusted').reset_index(drop=True)
adj_ranks['rank_adjusted'] = range(1, len(adj_ranks) + 1)
cv_merged = orig_ranks[['ticker', 'rank_original']].merge(
    adj_ranks[['ticker', 'rank_adjusted']], on='ticker')
cv_df = cv_df.merge(cv_merged, on='ticker', suffixes=('_x', ''))
cv_df['rank_change'] = cv_df['rank_original'] - cv_df['rank_adjusted']
cv_df = cv_df[['ticker', 'cv_kcal_kg', 'breakeven_original', 'breakeven_cv_adjusted',
               'rank_original', 'rank_adjusted', 'rank_change']]
cv_df.to_csv(robustness_dir / 'cv_normalized_curve.csv', index=False)

max_rank_change = cv_df['rank_change'].abs().max()
n_changed = (cv_df['rank_change'] != 0).sum()
print(f"  {n_changed} firms change rank, max change = {max_rank_change} positions")


# ── C8: NPL Shock Sensitivity ──
print("\n--- C8: NPL Shock Sensitivity ---")
npl_results = []
for npl_label, npl_shock_15 in [("Low (7.5%)", 0.075),
                                 ("Baseline (15%)", 0.15),
                                 ("Zero indirect", 0.0)]:
    total_loss_15 = 0
    for bank_ticker in exposure_no_unattr.index:
        # Direct losses (unchanged)
        direct = 0
        for coal_ticker in exposure_no_unattr.columns:
            exp_val = exposure_no_unattr.loc[bank_ticker, coal_ticker]
            if exp_val <= 0:
                continue
            lgd = lgd_lookup.get((coal_ticker, '1.5C'), 0.0)
            direct += exp_val * lgd

        # Indirect losses with varied NPL
        bank_row_data = bank[bank['ticker'] == bank_ticker]
        indirect = 0
        if not bank_row_data.empty:
            br = bank_row_data.iloc[0]
            mining_loans = br.get('mining_loans_usd_m', 0)
            mining_loans = mining_loans if pd.notna(mining_loans) else 0.0
            direct_total = bank_total_direct_exposure.get(bank_ticker, 0.0)
            indirect_mining = max(0.0, mining_loans - direct_total)
            indirect = indirect_mining * npl_shock_15 * LGD_GENERIC

        total_loss_15 += direct + indirect

    npl_results.append({
        'specification': npl_label,
        'npl_shock_1_5c': npl_shock_15,
        'total_loss_1_5c_usd_m': round(total_loss_15, 1),
    })
    print(f"  {npl_label}: total loss=${total_loss_15:,.1f}M")

pd.DataFrame(npl_results).to_csv(robustness_dir / 'npl_shock_sensitivity.csv', index=False)


# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("FINAL SUMMARY: All Revised Numbers")
print("=" * 70)

# Load final data
final_coal = pd.read_csv(OUTPUT_DIR / 'clean_coal_panel.csv')
final_valid = final_coal[final_coal['npv_bau'].notna()]
final_stress = pd.read_csv(OUTPUT_DIR / 'stress_test_summary.csv')
final_macro = pd.read_csv(OUTPUT_DIR / 'macro_impact_summary.csv')

print(f"\n  Coal firms with NPV: {len(final_valid)} (was 27)")
print(f"  Total production: {final_coal['production_mt'].sum():.1f} Mt (was 476.8)")

print(f"\n  Aggregate SV 2C: ${final_valid['sv_2c'].sum()/1000:.1f}B")
print(f"  Aggregate SV 1.5C: ${final_valid['sv_1_5c'].sum()/1000:.1f}B")
print(f"  Expected SV: ${final_valid['expected_sv'].sum()/1000:.1f}B")

print(f"\n  MC 90% CI SV 2C: ${np.percentile(mc_sv_2c, 5)/1000:.1f} - ${np.percentile(mc_sv_2c, 95)/1000:.1f}B")
print(f"  MC Median SV 2C: ${np.median(mc_sv_2c)/1000:.1f}B")
print(f"  MC 90% CI SV 1.5C: ${np.percentile(mc_sv_15, 5)/1000:.1f} - ${np.percentile(mc_sv_15, 95)/1000:.1f}B")
print(f"  MC Median SV 1.5C: ${np.median(mc_sv_15)/1000:.1f}B")
print(f"  MC 90% CI Expected SV: ${np.percentile(mc_esv, 5)/1000:.1f} - ${np.percentile(mc_esv, 95)/1000:.1f}B")
print(f"  MC Median Expected SV: ${np.median(mc_esv)/1000:.1f}B")

for scen in ['BAU', '2C', '1.5C']:
    row = final_stress[final_stress['scenario'] == scen].iloc[0]
    npv_col = {'BAU': 'npv_bau', '2C': 'npv_2c', '1.5C': 'npv_1_5c'}[scen]
    n_def = (final_valid[npv_col] < 0).sum()
    print(f"\n  {scen}: {n_def} defaults, bank loss=${row['total_loss_usd_m']:,.1f}M "
          f"({row['loss_pct_system_equity']:.2f}% equity)")

for _, row in final_macro.iterrows():
    print(f"\n  {row['scenario']}: GDP impact = {row['total_gdp_impact_pct']:.3f}%")
    print(f"    Fiscal: {row['fiscal_gdp_impact_pct']:.4f}%")
    print(f"    Credit: {row['credit_gdp_impact_pct']:.4f}%")
    print(f"    Market: {row['market_gdp_impact_pct']:.4f}%")

# BMRI detail
bmri_15 = stress[(stress['bank_ticker'] == 'BMRI') & (stress['scenario'] == '1.5C')]
if not bmri_15.empty:
    b = bmri_15.iloc[0]
    print(f"\n  BMRI (1.5C): loss=${b['total_loss']:,.1f}M, "
          f"profit={b['profit_impact_pct']:.1f}%, "
          f"CAR impact={b['CAR_impact']*100:.2f}pp")
    # BMRI share of system
    total_sys_loss = final_stress[final_stress['scenario'] == '1.5C'].iloc[0]['total_loss_usd_m']
    bmri_share = b['total_loss'] / total_sys_loss * 100
    print(f"  BMRI share of system loss: {bmri_share:.0f}%")

print("\n" + "=" * 70)
print("ALL COMPUTATIONS COMPLETE")
print("=" * 70)

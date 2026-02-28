"""
09_robustness.py -- Sensitivity and Robustness Analysis
========================================================
Performs deterministic sensitivity analysis (no Monte Carlo) across all
three models to evaluate the robustness of key results to parameter
perturbations.

1. Tornado / sensitivity analysis for Model 1 (Stranded Asset Values)
2. Alternative LGD assumptions for Model 2 (Bank Stress Test)
3. Alternative macro parameters for Model 3 (Macro Transmission)
4. Combined robustness summary table

Outputs (in output/robustness/):
  - tornado_sensitivity.csv
  - bank_stress_sensitivity.csv
  - macro_sensitivity.csv
  - robustness_summary.csv
"""

import sys
import importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
setup = importlib.import_module('00_setup')

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================
# PATHS AND CONSTANTS
# ============================================================
OUTPUT_DIR    = setup.OUTPUT_DIR
COAL_OUTPUT   = setup.COAL_OUTPUT
SCENARIOS     = setup.SCENARIOS
TAX_RATE      = setup.CORPORATE_TAX_RATE   # 0.22
LGD_GENERIC   = setup.LGD_GENERIC          # 0.45
OJK_CAR_MIN   = setup.OJK_CAR_MINIMUM      # 0.08
DSIB_CAR_BUFFER = setup.DSIB_CAR_BUFFER     # 0.105
FX_IDR_USD    = setup.FX_IDR_USD

SCENARIO_NAMES = ['BAU', '2C', '1.5C']

# Macro parameters (from Model 3)
INDONESIA_GDP_USD_B = 1319
FISCAL_MULTIPLIER   = 0.7
CREDIT_GDP_ELASTICITY = 0.06
WEALTH_EFFECT       = 0.03
CREDIT_MULTIPLIER   = 8

# Indirect mining NPL shocks (from Model 2)
DELTA_NPL = {'BAU': 0.005, '2C': 0.05, '1.5C': 0.15}

# Create output directory
ROBUST_DIR = OUTPUT_DIR / "robustness"
ROBUST_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("09: SENSITIVITY AND ROBUSTNESS ANALYSIS")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================
print("\n--- Loading data ---")

coal = pd.read_csv(OUTPUT_DIR / "clean_coal_panel.csv")
print(f"  Coal panel: {len(coal)} companies")

bank_raw = pd.read_csv(OUTPUT_DIR / "clean_bank_panel.csv")
bank = (bank_raw
        .sort_values('year', ascending=False)
        .drop_duplicates(subset='ticker', keep='first')
        .copy())
print(f"  Bank panel: {len(bank)} banks (latest year per bank)")

exposure = pd.read_csv(OUTPUT_DIR / "exposure_matrix.csv", index_col=0).fillna(0.0)
if 'TOTAL' in exposure.columns:
    exposure = exposure.drop(columns='TOTAL')
if 'UNATTRIBUTED' in exposure.index:
    exposure = exposure.drop(index='UNATTRIBUTED')
print(f"  Exposure matrix: {exposure.shape[0]} banks x {exposure.shape[1]} coal companies")

# Load pre-computed stress results and macro results for baseline reference
stress_results = pd.read_csv(OUTPUT_DIR / "bank_stress_results.csv")
stress_summary = pd.read_csv(OUTPUT_DIR / "stress_test_summary.csv")
macro_summary  = pd.read_csv(OUTPUT_DIR / "macro_impact_summary.csv")
agg_sv_mc      = pd.read_csv(OUTPUT_DIR / "aggregate_sv_mc.csv")

print(f"  Bank stress results: {len(stress_results)} rows")
print(f"  Macro summary: {len(macro_summary)} rows")


# ============================================================
# HELPER FUNCTIONS (from Model 1)
# ============================================================

def interpolate_price_path(anchor_dict, max_year):
    """Linearly interpolate annual coal prices from anchor-year dict."""
    years = sorted(anchor_dict.keys())
    prices = [anchor_dict[y] for y in years]
    if max_year > years[-1]:
        years.append(max_year)
        prices.append(prices[-1])
    all_years = np.arange(years[0], max_year + 1)
    all_prices = np.interp(all_years, years, prices)
    return dict(zip(all_years, all_prices))


def compute_npv_single(Q, C, T, r, price_path_array, tax_rate):
    """Compute DCF-based NPV for a single firm (deterministic).

    Parameters
    ----------
    Q : float  -- Annual production (Mt)
    C : float  -- Cash cost per tonne (USD/t)
    T : int    -- Mine life in years
    r : float  -- Discount rate
    price_path_array : np.ndarray -- Annual coal price starting from year 1
    tax_rate : float

    Returns
    -------
    float -- NPV in USD millions
    """
    T = max(1, int(T))
    P = price_path_array[:T]
    t = np.arange(1, T + 1)
    margin = (P - C) * Q                   # USD M per year (Mt * USD/t = M USD)
    after_tax = margin * (1.0 - tax_rate)
    discount = (1.0 + r) ** t
    pv = after_tax / discount
    return pv.sum()


def interpolate_carbon_path(anchor_dict, max_year):
    """Linearly interpolate annual carbon prices from anchor-year dict.
    Carbon prices before first anchor year are 0; after last anchor, held flat."""
    if not anchor_dict:
        return {}
    years = sorted(anchor_dict.keys())
    prices = [anchor_dict[y] for y in years]
    # Prepend year 2025 with price 0 if not present
    if 2025 not in anchor_dict:
        years = [2025] + years
        prices = [0.0] + prices
    if max_year > years[-1]:
        years.append(max_year)
        prices.append(prices[-1])
    all_years = np.arange(years[0], max_year + 1)
    all_prices = np.interp(all_years, years, prices)
    return dict(zip(all_years, all_prices))


def build_price_paths(scenarios, max_mine_life=50, coal_price_shift=0.0,
                      carbon_price_shift=0.0, avg_emissions_factor=0.0):
    """Build interpolated price arrays for each scenario.

    Matches Model 1 (04_model1_stranded_assets.py) by default: uses coal
    prices directly without carbon cost adjustment.  Carbon cost adjustment
    is applied only when avg_emissions_factor > 0, which is used as a
    separate sensitivity lever.

    Parameters
    ----------
    scenarios : dict -- Scenario parameters (from setup.SCENARIOS)
    max_mine_life : int
    coal_price_shift : float -- Multiplicative shift to coal prices (e.g., +0.15 = +15%)
    carbon_price_shift : float -- Additive shift to carbon prices (USD/tCO2)
    avg_emissions_factor : float -- tCO2 per tonne of coal (default 0 = no carbon cost,
                                    matching Model 1 baseline)

    Returns
    -------
    dict -- {scenario_name: np.ndarray of shape (max_mine_life,)}
    """
    price_paths = {}
    for sc_name in SCENARIO_NAMES:
        # Apply coal price shift
        coal_anchors = {y: p * (1.0 + coal_price_shift)
                        for y, p in scenarios[sc_name]['coal_prices'].items()}
        coal_pp = interpolate_price_path(coal_anchors, 2025 + max_mine_life)

        # Build price path for each year
        effective = []
        for y in range(2026, 2026 + max_mine_life):
            coal_p = coal_pp.get(y, coal_pp[max(coal_pp.keys())])

            # Carbon cost adjustment (only when avg_emissions_factor > 0)
            if avg_emissions_factor > 0:
                carbon_anchors_raw = scenarios[sc_name].get('carbon_prices', {})
                carbon_anchors = {yr: max(0, p + carbon_price_shift)
                                  for yr, p in carbon_anchors_raw.items()}
                carbon_pp = interpolate_carbon_path(carbon_anchors, 2025 + max_mine_life)
                carbon_p = carbon_pp.get(y, 0.0) if carbon_pp else 0.0
                coal_p = coal_p - carbon_p * avg_emissions_factor

            effective.append(coal_p)

        price_paths[sc_name] = np.array(effective)
    return price_paths


def compute_aggregate_sv(coal_df, price_paths, tax_rate,
                         disc_shift=0.0, prod_shift=0.0, cost_shift=0.0,
                         life_shift=0, prob_weights=None):
    """Compute aggregate stranded values across all firms (deterministic).

    Parameters
    ----------
    coal_df : DataFrame -- Coal panel
    price_paths : dict -- {scenario: np.ndarray}
    tax_rate : float
    disc_shift : float -- Additive shift to discount rate (pp)
    prod_shift : float -- Multiplicative shift to production (e.g., +0.10)
    cost_shift : float -- Multiplicative shift to cash cost (e.g., +0.15)
    life_shift : int -- Additive shift to mine life (years)
    prob_weights : dict or None -- {BAU: p, 2C: p, 1.5C: p}

    Returns
    -------
    dict with agg_sv_2c, agg_sv_1_5c, expected_sv
    """
    if prob_weights is None:
        prob_weights = {sc: SCENARIOS[sc]['probability'] for sc in SCENARIO_NAMES}

    required = ['production_mt', 'cash_cost_usd_t', 'wacc_base']
    eligible = coal_df.dropna(subset=required).copy()

    total_npv = {sc: 0.0 for sc in SCENARIO_NAMES}

    for _, row in eligible.iterrows():
        Q = row['production_mt'] * (1.0 + prod_shift)
        C = row['cash_cost_usd_t'] * (1.0 + cost_shift)
        r = max(0.01, row['wacc_base'] + disc_shift)
        T_base = row['mine_life_years'] if pd.notna(row.get('mine_life_years')) else 20.0
        T = max(1, int(T_base + life_shift))

        for sc_name in SCENARIO_NAMES:
            npv = compute_npv_single(Q, C, T, r, price_paths[sc_name], tax_rate)
            total_npv[sc_name] += npv

    # Add point estimates for firms without enough data
    skipped = coal_df[coal_df[required].isna().any(axis=1)]
    for _, row in skipped.iterrows():
        for sc_name, col in [('BAU', 'npv_bau'), ('2C', 'npv_2c'), ('1.5C', 'npv_1_5c')]:
            val = row.get(col, np.nan)
            if pd.notna(val):
                total_npv[sc_name] += val

    agg_sv_2c  = total_npv['BAU'] - total_npv['2C']
    agg_sv_15c = total_npv['BAU'] - total_npv['1.5C']
    expected_sv = (prob_weights['BAU'] * 0.0
                   + prob_weights['2C'] * agg_sv_2c
                   + prob_weights['1.5C'] * agg_sv_15c)

    return {
        'agg_sv_2c': agg_sv_2c,
        'agg_sv_1_5c': agg_sv_15c,
        'expected_sv': expected_sv,
        'npv_bau': total_npv['BAU'],
        'npv_2c': total_npv['2C'],
        'npv_1_5c': total_npv['1.5C'],
    }


# ============================================================
# PART 1: TORNADO / SENSITIVITY ANALYSIS FOR MODEL 1
# ============================================================
print("\n" + "=" * 70)
print("PART 1: Tornado Sensitivity Analysis (Model 1 -- Stranded Asset Values)")
print("=" * 70)

max_mine_life = 50

# --- Baseline ---
base_paths = build_price_paths(SCENARIOS, max_mine_life)
baseline = compute_aggregate_sv(coal, base_paths, TAX_RATE)
print(f"\n  Baseline:")
print(f"    NPV BAU:     ${baseline['npv_bau']:>12,.1f} M")
print(f"    NPV 2C:      ${baseline['npv_2c']:>12,.1f} M")
print(f"    NPV 1.5C:    ${baseline['npv_1_5c']:>12,.1f} M")
print(f"    Agg SV 2C:   ${baseline['agg_sv_2c']:>12,.1f} M")
print(f"    Agg SV 1.5C: ${baseline['agg_sv_1_5c']:>12,.1f} M")
print(f"    Expected SV: ${baseline['expected_sv']:>12,.1f} M")

# --- Define perturbations ---
perturbations = [
    # (parameter_name, perturbation_label, kwargs for compute_aggregate_sv, kwargs for build_price_paths)
    ("Discount rate",      "+2pp",   {'disc_shift': +0.02},  {}),
    ("Discount rate",      "-2pp",   {'disc_shift': -0.02},  {}),
    ("Production volume",  "+10%",   {'prod_shift': +0.10},  {}),
    ("Production volume",  "-10%",   {'prod_shift': -0.10},  {}),
    ("Cash cost",          "+15%",   {'cost_shift': +0.15},  {}),
    ("Cash cost",          "-15%",   {'cost_shift': -0.15},  {}),
    ("Mine life",          "+3yr",   {'life_shift': +3},     {}),
    ("Mine life",          "-3yr",   {'life_shift': -3},     {}),
    ("Coal price path",    "+15%",   {},                     {'coal_price_shift': +0.15}),
    ("Coal price path",    "-15%",   {},                     {'coal_price_shift': -0.15}),
    ("Carbon cost internal.", "partial (EF=1.0)",  {},         {'avg_emissions_factor': 1.0}),
    ("Carbon cost internal.", "full (EF=2.2)",     {},         {'avg_emissions_factor': 2.2}),
    ("Scenario weights",   "(0.2, 0.5, 0.3)",
         {'prob_weights': {'BAU': 0.2, '2C': 0.5, '1.5C': 0.3}}, {}),
    ("Scenario weights",   "(0.4, 0.3, 0.3)",
         {'prob_weights': {'BAU': 0.4, '2C': 0.3, '1.5C': 0.3}}, {}),
]

tornado_rows = []

# Add baseline row
tornado_rows.append({
    'parameter': 'Baseline',
    'perturbation': '-',
    'agg_sv_2c': baseline['agg_sv_2c'],
    'agg_sv_1_5c': baseline['agg_sv_1_5c'],
    'expected_sv': baseline['expected_sv'],
    'delta_sv_2c': 0.0,
    'delta_sv_1_5c': 0.0,
})

print(f"\n  Running {len(perturbations)} perturbations...")

for param_name, pert_label, sv_kwargs, pp_kwargs in perturbations:
    # Build price paths (may differ from base)
    pp = build_price_paths(SCENARIOS, max_mine_life, **pp_kwargs)
    result = compute_aggregate_sv(coal, pp, TAX_RATE, **sv_kwargs)

    delta_2c  = result['agg_sv_2c']  - baseline['agg_sv_2c']
    delta_15c = result['agg_sv_1_5c'] - baseline['agg_sv_1_5c']

    tornado_rows.append({
        'parameter': param_name,
        'perturbation': pert_label,
        'agg_sv_2c': result['agg_sv_2c'],
        'agg_sv_1_5c': result['agg_sv_1_5c'],
        'expected_sv': result['expected_sv'],
        'delta_sv_2c': delta_2c,
        'delta_sv_1_5c': delta_15c,
    })

    print(f"    {param_name:22s} {pert_label:20s}  "
          f"SV_2C: ${result['agg_sv_2c']:>12,.1f}M  "
          f"(delta: {delta_2c:>+12,.1f}M)  "
          f"SV_1.5C: ${result['agg_sv_1_5c']:>12,.1f}M  "
          f"(delta: {delta_15c:>+12,.1f}M)")

tornado_df = pd.DataFrame(tornado_rows)
tornado_path = ROBUST_DIR / "tornado_sensitivity.csv"
tornado_df.to_csv(tornado_path, index=False)
print(f"\n  Saved: {tornado_path}")


# ============================================================
# PART 2: ALTERNATIVE LGD ASSUMPTIONS FOR MODEL 2
# ============================================================
print("\n" + "=" * 70)
print("PART 2: Bank Stress Test Sensitivity (Model 2)")
print("=" * 70)


def run_bank_stress(coal_df, bank_df, exposure_df, lgd_generic,
                    default_threshold='npv_lt_0',
                    include_indirect=True):
    """
    Run bank stress test with given parameters.

    Parameters
    ----------
    coal_df : DataFrame
    bank_df : DataFrame -- one row per bank
    exposure_df : DataFrame -- exposure matrix (bank x coal)
    lgd_generic : float -- LGD for indirect mining loans
    default_threshold : str -- 'npv_lt_0' or 'npv_lt_minus10pct'
    include_indirect : bool -- whether to include indirect mining loan losses

    Returns
    -------
    dict -- {scenario: total_loss, total_direct, total_indirect, n_breach_ojk, ...}
    """
    # Step 1: Coal default status
    coal_tickers_in_exposure = [c for c in exposure_df.columns
                                if c in coal_df['ticker'].values]
    npv_cols = {'BAU': 'npv_bau', '2C': 'npv_2c', '1.5C': 'npv_1_5c'}
    sv_cols  = {'2C': 'sv_2c', '1.5C': 'sv_1_5c'}

    lgd_lookup = {}
    for _, row in coal_df.iterrows():
        ticker = row['ticker']
        total_debt   = row.get('total_debt', 0.0)
        total_equity = row.get('total_equity', 0.0)
        total_assets = row.get('total_assets', 0.0)
        total_debt   = total_debt   if pd.notna(total_debt)   else 0.0
        total_equity = total_equity if pd.notna(total_equity) else 0.0
        total_assets = total_assets if pd.notna(total_assets) else 0.0

        for scen in SCENARIO_NAMES:
            npv_val = row.get(npv_cols[scen], np.nan)
            sv_val  = row.get(sv_cols.get(scen, None), np.nan) if scen in sv_cols else 0.0
            sv_val  = sv_val if pd.notna(sv_val) else 0.0

            if pd.isna(npv_val):
                lgd_lookup[(ticker, scen)] = 0.0
                continue

            # Apply default threshold
            if default_threshold == 'npv_lt_0':
                is_default = npv_val < 0
            elif default_threshold == 'npv_lt_minus10pct':
                is_default = npv_val < -0.10 * max(total_assets, 1.0)
            else:
                is_default = npv_val < 0

            if is_default:
                lgd = min(1.0, abs(npv_val) / max(total_debt, 1.0))
            elif sv_val > 0.5 * total_equity and total_equity > 0:
                lgd = 0.3 * sv_val / max(total_assets, 1.0)
            else:
                lgd = 0.0

            lgd_lookup[(ticker, scen)] = lgd

    # Step 2: Direct credit losses
    bank_total_direct_exposure = exposure_df.sum(axis=1)
    results_by_scenario = {}

    for scen in SCENARIO_NAMES:
        total_direct = 0.0
        total_indirect = 0.0

        # Direct losses
        for bank_ticker in exposure_df.index:
            loss = 0.0
            for coal_ticker in exposure_df.columns:
                exp_val = exposure_df.loc[bank_ticker, coal_ticker]
                if exp_val <= 0:
                    continue
                lgd = lgd_lookup.get((coal_ticker, scen), 0.0)
                loss += exp_val * lgd
            total_direct += loss

        # Indirect losses
        if include_indirect:
            for bank_ticker in exposure_df.index:
                bank_row = bank_df[bank_df['ticker'] == bank_ticker]
                if bank_row.empty:
                    continue
                bank_row = bank_row.iloc[0]
                mining_loans = bank_row.get('mining_loans_usd_m', np.nan)
                mining_loans = mining_loans if pd.notna(mining_loans) else 0.0
                direct_total = bank_total_direct_exposure.get(bank_ticker, 0.0)
                indirect_mining = max(0.0, mining_loans - direct_total)
                delta_npl = DELTA_NPL[scen]
                total_indirect += indirect_mining * delta_npl * lgd_generic

        total_loss = total_direct + total_indirect

        # CAR impact (simplified aggregate)
        total_equity = bank_df['total_equity_usd_m'].sum()
        total_rwa = bank_df.apply(
            lambda r: (r['gross_loans_usd_m'] / 0.65
                       if pd.notna(r['gross_loans_usd_m']) and r['gross_loans_usd_m'] > 0
                       else r['total_assets_usd_m'] * 0.80
                       if pd.notna(r['total_assets_usd_m']) else 0),
            axis=1
        ).sum()
        avg_car_impact = (total_loss / total_rwa * 100) if total_rwa > 0 else 0.0
        loss_pct_equity = (total_loss / total_equity * 100) if total_equity > 0 else 0.0

        results_by_scenario[scen] = {
            'total_direct_loss': total_direct,
            'total_indirect_loss': total_indirect,
            'total_loss': total_loss,
            'loss_pct_equity': loss_pct_equity,
            'avg_car_impact_pp': avg_car_impact,
        }

    return results_by_scenario


# --- Define bank stress sensitivity specifications ---
bank_sens_specs = [
    # (spec_label, lgd_generic, default_threshold, include_indirect)
    ("Baseline (LGD=0.45, NPV<0, incl indirect)",      0.45, 'npv_lt_0',          True),
    ("LGD low (0.35)",                                  0.35, 'npv_lt_0',          True),
    ("LGD high (0.55)",                                 0.55, 'npv_lt_0',          True),
    ("Default threshold: NPV < -10% assets",            0.45, 'npv_lt_minus10pct', True),
    ("Exclude indirect mining losses",                  0.45, 'npv_lt_0',          False),
]

bank_sens_rows = []
print(f"\n  Running {len(bank_sens_specs)} bank stress specifications...")

for spec_label, lgd, threshold, incl_indirect in bank_sens_specs:
    res = run_bank_stress(coal, bank, exposure, lgd, threshold, incl_indirect)

    for scen in SCENARIO_NAMES:
        r = res[scen]
        bank_sens_rows.append({
            'specification': spec_label,
            'lgd_generic': lgd,
            'default_threshold': threshold,
            'include_indirect': incl_indirect,
            'scenario': scen,
            'total_direct_loss_usd_m': round(r['total_direct_loss'], 2),
            'total_indirect_loss_usd_m': round(r['total_indirect_loss'], 2),
            'total_loss_usd_m': round(r['total_loss'], 2),
            'loss_pct_equity': round(r['loss_pct_equity'], 4),
            'avg_car_impact_pp': round(r['avg_car_impact_pp'], 4),
        })

    # Print 2C scenario for each specification
    r2c = res['2C']
    r15 = res['1.5C']
    print(f"    {spec_label:55s}  "
          f"2C: ${r2c['total_loss']:>10,.1f}M  "
          f"1.5C: ${r15['total_loss']:>10,.1f}M")

bank_sens_df = pd.DataFrame(bank_sens_rows)
bank_sens_path = ROBUST_DIR / "bank_stress_sensitivity.csv"
bank_sens_df.to_csv(bank_sens_path, index=False)
print(f"\n  Saved: {bank_sens_path}")


# ============================================================
# PART 3: ALTERNATIVE MACRO PARAMETERS FOR MODEL 3
# ============================================================
print("\n" + "=" * 70)
print("PART 3: Macro Transmission Sensitivity (Model 3)")
print("=" * 70)


def run_macro_transmission(coal_df, bank_df, bank_stress_results,
                           fiscal_mult, credit_gdp_elast, wealth_eff,
                           credit_mult):
    """
    Run macro transmission model with given parameters.

    Returns
    -------
    dict -- {scenario: {fiscal_gdp_pct, credit_gdp_pct, market_gdp_pct, total_gdp_pct}}
    """
    gdp_usd_m = INDONESIA_GDP_USD_B * 1000
    bau_price_2030 = SCENARIOS['BAU']['coal_prices'][2030]

    # Prepare coal data
    coal_df = coal_df.copy()
    if 'market_cap' in coal_df.columns:
        coal_df['market_cap_usd_m'] = coal_df['market_cap'] / FX_IDR_USD / 1e6
    elif 'market_cap_usd_m' not in coal_df.columns:
        coal_df['market_cap_usd_m'] = np.nan
    if 'revenue' not in coal_df.columns:
        coal_df['revenue'] = 0.0
    else:
        coal_df['revenue'] = pd.to_numeric(coal_df['revenue'], errors='coerce').fillna(0.0)
    if 'royalty_rate_pct' not in coal_df.columns:
        coal_df['royalty_rate_pct'] = 5.0
    else:
        coal_df['royalty_rate_pct'] = pd.to_numeric(
            coal_df['royalty_rate_pct'], errors='coerce').fillna(5.0)

    # Total bank lending
    total_bank_lending = bank_df['gross_loans_usd_m'].dropna().sum()

    results = {}
    for scen_key in ['2C', '1.5C']:
        scen_price_2030 = SCENARIOS[scen_key]['coal_prices'][2030]
        price_decline = 1.0 - (scen_price_2030 / bau_price_2030)

        # --- Fiscal Channel ---
        coal_df['revenue_loss'] = coal_df['revenue'] * price_decline
        tax_loss = (coal_df['revenue_loss'] * TAX_RATE).sum()
        royalty_loss = (coal_df['revenue_loss'] * coal_df['royalty_rate_pct'] / 100.0).sum()

        ptba_dividend_loss = 0.0
        ptba_mask = coal_df['ticker'] == 'PTBA'
        if ptba_mask.any():
            ptba_mkt_cap = coal_df.loc[ptba_mask, 'market_cap_usd_m'].iloc[0]
            if pd.notna(ptba_mkt_cap) and ptba_mkt_cap > 0:
                ptba_dividend_loss = ptba_mkt_cap * 0.07 * price_decline

        total_fiscal_loss = tax_loss + royalty_loss + ptba_dividend_loss
        fiscal_gdp_impact = (total_fiscal_loss / gdp_usd_m) * fiscal_mult * 100

        # --- Credit Channel ---
        if bank_stress_results is not None and 'scenario' in bank_stress_results.columns:
            scen_stress = bank_stress_results[bank_stress_results['scenario'] == scen_key]
            total_bank_losses = scen_stress['total_loss'].sum()
        else:
            total_bank_losses = 0.0

        credit_contraction = total_bank_losses * credit_mult
        credit_contraction_pct = ((credit_contraction / total_bank_lending) * 100
                                  if total_bank_lending > 0 else 0.0)
        credit_gdp_impact = credit_contraction_pct * credit_gdp_elast

        # --- Market Channel ---
        sv_col = f'sv_{scen_key.lower().replace(".", "_")}'
        coal_market_loss = 0.0
        for _, row in coal_df.iterrows():
            mkt_cap = row.get('market_cap_usd_m', np.nan)
            npv_bau = row.get('npv_bau', np.nan)
            sv = row.get(sv_col, np.nan)
            if pd.isna(mkt_cap) or mkt_cap <= 0 or pd.isna(sv) or pd.isna(npv_bau):
                continue
            if npv_bau <= 0:
                loss_frac = min(abs(sv) / max(abs(npv_bau), 1.0), 1.0)
            else:
                loss_frac = min(sv / npv_bau, 1.0)
            coal_market_loss += min(mkt_cap * loss_frac, mkt_cap)

        bank_market_loss = 0.0
        if bank_stress_results is not None and 'scenario' in bank_stress_results.columns:
            scen_stress = bank_stress_results[bank_stress_results['scenario'] == scen_key]
            for _, brow in scen_stress.iterrows():
                btk = brow.get('bank_ticker', '')
                bloss = brow.get('total_loss', 0.0)
                if pd.isna(bloss) or bloss <= 0:
                    continue
                bmatch = bank_df[bank_df['ticker'] == btk]
                if bmatch.empty:
                    continue
                b_eq = bmatch.iloc[0].get('total_equity_usd_m', np.nan)
                b_mc = bmatch.iloc[0].get('market_cap_usd_m', np.nan)
                if pd.isna(b_eq) or b_eq <= 0 or pd.isna(b_mc) or b_mc <= 0:
                    continue
                bank_market_loss += b_mc * min(bloss / b_eq, 1.0)

        total_market_loss = coal_market_loss + bank_market_loss
        market_gdp_impact = (total_market_loss / gdp_usd_m) * wealth_eff * 100

        total_gdp_impact = fiscal_gdp_impact + credit_gdp_impact + market_gdp_impact

        results[scen_key] = {
            'fiscal_gdp_pct': fiscal_gdp_impact,
            'credit_gdp_pct': credit_gdp_impact,
            'market_gdp_pct': market_gdp_impact,
            'total_gdp_pct': total_gdp_impact,
            'total_bank_loss': total_bank_losses,
        }

    return results


# --- Define macro sensitivity specifications ---
macro_sens_specs = [
    # (label, fiscal_mult, credit_gdp_elast, wealth_eff, credit_mult)
    ("Baseline",                          0.7,  0.06, 0.03,  8),
    ("Fiscal multiplier = 0.5",           0.5,  0.06, 0.03,  8),
    ("Fiscal multiplier = 1.0",           1.0,  0.06, 0.03,  8),
    ("Credit-GDP elasticity = 0.04",      0.7,  0.04, 0.03,  8),
    ("Credit-GDP elasticity = 0.08",      0.7,  0.08, 0.03,  8),
    ("Wealth effect = 0.02",              0.7,  0.06, 0.02,  8),
    ("Wealth effect = 0.05",              0.7,  0.06, 0.05,  8),
    ("Credit multiplier = 6x",            0.7,  0.06, 0.03,  6),
    ("Credit multiplier = 12x",           0.7,  0.06, 0.03, 12),
]

macro_sens_rows = []
print(f"\n  Running {len(macro_sens_specs)} macro specifications...")

for spec_label, fm, cge, we, cm in macro_sens_specs:
    res = run_macro_transmission(coal, bank, stress_results, fm, cge, we, cm)

    for scen_key in ['2C', '1.5C']:
        r = res[scen_key]
        macro_sens_rows.append({
            'specification': spec_label,
            'fiscal_multiplier': fm,
            'credit_gdp_elasticity': cge,
            'wealth_effect': we,
            'credit_multiplier': cm,
            'scenario': scen_key,
            'fiscal_gdp_impact_pct': round(r['fiscal_gdp_pct'], 6),
            'credit_gdp_impact_pct': round(r['credit_gdp_pct'], 6),
            'market_gdp_impact_pct': round(r['market_gdp_pct'], 6),
            'total_gdp_impact_pct':  round(r['total_gdp_pct'], 6),
        })

    r2c = res['2C']
    r15 = res['1.5C']
    print(f"    {spec_label:40s}  "
          f"2C GDP: {r2c['total_gdp_pct']:.4f}%  "
          f"1.5C GDP: {r15['total_gdp_pct']:.4f}%")

macro_sens_df = pd.DataFrame(macro_sens_rows)
macro_sens_path = ROBUST_DIR / "macro_sensitivity.csv"
macro_sens_df.to_csv(macro_sens_path, index=False)
print(f"\n  Saved: {macro_sens_path}")


# ============================================================
# PART 4: COMBINED ROBUSTNESS SUMMARY TABLE
# ============================================================
print("\n" + "=" * 70)
print("PART 4: Combined Robustness Summary")
print("=" * 70)

# Baseline values from pre-computed outputs
baseline_sv_2c  = baseline['agg_sv_2c']
baseline_sv_15c = baseline['agg_sv_1_5c']

# Baseline bank loss from stress_test_summary
baseline_bank_2c  = stress_summary.loc[
    stress_summary['scenario'] == '2C', 'total_loss_usd_m'].values
baseline_bank_2c  = baseline_bank_2c[0] if len(baseline_bank_2c) > 0 else np.nan
baseline_bank_15c = stress_summary.loc[
    stress_summary['scenario'] == '1.5C', 'total_loss_usd_m'].values
baseline_bank_15c = baseline_bank_15c[0] if len(baseline_bank_15c) > 0 else np.nan

# Baseline macro GDP impact
baseline_gdp_2c  = macro_summary.loc[
    macro_summary['scenario'] == '2C', 'total_gdp_impact_pct'].values
baseline_gdp_2c  = baseline_gdp_2c[0] if len(baseline_gdp_2c) > 0 else np.nan
baseline_gdp_15c = macro_summary.loc[
    macro_summary['scenario'] == '1.5C', 'total_gdp_impact_pct'].values
baseline_gdp_15c = baseline_gdp_15c[0] if len(baseline_gdp_15c) > 0 else np.nan

# Build summary rows
summary_rows = []

# --- Baseline ---
summary_rows.append({
    'specification': 'Baseline',
    'agg_sv_2c_B': baseline_sv_2c / 1000,
    'agg_sv_1_5c_B': baseline_sv_15c / 1000,
    'bank_loss_2c_B': baseline_bank_2c / 1000 if pd.notna(baseline_bank_2c) else np.nan,
    'bank_loss_1_5c_B': baseline_bank_15c / 1000 if pd.notna(baseline_bank_15c) else np.nan,
    'gdp_impact_2c_pct': baseline_gdp_2c,
    'gdp_impact_1_5c_pct': baseline_gdp_15c,
})

# --- Key SV perturbations ---
key_sv_perts = [
    ("Discount rate +2pp",   {'disc_shift': +0.02},  {}),
    ("Discount rate -2pp",   {'disc_shift': -0.02},  {}),
    ("Production +10%",      {'prod_shift': +0.10},  {}),
    ("Production -10%",      {'prod_shift': -0.10},  {}),
    ("Cash cost +15%",       {'cost_shift': +0.15},  {}),
    ("Cash cost -15%",       {'cost_shift': -0.15},  {}),
    ("Mine life +3yr",       {'life_shift': +3},     {}),
    ("Mine life -3yr",       {'life_shift': -3},     {}),
    ("Coal price +15%",      {},                     {'coal_price_shift': +0.15}),
    ("Coal price -15%",      {},                     {'coal_price_shift': -0.15}),
]

for spec_name, sv_kw, pp_kw in key_sv_perts:
    pp = build_price_paths(SCENARIOS, max_mine_life, **pp_kw)
    res = compute_aggregate_sv(coal, pp, TAX_RATE, **sv_kw)
    summary_rows.append({
        'specification': spec_name,
        'agg_sv_2c_B': res['agg_sv_2c'] / 1000,
        'agg_sv_1_5c_B': res['agg_sv_1_5c'] / 1000,
        'bank_loss_2c_B': baseline_bank_2c / 1000 if pd.notna(baseline_bank_2c) else np.nan,
        'bank_loss_1_5c_B': baseline_bank_15c / 1000 if pd.notna(baseline_bank_15c) else np.nan,
        'gdp_impact_2c_pct': baseline_gdp_2c,
        'gdp_impact_1_5c_pct': baseline_gdp_15c,
    })

# --- Key bank stress perturbations ---
for spec_label, lgd, threshold, incl_indirect in bank_sens_specs[1:]:
    res = run_bank_stress(coal, bank, exposure, lgd, threshold, incl_indirect)
    bank_2c = res['2C']['total_loss']
    bank_15c = res['1.5C']['total_loss']

    # Re-run macro with adjusted bank losses
    macro_res = run_macro_transmission(coal, bank, stress_results,
                                       FISCAL_MULTIPLIER, CREDIT_GDP_ELASTICITY,
                                       WEALTH_EFFECT, CREDIT_MULTIPLIER)
    summary_rows.append({
        'specification': spec_label,
        'agg_sv_2c_B': baseline_sv_2c / 1000,
        'agg_sv_1_5c_B': baseline_sv_15c / 1000,
        'bank_loss_2c_B': bank_2c / 1000,
        'bank_loss_1_5c_B': bank_15c / 1000,
        'gdp_impact_2c_pct': macro_res['2C']['total_gdp_pct'],
        'gdp_impact_1_5c_pct': macro_res['1.5C']['total_gdp_pct'],
    })

# --- Key macro perturbations ---
for spec_label, fm, cge, we, cm in macro_sens_specs[1:]:
    res = run_macro_transmission(coal, bank, stress_results, fm, cge, we, cm)
    summary_rows.append({
        'specification': f"Macro: {spec_label}",
        'agg_sv_2c_B': baseline_sv_2c / 1000,
        'agg_sv_1_5c_B': baseline_sv_15c / 1000,
        'bank_loss_2c_B': baseline_bank_2c / 1000 if pd.notna(baseline_bank_2c) else np.nan,
        'bank_loss_1_5c_B': baseline_bank_15c / 1000 if pd.notna(baseline_bank_15c) else np.nan,
        'gdp_impact_2c_pct': res['2C']['total_gdp_pct'],
        'gdp_impact_1_5c_pct': res['1.5C']['total_gdp_pct'],
    })

summary_df = pd.DataFrame(summary_rows)

# Round for readability
for col in ['agg_sv_2c_B', 'agg_sv_1_5c_B', 'bank_loss_2c_B', 'bank_loss_1_5c_B']:
    if col in summary_df.columns:
        summary_df[col] = summary_df[col].round(3)
for col in ['gdp_impact_2c_pct', 'gdp_impact_1_5c_pct']:
    if col in summary_df.columns:
        summary_df[col] = summary_df[col].round(6)

summary_path = ROBUST_DIR / "robustness_summary.csv"
summary_df.to_csv(summary_path, index=False)
print(f"\n  Saved: {summary_path}")

# --- Print the summary table ---
print(f"\n  {'Specification':<45s}  {'SV_2C ($B)':>12s}  {'SV_1.5C ($B)':>13s}  "
      f"{'BankLoss_2C ($B)':>16s}  {'GDP_2C (%)':>11s}  {'GDP_1.5C (%)':>12s}")
print("  " + "-" * 115)
for _, r in summary_df.iterrows():
    sv2 = f"${r['agg_sv_2c_B']:>9,.2f}" if pd.notna(r['agg_sv_2c_B']) else "N/A"
    sv15 = f"${r['agg_sv_1_5c_B']:>9,.2f}" if pd.notna(r['agg_sv_1_5c_B']) else "N/A"
    bl2 = f"${r['bank_loss_2c_B']:>9,.3f}" if pd.notna(r['bank_loss_2c_B']) else "N/A"
    gdp2 = f"{r['gdp_impact_2c_pct']:>9.4f}%" if pd.notna(r['gdp_impact_2c_pct']) else "N/A"
    gdp15 = f"{r['gdp_impact_1_5c_pct']:>9.4f}%" if pd.notna(r['gdp_impact_1_5c_pct']) else "N/A"
    print(f"  {r['specification']:<45s}  {sv2:>12s}  {sv15:>13s}  {bl2:>16s}  {gdp2:>11s}  {gdp15:>12s}")


# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("ROBUSTNESS ANALYSIS COMPLETE")
print("=" * 70)
print(f"\n  Output files:")
print(f"    1. {tornado_path}")
print(f"    2. {bank_sens_path}")
print(f"    3. {macro_sens_path}")
print(f"    4. {summary_path}")

# Range of SV estimates
sv_2c_vals = tornado_df[tornado_df['parameter'] != 'Baseline']['agg_sv_2c']
sv_15c_vals = tornado_df[tornado_df['parameter'] != 'Baseline']['agg_sv_1_5c']
print(f"\n  Stranded Value 2C range:   ${sv_2c_vals.min():>12,.1f}M -- ${sv_2c_vals.max():>12,.1f}M  "
      f"(baseline: ${baseline['agg_sv_2c']:>12,.1f}M)")
print(f"  Stranded Value 1.5C range: ${sv_15c_vals.min():>12,.1f}M -- ${sv_15c_vals.max():>12,.1f}M  "
      f"(baseline: ${baseline['agg_sv_1_5c']:>12,.1f}M)")

# Range of GDP impacts
gdp_vals_2c = macro_sens_df[macro_sens_df['scenario'] == '2C']['total_gdp_impact_pct']
gdp_vals_15c = macro_sens_df[macro_sens_df['scenario'] == '1.5C']['total_gdp_impact_pct']
print(f"  GDP impact 2C range:       {gdp_vals_2c.min():.4f}% -- {gdp_vals_2c.max():.4f}%  "
      f"(baseline: {baseline_gdp_2c:.4f}%)" if pd.notna(baseline_gdp_2c) else "")
print(f"  GDP impact 1.5C range:     {gdp_vals_15c.min():.4f}% -- {gdp_vals_15c.max():.4f}%  "
      f"(baseline: {baseline_gdp_15c:.4f}%)" if pd.notna(baseline_gdp_15c) else "")

print(f"\n{'='*70}")
print("Script 09 complete.")
print(f"{'='*70}")

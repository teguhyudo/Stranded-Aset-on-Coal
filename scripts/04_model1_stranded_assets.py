"""
04_model1_stranded_assets.py -- Model 1: Stranded Asset Valuation with Monte Carlo Uncertainty
===============================================================================================
Adds Monte Carlo uncertainty quantification to the existing stranded-value calculations
in clean_coal_panel.csv.  For each coal company with sufficient operational data, draws
10,000 realisations of production, cost, mine life, discount rate, and scenario
probabilities, then computes NPV and stranded-value distributions.

Outputs (in setup.OUTPUT_DIR):
  1. stranded_values_mc.csv       -- Per-firm Monte Carlo percentiles
  2. aggregate_sv_mc.csv          -- Sector-level aggregate with CI
  3. supply_cost_curve_final.csv  -- Sorted by breakeven for plotting
"""

import sys
import importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
setup = importlib.import_module('00_setup')

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants from setup
# ---------------------------------------------------------------------------
OUTPUT_DIR    = setup.OUTPUT_DIR
COAL_OUTPUT   = setup.COAL_OUTPUT
SCENARIOS     = setup.SCENARIOS
MC_SEED       = setup.MC_SEED
MC_N          = setup.MC_N_SIMULATIONS
TAX_RATE      = setup.CORPORATE_TAX_RATE

SCENARIO_NAMES = ['BAU', '2C', '1.5C']
DIRICHLET_ALPHA = np.array([3.0, 4.0, 3.0])  # BAU, 2C, 1.5C


# ============================================================
# Helper functions
# ============================================================

def interpolate_price_path(anchor_dict, max_year):
    """Linearly interpolate annual coal prices from anchor-year dict.

    Parameters
    ----------
    anchor_dict : dict
        {year: price} pairs (e.g. {2025: 130, 2030: 120, ...})
    max_year : int
        Last year to generate (inclusive).

    Returns
    -------
    dict
        {year: price} for every integer year from min(anchor) to max_year.
    """
    years = sorted(anchor_dict.keys())
    prices = [anchor_dict[y] for y in years]
    # Extend to max_year if needed
    if max_year > years[-1]:
        years.append(max_year)
        prices.append(prices[-1])  # flat extrapolation beyond last anchor
    all_years = np.arange(years[0], max_year + 1)
    all_prices = np.interp(all_years, years, prices)
    return dict(zip(all_years, all_prices))


def compute_npv_vectorised(Q, C, T_int, r, price_path_array, tax_rate):
    """Compute DCF-based NPV for a single firm across N simulations.

    Parameters
    ----------
    Q : np.ndarray, shape (N,)
        Annual production (Mt).
    C : np.ndarray, shape (N,)
        Cash cost per tonne (USD/t).
    T_int : np.ndarray, shape (N,), dtype int
        Mine life in years (integer, clipped >= 1).
    r : np.ndarray, shape (N,)
        Discount rate.
    price_path_array : np.ndarray, shape (max_T,)
        Annual coal price starting from year 1 (index 0 = year 1).
    tax_rate : float

    Returns
    -------
    np.ndarray, shape (N,)
        NPV in USD millions.
    """
    N = len(Q)
    max_T = int(T_int.max())
    # Prices for years 1..max_T  (index 0 = year 1 = 2026, etc.)
    P = price_path_array[:max_T]  # shape (max_T,)

    # Build time grid: shape (N, max_T)
    t_grid = np.arange(1, max_T + 1)[np.newaxis, :]            # (1, max_T)
    mask = t_grid <= T_int[:, np.newaxis]                        # (N, max_T)

    # Revenue minus cost per tonne, after tax
    # Q is in Mt, prices in USD/t  => revenue in USD M  (Mt * USD/t = M USD)
    margin = (P[np.newaxis, :] - C[:, np.newaxis]) * Q[:, np.newaxis]  # (N, max_T)
    after_tax = margin * (1.0 - tax_rate)

    # Discount factors
    discount = (1.0 + r[:, np.newaxis]) ** t_grid  # (N, max_T)
    pv = after_tax / discount  # (N, max_T)

    # Zero out periods beyond mine life
    pv = np.where(mask, pv, 0.0)

    return pv.sum(axis=1)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("04: MODEL 1 -- STRANDED ASSET VALUATION WITH MONTE CARLO UNCERTAINTY")
    print("=" * 70)

    rng = np.random.default_rng(MC_SEED)

    # ------------------------------------------------------------------
    # Part A: Load data
    # ------------------------------------------------------------------
    print("\n--- Part A: Load data ---")
    panel = pd.read_csv(OUTPUT_DIR / "clean_coal_panel.csv")
    print(f"Loaded clean_coal_panel.csv: {len(panel)} firms, {panel.shape[1]} columns")

    scenario_params = pd.read_csv(COAL_OUTPUT / "scenario_parameters.csv")
    print(f"Loaded scenario_parameters.csv: {len(scenario_params)} rows")
    print(f"  Scenarios: {scenario_params['Scenario'].tolist()}")

    # Report production data status
    n_with_prod = panel['production_mt'].notna().sum()
    n_with_cost = panel['cash_cost_usd_t'].notna().sum()
    n_with_wacc = panel['wacc_base'].notna().sum()
    print(f"\n  Firms with verified production: {n_with_prod}")
    print(f"  Firms with cost data: {n_with_cost}")
    print(f"  Firms with WACC: {n_with_wacc}")

    # ------------------------------------------------------------------
    # Part B: Monte Carlo Simulation
    # ------------------------------------------------------------------
    print(f"\n--- Part B: Monte Carlo Simulation ({MC_N:,} draws per firm) ---")

    # Build interpolated price paths for each scenario (years 2026..2075)
    # Year 1 of the DCF corresponds to 2026
    max_mine_life = 50  # safety ceiling
    price_paths = {}
    for sc_name in SCENARIO_NAMES:
        anchors = SCENARIOS[sc_name]['coal_prices']
        pp = interpolate_price_path(anchors, 2025 + max_mine_life)
        # Convert to array starting at year 2026
        price_paths[sc_name] = np.array([pp.get(y, pp[max(pp.keys())])
                                          for y in range(2026, 2026 + max_mine_life)])

    # Determine which firms are eligible for Monte Carlo
    required_cols = ['production_mt', 'cash_cost_usd_t', 'wacc_base']
    eligible_mask = panel[required_cols].notna().all(axis=1)
    eligible = panel.loc[eligible_mask].copy()
    skipped  = panel.loc[~eligible_mask].copy()
    print(f"  Firms eligible for MC:  {len(eligible)}")
    print(f"  Firms skipped (missing data): {len(skipped)}")
    if len(skipped) > 0:
        print(f"    Skipped tickers: {skipped['ticker'].tolist()}")

    # Storage for per-firm results
    mc_results = []

    for idx, row in eligible.iterrows():
        ticker = row['ticker']
        Q_bar  = row['production_mt']
        C_bar  = row['cash_cost_usd_t']
        r_bar  = row['wacc_base']
        T_bar  = row['mine_life_years'] if pd.notna(row.get('mine_life_years')) else 20.0

        # ------- Draw parameters -------
        # Q: Normal(Q_bar, 0.10 * Q_bar), clipped > 0
        Q_sim = rng.normal(Q_bar, 0.10 * Q_bar, size=MC_N)
        Q_sim = np.clip(Q_sim, 0.01, None)

        # C: Normal(C_bar, 0.15 * C_bar), bounded below by 0
        C_sim = rng.normal(C_bar, 0.15 * C_bar, size=MC_N)
        C_sim = np.clip(C_sim, 0.0, None)

        # T: Triangular(max(5, T_bar-5), T_bar, T_bar+5), integer
        T_lo = max(5.0, T_bar - 5.0)
        T_mode = T_bar
        T_hi = T_bar + 5.0
        T_sim = rng.triangular(T_lo, T_mode, T_hi, size=MC_N)
        T_sim = np.clip(np.round(T_sim).astype(int), 1, max_mine_life)

        # r: Uniform(r_bar - 0.02, r_bar + 0.02)
        r_lo = max(0.01, r_bar - 0.02)
        r_hi = r_bar + 0.02
        r_sim = rng.uniform(r_lo, r_hi, size=MC_N)

        # pi: Dirichlet(3, 4, 3) -- scenario probability weights
        pi_sim = rng.dirichlet(DIRICHLET_ALPHA, size=MC_N)  # (N, 3)

        # ------- Compute NPV per scenario -------
        npv_sc = {}
        for j, sc_name in enumerate(SCENARIO_NAMES):
            npv_sc[sc_name] = compute_npv_vectorised(
                Q_sim, C_sim, T_sim, r_sim, price_paths[sc_name], TAX_RATE
            )

        # ------- Stranded value -------
        sv_2c  = npv_sc['BAU'] - npv_sc['2C']
        sv_15c = npv_sc['BAU'] - npv_sc['1.5C']

        # Expected SV (probability-weighted across scenarios)
        # E[SV] = pi_BAU * 0 + pi_2C * SV_2C + pi_1.5C * SV_1.5C
        expected_sv = pi_sim[:, 1] * sv_2c + pi_sim[:, 2] * sv_15c

        # ------- Collect percentiles -------
        pcts = [5, 25, 50, 75, 95]
        result = {'ticker': ticker, 'Company_Name': row['Company_Name']}

        for sc_name in SCENARIO_NAMES:
            for p in pcts:
                result[f'npv_{sc_name}_p{p}'] = np.percentile(npv_sc[sc_name], p)

        for label, arr in [('sv_2c', sv_2c), ('sv_1_5c', sv_15c)]:
            for p in [5, 50, 95]:
                result[f'{label}_p{p}'] = np.percentile(arr, p)

        for p in [5, 50, 95]:
            result[f'expected_sv_p{p}'] = np.percentile(expected_sv, p)

        # Also store mean for aggregation
        result['npv_bau_mean'] = npv_sc['BAU'].mean()
        result['sv_2c_mean']   = sv_2c.mean()
        result['sv_1_5c_mean'] = sv_15c.mean()
        result['expected_sv_mean'] = expected_sv.mean()

        # Point estimates from panel for reference
        result['npv_bau_point'] = row.get('npv_bau', np.nan)
        result['sv_2c_point']   = row.get('sv_2c', np.nan)
        result['sv_1_5c_point'] = row.get('sv_1_5c', np.nan)

        mc_results.append(result)

    mc_df = pd.DataFrame(mc_results)
    print(f"\n  MC completed for {len(mc_df)} firms.")

    # Add skipped firms (no production/cost/WACC) with NaN values
    if len(skipped) > 0:
        skip_records = []
        for _, row in skipped.iterrows():
            rec = {'ticker': row['ticker'], 'Company_Name': row['Company_Name']}
            for sc_label in ['BAU', '2C', '1.5C']:
                for p in [5, 25, 50, 75, 95]:
                    rec[f'npv_{sc_label}_p{p}'] = np.nan
            for label in ['sv_2c', 'sv_1_5c']:
                for p in [5, 50, 95]:
                    rec[f'{label}_p{p}'] = np.nan
            for p in [5, 50, 95]:
                rec[f'expected_sv_p{p}'] = np.nan
            rec['npv_bau_mean'] = np.nan
            rec['sv_2c_mean'] = np.nan
            rec['sv_1_5c_mean'] = np.nan
            rec['expected_sv_mean'] = np.nan
            rec['npv_bau_point'] = np.nan
            rec['sv_2c_point'] = np.nan
            rec['sv_1_5c_point'] = np.nan
            skip_records.append(rec)

        skip_df = pd.DataFrame(skip_records)
        mc_df = pd.concat([mc_df, skip_df], ignore_index=True)
        print(f"  Added {len(skip_df)} skipped firms (NaN -- no verified production).")

    # Save per-firm MC results
    mc_out = OUTPUT_DIR / "stranded_values_mc.csv"
    mc_df.to_csv(mc_out, index=False)
    print(f"\n  Saved: {mc_out}")

    # ------------------------------------------------------------------
    # Part C: Aggregate results
    # ------------------------------------------------------------------
    print("\n--- Part C: Aggregate results ---")

    # Re-run the full MC to get aggregate distribution (sum across firms)
    # We need the raw simulation arrays, so we repeat but store them
    print("  Running aggregate MC (summing across all eligible firms)...")

    # Arrays to accumulate sums: shape (MC_N,)
    total_npv = {sc: np.zeros(MC_N) for sc in SCENARIO_NAMES}
    total_sv_2c  = np.zeros(MC_N)
    total_sv_15c = np.zeros(MC_N)
    total_esv    = np.zeros(MC_N)

    # Reset RNG for reproducibility (same seed, same sequence)
    rng2 = np.random.default_rng(MC_SEED)

    for idx, row in eligible.iterrows():
        Q_bar = row['production_mt']
        C_bar = row['cash_cost_usd_t']
        r_bar = row['wacc_base']
        T_bar = row['mine_life_years'] if pd.notna(row.get('mine_life_years')) else 20.0

        Q_sim = np.clip(rng2.normal(Q_bar, 0.10 * Q_bar, size=MC_N), 0.01, None)
        C_sim = np.clip(rng2.normal(C_bar, 0.15 * C_bar, size=MC_N), 0.0, None)
        T_lo = max(5.0, T_bar - 5.0)
        T_sim = np.clip(np.round(rng2.triangular(T_lo, T_bar, T_bar + 5.0,
                                                  size=MC_N)).astype(int),
                        1, max_mine_life)
        r_sim = rng2.uniform(max(0.01, r_bar - 0.02), r_bar + 0.02, size=MC_N)
        pi_sim = rng2.dirichlet(DIRICHLET_ALPHA, size=MC_N)

        npv_sc = {}
        for j, sc_name in enumerate(SCENARIO_NAMES):
            npv_sc[sc_name] = compute_npv_vectorised(
                Q_sim, C_sim, T_sim, r_sim, price_paths[sc_name], TAX_RATE)
            total_npv[sc_name] += npv_sc[sc_name]

        sv_2c  = npv_sc['BAU'] - npv_sc['2C']
        sv_15c = npv_sc['BAU'] - npv_sc['1.5C']
        esv    = pi_sim[:, 1] * sv_2c + pi_sim[:, 2] * sv_15c

        total_sv_2c  += sv_2c
        total_sv_15c += sv_15c
        total_esv    += esv

    # Skipped firms have no production data -- they contribute zero to aggregates.
    # (Previously used fallback point estimates; now all NaN since production is NaN.)
    print(f"  Skipped firms ({len(skipped)}) contribute zero to aggregates "
          f"(no verified production data).")

    # Build aggregate table
    agg_rows = []
    for sc_name in SCENARIO_NAMES:
        agg_rows.append({
            'metric': f'Total NPV {sc_name}',
            'unit': 'USD M',
            'p5':     np.percentile(total_npv[sc_name], 5),
            'p25':    np.percentile(total_npv[sc_name], 25),
            'median': np.percentile(total_npv[sc_name], 50),
            'p75':    np.percentile(total_npv[sc_name], 75),
            'p95':    np.percentile(total_npv[sc_name], 95),
            'mean':   total_npv[sc_name].mean(),
        })

    for label, arr in [('Total SV 2C', total_sv_2c),
                        ('Total SV 1.5C', total_sv_15c),
                        ('Total Expected SV', total_esv)]:
        agg_rows.append({
            'metric': label,
            'unit': 'USD M',
            'p5':     np.percentile(arr, 5),
            'p25':    np.percentile(arr, 25),
            'median': np.percentile(arr, 50),
            'p75':    np.percentile(arr, 75),
            'p95':    np.percentile(arr, 95),
            'mean':   arr.mean(),
        })

    agg_df = pd.DataFrame(agg_rows)
    agg_out = OUTPUT_DIR / "aggregate_sv_mc.csv"
    agg_df.to_csv(agg_out, index=False)
    print(f"  Saved: {agg_out}")

    print("\n  Aggregate Monte Carlo results (USD M):")
    print("  " + "-" * 80)
    for _, r in agg_df.iterrows():
        print(f"  {r['metric']:<25s}  "
              f"median: {r['median']:>12,.1f}   "
              f"[p5: {r['p5']:>12,.1f},  p95: {r['p95']:>12,.1f}]")

    # ------------------------------------------------------------------
    # Part D: Supply cost curve data
    # ------------------------------------------------------------------
    print("\n--- Part D: Supply cost curve data ---")

    scc = panel[['ticker', 'Company_Name', 'breakeven_usd_t', 'production_mt']].copy()
    scc = scc.dropna(subset=['breakeven_usd_t', 'production_mt'])
    scc = scc.sort_values('breakeven_usd_t').reset_index(drop=True)
    scc['cumulative_production_mt'] = scc['production_mt'].cumsum()
    scc_out = OUTPUT_DIR / "supply_cost_curve_final.csv"
    scc.to_csv(scc_out, index=False)
    print(f"  {len(scc)} firms with breakeven + production data")
    print(f"  Saved: {scc_out}")

    if len(scc) > 0:
        print(f"\n  Lowest breakeven:  {scc['ticker'].iloc[0]:>6s}  "
              f"${scc['breakeven_usd_t'].iloc[0]:,.1f}/t")
        print(f"  Highest breakeven: {scc['ticker'].iloc[-1]:>6s}  "
              f"${scc['breakeven_usd_t'].iloc[-1]:,.1f}/t")
        print(f"  Total production:  {scc['production_mt'].sum():,.1f} Mt")

    # ------------------------------------------------------------------
    # Print key results
    # ------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("KEY RESULTS -- Model 1: Stranded Asset Valuation")
    print("=" * 70)

    # Per-firm top-5 by median SV (2C)
    mc_eligible = mc_df[mc_df['sv_2c_p50'].notna()].copy()
    if len(mc_eligible) > 0:
        top5_2c = mc_eligible.nlargest(5, 'sv_2c_p50')
        print("\nTop 5 firms by median SV under 2C scenario:")
        for _, r in top5_2c.iterrows():
            lo = r.get('sv_2c_p5', np.nan)
            med = r.get('sv_2c_p50', np.nan)
            hi = r.get('sv_2c_p95', np.nan)
            print(f"  {r['ticker']:>6s}  median: ${med:>10,.1f}M  "
                  f"[90% CI: ${lo:>10,.1f}M -- ${hi:>10,.1f}M]")

    # Aggregate headline
    sv_2c_row = agg_df[agg_df['metric'] == 'Total SV 2C']
    sv_15_row = agg_df[agg_df['metric'] == 'Total SV 1.5C']
    esv_row   = agg_df[agg_df['metric'] == 'Total Expected SV']

    if len(sv_2c_row) > 0:
        r = sv_2c_row.iloc[0]
        print(f"\nTotal Stranded Value (2C):")
        print(f"  Median: ${r['median']:>12,.1f}M  "
              f"[90% CI: ${r['p5']:>12,.1f}M -- ${r['p95']:>12,.1f}M]")

    if len(sv_15_row) > 0:
        r = sv_15_row.iloc[0]
        print(f"Total Stranded Value (1.5C):")
        print(f"  Median: ${r['median']:>12,.1f}M  "
              f"[90% CI: ${r['p5']:>12,.1f}M -- ${r['p95']:>12,.1f}M]")

    if len(esv_row) > 0:
        r = esv_row.iloc[0]
        print(f"Total Expected Stranded Value (probability-weighted):")
        print(f"  Median: ${r['median']:>12,.1f}M  "
              f"[90% CI: ${r['p5']:>12,.1f}M -- ${r['p95']:>12,.1f}M]")

    # ------------------------------------------------------------------
    # Part E: Write NPV/SV back to clean_coal_panel.csv
    # ------------------------------------------------------------------
    print("\n--- Part E: Updating clean_coal_panel.csv with computed NPV/SV ---")

    # Map MC median values back to panel
    mc_medians = mc_df[['ticker', 'npv_BAU_p50', 'npv_2C_p50', 'npv_1.5C_p50',
                         'sv_2c_p50', 'sv_1_5c_p50', 'expected_sv_p50']].copy()
    mc_medians = mc_medians.rename(columns={
        'npv_BAU_p50': 'npv_bau',
        'npv_2C_p50': 'npv_2c',
        'npv_1.5C_p50': 'npv_1_5c',
        'sv_2c_p50': 'sv_2c',
        'sv_1_5c_p50': 'sv_1_5c',
        'expected_sv_p50': 'expected_sv',
    })

    # Update panel with MC median values
    for col in ['npv_bau', 'npv_2c', 'npv_1_5c', 'sv_2c', 'sv_1_5c', 'expected_sv']:
        panel[col] = np.nan  # reset
    for _, mc_row in mc_medians.iterrows():
        mask = panel['ticker'] == mc_row['ticker']
        if mask.any():
            for col in ['npv_bau', 'npv_2c', 'npv_1_5c',
                         'sv_2c', 'sv_1_5c', 'expected_sv']:
                panel.loc[mask, col] = mc_row[col]

    # Recompute derived flags
    panel['stranded_2c'] = panel['npv_2c'] < 0
    panel['stranded_1_5c'] = panel['npv_1_5c'] < 0
    if 'total_assets' in panel.columns:
        panel['sv_2c_pct_assets'] = (
            panel['sv_2c'] /
            panel['total_assets'].replace(0, np.nan) * 100
        )
        panel['sv_1_5c_pct_assets'] = (
            panel['sv_1_5c'] /
            panel['total_assets'].replace(0, np.nan) * 100
        )

    panel_out = OUTPUT_DIR / "clean_coal_panel.csv"
    panel.to_csv(panel_out, index=False)
    print(f"  Updated: {panel_out}")
    print(f"  Firms with NPV: {panel['npv_bau'].notna().sum()}")
    n2c = panel['stranded_2c'].sum()
    n15 = panel['stranded_1_5c'].sum()
    print(f"  Stranded under 2C: {n2c}")
    print(f"  Stranded under 1.5C: {n15}")

    mc_med_2c  = agg_df.loc[agg_df['metric'] == 'Total SV 2C', 'median'].iloc[0]
    mc_med_15c = agg_df.loc[agg_df['metric'] == 'Total SV 1.5C', 'median'].iloc[0]
    print(f"\nMC median aggregate:")
    print(f"  SV 2C:   ${mc_med_2c:>12,.1f}M")
    print(f"  SV 1.5C: ${mc_med_15c:>12,.1f}M")

    print("\n" + "=" * 70)
    print("Model 1 complete.")
    print("=" * 70)

    return mc_df, agg_df, scc


if __name__ == "__main__":
    main()

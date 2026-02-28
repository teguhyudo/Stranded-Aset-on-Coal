"""
06_model3_macro_transmission.py -- Model 3: Macro-Financial Transmission
=========================================================================
Estimates GDP impact of coal stranding through three transmission channels:
  1. Fiscal Channel   -- tax, royalty, and SOE dividend revenue losses
  2. Credit Channel   -- bank deleveraging from capital losses
  3. Market Channel   -- equity value destruction (wealth effect)

Outputs:
  - macro_channel_details.csv   (per-channel breakdown by scenario)
  - macro_impact_summary.csv    (summary with sub-channel details)
"""

import sys, importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
setup = importlib.import_module('00_setup')

import numpy as np
import pandas as pd

# ============================================================
# PARAMETERS
# ============================================================
OUTPUT_DIR = setup.OUTPUT_DIR
COAL_OUTPUT = setup.COAL_OUTPUT
SCENARIOS = setup.SCENARIOS
CORPORATE_TAX_RATE = setup.CORPORATE_TAX_RATE  # 0.22

# Indonesia macro parameters (2023 estimates)
INDONESIA_GDP_USD_B = 1319          # GDP in USD billions
INDONESIA_GOV_REVENUE_USD_B = 190   # Total government revenue
INDONESIA_COAL_TAX_REVENUE_USD_B = 8.5  # Coal sector tax + royalty revenue
FISCAL_MULTIPLIER = 0.7            # Government spending multiplier
CREDIT_GDP_ELASTICITY = 0.06       # 1% credit contraction -> 0.06% GDP decline
WEALTH_EFFECT = 0.03               # 1% market cap loss -> 0.03% consumption decline
CREDIT_MULTIPLIER = 8              # Bank capital loss -> credit contraction multiplier

# IDR/USD for market cap conversion (coal panel market_cap is in IDR)
FX_IDR_USD = setup.FX_IDR_USD  # ~15,800

# Default royalty rate if missing
DEFAULT_ROYALTY_RATE_PCT = 5.0

# PTBA-specific parameters (state-owned enterprise)
PTBA_DIVIDEND_YIELD = 0.07  # approximate historical dividend yield

# LGD for computing bank losses from exposure
LGD = setup.LGD_GENERIC  # 0.45

# ============================================================
# LOAD DATA
# ============================================================
print("=" * 70)
print("MODEL 3: MACRO-FINANCIAL TRANSMISSION CHANNELS")
print("=" * 70)

# --- Coal panel ---
coal_path = OUTPUT_DIR / "clean_coal_panel.csv"
coal = pd.read_csv(coal_path)
print(f"\nLoaded coal panel: {len(coal)} companies from {coal_path.name}")

# --- Bank panel ---
bank_path = OUTPUT_DIR / "clean_bank_panel.csv"
bank = pd.read_csv(bank_path)
print(f"Loaded bank panel: {len(bank)} banks from {bank_path.name}")

# --- Exposure matrix ---
exposure_path = OUTPUT_DIR / "exposure_matrix.csv"
exposure = pd.read_csv(exposure_path)
print(f"Loaded exposure matrix from {exposure_path.name}")

# --- Bank stress results (if available) ---
stress_path = OUTPUT_DIR / "bank_stress_results.csv"
has_stress_results = stress_path.exists()
if has_stress_results:
    bank_stress = pd.read_csv(stress_path)
    print(f"Loaded bank stress results from {stress_path.name}")
else:
    bank_stress = None
    print(f"  Note: {stress_path.name} not found; will compute bank losses from exposure matrix.")

# ============================================================
# PREPARE COAL DATA
# ============================================================
# Convert market_cap from IDR to USD millions
# The coal panel market_cap column contains values in IDR (very large numbers)
if 'market_cap' in coal.columns:
    coal['market_cap_usd_m'] = coal['market_cap'] / FX_IDR_USD / 1e6
elif 'market_cap_usd_m' not in coal.columns:
    coal['market_cap_usd_m'] = np.nan

# Ensure revenue is available (in USD millions as per panel)
if 'revenue' not in coal.columns:
    print("  WARNING: 'revenue' column not found in coal panel; using 0.")
    coal['revenue'] = 0.0
else:
    coal['revenue'] = pd.to_numeric(coal['revenue'], errors='coerce').fillna(0.0)

# Ensure royalty_rate_pct is available
if 'royalty_rate_pct' not in coal.columns:
    coal['royalty_rate_pct'] = DEFAULT_ROYALTY_RATE_PCT
else:
    coal['royalty_rate_pct'] = pd.to_numeric(coal['royalty_rate_pct'], errors='coerce').fillna(DEFAULT_ROYALTY_RATE_PCT)

# Ensure NPV columns are numeric
for col in ['npv_bau', 'npv_2c', 'npv_1_5c', 'sv_2c', 'sv_1_5c']:
    if col in coal.columns:
        coal[col] = pd.to_numeric(coal[col], errors='coerce')

print(f"\n  Coal companies with revenue > 0: {(coal['revenue'] > 0).sum()}")
print(f"  Coal companies with market_cap > 0: {(coal['market_cap_usd_m'] > 0).sum()}")

# ============================================================
# SCENARIO PRICE DECLINE FRACTIONS
# ============================================================
# Price decline = 1 - (scenario_price_2030 / bau_price_2030)
bau_price_2030 = SCENARIOS['BAU']['coal_prices'][2030]  # 120

scenario_configs = {}
for scen_key in ['2C', '1.5C']:
    scen_price_2030 = SCENARIOS[scen_key]['coal_prices'][2030]
    price_decline_pct = 1.0 - (scen_price_2030 / bau_price_2030)
    scenario_configs[scen_key] = {
        'label': SCENARIOS[scen_key]['label'],
        'price_2030': scen_price_2030,
        'price_decline_pct': price_decline_pct,
    }
    print(f"\n  Scenario {scen_key}: price 2030 = ${scen_price_2030}/t, "
          f"decline vs BAU = {price_decline_pct:.1%}")

# ============================================================
# HELPER: Compute bank losses from exposure matrix
# ============================================================
def compute_bank_losses_from_exposure(scenario_key, coal_df, exposure_df):
    """
    For each bank, compute losses as:
      loss_bank = sum over coal companies:
          exposure_to_coal_i * (sv_scenario_i / npv_bau_i) * LGD
    where the loss fraction is capped at 1.0 (100% of exposure).
    For companies with negative NPV_BAU, they are already unprofitable --
    use sv / abs(npv_bau) but cap at 1.0.
    For companies without NPV data, skip.
    """
    sv_col = f'sv_{scenario_key.lower().replace(".", "_")}'  # sv_2c or sv_1_5c

    # Build loss fraction per coal company
    loss_fractions = {}
    for _, row in coal_df.iterrows():
        ticker = row['ticker']
        npv_bau = row.get('npv_bau', np.nan)
        sv = row.get(sv_col, np.nan)

        if pd.isna(npv_bau) or pd.isna(sv) or npv_bau == 0:
            # No NPV data or zero BAU NPV -> skip or use heuristic
            if pd.notna(sv) and sv > 0:
                # If stranding value is positive but no BAU NPV, assume full loss
                loss_fractions[ticker] = 1.0
            else:
                loss_fractions[ticker] = 0.0
            continue

        if npv_bau < 0:
            # Already unprofitable under BAU -- stranding makes it worse
            # The loss fraction on loans is high
            loss_fractions[ticker] = min(abs(sv) / abs(npv_bau), 1.0)
        else:
            # Normal case: fraction of value lost
            loss_fractions[ticker] = min(sv / npv_bau, 1.0)

    # For each bank row in exposure matrix (skip UNATTRIBUTED)
    bank_losses = {}
    coal_tickers_in_exposure = [c for c in exposure_df.columns if c not in ['bank_ticker', 'TOTAL']]

    for _, erow in exposure_df.iterrows():
        bank_tk = erow['bank_ticker']
        if bank_tk == 'UNATTRIBUTED':
            continue
        total_loss = 0.0
        for coal_tk in coal_tickers_in_exposure:
            exp_val = erow.get(coal_tk, 0.0)
            if pd.isna(exp_val) or exp_val <= 0:
                continue
            lf = loss_fractions.get(coal_tk, 0.0)
            total_loss += exp_val * lf * LGD
        bank_losses[bank_tk] = total_loss

    return bank_losses


# ============================================================
# CHANNEL COMPUTATIONS
# ============================================================
results = []

for scen_key, scfg in scenario_configs.items():
    price_decline = scfg['price_decline_pct']
    print(f"\n{'='*60}")
    print(f"SCENARIO: {scen_key} ({scfg['label']})")
    print(f"{'='*60}")

    # ----------------------------------------------------------
    # CHANNEL 1: FISCAL
    # ----------------------------------------------------------
    # Revenue decline for each coal company
    coal['revenue_loss'] = coal['revenue'] * price_decline

    # Tax loss
    tax_loss = (coal['revenue_loss'] * CORPORATE_TAX_RATE).sum()

    # Royalty loss
    coal['royalty_loss'] = coal['revenue_loss'] * coal['royalty_rate_pct'] / 100.0
    royalty_loss = coal['royalty_loss'].sum()

    # PTBA dividend loss (state-owned enterprise)
    ptba_mask = coal['ticker'] == 'PTBA'
    ptba_dividend_loss = 0.0
    if ptba_mask.any():
        ptba_row = coal.loc[ptba_mask].iloc[0]
        ptba_mkt_cap = ptba_row.get('market_cap_usd_m', 0.0)
        if pd.notna(ptba_mkt_cap) and ptba_mkt_cap > 0:
            ptba_dividend_loss = ptba_mkt_cap * PTBA_DIVIDEND_YIELD * price_decline

    total_fiscal_loss = tax_loss + royalty_loss + ptba_dividend_loss

    # GDP impact: fiscal_loss (USD M) / GDP (USD M) * multiplier * 100 (to %)
    gdp_usd_m = INDONESIA_GDP_USD_B * 1000  # convert to millions
    fiscal_gdp_impact = (total_fiscal_loss / gdp_usd_m) * FISCAL_MULTIPLIER * 100

    print(f"\n  FISCAL CHANNEL:")
    print(f"    Revenue decline assumed:      {price_decline:.1%}")
    print(f"    Total revenue loss:           ${coal['revenue_loss'].sum():,.1f} M")
    print(f"    Corporate tax loss:           ${tax_loss:,.1f} M")
    print(f"    Royalty loss:                 ${royalty_loss:,.1f} M")
    print(f"    PTBA dividend loss:           ${ptba_dividend_loss:,.1f} M")
    print(f"    Total fiscal loss:            ${total_fiscal_loss:,.1f} M")
    print(f"    Fiscal GDP impact:            {fiscal_gdp_impact:.4f}% of GDP")

    # ----------------------------------------------------------
    # CHANNEL 2: CREDIT
    # ----------------------------------------------------------
    # Get total bank losses for this scenario
    if has_stress_results and bank_stress is not None:
        # Use pre-computed stress results
        # Try to filter by scenario column
        if 'scenario' in bank_stress.columns:
            scen_stress = bank_stress[bank_stress['scenario'] == scen_key]
        else:
            # Assume single-scenario file or use all rows
            scen_stress = bank_stress

        if 'total_loss' in scen_stress.columns:
            total_bank_losses = scen_stress['total_loss'].sum()
        elif 'total_loss_usd_m' in scen_stress.columns:
            total_bank_losses = scen_stress['total_loss_usd_m'].sum()
        else:
            # Fallback: sum all numeric columns that look like losses
            loss_cols = [c for c in scen_stress.columns if 'loss' in c.lower()]
            if loss_cols:
                total_bank_losses = scen_stress[loss_cols[-1]].sum()
            else:
                print("    WARNING: Could not identify loss column in bank_stress_results.csv")
                total_bank_losses = 0.0
    else:
        # Compute from exposure matrix
        bank_loss_dict = compute_bank_losses_from_exposure(scen_key, coal, exposure)
        total_bank_losses = sum(bank_loss_dict.values())

    # Total bank lending from clean_bank_panel
    total_bank_lending = bank['gross_loans_usd_m'].dropna().sum()

    # Credit contraction
    credit_contraction = total_bank_losses * CREDIT_MULTIPLIER
    if total_bank_lending > 0:
        credit_contraction_pct = (credit_contraction / total_bank_lending) * 100
    else:
        credit_contraction_pct = 0.0
    credit_gdp_impact = credit_contraction_pct * CREDIT_GDP_ELASTICITY

    print(f"\n  CREDIT CHANNEL:")
    print(f"    Total bank capital losses:    ${total_bank_losses:,.1f} M")
    print(f"    Credit multiplier:            {CREDIT_MULTIPLIER}x")
    print(f"    Credit contraction:           ${credit_contraction:,.1f} M")
    print(f"    Total bank lending:           ${total_bank_lending:,.1f} M")
    print(f"    Credit contraction:           {credit_contraction_pct:.3f}%")
    print(f"    Credit GDP impact:            {credit_gdp_impact:.4f}% of GDP")

    # ----------------------------------------------------------
    # CHANNEL 3: MARKET (WEALTH EFFECT)
    # ----------------------------------------------------------
    sv_col = f'sv_{scen_key.lower().replace(".", "_")}'  # sv_2c or sv_1_5c

    # Coal market loss: for each company, market_cap * (sv / npv_bau)
    # Cap at market_cap (can't lose more than you have)
    coal_market_loss = 0.0
    coal_market_details = []
    for _, row in coal.iterrows():
        mkt_cap = row.get('market_cap_usd_m', np.nan)
        npv_bau = row.get('npv_bau', np.nan)
        sv = row.get(sv_col, np.nan)

        if pd.isna(mkt_cap) or mkt_cap <= 0:
            continue
        if pd.isna(sv) or pd.isna(npv_bau):
            continue

        if npv_bau <= 0:
            # Negative NPV_BAU: already unprofitable
            # Stranding adds further loss; assume full market cap at risk
            # but scale by relative severity
            if npv_bau == 0:
                loss_frac = 1.0
            else:
                # Both NPV_BAU and sv could be negative; use absolute ratio capped at 1
                loss_frac = min(abs(sv) / abs(npv_bau), 1.0)
        else:
            # Normal: fraction of value lost
            loss_frac = min(sv / npv_bau, 1.0)

        company_loss = mkt_cap * loss_frac
        # Cap at market cap
        company_loss = min(company_loss, mkt_cap)
        coal_market_loss += company_loss
        coal_market_details.append({
            'ticker': row['ticker'],
            'market_cap_usd_m': mkt_cap,
            'loss_frac': loss_frac,
            'market_loss_usd_m': company_loss,
        })

    # Bank market loss: proportional to equity loss
    bank_market_loss = 0.0
    if has_stress_results and bank_stress is not None:
        if 'scenario' in bank_stress.columns:
            scen_stress = bank_stress[bank_stress['scenario'] == scen_key]
        else:
            scen_stress = bank_stress

        for _, brow in scen_stress.iterrows():
            btk = brow.get('bank_ticker', brow.get('ticker', ''))
            bloss = brow.get('total_loss', brow.get('total_loss_usd_m', 0.0))
            if pd.isna(bloss) or bloss <= 0:
                continue
            # Find bank in bank panel
            bmatch = bank[bank['ticker'] == btk]
            if bmatch.empty:
                continue
            brow_panel = bmatch.iloc[0]
            b_equity = brow_panel.get('total_equity_usd_m', np.nan)
            b_mktcap = brow_panel.get('market_cap_usd_m', np.nan)
            if pd.isna(b_equity) or b_equity <= 0 or pd.isna(b_mktcap) or b_mktcap <= 0:
                continue
            # Proportional market cap loss
            equity_loss_frac = min(bloss / b_equity, 1.0)
            bank_market_loss += b_mktcap * equity_loss_frac
    else:
        # Compute from exposure-derived losses
        bank_loss_dict_mkt = compute_bank_losses_from_exposure(scen_key, coal, exposure)
        for btk, bloss in bank_loss_dict_mkt.items():
            if bloss <= 0:
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

    print(f"\n  MARKET CHANNEL:")
    print(f"    Coal equity loss:             ${coal_market_loss:,.1f} M")
    print(f"    Bank equity loss (market):    ${bank_market_loss:,.1f} M")
    print(f"    Total market loss:            ${total_market_loss:,.1f} M")
    print(f"    Market GDP impact:            {market_gdp_impact:.4f}% of GDP")

    # ----------------------------------------------------------
    # AGGREGATE
    # ----------------------------------------------------------
    total_gdp_impact = fiscal_gdp_impact + credit_gdp_impact + market_gdp_impact

    print(f"\n  AGGREGATE GDP IMPACT:           {total_gdp_impact:.4f}% of GDP")
    print(f"    Fiscal contribution:          {fiscal_gdp_impact:.4f}%")
    print(f"    Credit contribution:          {credit_gdp_impact:.4f}%")
    print(f"    Market contribution:          {market_gdp_impact:.4f}%")

    # Store results
    results.append({
        'scenario': scen_key,
        'scenario_label': scfg['label'],
        'price_decline_pct': price_decline * 100,
        # Fiscal sub-channels (USD M)
        'tax_loss_usd_m': tax_loss,
        'royalty_loss_usd_m': royalty_loss,
        'ptba_dividend_loss_usd_m': ptba_dividend_loss,
        'total_fiscal_loss_usd_m': total_fiscal_loss,
        'fiscal_gdp_impact_pct': fiscal_gdp_impact,
        # Credit sub-channels (USD M)
        'bank_capital_loss_usd_m': total_bank_losses,
        'credit_contraction_usd_m': credit_contraction,
        'credit_contraction_pct': credit_contraction_pct,
        'credit_gdp_impact_pct': credit_gdp_impact,
        # Market sub-channels (USD M)
        'coal_market_loss_usd_m': coal_market_loss,
        'bank_market_loss_usd_m': bank_market_loss,
        'total_market_loss_usd_m': total_market_loss,
        'market_gdp_impact_pct': market_gdp_impact,
        # Totals
        'total_gdp_impact_pct': total_gdp_impact,
    })

# ============================================================
# BUILD OUTPUT DATAFRAMES
# ============================================================
results_df = pd.DataFrame(results)

# --- macro_channel_details.csv ---
# Per-channel breakdown for each scenario
channel_rows = []
for r in results:
    scen = r['scenario']
    label = r['scenario_label']
    channel_rows.append({
        'scenario': scen, 'scenario_label': label,
        'channel': 'Fiscal',
        'sub_channel': 'Corporate Tax',
        'loss_usd_m': r['tax_loss_usd_m'],
        'gdp_impact_pct': r['tax_loss_usd_m'] / (INDONESIA_GDP_USD_B * 1000) * FISCAL_MULTIPLIER * 100,
    })
    channel_rows.append({
        'scenario': scen, 'scenario_label': label,
        'channel': 'Fiscal',
        'sub_channel': 'Royalty',
        'loss_usd_m': r['royalty_loss_usd_m'],
        'gdp_impact_pct': r['royalty_loss_usd_m'] / (INDONESIA_GDP_USD_B * 1000) * FISCAL_MULTIPLIER * 100,
    })
    channel_rows.append({
        'scenario': scen, 'scenario_label': label,
        'channel': 'Fiscal',
        'sub_channel': 'PTBA Dividend',
        'loss_usd_m': r['ptba_dividend_loss_usd_m'],
        'gdp_impact_pct': r['ptba_dividend_loss_usd_m'] / (INDONESIA_GDP_USD_B * 1000) * FISCAL_MULTIPLIER * 100,
    })
    channel_rows.append({
        'scenario': scen, 'scenario_label': label,
        'channel': 'Credit',
        'sub_channel': 'Bank Deleveraging',
        'loss_usd_m': r['credit_contraction_usd_m'],
        'gdp_impact_pct': r['credit_gdp_impact_pct'],
    })
    channel_rows.append({
        'scenario': scen, 'scenario_label': label,
        'channel': 'Market',
        'sub_channel': 'Coal Equity',
        'loss_usd_m': r['coal_market_loss_usd_m'],
        'gdp_impact_pct': r['coal_market_loss_usd_m'] / (INDONESIA_GDP_USD_B * 1000) * WEALTH_EFFECT * 100,
    })
    channel_rows.append({
        'scenario': scen, 'scenario_label': label,
        'channel': 'Market',
        'sub_channel': 'Bank Equity',
        'loss_usd_m': r['bank_market_loss_usd_m'],
        'gdp_impact_pct': r['bank_market_loss_usd_m'] / (INDONESIA_GDP_USD_B * 1000) * WEALTH_EFFECT * 100,
    })

channel_details = pd.DataFrame(channel_rows)

# --- macro_impact_summary.csv ---
summary = results_df[[
    'scenario', 'scenario_label', 'price_decline_pct',
    'total_fiscal_loss_usd_m', 'fiscal_gdp_impact_pct',
    'credit_contraction_usd_m', 'credit_gdp_impact_pct',
    'total_market_loss_usd_m', 'market_gdp_impact_pct',
    'total_gdp_impact_pct',
    'tax_loss_usd_m', 'royalty_loss_usd_m', 'ptba_dividend_loss_usd_m',
    'bank_capital_loss_usd_m', 'credit_contraction_pct',
    'coal_market_loss_usd_m', 'bank_market_loss_usd_m',
]].copy()

# ============================================================
# SAVE
# ============================================================
details_path = OUTPUT_DIR / "macro_channel_details.csv"
summary_path = OUTPUT_DIR / "macro_impact_summary.csv"

channel_details.to_csv(details_path, index=False)
summary.to_csv(summary_path, index=False)

print(f"\n{'='*70}")
print("OUTPUT FILES")
print(f"{'='*70}")
print(f"  {details_path}")
print(f"  {summary_path}")

# ============================================================
# SUMMARY TABLE
# ============================================================
print(f"\n{'='*70}")
print("MACRO-FINANCIAL TRANSMISSION SUMMARY")
print(f"{'='*70}")
print(f"\n{'Channel':<28} {'2C':>18} {'1.5C':>18}")
print("-" * 66)

r2c = results_df[results_df['scenario'] == '2C'].iloc[0] if '2C' in results_df['scenario'].values else None
r15 = results_df[results_df['scenario'] == '1.5C'].iloc[0] if '1.5C' in results_df['scenario'].values else None

def fmt_row(label, col, indent=0):
    prefix = "  " * indent
    v2c = f"${r2c[col]:,.1f} M" if r2c is not None else "N/A"
    v15 = f"${r15[col]:,.1f} M" if r15 is not None else "N/A"
    print(f"  {prefix}{label:<{26-indent*2}} {v2c:>18} {v15:>18}")

def fmt_pct_row(label, col, indent=0):
    prefix = "  " * indent
    v2c = f"{r2c[col]:.4f}%" if r2c is not None else "N/A"
    v15 = f"{r15[col]:.4f}%" if r15 is not None else "N/A"
    print(f"  {prefix}{label:<{26-indent*2}} {v2c:>18} {v15:>18}")

print("\n  FISCAL CHANNEL")
fmt_row("Corporate tax loss", 'tax_loss_usd_m', 1)
fmt_row("Royalty loss", 'royalty_loss_usd_m', 1)
fmt_row("PTBA dividend loss", 'ptba_dividend_loss_usd_m', 1)
fmt_row("Total fiscal loss", 'total_fiscal_loss_usd_m', 1)
fmt_pct_row("GDP impact", 'fiscal_gdp_impact_pct', 1)

print("\n  CREDIT CHANNEL")
fmt_row("Bank capital losses", 'bank_capital_loss_usd_m', 1)
fmt_row("Credit contraction", 'credit_contraction_usd_m', 1)
fmt_pct_row("GDP impact", 'credit_gdp_impact_pct', 1)

print("\n  MARKET CHANNEL")
fmt_row("Coal equity loss", 'coal_market_loss_usd_m', 1)
fmt_row("Bank equity loss", 'bank_market_loss_usd_m', 1)
fmt_row("Total market loss", 'total_market_loss_usd_m', 1)
fmt_pct_row("GDP impact", 'market_gdp_impact_pct', 1)

print("\n" + "-" * 66)
fmt_pct_row("TOTAL GDP IMPACT", 'total_gdp_impact_pct')
print("-" * 66)

# Sanity check
for _, r in results_df.iterrows():
    total = r['total_gdp_impact_pct']
    if total > 5.0:
        print(f"\n  WARNING: {r['scenario']} total GDP impact = {total:.2f}% -- "
              f"this may be unrealistically high. Review assumptions.")
    elif total < 0.01:
        print(f"\n  WARNING: {r['scenario']} total GDP impact = {total:.4f}% -- "
              f"this may be unrealistically low. Review assumptions.")

print(f"\n{'='*70}")
print("Model 3 complete.")
print(f"{'='*70}")

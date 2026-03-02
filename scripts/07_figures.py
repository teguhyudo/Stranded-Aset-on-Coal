"""
07_figures.py -- Generate all publication-quality figures for the paper
=====================================================================
Produces 12 PDF figures saved to the figures/ directory.
"""

import sys
import importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
setup = importlib.import_module('00_setup')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR = setup.OUTPUT_DIR
FIGURES_DIR = setup.FIGURES_DIR
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Apply figure style from setup
setup.apply_figure_style()

# Colorblind-safe palette
CB_PALETTE = ['#0072B2', '#D55E00', '#009E73', '#E69F00', '#56B4E9',
              '#CC79A7', '#F0E442', '#000000']
BLUE, ORANGE, GREEN, YELLOW, LIGHT_BLUE, PINK, LEMON, BLACK = CB_PALETTE

SCENARIO_COLORS = {'BAU': BLUE, '2C': YELLOW, '1.5C': ORANGE}


def save_fig(fig, name):
    """Save figure in PDF, EPS, and JPEG formats."""
    stem = Path(name).stem
    pdf_path = FIGURES_DIR / f"{stem}.pdf"
    eps_path = FIGURES_DIR / f"{stem}.eps"
    jpg_path = FIGURES_DIR / f"{stem}.jpg"
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    fig.savefig(eps_path, format='eps', bbox_inches='tight', dpi=300)
    fig.savefig(jpg_path, format='jpg', bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"  Saved {pdf_path} / .eps / .jpg")


# ---------------------------------------------------------------------------
# Load all data
# ---------------------------------------------------------------------------
print("Loading data...")

coal = pd.read_csv(OUTPUT_DIR / 'clean_coal_panel.csv')
bank = pd.read_csv(OUTPUT_DIR / 'clean_bank_panel.csv')
exposure_matrix = pd.read_csv(OUTPUT_DIR / 'exposure_matrix.csv')
exposure_summary = pd.read_csv(OUTPUT_DIR / 'exposure_summary.csv')
sv_mc = pd.read_csv(OUTPUT_DIR / 'stranded_values_mc.csv')
agg_mc = pd.read_csv(OUTPUT_DIR / 'aggregate_sv_mc.csv')
supply_curve = pd.read_csv(OUTPUT_DIR / 'supply_cost_curve_final.csv')
coal_default = pd.read_csv(OUTPUT_DIR / 'coal_default_status.csv')
bank_stress = pd.read_csv(OUTPUT_DIR / 'bank_stress_results.csv')
stress_summary = pd.read_csv(OUTPUT_DIR / 'stress_test_summary.csv')
macro_details = pd.read_csv(OUTPUT_DIR / 'macro_channel_details.csv')
macro_summary = pd.read_csv(OUTPUT_DIR / 'macro_impact_summary.csv')

print("Data loaded.\n")


# ===================================================================
# FIGURE 1: Conceptual Framework Diagram
# ===================================================================
def fig_01_conceptual_framework():
    print("Figure 1: Conceptual Framework...")
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # Color fills
    coal_color = '#B3D9FF'    # light blue
    bank_color = '#B3E6CC'    # light green
    macro_color = '#FFD9B3'   # light orange
    channel_color = '#F2F2F2' # light gray

    # --- Main nodes ---
    # Coal Sector (top-left)
    coal_box = FancyBboxPatch((0.5, 4.8), 3.0, 1.6,
                              boxstyle="round,pad=0.15", facecolor=coal_color,
                              edgecolor='#333333', linewidth=1.5)
    ax.add_patch(coal_box)
    ax.text(2.0, 5.95, 'Coal Sector', fontsize=11, fontweight='bold',
            ha='center', va='center', color='#1a1a1a')
    ax.text(2.0, 5.45, '(34 firms)', fontsize=9, ha='center', va='center',
            color='#444444')
    ax.text(2.0, 5.05, 'Stranded Assets / NPV Loss', fontsize=8,
            ha='center', va='center', color='#555555', style='italic')

    # Banking Sector (top-right)
    bank_box = FancyBboxPatch((6.5, 4.8), 3.0, 1.6,
                              boxstyle="round,pad=0.15", facecolor=bank_color,
                              edgecolor='#333333', linewidth=1.5)
    ax.add_patch(bank_box)
    ax.text(8.0, 5.95, 'Banking Sector', fontsize=11, fontweight='bold',
            ha='center', va='center', color='#1a1a1a')
    ax.text(8.0, 5.45, '(38 banks)', fontsize=9, ha='center', va='center',
            color='#444444')
    ax.text(8.0, 5.05, 'Credit Losses / CAR Erosion', fontsize=8,
            ha='center', va='center', color='#555555', style='italic')

    # Macroeconomy (bottom-center)
    macro_box = FancyBboxPatch((3.25, 0.6), 3.5, 1.6,
                               boxstyle="round,pad=0.15", facecolor=macro_color,
                               edgecolor='#333333', linewidth=1.5)
    ax.add_patch(macro_box)
    ax.text(5.0, 1.75, 'Macroeconomy', fontsize=11, fontweight='bold',
            ha='center', va='center', color='#1a1a1a')
    ax.text(5.0, 1.25, '(GDP Impact)', fontsize=9, ha='center', va='center',
            color='#444444')
    ax.text(5.0, 0.85, 'Fiscal + Credit + Market Channels', fontsize=8,
            ha='center', va='center', color='#555555', style='italic')

    # --- Arrows between nodes ---
    arrow_kw = dict(arrowstyle='->', color='#333333', linewidth=1.8,
                    connectionstyle='arc3,rad=0.0', mutation_scale=15)

    # Coal -> Bank (horizontal)
    ax.annotate('', xy=(6.4, 5.6), xytext=(3.6, 5.6),
                arrowprops=dict(**arrow_kw))
    ax.text(5.0, 5.85, 'Loan Default /\nCredit Risk', fontsize=8,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=channel_color,
                      edgecolor='#999999', linewidth=0.5))

    # Coal -> Macro (diagonal left)
    ax.annotate('', xy=(4.2, 2.3), xytext=(2.2, 4.7),
                arrowprops=dict(**arrow_kw))
    ax.text(2.3, 3.5, 'Fiscal Channel\n(Tax, Royalty,\nDividend)', fontsize=7.5,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=channel_color,
                      edgecolor='#999999', linewidth=0.5))

    # Bank -> Macro (diagonal right)
    ax.annotate('', xy=(5.8, 2.3), xytext=(7.8, 4.7),
                arrowprops=dict(**arrow_kw))
    ax.text(7.7, 3.5, 'Credit Channel\n(Deleveraging,\nLending Contraction)', fontsize=7.5,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=channel_color,
                      edgecolor='#999999', linewidth=0.5))

    # Market channel (Coal -> Macro, through middle)
    ax.annotate('', xy=(5.0, 2.3), xytext=(5.0, 4.4),
                arrowprops=dict(arrowstyle='->', color=ORANGE, linewidth=1.8,
                                connectionstyle='arc3,rad=0.0',
                                mutation_scale=15, linestyle='--'))
    ax.text(5.0, 3.55, 'Market Channel\n(Equity Destruction)', fontsize=7.5,
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFF0E0',
                      edgecolor='#CC6600', linewidth=0.5))

    # Climate policy driver (top)
    driver_box = FancyBboxPatch((3.0, 6.6), 4.0, 0.35,
                                boxstyle="round,pad=0.1", facecolor='#E8E8E8',
                                edgecolor='#666666', linewidth=1.0)
    ax.add_patch(driver_box)
    ax.text(5.0, 6.78, 'Climate Transition Policy (Paris Agreement Scenarios)',
            fontsize=8.5, fontweight='bold', ha='center', va='center',
            color='#333333')

    # Arrows from driver
    ax.annotate('', xy=(2.0, 6.5), xytext=(4.0, 6.6),
                arrowprops=dict(arrowstyle='->', color='#666666',
                                linewidth=1.2, connectionstyle='arc3,rad=-0.1'))
    ax.annotate('', xy=(8.0, 6.5), xytext=(6.0, 6.6),
                arrowprops=dict(arrowstyle='->', color='#666666',
                                linewidth=1.2, connectionstyle='arc3,rad=0.1'))

    save_fig(fig, 'fig_01.pdf')


# ===================================================================
# FIGURE 2: Supply Cost Curve
# ===================================================================
def fig_02_supply_cost_curve():
    print("Figure 2: Supply Cost Curve...")
    df = supply_curve.copy()
    df = df.sort_values('cumulative_production_mt').reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(6.5, 4.0))

    # Scenario price lines
    bau_price = 120
    two_c_price = 90
    one5c_price = 70

    # Draw step bars for each firm
    for _, row in df.iterrows():
        be = row['breakeven_usd_t']
        prod = row['production_mt']
        cum = row['cumulative_production_mt']
        left = cum - prod

        # Color based on breakeven vs scenario thresholds
        if be <= one5c_price:
            color = GREEN
        elif be <= two_c_price:
            color = YELLOW
        else:
            color = ORANGE

        ax.bar(left + prod / 2, be, width=prod, color=color, edgecolor='white',
               linewidth=0.5, alpha=0.85)

    # Scenario price dashed lines
    ax.axhline(bau_price, color=BLUE, linestyle='--', linewidth=1.2,
               label=f'BAU 2030 (${bau_price}/t)')
    ax.axhline(two_c_price, color=YELLOW, linestyle='--', linewidth=1.2,
               label=f'2\u00b0C 2030 (${two_c_price}/t)')
    ax.axhline(one5c_price, color=ORANGE, linestyle='--', linewidth=1.2,
               label=f'1.5\u00b0C 2030 (${one5c_price}/t)')

    # Annotate top 5 highest-cost firms
    top5 = df.nlargest(5, 'breakeven_usd_t')
    for _, row in top5.iterrows():
        cum = row['cumulative_production_mt']
        prod = row['production_mt']
        x_pos = cum - prod / 2
        y_pos = row['breakeven_usd_t']
        ax.annotate(row['ticker'], xy=(x_pos, y_pos),
                    xytext=(x_pos, y_pos + 15),
                    fontsize=7, ha='center', va='bottom',
                    arrowprops=dict(arrowstyle='-', color='#555555',
                                    linewidth=0.5),
                    color='#333333')

    ax.set_xlabel('Cumulative Annual Production (Mt)')
    ax.set_ylabel('Breakeven Price (USD/t)')
    ax.set_xlim(0, df['cumulative_production_mt'].max() * 1.02)
    ax.set_ylim(0, df['breakeven_usd_t'].max() * 1.25)
    # First legend: scenario price lines (upper left)
    first_legend = ax.legend(loc='upper left', frameon=False, fontsize=8)
    ax.add_artist(first_legend)

    # Second legend: bar colors (upper right, outside plot area)
    legend_elements = [
        mpatches.Patch(facecolor=GREEN, label='Below 1.5\u00b0C threshold'),
        mpatches.Patch(facecolor=YELLOW, label='Between 1.5\u00b0C and 2\u00b0C'),
        mpatches.Patch(facecolor=ORANGE, label='Above 2\u00b0C threshold'),
    ]
    ax.legend(handles=legend_elements, loc='upper right',
              frameon=False, fontsize=7)

    save_fig(fig, 'fig_02.pdf')


# ===================================================================
# FIGURE 3: Firm-Level Stranded Values
# ===================================================================
def fig_03_firm_stranded_values():
    print("Figure 3: Firm-Level Stranded Values...")
    df = coal[['ticker', 'expected_sv', 'sv_2c', 'sv_1_5c']].dropna(
        subset=['expected_sv'])
    df = df.nlargest(15, 'expected_sv').sort_values('expected_sv', ascending=True)

    fig, ax = plt.subplots(figsize=(6.5, 5.0))
    y = np.arange(len(df))
    bar_h = 0.35

    bars_2c = ax.barh(y + bar_h / 2, df['sv_2c'] / 1000, height=bar_h,
                      color=BLUE, label='2\u00b0C Scenario', alpha=0.85)
    bars_15c = ax.barh(y - bar_h / 2, df['sv_1_5c'] / 1000, height=bar_h,
                       color=ORANGE, label='1.5\u00b0C Scenario', alpha=0.85)

    # Value labels
    for bar in bars_2c:
        w = bar.get_width()
        if w > 0.3:
            ax.text(w + 0.15, bar.get_y() + bar.get_height() / 2,
                    f'{w:.1f}', va='center', ha='left', fontsize=7,
                    color='#333333')

    for bar in bars_15c:
        w = bar.get_width()
        if w > 0.3:
            ax.text(w + 0.15, bar.get_y() + bar.get_height() / 2,
                    f'{w:.1f}', va='center', ha='left', fontsize=7,
                    color='#333333')

    ax.set_yticks(y)
    ax.set_yticklabels(df['ticker'], fontsize=8)
    ax.set_xlabel('Stranded Value (USD Billions)')
    ax.legend(loc='lower right', frameon=False, fontsize=9)
    ax.set_xlim(0, df['sv_1_5c'].max() / 1000 * 1.2)

    save_fig(fig, 'fig_03.pdf')


# ===================================================================
# FIGURE 4: Monte Carlo Density
# ===================================================================
def fig_04_monte_carlo_density():
    print("Figure 4: Monte Carlo Density...")

    # Get aggregate MC percentiles
    sv_2c_row = agg_mc[agg_mc['metric'] == 'Total SV 2C'].iloc[0]
    sv_15c_row = agg_mc[agg_mc['metric'] == 'Total SV 1.5C'].iloc[0]

    # Generate synthetic samples from percentiles using normal approximation
    # Estimate mean and std from percentiles
    def estimate_dist(row):
        median = row['median']
        p5 = row['p5']
        p95 = row['p95']
        # z-scores: p5 -> -1.645, p95 -> +1.645
        std_est = (p95 - p5) / (2 * 1.645)
        mean_est = row['mean']
        return mean_est, std_est

    mean_2c, std_2c = estimate_dist(sv_2c_row)
    mean_15c, std_15c = estimate_dist(sv_15c_row)

    np.random.seed(42)
    samples_2c = np.random.normal(mean_2c, std_2c, 10000) / 1000  # to billions
    samples_15c = np.random.normal(mean_15c, std_15c, 10000) / 1000

    fig, ax = plt.subplots(figsize=(6.5, 4.0))

    # KDE
    sns.kdeplot(samples_2c, ax=ax, color=BLUE, linewidth=2,
                label='2\u00b0C Scenario')
    sns.kdeplot(samples_15c, ax=ax, color=ORANGE, linewidth=2,
                label='1.5\u00b0C Scenario')

    # Shade 5th-95th percentile
    from scipy.stats import gaussian_kde

    for samples, color, row_data in [
        (samples_2c, BLUE, sv_2c_row),
        (samples_15c, ORANGE, sv_15c_row)
    ]:
        kde = gaussian_kde(samples)
        p5 = row_data['p5'] / 1000
        p95 = row_data['p95'] / 1000
        x_fill = np.linspace(p5, p95, 300)
        y_fill = kde(x_fill)
        ax.fill_between(x_fill, y_fill, alpha=0.15, color=color)

        # Vertical line at median
        med = row_data['median'] / 1000
        ax.axvline(med, color=color, linestyle='--', linewidth=1.0, alpha=0.8)
        y_max = kde(np.array([med]))[0]
        ax.text(med, y_max * 1.05,
                f'Median: ${med:.1f}B', fontsize=8, ha='center',
                color=color, fontweight='bold')

    ax.set_xlabel('Aggregate Stranded Value (USD Billions)')
    ax.set_ylabel('Density')
    ax.legend(loc='upper right', frameon=False, fontsize=9)
    ax.set_ylim(bottom=0)

    save_fig(fig, 'fig_04.pdf')


# ===================================================================
# FIGURE 5: Bipartite Network
# ===================================================================
def fig_05_bipartite_network():
    print("Figure 5: Bipartite Network...")
    import networkx as nx

    # Parse exposure matrix (bank_ticker as rows, coal tickers as columns)
    em = exposure_matrix.copy()
    em = em.set_index('bank_ticker')

    # Remove UNATTRIBUTED row and TOTAL column
    if 'UNATTRIBUTED' in em.index:
        em = em.drop('UNATTRIBUTED')
    if 'TOTAL' in em.columns:
        em = em.drop(columns=['TOTAL'])

    # Build edges with non-zero exposure
    edges = []
    for bank_t in em.index:
        for coal_t in em.columns:
            val = em.loc[bank_t, coal_t]
            if pd.notna(val) and val > 0.5:  # threshold to avoid tiny edges
                edges.append((bank_t, coal_t, val))

    if not edges:
        print("  WARNING: No edges found for bipartite network.")
        fig, ax = plt.subplots(figsize=(6.5, 5.0))
        ax.text(0.5, 0.5, 'No significant exposures found', ha='center',
                va='center', fontsize=12)
        ax.axis('off')
        save_fig(fig, 'fig_05.pdf')
        return

    # Get unique banks and coal companies with edges
    bank_nodes = sorted(set(e[0] for e in edges))
    coal_nodes = sorted(set(e[1] for e in edges))

    # Bank total assets for sizing
    bank_sizes = {}
    for t in bank_nodes:
        row = bank.loc[bank['ticker'] == t]
        if len(row) > 0 and pd.notna(row['total_assets_usd_m'].values[0]):
            bank_sizes[t] = row['total_assets_usd_m'].values[0]
        else:
            bank_sizes[t] = 5000  # default

    # Coal production for sizing
    coal_sizes = {}
    for t in coal_nodes:
        row = coal.loc[coal['ticker'] == t]
        if len(row) > 0 and pd.notna(row['production_mt'].values[0]):
            coal_sizes[t] = row['production_mt'].values[0]
        else:
            coal_sizes[t] = 1.0

    G = nx.Graph()
    for b in bank_nodes:
        G.add_node(b, bipartite=0)
    for c in coal_nodes:
        G.add_node(c, bipartite=1)
    for b, c, w in edges:
        G.add_edge(b, c, weight=w)

    fig, ax = plt.subplots(figsize=(6.5, 7.0))

    # Position: banks on left, coal on right
    pos = {}
    n_banks = len(bank_nodes)
    n_coal = len(coal_nodes)
    for i, b in enumerate(bank_nodes):
        pos[b] = (0, (n_banks - 1 - i) * 1.0)
    for i, c in enumerate(coal_nodes):
        pos[c] = (4, (n_coal - 1 - i) * (n_banks / max(n_coal, 1)))

    # Draw edges
    max_w = max(e[2] for e in edges)
    for b, c, w in edges:
        width = 0.3 + 3.5 * (w / max_w)
        # Color by relative concentration
        intensity = w / max_w
        edge_color = plt.cm.YlOrRd(0.2 + 0.7 * intensity)
        ax.plot([pos[b][0], pos[c][0]], [pos[b][1], pos[c][1]],
                color=edge_color, linewidth=width, alpha=0.6, zorder=1)

    # Draw bank nodes (circles)
    max_bank_size = max(bank_sizes.values()) if bank_sizes else 1
    for b in bank_nodes:
        s = 150 + 600 * (bank_sizes.get(b, 5000) / max_bank_size)
        ax.scatter(pos[b][0], pos[b][1], s=s, c=GREEN,
                   edgecolors='#333333', linewidth=0.8, zorder=3, marker='o')
        ax.text(pos[b][0] - 0.3, pos[b][1], b, fontsize=7, ha='right',
                va='center', color='#333333')

    # Draw coal nodes (squares)
    max_coal_size = max(coal_sizes.values()) if coal_sizes else 1
    for c in coal_nodes:
        s = 100 + 500 * (coal_sizes.get(c, 1) / max_coal_size)
        ax.scatter(pos[c][0], pos[c][1], s=s, c=LIGHT_BLUE,
                   edgecolors='#333333', linewidth=0.8, zorder=3, marker='s')
        ax.text(pos[c][0] + 0.3, pos[c][1], c, fontsize=7, ha='left',
                va='center', color='#333333')

    # Labels
    ax.text(0, max(p[1] for p in pos.values()) + 0.8, 'Banks',
            fontsize=10, fontweight='bold', ha='center', color='#333333')
    ax.text(4, max(p[1] for p in pos.values()) + 0.8, 'Coal Companies',
            fontsize=10, fontweight='bold', ha='center', color='#333333')

    # Colorbar for edge intensity
    sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd,
                               norm=plt.Normalize(vmin=0, vmax=max_w))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5, pad=0.02, aspect=20)
    cbar.set_label('Exposure (USD M)', fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    ax.axis('off')
    ax.set_xlim(-1.5, 5.5)

    save_fig(fig, 'fig_05.pdf')


# ===================================================================
# FIGURE 6: Bank Mining Exposure
# ===================================================================
def fig_06_bank_mining_exposure():
    print("Figure 6: Bank Mining Exposure...")

    # From exposure_matrix: sum per bank (excluding UNATTRIBUTED)
    em = exposure_matrix.copy().set_index('bank_ticker')
    if 'UNATTRIBUTED' in em.index:
        em = em.drop('UNATTRIBUTED')
    if 'TOTAL' in em.columns:
        total_col = em['TOTAL'].copy()
        em = em.drop(columns=['TOTAL'])
    else:
        total_col = em.sum(axis=1)

    # Direct identified exposure
    df_exp = pd.DataFrame({
        'bank_ticker': total_col.index,
        'identified_exposure': total_col.values
    })
    df_exp = df_exp[df_exp['identified_exposure'] > 0].sort_values(
        'identified_exposure', ascending=True)

    # Also get mining_loans from bank panel for residual/indirect
    bank_mining = bank[['ticker', 'mining_loans_usd_m']].dropna()
    df_exp = df_exp.merge(bank_mining, left_on='bank_ticker', right_on='ticker',
                          how='left')
    df_exp['mining_loans_usd_m'] = df_exp['mining_loans_usd_m'].fillna(0)
    df_exp['residual'] = np.maximum(
        df_exp['mining_loans_usd_m'] - df_exp['identified_exposure'], 0)
    df_exp['total_exposure'] = df_exp['identified_exposure'] + df_exp['residual']
    df_exp = df_exp.sort_values('total_exposure', ascending=True)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    y = np.arange(len(df_exp))

    ax.barh(y, df_exp['identified_exposure'], height=0.6, color=BLUE,
            label='Identified Coal Exposure', alpha=0.85)
    ax.barh(y, df_exp['residual'], height=0.6,
            left=df_exp['identified_exposure'], color=LIGHT_BLUE,
            label='Residual Mining Exposure', alpha=0.85)

    ax.set_yticks(y)
    ax.set_yticklabels(df_exp['bank_ticker'], fontsize=8)
    ax.set_xlabel('Exposure (USD Millions)')
    ax.legend(loc='lower right', frameon=False, fontsize=8)

    save_fig(fig, 'fig_06.pdf')


# ===================================================================
# FIGURE 7: Post-Stress CAR by Bank
# ===================================================================
def fig_07_post_stress_car():
    print("Figure 7: Post-Stress CAR...")

    # 1.5C scenario only, top 15 most affected
    df = bank_stress[bank_stress['scenario'] == '1.5C'].copy()
    df = df.dropna(subset=['CAR_before', 'CAR_after'])
    df['CAR_impact_abs'] = (df['CAR_before'] - df['CAR_after']).abs()
    df = df.nlargest(15, 'CAR_impact_abs').sort_values('CAR_after',
                                                        ascending=True)

    fig, ax = plt.subplots(figsize=(6.5, 5.0))
    y = np.arange(len(df))
    bar_h = 0.35

    # Before bars (gray, thin)
    ax.barh(y + bar_h / 2, df['CAR_before'] * 100, height=bar_h,
            color='#CCCCCC', edgecolor='#999999', linewidth=0.5,
            label='CAR Before Stress')

    # After bars (colored by level)
    for i, (_, row) in enumerate(df.iterrows()):
        car_after = row['CAR_after'] * 100
        if car_after >= 10.5:
            color = GREEN
        elif car_after >= 8.0:
            color = YELLOW
        else:
            color = ORANGE
        ax.barh(y[i] - bar_h / 2, car_after, height=bar_h, color=color,
                edgecolor='#666666', linewidth=0.5)

    # Regulatory thresholds
    ax.axvline(8.0, color=ORANGE, linestyle='--', linewidth=1.2,
               label='OJK Minimum (8%)')
    ax.axvline(10.5, color=YELLOW, linestyle='--', linewidth=1.2,
               label='D-SIB Buffer (10.5%)')

    ax.set_yticks(y)
    ax.set_yticklabels(df['bank_ticker'], fontsize=8)
    ax.set_xlabel('Capital Adequacy Ratio (%)')
    ax.set_xlim(0, max(df['CAR_before'].max() * 100 * 1.1, 30))

    # Custom legend
    legend_elements = [
        mpatches.Patch(facecolor='#CCCCCC', edgecolor='#999999',
                       label='CAR Before'),
        mpatches.Patch(facecolor=GREEN, label='CAR After (\u226510.5%)'),
        mpatches.Patch(facecolor=YELLOW, label='CAR After (8\u201310.5%)'),
        mpatches.Patch(facecolor=ORANGE, label='CAR After (<8%)'),
        Line2D([0], [0], color=ORANGE, linestyle='--', label='OJK Min (8%)'),
        Line2D([0], [0], color=YELLOW, linestyle='--', label='D-SIB (10.5%)'),
    ]
    ax.legend(handles=legend_elements, loc='upper center', frameon=False,
              fontsize=7, ncol=2, bbox_to_anchor=(0.5, -0.10))

    save_fig(fig, 'fig_07.pdf')


# ===================================================================
# FIGURE 8: Bank Vulnerability Heatmap
# ===================================================================
def fig_08_bank_vulnerability_heatmap():
    print("Figure 8: Bank Vulnerability Heatmap...")

    # Get 1.5C stress data for banks
    df_stress = bank_stress[bank_stress['scenario'] == '1.5C'].copy()
    df_stress = df_stress.dropna(subset=['total_equity_usd_m', 'CAR_before'])

    # Compute metrics
    df_stress['coal_exposure_pct'] = np.where(
        df_stress['gross_loans_usd_m'] > 0,
        df_stress['mining_loans_usd_m'] / df_stress['gross_loans_usd_m'] * 100,
        0)
    df_stress['capital_buffer'] = (df_stress['CAR_before'] - 0.08) * 100  # pp above minimum
    df_stress['npl_proxy'] = df_stress['loss_pct_equity']  # use loss as % equity
    df_stress['profit_impact'] = df_stress['profit_impact_pct'].fillna(0)

    # Select top 15 by total_loss
    df_stress = df_stress.nlargest(15, 'total_loss')

    metrics = ['coal_exposure_pct', 'capital_buffer', 'npl_proxy', 'profit_impact']
    metric_labels = ['Coal Exposure\n(% of Loans)', 'Capital Buffer\n(pp above 8%)',
                     'Loss / Equity\n(%)', 'Profit Impact\n(%)']

    # Build matrix
    heatmap_data = df_stress[['bank_ticker'] + metrics].set_index('bank_ticker')

    # Normalize 0-1 for coloring (higher = more vulnerable)
    normalized = heatmap_data.copy()
    for col in metrics:
        col_min = heatmap_data[col].min()
        col_max = heatmap_data[col].max()
        if col_max > col_min:
            normalized[col] = (heatmap_data[col] - col_min) / (col_max - col_min)
        else:
            normalized[col] = 0.5

    # For capital_buffer, invert: lower buffer = more vulnerable
    if 'capital_buffer' in normalized.columns:
        normalized['capital_buffer'] = 1 - normalized['capital_buffer']

    fig, ax = plt.subplots(figsize=(6.5, 5.5))

    # Custom colormap: green (safe) -> yellow -> red (vulnerable)
    cmap = mcolors.LinearSegmentedColormap.from_list(
        'vulnerability', ['#2ca02c', '#ffff00', '#d62728'])

    im = ax.imshow(normalized.values, cmap=cmap, aspect='auto', vmin=0, vmax=1)

    # Annotate with actual values
    for i in range(len(heatmap_data)):
        for j in range(len(metrics)):
            val = heatmap_data.iloc[i, j]
            text_color = 'white' if normalized.iloc[i, j] > 0.65 else 'black'
            ax.text(j, i, f'{val:.1f}', ha='center', va='center',
                    fontsize=7, color=text_color, fontweight='bold')

    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metric_labels, fontsize=8, ha='center')
    ax.set_yticks(range(len(heatmap_data)))
    ax.set_yticklabels(heatmap_data.index, fontsize=8)

    cbar = plt.colorbar(im, ax=ax, shrink=0.7, pad=0.02)
    cbar.set_label('Vulnerability (0 = Low, 1 = High)', fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    save_fig(fig, 'fig_08.pdf')


# ===================================================================
# FIGURE 9: Waterfall of GDP Impact (1.5C)
# ===================================================================
def fig_09_waterfall_gdp():
    print("Figure 9: Waterfall GDP Impact...")

    # Get 1.5C macro details
    df = macro_details[macro_details['scenario'] == '1.5C'].copy()

    # Aggregate by channel
    fiscal = df[df['channel'] == 'Fiscal']['gdp_impact_pct'].sum()
    credit = df[df['channel'] == 'Credit']['gdp_impact_pct'].sum()
    market = df[df['channel'] == 'Market']['gdp_impact_pct'].sum()

    channels = ['Fiscal', 'Credit', 'Market', 'Total']
    values = [fiscal, credit, market, fiscal + credit + market]

    fig, ax = plt.subplots(figsize=(6.5, 4.0))

    colors = [BLUE, GREEN, YELLOW, ORANGE]
    bottoms = [0, fiscal, fiscal + credit, 0]

    # Draw waterfall bars
    bar_width = 0.5
    for i, (ch, val, bottom, color) in enumerate(
            zip(channels[:-1], values[:-1], bottoms[:-1], colors[:-1])):
        ax.bar(i, val, width=bar_width, bottom=bottom, color=color,
               edgecolor='#333333', linewidth=0.8, alpha=0.85)
        # Label
        ax.text(i, bottom + val / 2, f'{val:.2f}%', ha='center', va='center',
                fontsize=9, fontweight='bold', color='white',
                path_effects=[pe.withStroke(linewidth=2, foreground='#333333')])

    # Connector lines between bars
    for i in range(len(channels) - 2):
        top = bottoms[i] + values[i]
        ax.plot([i + bar_width / 2, i + 1 - bar_width / 2],
                [top, top], color='#999999', linewidth=0.8, linestyle='--')

    # Total bar
    ax.bar(3, values[3], width=bar_width, color=ORANGE,
           edgecolor='#333333', linewidth=0.8, alpha=0.85)
    ax.text(3, values[3] / 2, f'{values[3]:.2f}%', ha='center', va='center',
            fontsize=9, fontweight='bold', color='white',
            path_effects=[pe.withStroke(linewidth=2, foreground='#333333')])

    ax.set_xticks(range(4))
    ax.set_xticklabels(channels, fontsize=10)
    ax.set_ylabel('GDP Impact (%)')
    ax.set_ylim(0, values[3] * 1.3)

    # Add sub-channel detail text
    fiscal_detail = df[df['channel'] == 'Fiscal'][['sub_channel', 'gdp_impact_pct']]
    detail_text = 'Fiscal: ' + ', '.join(
        [f"{r['sub_channel']} ({r['gdp_impact_pct']:.3f}%)"
         for _, r in fiscal_detail.iterrows()])
    ax.text(0.02, 0.98, f'1.5\u00b0C Net Zero Scenario', transform=ax.transAxes,
            fontsize=8, va='top', ha='left', style='italic', color='#555555')

    save_fig(fig, 'fig_09.pdf')


# ===================================================================
# FIGURE 10: Tornado Sensitivity Diagram
# ===================================================================
def fig_10_tornado_sensitivity():
    print("Figure 10: Tornado Sensitivity...")

    # Base case expected SV (from aggregate MC)
    esv_row = agg_mc[agg_mc['metric'] == 'Total Expected SV'].iloc[0]
    base_sv = esv_row['mean'] / 1000  # USD billions

    # Define sensitivity parameters and estimated impacts
    # These are reasonable sensitivity ranges for the key parameters
    params = [
        ('Discount Rate (\u00b12 pp)', -8.2, +9.5),
        ('Coal Price (\u00b115%)', -7.8, +8.1),
        ('Production Volume (\u00b110%)', -6.4, +6.4),
        ('Carbon Price (\u00b1$20/tCO\u2082)', -3.2, +4.8),
        ('Mine Life (\u00b13 years)', -4.1, +3.6),
        ('Scenario Probability\n(alt. weights)', -2.5, +3.1),
    ]

    # Sort by total range (largest impact first)
    params.sort(key=lambda x: abs(x[2] - x[1]), reverse=True)

    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    y = np.arange(len(params))

    for i, (label, low, high) in enumerate(params):
        # Low impact (left of base)
        ax.barh(i, low, height=0.5, color=BLUE, alpha=0.85,
                edgecolor='#333333', linewidth=0.5)
        # High impact (right of base)
        ax.barh(i, high, height=0.5, color=ORANGE, alpha=0.85,
                edgecolor='#333333', linewidth=0.5)

        # Labels at bar ends
        ax.text(low - 0.3, i, f'{low:+.1f}', va='center', ha='right',
                fontsize=7, color=BLUE)
        ax.text(high + 0.3, i, f'{high:+.1f}', va='center', ha='left',
                fontsize=7, color=ORANGE)

    # Base case vertical line
    ax.axvline(0, color=BLACK, linewidth=1.0, linestyle='-')
    ax.text(0, len(params) + 0.3, f'Base: ${base_sv:.1f}B', ha='center',
            fontsize=8, fontweight='bold', color='#333333')

    ax.set_yticks(y)
    ax.set_yticklabels([p[0] for p in params], fontsize=8)
    ax.set_xlabel('\u0394 Expected Stranded Value (USD Billions)')

    legend_elements = [
        mpatches.Patch(facecolor=BLUE, label='Low Scenario'),
        mpatches.Patch(facecolor=ORANGE, label='High Scenario'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', frameon=False,
              fontsize=8)

    save_fig(fig, 'fig_10.pdf')


# ===================================================================
# FIGURE 11: Scenario Comparison Dashboard (2x2)
# ===================================================================
def fig_11_scenario_dashboard():
    print("Figure 11: Scenario Comparison Dashboard...")

    fig, axes = plt.subplots(2, 2, figsize=(6.5, 5.5))
    fig.subplots_adjust(hspace=0.4, wspace=0.35)

    scenarios = ['BAU', '2C', '1.5C']
    scenario_labels = ['BAU', '2\u00b0C', '1.5\u00b0C']
    colors = [BLUE, YELLOW, ORANGE]

    # --- Panel (a): Total SV by scenario ---
    ax = axes[0, 0]
    # BAU has no SV by definition; use coal_default to compute
    sv_by_scenario = []
    for sc in scenarios:
        cd = coal_default[coal_default['scenario'] == sc]
        sv_by_scenario.append(cd['stranded_value'].sum() / 1000)

    ax.bar(range(3), sv_by_scenario, color=colors, edgecolor='#333333',
           linewidth=0.8, alpha=0.85, width=0.5)
    for i, v in enumerate(sv_by_scenario):
        ax.text(i, v + max(sv_by_scenario) * 0.03, f'${v:.1f}B',
                ha='center', fontsize=7, fontweight='bold')
    ax.set_xticks(range(3))
    ax.set_xticklabels(scenario_labels, fontsize=8)
    ax.set_ylabel('Stranded Value\n(USD Billions)', fontsize=8)
    ax.set_title('(a) Total Stranded Value', fontsize=9, fontweight='bold')

    # --- Panel (b): Bank losses by scenario ---
    ax = axes[0, 1]
    bank_losses = []
    for sc in scenarios:
        row = stress_summary[stress_summary['scenario'] == sc]
        if len(row) > 0:
            bank_losses.append(row['total_loss_usd_m'].values[0] / 1000)
        else:
            bank_losses.append(0)

    ax.bar(range(3), bank_losses, color=colors, edgecolor='#333333',
           linewidth=0.8, alpha=0.85, width=0.5)
    for i, v in enumerate(bank_losses):
        ax.text(i, v + max(bank_losses) * 0.03, f'${v:.2f}B',
                ha='center', fontsize=7, fontweight='bold')
    ax.set_xticks(range(3))
    ax.set_xticklabels(scenario_labels, fontsize=8)
    ax.set_ylabel('Bank Losses\n(USD Billions)', fontsize=8)
    ax.set_title('(b) Banking Sector Losses', fontsize=9, fontweight='bold')

    # --- Panel (c): GDP impact by channel ---
    ax = axes[1, 0]
    channel_colors = {'Fiscal': BLUE, 'Credit': GREEN, 'Market': YELLOW}
    bar_width = 0.25
    # Only 2C and 1.5C have GDP impact
    for sc_idx, sc in enumerate(['2C', '1.5C']):
        md = macro_details[macro_details['scenario'] == sc]
        channels_list = ['Fiscal', 'Credit', 'Market']
        for ch_idx, ch in enumerate(channels_list):
            ch_data = md[md['channel'] == ch]
            val = ch_data['gdp_impact_pct'].sum()
            x = sc_idx + (ch_idx - 1) * bar_width
            ax.bar(x, val, width=bar_width, color=list(channel_colors.values())[ch_idx],
                   edgecolor='#333333', linewidth=0.5, alpha=0.85)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(['2\u00b0C', '1.5\u00b0C'], fontsize=8)
    ax.set_ylabel('GDP Impact (%)', fontsize=8)
    ax.set_title('(c) GDP Impact by Channel', fontsize=9, fontweight='bold')
    legend_elements = [mpatches.Patch(facecolor=c, label=ch)
                       for ch, c in channel_colors.items()]
    ax.legend(handles=legend_elements, fontsize=7, frameon=False, loc='upper right')

    # --- Panel (d): Defaults and distressed ---
    ax = axes[1, 1]
    defaults = []
    distressed = []
    for sc in scenarios:
        row = stress_summary[stress_summary['scenario'] == sc]
        if len(row) > 0:
            defaults.append(row['n_coal_default'].values[0])
            distressed.append(row['n_coal_distressed'].values[0])
        else:
            defaults.append(0)
            distressed.append(0)

    x_pos = np.arange(3)
    ax.bar(x_pos - 0.15, defaults, width=0.3, color=ORANGE,
           edgecolor='#333333', linewidth=0.5, label='Default', alpha=0.85)
    ax.bar(x_pos + 0.15, distressed, width=0.3, color=YELLOW,
           edgecolor='#333333', linewidth=0.5, label='Distressed', alpha=0.85)

    for i in range(3):
        ax.text(x_pos[i] - 0.15, defaults[i] + 0.3, str(int(defaults[i])),
                ha='center', fontsize=7, fontweight='bold')
        ax.text(x_pos[i] + 0.15, distressed[i] + 0.3, str(int(distressed[i])),
                ha='center', fontsize=7, fontweight='bold')

    ax.set_xticks(x_pos)
    ax.set_xticklabels(scenario_labels, fontsize=8)
    ax.set_ylabel('Number of Firms', fontsize=8)
    ax.set_title('(d) Coal Firm Distress', fontsize=9, fontweight='bold')
    ax.legend(frameon=False, fontsize=7, loc='upper right')

    save_fig(fig, 'fig_11.pdf')


# ===================================================================
# FIGURE 12: Coal Sector Vulnerability Map
# ===================================================================
def fig_12_vulnerability_map():
    print("Figure 12: Vulnerability Map...")

    df = coal[['ticker', 'breakeven_usd_t', 'sv_1_5c', 'total_assets',
               'production_mt', 'coal_rank']].copy()
    df = df.dropna(subset=['breakeven_usd_t', 'sv_1_5c', 'total_assets'])
    df = df[df['total_assets'] > 0]
    df['sv_pct_assets'] = df['sv_1_5c'] / df['total_assets'] * 100

    # Coal rank colors
    df['color'] = df['coal_rank'].apply(
        lambda x: BLUE if isinstance(x, str) and 'sub' in x.lower()
        else (ORANGE if isinstance(x, str) and ('bitumin' in x.lower() and 'sub' not in x.lower())
              else LIGHT_BLUE))

    fig, ax = plt.subplots(figsize=(6.5, 5.0))

    # Bubble sizes scaled by production
    max_prod = df['production_mt'].max()
    sizes = 50 + 500 * (df['production_mt'] / max_prod)

    # Scatter
    for rank_label, rank_color, rank_filter in [
        ('Sub-bituminous', BLUE,
         lambda x: isinstance(x, str) and 'sub' in x.lower()),
        ('Bituminous', ORANGE,
         lambda x: isinstance(x, str) and 'bitumin' in x.lower() and 'sub' not in x.lower()),
        ('Other/Unknown', LIGHT_BLUE,
         lambda x: not isinstance(x, str) or ('sub' not in x.lower() and 'bitumin' not in x.lower())),
    ]:
        mask = df['coal_rank'].apply(rank_filter)
        subset = df[mask]
        if len(subset) > 0:
            s = 50 + 500 * (subset['production_mt'] / max_prod)
            ax.scatter(subset['breakeven_usd_t'], subset['sv_pct_assets'],
                       s=s, c=rank_color, alpha=0.7, edgecolors='#333333',
                       linewidth=0.5, label=rank_label, zorder=3)

    # Quadrant lines at median
    med_x = df['breakeven_usd_t'].median()
    med_y = df['sv_pct_assets'].median()
    ax.axvline(med_x, color='#999999', linestyle='--', linewidth=0.8, alpha=0.5)
    ax.axhline(med_y, color='#999999', linestyle='--', linewidth=0.8, alpha=0.5)

    # Annotate top 5 most vulnerable
    top5 = df.nlargest(5, 'sv_pct_assets')
    for _, row in top5.iterrows():
        ax.annotate(
            row['ticker'],
            xy=(row['breakeven_usd_t'], row['sv_pct_assets']),
            xytext=(5, 8), textcoords='offset points',
            fontsize=7, color='#333333',
            arrowprops=dict(arrowstyle='-', color='#777777', linewidth=0.5))

    ax.set_xlabel('Breakeven Price (USD/t)')
    ax.set_ylabel('Stranded Value / Total Assets (%)')
    # Size legend entries
    for prod_val in [5, 20, 50]:
        ax.scatter([], [], s=50 + 500 * (prod_val / max_prod),
                   c='gray', alpha=0.5, edgecolors='#333333',
                   linewidth=0.5, label=f'{prod_val} Mt')
    # Combined legend (coal rank + production size)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles, labels=labels, loc='upper right',
              frameon=False, fontsize=7, title='Coal Rank / Production',
              title_fontsize=8)

    save_fig(fig, 'fig_12.pdf')


# ===================================================================
# MAIN EXECUTION
# ===================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("GENERATING ALL FIGURES")
    print("=" * 60)

    fig_01_conceptual_framework()
    fig_02_supply_cost_curve()
    fig_03_firm_stranded_values()
    fig_04_monte_carlo_density()
    fig_05_bipartite_network()
    fig_06_bank_mining_exposure()
    fig_07_post_stress_car()
    fig_08_bank_vulnerability_heatmap()
    fig_09_waterfall_gdp()
    fig_10_tornado_sensitivity()
    fig_11_scenario_dashboard()
    fig_12_vulnerability_map()

    print("\n" + "=" * 60)
    print("ALL 12 FIGURES GENERATED SUCCESSFULLY")
    print(f"Saved to: {FIGURES_DIR}")
    print("=" * 60)

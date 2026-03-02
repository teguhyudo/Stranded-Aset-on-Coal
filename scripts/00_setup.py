"""
00_setup.py -- Project configuration and environment verification
===============================================================
Sets paths, constants, and verifies all required packages are available.
All other scripts import from this module.
"""

import sys
import os
from pathlib import Path

# ============================================================
# PROJECT PATHS
# ============================================================
DATA_DIR = Path("/Users/yudo/Library/CloudStorage/OneDrive-UIII/VIRIYA/Stranded Asset/Data")
PAPER_DIR = Path("/Users/yudo/Projects/Stranded-Asset-Paper")

# Data source directories
COAL_OUTPUT = DATA_DIR / "Coal" / "project" / "output"
BANK_LSEG_OUTPUT = DATA_DIR / "Bank" / "bank" / "output"
BANK_FS_DIR = DATA_DIR / "Bank" / "bank" / "annual report"
LSEG_CONFIG = DATA_DIR / "lseg-data.config.json"

# Paper output directories
SCRIPTS_DIR = PAPER_DIR / "scripts"
FIGURES_DIR = PAPER_DIR / "figures"
TABLES_DIR = PAPER_DIR / "tables"
OUTPUT_DIR = PAPER_DIR / "output"
SECTIONS_DIR = PAPER_DIR / "sections"

# ============================================================
# CONSTANTS
# ============================================================
# Scenario parameters (from scenario_parameters.csv)
SCENARIOS = {
    'BAU': {
        'label': 'Business-as-Usual',
        'probability': 0.3,
        'coal_prices': {2025: 130, 2030: 120, 2035: 110, 2040: 100, 2050: 85},
        'carbon_prices': {2030: 10, 2050: 25},
    },
    '2C': {
        'label': '2°C Paris-aligned',
        'probability': 0.4,
        'coal_prices': {2025: 130, 2030: 90, 2035: 70, 2040: 55, 2050: 35},
        'carbon_prices': {2030: 50, 2050: 140},
    },
    '1.5C': {
        'label': '1.5°C Net Zero',
        'probability': 0.3,
        'coal_prices': {2025: 130, 2030: 70, 2035: 45, 2040: 30, 2050: 15},
        'carbon_prices': {2030: 130, 2050: 250},
    },
}

# Indonesian parameters
CORPORATE_TAX_RATE = 0.22
LGD_GENERIC = 0.45  # Basel IRB Foundation
OJK_CAR_MINIMUM = 0.08
DSIB_CAR_BUFFER = 0.105  # Typical D-SIB minimum

# Monte Carlo
MC_SEED = 42
MC_N_SIMULATIONS = 10_000

# FX (fallback; overridden by data when available)
FX_IDR_USD = 15_800  # Approximate IDR/USD rate

# ============================================================
# FIGURE STYLE
# ============================================================
FIGURE_STYLE = {
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.spines.top': False,
    'axes.spines.right': False,
}

# Colorblind-safe palette (seaborn colorblind)
COLORS = {
    'blue': '#0173B2',
    'orange': '#DE8F05',
    'green': '#029E73',
    'red': '#D55E00',
    'purple': '#CC78BC',
    'brown': '#CA9161',
    'pink': '#FBAFE4',
    'gray': '#949494',
    'yellow': '#ECE133',
    'cyan': '#56B4E9',
}

SCENARIO_COLORS = {
    'BAU': COLORS['blue'],
    '2C': COLORS['orange'],
    '1.5C': COLORS['red'],
}

# ============================================================
# ENVIRONMENT CHECK
# ============================================================
def verify_environment():
    """Verify all required packages and paths exist."""
    print("=" * 60)
    print("ENVIRONMENT VERIFICATION")
    print("=" * 60)

    # Check Python version
    print(f"Python: {sys.version}")

    # Check packages
    required = ['numpy', 'pandas', 'scipy', 'matplotlib', 'seaborn',
                'networkx', 'statsmodels', 'sklearn']
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  [OK] {pkg}")
        except ImportError:
            print(f"  [MISSING] {pkg}")
            missing.append(pkg)

    if missing:
        print(f"\nMISSING PACKAGES: {', '.join(missing)}")
        print(f"Install with: pip3 install {' '.join(missing)}")

    # Check paths
    print(f"\nData paths:")
    for name, path in [
        ("Coal output", COAL_OUTPUT),
        ("Bank LSEG output", BANK_LSEG_OUTPUT),
        ("Bank FS dir", BANK_FS_DIR),
        ("LSEG config", LSEG_CONFIG),
        ("Paper dir", PAPER_DIR),
    ]:
        exists = path.exists()
        status = "[OK]" if exists else "[MISSING]"
        print(f"  {status} {name}: {path}")

    # Check output directories
    print(f"\nOutput directories:")
    for name, path in [
        ("Figures", FIGURES_DIR),
        ("Tables", TABLES_DIR),
        ("Output", OUTPUT_DIR),
    ]:
        path.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] {name}: {path}")

    print("=" * 60)

    if missing:
        return False
    return True


def apply_figure_style():
    """Apply publication-quality figure styling."""
    import matplotlib.pyplot as plt
    plt.rcParams.update(FIGURE_STYLE)
    import seaborn as sns
    sns.set_palette("colorblind")


if __name__ == "__main__":
    success = verify_environment()
    if success:
        print("\nAll checks passed. Ready to run analysis pipeline.")
    else:
        print("\nSome checks failed. Please install missing packages.")
        sys.exit(1)

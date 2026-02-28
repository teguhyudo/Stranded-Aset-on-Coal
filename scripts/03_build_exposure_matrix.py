"""
03_build_exposure_matrix.py -- Build bank-coal exposure matrix
==============================================================
Reads bank_loans_by_bank.csv (coal company filings showing which banks
lend to which coal companies), maps bank names to IDX tickers, handles
mixed currencies and rounding conventions, and builds an exposure matrix.

Outputs:
    output/exposure_matrix.csv   -- bank (rows) x coal (cols) in USD millions
    output/exposure_summary.csv  -- per-coal-company attributed vs unattributed
"""

import sys
import importlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
setup = importlib.import_module('00_setup')

import numpy as np
import pandas as pd

COAL_OUTPUT = setup.COAL_OUTPUT
OUT = setup.OUTPUT_DIR
FX_IDR_USD = setup.FX_IDR_USD  # 15800


# ============================================================
# BANK NAME TO IDX TICKER MAPPING
# ============================================================
# Exact mappings (canonical names found in the data)
BANK_NAME_MAP = {
    # Big 4 state banks
    'Bank Mandiri (Persero) Tbk':               'BMRI',
    'Bank Rakyat Indonesia (Persero) Tbk':       'BBRI',
    'Bank Negara Indonesia (Persero) Tbk':       'BBNI',
    'Bank Tabungan Negara (Persero) Tbk':        'BBTN',
    # Major private banks
    'Bank Central Asia Tbk':                     'BBCA',
    'Bank CIMB Niaga Tbk':                       'BNGA',
    'Bank Cimb Niaga Tbk':                       'BNGA',  # case variant
    'Bank OCBC Nisp Tbk':                        'NISP',
    'Bank OCBC NISP Tbk':                        'NISP',  # case variant
    'Bank Danamon Indonesia Tbk':                'BDMN',
    'Bank Permata Tbk':                          'BNLI',
    'Bank Pan Indonesia Tbk':                    'PNBN',
    'Bank Panin Tbk':                            'PNBN',
    'Bank Panin Indonesia Tbk':                  'PNBN',
    'Bank Maybank Indonesia Tbk':                'BNII',
    'Bank Mega Tbk':                             'MEGA',
    # Islamic banks
    'Bank Syariah Indonesia Tbk':                'BRIS',
    'Bank BTPN Syariah Tbk':                     'BTPS',
    'Bank Panin Dubai Syariah Tbk':              'PNBS',
    # Other listed banks
    'Bank BTPN Tbk':                             'BTPN',
    'Bank KB Bukopin Tbk':                       'BBKP',
    'Bank Bukopin Tbk':                          'BBKP',
    'Bank Mayapada Internasional Tbk':           'MAYA',
    'Bank Mayapada International Tbk':           'MAYA',
    'Bank Sinarmas Tbk':                         'BSIM',
    'Bank Jago Tbk':                             'ARTO',
    # Unattributable categories
    'Bank asing lainnya':                        'UNATTRIBUTED',
    'Bank asing':                                'UNATTRIBUTED',
    'Pinjaman sindikasi':                        'UNATTRIBUTED',
    'Lembaga keuangan lainnya':                  'UNATTRIBUTED',
    'Bank lokal lainnya':                        'UNATTRIBUTED',
    'Lembaga keuangan lain':                     'UNATTRIBUTED',
}

# Partial-match patterns for fuzzy fallback (checked in order)
BANK_PARTIAL_MAP = [
    ('mandiri',         'BMRI'),
    ('rakyat indonesia', 'BBRI'),
    ('negara indonesia', 'BBNI'),
    ('tabungan negara',  'BBTN'),
    ('central asia',     'BBCA'),
    ('cimb niaga',       'BNGA'),
    ('ocbc',             'NISP'),
    ('danamon',          'BDMN'),
    ('permata',          'BNLI'),
    ('pan indonesia',    'PNBN'),
    ('panin',            'PNBN'),
    ('maybank',          'BNII'),
    ('mega',             'MEGA'),
    ('syariah indonesia', 'BRIS'),
    ('btpn syariah',     'BTPS'),
    ('btpn',             'BTPN'),
    ('bukopin',          'BBKP'),
    ('kb bukopin',       'BBKP'),
    ('mayapada',         'MAYA'),
    ('sinarmas',         'BSIM'),
    ('jago',             'ARTO'),
    ('asing',            'UNATTRIBUTED'),
    ('sindikasi',        'UNATTRIBUTED'),
    ('lembaga keuangan', 'UNATTRIBUTED'),
    ('lokal lainnya',    'UNATTRIBUTED'),
]


def map_bank_name(name):
    """Map a bank name string to an IDX ticker."""
    if pd.isna(name):
        return 'UNATTRIBUTED'

    name_clean = str(name).strip()

    # Exact match first
    if name_clean in BANK_NAME_MAP:
        return BANK_NAME_MAP[name_clean]

    # Partial match (case-insensitive)
    name_lower = name_clean.lower()
    for pattern, ticker in BANK_PARTIAL_MAP:
        if pattern in name_lower:
            return ticker

    # If nothing matched, flag as unattributed
    return 'UNATTRIBUTED'


def convert_to_usd_millions(row):
    """
    Convert a loan amount to USD millions based on the reporting_currency
    and rounding convention.

    Key logic:
    - reporting_currency = "Dollar Amerika / USD":
        The amount is denominated in USD.
        - rounding = "Ribuan / In Thousand": amount is in USD thousands
            -> USD millions = amount / 1000
        - rounding = "Satuan Penuh / Full Amount": amount is in full USD
            -> USD millions = amount / 1e6

    - reporting_currency = "Rupiah / IDR":
        The amount is denominated in IDR.
        - rounding = "Ribuan / In Thousand": amount is in IDR thousands
            -> USD millions = (amount * 1000) / FX / 1e6
        - rounding = "Satuan Penuh / Full Amount": amount is in full IDR
            -> USD millions = amount / FX / 1e6
        - rounding = "Jutaan / In Million": amount is in IDR millions
            -> USD millions = (amount * 1e6) / FX / 1e6 = amount / FX
    """
    amount = row['amount']
    if pd.isna(amount) or amount == 0:
        return 0.0

    rounding = str(row.get('rounding', '')).strip()
    reporting = str(row.get('reporting_currency', '')).strip()

    is_usd_reporting = 'usd' in reporting.lower() or 'dollar' in reporting.lower()
    is_idr_reporting = 'idr' in reporting.lower() or 'rupiah' in reporting.lower()
    is_ribuan = 'ribuan' in rounding.lower() or 'thousand' in rounding.lower()
    is_full = 'satuan' in rounding.lower() or 'full' in rounding.lower()
    is_jutaan = 'jutaan' in rounding.lower() or 'million' in rounding.lower()

    if is_usd_reporting:
        if is_ribuan:
            # Amount is in USD thousands
            return amount / 1_000
        elif is_full:
            # Amount is in full USD
            return amount / 1_000_000
        elif is_jutaan:
            # Amount is in USD millions (unlikely but handle)
            return amount
        else:
            # Default: assume full USD
            return amount / 1_000_000
    elif is_idr_reporting:
        if is_ribuan:
            # Amount is in IDR thousands
            return (amount * 1_000) / FX_IDR_USD / 1_000_000
        elif is_full:
            # Amount is in full IDR
            return amount / FX_IDR_USD / 1_000_000
        elif is_jutaan:
            # Amount is in IDR millions
            return (amount * 1_000_000) / FX_IDR_USD / 1_000_000
        else:
            # Default: assume full IDR
            return amount / FX_IDR_USD / 1_000_000
    else:
        # Unknown reporting currency -- assume USD full amount
        print(f"  WARNING: unknown reporting_currency '{reporting}' "
              f"for ticker={row.get('ticker', '?')}, bank={row.get('bank', '?')}")
        return amount / 1_000_000


def main():
    print("=" * 60)
    print("03: BUILDING BANK-COAL EXPOSURE MATRIX")
    print("=" * 60)

    # ----------------------------------------------------------
    # 1. Load data
    # ----------------------------------------------------------
    print("\n[1/6] Loading bank_loans_by_bank.csv...")
    df = pd.read_csv(COAL_OUTPUT / "bank_loans_by_bank.csv")
    print(f"  Raw rows: {len(df)}")
    print(f"  Coal companies: {df['ticker'].nunique()} -- {sorted(df['ticker'].unique())}")
    print(f"  Years: {sorted(df['year'].unique())}")
    print(f"  Banks (raw names): {df['bank'].nunique()}")
    print(f"  Rounding types: {df['rounding'].unique().tolist()}")
    print(f"  Reporting currencies: {df['reporting_currency'].unique().tolist()}")
    print(f"  Loan currencies: {df['loan_currency'].unique().tolist()}")

    # ----------------------------------------------------------
    # 2. Map bank names to IDX tickers
    # ----------------------------------------------------------
    print("\n[2/6] Mapping bank names to IDX tickers...")
    df['bank_ticker'] = df['bank'].apply(map_bank_name)

    # Report mapping results
    unmapped = df[df['bank_ticker'] == 'UNATTRIBUTED']['bank'].unique()
    mapped = df[df['bank_ticker'] != 'UNATTRIBUTED']
    print(f"  Mapped to IDX tickers: {mapped['bank_ticker'].nunique()} unique banks")
    print(f"  Mapped bank tickers: {sorted(mapped['bank_ticker'].unique())}")
    print(f"  Unattributable categories ({len(unmapped)}):")
    for name in sorted(unmapped):
        n_rows = len(df[df['bank'] == name])
        print(f"    '{name}' ({n_rows} rows)")

    # ----------------------------------------------------------
    # 3. Convert amounts to USD millions
    # ----------------------------------------------------------
    print("\n[3/6] Converting amounts to USD millions...")
    df['amount_usd_m'] = df.apply(convert_to_usd_millions, axis=1)

    # Sanity checks
    print(f"  Total loan exposure (all years): ${df['amount_usd_m'].sum():,.1f}M")
    print(f"  Min: ${df['amount_usd_m'].min():,.4f}M | Max: ${df['amount_usd_m'].max():,.1f}M")

    # ----------------------------------------------------------
    # 4. Filter to latest year per coal company
    # ----------------------------------------------------------
    print("\n[4/6] Filtering to latest year per coal company...")
    latest_year = df.groupby('ticker')['year'].max().reset_index()
    latest_year.columns = ['ticker', 'latest_year']
    df = df.merge(latest_year, on='ticker')
    df = df[df['year'] == df['latest_year']].copy()
    df = df.drop(columns=['latest_year'])
    print(f"  Rows after latest-year filter: {len(df)}")
    print(f"  Year per coal company:")
    for t in sorted(df['ticker'].unique()):
        yr = df.loc[df['ticker'] == t, 'year'].iloc[0]
        n_banks = df.loc[df['ticker'] == t, 'bank_ticker'].nunique()
        total = df.loc[df['ticker'] == t, 'amount_usd_m'].sum()
        print(f"    {t} ({yr}): {n_banks} banks, ${total:,.1f}M total")

    # ----------------------------------------------------------
    # 5. Aggregate and build exposure matrix
    # ----------------------------------------------------------
    print("\n[5/6] Building exposure matrix...")

    # Aggregate: sum amounts per bank_ticker x coal_ticker
    agg = (df.groupby(['bank_ticker', 'ticker'])['amount_usd_m']
           .sum()
           .reset_index())

    # Pivot to matrix: rows = bank_ticker, columns = coal_ticker
    matrix = agg.pivot_table(
        index='bank_ticker', columns='ticker',
        values='amount_usd_m', aggfunc='sum', fill_value=0
    )

    # Add row totals
    matrix['TOTAL'] = matrix.sum(axis=1)

    # Sort by total exposure descending
    matrix = matrix.sort_values('TOTAL', ascending=False)

    # Save matrix
    matrix_path = OUT / "exposure_matrix.csv"
    matrix.to_csv(matrix_path)
    print(f"  Saved: {matrix_path}")
    print(f"  Matrix shape: {matrix.shape[0]} banks x {matrix.shape[1]-1} coal companies")

    # ----------------------------------------------------------
    # 6. Build exposure summary
    # ----------------------------------------------------------
    print("\n[6/6] Building exposure summary...")

    # Per coal company: attributed vs unattributed
    summary_rows = []
    for coal_ticker in sorted(df['ticker'].unique()):
        coal_df = df[df['ticker'] == coal_ticker]
        yr = coal_df['year'].iloc[0]
        total = coal_df['amount_usd_m'].sum()
        attributed = coal_df[coal_df['bank_ticker'] != 'UNATTRIBUTED']['amount_usd_m'].sum()
        unattributed = coal_df[coal_df['bank_ticker'] == 'UNATTRIBUTED']['amount_usd_m'].sum()
        n_banks = coal_df[coal_df['bank_ticker'] != 'UNATTRIBUTED']['bank_ticker'].nunique()
        bank_list = (coal_df[coal_df['bank_ticker'] != 'UNATTRIBUTED']['bank_ticker']
                     .unique().tolist())

        summary_rows.append({
            'coal_ticker': coal_ticker,
            'year': yr,
            'total_exposure_usd_m': round(total, 4),
            'attributed_usd_m': round(attributed, 4),
            'unattributed_usd_m': round(unattributed, 4),
            'pct_attributed': round(attributed / total * 100, 1) if total > 0 else 0,
            'n_identified_banks': n_banks,
            'identified_banks': '; '.join(sorted(bank_list)),
        })

    summary = pd.DataFrame(summary_rows)
    summary = summary.sort_values('total_exposure_usd_m', ascending=False)

    summary_path = OUT / "exposure_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"  Saved: {summary_path}")

    # ----------------------------------------------------------
    # PRINT SUMMARY STATISTICS
    # ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("EXPOSURE SUMMARY STATISTICS")
    print("=" * 60)

    total_all = df['amount_usd_m'].sum()
    total_attr = df[df['bank_ticker'] != 'UNATTRIBUTED']['amount_usd_m'].sum()
    total_unattr = df[df['bank_ticker'] == 'UNATTRIBUTED']['amount_usd_m'].sum()

    print(f"\nTotal identified exposure:   ${total_all:>12,.1f}M")
    print(f"  Attributed to IDX banks:   ${total_attr:>12,.1f}M ({total_attr/total_all*100:.1f}%)")
    print(f"  Unattributed (foreign/syndicated): ${total_unattr:>12,.1f}M ({total_unattr/total_all*100:.1f}%)")

    # Number of unique bank-coal links
    links = agg[agg['bank_ticker'] != 'UNATTRIBUTED']
    print(f"\nNumber of bank-coal links (attributed): {len(links)}")
    print(f"Number of IDX-listed banks with coal exposure: {links['bank_ticker'].nunique()}")
    print(f"Number of coal companies in data: {df['ticker'].nunique()}")

    # Top 10 exposures (attributed)
    print(f"\nTop 10 bank-coal exposures (attributed):")
    top10 = (links.sort_values('amount_usd_m', ascending=False)
             .head(10)
             .reset_index(drop=True))
    for _, row in top10.iterrows():
        print(f"  {row['bank_ticker']:>6s} -> {row['ticker']:<6s}: ${row['amount_usd_m']:>10,.2f}M")

    # Top banks by total coal exposure
    print(f"\nTop banks by total coal exposure (attributed):")
    bank_totals = (links.groupby('bank_ticker')['amount_usd_m']
                   .sum()
                   .sort_values(ascending=False))
    for bank, total in bank_totals.items():
        n_coal = links[links['bank_ticker'] == bank]['ticker'].nunique()
        print(f"  {bank:>6s}: ${total:>10,.2f}M across {n_coal} coal companies")

    # Top coal companies by total bank borrowing
    print(f"\nTop coal companies by total bank borrowing (latest year):")
    coal_totals = (df.groupby('ticker')['amount_usd_m']
                   .sum()
                   .sort_values(ascending=False)
                   .head(10))
    for coal, total in coal_totals.items():
        print(f"  {coal:<6s}: ${total:>10,.2f}M")

    return matrix, summary


if __name__ == "__main__":
    main()

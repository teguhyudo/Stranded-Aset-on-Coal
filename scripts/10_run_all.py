"""
10_run_all.py -- Master orchestrator
====================================
Runs the entire analysis pipeline in sequence.

Usage: python scripts/10_run_all.py
"""

import sys
import importlib
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
setup = importlib.import_module('00_setup')

SCRIPTS = [
    ('01_clean_coal_data', '01: Clean coal data'),
    ('02_clean_bank_data', '02: Clean bank data'),
    ('03_build_exposure_matrix', '03: Build exposure matrix'),
    ('04_model1_stranded_assets', '04: Model 1 - Stranded assets'),
    ('05_model2_bank_stress', '05: Model 2 - Bank stress test'),
    ('06_model3_macro_transmission', '06: Model 3 - Macro transmission'),
    ('07_figures', '07: Generate figures'),
    ('08_tables', '08: Generate tables'),
    ('09_robustness', '09: Robustness analysis'),
]


def main():
    print("=" * 60)
    print("MASTER PIPELINE: Coal-Banking-Sovereign Nexus")
    print("=" * 60)

    results = []
    t0 = time.time()

    for script_name, label in SCRIPTS:
        print(f"\n{'=' * 60}")
        print(f"RUNNING: {label}")
        print(f"{'=' * 60}")
        t1 = time.time()
        try:
            mod = importlib.import_module(script_name)
            if hasattr(mod, 'main'):
                mod.main()
            elapsed = time.time() - t1
            results.append((label, 'OK', f'{elapsed:.1f}s'))
            print(f"\n  >> {label}: COMPLETED in {elapsed:.1f}s")
        except Exception as e:
            elapsed = time.time() - t1
            results.append((label, 'FAILED', str(e)[:80]))
            print(f"\n  >> {label}: FAILED after {elapsed:.1f}s -- {e}")

    total = time.time() - t0
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    for label, status, info in results:
        icon = '[OK]' if status == 'OK' else '[FAIL]'
        print(f"  {icon} {label}: {info}")
    print(f"\nTotal time: {total:.1f}s")

    n_ok = sum(1 for _, s, _ in results if s == 'OK')
    n_fail = len(results) - n_ok
    print(f"Passed: {n_ok}/{len(results)}, Failed: {n_fail}/{len(results)}")

    if n_fail > 0:
        print("\nWARNING: Some scripts failed. Check output above for details.")
        sys.exit(1)
    else:
        print("\nAll scripts completed successfully.")


if __name__ == "__main__":
    main()

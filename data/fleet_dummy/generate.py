#!/usr/bin/env python3
"""
KidecoIQ — Data Generator: Fleet Dummy Logs
=============================================
Menghasilkan CSV data log fleet alat berat sintetis untuk
pengujian pipeline deteksi anomali.

Usage:
    python generate.py                           # output di direktori ini
    python generate.py --output /path/to/log.csv # custom path
    python generate.py --units 10 --shifts 60    # custom size
"""

import argparse
import sys
import os

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.modules.operasional.fleet_data import generate_fleet_csv, DEFAULT_CSV_PATH


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic fleet log CSV")
    parser.add_argument(
        "--output",
        default=DEFAULT_CSV_PATH,
        help=f"Output CSV path (default: {DEFAULT_CSV_PATH})",
    )
    parser.add_argument("--units", type=int, default=10, help="Number of fleet units (default: 10)")
    parser.add_argument("--shifts", type=int, default=60, help="Number of shifts per unit (default: 60)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")

    args = parser.parse_args()

    path = generate_fleet_csv(
        output_path=args.output,
        num_units=args.units,
        num_shifts=args.shifts,
        seed=args.seed,
    )

    print(f"✅ Fleet log CSV generated: {path}")
    print(f"   Units: {args.units}, Shifts per unit: {args.shifts}")


if __name__ == "__main__":
    main()

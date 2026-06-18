#!/usr/bin/env python3
"""
KidecoIQ — Data Generator: Synthetic Satellite Rasters
=======================================================
Menghasilkan 2 file GeoTIFF sintetis (Red & NIR band) untuk
pengujian pipeline NDVI.

Usage:
    python generate.py                    # output di direktori ini
    python generate.py --output /path/to  # output custom
"""

import argparse
import sys
import os

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.modules.reklamasi.synthetic_raster import generate_synthetic_bands, DEFAULT_OUTPUT_DIR


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic satellite rasters for NDVI testing")
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument("--width", type=int, default=20, help="Raster width (default: 20)")
    parser.add_argument("--height", type=int, default=20, help="Raster height (default: 20)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")

    args = parser.parse_args()

    red_path, nir_path = generate_synthetic_bands(
        output_dir=args.output,
        width=args.width,
        height=args.height,
        seed=args.seed,
    )

    print(f"✅ Synthetic rasters generated:")
    print(f"   Red (B4): {red_path}")
    print(f"   NIR (B8): {nir_path}")


if __name__ == "__main__":
    main()

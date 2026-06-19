"""
KidecoIQ — Modul Reklamasi: Synthetic Raster Generator
=======================================================
Menghasilkan 2 band GeoTIFF sintetis (Red & NIR) ukuran kecil
untuk validasi pipeline NDVI. BUKAN data final — hanya untuk
pengujian dan development.

.. important::

   **Drop-in replacement untuk citra Sentinel-2 asli**

   File ini adalah *synthetic stand-in* yang memungkinkan development
   dan testing pipeline NDVI tanpa harus mengunduh citra satelit nyata.
   
   Untuk production, fungsi :func:`load_band` cukup diubah agar membaca
   file GeoTIFF dari Google Earth Engine export (atau sumber Sentinel-2
   lainnya), tanpa perubahan pada pipeline NDVI di atasnya (``ndvi.py``).
   
   Dengan kata lain::
   
       # Development (sekarang):
       red = load_band("data/satellite_samples/band4_red.tif")   # sintetis
       
       # Production (cukup ganti path):
       red = load_band("data/sentinel_scenes/2026-06-01_B04.tif")  # asli

   Semua fungsi di ``ndvi.py`` (``compute_ndvi``, ``classify_ndvi``,
   ``process_bands``, dll.) TIDAK perlu diubah — mereka bekerja pada
   numpy array yang identik strukturnya.

Region layout (20×20 pixels):
    ┌────────────┬────────────┐
    │  Region 1  │  Region 2  │
    │  sehat     │  stres     │
    │  NDVI~0.6  │  NDVI~0.3  │
    ├────────────┼────────────┤
    │  Region 3  │  Region 4  │
    │  kosong    │  air       │
    │  NDVI~0.1  │  NDVI~-0.2 │
    └────────────┴────────────┘
    Ditambah noise kecil di batas.
"""

import os
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS


def _get_project_root() -> str:
    """
    Find project root by walking up until SPEC.md is found.
    Fallback to grandparent of backend/ if marker not found.
    """
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):  # safety limit
        if os.path.isfile(os.path.join(current, "SPEC.md")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    # Fallback: backend/../../../
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Default output directory: project_root/data/satellite_samples/
DEFAULT_OUTPUT_DIR = os.path.join(
    _get_project_root(),
    "data",
    "satellite_samples",
)


def _make_synthetic_arrays(
    width: int = 20,
    height: int = 20,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic Red and NIR 2D arrays with known NDVI properties.

    Returns:
        (red_array, nir_array) each of shape (height, width).
    """
    rng = np.random.default_rng(seed)

    # Start with zeros
    red = np.zeros((height, width), dtype=np.float64)
    nir = np.zeros((height, width), dtype=np.float64)

    half_h, half_w = height // 2, width // 2

    # Region 1: Vegetasi Sehat (top-left)
    # NDVI ≈ 0.6  →  NIR=0.8, Red=0.2
    red[0:half_h, 0:half_w] = 0.20
    nir[0:half_h, 0:half_w] = 0.80

    # Region 2: Vegetasi Stres (top-right)
    # NDVI ≈ 0.3  →  NIR=0.65, Red=0.35
    red[0:half_h, half_w:] = 0.35
    nir[0:half_h, half_w:] = 0.65

    # Region 3: Lahan Kosong (bottom-left)
    # NDVI ≈ 0.1  →  NIR=0.55, Red=0.45
    red[half_h:, 0:half_w] = 0.45
    nir[half_h:, 0:half_w] = 0.55

    # Region 4: Air (bottom-right)
    # NDVI ≈ -0.2  →  NIR=0.2, Red=0.3
    red[half_h:, half_w:] = 0.30
    nir[half_h:, half_w:] = 0.20

    # Add small random noise (±0.02) to create realistic variation
    noise_red = rng.normal(0, 0.02, size=(height, width))
    noise_nir = rng.normal(0, 0.02, size=(height, width))
    red = np.clip(red + noise_red, 0.0, 1.0)
    nir = np.clip(nir + noise_nir, 0.0, 1.0)

    return red, nir


def generate_synthetic_bands(
    output_dir: str = DEFAULT_OUTPUT_DIR,
    width: int = 20,
    height: int = 20,
    seed: int = 42,
) -> tuple[str, str]:
    """
    Generate and save synthetic Red (B4) and NIR (B8) GeoTIFF files.

    Args:
        output_dir: Directory to write files.
        width: Raster width in pixels.
        height: Raster height in pixels.
        seed: Random seed for reproducibility.

    Returns:
        (red_path, nir_path) — absolute paths to created files.
    """
    os.makedirs(output_dir, exist_ok=True)

    red_path = os.path.join(output_dir, "band4_red.tif")
    nir_path = os.path.join(output_dir, "band8_nir.tif")

    red, nir = _make_synthetic_arrays(width, height, seed)

    # Dummy geospatial metadata
    # Transform: west (left), north (top), xsize, ysize
    transform = from_origin(117.0, -1.0, 0.0001, 0.0001)
    crs = CRS.from_epsg(4326)

    # Write Red band
    with rasterio.open(
        red_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=red.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(red, 1)

    # Write NIR band
    with rasterio.open(
        nir_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=nir.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(nir, 1)

    return red_path, nir_path


def load_band(filepath: str) -> np.ndarray:
    """
    Load a single-band GeoTIFF as a 2D numpy array.

    Args:
        filepath: Path to GeoTIFF file.

    Returns:
        2D numpy array of band data.
    """
    with rasterio.open(filepath) as src:
        return src.read(1).astype(np.float64)


# ── CLI entry point ───────────────────────────────────────────

if __name__ == "__main__":
    paths = generate_synthetic_bands()
    print(f"✅ Synthetic rasters created:")
    print(f"   Red: {paths[0]}")
    print(f"   NIR: {paths[1]}")

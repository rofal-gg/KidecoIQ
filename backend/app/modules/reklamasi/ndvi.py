"""
KidecoIQ — Modul Reklamasi: NDVI Processing & Classification
=============================================================

Pipeline:
    compute_ndvi(red, nir) → classify_ndvi(ndvi) → classify_to_label(array)

NDVI Formula:
    NDVI = (NIR - Red) / (NIR + Red)

4-class threshold (MVP — dapat disesuaikan dengan data lapangan nanti):
    - air            : NDVI < 0.0
    - lahan_kosong   : 0.0 ≤ NDVI < 0.25
    - vegetasi_stres : 0.25 ≤ NDVI < 0.45
    - vegetasi_sehat : NDVI ≥ 0.45
"""

import numpy as np

# ── Classification constants ──────────────────────────────────

# Integer codes for each class
CLASS_AIR: int = 0
CLASS_LAHAN_KOSONG: int = 1
CLASS_VEGETASI_STRES: int = 2
CLASS_VEGETASI_SEHAT: int = 3

# Human-readable labels (order matches integer codes)
CLASS_LABELS: list[str] = [
    "air",
    "lahan_kosong",
    "vegetasi_stres",
    "vegetasi_sehat",
]

# Lookup dict: int code → label string
CLASS_MAP: dict[int, str] = {i: label for i, label in enumerate(CLASS_LABELS)}

# Valid set for assertions in tests
VALID_CLASSES: set[int] = set(CLASS_MAP.keys())

# Threshold boundaries (inclusive on left, exclusive on right except last)
# air: (-inf, 0.0)
# lahan_kosong: [0.0, 0.25)
# vegetasi_stres: [0.25, 0.45)
# vegetasi_sehat: [0.45, +inf)
NDVI_THRESHOLDS: list[float] = [0.0, 0.25, 0.45]


def compute_ndvi(red: np.ndarray, nir: np.ndarray, epsilon: float = 1e-10) -> np.ndarray:
    """
    Compute NDVI from Red and NIR band arrays.

    Args:
        red: 2D numpy array of Red band reflectance (B4 for Sentinel-2).
        nir: 2D numpy array of NIR band reflectance (B8 for Sentinel-2).
        epsilon: Small constant to avoid division by zero.

    Returns:
        2D numpy array of NDVI values, clipped to [-1, 1].

    Raises:
        ValueError: If red and nir have different shapes.
    """
    if red.shape != nir.shape:
        raise ValueError(
            f"Red shape {red.shape} does not match NIR shape {nir.shape}"
        )

    red = red.astype(np.float64)
    nir = nir.astype(np.float64)

    denominator = nir + red
    # Avoid division by zero: where denominator ≈ 0, NDVI = 0
    ndvi = np.divide(
        nir - red,
        denominator,
        out=np.zeros_like(denominator),
        where=np.abs(denominator) > epsilon,
    )
    # Clip to [-1, 1] to handle floating-point edge cases
    ndvi = np.clip(ndvi, -1.0, 1.0)

    return ndvi


def classify_ndvi(ndvi: np.ndarray) -> np.ndarray:
    """
    Classify NDVI array into 4 integer categories using thresholds.

    Args:
        ndvi: 2D numpy array of NDVI values.

    Returns:
        2D integer numpy array with values in {0, 1, 2, 3}.
    """
    # Start with everything as "air" (0)
    classes = np.full(ndvi.shape, CLASS_AIR, dtype=np.int8)

    # Apply thresholds from lowest to highest
    classes[ndvi >= NDVI_THRESHOLDS[0]] = CLASS_LAHAN_KOSONG   # ≥ 0.0
    classes[ndvi >= NDVI_THRESHOLDS[1]] = CLASS_VEGETASI_STRES # ≥ 0.25
    classes[ndvi >= NDVI_THRESHOLDS[2]] = CLASS_VEGETASI_SEHAT # ≥ 0.45

    return classes


def classify_to_label(ndvi: np.ndarray) -> np.ndarray:
    """
    Classify NDVI array and return human-readable string labels.

    Args:
        ndvi: 2D numpy array of NDVI values.

    Returns:
        2D numpy array of strings (dtype='<U16').
    """
    codes = classify_ndvi(ndvi)
    labels = np.vectorize(CLASS_MAP.get)(codes)
    return labels


# ── Convenience: compute + label in one call ──────────────────

def process_bands(red: np.ndarray, nir: np.ndarray) -> dict:
    """
    Full pipeline: compute NDVI, classify, return results as a dict.

    Args:
        red: 2D numpy array of Red band.
        nir: 2D numpy array of NIR band.

    Returns:
        dict with keys:
            - 'ndvi': raw NDVI array
            - 'classification_codes': integer codes array
            - 'classification_labels': string labels array
            - 'ndvi_mean', 'ndvi_min', 'ndvi_max': summary stats
            - 'vegetation_cover_pct': percentage of pixels with
              NDVI ≥ 0.25 (stressed + healthy)
    """
    ndvi = compute_ndvi(red, nir)
    codes = classify_ndvi(ndvi)

    # Vegetation cover = stressed + healthy (class 2 & 3)
    veg_mask = codes >= CLASS_VEGETASI_STRES
    vegetation_cover_pct = float(np.mean(veg_mask) * 100)

    return {
        "ndvi": ndvi,
        "classification_codes": codes,
        "classification_labels": classify_to_label(ndvi),
        "ndvi_mean": float(np.mean(ndvi)),
        "ndvi_min": float(np.min(ndvi)),
        "ndvi_max": float(np.max(ndvi)),
        "vegetation_cover_pct": round(vegetation_cover_pct, 2),
    }

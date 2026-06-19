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


# ── RandomForest classifier (upgrade path) ──────────────────────

def _generate_training_data(
    n_samples_per_class: int = 100,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic NDVI training data for all 4 vegetation classes.

    Each class is modeled as a normal distribution around a representative
    NDVI mean with small standard deviation, mimicking real-world variation.

    Args:
        n_samples_per_class: Number of training samples per class.
        seed: Random seed for reproducibility.

    Returns:
        (X, y):
            X: shape (n_samples, 1) — NDVI values.
            y: shape (n_samples,) — integer class codes (0..3).
    """
    rng = np.random.default_rng(seed)

    # (class_code, mean_ndvi, std_dev)
    class_params = [
        (CLASS_AIR, -0.30, 0.15),              # air around -0.3
        (CLASS_LAHAN_KOSONG, 0.12, 0.08),      # bare land around 0.12
        (CLASS_VEGETASI_STRES, 0.35, 0.06),    # stressed around 0.35
        (CLASS_VEGETASI_SEHAT, 0.60, 0.08),    # healthy around 0.60
    ]

    X_list: list[np.ndarray] = []
    y_list: list[np.ndarray] = []

    for class_code, mean, std in class_params:
        samples = rng.normal(mean, std, n_samples_per_class)
        samples = np.clip(samples, -1.0, 1.0)  # stay within NDVI bounds
        X_list.append(samples)
        y_list.append(np.full(n_samples_per_class, class_code, dtype=np.int8))

    X = np.concatenate(X_list).reshape(-1, 1)
    y = np.concatenate(y_list)
    return X, y


def classify_with_random_forest(
    ndvi_array: np.ndarray,
    n_samples_per_class: int = 100,
    seed: int = 42,
) -> tuple[np.ndarray, "RandomForestClassifier"]:  # noqa: F821
    """
    Classify NDVI array using RandomForest as an alternative to threshold.

    This is an **upgrade path** — for MVP, threshold classification remains
    the default. RandomForest becomes the preferred method once real labeled
    field data is available to replace the synthetic training data.

    Training data: synthetic NDVI samples representing all 4 classes,
    generated via :func:`_generate_training_data`.

    Args:
        ndvi_array: 2D numpy array of NDVI values in [-1, 1].
        n_samples_per_class: Training samples per class (total samples = 4 × N).
        seed: Random seed for reproducibility.

    Returns:
        (label_array, trained_model):
            - label_array: 2D string array with shape matching ndvi_array,
              containing labels like ``"vegetasi_sehat"``.
            - trained_model: Fitted ``RandomForestClassifier`` instance,
              ready for further use or inspection.
    """
    from sklearn.ensemble import RandomForestClassifier

    # 1. Generate synthetic training data
    X_train, y_train = _generate_training_data(n_samples_per_class, seed)

    # 2. Train the model
    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=5,
        random_state=seed,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    # 3. Predict on input
    flat_input = ndvi_array.ravel().reshape(-1, 1)
    flat_pred = model.predict(flat_input)

    # 4. Map integer predictions to string labels
    label_array = np.array(
        [CLASS_MAP.get(int(c), "unknown") for c in flat_pred],
        dtype="<U16",
    ).reshape(ndvi_array.shape)

    return label_array, model


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

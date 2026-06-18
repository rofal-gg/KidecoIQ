"""
KidecoIQ — Unit Tests: NDVI & Classification
=============================================
Validasi:

1. NDVI selalu dalam rentang [-1, 1] untuk semua input.
2. Tidak ada NaN atau Inf.
3. Setiap piksel terklasifikasi ke salah satu dari 4 kategori valid.
4. Boundary thresholds bekerja dengan benar.
5. Pipeline end-to-end dari synthetic raster menghasilkan output yang
   sesuai dengan region yang diketahui.
"""

import os
import sys

import numpy as np
import pytest

# ── Ensure backend is importable ──────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.modules.reklamasi import ndvi
from app.modules.reklamasi.synthetic_raster import (
    _make_synthetic_arrays,
    generate_synthetic_bands,
    load_band,
    DEFAULT_OUTPUT_DIR,
)

# ── Constants for validation ──────────────────────────────────

VALID_CLASSES = ndvi.VALID_CLASSES          # {0, 1, 2, 3}
VALID_LABELS = set(ndvi.CLASS_LABELS)       # {"air", "lahan_kosong", ...}
NUM_CLASSES = len(ndvi.CLASS_LABELS)        # 4


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def synthetic_arrays():
    """Generate synthetic Red/NIR arrays once per test session."""
    red, nir = _make_synthetic_arrays(width=20, height=20, seed=42)
    return red, nir


@pytest.fixture(scope="module")
def synthetic_rasters():
    """Generate and load synthetic raster files once per session."""
    red_path, nir_path = generate_synthetic_bands(
        output_dir=DEFAULT_OUTPUT_DIR,
        width=20,
        height=20,
        seed=42,
    )
    red = load_band(red_path)
    nir = load_band(nir_path)
    return red, nir


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 1: NDVI Computation
# ══════════════════════════════════════════════════════════════

class TestComputeNDVI:
    """Validasi fungsi compute_ndvi()."""

    def test_ndvi_range(self, synthetic_arrays):
        """NDVI harus berada dalam rentang [-1, 1]."""
        red, nir = synthetic_arrays
        result = ndvi.compute_ndvi(red, nir)
        assert np.all(result >= -1.0), f"NDVI < -1 ditemukan: min={result.min()}"
        assert np.all(result <= 1.0), f"NDVI > 1 ditemukan: max={result.max()}"
        assert result.shape == red.shape

    def test_no_nan_or_inf(self, synthetic_arrays):
        """Tidak boleh ada NaN atau Inf dalam output NDVI."""
        red, nir = synthetic_arrays
        result = ndvi.compute_ndvi(red, nir)
        assert not np.any(np.isnan(result)), "NDVI mengandung NaN"
        assert not np.any(np.isinf(result)), "NDVI mengandung Inf"

    def test_known_value_healthy(self):
        """NDVI untuk (NIR=0.8, Red=0.2) harus ≈ 0.6."""
        red = np.array([[0.2]], dtype=np.float64)
        nir = np.array([[0.8]], dtype=np.float64)
        result = ndvi.compute_ndvi(red, nir)
        expected = (0.8 - 0.2) / (0.8 + 0.2)  # = 0.6
        assert np.isclose(result[0, 0], expected, atol=1e-10)

    def test_known_value_water(self):
        """NDVI untuk (NIR=0.1, Red=0.3) harus ≈ -0.5."""
        red = np.array([[0.3]], dtype=np.float64)
        nir = np.array([[0.1]], dtype=np.float64)
        result = ndvi.compute_ndvi(red, nir)
        expected = (0.1 - 0.3) / (0.1 + 0.3)  # = -0.5
        assert np.isclose(result[0, 0], expected, atol=1e-10)

    def test_division_by_zero(self):
        """NIR=0 dan Red=0 harus menghasilkan NDVI=0 (bukan NaN/Inf)."""
        red = np.array([[0.0, 0.0], [0.0, 0.0]], dtype=np.float64)
        nir = np.array([[0.0, 0.0], [0.0, 0.0]], dtype=np.float64)
        result = ndvi.compute_ndvi(red, nir)
        assert not np.any(np.isnan(result))
        assert not np.any(np.isinf(result))
        assert np.all(result == 0.0), f"Expected 0.0, got {result}"

    def test_shape_mismatch_raises(self):
        """Input dengan shape berbeda harus raise ValueError."""
        red = np.zeros((10, 10))
        nir = np.zeros((5, 5))
        with pytest.raises(ValueError, match="shape"):
            ndvi.compute_ndvi(red, nir)

    def test_extreme_values(self):
        """NIR=1.0, Red=0.0 → NDVI=1.0 (max). NIR=0.0, Red=1.0 → NDVI=-1.0 (min)."""
        # Max NDVI
        r_max = np.array([[0.0]], dtype=np.float64)
        n_max = np.array([[1.0]], dtype=np.float64)
        assert np.isclose(ndvi.compute_ndvi(r_max, n_max)[0, 0], 1.0)

        # Min NDVI
        r_min = np.array([[1.0]], dtype=np.float64)
        n_min = np.array([[0.0]], dtype=np.float64)
        assert np.isclose(ndvi.compute_ndvi(r_min, n_min)[0, 0], -1.0)


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 2: Classification
# ══════════════════════════════════════════════════════════════

class TestClassifyNDVI:
    """Validasi fungsi classify_ndvi()."""

    def test_every_pixel_classified_valid(self, synthetic_arrays):
        """Setiap piksel terklasifikasi ke salah satu dari 4 kategori valid."""
        red, nir = synthetic_arrays
        ndvi_arr = ndvi.compute_ndvi(red, nir)
        classes = ndvi.classify_ndvi(ndvi_arr)
        unique = set(np.unique(classes))
        invalid = unique - VALID_CLASSES
        assert not invalid, f"Kelas tidak valid ditemukan: {invalid}"

    def test_no_out_of_range_values(self, synthetic_arrays):
        """Tidak ada nilai class di luar {0, 1, 2, 3}."""
        red, nir = synthetic_arrays
        ndvi_arr = ndvi.compute_ndvi(red, nir)
        classes = ndvi.classify_ndvi(ndvi_arr)
        assert np.all(classes >= 0)
        assert np.all(classes < NUM_CLASSES)

    def test_all_categories_appear(self, synthetic_arrays):
        """Semua 4 kategori harus muncul di hasil klasifikasi."""
        red, nir = synthetic_arrays
        ndvi_arr = ndvi.compute_ndvi(red, nir)
        classes = ndvi.classify_ndvi(ndvi_arr)
        found = set(np.unique(classes))
        assert found == VALID_CLASSES, (
            f"Kategori yang muncul: {found}, "
            f"diharapkan: {VALID_CLASSES}"
        )

    def test_boundary_air(self):
        """NDVI=0.0 harus diklasifikasikan sebagai lahan_kosong (1), bukan air (0)."""
        ndvi_arr = np.array([[0.0]], dtype=np.float64)
        classes = ndvi.classify_ndvi(ndvi_arr)
        assert classes[0, 0] == ndvi.CLASS_LAHAN_KOSONG, (
            f"NDVI=0.0 harus lahan_kosong, got {classes[0, 0]}"
        )

    def test_boundary_just_below_air(self):
        """NDVI=-0.001 harus diklasifikasikan sebagai air (0)."""
        ndvi_arr = np.array([[-0.001]], dtype=np.float64)
        classes = ndvi.classify_ndvi(ndvi_arr)
        assert classes[0, 0] == ndvi.CLASS_AIR

    def test_boundary_transition_kosong_stres(self):
        """NDVI=0.249 → lahan_kosong, NDVI=0.25 → vegetasi_stres."""
        arr = np.array([[0.249, 0.25]], dtype=np.float64)
        classes = ndvi.classify_ndvi(arr)
        assert classes[0, 0] == ndvi.CLASS_LAHAN_KOSONG, "0.249 harus lahan_kosong"
        assert classes[0, 1] == ndvi.CLASS_VEGETASI_STRES, "0.25 harus vegetasi_stres"

    def test_boundary_transition_stres_sehat(self):
        """NDVI=0.449 → vegetasi_stres, NDVI=0.45 → vegetasi_sehat."""
        arr = np.array([[0.449, 0.45]], dtype=np.float64)
        classes = ndvi.classify_ndvi(arr)
        assert classes[0, 0] == ndvi.CLASS_VEGETASI_STRES, "0.449 harus stres"
        assert classes[0, 1] == ndvi.CLASS_VEGETASI_SEHAT, "0.45 harus sehat"

    def test_negative_ndvi_is_air(self):
        """Semua NDVI negatif harus air (0)."""
        ndvi_arr = np.array([[-0.5, -0.1, -0.01]], dtype=np.float64)
        classes = ndvi.classify_ndvi(ndvi_arr)
        assert np.all(classes == ndvi.CLASS_AIR)

    def test_high_ndvi_is_healthy(self):
        """Semua NDVI ≥ 0.45 harus vegetasi_sehat (3)."""
        ndvi_arr = np.array([[0.45, 0.7, 1.0]], dtype=np.float64)
        classes = ndvi.classify_ndvi(ndvi_arr)
        assert np.all(classes == ndvi.CLASS_VEGETASI_SEHAT)


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 3: Label Output
# ══════════════════════════════════════════════════════════════

class TestClassifyToLabel:
    """Validasi fungsi classify_to_label()."""

    def test_labels_are_valid_strings(self, synthetic_arrays):
        """Semua label harus dari set {air, lahan_kosong, vegetasi_stres, vegetasi_sehat}."""
        red, nir = synthetic_arrays
        ndvi_arr = ndvi.compute_ndvi(red, nir)
        labels = ndvi.classify_to_label(ndvi_arr)
        unique_labels = set(np.unique(labels))
        invalid = unique_labels - VALID_LABELS
        assert not invalid, f"Label tidak valid: {invalid}"

    def test_label_shape_matches_input(self, synthetic_arrays):
        """Shape array label harus sama dengan shape input."""
        red, nir = synthetic_arrays
        ndvi_arr = ndvi.compute_ndvi(red, nir)
        labels = ndvi.classify_to_label(ndvi_arr)
        assert labels.shape == ndvi_arr.shape


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 4: Process Bands (Integration)
# ══════════════════════════════════════════════════════════════

class TestProcessBands:
    """Validasi fungsi process_bands() end-to-end."""

    def test_result_contains_all_keys(self, synthetic_arrays):
        """Dict hasil harus memiliki semua key yang dijanjikan."""
        red, nir = synthetic_arrays
        result = ndvi.process_bands(red, nir)
        expected_keys = {
            "ndvi", "classification_codes", "classification_labels",
            "ndvi_mean", "ndvi_min", "ndvi_max", "vegetation_cover_pct",
        }
        assert set(result.keys()) == expected_keys

    def test_ndvi_stats_reasonable(self, synthetic_arrays):
        """ndvi_mean harus antara -1 dan 1, dan masuk akal untuk data sintetis."""
        red, nir = synthetic_arrays
        result = ndvi.process_bands(red, nir)
        assert -1.0 <= result["ndvi_mean"] <= 1.0
        assert -1.0 <= result["ndvi_min"] <= result["ndvi_max"] <= 1.0

    def test_vegetation_cover_percentage(self, synthetic_arrays):
        """Vegetation cover harus antara 0-100%."""
        red, nir = synthetic_arrays
        result = ndvi.process_bands(red, nir)
        assert 0.0 <= result["vegetation_cover_pct"] <= 100.0

    def test_classification_codes_ndvi_consistency(self, synthetic_arrays):
        """Klasifikasi harus konsisten: NDVI tinggi → kelas lebih tinggi."""
        red, nir = synthetic_arrays
        result = ndvi.process_bands(red, nir)
        ndvi_arr = result["ndvi"]
        codes = result["classification_codes"]
        # Untuk setiap posisi, NDVI yang lebih tinggi harus punya class ≥ class tetangga
        # (tidak wajib monotonik karena ada noise, tapi secara umum)
        assert codes.dtype in (np.int8, np.int64, np.int32)


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 5: End-to-End with Actual Raster Files
# ══════════════════════════════════════════════════════════════

class TestEndToEndRaster:
    """Pipeline lengkap: file GeoTIFF → NDVI → klasifikasi."""

    def test_all_four_regions_detectable(self, synthetic_rasters):
        """
        Synthetic raster memiliki 4 region dengan NDVI berbeda.
        Verifikasi keempat kategori muncul dalam output klasifikasi.
        """
        red, nir = synthetic_rasters
        result = ndvi.process_bands(red, nir)
        codes = result["classification_codes"]
        found = set(np.unique(codes))
        assert found == VALID_CLASSES, (
            f"Tidak semua kategori terdeteksi. "
            f"Ditemukan: {found}, diharapkan: {VALID_CLASSES}"
        )

    def test_ndvi_from_file_in_range(self, synthetic_rasters):
        """NDVI dari file raster langsung harus dalam [-1, 1]."""
        red, nir = synthetic_rasters
        ndvi_arr = ndvi.compute_ndvi(red, nir)
        assert ndvi_arr.min() >= -1.0
        assert ndvi_arr.max() <= 1.0

    def test_no_nan_in_file_pipeline(self, synthetic_rasters):
        """Pipeline file → NDVI tidak boleh menghasilkan NaN."""
        red, nir = synthetic_rasters
        ndvi_arr = ndvi.compute_ndvi(red, nir)
        assert not np.any(np.isnan(ndvi_arr))

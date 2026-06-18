"""
KidecoIQ — Unit Tests: Fleet Data & Anomaly Detection
=======================================================
Validasi:

1. Data generator menghasilkan CSV dengan struktur benar.
2. Agregasi per unit bekerja dengan baik.
3. ⭐ Anomali yang sengaja disisipkan TERDETEKSI oleh IsolationForest.
4. Unit normal tidak terdeteksi sebagai anomali (false positive minimal).
5. Skor risiko maintenance dalam rentang 0-100.
6. Alert level mapping konsisten.
7. Endpoint API merespons dengan format yang benar.
"""

import os
import sys
import tempfile

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

# ── Ensure backend is importable ──────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.modules.operasional import fleet_data
from app.modules.operasional.fleet_data import (
    generate_fleet_csv,
    aggregate_shifts,
    compute_summary_with_anomaly,
    compute_risk_scores,
    INJECTED_ANOMALIES,
    UNIT_DEFINITIONS,
    CSV_COLUMNS,
)


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def raw_csv_path():
    """Generate a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        tmp_path = f.name
    generate_fleet_csv(tmp_path, num_units=10, num_shifts=60, seed=42)
    yield tmp_path
    os.unlink(tmp_path)


@pytest.fixture(scope="module")
def raw_df(raw_csv_path):
    """Load raw CSV as DataFrame."""
    return pd.read_csv(raw_csv_path)


@pytest.fixture(scope="module")
def summary_df(raw_df):
    """Aggregated + anomaly (shift-level) + risk pipeline."""
    df = compute_summary_with_anomaly(
        raw_df,
        contamination=0.02,      # hanya ~12 shift paling ekstrem
        random_state=42,
        anomaly_shift_threshold_pct=3.0,
    )
    df = compute_risk_scores(df)
    return df


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 1: Data Generator
# ══════════════════════════════════════════════════════════════

class TestDataGenerator:
    """Validasi generate_fleet_csv()."""

    def test_csv_created(self, raw_csv_path):
        """File CSV harus ada."""
        assert os.path.isfile(raw_csv_path)

    def test_csv_columns(self, raw_df):
        """Kolom harus sesuai CSV_COLUMNS."""
        assert list(raw_df.columns) == CSV_COLUMNS

    def test_all_units_present(self, raw_df):
        """Semua 10 unit harus ada di data."""
        expected_units = {uid for uid, _ in UNIT_DEFINITIONS}
        actual_units = set(raw_df["unit_id"].unique())
        assert actual_units == expected_units, (
            f"Missing units: {expected_units - actual_units}"
        )

    def test_num_rows_correct(self, raw_df):
        """Jumlah baris = 10 unit × 60 shift."""
        assert len(raw_df) == 10 * 60, f"Expected 600 rows, got {len(raw_df)}"

    def test_normal_idle_ratio_range(self, raw_df):
        """Normal data (non-anomaly) harus dalam rentang 5-25% idle ratio."""
        # Exclude injected anomaly units/shifts
        anomaly_units = {a["unit"] for a in INJECTED_ANOMALIES}
        normal_df = raw_df[~raw_df["unit_id"].isin(anomaly_units)]

        assert normal_df["idle_ratio"].min() >= 3.0, (
            f"Normal idle_ratio too low: min={normal_df['idle_ratio'].min()}"
        )
        assert normal_df["idle_ratio"].max() <= 28.0, (
            f"Normal idle_ratio too high: max={normal_df['idle_ratio'].max()}"
        )

    def test_normal_fuel_range(self, raw_df):
        """Normal data (non-anomaly) harus dalam rentang 15-30 L/h."""
        anomaly_units = {a["unit"] for a in INJECTED_ANOMALIES}
        normal_df = raw_df[~raw_df["unit_id"].isin(anomaly_units)]

        assert normal_df["fuel_consumption"].min() >= 12.0
        assert normal_df["fuel_consumption"].max() <= 33.0

    def test_anomaly_values_extreme(self, raw_df):
        """Nilai anomali harus ekstrem (jauh dari normal)."""
        for anomaly in INJECTED_ANOMALIES:
            unit_data = raw_df[raw_df["unit_id"] == anomaly["unit"]]
            unit_anomaly = unit_data[
                (unit_data["shift"] >= anomaly["shift_start"]) &
                (unit_data["shift"] <= anomaly["shift_end"])
            ]
            if anomaly["idle_ratio"] is not None:
                # idle_ratio around 68-73 vs normal 5-25
                assert unit_anomaly["idle_ratio"].mean() > 60, (
                    f"{anomaly['unit']} anomaly idle should be >60%"
                )
            if anomaly["fuel"] is not None:
                assert unit_anomaly["fuel_consumption"].mean() > 40, (
                    f"{anomaly['unit']} anomaly fuel should be >40 L/h"
                )


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 2: Aggregation
# ══════════════════════════════════════════════════════════════

class TestAggregation:
    """Validasi aggregate_shifts()."""

    def test_returns_one_row_per_unit(self, summary_df):
        """Satu baris per unit (10 unit)."""
        assert len(summary_df) == 10

    def test_has_required_columns(self, summary_df):
        """Kolom agregasi harus ada."""
        expected = {"unit_id", "idle_ratio_avg", "fuel_avg", "total_hours", "num_shifts"}
        assert expected.issubset(set(summary_df.columns)), (
            f"Missing columns: {expected - set(summary_df.columns)}"
        )

    def test_num_shifts_correct(self, summary_df):
        """Setiap unit harus punya 60 shift."""
        assert (summary_df["num_shifts"] == 60).all()

    def test_total_hours_reasonable(self, summary_df):
        """Total jam operasi per unit harus antara 500-750 (60 shift × 10-12h)."""
        assert summary_df["total_hours"].min() >= 500
        assert summary_df["total_hours"].max() <= 750


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 3: Anomaly Detection — THE CRITICAL TESTS
# ══════════════════════════════════════════════════════════════

class TestAnomalyDetection:
    """
    Validasi deteksi anomali dengan IsolationForest.

    ⚠️  KRUSIAL: Anomali yang sengaja disisipkan HARUS terdeteksi.
    Karena anomali dibuat ekstrem (idle 68% vs normal 5-25%,
    fuel 52 L/h vs normal 15-30), IsolationForest dengan
    random_state=42 harus konsisten mendeteksinya.
    """

    def test_injected_anomaly_hd002_detected(self, summary_df):
        """
        HD-002 (idle_ratio ~68%) harus terdeteksi sebagai anomali.

        Dengan normal range 5-25%, idle 68% sangat ekstrem
        sehingga IsolationForest harus menandainya.
        """
        hd002 = summary_df[summary_df["unit_id"] == "HD-002"].iloc[0]
        assert hd002["anomaly_label"] == "anomaly", (
            f"HD-002 should be anomaly (idle_ratio_avg={hd002['idle_ratio_avg']:.1f}%), "
            f"got {hd002['anomaly_label']}"
        )

    def test_injected_anomaly_ex001_detected(self, summary_df):
        """
        EX-001 (fuel ~52 L/h) harus terdeteksi sebagai anomali.

        Dengan normal range 15-30 L/h, fuel 52 L/h sangat ekstrem.
        """
        ex001 = summary_df[summary_df["unit_id"] == "EX-001"].iloc[0]
        assert ex001["anomaly_label"] == "anomaly", (
            f"EX-001 should be anomaly (fuel_avg={ex001['fuel_avg']:.1f} L/h), "
            f"got {ex001['anomaly_label']}"
        )

    def test_injected_anomaly_hd004_detected(self, summary_df):
        """
        HD-004 (idle ~73% + fuel ~45 L/h) harus terdeteksi sebagai anomali.

        Double anomaly — harus sangat jelas terdeteksi.
        """
        hd004 = summary_df[summary_df["unit_id"] == "HD-004"].iloc[0]
        assert hd004["anomaly_label"] == "anomaly", (
            f"HD-004 should be anomaly (idle_ratio_avg={hd004['idle_ratio_avg']:.1f}%, "
            f"fuel_avg={hd004['fuel_avg']:.1f} L/h), got {hd004['anomaly_label']}"
        )

    def test_normal_units_not_anomaly(self, summary_df):
        """
        Unit tanpa anomali injeksi tidak boleh terdeteksi sebagai anomali.

        Ini memvalidasi bahwa model tidak menghasilkan false positive
        untuk unit yang beroperasi normal.
        """
        anomaly_units = {a["unit"] for a in INJECTED_ANOMALIES}
        normal_units = summary_df[~summary_df["unit_id"].isin(anomaly_units)]
        false_positives = normal_units[normal_units["anomaly_label"] == "anomaly"]

        assert len(false_positives) == 0, (
            f"False positives detected on normal units: "
            f"{false_positives['unit_id'].tolist()}"
        )

    def test_anomaly_count_matches_injected(self, summary_df):
        """
        Jumlah unit yang terdeteksi anomali harus >= jumlah yang
        sengaja disisipkan (3). False positive dari unit normal
        sudah dicek di test terpisah.
        """
        anomalies = summary_df[summary_df["anomaly_label"] == "anomaly"]
        detected_units = set(anomalies["unit_id"])
        injected_units = {a["unit"] for a in INJECTED_ANOMALIES}

        assert injected_units.issubset(detected_units), (
            f"Not all injected anomalies detected. "
            f"Missing: {injected_units - detected_units}"
        )

    def test_anomaly_score_is_minus_one(self, summary_df):
        """Unit anomali harus punya anomaly_score = -1."""
        anomalies = summary_df[summary_df["anomaly_label"] == "anomaly"]
        assert (anomalies["anomaly_score"] == -1).all()


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 4: Risk Scores
# ══════════════════════════════════════════════════════════════

class TestRiskScores:
    """Validasi compute_risk_scores()."""

    def test_risk_score_in_range(self, summary_df):
        """risk_score harus dalam [0, 100]."""
        assert summary_df["risk_score"].min() >= 0.0
        assert summary_df["risk_score"].max() <= 100.0

    def test_anomaly_units_have_higher_risk(self, summary_df):
        """Unit dengan anomali harus punya risk_score lebih tinggi."""
        anomaly_units = summary_df[summary_df["anomaly_label"] == "anomaly"]
        normal_units = summary_df[summary_df["anomaly_label"] == "normal"]

        anomaly_mean = anomaly_units["risk_score"].mean()
        normal_mean = normal_units["risk_score"].mean()
        assert anomaly_mean > normal_mean, (
            f"Anomaly mean risk ({anomaly_mean:.1f}) should be > "
            f"normal mean risk ({normal_mean:.1f})"
        )

    def test_alert_level_mapping(self, summary_df):
        """alert_level harus low/medium/high sesuai range."""
        valid_levels = {"low", "medium", "high"}
        assert set(summary_df["alert_level"].unique()).issubset(valid_levels)

        for _, row in summary_df.iterrows():
            score = row["risk_score"]
            level = row["alert_level"]
            if score >= 70:
                assert level == "high", f"risk={score} should be high, got {level}"
            elif score >= 30:
                assert level == "medium", f"risk={score} should be medium, got {level}"
            else:
                assert level == "low", f"risk={score} should be low, got {level}"


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 5: Alert Generation
# ══════════════════════════════════════════════════════════════

class TestAlerts:
    """Validasi get_alerts_from_summary()."""

    def test_alerts_only_for_medium_high(self, summary_df):
        """Alert hanya untuk medium dan high risk."""
        alerts = fleet_data.get_alerts_from_summary(summary_df)
        for alert in alerts:
            assert alert["alert_level"] in ("medium", "high")

    def test_alert_has_required_fields(self, summary_df):
        """Setiap alert harus punya semua field."""
        alerts = fleet_data.get_alerts_from_summary(summary_df)
        required = {"unit_id", "alert_level", "risk_score", "message", "recommendation"}
        for alert in alerts:
            assert required.issubset(alert.keys())

    def test_low_risk_not_in_alerts(self, summary_df):
        """Unit low risk tidak boleh muncul di alerts."""
        low_units = set(summary_df[summary_df["alert_level"] == "low"]["unit_id"])
        alerts = fleet_data.get_alerts_from_summary(summary_df)
        alert_units = {a["unit_id"] for a in alerts}
        overlap = low_units & alert_units
        assert not overlap, (f"Low risk units in alerts: {overlap}")


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 6: API Endpoints
# ══════════════════════════════════════════════════════════════

class TestAPIFleet:
    """Validasi endpoint GET /operasional/fleet."""

    def test_status_200(self, client):
        resp = client.get("/operasional/fleet")
        assert resp.status_code == 200

    def test_returns_list(self, client):
        resp = client.get("/operasional/fleet")
        data = resp.json()
        assert isinstance(data, list)

    def test_has_10_units(self, client):
        resp = client.get("/operasional/fleet")
        data = resp.json()
        assert len(data) == 10

    def test_required_fields(self, client):
        resp = client.get("/operasional/fleet")
        data = resp.json()
        required = {"unit_id", "model", "status", "idle_ratio_avg", "fuel_avg",
                     "total_hours", "risk_score", "alert_level"}
        for unit in data:
            assert required.issubset(unit.keys())

    def test_risk_score_range(self, client):
        resp = client.get("/operasional/fleet")
        data = resp.json()
        for unit in data:
            assert 0.0 <= unit["risk_score"] <= 100.0

    def test_alert_level_valid(self, client):
        resp = client.get("/operasional/fleet")
        data = resp.json()
        for unit in data:
            assert unit["alert_level"] in ("low", "medium", "high")


class TestAPIAnomaly:
    """Validasi endpoint GET /operasional/fleet/{unit_id}/anomaly."""

    def test_status_200_known_unit(self, client):
        resp = client.get("/operasional/fleet/HD-001/anomaly")
        assert resp.status_code == 200

    def test_status_404_unknown_unit(self, client):
        resp = client.get("/operasional/fleet/UNKNOWN-999/anomaly")
        assert resp.status_code == 404

    def test_has_unit_id_and_shifts(self, client):
        resp = client.get("/operasional/fleet/HD-001/anomaly")
        data = resp.json()
        assert "unit_id" in data
        assert "shifts" in data
        assert data["unit_id"] == "HD-001"

    def test_anomaly_unit_has_flagged_shifts(self, client):
        """Unit dengan anomali harus punya shift yang terdeteksi."""
        resp = client.get("/operasional/fleet/HD-002/anomaly")
        data = resp.json()
        anomaly_shifts = [s for s in data["shifts"] if s["anomaly_label"] == "anomaly"]
        assert len(anomaly_shifts) > 0, (
            "HD-002 should have anomalous shifts detected"
        )

    def test_shift_has_required_fields(self, client):
        resp = client.get("/operasional/fleet/HD-001/anomaly")
        data = resp.json()
        required = {"shift", "idle_ratio", "fuel_consumption", "anomaly_score", "anomaly_label"}
        for shift in data["shifts"]:
            assert required.issubset(shift.keys())
            assert shift["anomaly_label"] in ("anomaly", "normal")


class TestAPIAlerts:
    """Validasi endpoint GET /operasional/alerts."""

    def test_status_200(self, client):
        resp = client.get("/operasional/alerts")
        assert resp.status_code == 200

    def test_has_alerts_and_total(self, client):
        resp = client.get("/operasional/alerts")
        data = resp.json()
        assert "alerts" in data
        assert "total_alerts" in data
        assert "generated_at" in data
        assert data["total_alerts"] == len(data["alerts"])

    def test_alert_fields(self, client):
        resp = client.get("/operasional/alerts")
        data = resp.json()
        required = {"unit_id", "alert_level", "risk_score", "message", "recommendation"}
        for alert in data["alerts"]:
            assert required.issubset(alert.keys())
            assert alert["alert_level"] in ("medium", "high")

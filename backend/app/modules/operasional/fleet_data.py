"""
KidecoIQ — Modul Operasional: Fleet Data Generator & Anomaly Detection
=======================================================================

Pipeline sesuai SPEC.md §6:
    1. generate_fleet_csv() — data dummy realistis dengan anomali tersisip
    2. aggregate_shifts() — hitung idle_ratio & fuel per unit per shift
    3. detect_anomalies() — IsolationForest pada [idle_ratio, fuel_consumption]
    4. compute_risk_scores() — skor risiko maintenance (0-100)

Anomali sengaja disisipkan di 3 unit untuk validasi test:
    - HD-002: shift 15-16 → idle_ratio = 68% (normal: 5-25%)
    - EX-001: shift 20-21 → fuel_consumption = 52 L/h (normal: 15-30)
    - HD-004: shift 30-31 → idle_ratio = 73% + fuel = 45 L/h
"""

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Optional

# ── Constants ─────────────────────────────────────────────────

NUM_UNITS = 10
NUM_SHIFTS = 60  # 30 hari × 2 shift

UNIT_DEFINITIONS = [
    ("HD-001", "HD785 Dump Truck"),
    ("HD-002", "HD785 Dump Truck"),
    ("HD-003", "HD785 Dump Truck"),
    ("HD-004", "HD785 Dump Truck"),
    ("HD-005", "HD785 Dump Truck"),
    ("EX-001", "PC1250 Excavator"),
    ("EX-002", "PC1250 Excavator"),
    ("EX-003", "PC1250 Excavator"),
    ("WD-001", "D375A Water Drill"),
    ("WD-002", "D375A Water Drill"),
]

# Anomaly injection plan: (unit_id, shift_start, shift_end, idle_ratio_target, fuel_target)
# idle_ratio_target=68 means we force idle ratio to ~68%
INJECTED_ANOMALIES = [
    {"unit": "HD-002", "shift_start": 15, "shift_end": 16, "idle_ratio": 68.0, "fuel": None},
    {"unit": "EX-001", "shift_start": 20, "shift_end": 21, "idle_ratio": None, "fuel": 52.0},
    {"unit": "HD-004", "shift_start": 30, "shift_end": 31, "idle_ratio": 73.0, "fuel": 45.0},
]

# Column names in the generated CSV
CSV_COLUMNS = ["unit_id", "shift", "idle_ratio", "fuel_consumption", "operating_hours"]

# ── Helper to find project root ──────────────────────────────

def _get_project_root() -> str:
    """Find project root by walking up until SPEC.md is found."""
    current = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Start from backend/app/modules/operasional, go up to project root
    # backend/app/modules/operasional → backend/app/modules → backend/app → backend → project root
    for _ in range(5):
        if os.path.isfile(os.path.join(current, "SPEC.md")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


DEFAULT_OUTPUT_DIR = os.path.join(_get_project_root(), "data", "fleet_dummy")
DEFAULT_CSV_PATH = os.path.join(DEFAULT_OUTPUT_DIR, "fleet_logs.csv")


# ══════════════════════════════════════════════════════════════
#  1. DATA GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_fleet_csv(
    output_path: str = DEFAULT_CSV_PATH,
    num_units: int = NUM_UNITS,
    num_shifts: int = NUM_SHIFTS,
    seed: int = 42,
) -> str:
    """
    Generate realistic fleet log CSV with injected anomalies.

    Returns:
        Path to generated CSV file.
    """
    rng = np.random.default_rng(seed)
    rows = []

    for unit_idx in range(num_units):
        unit_id, model = UNIT_DEFINITIONS[unit_idx]
        for shift in range(1, num_shifts + 1):
            # Normal ranges
            idle_ratio = rng.uniform(5.0, 25.0)
            fuel_consumption = rng.uniform(15.0, 30.0)
            operating_hours = rng.uniform(10.0, 12.0)  # per shift

            # Check if this unit/shift is an injected anomaly
            for anomaly in INJECTED_ANOMALIES:
                if anomaly["unit"] == unit_id and anomaly["shift_start"] <= shift <= anomaly["shift_end"]:
                    if anomaly["idle_ratio"] is not None:
                        idle_ratio = anomaly["idle_ratio"] + rng.uniform(-2.0, 2.0)
                    if anomaly["fuel"] is not None:
                        fuel_consumption = anomaly["fuel"] + rng.uniform(-3.0, 3.0)
                    break

            rows.append([unit_id, shift, round(idle_ratio, 2), round(fuel_consumption, 2), round(operating_hours, 2)])

    df = pd.DataFrame(rows, columns=CSV_COLUMNS)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


# ══════════════════════════════════════════════════════════════
#  2. AGGREGATION
# ══════════════════════════════════════════════════════════════

def aggregate_shifts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate per-unit shift data into summary features for anomaly detection.

    Returns DataFrame with columns:
        unit_id, idle_ratio_avg, fuel_avg, total_hours, num_shifts
    """
    agg = df.groupby("unit_id").agg(
        idle_ratio_avg=("idle_ratio", "mean"),
        fuel_avg=("fuel_consumption", "mean"),
        total_hours=("operating_hours", "sum"),
        num_shifts=("shift", "count"),
    ).reset_index()

    agg["idle_ratio_avg"] = agg["idle_ratio_avg"].round(2)
    agg["fuel_avg"] = agg["fuel_avg"].round(2)
    agg["total_hours"] = agg["total_hours"].round(1)
    return agg


# ══════════════════════════════════════════════════════════════
#  3. ANOMALY DETECTION (IsolationForest on SHIFT-level data)
# ══════════════════════════════════════════════════════════════

def detect_anomalies_on_shifts(
    raw_df: pd.DataFrame,
    contamination: float = 0.05,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Detect anomalous SHIFTS using IsolationForest pada
    fitur [idle_ratio, fuel_consumption].

    Args:
        raw_df: Shift-level DataFrame (unit_id, shift, idle_ratio, fuel_consumption, ...)
        contamination: Expected proportion of outlier shifts.
        random_state: Seed for reproducibility.

    Returns:
        raw_df with added columns: anomaly_score (-1/1), anomaly_label (anomaly/normal).
    """
    features = ["idle_ratio", "fuel_consumption"]
    X = raw_df[features].values

    model = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=100,
    )
    df = raw_df.copy()
    df["anomaly_score"] = model.fit_predict(X)
    df["anomaly_label"] = df["anomaly_score"].map({-1: "anomaly", 1: "normal"})
    return df


def compute_summary_with_anomaly(
    raw_df: pd.DataFrame,
    contamination: float = 0.05,
    random_state: int = 42,
    anomaly_shift_threshold_pct: float = 3.0,
) -> pd.DataFrame:
    """
    Full pipeline: detect anomalies on SHIFT level → aggregate per unit.

    Sebuah unit dianggap "anomaly" jika > anomaly_shift_threshold_pct
    dari shift-nya terdeteksi sebagai anomali oleh IsolationForest.

    Returns:
        DataFrame per-unit dengan kolom: unit_id, idle_ratio_avg, fuel_avg,
        total_hours, num_shifts, anomaly_shift_pct, anomaly_label, anomaly_score.
    """
    # Step 1: Anomaly detection on every individual shift
    raw_labeled = detect_anomalies_on_shifts(raw_df, contamination, random_state)

    # Step 2: Aggregate per unit
    summary = aggregate_shifts(raw_labeled)

    # Step 3: Calculate % of anomalous shifts per unit
    anomaly_pct = raw_labeled.groupby("unit_id")["anomaly_label"].apply(
        lambda x: (x == "anomaly").mean() * 100
    ).reset_index(name="anomaly_shift_pct")
    anomaly_pct["anomaly_shift_pct"] = anomaly_pct["anomaly_shift_pct"].round(1)

    summary = summary.merge(anomaly_pct, on="unit_id")
    summary["anomaly_label"] = summary["anomaly_shift_pct"].apply(
        lambda pct: "anomaly" if pct > anomaly_shift_threshold_pct else "normal"
    )
    summary["anomaly_score"] = summary["anomaly_label"].map({"anomaly": -1, "normal": 1}).astype(int)

    return summary


# ══════════════════════════════════════════════════════════════
#  4. MAINTENANCE RISK SCORE
# ══════════════════════════════════════════════════════════════

def compute_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute maintenance risk score (0-100) per unit.

    Formula:
        - operating_hours_factor = min(1.0, total_hours / 500) * 50
        - anomaly_factor = (jika anomaly) 40 else 0
        - risk_score = operating_hours_factor + anomaly_factor
        - clamped to [0, 100]

    Returns DataFrame with added columns:
        risk_score, alert_level
    """
    df = df.copy()
    total_max = df["total_hours"].max() if df["total_hours"].max() > 0 else 1

    df["operating_hours_factor"] = (df["total_hours"] / total_max) * 50
    # Anomaly units get +40 additional points
    df["anomaly_penalty"] = df["anomaly_label"].map({"anomaly": 40, "normal": 0})
    df["risk_score"] = (df["operating_hours_factor"] + df["anomaly_penalty"]).clip(0, 100).round(1)

    # Alert level
    def _alert(score: float) -> str:
        if score >= 70:
            return "high"
        elif score >= 30:
            return "medium"
        return "low"

    df["alert_level"] = df["risk_score"].apply(_alert)
    return df


# ══════════════════════════════════════════════════════════════
#  5. QUERY HELPERS (for data_store)
# ══════════════════════════════════════════════════════════════

def get_anomalies_for_unit(raw_df: pd.DataFrame, unit_id: str) -> list[dict]:
    """
    Return all shift-level data for a specific unit including anomaly flags.

    Uses IsolationForest on shift-level data to mark individual anomalies.
    """
    unit_data = raw_df[raw_df["unit_id"] == unit_id].copy()
    if unit_data.empty:
        return []

    # Fit IsolationForest on this unit's shift data
    features = ["idle_ratio", "fuel_consumption"]
    X = unit_data[features].values
    model = IsolationForest(contamination=0.1, random_state=42)
    unit_data["anomaly_score"] = model.fit_predict(X)
    unit_data["anomaly_label"] = unit_data["anomaly_score"].map({-1: "anomaly", 1: "normal"})

    return unit_data.to_dict(orient="records")


def get_alerts_from_summary(summary_df: pd.DataFrame) -> list[dict]:
    """
    Generate alert objects from the summary DataFrame.

    Returns list of dicts with keys:
        unit_id, alert_level, risk_score, message, recommendation
    """
    alerts = []
    for _, row in summary_df.iterrows():
        if row["alert_level"] == "low":
            continue  # no alert for low risk

        unit_id = row["unit_id"]
        level = row["alert_level"]
        score = row["risk_score"]
        is_anomaly = row["anomaly_label"] == "anomaly"

        if level == "high":
            message = f"Unit {unit_id} memerlukan maintenance segera"
            recommendation = "Segera lakukan inspeksi menyeluruh dan jadwalkan overhaul"
        else:
            message = f"Unit {unit_id} menunjukkan tanda-tanda risiko menengah"
            recommendation = "Tingkatkan frekuensi monitoring dan lakukan pengecekan rutin"

        if is_anomaly:
            message += " (pola operasi tidak normal terdeteksi)"
            recommendation += " — periksa pola idle time dan konsumsi BBM"

        alerts.append({
            "unit_id": unit_id,
            "alert_level": level,
            "risk_score": score,
            "message": message,
            "recommendation": recommendation,
        })

    return alerts

"""
KidecoIQ — API Integration Tests: Reklamasi Module
===================================================
Validasi endpoint modul reklamasi:
1. Status code 200 untuk semua endpoint.
2. Struktur JSON response sesuai kontrak SPEC.md §5 via Pydantic schemas.
3. HTTP 404 untuk zone_id yang tidak dikenal.
4. Validasi isi data (tipe, range, konsistensi).
"""

import os
import sys
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

# ── Ensure backend is importable ──────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app
from app.modules.reklamasi.schemas import (
    ZoneResponse,
    ZoneHistoryResponse,
    ReportResponse,
    HistoryPoint,
)


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient — hidup selama satu sesi test."""
    with TestClient(app) as c:
        yield c


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 1: GET /reklamasi/zones
# ══════════════════════════════════════════════════════════════

class TestGetZones:
    """Validasi endpoint GET /reklamasi/zones."""

    def test_status_200(self, client):
        """Endpoint harus merespons 200 OK."""
        resp = client.get("/reklamasi/zones")
        assert resp.status_code == 200

    def test_returns_list(self, client):
        """Response harus berupa list."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        assert isinstance(data, list)

    def test_has_zones(self, client):
        """List tidak boleh kosong (minimal 4 zone)."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        assert len(data) >= 4, f"Expected >=4 zones, got {len(data)}"

    def test_each_zone_validates_schema(self, client):
        """Setiap item zone harus valid terhadap ZoneResponse."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        for z in data:
            # This will raise if validation fails
            zone = ZoneResponse(**z)
            assert zone.status in ("air", "lahan_kosong", "vegetasi_stres", "vegetasi_sehat")

    def test_zone_has_all_required_fields(self, client):
        """Setiap zone harus punya semua field yang dibutuhkan."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        required_fields = {"id", "name", "status", "ndvi_latest", "area_ha",
                           "vegetation_cover_pct", "trend_prediction",
                           "updated_at",
                           "southwest_lat", "southwest_lng",
                           "northeast_lat", "northeast_lng"}
        for z in data:
            assert required_fields.issubset(z.keys()), (
                f"Missing fields: {required_fields - z.keys()}"
            )

    def test_ndvi_range(self, client):
        """ndvi_latest harus dalam [-1, 1]."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        for z in data:
            assert -1.0 <= z["ndvi_latest"] <= 1.0, (
                f"Zone {z['id']}: ndvi_latest={z['ndvi_latest']} out of range"
            )

    def test_vegetation_cover_range(self, client):
        """vegetation_cover_pct harus dalam [0, 100]."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        for z in data:
            assert 0.0 <= z["vegetation_cover_pct"] <= 100.0

    def test_area_positive(self, client):
        """area_ha harus >= 0."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        for z in data:
            assert z["area_ha"] >= 0

    def test_updated_at_is_iso_datetime(self, client):
        """updated_at harus string datetime ISO yang valid."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        for z in data:
            dt = datetime.fromisoformat(z["updated_at"])
            assert dt.tzinfo is not None  # must be timezone-aware

    def test_all_four_statuses_appear(self, client):
        """Semua 4 status klasifikasi harus muncul di zona yang ada."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        statuses = {z["status"] for z in data}
        expected = {"air", "lahan_kosong", "vegetasi_stres", "vegetasi_sehat"}
        assert statuses == expected, f"Missing statuses: {expected - statuses}"

    def test_trend_prediction_valid_values(self, client):
        """trend_prediction harus salah satu dari: meningkat, menurun, stabil."""
        resp = client.get("/reklamasi/zones")
        data = resp.json()
        valid_trends = {"meningkat", "menurun", "stabil"}
        for z in data:
            assert z["trend_prediction"] in valid_trends, (
                f"Zone {z['id']}: trend_prediction='{z['trend_prediction']}' "
                f"not in {valid_trends}"
            )


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 2: GET /reklamasi/zones/{id}/history
# ══════════════════════════════════════════════════════════════

class TestGetZoneHistory:
    """Validasi endpoint GET /reklamasi/zones/{id}/history."""

    def _get_first_zone_id(self, client) -> str:
        """Helper: ambil ID zona pertama."""
        resp = client.get("/reklamasi/zones")
        return resp.json()[0]["id"]

    def test_status_200(self, client):
        """Endpoint dengan zone_id valid harus 200."""
        zone_id = self._get_first_zone_id(client)
        resp = client.get(f"/reklamasi/zones/{zone_id}/history")
        assert resp.status_code == 200

    def test_status_404_unknown_zone(self, client):
        """Endpoint dengan zone_id tidak dikenal harus 404."""
        resp = client.get("/reklamasi/zones/nonexistent-id-12345/history")
        assert resp.status_code == 404

    def test_validates_schema(self, client):
        """Response harus valid terhadap ZoneHistoryResponse."""
        zone_id = self._get_first_zone_id(client)
        resp = client.get(f"/reklamasi/zones/{zone_id}/history")
        data = resp.json()
        history = ZoneHistoryResponse(**data)
        assert history.zone_id == zone_id

    def test_has_required_fields(self, client):
        """Response harus punya zone_id, zone_name, history."""
        zone_id = self._get_first_zone_id(client)
        resp = client.get(f"/reklamasi/zones/{zone_id}/history")
        data = resp.json()
        assert "zone_id" in data
        assert "zone_name" in data
        assert "history" in data

    def test_zone_name_matches(self, client):
        """zone_name di history harus cocok dengan name di zones."""
        zone_id = self._get_first_zone_id(client)
        resp_zones = client.get("/reklamasi/zones")
        zone_name = next(z["name"] for z in resp_zones.json() if z["id"] == zone_id)

        resp = client.get(f"/reklamasi/zones/{zone_id}/history")
        data = resp.json()
        assert data["zone_name"] == zone_name

    def test_history_has_at_least_2_points(self, client):
        """History minimal 2 titik waktu (dengan data sintetis, bisa 3)."""
        zone_id = self._get_first_zone_id(client)
        resp = client.get(f"/reklamasi/zones/{zone_id}/history")
        data = resp.json()
        assert len(data["history"]) >= 2

    def test_each_history_point_validates(self, client):
        """Setiap history point harus valid terhadap HistoryPoint."""
        zone_id = self._get_first_zone_id(client)
        resp = client.get(f"/reklamasi/zones/{zone_id}/history")
        data = resp.json()
        for hp in data["history"]:
            point = HistoryPoint(**hp)
            assert -1.0 <= point.ndvi_mean <= 1.0
            assert 0.0 <= point.vegetation_cover_pct <= 100.0
            assert point.classification in (
                "air", "lahan_kosong", "vegetasi_stres", "vegetasi_sehat"
            )

    def test_history_chronological_order(self, client):
        """History harus terurut ascending oleh image_date."""
        zone_id = self._get_first_zone_id(client)
        resp = client.get(f"/reklamasi/zones/{zone_id}/history")
        data = resp.json()
        dates = [datetime.strptime(hp["image_date"], "%Y-%m-%d") for hp in data["history"]]
        # Check non-decreasing (allow equal)
        for i in range(1, len(dates)):
            assert dates[i] >= dates[i-1], (
                f"History not chronological: {dates[i-1]} > {dates[i]}"
            )

    def test_image_date_is_valid_date(self, client):
        """image_date harus string tanggal yang valid."""
        zone_id = self._get_first_zone_id(client)
        resp = client.get(f"/reklamasi/zones/{zone_id}/history")
        data = resp.json()
        for hp in data["history"]:
            parsed = date.fromisoformat(hp["image_date"])
            assert isinstance(parsed, date)


# ══════════════════════════════════════════════════════════════
#  TEST GROUP 3: GET /reklamasi/report
# ══════════════════════════════════════════════════════════════

class TestGetReport:
    """Validasi endpoint GET /reklamasi/report."""

    def test_status_200(self, client):
        """Endpoint harus merespons 200 OK."""
        resp = client.get("/reklamasi/report")
        assert resp.status_code == 200

    def test_validates_schema(self, client):
        """Response harus valid terhadap ReportResponse."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        report = ReportResponse(**data)
        assert report.total_zones >= 4

    def test_has_required_fields(self, client):
        """Response harus punya semua field wajib."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        required = {"generated_at", "total_zones", "status_summary",
                     "overall_ndvi_mean", "overall_vegetation_cover_pct",
                     "compliance_score", "zones"}
        assert required.issubset(data.keys())

    def test_total_zones_matches(self, client):
        """total_zones harus sama dengan panjang list zones."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        assert data["total_zones"] == len(data["zones"])

    def test_status_summary_counts(self, client):
        """Jumlah status di status_summary harus sama dengan total_zones."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        total_from_summary = sum(data["status_summary"].values())
        assert total_from_summary == data["total_zones"], (
            f"Summary total {total_from_summary} != {data['total_zones']}"
        )

    def test_status_summary_all_keys(self, client):
        """status_summary harus punya keempat key."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        expected_keys = {"vegetasi_sehat", "vegetasi_stres", "lahan_kosong", "air"}
        assert set(data["status_summary"].keys()) == expected_keys

    def test_overall_ndvi_mean_in_range(self, client):
        """overall_ndvi_mean harus dalam [-1, 1]."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        assert -1.0 <= data["overall_ndvi_mean"] <= 1.0

    def test_overall_vegetation_cover_in_range(self, client):
        """overall_vegetation_cover_pct harus dalam [0, 100]."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        assert 0.0 <= data["overall_vegetation_cover_pct"] <= 100.0

    def test_compliance_score_in_range(self, client):
        """compliance_score harus dalam [0, 100]."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        assert 0.0 <= data["compliance_score"] <= 100.0

    def test_each_zone_report_item(self, client):
        """Setiap item di list zones harus punya field lengkap."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        for z in data["zones"]:
            assert "zone_id" in z
            assert "name" in z
            assert "status" in z
            assert "ndvi_mean" in z
            assert "area_ha" in z
            assert "risk_flag" in z
            assert z["status"] in ("air", "lahan_kosong", "vegetasi_stres", "vegetasi_sehat")
            assert isinstance(z["risk_flag"], bool)

    def test_risk_flag_consistent_with_status(self, client):
        """Zona dengan status air/lahan_kosong harus risk_flag=True."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        for z in data["zones"]:
            if z["status"] in ("air", "lahan_kosong"):
                assert z["risk_flag"] is True, (
                    f"Zone {z['name']} status={z['status']} should have risk_flag=True"
                )

    def test_generated_at_is_datetime(self, client):
        """generated_at harus string datetime ISO yang valid."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        dt = datetime.fromisoformat(data["generated_at"])
        assert dt.tzinfo is not None

    def test_compliance_score_reasonable(self, client):
        """Dengan campuran 4 kategori, score harus antara 10-100."""
        resp = client.get("/reklamasi/report")
        data = resp.json()
        # With 4 zones: best=400, worst=40 → score range 10-100
        assert 10.0 <= data["compliance_score"] <= 100.0

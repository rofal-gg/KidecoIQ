# KidecoIQ — AI-Driven Operational Excellence

Platform AI untuk monitoring reklamasi lahan pascatambang dan efisiensi fleet alat berat.
Proyek ini dibuat untuk Hackathon KIC 2026 (PT Kideco Jaya Agung x ITK).

## Struktur Proyek

```
kideco-iq/
├── backend/          # FastAPI + PostgreSQL + PostGIS + ML (scikit-learn)
├── frontend/         # Next.js + TypeScript + Tailwind CSS + Leaflet
├── data/             # Sample data (raster sintetis, CSV fleet dummy)
├── docker-compose.yml
└── README.md
```

## Cara Jalankan dengan Docker (untuk juri/panitia)

**Prasyarat:** Docker Engine 24+ dan Docker Compose v2 terinstall.

```bash
# 1. Clone repositori
git clone https://github.com/rofal-gg/KidecoIQ.git kideco-iq
cd kideco-iq

# 2. Build & jalankan semua service (pertama kali atau setelah perubahan)
docker compose up --build -d

# 3. Buka browser: http://localhost:3000
#
#    Dashboard langsung bisa dipakai — data otomatis terisi:
#    - Modul Reklamasi: 5 zona reklamasi dengan NDVI + status
#    - Modul Operasional: 10 unit fleet + deteksi anomali + alert
#
#    Akses langsung API:
#    - Health check: http://localhost:8000/health
#    - Reklamasi API: http://localhost:8000/reklamasi/zones
#    - Operasional API: http://localhost:8000/operasional/fleet
```

**Perintah penting lainnya:**

| Perintah | Fungsi |
|---|---|
| `docker compose up` | Jalankan (tanpa rebuild) |
| `docker compose down` | Hentikan semua container |
| `docker compose down -v` | Hentikan + hapus database (reset penuh) |
| `docker compose logs -f backend` | Lihat log backend |
| `docker compose logs -f frontend` | Lihat log frontend |

### Akses langsung ke service

| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API (health check) | http://localhost:8000/health |
| API Reklamasi | http://localhost:8000/reklamasi/zones |
| API Operasional | http://localhost:8000/operasional/fleet |

## Cara Jalankan untuk Development (tanpa Docker)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Pastikan PostgreSQL 16 + PostGIS running di localhost:5432
# Buat database: createdb kidecoiq
# Sesuaikan .env jika perlu

./migrate.sh up
uvicorn app.main:app --reload
# → http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Test

```bash
cd backend
python -m pytest
# → 94 test passing
```

## Tech Stack

| Layer | Teknologi |
|---|---|
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 16 + PostGIS |
| ML Reklamasi | rasterio, numpy, scikit-learn (RandomForest) |
| ML Operasional | pandas, scikit-learn (IsolationForest) |
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Peta | Leaflet.js (react-leaflet) |
| Auth | JWT (stub) |
| Deployment | Docker Compose |

## Agent Kit

Repositori ini menggunakan **opencode agent kit** untuk pengembangan berbasis AI.
Lihat `TASKS.md` dan `PROGRESS.md` untuk detail pekerjaan yang sudah dan belum selesai.

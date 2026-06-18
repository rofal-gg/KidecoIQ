# SPEC.md — KidecoIQ
> **Wajib dibaca penuh oleh SETIAP agent di SETIAP sesi sebelum mengerjakan apapun.**
> File ini adalah satu-satunya sumber kebenaran arsitektur. Jangan ambil keputusan desain baru tanpa menuliskannya di sini dulu (lihat bagian "Decision Log").

## 1. Konteks Proyek
KidecoIQ adalah platform AI untuk submisi Hackathon KIC 2026 (PT Kideco Jaya Agung x ITK), kategori Hackathon, tema besar "AI-Driven Operational Excellence". Platform ini menggabungkan dua modul dalam satu produk:

- **Modul Reklamasi** — memantau & memprediksi progres reklamasi lahan pascatambang menggunakan citra satelit (NDVI) dan AI, menggantikan survei terestrial manual.
- **Modul Operasional** — memantau efisiensi fleet alat berat (idle time, anomali) dan memberi peringatan dini predictive maintenance, menggunakan data telematik (atau data simulasi untuk demo).

Kedua modul berbagi satu backend, satu database, dan satu dashboard shell — bukan dua aplikasi terpisah yang ditempel.

## 2. Prinsip Desain (Non-Negotiable)
1. **Software-only.** Tidak ada sensor IoT atau hardware baru di MVP ini. Semua input data berasal dari: (a) citra satelit publik gratis (Sentinel-2/Landsat), (b) data telematik yang dianggap sudah ada di alat berat (disimulasikan untuk demo), (c) data GIS perizinan yang sudah dimiliki perusahaan.
2. **Modular, bukan monolitik membingungkan.** Modul Reklamasi dan Operasional adalah dua folder terpisah di bawah satu backend (`backend/app/modules/<nama>`), dengan pola yang konsisten satu sama lain: `ingest -> preprocess -> model -> api -> dashboard`.
3. **MVP realistis untuk waktu terbatas.** Jangan training deep learning dari nol tanpa dataset berlabel. Default: NDVI + threshold/Random Forest untuk klasifikasi vegetasi; Isolation Forest/statistik sederhana untuk anomali fleet. Model yang lebih canggih (U-Net, LSTM) adalah "nice to have" di fase lanjutan, BUKAN blocker MVP.
4. **Setiap agent WAJIB update `PROGRESS.md`** di akhir tugasnya sebelum sesi berakhir. Tidak ada pengecualian.

## 3. Tech Stack (Final — jangan diganti tanpa update Decision Log di bawah)

| Layer | Pilihan |
|---|---|
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 16 + PostGIS |
| AI/ML — Reklamasi | rasterio, numpy, scikit-learn (RandomForestClassifier) |
| AI/ML — Operasional | pandas, scikit-learn (IsolationForest), prophet (opsional, fase lanjutan) |
| Frontend | Next.js (React) + TypeScript + Tailwind CSS |
| Peta interaktif | Leaflet.js |
| Auth | JWT sederhana (fastapi-jwt-auth atau implementasi manual) |
| Deployment demo | Docker Compose |

## 4. Struktur Folder (sudah di-scaffold, JANGAN diubah strukturnya tanpa alasan kuat)
```
kideco-iq/
├── SPEC.md, PROGRESS.md, TASKS.md   <- baca semua sebelum mulai
├── .opencode/agent/*.md              <- definisi agent
├── backend/
│   ├── app/
│   │   ├── modules/
│   │   │   ├── reklamasi/            <- milik agent backend-reklamasi
│   │   │   └── operasional/          <- milik agent backend-operasional
│   │   ├── core/                     <- shared: db, auth, config — HANYA lead/devops yang edit
│   │   └── main.py
│   ├── ml_models/
│   └── requirements.txt
├── frontend/                          <- milik agent frontend
├── data/
│   ├── satellite_samples/
│   └── fleet_dummy/
└── docker-compose.yml                 <- milik agent devops
```

## 5. Modul Reklamasi — Spesifikasi Fungsional
- **Input:** citra Sentinel-2 (band B4/Red, B8/NIR untuk NDVI) area konsesi Kideco (Roto Samurangau sebagai area pilot), format GeoTIFF; poligon batas area reklamasi (GeoJSON).
- **Pipeline:** hitung NDVI per piksel -> klasifikasi 4 kelas (vegetasi sehat / stres / lahan kosong / air) via threshold NDVI atau RandomForest jika ada label training -> agregasi per poligon -> simpan ke PostGIS -> hitung tren time-series antar tanggal citra untuk skor risiko gagal tumbuh.
- **Output API:** `GET /reklamasi/zones` (daftar poligon + status terbaru), `GET /reklamasi/zones/{id}/history` (tren NDVI), `GET /reklamasi/report` (laporan kepatuhan siap unduh).
- **Endpoint tidak boleh diubah namanya** tanpa update bagian ini dan memberi tahu agent frontend.

## 6. Modul Operasional — Spesifikasi Fungsional
- **Input:** data simulasi log alat berat (CSV: timestamp, unit_id, status [idle/active/maintenance], fuel_consumption) — buat generator data dummy yang realistis untuk demo, taruh di `data/fleet_dummy/`.
- **Pipeline:** hitung idle time ratio per unit per shift -> deteksi anomali (IsolationForest pada fitur idle_ratio, fuel_consumption) -> skor risiko maintenance sederhana berbasis jam operasi kumulatif.
- **Output API:** `GET /operasional/fleet` (status semua unit), `GET /operasional/fleet/{id}/anomaly`, `GET /operasional/alerts`.

## 7. Kontrak Frontend (agar backend & frontend tidak saling menunggu)
Frontend boleh mulai development dengan MOCK data yang strukturnya identik dengan kontrak API di atas, jangan menunggu backend selesai 100%. Taruh mock JSON di `frontend/mocks/`.

## 8. Out of Scope (JANGAN dikerjakan agent manapun kecuali diminta eksplisit di TASKS.md)
- Aplikasi mobile native
- Integrasi IoT/hardware sungguhan
- Autentikasi OAuth pihak ketiga
- Multi-tenant / multi-perusahaan

## 9. Decision Log
> Tambahkan entri baru di sini setiap kali ada keputusan arsitektur yang menyimpang dari spek awal di atas. Format: `[YYYY-MM-DD] [agent] keputusan — alasan`

- `[2026-06-18] [lead] Menggunakan `geoalchemy2` untuk kolom PostGIS `Geometry` di models — karena PostGIS adalah standar untuk data spasial dan dibutuhkan oleh modul Reklamasi untuk poligon zona. Wajib di requirements.
- `[2026-06-18] [lead] Database URL default: `postgresql://kideco:kideco@localhost:5432/kidecoiq` — konsisten dengan konfigurasi docker-compose.
- `[2026-06-18] [lead] Trigger `update_updated_at_column()` via plpgsql, bukan via SQLAlchemy `onupdate` — agar konsisten antara aplikasi dan akses DB langsung.
- `[2026-06-18] [backend-reklamasi] Threshold NDVI: air < 0.0, lahan_kosong [0.0, 0.25), vegetasi_stres [0.25, 0.45), vegetasi_sehat ≥ 0.45 — threshold ini adalah nilai konservatif dari literatur NDVI yang berlaku universal untuk MVP. Akan dikalibrasi ulang jika ada data lapangan.
- `[2026-06-18] [backend-reklamasi] Data layer MVP menggunakan in-memory store dengan bootstrap dari raster sintetis — percepat development tanpa ketergantungan PostgreSQL. Saat DB tersedia, cukup ganti body `data_store.py` tanpa ubah `router.py` atau `schemas.py`.
- `[2026-06-18] [backend-reklamasi] Compliance score: vegetasi_sehat=100pts, vegetasi_stres=50pts, lahan_kosong=10pts, air=25pts. Skor = (total/max)×100 — formula sederhana yang bisa diaudit dan dimodifikasi.
- `[2026-06-18] [backend-operasional] Anomali dideteksi pada level SHIFT (bukan agregat unit) — karena 2 shift anomali dari 60 akan hilang di rata-rata. IsolationForest pada level shift lebih sensitif.
- `[2026-06-18] [backend-operasional] `contamination=0.02` pada IsolationForest — hanya ~12 shift paling ekstrem (cukup untuk 6 shift injeksi). Hyperparameter yang harus dikalibrasi dengan data asli.
- `[2026-06-18] [backend-operasional] Risk score = operating_hours_factor (0-50) + anomaly_penalty (40 jika anomaly, 0 normal) — formula sederhana, dapat dikembangkan dengan bobot lebih kompleks di produksi.
- `[2026-06-18] [frontend] Menggunakan react-leaflet v5 — kompatibel dengan React 19 yang dibundel Next.js 15.
- `[2026-06-18] [frontend] Proxy rewrite di Next.js: `/api/*` → `http://localhost:8000/*` — menghilangkan kebutuhan CORS handling di development dan Docker.
- `[2026-06-18] [devops] Build context = root repo (bukan subfolder) — agar SPEC.md + data/ ikut tercopy untuk path detection `_get_project_root()`.
- `[2026-06-18] [devops] `output: "standalone"` di next.config.ts — production build yang ringan untuk Docker, tidak mengganggu dev mode.

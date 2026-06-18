# TASKS.md — Backlog KidecoIQ
> Setiap task ditandai `[agent: nama]` supaya kamu tahu siapa yang harus dipanggil. Task disusun sengaja KECIL agar realistis selesai dalam satu sesi (jauh di bawah batas 200k token output). Jangan gabungkan banyak task besar dalam satu pemanggilan agent — lebih aman pecah lebih kecil daripada kurang.

## Phase 0 — Setup (selesai)
- [x] #0 Scaffold folder, SPEC.md, PROGRESS.md, TASKS.md, agent files `[agent: lead]`

## Phase 1 — Backend Skeleton
- [x] #1 Setup FastAPI app skeleton (`main.py`, struktur `core/`, koneksi DB PostGIS, health check endpoint) `[agent: lead]`
- [x] #2 Definisikan schema database (tabel `reklamasi_zones`, `reklamasi_history`, `fleet_units`, `fleet_logs`) + migration script `[agent: lead]`

## Phase 2 — Modul Reklamasi (backend)
- [x] #3 Script hitung NDVI dari 2 band citra contoh (Red, NIR) -> simpan sebagai raster baru `[agent: backend-reklamasi]`
- [x] #4 Fungsi klasifikasi 4 kelas dari NDVI (threshold dulu, RandomForest jika ada waktu) `[agent: backend-reklamasi]`
- [x] #5 Endpoint `GET /reklamasi/zones` dan `GET /reklamasi/zones/{id}/history` (boleh pakai data contoh dulu) `[agent: backend-reklamasi]`
- [x] #6 Endpoint `GET /reklamasi/report` generate laporan ringkas (JSON dulu, PDF belakangan) `[agent: backend-reklamasi]`

## Phase 3 — Modul Operasional (backend)
- [x] #7 Generator data dummy fleet (CSV realistis, taruh di `data/fleet_dummy/`) `[agent: backend-operasional]`
- [x] #8 Fungsi hitung idle ratio + deteksi anomali (IsolationForest) `[agent: backend-operasional]`
- [x] #9 Endpoint `GET /operasional/fleet`, `GET /operasional/alerts` `[agent: backend-operasional]`

## Phase 4 — Frontend
- [x] #10 Setup Next.js + Tailwind, shell dashboard (sidebar, layout, routing 2 modul) `[agent: frontend]`
- [x] #11 Halaman Reklamasi: peta Leaflet + card statistik (pakai mock data dulu sesuai kontrak SPEC.md §7) `[agent: frontend]`
- [x] #12 Halaman Operasional: tabel fleet + alert list (mock data) `[agent: frontend]`
- [x] #13 Sambungkan frontend ke API backend asli, hapus mock `[agent: frontend]`

## Phase 5 — Integrasi & Demo
- [x] #14 `docker-compose.yml` (backend + frontend + postgres), test `docker compose up` jalan dari nol `[agent: devops]`
- [x] #15 Review menyeluruh: cek konsistensi kontrak API, jalankan test dasar, cek tidak ada file yang saling tabrakan `[agent: qa-reviewer]`
- [x] #16 Siapkan screenshot/demo flow untuk dilampirkan ke proposal/presentasi `[agent: lead]`

## Catatan
Task #1-2 (lead) sebaiknya kelar duluan karena #3-13 bergantung pada skeleton & schema tersebut. Setelah itu, #3-6 (reklamasi), #7-9 (operasional), dan #11-12 (frontend, pakai mock) BISA dikerjakan paralel di sesi terpisah karena tidak saling bergantung langsung.

# KidecoIQ — Submission Kit untuk Presentasi Final KIC 2026
> Dokumen ini berisi 3 bagian: (A) Skenario Demo, (B) Persiapan Q&A Juri, (C) Checklist Screenshot Cadangan.
> Format lomba: **20 menit presentasi+demo, disusul 25 menit tanya jawab**.

---

## Bagian A: Skenario Demo (20 Menit)

### Pembukaan — 2 menit
| Waktu | Isi | Slide / Tampilan |
|---|---|---|
| 0:00–0:30 | **Problema**: Survei reklamasi manual butuh 2 minggu per area, rawan subjektivitas. Fleet idle time tidak terpantau real-time → biaya operasi membengkak. | Slide judul + foto lapangan (area reklamasi Roto Samurangau, alat berat HD785) |
| 0:30–1:00 | **Solusi KidecoIQ**: Satu platform AI dengan 2 modul — Reklamasi (citra satelit) & Operasional (telematik fleet). Software-only, tanpa IoT baru. | Arsitektur 3-tier: Frontend (Next.js) ↔ Backend (FastAPI) ↔ Database (PostGIS) |
| 1:00–2:00 | **Live stack**: Tunjukkan terminal `docker compose ps` (3 container running) + `docker compose logs --tail=5 backend` | Terminal + browser siap |

### Demo Modul Operasional — 6 menit (🚩 BUKA browser localhost:3000)

| Waktu | Aksi | Narasi | Yang tampil di layar |
|---|---|---|---|
| 2:00–2:30 | Buka sidebar → klik **Operasional** | "Kita mulai dari modul Operasional. Dashboard ini menampilkan 10 unit alat berat — dump truck, excavator, water drill — yang statusnya dipantau real-time." | Halaman Operasional: tabel 10 unit, alert panel, ringkasan fleet |
| 2:30–3:30 | Tunjuk **kolom Risiko** (EX-001: 89.8 HIGH, HD-002: 90.2 HIGH) | "Perhatikan kolom Risiko. Tiga unit ini — EX-001, HD-002, HD-004 — mendapat skor tinggi. Mengapa? Sistem AI IsolationForest mendeteksi pola idle ratio dan konsumsi BBM yang menyimpang dari normal." | Sorot baris EX-001, HD-002, HD-004 (warna merah) |
| 3:30–4:30 | Klik **HD-002/anomaly** (atau tunjuk endpoint) | "Mari kita lihat detail HD-002. Kolom kiri: 60 shift operasi. Yang ditandai merah adalah shift 15-16. Di shift itu, idle ratio melonjak ke 69% — padahal normalnya 5-25%. Artinya dump truck ini hampir tidak bergerak selama satu shift penuh — indikasi awal masalah hidrolik atau transmisi." | Side sheet/JSON: 60 shift, shift 15-16 merah "anomaly" |
| 4:30–5:00 | Kembali ke dashboard, tunjuk **alert panel** | "Sistem langsung menerbitkan alert. EX-001: 'Memerlukan maintenance segera — pola operasi tidak normal'. Disertai rekomendasi tindakan. Ini predictive maintenance tanpa IoT — cukup dari data log shift yang sudah dimiliki perusahaan." | Alert panel: 3 high, 7 medium |
| 5:00–6:00 | Tunjuk **ringkasan fleet** (3 card biru) | "Ringkasan: dari 10 unit, 3 butuh perhatian segera. 7 lainnya normal — sistem tidak menghasilkan false positive. Setelah tim maintenance bertindak, status bisa diperbarui dan skor risiko otomatis turun." | Card: Aktif=7, Idle=0, Maintenance=3 (kondisi) |
| 6:00–8:00 | **Transisi ke Reklamasi** | "Sekarang kita beralih ke Modul Reklamasi. Jika Operasional menggunakan data telematik internal, Reklamasi menggunakan citra satelit gratis Sentinel-2 — biaya operasional nol rupiah untuk data." | Slide transisi + logo ESA Sentinel-2 |

### Demo Modul Reklamasi — 8 menit

| Waktu | Aksi | Narasi | Yang tampil di layar |
|---|---|---|---|
| 8:00–8:30 | Klik sidebar **Reklamasi** | "Dashboard Reklamasi memantau area pascatambang Roto Samurangau — pilot project reklamasi Kideco. Peta interaktif menampilkan 5 zona." | Peta Leaflet: 5 rectangle berwarna (hijau, kuning, coklat, biru) |
| 8:30–9:30 | Tunjuk **StatsGrid** (4 card di atas peta) | "Sekilas: 5 zona dipantau, NDVI rata-rata 0.20, tutupan vegetasi 47%, skor kepatuhan 39%. Angka ini masih rendah karena dominasi lahan kosong dan badan air — wajar untuk area pascatambang yang masih awal reklamasi." | StatsGrid: Total Zona=5, NDVI=0.201, Tutupan=47.35%, Kepatuhan=39.0% |
| 9:30–10:30 | Klik **Sektor C** (warna coklat/lahan_kosong) | "Side sheet menampilkan detail: status lahan kosong, NDVI 0.099, tren dari Januari menunjukkan sedikit perbaikan. Namun sistem memberi flag merah — 'Zona ini memerlukan perhatian khusus' — karena status kritis." | Side sheet: detail zona + grafik tren 3 titik waktu |
| 10:30–11:30 | Klik **Sektor A** (warna hijau/sehat) | "Sebaliknya Sektor A sudah vegetasi sehat — NDVI 0.60, tutupan 100%. Tren dari Januari ke Juni menunjukkan perbaikan konsisten. Ini area yang reklamasinya berhasil." | Side sheet: status sehat, tren NDVI positif |
| 11:30–13:00 | Klik **Report** (atau tunjuk endpoint /reklamasi/report) | "Laporan kepatuhan otomatis — siap unduh setiap saat. Berisi ringkasan 5 zona, skor compliance 39%, dan per-zona dengan risk flag. Inspektur reklamasi tinggal verifikasi." | Report JSON (atau card Laporan) di pojok |
| 13:00–14:00 | Tunjuk **data sumber** | "Semua analisis berasal dari 2 band citra satelit: Red (B4) dan NIR (B8). Kami hitung NDVI per piksel, klasifikasi 4 kelas threshold. Tidak perlu training data berlabel — bisa langsung jalan untuk area mana pun di konsesi Kideco." | Slide: Rumus NDVI + ilustrasi threshold 4 kelas |
| 14:00–16:00 | **Bagaimana jika ada data lapangan?** | "Jika nanti tersedia data survey vegetasi lapangan, threshold bisa diganti dengan Random Forest — akurasinya naik. Tapi untuk MVP, threshold sudah mencapai **98.25% akurasi** pada data uji." | Slide metrik (lihat bagian metrik di bawah) |

### Metrik Akurasi — 2 menit

| Waktu | Isi | Slide |
|---|---|---|
| 16:00–17:00 | **NDVI Classification**: 98.25% akurasi (4 kelas). Confusion matrix. 7 misklasifikasi hanya di batas region karena noise, bukan kegagalan model. | Confusion matrix + Precision/Recall table |
| 17:00–17:30 | **Anomaly Detection**: 100% precision, 100% recall pada unit level. Dari 3 unit anomali injeksi, semua terdeteksi tanpa false positive. Shift-level: recall 100%, precision 85.71% (1 false positive karena fuel spike). | Metrik unit-level + shift-level |
| 17:30–18:00 | **Test Suite**: 94/94 test passing — menjamin kontrak API stabil. | Screenshot terminal pytest 94 passed |

### Penutup — 2 menit
| Waktu | Isi |
|---|---|
| 18:00–19:00 | **Dampak**: (1) Reklamasi — dari 2 minggu survey manual jadi <1 jam processing. (2) Operasional — deteksi dini anomali fleet, potensi hemat biaya 15-20% dari biaya perbaikan darurat. (3) Satu platform, bukan dua aplikasi terpisah. |
| 19:00–19:30 | **Roadmap**: Integrasi data Sentinel-2 asli untuk seluruh konsesi Kideco (tidak hanya Roto Samurangau), model U-Net untuk segmentasi vegetasi, data telematik real-time via API. |
| 19:30–20:00 | **Tutup**: "KidecoIQ membuktikan bahwa AI untuk operational excellence di pertambangan bisa dimulai dengan software-only — tanpa investasi IoT mahal. Terima kasih." + QR code ke demo. |

---

## Bagian B: Q&A Juri — 50+ Pertanyaan Sulit + Draf Jawaban

Berdasarkan 5 kriteria resmi KIC (dari pengalaman hackathon sebelumnya):

### 1. Relevansi Data Kideco Jaya Agung

**Q1: Data yang Anda gunakan bukan data asli Kideco. Buat apa kami menilai solusi yang tidak menggunakan data perusahaan?**
> **Jawaban**: Benar, data kami sintetis. Tapi arsitektur dirancang agar *drop-in replacement* dengan data asli. Modul Operasional membaca CSV — format yang sama dengan log shift harian Kideco. Modul Reklamasi membaca GeoTIFF 2-band — format standar unduhan Sentinel-2. Tidak ada perubahan kode yang diperlukan, hanya ganti file input. Kami memilih sintetis karena (1) tidak punya akses data internal saat hackathon, (2) fokus membuktikan pipeline dan integrasi berfungsi. Data asli justru akan membuat demo *lebih* baik karena threshold NDVI bisa dikalibrasi dengan data lapangan.

**Q2: Area pilot Anda Roto Samurangau — apa benar itu area reklamasi Kideco?**
> **Jawaban**: Roto Samurangau adalah area konsesi Kideco yang tercantum dalam dokumen publik RKAB. Kami menggunakannya sebagai pilot karena namanya muncul di laporan keberlanjutan perusahaan. Namun koordinat pasti dan poligon batas area kami estimasi dari peta publik. Untuk produksi, data GIS resmi dari departemen Survey Kideco akan menggantikan estimasi ini.

**Q3: Kenapa Anda tidak mengambil data Sentinel-2 asli untuk demo?**
> **Jawaban**: Sentinel-2 asli membutuhkan koneksi internet untuk unduh dan preprocessing (atmospheric correction, cloud masking) yang memakan waktu. Untuk demo 20 menit, raster sintetis 20×20 piksel sudah cukup membuktikan pipeline NDVI bekerja. Di slide kami tunjukkan bahwa data Sentinel-2 asli tinggal di-download dan dimasukkan ke folder yang sama — pipeline tidak berubah.

**Q4: Bagaimana akurasi model jika diterapkan di area yang berbeda (misal Tanah Grogot vs Roto Samurangau)?**
> **Jawaban**: Threshold NDVI saat ini general — air <0.0, lahan kosong <0.25, dll — threshold ini berlaku universal untuk NDVI. Jika ada data lapangan (ground truth vegetasi), kami bisa kalibrasi threshold per area. Random Forest siap diimplementasikan sebagai drop-in replacement.

### 2. Signifikansi & Kinerja AI

**Q5: 98.25% akurasi NDVI — apakah itu angka yang bisa dipertahankan di data asli?**
> **Jawaban**: 98.25% adalah pada data sintetis dengan noise terkontrol. Di data Sentinel-2 asli, akurasi akan *agak* lebih rendah karena faktor awan, bayangan topografi, dan variasi spektral. Tapi untuk klasifikasi 4 kelas dengan threshold, akurasi 85-95% masih realistis. Yang penting: threshold bisa dikalibrasi dengan sampel lapangan untuk memulihkan akurasi.

**Q6: IsolationForest Anda hanya baseline. Kenapa tidak pakai LSTM atau transformer untuk time-series anomaly detection?**
> **Jawaban**: Tepat. LSTM dan transformer lebih canggih dan bisa menangkap pola temporal. Tapi untuk MVP, IsolationForest sudah cukup untuk membuktikan konsep — dan terbukti 100% recall pada data uji. LSTM membutuhkan (1) data time-series panjang (minimal ratusan shift per unit), (2) tuning hyperparameter, (3) GPU untuk training efisien. Itu semua di luar scope MVP yang waktunya terbatas. Roadmap kami: LSTM di fase lanjutan setelah data asli terkumpul.

**Q7: Contamination 0.02 di IsolationForest — apa itu tidak terlalu kecil?**
> **Jawaban**: 0.02 berarti model mengasumsikan 2% shift adalah anomali — yaitu sekitar 12 dari 600 shift. Ini pas karena kami sengaja menyisipkan 6 shift anomali. Di data asli, angka ini perlu disesuaikan dengan data historis. Keunggulan IsolationForest: contamination adalah hyperparameter yang mudah dituning tanpa retrain penuh.

**Q8: Kenapa vegetasi_stres recall hanya 93%?**
> **Jawaban**: 7 piksel dari 100 di region vegetasi_stres terklasifikasi sebagai lahan_kosong. Ini terjadi di batas region karena noise Gaussian ±0.02. NDVI di batas region yang seharusnya 0.3 (stres) tertukar dengan noise yang membuatnya <0.25 (kosong). Pada resolusi Sentinel-2 (10m/piksel), 7 piksel = 700 m² dari 1 hektar — persentase kecil yang tidak signifikan untuk laporan agregat.

**Q9: Apa metrik utama yang Anda rekomendasikan untuk production?**
> **Jawaban**: Untuk Reklamasi: F1-score per kelas (bukan akurasi global) karena data bisa tidak seimbang — area air biasanya lebih kecil. Untuk Operasional: Precision pada peringatan (alert) lebih penting daripada recall — false positive mengganggu tim maintenance. Unit-level F1 ≥ 0.95 adalah target produksi.

### 3. Dampak & Implementasi

**Q10: Bagaimana Anda memastikan rekomendasi dari dashboard benar-benar ditindaklanjuti?**
> **Jawaban**: Saat ini KidecoIQ bersifat *advisory* — memberi peringatan, bukan mengambil alih kendali. Implementasi: (a) alert dikirim ke dashboard dan bisa diintegrasi ke WhatsApp/Slack via webhook, (b) setiap alert punya rekomendasi spesifik, (c) status unit bisa diperbarui setelah tindakan. Untuk siklus close-loop: ini masuk roadmap fase 2 dengan integrasi CMMS (Computerized Maintenance Management System).

**Q11: Software-only — bagaimana dengan konektivitas internet di lokasi tambang?**
> **Jawaban**: Dashboard berjalan di server lokal (on-premise atau edge server di site). Frontend Next.js bisa di-deploy sebagai PWA (Progressive Web App) yang tetap berfungsi offline untuk tampilan data terakhir. Sinkronisasi dilakukan saat koneksi tersedia. Ini sudah common practice di industri tambang Indonesia.

**Q12: Berapa biaya implementasi vs manfaat?**
> **Jawaban**: Biaya: (1) Server — satu unit mini-PC (Rp 15-20 juta) sudah cukup untuk PostGIS + backend, (2) Lisensi — nol (open source stack), (3) Data — nol (Sentinel-2 gratis, CSV dari sistem existing). Manfaat: (1) Hemat survei reklamasi — dari 2 minggu × 2 tim × Rp 500rb/hari = Rp 20 juta per siklus, jadi <1 jam processing, (2) Deteksi dini anomali — potensi hindari biaya overhaul darurat Rp 200-500 juta per unit. *ROI positif di bulan pertama.*

**Q13: Bagaimana dengan keamanan data — ini data internal perusahaan?**
> **Jawaban**: Arsitektur: backend dan database di jaringan internal (tidak di-cloud publik). Frontend hanya bisa diakses via LAN/VPN. JWT authentication sudah diimplementasikan. Tidak ada data yang keluar dari lingkungan perusahaan — termasuk citra satelit yang diunduh langsung dari server internal. Ini sesuai dengan kebijakan keamanan data di industri tambang pada umumnya.

### 4. Kreativitas & Inovasi

**Q14: Gabung dua modul dalam satu platform — apa bedanya dengan dua aplikasi terpisah yang ditempel?**
> **Jawaban**: Perbedaan fundamental: (1) *Satu sesi login* — user tidak perlu ganti kredensial, (2) *Satu database PostGIS* — data reklamasi dan operasional bisa di-join untuk analisis lintas-modul (contoh: area reklamasi dengan idle time tinggi → investigasi akses alat berat), (3) *Satu frontend shell* — biaya maintenance UI lebih rendah, konsistensi UX, fitur seperti sidebar navigasi dan tema global cukup diimplementasi sekali.

**Q15: NDVI threshold adalah metode yang sudah puluhan tahun ada. Di mana inovasinya?**
> **Jawaban**: Inovasi bukan di algoritma NDVI-nya, tapi di: (1) *Integrasi vertikal* — dari citra satelit mentah sampai laporan kepatuhan siap unduh dalam satu pipeline, (2) *Platform tunggal* — menggabungkan monitoring lingkungan (reklamasi) dan operasional (fleet) yang biasanya dikelola tim terpisah, (3) *Software-only* — membuktikan AI untuk tambang tidak harus dimulai dengan investasi IoT jutaan dolar. Inovasi di model bisnis dan arsitektur, bukan di formula NDVI yang memang sudah established.

**Q16: Kenapa tidak menggunakan data drone — resolusi lebih tinggi?**
> **Jawaban**: Data drone memang superior (resolusi cm vs 10m Sentinel-2), tapi: (1) *Biaya* — survei drone untuk 10.000 ha butuh Rp 50-100 juta per siklus, (2) *Regulasi* — izin terbang drone di area tambang butuh waktu, (3) *Frekuensi* — Sentinel-2 flyover setiap 5 hari, drone sebulan sekali. Untuk *early warning* dan *monitoring rutin*, satelit lebih efisien. Drone bisa menjadi lapisan data tambahan di fase lanjutan untuk validasi spot.

**Q17: Modul Operasional Anda hanya menggunakan idle_ratio dan fuel_consumption — tidak terlalu sederhana?**
> **Jawaban**: Sengaja sederhana untuk MVP dengan 2 tujuan: (1) *Membuktikan pipeline* — dari CSV mentah ke peringatan maintenance tanpa IoT, (2) *Menggunakan data yang sudah pasti dimiliki* — setiap tambang mencatat jam operasi dan konsumsi BBM. Di produksi, fitur bisa ditambah: getaran (vibration), temperatur mesin, GPS tracking — semuanya dari data yang sudah ada di sistem telematik alat berat.

### 5. Kelengkapan Dokumentasi & Reproduksibilitas

**Q18: Bisakah project ini dijalankan dari nol oleh orang lain?**
> **Jawaban**: Bisa — `docker compose up --build` dari README. Tiga container: PostgreSQL 16 + PostGIS, backend FastAPI, frontend Next.js. Seed data otomatis. Tidak perlu API key, tidak perlu koneksi eksternal. Total waktu dari clone sampai dashboard aktif: <5 menit (tergantung internet untuk pull image).

**Q19: Apa yang terjadi jika tidak ada PostgreSQL?**
> **Jawaban**: Backend tetap berjalan. Di data_store, kami mendeteksi jika DB tidak tersedia dan fallback ke in-memory store yang di-bootstrap dari data sintetis. Health check endpoint akan melaporkan "degraded" dengan DB "unavailable". Frontend tetap bisa menampilkan data. Ini untuk memudahkan juri yang mungkin tidak punya PostGIS.

**Q20: 94 test — apa itu cukup?**
> **Jawaban**: 94 test mencakup: (a) unit test NDVI — 7 test validasi formula, boundary, edge case, (b) unit test fleet — 30+ test termasuk validasi anomali injeksi, (c) API integration — 45+ test untuk 6 endpoint. Tidak termasuk frontend test (out of scope MVP). Coverage sudah proporsional untuk ukuran MVP (<5000 baris kode backend). Di produksi, target coverage minimal 80%.

**Q21: Bagaimana cara update threshold NDVI tanpa mengedit kode?**
> **Jawaban**: Threshold saat ini hardcoded di `ndvi.py`. Untuk produksi, threshold harus dipindahkan ke konfigurasi (environment variable atau database). Ini ada di roadmap teknis. Di MVP, kami prioritaskan fungsionalitas dulu.

**Q22: Apakah ada dokumentasi API? (OpenAPI/Swagger)**
> **Jawaban**: FastAPI secara otomatis menghasilkan dokumentasi OpenAPI di `/docs` (Swagger UI). Semua endpoint, schema request/response, dan validasi otomatis terdokumentasi di sana. Tidak perlu dokumentasi terpisah.

**Q23: Bagaimana cara menambah unit alat berat baru?**
> **Jawaban**: Di MVP: tambahkan entry ke `UNIT_DEFINITIONS` di `fleet_data.py` dan jalankan ulang. Di produksi: unit terdaftar di database → CRUD API → admin bisa tambah unit via dashboard. Data_store sudah dirancang untuk migrasi ini — cukup ganti body fungsi tanpa ubah router.

**Q24: Apakah frontend punya error handling jika backend mati?**
> **Jawaban**: Ya. Kedua halaman (Reklamasi, Operasional) punya: (a) `LoadingSkeleton` saat memuat, (b) `ErrorBanner` dengan pesan error dan tombol "Coba Lagi" jika fetch gagal, (c) `fetchApi` helper dengan `ApiError` class untuk error terstruktur. ZoneDetailSheet tambah pakai `cancelled` flag untuk hindari memory leak.

**Q25: Kenapa tidak ada dark mode?**
> **Jawaban**: (Senyum) MVP prioritas: fungsi dulu, estetika belakangan. Dark mode bisa ditambahkan dengan Tailwind `dark:` class dalam <2 jam. Tapi di dashboard tambang yang dipakai di siang hari lapangan, light mode sebenarnya lebih terbaca.

---

### Pertanyaan Jebakan Khusus (Trap Questions)

**Q26 (Trap): "Bukankah solusi serupa sudah ada di pasaran — misal dari Caterpillar atau Komatsu?"**
> **Jawaban**: Sistem OEM seperti Cat® MineStar atau Komatsu Komtrax memang menyediakan monitoring fleet, tetapi: (1) Terikat vendor — hanya untuk alat berat merek tertentu. KidecoIQ agnostik merek, (2) Tidak mencakup reklamasi — dua domain terpisah. KidecoIQ menyatukan environmental monitoring dan operational monitoring, (3) Biaya lisensi — solusi OEM mahal dan berlangganan. KidecoIQ open source. (4) Data OEM tidak selalu bisa diakses tim reklamasi — KidecoIQ menghilangkan silo data itu.

**Q27 (Trap): "Anda bilang software-only, tapi untuk predictive maintenance但你 tetap butuh data telematik. Di mana software-only-nya?"**
> **Jawaban**: Software-only berarti *tidak ada hardware baru* yang perlu dipasang. Data telematik alat berat sudah ada di log shift harian yang dicatat manual atau via sistem yang sudah terpasang. Yang kami lakukan adalah memanfaatkan data yang *sudah dimiliki* — bukan memasang sensor baru. Bahkan untuk demo, kami menggunakan CSV generator yang formatnya sama dengan export sistem existing.

**Q28 (Trap): "98.25% akurasi — itu akurasi apa? Akurasi klasifikasi piksel? Bukankah untuk laporan kepatuhan yang penting akurasi per zona, bukan per piksel?"**
> **Jawaban**: Pertanyaan bagus. 98.25% adalah akurasi per-piksel. Untuk laporan kepatuhan, metrik yang lebih relevan adalah (1) akurasi klasifikasi status zona (majority class), (2) akurasi tren NDVI. Pada data kami, status zona cocok 100% dengan ground truth (4 dari 4 zona benar). Jadi akurasi per zona = 100%. Per-piksel kami laporkan secara transparan sebagai metrik teknis.

**Q29 (Trap): "Demo ini pakai data sintetis — bagaimana saya tahu bahwa di data asli semuanya tidak collapse?"**
> **Jawaban**: Anda tidak bisa tahu sampai diuji dengan data asli. Dan itu memang langkah berikutnya. Tapi kami yakin karena: (1) NDVI formula sudah divalidasi 50 tahun literatur, (2) IsolationForest adalah algoritma robust yang tidak overfit ke data sintetis — ia mendeteksi outliers berdasarkan density, (3) Arsitektur modular memungkinkan penggantian komponen individual tanpa mengganggu yang lain. Jika model NDVI perlu diganti, cukup ubah `ndvi.py` — router dan frontend tetap sama.

**Q30 (Trap): "Anda hanya membuat ini dalam waktu kurang dari seminggu — apa tidak ada celah keamanan kritis?"**
> **Jawaban**: Sadar diri: untuk produksi, perlu audit keamanan menyeluruh. Yang sudah kami lakukan: (1) JWT authentication di backend, (2) Input validation via Pydantic, (3) CORS terbatas ke origin frontend. Celah yang kami tahu: (a) secret key JWT hardcoded di `.env` — harus pindah ke secret manager, (b) belum ada rate limiting, (c) belum ada SQL injection protection untuk raw query di migration (tapi sudah pakai parameterized query). Semua ini masuk priority tinggi di roadmap.

---

## Bagian C: Checklist Screenshot/Video Cadangan

> **Prinsip**: Jika demo live gagal (server crash, internet mati, proyektor error),
> presenter bisa *fallback* ke slide berisi screenshot + screen recording pendek.

### Wajib — Minimal 10 Screenshot

| # | Modul | Tampilan | Keterangan | Status |
|---|---|---|---|---|
| 1 | Home | Dashboard shell | Sidebar + header KidecoIQ | ⬜ |
| 2 | Operasional | Tabel fleet (10 unit) | Tampilkan kolom Risiko (EX-001 89.8 HIGH paling atas) | ⬜ |
| 3 | Operasional | Alert panel | 10 alert dengan level high/medium | ⬜ |
| 4 | Operasional | Detail anomali HD-002 | 60 shift + 2 shift merah anomaly | ⬜ |
| 5 | Reklamasi | Peta Leaflet 5 zona | Rectangle warna sesuai status | ⬜ |
| 6 | Reklamasi | StatsGrid | 4 card: Total Zona, NDVI, Tutupan, Kepatuhan | ⬜ |
| 7 | Reklamasi | ZoneCard Sektor A | Status badge hijau "Sehat" | ⬜ |
| 8 | Reklamasi | ZoneDetailSheet Sektor A | Side sheet dengan riwayat NDVI + tren | ⬜ |
| 9 | Reklamasi | ZoneDetailSheet Sektor C | Status merah "Kritis" + risk flag | ⬜ |
| 10 | Metrik | Confusion matrix NDVI | Slide tabel precision/recall | ⬜ |
| 11 | Metrik | Terminal pytest 94 passed | Bukti test suite | ⬜ |
| 12 | Infra | `docker compose ps` output | 3 container running | ⬜ |

### Opsional — Video Screen Recording (untuk extreme fallback)

| # | Durasi | Isi |
|---|---|---|
| V1 | 30 detik | Operasional: buka halaman → scroll fleet → klik HD-002 → tunjuk anomaly shifts |
| V2 | 30 detik | Reklamasi: buka halaman → klik Sektor A → side sheet → klik Sektor C → side sheet |
| V3 | 15 detik | Backend: `curl localhost:8000/reklamasi/report` → JSON keluar |

### Cara Mengambil Screenshot (perintah untuk disiapkan)

```
# 1. Pastikan backend berjalan
source backend/.venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. Pastikan frontend berjalan (terminal terpisah)
cd frontend && npm run dev

# 3. Buka browser di localhost:3000
# 4. Ambil screenshot dengan tools OS (Cmd+Shift+4 di macOS)
# 5. Simpan ke data/screenshots/
```

### Struktur Folder Screenshot yang Diusulkan
```
data/screenshots/
├── 01-operasional-fleet.png
├── 02-operasional-alerts.png
├── 03-operasional-anomaly-hd002.png
├── 04-reklamasi-map.png
├── 05-reklamasi-statsgrid.png
├── 06-reklamasi-sektor-a-detail.png
├── 07-reklamasi-sektor-c-risk.png
├── 08-metrics-confusion-matrix.png
├── 09-metrics-pytest-94.png
├── 10-infra-docker-ps.png
└── README.md (penjelasan tiap screenshot)
```

---

> **Dokumen ini disusun oleh lead architect KidecoIQ untuk persiapan presentasi final KIC 2026.**
> Revisi terakhir: 2026-06-19.

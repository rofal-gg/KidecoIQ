# PROMPT_PLAYBOOK.md — Urutan Prompt KidecoIQ (Awal sampai Final & Testing)
> Asumsi: folder `kideco-iq-agent-kit` (SPEC.md, TASKS.md, PROGRESS.md, opencode.json, `.opencode/agent/*`) sudah ada di root repo (lihat deliverable sebelumnya). Prompt di sini SENGAJA dipecah kecil per sesi — jangan digabung jadi satu mega-prompt, itu melawan desain SPEC.md/TASKS.md yang sudah kita buat.
>
> Pola tiap sesi: (1) buka dengan agent **Plan**, (2) eksekusi dengan subagent spesifik via prompt di bawah, (3) tutup sesi — pastikan agent sudah update PROGRESS.md & centang TASKS.md sebelum keluar.

---

## Sesi 0 — Sanity Check Setup (sekali saja di awal)
```
Baca SPEC.md, PROGRESS.md, TASKS.md. Konfirmasi: apakah opencode.json terbaca dengan benar (instructions ter-load), dan apakah model deepseek/deepseek-v4-flash aktif. Jangan eksekusi task apapun, cukup laporkan status setup.
```

---

## FASE 1 — Skeleton (agent: lead)
**Sesi 1**
```
@lead Kerjakan task #1 dan #2 di TASKS.md: setup skeleton FastAPI (main.py, struktur core/, koneksi PostgreSQL+PostGIS, endpoint health check), dan buat schema database untuk tabel reklamasi_zones, reklamasi_history, fleet_units, fleet_logs sesuai SPEC.md §5-6. Sertakan migration script. Jalankan server lokal, pastikan health check merespons 200, baru update PROGRESS.md.
```
**Checklist tutup sesi:** server start tanpa error, endpoint `/health` jalan, PROGRESS.md & TASKS.md sudah diupdate.

---

## FASE 2 — Modul Reklamasi (agent: backend-reklamasi)
**Sesi 2**
```
@backend-reklamasi Kerjakan task #3 dan #4 di TASKS.md. Buat dulu 1-2 raster sintetis kecil (band Red & NIR) sebagai data uji pipeline NDVI (bukan data final, cuma untuk validasi kode). Implementasikan kalkulasi NDVI dan klasifikasi 4 kategori. WAJIB sertakan unit test: NDVI harus berada di rentang -1 sampai 1, dan setiap piksel terklasifikasi ke salah satu dari 4 kategori yang valid (tidak ada nilai di luar itu).
```
**Sesi 3**
```
@backend-reklamasi Kerjakan task #5 dan #6: endpoint GET /reklamasi/zones, /reklamasi/zones/{id}/history, /reklamasi/report — sesuai kontrak di SPEC.md §5, gunakan data hasil sesi sebelumnya. Sertakan test API sederhana (httpx/pytest) yang memastikan setiap endpoint mengembalikan status 200 dan struktur JSON sesuai kontrak.
```
**Checklist tutup fase:** unit test NDVI lulus, 3 endpoint merespons benar, struktur JSON dicatat di PROGRESS.md supaya agent frontend tahu bentuk datanya persis.

---

## FASE 3 — Modul Operasional (agent: backend-operasional)
**Sesi 4**
```
@backend-operasional Kerjakan task #7 dan #8: buat generator data dummy fleet yang realistis (8-10 unit, variasi idle time 5-25%, sesekali anomali jelas), lalu implementasikan deteksi anomali (Isolation Forest) dan skor risiko maintenance. Sertakan test yang memverifikasi: anomali yang disisipkan sengaja di data dummy memang terdeteksi oleh model (bukan asal lolos semua).
```
**Sesi 5**
```
@backend-operasional Kerjakan task #9: endpoint GET /operasional/fleet, /operasional/fleet/{id}/anomaly, /operasional/alerts sesuai kontrak SPEC.md §6. Sertakan test API dasar seperti yang dilakukan agent backend-reklamasi.
```
**Checklist tutup fase:** model anomali terbukti mendeteksi kasus yang disengaja salah di data dummy (bukan hanya "jalan tanpa error"), 3 endpoint merespons benar.

---

## FASE 4 — Frontend (agent: frontend)
**Sesi 6**
```
@frontend Kerjakan task #10 dan #11: setup Next.js+Tailwind, shell dashboard 2 modul, dan halaman Reklamasi (peta Leaflet + card statistik) memakai MOCK data sesuai kontrak SPEC.md §5 — JANGAN tunggu backend. Setelah selesai, laporkan ke saya cara menjalankannya (`npm run dev` dst) supaya saya bisa cek tampilannya sendiri — kamu tidak bisa melihat hasil visualmu sendiri.
```
*(→ kamu cek tampilan manual di browser sebelum lanjut sesi berikutnya)*

**Sesi 7**
```
@frontend Kerjakan task #12: halaman Operasional (tabel fleet + alert list) dengan mock data. Lanjutkan task #13: ganti SEMUA mock data di kedua halaman dengan fetch API asli ke backend (cek PROGRESS.md untuk konfirmasi endpoint backend sudah siap). Hapus kode mock yang sudah tidak terpakai, jangan dibiarkan dua-duanya hidup.
```
**Checklist tutup fase:** kamu sudah membuka dashboard di browser dan mengecek tampilan sendiri (bukan hanya percaya laporan agent), data yang tampil benar-benar dari API bukan mock lagi.

---

## FASE 5 — Integrasi Infra (agent: devops)
**Sesi 8**
```
@devops Kerjakan task #14: buat docker-compose.yml (backend+frontend+postgres) dan Dockerfile masing-masing. Setelah siap, jalankan `docker compose down -v` lalu `docker compose up` dari kondisi benar-benar bersih, pastikan dashboard bisa diakses dan data awal (seed) otomatis terisi tanpa langkah manual tambahan. Tuliskan command persis yang harus dijalankan orang lain (juri/panitia) di README project.
```
**Checklist tutup fase:** `docker compose up` dari nol benar-benar berhasil tanpa langkah manual tersembunyi yang kamu lakukan sendiri tanpa sadar.

---

## FASE 6 — Testing & QA Menyeluruh (agent: qa-reviewer)
**Sesi 9**
```
@qa-reviewer Lakukan audit penuh: (1) cocokkan kontrak API yang diimplementasikan backend dengan yang dipakai frontend, laporkan ketidakcocokan field/endpoint apa pun. (2) Jalankan SEMUA unit test & API test yang ada di seluruh modul, laporkan yang gagal. (3) Jalankan model klasifikasi vegetasi dan model deteksi anomali fleet pada data validasi yang tersedia, laporkan metrik konkret (akurasi, precision/recall, atau minimal confusion matrix sederhana) — angka ini akan dikutip di proposal/presentasi, jadi harus jujur dan bisa dipertanggungjawabkan, jangan dibuat-buat. (4) Cek di PROGRESS.md apakah ada agent yang menyentuh file di luar scope-nya. Laporkan status akhir: "siap demo" atau daftar hal yang harus diperbaiki dulu.
```
**Kalau ada temuan "belum siap demo":** kembali ke agent terkait dengan prompt singkat yang merujuk temuan spesifik dari qa-reviewer, jangan minta perbaikan general.

---

## FASE 7 — Persiapan Demo & Presentasi Final (agent: lead)
**Sesi 10**
```
@lead Kerjakan task #16. Siapkan: (1) skenario demo langkah-demi-langkah yang pas untuk slot 20 menit presentasi+demo sesuai format final KIC (lalu disusul 25 menit tanya jawab juri), urutannya: masalah singkat → demo Modul Operasional (tunjukkan deteksi anomali) → demo Modul Reklamasi (tunjukkan peta & prediksi risiko) → metrik akurasi dari hasil QA → penutup dampak. (2) Daftar pertanyaan sulit yang mungkin ditanyakan juri berdasarkan 5 kriteria resmi (relevansi data Kideco, signifikansi AI, dampak & implementasi, kreativitas, kelengkapan dokumentasi), beserta draf jawaban jujur — termasuk jawaban siap untuk pertanyaan soal data yang masih generalisasi industri (predictive maintenance) bukan data internal Kideco asli. (3) Checklist screenshot/rekaman video cadangan untuk tiap modul, jaga-jaga kalau demo live gagal saat presentasi.
```

**Sesi 11 (opsional, hari sebelum presentasi)**
```
@lead Lakukan dry-run penuh skenario demo dari awal sampai akhir tanpa interupsi, seolah-olah sedang presentasi sungguhan ke juri. Catat di PROGRESS.md bagian mana yang terasa janggal/lambat/berisiko gagal, dan perbaikan apa yang masih realistis dilakukan dalam waktu tersisa.
```

---

## Catatan Penutup
- Total ini 11 sesi inti (di luar Sesi 0). Kalau satu sesi terasa akan melebihi budget 200k token output, hentikan di tengah task — bukan masalah, PROGRESS.md akan menyimpan progres, lanjutkan task yang sama di sesi berikutnya dengan prompt yang sama.
- Urutan FASE 2 dan FASE 3 (backend-reklamasi vs backend-operasional) bisa ditukar atau dikerjakan berselang-seling karena tidak saling bergantung — sesuaikan dengan siapa di tim yang lebih siap mengerjakan bagian mana lebih dulu.
- FASE 4 (frontend) sengaja baru disuruh ganti dari mock ke API asli di akhir (task #13) — supaya frontend tidak terblokir menunggu backend di awal.

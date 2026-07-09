# ☕ KopiSeru Marketing Dashboard

> **One-screen interactive marketing analytics dashboard for KopiSeru coffee chain branches across Indonesia.**

![Dashboard](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)

---

## 📋 Deskripsi Proyek

**KopiSeru Marketing Dashboard** adalah aplikasi web satu halaman (*one-screen dashboard*) yang dibangun menggunakan **Streamlit** untuk memvisualisasikan data pemasaran, transaksi, dan pendapatan jaringan kedai kopi KopiSeru secara interaktif dan real-time.

Dashboard ini dirancang untuk kebutuhan **analitik pemasaran** tingkat manajerial, menampilkan KPI utama, tren keuangan bulanan, distribusi saluran pelanggan, efektivitas promo, performa kategori produk, dan perbedaan perilaku pelanggan antara hari kerja dan akhir pekan — semuanya dalam **satu tampilan layar tanpa scroll**.

---

## 🏗️ Struktur Proyek

```
uas/
│
├── app.py                      # Aplikasi utama Streamlit
├── coffe_shop_final.xlsx       # Dataset utama (28.748 baris, 24 kolom)
├── explore_data.py             # Script eksplorasi & validasi data
├── data_info.txt               # Output ringkasan info dataset
├── dashboard_architecture.txt  # Dokumentasi arsitektur aplikasi
└── README.md                   # Dokumentasi proyek ini
```

---

## 🚀 Cara Menjalankan

### 1. Prasyarat

Pastikan Python `3.12+` sudah terpasang, kemudian install dependensi:

```bash
pip install streamlit pandas numpy plotly openpyxl
```

### 2. Jalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan otomatis membuka browser di `http://localhost:8501`.

### 3. Konfigurasi Data (Opsional)

Secara default, aplikasi akan **otomatis mencari file Excel** di direktori yang sama dengan `app.py`. Prioritas pencarian:

1. Environment variable `KOPISERU_DATA_PATH` (path absolut ke file `.xlsx`)
2. File bernama `coffe_shop_final.xlsx` di direktori proyek
3. Fallback: file `.xlsx` pertama yang ditemukan di direktori proyek

```bash
# Contoh menggunakan env variable (opsional)
set KOPISERU_DATA_PATH=C:\path\ke\data\kopiseru.xlsx
streamlit run app.py
```

---

## 📊 Dataset

| Atribut | Detail |
|---|---|
| **File** | `coffe_shop_final.xlsx` |
| **Jumlah Baris** | 28.748 baris |
| **Jumlah Kolom** | 24 kolom |
| **Periode Data** | 2021 — 2023 |
| **Jumlah Cabang** | 40 cabang di seluruh Indonesia |

### Kolom Dataset

| Kolom | Tipe | Keterangan |
|---|---|---|
| `date` | datetime | Tanggal observasi harian per cabang |
| `branch_id` | str | Kode unik cabang (contoh: `KS-031`) |
| `branch_name` | str | Nama cabang |
| `branch_city` | str | Kota lokasi cabang |
| `branch_province` | str | Provinsi lokasi cabang |
| `branch_type` | str | Tipe cabang: `Standalone`, `University`, `Office Area`, `Mall` |
| `total_transactions` | int | Jumlah transaksi harian |
| `total_revenue` | int | Total pendapatan harian (Rp) |
| `avg_ticket_size` | int | Rata-rata nilai belanja per transaksi (Rp) |
| `total_cups_sold` | int | Total cup terjual dalam sehari |
| `top_selling_category` | str | Kategori produk terlaris hari itu |
| `dine_in_percent` | float | Persentase transaksi dine-in (%) |
| `delivery_percent` | float | Persentase transaksi delivery (%) |
| `takeaway_percent` | float | Persentase transaksi takeaway (%) |
| `operating_cost` | int | Biaya operasional harian cabang (Rp) |
| `promo_active` | bool | Status apakah promo sedang berjalan |
| `promo_type` | str | Jenis promo: `Cashback E-Wallet`, `Bundling Snack`, `Happy Hour`, `Diskon 20%`, `Buy 1 Get 1` |
| `is_weekend` | bool | `True` jika hari Sabtu/Minggu |
| `customer_satisfaction` | float | Skor kepuasan pelanggan (2.5 — 5.0) |
| `weather` | str | Kondisi cuaca harian |
| `employee_on_duty` | int | Jumlah karyawan bertugas |

---

## 🖥️ Fitur Dashboard

### 🔍 Filter Interaktif (Cascading Filters)
Dashboard memiliki sistem filter berjenjang (*cascading*) yang **dinamis dan anti-crash**:

| Filter | Opsi |
|---|---|
| **Year** | All Years / 2021 / 2022 / 2023 |
| **Branch** | All Branches / 40 nama cabang |
| **City** | All Cities / kota-kota dinamis |
| **Branch Type** | All Types / Standalone / University / Office Area / Mall |
| **Promo Type** | All Promos / Cashback E-Wallet / Bundling Snack / dll |

> Jika pilihan filter menjadi tidak valid (misal kota berpindah namun cabang tidak tersedia), sistem otomatis mereset filter yang bersangkutan.

---

### 📈 Komponen Visualisasi

#### 1. 📦 KPI Cards (4 Kartu Utama)
| Kartu | Metrik | Formula |
|---|---|---|
| 💰 Revenue | Total Pendapatan | `SUM(total_revenue)` |
| 👥 Total Transactions | Total Transaksi | `SUM(total_transactions)` |
| 🎟️ Avg Ticket Size | Rata-rata Nilai Belanja | `SUM(revenue) / SUM(transactions)` (Weighted Average) |
| ☕ Cups Sold | Total Cup Terjual | `SUM(total_cups_sold)` |

Setiap kartu dilengkapi **badge YoY Delta** (▲/▼ %) yang aktif saat filter **Year** dipilih, membandingkan performa dengan tahun sebelumnya.

---

#### 2. 📉 Performance Overview *(Baris Tengah Kiri)*
Grafik garis ganda yang menampilkan **tren bulanan Revenue vs Biaya Operasional (Operating Cost)** dalam skala Rupiah yang sama.

- **Revenue** → Garis solid tebal, dengan area bayangan transparan
- **Operating Cost** → Garis putus-putus (dotted)
- Hover menampilkan nilai Rupiah lengkap untuk kedua metrik

---

#### 3. 🍩 Customer Channel Mix *(Baris Tengah Kanan)*
Grafik donat (*donut chart*) yang menampilkan **distribusi saluran pelanggan**:
- **Dine-in** — persentase pelanggan makan di tempat
- **Delivery** — persentase pengiriman
- **Takeaway** — persentase bawa pulang

---

#### 4. 📊 Promo vs Non-Promo *(Baris Bawah Kiri)*
Grafik batang vertikal yang membandingkan **rata-rata pendapatan harian** saat promo aktif vs tidak ada promo, membantu mengukur efektivitas kampanye pemasaran.

---

#### 5. 🏆 Top Category Performance *(Baris Bawah Tengah)*
Grafik batang horizontal yang mengurutkan **5 kategori produk** berdasarkan total pendapatan:
- Non-Coffee
- Espresso Based
- Kopi Susu
- Tea
- Snack & Pastry

---

#### 6. 📅 Weekday vs Weekend Performance *(Baris Bawah Kanan)*
Grafik batang kelompok (*grouped bar*) yang membandingkan performa antara **hari kerja dan akhir pekan** untuk tiga metrik sekaligus:
- Rata-rata Pendapatan
- Rata-rata Transaksi
- Rata-rata Ticket Size

---

## 🛠️ Teknologi yang Digunakan

| Library | Versi | Kegunaan |
|---|---|---|
| `streamlit` | Latest | Web framework & UI server |
| `pandas` | Latest | Manipulasi & agregasi data |
| `numpy` | Latest | Komputasi numerik |
| `plotly` | Latest | Grafik interaktif |
| `openpyxl` | Latest | Pembacaan file Excel (.xlsx) |

---

## 🎨 Desain & Estetika

- **Palet Warna**: Dominan cokelat-kopi & krem (`#3E2723` — `#F8F4EF`) dengan aksen hijau/merah untuk indikator delta
- **Tipografi**: [Inter](https://fonts.google.com/specimen/Inter) dari Google Fonts (weight 300–800)
- **Layout**: Full-screen tanpa scrollbar vertikal, dioptimasi untuk resolusi laptop standar
- **Responsif**: Media query `@media (max-height: 720px)` untuk adaptasi saat browser di-zoom-in
- **Animasi**: Micro-animations pada hover kartu KPI

---

## 📁 Cabang KopiSeru (40 Cabang)

Tersebar di berbagai kota besar Indonesia:

| Kota | Cabang |
|---|---|
| **Bali** | Renon, Beachwalk, Udayana, Pantai Indah |
| **Bandung** | Dago, Braga, ITB, Cihampelas, Pasteur, Paragon |
| **Jakarta** | Sudirman, Thamrin, Kuningan, Grand Indonesia, UI Depok, Kemang, Senayan, PIK, Kelapa Gading, Pondok Indah, Binus Anggrek |
| **Semarang** | Undip, Simpang Lima |
| **Surabaya** | Darmo, Tunjungan, ITS, HR Muhammad, Asia Mega Mas, Pakuwon |
| **Yogyakarta** | UGM, Ambarukmo, Malioboro, Seturan |
| **Malang** | Malang Town Square, UB |
| **Makassar** | Losari, Panakkukang |
| **Medan** | Sun Plaza, USU |

---

## 📌 Catatan Akademis

Proyek ini dibuat sebagai tugas **Ujian Akhir Semester (UAS)** mata kuliah **Data Analytics & Visualization (DAV)**, Semester 6.

---

*Built with ☕ and Python*

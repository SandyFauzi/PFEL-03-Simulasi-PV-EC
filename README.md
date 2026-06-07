# Simulasi Sistem Fotovoltaik–Elektrokimia (PV-EC)

### Penangkapan CO₂ dan Produksi Oksigen melalui *Artificial Photosynthesis*

> **Proyek Akhir Mata Kuliah Pengantar Energi** · Program Studi Fisika — Kelompok 3 (PFEL)

Simulasi numerik *time-series* (resolusi 1 menit) sebuah sistem terintegrasi **Fotovoltaik–Elektrokimia + Direct Air Capture (PV-EC-DAC)** yang menggerakkan reaktor *artificial photosynthesis* dengan energi surya untuk **mereduksi CO₂ menjadi metanol** sekaligus **menghasilkan O₂**. Model mengimplementasikan tujuh persamaan tata kelola secara dinamis: konversi fotovoltaik dengan koreksi termal, persamaan **Nernst**, kinetika **Tafel** (OER & CO₂RR), **Hukum Faraday**, dan neraca massa **DAC**.

📄 **Halaman dokumentasi lengkap (akademis):** [`docs/index.html`](docs/index.html) — buka via GitHub Pages.

---

## 🔑 Hasil Utama (panel 10 m²)

| Metrik | Harian | Tahunan |
|---|---|---|
| Efisiensi *sun-to-fuel* (η_total) | **8,8%** | 9,5% |
| Efisiensi neto (η_net, termasuk DAC) | 8,5% | 9,1% |
| Produksi O₂ | 1.641 g | **453 kg** (≈ 5 pohon) |
| CO₂ ditangkap → metanol | 902 g | **249 kg** |
| H₂ produk samping (HER) | 82 g | 22,6 kg |
| Tegangan sel reaktor | 2,05 V | (min. teoritis 1,23 V) |
| Kebutuhan air | 6,1 L | 1.680 L |

Produktivitas musim **kemarau 25% lebih tinggi** daripada musim hujan (iklim tropis).

---

## 📂 Struktur Repositori

```
.
├── Simulasi.py              # Skenario HARIAN (24 jam, resolusi 1 menit) → 7 grafik
├── Simulasi_Tahunan.py      # Skenario TAHUNAN (365 hari, musim tropis) → 3 grafik
├── Dashboard_Simulasi.py    # Dashboard 14-panel gabungan → Dashboard_Semua.png
├── Poster_Grafik.py         # Generator 6 grafik gaya poster (impor mesin v2.0)
├── Laporan DOCX.md          # Laporan akademis lengkap (Abstrak, Bab 1–7, Pustaka)
├── konteks_proyek.md        # Landasan teori & persamaan kunci
├── requirements.txt
└── docs/
    ├── index.html           # Halaman dokumentasi akademis (gaya Documenter)
    └── images/              # Figur terkurasi (dashboard + 6 grafik poster)
```

---

## 🚀 Cara Menjalankan

```bash
# 1. Pasang dependensi
pip install -r requirements.txt

# 2. Jalankan simulasi
python Simulasi.py            # → 7 grafik harian + ringkasan ke layar
python Simulasi_Tahunan.py    # → 3 grafik tahunan + ringkasan
python Dashboard_Simulasi.py  # → Dashboard_Semua.png (14 panel)
python Poster_Grafik.py       # → 6 grafik gaya poster (poster_1..6.png)
```

Seluruh parameter dapat diubah di blok atas tiap skrip (mis. `LUAS_PANEL`, `ETA_PV_REF`,
`PHI_CO2RR`, `N_SEL`). Hasil otomatis konsisten karena `Poster_Grafik.py` mengimpor
mesin fisika dari `Simulasi.py` dan `Simulasi_Tahunan.py`.

---

## 🧮 Model Fisika (ringkas)

Rantai konversi enam tahap, dievaluasi tiap langkah waktu:

```
Energi Surya → [PV + MPPT, η(T)] → [Penyaluran DC, I²R]
            → [Reaktor: Nernst + Tafel + Faraday] → [Selektivitas + DAC]
            → O₂ + CH₃OH (dari CO₂) + H₂
```

| Pers. | Bentuk | Peran |
|---|---|---|
| 1.1 | `P = V·I` | Daya panel, η_PV bergantung suhu |
| 1.2 | `ΔG = −nFE` (Nernst) | Potensial reversibel E_rev(T) |
| 1.3 | `2H₂O → O₂ + 4H⁺ + 4e⁻` | OER (anoda), kinetika Tafel |
| 1.4 | `CO₂ + 6H⁺ + 6e⁻ → CH₃OH + H₂O` | CO₂RR (katoda) + transpor massa |
| 1.5 | `CO₂ + 2KOH → K₂CO₃ + H₂O` | DAC + energi regenerasi |
| 1.6 | `η_total = η_PV · η_EC` | Efisiensi total |
| 1.7 | `P_loss = I²·R` | Rugi ohmik |

---

## 👥 Tim — Kelompok 3 (PFEL), Fisika

| Anggota | NPM |
|---|---|
| Sandy Fauzi Amrulloh | 140310240054 |
| Aleasandrina Senjaya Putri | 140310240076 |
| Khansa Humaira Adhari | 140310240068 |
| Muhammad Qaisha Rosyada | 140310240040 |

---

## 📜 Lisensi

Proyek akademik untuk keperluan edukasi. Materi referensi (jurnal) tidak disertakan
dalam repositori karena alasan hak cipta.

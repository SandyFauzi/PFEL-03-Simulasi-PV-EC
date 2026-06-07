# Konteks Proyek PFEL Kelompok 3

## Informasi Umum

**Judul Proyek:** Integrasi Panel Surya pada Sistem Carbon Capture untuk Konversi CO₂ menjadi Oksigen melalui Artificial Photosynthesis

**Anggota Kelompok:**
1. Sandy Fauzi Amrulloh — 140310240054
2. Aleasandrina Senjaya Putri — 140310240076
3. Khansa Humaira Adhari — 140310240068
4. Muhammad Qaisha Rosyada — 140310240040

---

## I. Latar Belakang

Peningkatan konsentrasi gas rumah kaca, khususnya karbon dioksida (CO₂), di atmosfer akibat pembakaran bahan bakar fosil telah memicu perubahan iklim global yang semakin mengkhawatirkan. Menurut Prats-Salvado dkk. (2024), teknologi penangkapan karbon langsung dari udara atau **Direct Air Capture (DAC)** merupakan salah satu pendekatan paling menjanjikan untuk mengurangi konsentrasi CO₂ atmosfer secara aktif. Tantangan utama teknologi ini adalah kebutuhan energi operasionalnya yang sangat besar — menggunakan listrik dari pembangkit fosil untuk menangkap emisi fosil justru menjadi sebuah ironi teknis.

Di sisi lain, perkembangan teknologi energi terbarukan, terutama **Pembangkit Listrik Tenaga Surya (PLTS)**, membuka peluang untuk mengatasi hambatan tersebut. Panel surya (fotovoltaik) menghasilkan arus searah (DC) bersih yang secara teknis kompatibel untuk menggerakkan sistem DAC maupun reaktor elektrokimia. Dalam kerangka **Artificial Photosynthesis (Fotosintesis Buatan)**, energi surya tidak hanya digunakan sebagai sumber daya, melainkan juga sebagai pemicu reaksi fotokatalitik yang meniru prinsip fotosintesis alami pada tumbuhan — menyerap CO₂ dan air (H₂O) untuk menghasilkan oksigen (O₂) dan molekul berenergi tinggi (Wang & Pornrungroj, 2025).

Konsep integrasi ini dikenal sebagai sistem **Fotovoltaik-Elektrokimia (PV-EC)**. Panel surya menyuplai listrik ke reaktor fotoelektrokimia yang bekerja secara dua fungsi sekaligus: menangkap CO₂ dari udara dan menghasilkan O₂ sebagai produk akhir. Tantangan teknis muncul dari sifat output panel surya yang fluktuatif akibat perubahan intensitas cahaya dan suhu, sehingga diperlukan komponen **Maximum Power Point Tracking (MPPT) Charge Controller** yang meregulasi tegangan dan arus keluaran panel.

---

## II. Rumusan Masalah

1. Bagaimana cara kerja rangkaian kelistrikan sistem PLTS off-grid dalam menyuplai daya DC secara stabil untuk sistem carbon capture dan reaktor artificial photosynthesis?
2. Bagaimana cara kerja reaktor artificial photosynthesis dalam mengonversi CO₂ menjadi oksigen (O₂), serta faktor-faktor yang mempengaruhi efisiensinya?
3. Bagaimana efisiensi keseluruhan sistem Fotovoltaik-Elektrokimia (PV-EC) dalam mengintegrasikan proses penangkapan dan konversi CO₂, termasuk ditinjau dari potensi kehilangan energi dalam sistem, serta bagaimana hal tersebut mempengaruhi kelayakan penerapannya sebagai solusi berkelanjutan?
4. Bagaimana dampak implementasi sistem PV-EC terhadap kualitas udara, khususnya dalam peningkatan kadar oksigen (O₂) di lingkungan sekitar?

---

## III. Tujuan Kajian

1. Mengetahui cara kerja rangkaian kelistrikan sistem PLTS off-grid dalam menyuplai daya DC secara stabil untuk mendukung operasional sistem carbon capture dan reaktor artificial photosynthesis.
2. Mengetahui cara kerja reaktor artificial photosynthesis dalam mengonversi CO₂ menjadi O₂ serta faktor-faktor yang mempengaruhi efisiensinya.
3. Mengetahui efisiensi keseluruhan sistem PV-EC dalam mengintegrasikan proses penangkapan dan konversi CO₂, termasuk pengaruh kehilangan energi dalam sistem, serta dampaknya terhadap kelayakan penerapan sistem sebagai solusi berkelanjutan.
4. Mengetahui dampak implementasi sistem PV-EC terhadap kualitas udara, khususnya dalam peningkatan kadar oksigen (O₂) di lingkungan sekitar.

---

## IV. Hasil dan Pembahasan — Analisis dan Sintesis

### A. Aspek Teknis & Fisika

#### 1. Eksitasi Foton dan Mekanisme Transportasi Muatan

PLTS beroperasi berlandaskan hukum Fisika Zat Padat dan mekanika kuantum, dimana radiasi matahari berinteraksi dengan material semikonduktor dalam bentuk paket energi diskret (foton).

- **Interaksi Foton-Elektron:** Ketika foton menumbuk permukaan panel surya (berbasis silikon p-n junction), foton tersebut harus memiliki energi kuantum yang setara atau melebihi celah pita energi material semikonduktor tersebut (`E_foton ≥ E_gap`). Penyerapan energi ini memicu transisi elektronik, menyebabkan elektron tereksitasi dari Pita Valensi (Valence Band) melampaui celah pita (band gap) energi menuju Pita Konduksi (Conduction Band) dan menjadi elektron bebas (Rudiyanto et al., 2023).

- **Pemisahan Pasangan Muatan:** Transisi elektronik ini meninggalkan kekosongan bermuatan positif (lubang) di Pita Valensi. Pemisahan pasangan muatan elektron-lubang menciptakan medan listrik internal pada sambungan p-n, yang mencegah muatan untuk berekombinasi secara prematur dan mendorong elektron mengalir melalui sirkuit eksternal (Rauf et al., 2023).

- **Dinamika Daya dan Peran MPPT:** Aliran elektron menghasilkan arus searah (DC) dengan keluaran daya yang didefinisikan oleh:

  ```
  P = V × I    ...(1.1)
  ```

  Intensitas iradiasi (W/m²) dan temperatur sel berfluktuasi secara real-time. Modul MPPT secara konstan memantau fluktuasi ini dan mengubah impedansi sirkuit agar panel surya terus beroperasi tepat pada titik P_maks dalam kurva tegangan-arus (I-V), memastikan suplai energi ke reaktor tetap pada batas maksimum teoritisnya (Rauf et al., 2023).

#### 2. Konversi Termodinamika dan Kinetika Elektrokimia

Sistem PV-EC mengubah peran kelistrikan PLTS dari sekadar penyuplai daya rumah tangga menjadi penggerak reaksi redoks dalam sistem artificial photosynthesis. Alur konversi: `Energi Surya → Listrik DC → Energi Kimia`.

- **Termodinamika Reaksi Up-Hill:** Reaksi pemecahan air (H₂O) dan reduksi CO₂ merupakan reaksi non-spontan yang sangat endotermik (`ΔG > 0`). Pemecahan H₂O menjadi H₂ dan O₂ menuntut perubahan energi bebas Gibbs standar sebesar `ΔG° = 237,13 kJ/mol`, ekuivalen dengan tegangan termodinamika minimum sebesar **1,23 V** (Whang & Apaydin, 2018).

- **Intervensi Hukum Nernst:** Untuk membalikkan keadaan termodinamika ini, energi dari luar diinjeksikan, direpresentasikan oleh korelasi:

  ```
  ΔG = -nFE    ...(1.2)
  ```

  Dimana `n` = mol elektron, `F` = konstanta Faraday, `E` = potensial sel. Arus DC dari PLTS menyediakan beda potensial (E) ini. Potensial tegangan berlebih (overpotential) yang diinduksi oleh listrik surya menekan nilai ΔG sistem menjadi negatif, sehingga reaksi dapat dilangsungkan secara paksa (Prats-Salvado et al., 2024).

- **Tantangan Kinetika dan Peran Katalis:** Meskipun termodinamika telah diatasi oleh voltase PLTS, reaksi ini masih dihadapkan pada rintangan kinetik masif, terutama pada **Oxygen Evolution Reaction (OER)** di anoda yang melibatkan transfer 4 elektron secara simultan (Nosaka, 2023). Diperlukan fungsionalisasi permukaan menggunakan katalis nanopartikel untuk menurunkan energi aktivasi (`E_a`), memfasilitasi transfer elektron yang cepat, dan meminimalkan energi terbuang menjadi panas (Martí et al., 2023).

#### 3. Reaksi Elektrokimia (Anoda & Katoda)

Reaksi elektrokimia dalam sistem artificial photosynthesis adalah proses konversi energi listrik menjadi energi kimia melalui perpindahan elektron dan ion dalam suatu sel elektrolisis.

- **Reaksi di Anoda (Oksidasi — OER):**

  ```
  2H₂O → O₂ + 4H⁺ + 4e⁻    ...(1.3)
  ```

  Molekul air teradsorpsi pada situs aktif katalis, melepaskan elektron dan membentuk spesies antara (OH, O, OOH) sebelum membentuk O₂. Proses ini melibatkan transfer muatan antar permukaan, perubahan energi potensial permukaan, dan reorganisasi struktur molekul. Energi pemutusan ikatan O-H sangat besar sehingga kehadiran katalis mutlak diperlukan.

- **Dinamika Aliran Muatan:** Elektron dari anoda mengalir melalui sirkuit eksternal menuju katoda (mengikuti hukum Ohm), sedangkan proton (H⁺) bermigrasi melalui elektrolit akibat dorongan difusi dan medan listrik.

- **Reaksi di Katoda (Reduksi — CO₂RR):**

  ```
  CO₂ + 6H⁺ + 6e⁻ → CH₃OH + H₂O    ...(1.4)
  ```

  Molekul CO₂ yang linear dan stabil harus teradsorpsi dan teraktivasi menjadi radikal antara (*CO₂⁻) untuk melemahkan ikatan rangkap C=O. Serangkaian transfer proton dan elektron kemudian terjadi secara bertahap.

- **Efisiensi keseluruhan** ditentukan oleh minimasi overpotential, penurunan resistansi ohmik, serta optimalisasi transpor massa (difusi CO₂ ke permukaan elektroda).

#### 4. Transpor Muatan & Carbon Capture

- **Mekanisme Transpor Muatan:** Elektron (e⁻) mengalir melalui rangkaian eksternal menuruni gradien potensial listrik dari anoda ke katoda. Proton (H⁺) berdifusi dan bermigrasi melalui elektrolit, sering melalui **mekanisme Grotthuss** (lompatan proton antar molekul air). Konduktivitas elektrolit dan suhu mendikte resistansi internal.

- **Mekanisme Carbon Capture (DAC):** Molekul CO₂ berdifusi dari udara menuju larutan basa (KOH) menuruni gradien konsentrasi:

  ```
  CO₂ + 2KOH → K₂CO₃ + H₂O    ...(1.5)
  ```

  Senyawa karbonat yang terbentuk kemudian diregenerasi melalui pemanasan (kalsinasi) yang membutuhkan transfer panas masif untuk memutus ikatan kimia dan melepaskan CO₂ murni ke dalam reaktor (Zhang et al., 2020).

#### 5. Efisiensi & Loss Energi

Efisiensi total sistem PV-EC:

```
η_total = η_PV × η_EC    ...(1.6)
```

- **Kehilangan Energi pada Panel Surya (η_PV):** Panel surya hanya menyerap foton yang memenuhi syarat energi celah pita (`E_foton ≥ E_gap`). Foton berenergi rendah tidak terserap (transmisi), energi berlebih dari foton berenergi tinggi terbuang menjadi panas (thermalization loss). Ditambah kerugian rekombinasi, efisiensi sel silikon tunggal dibatasi oleh **Batas Shockley-Queisser di angka ~33%**. Modul MPPT krusial untuk meminimalkan mismatch loss.

- **Kehilangan Energi pada Elektrokimia (η_EC):** Kerugian terbesar dari overpotential (tegangan di atas batas teoritis 1,23 V) yang terbuang sebagai panas akibat rintangan kinetik. Terdapat juga disipasi energi akibat hambatan ohmik:

  ```
  P_loss = I² × R    ...(1.7)
  ```

- **Nilai Tambah:** Meskipun efisiensi sun-to-fuel lebih rendah dari sun-to-electricity konvensional, sistem ini mampu menyimpan densitas energi sangat tinggi dalam bentuk ikatan kimiawi (solar fuels) jangka panjang.

---

### B. Aspek Ekonomi & Lingkungan

#### 1. Aspek Ekonomi (LCOP vs LCOD)

Sistem berbasis tenaga surya umumnya memiliki **biaya investasi awal (CAPEX)** yang tinggi akibat kebutuhan panel surya dan kapasitas penyimpanan energi (baterai) dalam jumlah besar.

- **LCOP (Levelized Cost of Produced CO₂):** Menghitung biaya rata-rata untuk setiap CO₂ yang berhasil ditangkap, **tanpa** memperhatikan emisi tambahan selama proses. Hanya fokus pada output CO₂ yang keluar dari sistem.

- **LCOD (Levelized Cost of Removed CO₂):** Metrik **lebih lengkap** — menghitung biaya berdasarkan jumlah CO₂ yang benar-benar berhasil dihilangkan dari atmosfer secara bersih (neto). Memperhitungkan emisi tidak langsung yang muncul selama proses.

**Perbandingan:**
- Sistem DAC konvensional (gas alam): terlihat murah di LCOP, namun LCOD meningkat tajam karena emisi proses besar.
- Sistem DAC surya: kenaikan biaya dari LCOP ke LCOD relatif kecil karena emisi tambahan jauh lebih rendah.
- **Kesimpulan:** LCOD dianggap metrik yang lebih akurat dan adil untuk evaluasi kinerja ekonomi sekaligus dampak lingkungan (Prats-Salvado et al., 2024).

#### 2. Fakta Lingkungan

- Sistem L-DAC konvensional mengandalkan pembakaran gas alam untuk kalsinasi bersuhu tinggi — menghasilkan emisi fosil baru.
- Integrasi teknologi **panas matahari terkonsentrasi** (concentrated solar thermal) mampu mengeliminasi emisi operasional secara signifikan.
- Dengan energi bersih, jejak karbon terutama hanya dari tahap konstruksi → pencapaian **net removal** yang jauh lebih tinggi (Keith et al., 2018).

#### 3. Kelemahan Lingkungan Fisik: Konsumsi Air

- Sistem L-DAC mengkonsumsi **~4,7 ton H₂O per 1 ton CO₂** yang ditangkap.
- Laju penguapan melonjak drastis di area bersuhu tinggi dengan kelembaban rendah.
- **Solusi:**
  - Penempatan fasilitas di wilayah pesisir (< 100 km dari laut)
  - Integrasi dengan unit desalinasi bertenaga surya (~3,5 kWh per ton H₂O)
  - Tangki penyimpanan air yang disesuaikan kebutuhan puncak harian
  - Inovasi masa depan: material **Metal-Organic Frameworks (MOFs)** atau pendekatan biomimetik untuk memanen air dari udara (Prats-Salvado et al., 2024)

---

### C. Aspek Sosial dan Regulasi

#### 1. Potensi Penerimaan Masyarakat
- Tren positif namun tantangan pemahaman masih ada.
- Persepsi kuat bahwa bahan bakar fosil harus digantikan energi bersih (Protti & Serpone, 2023).
- Hambatan utama: kurangnya kesadaran manfaat jangka panjang dan biaya awal yang dipersepsikan tinggi.
- Di daerah pedesaan, keberhasilan bergantung pada proses partisipatoris dan manfaat kolektif langsung (Rauf dkk., 2023).

#### 2. Penciptaan Lapangan Kerja
- Sektor energi surya global telah menciptakan > 4,4 juta pekerjaan (hingga 2019), diproyeksikan terus meningkat.
- Sistem PV-EC membutuhkan SDM terampil: instalasi, pemeliharaan modul PV, pengoperasian reaktor kimia.
- Membuka peluang industri lokal naik kelas dari perakitan ke pabrikasi sel surya dan komponen teknologi tinggi (Rauf dkk., 2023).

#### 3. Kebijakan yang Diperlukan
- **Feed-in Tariff (FiT):** Kepastian harga jual listrik untuk meningkatkan minat investasi.
- **Insentif fiskal dan green financing** untuk meningkatkan kelayakan ekonomi proyek.
- **Carbon trading / carbon pricing** untuk memberikan nilai ekonomi pada pengurangan emisi.
- Penyederhanaan perizinan dan penguatan kebijakan industri (TKDN).

#### 4. Insentif yang Sudah Tersedia
- Kebijakan Feed-in Tariff (FiT) / skema harga listrik energi terbarukan.
- **Perpres No. 112 Tahun 2022:** Percepatan pengembangan energi terbarukan.
- Insentif fiskal: keringanan pajak, pembebasan bea masuk, fasilitas perpajakan.
- **Perpres No. 98 Tahun 2021:** Mekanisme nilai ekonomi karbon, perdagangan karbon.

#### 5. Hambatan Non-Teknis
- **Finansial:** CAPEX sangat tinggi; biaya pembiayaan tinggi di negara berkembang; ketidakpastian biaya konstruksi untuk proses baru.
- **Sosial:** Kurangnya kesadaran masyarakat; rendahnya rasa memiliki (ownership) pada proyek komunitas; kurangnya SDM terampil lokal.
- **Regulasi:** Birokrasi rumit (red tape); kurangnya konsistensi informasi antar pemangku kepentingan; konflik pemanfaatan lahan; rendahnya daya beli listrik oleh utilitas.

---

## V. Kesimpulan dan Rekomendasi

### 1. Urgensi dan Nilai Strategis
- Sistem PV-EC berperan krusial dalam pemanfaatan energi surya secara komprehensif.
- Alur konversi: `Energi Surya → Listrik DC → Energi Kimia`
- PLTS bertindak sebagai penggerak utama reaksi redoks pada artificial photosynthesis.
- Emisi operasional dari kalsinasi bersuhu tinggi dapat dieliminasi dengan panas matahari terkonsentrasi.
- Seluruh sirkulasi konversi CO₂ → O₂ digerakkan energi terbarukan bersih, lebih unggul secara ekonomi dan lingkungan saat dievaluasi menggunakan metrik **LCOD**.

### 2. Analisis Efisiensi dan Kapabilitas
- Panel surya silikon tunggal dibatasi **Batas Shockley-Queisser (~33%)** akibat kerugian transmisi dan rekombinasi.
- Efisiensi total: `η_total = η_PV × η_EC`
- Efisiensi sun-to-fuel lebih rendah dari panel konvensional, namun menawarkan **penyimpanan densitas energi sangat tinggi** dalam ikatan kimiawi jangka panjang.

### 3. Kendala Utama
- **Termodinamika & Kinetika:** Reaksi endotermik non-spontan (ΔG > 0). Tegangan teoritis 1,23 V + overpotential besar akibat transfer 4 elektron di anoda.
- **Kelemahan Fisik:** L-DAC mengkonsumsi 4,7 ton H₂O / 1 ton CO₂. Laju penguapan melonjak di area panas & kering.
- **Hambatan Ekonomi:** CAPEX sangat tinggi untuk perangkat keras dan infrastruktur.

### 4. Solusi dan Rekomendasi
- **Fungsionalisasi Material Katalis:** Katalis nanopartikel pada elektroda untuk memangkas energi aktivasi, mempercepat transfer elektron, meminimalkan rugi panas.
- **Optimalisasi Sirkuit Daya:** Integrasi modul MPPT pada Solar Charge Controller (SCC) untuk menekan mismatch loss saat panel menyuplai arus fluktuatif (~6 jam/hari).
- **Strategi Pengelolaan Cairan:** Penempatan di area pesisir (< 100 km dari laut) + desalinasi bertenaga surya. Ke depan: adopsi MOFs atau pendekatan biomimetik untuk pemanenan air dari udara.

---

## VI. Daftar Referensi (APA 7th Edition)

1. **Prats-Salvado, E., Jagtap, N., Monnerie, N., & Sattler, C.** (2024). Solar-Powered Direct Air Capture: Techno-Economic and Environmental Assessment. *Environmental Science & Technology, 58*(5), 2282–2292. https://doi.org/10.1021/acs.est.3c06313

2. **Nosaka, Y.** (2023). Molecular Mechanisms of Oxygen Evolution Reactions for Artificial Photosynthesis. *Oxygen, 3*(1), 146–163. https://doi.org/10.3390/oxygen3010014

3. **Martí, G., Mallón, L., Romero, N., Francàs, L., Bofill, R., Philippot, K., García-Antón, J., & Sala, X.** (2023). Surface-Functionalized Nanoparticles as Catalysts for Artificial Photosynthesis. *Advanced Energy Materials, 13*(21), 2300282. https://doi.org/10.1002/aenm.202300282

4. **Whang, D. R., & Apaydin, D. H.** (2018). Artificial Photosynthesis: Learning from Nature. *ChemPhotoChem, 2*(2), 148–160. https://doi.org/10.1002/cptc.201700163

5. **Wang, Q., & Pornrungroj, C.** (2025). Artificial photosynthetic processes using carbon dioxide, water and sunlight: can they power a sustainable future? *Chemical Science, 16*(1), 18990–19011. https://doi.org/10.1039/D4SC05481B

6. **Le, A. H., & Guillomaitre, N.** (2022). Artificial Photosynthesis: A Review of the Technology, Application, Opportunities, and Challenges. *Journal of Student Research, 11*(1). https://doi.org/10.47611/jsrhs.v11i1.2332

7. **Protti, S., & Serpone, N.** (2023). Multidisciplinary approaches to solar-driven water splitting and carbon dioxide conversion. Dalam S. Ghosh & Q. Wang (Eds.), *Recent Developments in Functional Materials for Artificial Photosynthesis* (hlm. 1–32). Royal Society of Chemistry. https://doi.org/10.1039/9781839164422-00001

8. **Rudiyanto, B., Rachmanita, R. E., & Budiprasojo, A.** (2023). *Dasar-dasar Pemasangan Panel Surya*. Unisma Press.

9. **Wibowo, A.** (2023). *Instalasi Panel Listrik Surya*. Yayasan Prima Agus Teknik.

10. **Rauf, R., Ritnawati, Rachim, F., Dahri, A. T., Andre, H., Napitupulu, R. A. M., Erdawaty, Aminur, Corio, D., & Siagian, P.** (2023). *Matahari sebagai Energi Masa Depan: Panduan Lengkap Pembangkit Listrik Tenaga Surya (PLTS)*. Yayasan Kita Menulis.

---

## VII. Persamaan-Persamaan Kunci

| No. | Persamaan | Keterangan |
|-----|-----------|------------|
| 1.1 | `P = V × I` | Daya keluaran panel surya |
| 1.2 | `ΔG = -nFE` | Korelasi elektrokimia Nernst |
| 1.3 | `2H₂O → O₂ + 4H⁺ + 4e⁻` | Reaksi anoda (OER) |
| 1.4 | `CO₂ + 6H⁺ + 6e⁻ → CH₃OH + H₂O` | Reaksi katoda (CO₂RR) |
| 1.5 | `CO₂ + 2KOH → K₂CO₃ + H₂O` | Penangkapan karbon (DAC) |
| 1.6 | `η_total = η_PV × η_EC` | Efisiensi total sistem PV-EC |
| 1.7 | `P_loss = I² × R` | Disipasi energi ohmik (Hukum Joule) |

---

## VIII. Konstanta dan Parameter Penting

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| Batas Shockley-Queisser | ~33% | Efisiensi maksimum sel surya silikon tunggal |
| Tegangan teoritis pemecahan air | 1,23 V | Minimum termodinamika |
| ΔG° pemecahan air | 237,13 kJ/mol | Energi bebas Gibbs standar |
| Konsumsi air L-DAC | ~4,7 ton H₂O / ton CO₂ | Kelemahan fisik sistem |
| Energi desalinasi surya | ~3,5 kWh / ton H₂O | Kebutuhan energi rendah |
| Jarak ideal ke laut | < 100 km | Untuk integrasi desalinasi |
| Waktu pengisian surya | ~6 jam/hari | Jadwal suplai DC fluktuatif |

# -*- coding: utf-8 -*-
"""
============================================================================
 POSTER_GRAFIK.py  —  Generator 4 Grafik Terpilih untuk Poster Ilmiah
 Proyek PV-EC · PFEL Kelompok 3
----------------------------------------------------------------------------
 Menghasilkan 4 grafik PALING KUAT (gaya poster: font besar, judul + caption)
 dengan ANGKA IDENTIK model fisika v2.0 — diimpor langsung dari Simulasi.py
 dan Simulasi_Tahunan.py (bukan dihitung ulang), jadi selalu sinkron.

   Gambar 1 · Aliran & Kehilangan Energi   (Sankey)        → section ANALISIS
   Gambar 2 · Efisiensi Konversi Sistem    (bar + SQ)      → section ANALISIS
   Gambar 3 · Dekomposisi Tegangan Sel     (stacked bar)   → section SIMULASI
   Gambar 4 · Produksi O₂ & CO₂ Tahunan    (bar bulanan)   → section VISUALISASI

 Jalankan:  python Poster_Grafik.py
============================================================================
"""
import io
import sys
import contextlib
sys.stdout.reconfigure(encoding="utf-8")  # agar panah → dll tercetak di console
import matplotlib
matplotlib.use("Agg")                     # headless: tidak membuka window
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey

# --- Impor mesin fisika v2.0 (jalankan diam-diam, angka diambil apa adanya) ---
# StringIO dummy: kedua modul memanggil sys.stdout.reconfigure() saat diimpor.
class _Quiet(io.StringIO):
    def reconfigure(self, *a, **k):   # no-op agar tidak error
        pass

print("Memuat model fisika v2.0 (harian + tahunan)...")
with contextlib.redirect_stdout(_Quiet()):
    import Simulasi as S              # model harian  (Opus 4.6 v2.0)
    import Simulasi_Tahunan as T      # model tahunan (Opus 4.6 v2.0)
plt.close("all")                      # bersihkan figur bawaan kedua modul

# ===========================================================================
# GAYA POSTER  (font besar agar terbaca dari ~1,5–2 m)
# ===========================================================================
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 15,
    "axes.titlesize": 20,
    "axes.titleweight": "bold",
    "axes.labelsize": 16,
    "axes.labelweight": "bold",
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "figure.dpi": 120,
})
# Palet konsisten lintas-grafik
C_SUN = "#F9A825"; C_PV = "#1565C0"; C_RE = "#2E7D32"
C_RUGI = "#C62828"; C_O2 = "#0277BD"; C_CO2 = "#6A1B9A"; C_DARK = "#263238"
# Palet 3 produk — diselaraskan dengan warna kartu indikator
P_O2 = "#7CB342"; P_CO2 = "#1565C0"; P_H2 = "#5E35B1"
# Pita musim
C_KEMARAU = "#FFE0B2"; C_HUJAN = "#B3E5FC"


def caption(fig, teks):
    """Tambah caption 1-baris di bawah figur (gaya poster)."""
    fig.text(0.5, 0.005, teks, ha="center", va="bottom",
             fontsize=12.5, style="italic", color=C_DARK, wrap=True)


# ===========================================================================
# GAMBAR 1 — ALIRAN & KEHILANGAN ENERGI (Sankey)
# ===========================================================================
fig1 = plt.figure(figsize=(10, 6.5))
ax1 = fig1.add_subplot(1, 1, 1, xticks=[], yticks=[])
ax1.set_title("Gambar 1. Aliran & Kehilangan Energi Sistem PV-EC",
              pad=16, color=C_DARK)
sk = Sankey(ax=ax1, unit=None, scale=1/100, gap=0.5, head_angle=120, shoulder=0.02)
sk.add(
    flows=[100, -S.pct_rugi_pv, -S.pct_rugi_ohm, -S.pct_rugi_ec, -S.pct_kim],
    labels=["Surya\nmasuk\n100%",
            f"Rugi Panel\n(suhu + SQ)\n{S.pct_rugi_pv:.0f}%",
            f"Rugi Ohmik\nI²R  {S.pct_rugi_ohm:.1f}%",
            f"Rugi Elektrokimia\n(overpotensial)\n{S.pct_rugi_ec:.1f}%",
            f"ENERGI KIMIA\nBERGUNA\n{S.pct_kim:.1f}%"],
    orientations=[0, 1, 1, 1, 0],
    pathlengths=[0.5, 0.40, 0.35, 0.6, 0.55],
    facecolor=C_PV, edgecolor="#0D47A1",
)
for d in sk.finish():
    for txt in d.texts:
        txt.set_fontsize(12); txt.set_fontweight("bold")
caption(fig1, f"Dari 100% energi surya, hanya {S.pct_kim:.1f}% tersimpan sebagai "
              "energi kimia (O₂). Rugi terbesar terjadi di konversi panel surya.")
fig1.tight_layout(rect=[0, 0.03, 1, 1])
fig1.savefig("poster_1_aliran_energi.png", dpi=300, bbox_inches="tight")

# ===========================================================================
# GAMBAR 2 — EFISIENSI KONVERSI (bar + batas Shockley-Queisser)
# ===========================================================================
fig2, ax2 = plt.subplots(figsize=(8, 6))
lbl = ["η_PV", "η_EC", "η_total\n(PV×EC)", "FE\n(Faraday)"]
val = [S.eta_pv_avg*100, S.eta_EC_avg*100, S.eta_total*100, S.FE_avg*100]
clr = [C_PV, C_RE, C_DARK, "#FF6F00"]
bars = ax2.bar(lbl, val, color=clr, width=0.62, edgecolor="white", linewidth=1.5)
ax2.bar_label(bars, fmt="%.1f%%", padding=4, fontweight="bold", fontsize=15)
ax2.axhline(S.SQ_LIMIT*100, color=C_RUGI, ls="--", lw=2)
ax2.text(3.45, S.SQ_LIMIT*100 + 1.2, f"Batas Shockley-Queisser ({S.SQ_LIMIT*100:.0f}%)",
         color=C_RUGI, ha="right", fontsize=12.5, fontweight="bold")
ax2.set_ylabel("Efisiensi [%]")
ax2.set_ylim(0, 100)
ax2.set_title("Gambar 2. Efisiensi Konversi Sistem PV-EC", pad=14, color=C_DARK)
caption(fig2, f"Efisiensi total {S.eta_total*100:.1f}% = η_PV × η_EC. "
              "Rendah karena rantai konversi panjang (sun-to-fuel).")
fig2.tight_layout(rect=[0, 0.04, 1, 1])
fig2.savefig("poster_2_efisiensi.png", dpi=300, bbox_inches="tight")

# ===========================================================================
# GAMBAR 3 — DEKOMPOSISI TEGANGAN SEL (stacked bar horizontal)
# ===========================================================================
E_rev_avg   = float(np.mean(S.E_rev[S.mask_aktif]))
v_ohm_avg   = float(np.mean(S.v_ohm_int[S.mask_aktif]))
komp_nilai  = [E_rev_avg, S.eta_oer_avg, S.eta_co2rr_avg, v_ohm_avg]
komp_label  = ["E_rev (Nernst)", "η_OER (anoda)", "η_CO₂RR (katoda)", "V_ohm (I·R)"]
komp_warna  = [C_RE, C_RUGI, "#FF9800", "#9E9E9E"]

fig3, ax3 = plt.subplots(figsize=(11, 4.2))
kiri = 0.0
for nilai, lab, w in zip(komp_nilai, komp_label, komp_warna):
    ax3.barh(0, nilai, left=kiri, color=w, edgecolor="white", linewidth=2,
             height=0.55, label=f"{lab} = {nilai:.3f} V")
    if nilai > 0.05:
        ax3.text(kiri + nilai/2, 0, f"{nilai:.2f}", ha="center", va="center",
                 color="white", fontweight="bold", fontsize=13)
    kiri += nilai
# Garis minimum teoritis 1,23 V
ax3.axvline(1.23, color=C_DARK, ls="--", lw=2.5)
ax3.text(1.23, 0.42, "Minimum teoritis 1,23 V", ha="center", va="bottom",
         color=C_DARK, fontsize=12.5, fontweight="bold")
ax3.annotate("", xy=(kiri, -0.42), xytext=(1.23, -0.42),
             arrowprops=dict(arrowstyle="<->", color=C_RUGI, lw=2))
ax3.text((1.23 + kiri)/2, -0.5, f"Overpotensial terbuang = {kiri-1.23:.2f} V",
         ha="center", va="top", color=C_RUGI, fontsize=12, fontweight="bold")
ax3.set_xlim(0, kiri*1.05); ax3.set_ylim(-0.75, 0.75)
ax3.set_yticks([]); ax3.set_xlabel("Tegangan sel [V]")
ax3.set_title(f"Gambar 3. Dekomposisi Tegangan Sel Reaktor ({kiri:.2f} V)",
              pad=14, color=C_DARK)
ax3.legend(loc="upper left", fontsize=11, framealpha=0.9)
ax3.grid(axis="y")
caption(fig3, f"Sel butuh {kiri:.2f} V, padahal teori cukup 1,23 V. "
              "Selisihnya (overpotensial, dominan dari OER) terbuang jadi panas.")
fig3.tight_layout(rect=[0, 0.05, 1, 1])
fig3.savefig("poster_3_tegangan_sel.png", dpi=300, bbox_inches="tight")

# ===========================================================================
# GAMBAR 4 — GABUNGAN: SUMBER SURYA (titik-titik) + PRODUKSI BULANAN
# ===========================================================================
fig4, (ax4a, ax4b) = plt.subplots(2, 1, figsize=(11, 8.5), sharex=True,
                                  height_ratios=[1, 1.2])
mid = np.array([T.ab[m] + T.hpb[m]/2 for m in range(12)])

# Pita musim di latar KEDUA panel
for ax in (ax4a, ax4b):
    for m in [4, 5, 6, 7, 8]:                       # Mei–Sep = kemarau
        ax.axvspan(T.ab[m], T.ab[m+1], color=C_KEMARAU, alpha=0.55, zorder=0)
    for m in [0, 1, 2, 10, 11]:                     # Nov–Mar = hujan
        ax.axvspan(T.ab[m], T.ab[m+1], color=C_HUJAN, alpha=0.55, zorder=0)

# (a) PANEL ATAS — sumber surya: scatter titik-titik harian + rata-rata bergerak
ax4a.scatter(T.doy - 1, T.H_harian, s=12, color=C_SUN, alpha=0.55,
             label="Iradiasi harian", zorder=2)
Hs = np.convolve(T.H_harian, np.ones(15)/15, mode="same")
ax4a.plot((T.doy - 1)[7:-7], Hs[7:-7], color="#E65100", lw=3,
          label="Rata-rata bergerak", zorder=3)
ax4a.set_ylabel("Iradiasi\n[kWh/m²/hari]")
ax4a.set_ylim(T.H_harian.min()*0.85, T.H_harian.max()*1.18)
ax4a.set_title("Gambar 4. Sumber Surya & Produksi Sepanjang Tahun (Iklim Tropis)",
               pad=12, color=C_DARK)
ax4a.legend(loc="upper left", fontsize=11, ncol=2, framealpha=0.9)
ax4a.text(np.mean(mid[[4, 8]]), T.H_harian.max()*1.10, "MUSIM KEMARAU",
          ha="center", color="#E65100", fontsize=12, fontweight="bold")
ax4a.text(mid[0], T.H_harian.max()*1.10, "hujan", ha="center",
          color="#0277BD", fontsize=11, fontweight="bold")

# (b) PANEL BAWAH — produksi bulanan O₂ & CO₂ (warna seragam kartu indikator)
w = 12
b1 = ax4b.bar(mid - w/2, T.O2_bln, w, color=P_O2, label="O₂ dihasilkan",
              edgecolor="white", linewidth=1, zorder=2)
b2 = ax4b.bar(mid + w/2, T.CO2_bln, w, color=P_CO2, label="CO₂ ditangkap",
              edgecolor="white", linewidth=1, zorder=2)
ax4b.bar_label(b1, fmt="%.0f", fontsize=10, padding=2, fontweight="bold")
ax4b.set_ylabel("Produksi\n[kg/bulan]")
ax4b.set_ylim(0, T.O2_bln.max()*1.20)
ax4b.set_xlim(0, 365)
ax4b.set_xticks(mid); ax4b.set_xticklabels(T.nb)
ax4b.legend(loc="upper left", fontsize=12, framealpha=0.9)

caption(fig4, f"Iradiasi surya (atas) menggerakkan produksi (bawah): total {T.O2_th:.0f} kg O₂ "
              f"& {T.CO2_th:.0f} kg CO₂/tahun. Kemarau {((T.O2_k/T.O2_h)-1)*100:.0f}% lebih produktif.")
fig4.tight_layout(rect=[0, 0.04, 1, 1])
fig4.savefig("poster_4_produksi_tahunan.png", dpi=300, bbox_inches="tight")

# ===========================================================================
# GAMBAR 5 — PRODUK HARIAN O₂, CO₂ & H₂ (kumulatif sepanjang hari)
# ===========================================================================
fig5, ax5 = plt.subplots(figsize=(11, 6))
ax5.plot(S.t, S.kum_g_O2,  color=P_O2,  lw=3, label="O₂ dihasilkan")
ax5.plot(S.t, S.kum_g_CO2, color=P_CO2, lw=3, label="CO₂ ditangkap → metanol")
ax5.plot(S.t, S.kum_g_H2,  color=P_H2,  lw=3, label="H₂ produk samping")
ax5.fill_between(S.t, 0, S.kum_g_O2, color=P_O2, alpha=0.07)
for ckg, warna, dy in [(S.g_O2, P_O2, 0), (S.g_CO2, P_CO2, 0), (S.g_H2, P_H2, 0)]:
    ax5.annotate(f"{ckg:.0f} g", xy=(24, ckg), xytext=(24.3, ckg),
                 va="center", color=warna, fontweight="bold", fontsize=13)
ax5.set_xlabel("Waktu [jam]"); ax5.set_ylabel("Massa kumulatif [g/hari]")
ax5.set_xlim(0, 25.5); ax5.set_xticks(range(0, 25, 3))
ax5.set_title("Gambar 5. Produksi Harian O₂, CO₂ & H₂ (Kumulatif)",
              pad=14, color=C_DARK)
ax5.legend(loc="upper left", fontsize=13)
caption(fig5, f"Sehari: {S.g_O2:.0f} g O₂ · {S.g_CO2:.0f} g CO₂ · {S.g_H2:.0f} g H₂. "
              "Produksi terkonsentrasi siang hari saat surya kuat.")
fig5.tight_layout(rect=[0, 0.04, 1, 1])
fig5.savefig("poster_5_produk_harian.png", dpi=300, bbox_inches="tight")

# ===========================================================================
# GAMBAR 6 — PRODUK TAHUNAN O₂, CO₂ & H₂ (kumulatif sepanjang tahun)
# ===========================================================================
doy = T.doy - 1
kum_O2_th  = np.cumsum(T.g_O2_h)  / 1000.0      # kg
kum_CO2_th = np.cumsum(T.g_CO2_h) / 1000.0
kum_H2_th  = np.cumsum(T.g_H2_h)  / 1000.0

fig6, ax6 = plt.subplots(figsize=(11, 6))
ax6.plot(doy, kum_O2_th,  color=P_O2,  lw=3, label="O₂ dihasilkan")
ax6.plot(doy, kum_CO2_th, color=P_CO2, lw=3, label="CO₂ ditangkap → metanol")
ax6.plot(doy, kum_H2_th,  color=P_H2,  lw=3, label="H₂ produk samping")
ax6.fill_between(doy, 0, kum_O2_th, color=P_O2, alpha=0.07)
for tot, warna in [(T.O2_th, P_O2), (T.CO2_th, P_CO2), (T.H2_th, P_H2)]:
    ax6.annotate(f"{tot:.0f} kg", xy=(364, tot), xytext=(366, tot),
                 va="center", color=warna, fontweight="bold", fontsize=13)
ax6.set_xticks([T.ab[m] + T.hpb[m]/2 for m in range(12)]); ax6.set_xticklabels(T.nb)
ax6.set_xlim(0, 395); ax6.set_ylabel("Massa kumulatif [kg/tahun]")
ax6.set_title("Gambar 6. Produksi Tahunan O₂, CO₂ & H₂ (Kumulatif)",
              pad=14, color=C_DARK)
ax6.legend(loc="upper left", fontsize=13)
caption(fig6, f"Setahun: {T.O2_th:.0f} kg O₂ · {T.CO2_th:.0f} kg CO₂ · {T.H2_th:.0f} kg H₂. "
              "Kemiringan makin curam saat musim kemarau (Jun–Sep).")
fig6.tight_layout(rect=[0, 0.04, 1, 1])
fig6.savefig("poster_6_produk_tahunan.png", dpi=300, bbox_inches="tight")

# ===========================================================================
# RINGKASAN
# ===========================================================================
print("\n6 grafik poster tersimpan (300 dpi, gaya poster):")
print("  poster_1_aliran_energi.png      → ANALISIS    (Sankey energi)")
print("  poster_2_efisiensi.png          → ANALISIS    (bar efisiensi)")
print("  poster_3_tegangan_sel.png       → SIMULASI    (dekomposisi V)")
print("  poster_4_produksi_tahunan.png   → VISUALISASI (bar bulanan)")
print("  poster_5_produk_harian.png      → VISUALISASI (O₂+CO₂+H₂ harian)")
print("  poster_6_produk_tahunan.png     → VISUALISASI (O₂+CO₂+H₂ tahunan)")
print(f"\nAngka kunci (sinkron v2.0): η_total {S.eta_total*100:.1f}% | "
      f"V_sel {S.V_sel_avg:.2f} V")
print(f"  Harian : {S.g_O2:.0f} g O₂ · {S.g_CO2:.0f} g CO₂ · {S.g_H2:.0f} g H₂")
print(f"  Tahunan: {T.O2_th:.0f} kg O₂ · {T.CO2_th:.0f} kg CO₂ · {T.H2_th:.0f} kg H₂")

# -*- coding: utf-8 -*-
"""
============================================================================
 SIMULASI SISTEM PV-EC  —  Model Fisika Lengkap (Harian)
 Integrasi Panel Surya + Carbon Capture + Artificial Photosynthesis
----------------------------------------------------------------------------
 PFEL Kelompok 3
   1. Sandy Fauzi Amrulloh      140310240054
   2. Aleasandrina Senjaya P.   140310240076
   3. Khansa Humaira Adhari     140310240068
   4. Muhammad Qaisha Rosyada   140310240040
----------------------------------------------------------------------------
 Rantai konversi:  Energi Surya -> Listrik DC -> Energi Kimia (O2)

 Persamaan yang diimplementasikan:
   1.1  P = V x I                     (daya panel)
   1.2  dG = -nFE  /  Nernst          (potensial reversibel)
   1.3  2H2O -> O2 + 4H+ + 4e-       (OER, kinetika Tafel)
   1.4  CO2 + 6H+ + 6e- -> CH3OH     (CO2RR, kinetika Tafel)
   1.5  CO2 + 2KOH -> K2CO3 + H2O    (DAC, laju absorpsi)
   1.6  eta_total = eta_PV x eta_EC   (efisiensi total)
   1.7  P_loss = I^2 x R             (rugi ohmik)
============================================================================
"""
import sys, numpy as np
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
sys.stdout.reconfigure(encoding='utf-8')

# ===== 1. KONSTANTA UNIVERSAL =====
F_CONST  = 96485.0       # Konstanta Faraday      [C/mol]
R_GAS    = 8.314         # Konstanta gas           [J/(mol·K)]
M_O2     = 32.0          # Massa molar O2          [g/mol]
M_CO2    = 44.0          # Massa molar CO2         [g/mol]
M_H2     = 2.0           # Massa molar H2          [g/mol]
M_H2O    = 18.0          # Massa molar H2O         [g/mol]
VM_STP   = 22.4          # Volume molar STP        [L/mol]

# ===== 2. PARAMETER SURYA =====
G_PEAK       = 1000.0    # Iradiasi puncak STC     [W/m²]
JAM_TERBIT   = 6.0
JAM_TERBENAM = 18.0

# ===== 3. PARAMETER PANEL SURYA =====
LUAS_PANEL = 10.0        # Luas panel              [m²]
ETA_PV_REF = 0.20        # Efisiensi PV @25°C      [-]
SQ_LIMIT   = 0.33        # Batas Shockley-Queisser [-]
BETA_TEMP  = 0.004       # Koef. suhu silikon      [1/°C]
NOCT       = 45.0        # Suhu operasi nominal    [°C]
T_REF_PV   = 25.0        # Suhu referensi PV       [°C]
MISMATCH   = 0.25        # Rugi tanpa MPPT         [-]

# ===== 4. PROFIL SUHU AMBIENT (tropis) =====
T_AMB_MIN = 26.0         # Subuh                   [°C]
T_AMB_MAX = 34.0         # Sore                    [°C]

# ===== 5. BUS DC =====
V_BUS   = 48.0           # Tegangan bus            [V]
R_KABEL = 0.05           # Resistansi kabel        [Ω]

# ===== 6. REAKTOR ELEKTROKIMIA =====
E_REV_STD   = 1.229      # Potensial reversibel @25°C [V] (Pers. 1.2)
A_ELEKTRODA = 2000.0      # Luas elektroda efektif  [cm²]
N_SEL       = 5           # Jumlah sel seri (stack)
R_ASR       = 0.5         # Resistansi spesifik     [Ω·cm²]

# Kinetika OER — anoda (Pers. 1.3)
J0_OER     = 1e-6        # Rapat arus tukar OER    [A/cm²]
ALPHA_OER  = 0.50        # Koef. transfer OER      [-]

# Kinetika CO2RR — katoda (Pers. 1.4)
J0_CO2RR    = 5e-4       # Rapat arus tukar CO2RR  [A/cm²]
ALPHA_CO2RR = 0.50       # Koef. transfer CO2RR    [-]

# Efisiensi Faraday & transpor massa
FE_MAX  = 0.95           # FE maksimum             [-]
J_LIM   = 0.50           # Rapat arus batas difusi [A/cm²]

Z_O2  = 4                # Elektron per O2  (Pers. 1.3)
Z_CO2 = 6                # Elektron per CO2 (Pers. 1.4)

# ===== 7. PARAMETER DAC (Pers. 1.5) =====
K_ABS       = 0.01       # Koef. transfer massa    [m/s]
A_KONTAKTOR = 20.0       # Luas kontaktor udara    [m²]
CO2_PPM     = 420.0      # CO2 atmosfer            [ppm]
P_ATM       = 101325.0   # Tekanan atmosfer        [Pa]

# ===== 7b. SELEKTIVITAS KATODA — CO2RR vs HER =====
# Di artificial photosynthesis nyata, katoda tidak 100% menghasilkan metanol;
# sebagian arus "bocor" menjadi gas H2 (Hydrogen Evolution Reaction).
PHI_CO2RR = 0.60         # Fraksi arus faradaik -> CH3OH; sisanya -> H2  [-]
Z_H2      = 2            # Elektron per molekul H2 (2H+ + 2e- -> H2)

# ===== 7c. ENERGI REGENERASI DAC — kalsinasi (Keith 2018) =====
# Menangkap CO2 butuh memecah K2CO3/CaCO3 lewat kalsinasi ~900°C.
# Energi panas ini DOMINAN & terpisah dari listrik reaktor (dari surya termal).
Q_REGEN_TH   = 1.46      # Panas regenerasi [kWh_th/kg CO2] (~5.25 GJ/t, Keith 2018)
E_DAC_ELEK   = 0.37      # Listrik bantu DAC (kontaktor+kompresi) [kWh/kg CO2] (~366 kWh/t)
ETA_SOLAR_TH = 0.50      # Efisiensi kolektor surya termal (untuk hitung luas) [-]

# ===== 7d. NERACA AIR (Prats-Salvado 2024) =====
H2O_DAC = 4.7            # Konsumsi air DAC [kg H2O / kg CO2] (evaporasi L-DAC)

# Acuan konteks
O2_PER_POHON  = 274.0    # g O2/hari per pohon
CO2_PER_ORANG = 1000.0   # g CO2/hari per manusia

# ===== 8. SUMBU WAKTU (1 menit resolusi, 24 jam) =====
t    = np.linspace(0.0, 24.0, 24*60+1)
dt_s = (t[1] - t[0]) * 3600.0

# ===== TAHAP 1: PROFIL IRADIASI + SUHU =====
siang  = (t >= JAM_TERBIT) & (t <= JAM_TERBENAM)
durasi = JAM_TERBENAM - JAM_TERBIT
G = np.where(siang, G_PEAK * np.sin(np.pi*(t - JAM_TERBIT)/durasi), 0.0)
G = np.clip(G, 0.0, None)

# Suhu ambient: minimum subuh (~05), maksimum sore (~14)
T_amb = T_AMB_MIN + (T_AMB_MAX - T_AMB_MIN) * np.sin(
    np.clip(np.pi*(t - 5.0)/18.0, 0, np.pi))
T_amb = np.clip(T_amb, T_AMB_MIN, T_AMB_MAX)

# Suhu sel panel (NOCT model)
T_cell = T_amb + (NOCT - 20.0) * G / 800.0

# ===== TAHAP 2: PANEL + MPPT (Pers. 1.1) =====
# Efisiensi PV bergantung suhu sel
eta_pv = ETA_PV_REF * (1.0 - BETA_TEMP * (T_cell - T_REF_PV))
eta_pv = np.clip(eta_pv, 0.0, SQ_LIMIT)

P_pv = eta_pv * LUAS_PANEL * G                   # daya PV [W]
P_tanpa_mppt = P_pv * (1.0 - MISMATCH)

# ===== TAHAP 3: RUGI OHMIK KABEL (Pers. 1.7) =====
I_bus     = P_pv / V_BUS
P_ohmik   = I_bus**2 * R_KABEL
P_reaktor = np.clip(P_pv - P_ohmik, 0.0, None)

# ===== TAHAP 4: REAKTOR ELEKTROKIMIA (Pers. 1.2–1.5) =====
# Suhu reaktor ~ suhu ambient (reaktor outdoor, heat exchange)
T_reak_K = (T_amb + 5.0) + 273.15   # sedikit lebih panas dari ambient

# (a) Potensial reversibel Nernst (Pers. 1.2)
E_rev = E_REV_STD - 0.000846 * (T_reak_K - 298.15)

# (b) Iterasi titik operasi: P = V_stack × I
#     V_stack = N × [E_rev + η_OER(j) + η_CO2RR(j) + j·R_ASR]
I_reak = np.where(P_reaktor > 0, P_reaktor / (N_SEL * 2.0), 0.0)

for _ in range(60):
    j = I_reak / A_ELEKTRODA
    j_safe = np.maximum(j, 1e-12)
    # Tafel OER (Pers. 1.3)
    eta_oer = R_GAS*T_reak_K/(ALPHA_OER*F_CONST) * np.log(
        np.maximum(j_safe/J0_OER, 1.0))
    # Tafel CO2RR (Pers. 1.4)
    eta_co2rr = R_GAS*T_reak_K/(ALPHA_CO2RR*F_CONST) * np.log(
        np.maximum(j_safe/J0_CO2RR, 1.0))
    # Ohmik internal
    v_ohm_int = j_safe * R_ASR
    # Tegangan sel total
    V_sel = E_rev + eta_oer + eta_co2rr + v_ohm_int
    V_stack = N_SEL * V_sel
    I_new = np.where(V_stack > 0, P_reaktor / V_stack, 0.0)
    I_new = np.where(P_reaktor > 0, I_new, 0.0)
    if np.max(np.abs(I_new - I_reak)) < 1e-9:
        break
    I_reak = I_new

j_final = I_reak / A_ELEKTRODA

# (c) Efisiensi Faraday dinamis — limitasi transpor massa
FE_dyn = FE_MAX * np.sqrt(np.maximum(1.0 - j_final/J_LIM, 0.0))
FE_dyn = np.where(P_reaktor > 0, FE_dyn, 0.0)

# (c2) Selektivitas katoda: dari arus faradaik, fraksi PHI_CO2RR -> CH3OH (CO2RR),
#      sisanya "bocor" jadi H2 (HER) — kompetisi nyata di artificial photosynthesis
FE_CO2RR = FE_dyn * PHI_CO2RR            # porsi metanol
FE_HER   = FE_dyn * (1.0 - PHI_CO2RR)    # porsi hidrogen

# (d) Model DAC (Pers. 1.5): laju absorpsi CO2 dari udara
C_CO2_udara = CO2_PPM * 1e-6 * P_ATM / (R_GAS * (T_amb + 273.15))
r_DAC = K_ABS * A_KONTAKTOR * C_CO2_udara   # [mol/s] CO2 tersedia

# (e) Laju produksi (Hukum Faraday). O2 di anoda mengikuti TOTAL arus faradaik;
#     CH3OH hanya dari porsi CO2RR; H2 dari porsi HER.
laju_O2_max  = N_SEL * FE_dyn   * I_reak / (Z_O2   * F_CONST)
laju_CO2_max = N_SEL * FE_CO2RR * I_reak / (Z_CO2  * F_CONST)   # = laju CH3OH
laju_H2_max  = N_SEL * FE_HER   * I_reak / (Z_H2   * F_CONST)

# (f) Batasi CO2RR oleh suplai DAC; arus yang kekurangan CO2 beralih ke HER
#     (elektron kekal -> O2 tak berubah, hanya produk katoda yang bergeser)
rasio_DAC = np.where(laju_CO2_max > 0,
                     np.minimum(np.divide(r_DAC, laju_CO2_max,
                                out=np.ones_like(r_DAC), where=laju_CO2_max>0),
                                1.0), 1.0)
laju_CO2 = laju_CO2_max * rasio_DAC
laju_H2  = laju_H2_max + laju_CO2_max * (1.0 - rasio_DAC) * (Z_CO2 / Z_H2)
laju_O2  = laju_O2_max

# Akumulasi
kum_mol_O2  = np.cumsum(laju_O2)  * dt_s
kum_mol_CO2 = np.cumsum(laju_CO2) * dt_s
kum_mol_H2  = np.cumsum(laju_H2)  * dt_s
kum_g_O2    = kum_mol_O2  * M_O2
kum_g_CO2   = kum_mol_CO2 * M_CO2
kum_g_H2    = kum_mol_H2  * M_H2

# ===== 9. RINGKASAN & EFISIENSI (Pers. 1.6) =====
def integral_kWh(P): return np.sum(P) * dt_s / 3.6e6

E_surya   = integral_kWh(G * LUAS_PANEL)
E_pv      = integral_kWh(P_pv)
E_ohm_kb  = integral_kWh(P_ohmik)
E_reaktor = integral_kWh(P_reaktor)

muatan = np.sum(I_reak * FE_dyn * rasio_DAC) * dt_s
# Energi kimia = N_sel × E_rev × I_eff × FE × dt  (tiap sel menyimpan energi)
E_kimia = N_SEL * np.sum(E_rev * I_reak * FE_dyn * rasio_DAC) * dt_s / 3.6e6

eta_pv_avg = E_pv / E_surya if E_surya > 0 else 0
eta_EC_avg = E_kimia / E_reaktor if E_reaktor > 0 else 0
eta_total  = E_kimia / E_surya if E_surya > 0 else 0

g_O2  = kum_g_O2[-1];  g_CO2 = kum_g_CO2[-1];  g_H2 = kum_g_H2[-1]
mol_O2 = kum_mol_O2[-1]; mol_CO2 = kum_mol_CO2[-1]; mol_H2 = kum_mol_H2[-1]
L_O2 = mol_O2 * VM_STP
setara_pohon   = g_O2  / O2_PER_POHON
setara_manusia = g_CO2 / CO2_PER_ORANG

# --- Neraca air (Prats-Salvado 2024) ---
air_OER_mL = mol_O2 * 2.0 * M_H2O                  # 2 H2O dipecah per O2 (stoikiometri OER)
air_DAC_mL = (g_CO2 / 1000.0) * H2O_DAC * 1000.0   # 4,7 kg H2O / kg CO2 (evaporasi)
air_total_L = (air_OER_mL + air_DAC_mL) / 1000.0   # liter/hari (1 g air ≈ 1 mL)

# --- Energi regenerasi DAC / kalsinasi (Keith 2018) ---
E_regen_th  = (g_CO2 / 1000.0) * Q_REGEN_TH        # kWh panas (kalsinasi ~900°C)
E_dac_el    = (g_CO2 / 1000.0) * E_DAC_ELEK        # kWh listrik bantu DAC
E_solar_th  = E_regen_th / ETA_SOLAR_TH            # surya yg harus dipanen kolektor termal
luas_termal = E_solar_th / (E_surya / LUAS_PANEL) if E_surya > 0 else 0.0  # m² kolektor
eta_net     = E_kimia / (E_surya + E_solar_th) if (E_surya + E_solar_th) > 0 else 0.0

pct = lambda x: x / E_surya * 100 if E_surya > 0 else 0
pct_pv  = pct(E_pv); pct_reak = pct(E_reaktor); pct_kim = pct(E_kimia)
pct_rugi_pv = 100 - pct_pv
pct_rugi_ohm = pct_pv - pct_reak
pct_rugi_ec = pct_reak - pct_kim

# Statistik overpotensial saat siang
mask_aktif = P_reaktor > 10.0
eta_oer_avg = np.mean(eta_oer[mask_aktif]) if np.any(mask_aktif) else 0
eta_co2rr_avg = np.mean(eta_co2rr[mask_aktif]) if np.any(mask_aktif) else 0
V_sel_avg = np.mean(V_sel[mask_aktif]) if np.any(mask_aktif) else 0
FE_avg = np.mean(FE_dyn[mask_aktif]) if np.any(mask_aktif) else 0

print("=" * 68)
print(" SIMULASI HARIAN PV-EC  —  MODEL FISIKA LENGKAP")
print("=" * 68)
print(f" Panel {LUAS_PANEL:.0f} m² | {N_SEL} sel × {A_ELEKTRODA:.0f} cm² elektroda")
print(f" η_PV ref = {ETA_PV_REF*100:.0f}% | β = {BETA_TEMP*100:.1f}%/°C")
print("-" * 68)
print(" TEGANGAN SEL (rata-rata siang)")
print(f"   E_rev (Nernst)        : {np.mean(E_rev[mask_aktif]):.3f} V")
print(f"   η_OER (Tafel anoda)   : {eta_oer_avg:.3f} V")
print(f"   η_CO2RR (Tafel katoda): {eta_co2rr_avg:.3f} V")
print(f"   V_ohm internal        : {np.mean(v_ohm_int[mask_aktif]):.3f} V")
print(f"   V_sel total           : {V_sel_avg:.3f} V")
print("-" * 68)
print(" ALIRAN ENERGI")
print(f"   Surya datang          : {E_surya:7.2f} kWh  (100.0%)")
print(f"   → Listrik PV          : {E_pv:7.2f} kWh  ({pct_pv:.1f}%)")
print(f"   → Tiba di reaktor     : {E_reaktor:7.2f} kWh  ({pct_reak:.1f}%)")
print(f"   → Energi kimia        : {E_kimia:7.2f} kWh  ({pct_kim:.1f}%)")
print("-" * 68)
print(" EFISIENSI (Pers. 1.6)")
print(f"   η_PV rata-rata        : {eta_pv_avg*100:5.1f}%  (batas SQ {SQ_LIMIT*100:.0f}%)")
print(f"   η_EC rata-rata        : {eta_EC_avg*100:5.1f}%")
print(f"   η_total               : {eta_total*100:5.1f}%")
print(f"   FE rata-rata          : {FE_avg*100:5.1f}%  (transpor massa)")
print("-" * 68)
print(" PRODUKSI")
print(f"   O₂  dihasilkan        : {g_O2:7.1f} g  ({mol_O2:.1f} mol | {L_O2:.0f} L)")
print(f"   CH₃OH (via CO₂RR)     : CO₂ ditangkap {g_CO2:7.1f} g  ({mol_CO2:.1f} mol)")
print(f"   ≈ {setara_pohon:.1f} pohon  |  ≈ napas {setara_manusia:.1f} orang")
print("-" * 68)
print(" SELEKTIVITAS KATODA  (CO₂RR vs HER)")
print(f"   Porsi metanol/H₂      : {PHI_CO2RR*100:.0f}% CH₃OH | {(1-PHI_CO2RR)*100:.0f}% H₂")
print(f"   H₂ produk samping     : {g_H2:7.1f} g  ({mol_H2:.1f} mol)  ← juga solar fuel")
print("-" * 68)
print(" BEBAN REGENERASI DAC  (kalsinasi ~900°C — Keith 2018)")
print(f"   Energi panas regen    : {E_regen_th:6.2f} kWh  (dari surya termal terpisah)")
print(f"   Listrik bantu DAC     : {E_dac_el:6.2f} kWh")
print(f"   Luas kolektor termal  : {luas_termal:6.1f} m²  (TAMBAHAN di luar {LUAS_PANEL:.0f} m² PV)")
print(f"   η_NET (PV + DAC)      : {eta_net*100:5.1f}%  ← vs η_total {eta_total*100:.1f}% (tanpa DAC)")
print("-" * 68)
print(" NERACA AIR  (Prats-Salvado 2024)")
print(f"   Air pemecahan (OER)   : {air_OER_mL:7.0f} mL")
print(f"   Air DAC (evaporasi)   : {air_DAC_mL:7.0f} mL  (4,7 kg/kg CO₂)")
print(f"   Total kebutuhan air   : {air_total_L:7.2f} L/hari")
print("=" * 68)

# ===== 10. GRAFIK (6 file PNG, 300 dpi) =====
plt.rcParams.update({"font.size": 11, "axes.titleweight": "bold",
                     "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 110})
C_SUN = "#F9A825"; C_PV = "#1565C0"; C_RE = "#2E7D32"
C_RUGI = "#C62828"; C_O2 = "#0277BD"; C_CO2 = "#6A1B9A"

# --- 1. Profil Daya + MPPT + efek suhu ---
fig1, (ax1a, ax1b) = plt.subplots(2, 1, figsize=(9, 7), height_ratios=[3, 1],
                                   sharex=True)
ax1a.fill_between(t, G*LUAS_PANEL, color=C_SUN, alpha=.25, label="Surya datang")
ax1a.plot(t, P_pv, color=C_PV, lw=2.2, label="PV + MPPT")
ax1a.plot(t, P_tanpa_mppt, color=C_RUGI, lw=1.5, ls="--", label="PV tanpa MPPT")
ax1a.fill_between(t, P_tanpa_mppt, P_pv, color=C_PV, alpha=.10)
ax1a.set_ylabel("Daya [W]"); ax1a.set_title("① Profil Daya & Suhu Panel")
ax1a.legend(fontsize=9)
ax1b.plot(t, T_cell, color=C_RUGI, lw=1.8, label="T sel")
ax1b.plot(t, T_amb, color=C_SUN, lw=1.2, ls="--", label="T ambient")
ax1b.plot(t, eta_pv*100, color=C_PV, lw=1.8, label="η_PV [%]")
ax1b.set_xlabel("Waktu [jam]"); ax1b.set_ylabel("°C  /  %")
ax1b.set_xlim(0, 24); ax1b.set_xticks(range(0, 25, 3))
ax1b.legend(fontsize=8, ncol=3); fig1.tight_layout()
fig1.savefig("1_profil_daya.png", dpi=300, bbox_inches="tight")

# --- 2. Tegangan sel & komponen overpotensial ---
fig2, ax2 = plt.subplots(figsize=(9, 5.5))
ax2.fill_between(t, 0, np.where(mask_aktif, E_rev, 0),
                 color="#4CAF50", alpha=.4, label="E_rev (Nernst)")
ax2.fill_between(t, np.where(mask_aktif, E_rev, 0),
                 np.where(mask_aktif, E_rev + eta_oer, 0),
                 color=C_RUGI, alpha=.4, label="η_OER (Tafel)")
ax2.fill_between(t, np.where(mask_aktif, E_rev + eta_oer, 0),
                 np.where(mask_aktif, E_rev + eta_oer + eta_co2rr, 0),
                 color="#FF9800", alpha=.4, label="η_CO₂RR (Tafel)")
ax2.fill_between(t, np.where(mask_aktif, E_rev + eta_oer + eta_co2rr, 0),
                 np.where(mask_aktif, V_sel, 0),
                 color="#9E9E9E", alpha=.4, label="V_ohm (I·R)")
ax2.plot(t, np.where(mask_aktif, V_sel, np.nan), color="black", lw=1.5,
         label=f"V_sel total ({V_sel_avg:.2f} V avg)")
ax2.axhline(E_REV_STD, color="#4CAF50", ls=":", lw=1, alpha=.6)
ax2.set_xlabel("Waktu [jam]"); ax2.set_ylabel("Tegangan [V]")
ax2.set_title("② Dekomposisi Tegangan Sel — Nernst + Tafel + Ohmik")
ax2.set_xlim(0, 24); ax2.set_xticks(range(0, 25, 3))
ax2.legend(fontsize=8, loc="upper right"); fig2.tight_layout()
fig2.savefig("2_tegangan_sel.png", dpi=300, bbox_inches="tight")

# --- 3. Sankey aliran energi ---
fig3 = plt.figure(figsize=(9, 5.5))
ax3 = fig3.add_subplot(1, 1, 1, xticks=[], yticks=[])
ax3.set_title("③ Aliran & Kehilangan Energi  (per 100% surya datang)")
sk = Sankey(ax=ax3, unit=None, scale=1/100, gap=0.45, head_angle=120, shoulder=0.02)
sk.add(flows=[100, -pct_rugi_pv, -pct_rugi_ohm, -pct_rugi_ec, -pct_kim],
       labels=["Surya\nmasuk",
               f"Rugi PV\n{pct_rugi_pv:.0f}%",
               f"Rugi ohmik\n{pct_rugi_ohm:.1f}%",
               f"Rugi EC\n{pct_rugi_ec:.1f}%",
               f"Kimia\n{pct_kim:.1f}%"],
       orientations=[0, 1, 1, 1, 0],
       pathlengths=[.4, .35, .30, .55, .50],
       facecolor=C_PV, edgecolor="#0D47A1")
for d in sk.finish():
    for txt in d.texts: txt.set_fontsize(8.5)
fig3.tight_layout()
fig3.savefig("3_sankey_energi.png", dpi=300, bbox_inches="tight")

# --- 4. Bar efisiensi ---
fig4, ax4 = plt.subplots(figsize=(7, 5))
lbl = ["η_PV\n(avg)", "η_EC\n(avg)", "η_total\n(PV×EC)", "FE\n(Faraday)"]
val = [eta_pv_avg*100, eta_EC_avg*100, eta_total*100, FE_avg*100]
clr = [C_PV, C_RE, "#37474F", "#FF6F00"]
bar = ax4.bar(lbl, val, color=clr, width=0.55)
ax4.bar_label(bar, fmt="%.1f%%", padding=3, fontweight="bold")
ax4.axhline(SQ_LIMIT*100, color=C_RUGI, ls="--", lw=1.5)
ax4.text(3.4, SQ_LIMIT*100+0.8, f"Batas SQ ({SQ_LIMIT*100:.0f}%)",
         color=C_RUGI, ha="right", fontsize=9, fontweight="bold")
ax4.set_ylabel("Efisiensi [%]"); ax4.set_ylim(0, 100)
ax4.set_title("④ Efisiensi Konversi Sistem PV-EC"); fig4.tight_layout()
fig4.savefig("4_efisiensi.png", dpi=300, bbox_inches="tight")

# --- 5. Produksi kumulatif ---
fig5, ax5 = plt.subplots(figsize=(9, 5))
ax5.plot(t, kum_g_O2, color=C_O2, lw=2.4, label="O₂ dihasilkan")
ax5.plot(t, kum_g_CO2, color=C_CO2, lw=2.4, label="CO₂ ditangkap")
ax5.fill_between(t, 0, kum_g_O2, color=C_O2, alpha=.08)
if g_O2 > 0:
    ax5.annotate(f"{g_O2:.0f} g O₂\n≈ {setara_pohon:.1f} pohon",
                 xy=(22, kum_g_O2[-60]), xytext=(12, g_O2*.75),
                 arrowprops=dict(arrowstyle="->", color=C_O2),
                 fontsize=9, color=C_O2, fontweight="bold")
    ax5.annotate(f"{g_CO2:.0f} g CO₂\n≈ napas {setara_manusia:.1f} orang",
                 xy=(20, kum_g_CO2[-240]), xytext=(13, g_CO2*.4),
                 arrowprops=dict(arrowstyle="->", color=C_CO2),
                 fontsize=9, color=C_CO2, fontweight="bold")
ax5.set_xlabel("Waktu [jam]"); ax5.set_ylabel("Massa kumulatif [g]")
ax5.set_title("⑤ Produksi Kumulatif O₂ & CO₂"); ax5.legend(fontsize=9)
ax5.set_xlim(0, 24); ax5.set_xticks(range(0, 25, 3)); fig5.tight_layout()
fig5.savefig("5_produksi.png", dpi=300, bbox_inches="tight")

# --- 6. FE dinamis & laju DAC ---
fig6, (ax6a, ax6b) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax6a.plot(t, FE_dyn*100, color="#FF6F00", lw=2, label="FE(j) dinamis")
ax6a.axhline(FE_MAX*100, color="#FF6F00", ls=":", lw=1, alpha=.5)
ax6a.set_ylabel("FE [%]"); ax6a.set_title("⑥ Efisiensi Faraday & Laju DAC")
ax6a.legend(fontsize=9)
ax6b.plot(t, laju_CO2_max*1e6, color=C_CO2, lw=1.8, label="Kebutuhan CO₂ reaktor")
ax6b.plot(t, r_DAC*1e6, color=C_RE, lw=1.8, ls="--", label="Suplai DAC")
ax6b.fill_between(t, laju_CO2_max*1e6, r_DAC*1e6,
                  where=laju_CO2_max > r_DAC,
                  color=C_RUGI, alpha=.2, label="Defisit DAC")
ax6b.set_xlabel("Waktu [jam]"); ax6b.set_ylabel("Laju [μmol/s]")
ax6b.set_xlim(0, 24); ax6b.set_xticks(range(0, 25, 3))
ax6b.legend(fontsize=8); fig6.tight_layout()
fig6.savefig("6_faraday_dac.png", dpi=300, bbox_inches="tight")

# --- 7. Neraca lengkap: produk, beban energi DAC, air ---
fig7, (ax7a, ax7b, ax7c) = plt.subplots(1, 3, figsize=(13, 4.5))

# (a) Produk harian — O2, CH3OH (dari CO2), H2
prod_lbl = ["O₂", "CH₃OH\n(via CO₂)", "H₂\n(HER)"]
prod_val = [g_O2, g_CO2, g_H2]   # gram (CO2 ~ proxy metanol via CO2RR)
prod_clr = [C_O2, C_CO2, "#00897B"]
b7 = ax7a.bar(prod_lbl, prod_val, color=prod_clr, width=0.6)
ax7a.bar_label(b7, fmt="%.0f g", padding=3, fontweight="bold", fontsize=9)
ax7a.set_ylabel("Massa [g/hari]")
ax7a.set_title("⑦a Produk Harian\n(selektivitas katoda)")
ax7a.set_ylim(0, max(prod_val) * 1.25)

# (b) Beban energi — kimia berguna vs regenerasi DAC
en_lbl = ["Energi\nkimia", "Regen DAC\n(panas)", "Listrik\nDAC"]
en_val = [E_kimia, E_regen_th, E_dac_el]
en_clr = [C_RE, C_RUGI, "#FF9800"]
b8 = ax7b.bar(en_lbl, en_val, color=en_clr, width=0.6)
ax7b.bar_label(b8, fmt="%.1f", padding=3, fontweight="bold", fontsize=9)
ax7b.set_ylabel("Energi [kWh/hari]")
ax7b.set_title(f"⑦b Beban Energi DAC\nη_net {eta_net*100:.1f}% vs η_total {eta_total*100:.1f}%")

# (c) Neraca air — OER vs DAC
air_lbl = ["Pemecahan\n(OER)", "DAC\n(evaporasi)"]
air_val = [air_OER_mL / 1000, air_DAC_mL / 1000]   # liter
b9 = ax7c.bar(air_lbl, air_val, color=["#0277BD", "#C62828"], width=0.6)
ax7c.bar_label(b9, fmt="%.1f L", padding=3, fontweight="bold", fontsize=9)
ax7c.set_ylabel("Air [L/hari]")
ax7c.set_title(f"⑦c Neraca Air\nTotal {air_total_L:.1f} L/hari")
fig7.tight_layout()
fig7.savefig("7_neraca_lengkap.png", dpi=300, bbox_inches="tight")

print(f"\n7 grafik tersimpan: 1–7 PNG (300 dpi)")

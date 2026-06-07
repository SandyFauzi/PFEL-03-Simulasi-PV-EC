# -*- coding: utf-8 -*-
"""
============================================================================
 SIMULASI SISTEM PV-EC  —  Model Fisika Lengkap (Dashboard Harian + Tahunan)
 Integrasi Panel Surya + Carbon Capture + Artificial Photosynthesis
----------------------------------------------------------------------------
 PFEL Kelompok 3
============================================================================
"""
import sys, numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
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
PHI_CO2RR = 0.60         # Fraksi arus faradaik -> CH3OH; sisanya -> H2  [-]
Z_H2      = 2            # Elektron per molekul H2 (2H+ + 2e- -> H2)

# ===== 7c. ENERGI REGENERASI DAC — kalsinasi (Keith 2018) =====
Q_REGEN_TH   = 1.46      # Panas regenerasi [kWh_th/kg CO2] (~5.25 GJ/t, Keith 2018)
E_DAC_ELEK   = 0.37      # Listrik bantu DAC (kontaktor+kompresi) [kWh/kg CO2] (~366 kWh/t)
ETA_SOLAR_TH = 0.50      # Efisiensi kolektor surya termal (untuk hitung luas) [-]

# ===== 7d. NERACA AIR (Prats-Salvado 2024) =====
H2O_DAC = 4.7            # Konsumsi air DAC [kg H2O / kg CO2] (evaporasi L-DAC)

# Acuan konteks
O2_PER_POHON  = 274.0    # g O2/hari per pohon
CO2_PER_ORANG = 1000.0   # g CO2/hari per manusia
O2_PER_POHON_TAHUN = 100_000.0 # g O2 / pohon per tahun

# ===== 8. SUMBU WAKTU (1 menit resolusi, 24 jam) =====
t    = np.linspace(0.0, 24.0, 24*60+1)
dt_s = (t[1] - t[0]) * 3600.0

# ====================================================================
# [A] SIMULASI HARIAN (Fokus Detil Proses 1 Hari)
# ====================================================================
siang  = (t >= JAM_TERBIT) & (t <= JAM_TERBENAM)
durasi = JAM_TERBENAM - JAM_TERBIT
G = np.where(siang, G_PEAK * np.sin(np.pi*(t - JAM_TERBIT)/durasi), 0.0)
G = np.clip(G, 0.0, None)

T_amb = T_AMB_MIN + (T_AMB_MAX - T_AMB_MIN) * np.sin(
    np.clip(np.pi*(t - 5.0)/18.0, 0, np.pi))
T_amb = np.clip(T_amb, T_AMB_MIN, T_AMB_MAX)

T_cell = T_amb + (NOCT - 20.0) * G / 800.0

eta_pv = ETA_PV_REF * (1.0 - BETA_TEMP * (T_cell - T_REF_PV))
eta_pv = np.clip(eta_pv, 0.0, SQ_LIMIT)

P_pv = eta_pv * LUAS_PANEL * G                   # daya PV [W]
P_tanpa_mppt = P_pv * (1.0 - MISMATCH)

I_bus     = P_pv / V_BUS
P_ohmik   = I_bus**2 * R_KABEL
P_reaktor = np.clip(P_pv - P_ohmik, 0.0, None)

T_reak_K = (T_amb + 5.0) + 273.15
E_rev = E_REV_STD - 0.000846 * (T_reak_K - 298.15)
I_reak = np.where(P_reaktor > 0, P_reaktor / (N_SEL * 2.0), 0.0)

for _ in range(60):
    j = I_reak / A_ELEKTRODA
    j_safe = np.maximum(j, 1e-12)
    eta_oer = R_GAS*T_reak_K/(ALPHA_OER*F_CONST) * np.log(np.maximum(j_safe/J0_OER, 1.0))
    eta_co2rr = R_GAS*T_reak_K/(ALPHA_CO2RR*F_CONST) * np.log(np.maximum(j_safe/J0_CO2RR, 1.0))
    v_ohm_int = j_safe * R_ASR
    V_sel = E_rev + eta_oer + eta_co2rr + v_ohm_int
    V_stack = N_SEL * V_sel
    I_new = np.where(V_stack > 0, P_reaktor / V_stack, 0.0)
    I_new = np.where(P_reaktor > 0, I_new, 0.0)
    if np.max(np.abs(I_new - I_reak)) < 1e-9: break
    I_reak = I_new

j_final = I_reak / A_ELEKTRODA

FE_dyn = FE_MAX * np.sqrt(np.maximum(1.0 - j_final/J_LIM, 0.0))
FE_dyn = np.where(P_reaktor > 0, FE_dyn, 0.0)

FE_CO2RR = FE_dyn * PHI_CO2RR
FE_HER   = FE_dyn * (1.0 - PHI_CO2RR)

C_CO2_udara = CO2_PPM * 1e-6 * P_ATM / (R_GAS * (T_amb + 273.15))
r_DAC = K_ABS * A_KONTAKTOR * C_CO2_udara

laju_O2_max  = N_SEL * FE_dyn   * I_reak / (Z_O2   * F_CONST)
laju_CO2_max = N_SEL * FE_CO2RR * I_reak / (Z_CO2  * F_CONST)
laju_H2_max  = N_SEL * FE_HER   * I_reak / (Z_H2   * F_CONST)

rasio_DAC = np.where(laju_CO2_max > 0,
                     np.minimum(np.divide(r_DAC, laju_CO2_max,
                                out=np.ones_like(r_DAC), where=laju_CO2_max>0), 1.0), 1.0)
laju_CO2 = laju_CO2_max * rasio_DAC
laju_H2  = laju_H2_max + laju_CO2_max * (1.0 - rasio_DAC) * (Z_CO2 / Z_H2)
laju_O2  = laju_O2_max

kum_mol_O2  = np.cumsum(laju_O2)  * dt_s
kum_mol_CO2 = np.cumsum(laju_CO2) * dt_s
kum_mol_H2  = np.cumsum(laju_H2)  * dt_s
kum_g_O2    = kum_mol_O2  * M_O2
kum_g_CO2   = kum_mol_CO2 * M_CO2
kum_g_H2    = kum_mol_H2  * M_H2

def integral_kWh(P): return np.sum(P) * dt_s / 3.6e6

E_surya   = integral_kWh(G * LUAS_PANEL)
E_pv      = integral_kWh(P_pv)
E_ohm_kb  = integral_kWh(P_ohmik)
E_reaktor = integral_kWh(P_reaktor)

E_kimia = N_SEL * np.sum(E_rev * I_reak * FE_dyn * rasio_DAC) * dt_s / 3.6e6

eta_pv_avg = E_pv / E_surya if E_surya > 0 else 0
eta_EC_avg = E_kimia / E_reaktor if E_reaktor > 0 else 0
eta_total  = E_kimia / E_surya if E_surya > 0 else 0

g_O2  = kum_g_O2[-1];  g_CO2 = kum_g_CO2[-1];  g_H2 = kum_g_H2[-1]
mol_O2 = kum_mol_O2[-1]; mol_CO2 = kum_mol_CO2[-1]; mol_H2 = kum_mol_H2[-1]
L_O2 = mol_O2 * VM_STP
setara_pohon   = g_O2  / O2_PER_POHON
setara_manusia = g_CO2 / CO2_PER_ORANG

air_OER_mL = mol_O2 * 2.0 * M_H2O
air_DAC_mL = (g_CO2 / 1000.0) * H2O_DAC * 1000.0
air_total_L = (air_OER_mL + air_DAC_mL) / 1000.0

E_regen_th  = (g_CO2 / 1000.0) * Q_REGEN_TH
E_dac_el    = (g_CO2 / 1000.0) * E_DAC_ELEK
E_solar_th  = E_regen_th / ETA_SOLAR_TH
eta_net     = E_kimia / (E_surya + E_solar_th) if (E_surya + E_solar_th) > 0 else 0.0

pct = lambda x: x / E_surya * 100 if E_surya > 0 else 0
pct_pv  = pct(E_pv); pct_reak = pct(E_reaktor); pct_kim = pct(E_kimia)
pct_rugi_pv = 100 - pct_pv
pct_rugi_ohm = pct_pv - pct_reak
pct_rugi_ec = pct_reak - pct_kim

mask_aktif = P_reaktor > 10.0
eta_oer_avg = np.mean(eta_oer[mask_aktif]) if np.any(mask_aktif) else 0
eta_co2rr_avg = np.mean(eta_co2rr[mask_aktif]) if np.any(mask_aktif) else 0
V_sel_avg = np.mean(V_sel[mask_aktif]) if np.any(mask_aktif) else 0
FE_avg = np.mean(FE_dyn[mask_aktif]) if np.any(mask_aktif) else 0

# ====================================================================
# [B] SIMULASI TAHUNAN (Loop 365 Hari)
# ====================================================================
CERAH_RATA = 0.70; CERAH_AMPL = 0.16; DOY_PUNCAK = 227; SEED = 42
T_AMB_MEAN_KEMARAU = 30.0; T_AMB_MEAN_HUJAN = 27.0
rng = np.random.default_rng(SEED)
doy = np.arange(1, 366)
cerah_musim = CERAH_RATA + CERAH_AMPL * np.cos(2*np.pi*(doy - DOY_PUNCAK)/365.0)
basah = (CERAH_RATA + CERAH_AMPL - cerah_musim) / (2*CERAH_AMPL)
sigma = 0.07 + 0.10 * basah
derau = rng.normal(1.0, sigma)
cerah = np.clip(cerah_musim * derau, 0.20, 1.0)
T_amb_hari = T_AMB_MEAN_HUJAN + (T_AMB_MEAN_KEMARAU - T_AMB_MEAN_HUJAN) * (1 - basah)

G_base = np.where(siang, G_PEAK * np.sin(np.pi*(t - JAM_TERBIT)/(JAM_TERBENAM - JAM_TERBIT)), 0.0)

def jalankan_hari(s, T_amb_mean):
    G_h = s * G_base
    T_amp = 4.0
    T_amb_h = T_amb_mean - T_amp + 2*T_amp * np.sin(np.clip(np.pi*(t - 5.0)/18.0, 0, np.pi))
    T_cell_h = T_amb_h + (NOCT - 20.0) * G_h / 800.0
    eta_pv_h = ETA_PV_REF * (1.0 - BETA_TEMP * (T_cell_h - T_REF_PV))
    eta_pv_h = np.clip(eta_pv_h, 0.0, 0.33)
    P_pv_h = eta_pv_h * LUAS_PANEL * G_h
    I_bus_h = P_pv_h / V_BUS
    P_ohmik_h = I_bus_h**2 * R_KABEL
    P_reak_h = np.clip(P_pv_h - P_ohmik_h, 0.0, None)
    T_rK_h = (T_amb_h + 5.0) + 273.15
    E_rev_h = E_REV_STD - 0.000846 * (T_rK_h - 298.15)
    I_r_h = np.where(P_reak_h > 0, P_reak_h / (N_SEL * 2.0), 0.0)
    for _ in range(60):
        j_h = I_r_h / A_ELEKTRODA
        js_h = np.maximum(j_h, 1e-12)
        eta_a_h = R_GAS*T_rK_h/(ALPHA_OER*F_CONST) * np.log(np.maximum(js_h/J0_OER, 1.0))
        eta_c_h = R_GAS*T_rK_h/(ALPHA_CO2RR*F_CONST) * np.log(np.maximum(js_h/J0_CO2RR, 1.0))
        V_s_h = E_rev_h + eta_a_h + eta_c_h + js_h*R_ASR
        V_st_h = N_SEL * V_s_h
        I_new_h = np.where(V_st_h > 0, P_reak_h / V_st_h, 0.0)
        I_new_h = np.where(P_reak_h > 0, I_new_h, 0.0)
        if np.max(np.abs(I_new_h - I_r_h)) < 1e-9: break
        I_r_h = I_new_h
    j_f_h = I_r_h / A_ELEKTRODA
    FE_d_h = FE_MAX * np.sqrt(np.maximum(1.0 - j_f_h/J_LIM, 0.0))
    FE_d_h = np.where(P_reak_h > 0, FE_d_h, 0.0)
    C_co2_h = CO2_PPM * 1e-6 * P_ATM / (R_GAS * (T_amb_h + 273.15))
    r_dac_h = K_ABS * A_KONTAKTOR * C_co2_h
    FE_co2rr_h = FE_d_h * PHI_CO2RR
    FE_her_h   = FE_d_h * (1.0 - PHI_CO2RR)
    l_o2_h  = N_SEL * FE_d_h     * I_r_h / (Z_O2   * F_CONST)
    l_co2_h = N_SEL * FE_co2rr_h * I_r_h / (Z_CO2  * F_CONST)
    l_h2_h  = N_SEL * FE_her_h   * I_r_h / (Z_H2   * F_CONST)
    rdac_h = np.where(l_co2_h > 0, np.minimum(np.divide(r_dac_h, l_co2_h, out=np.ones_like(r_dac_h), where=l_co2_h>0), 1.0), 1.0)
    l_co2_f_h = l_co2_h * rdac_h
    l_h2_f_h  = l_h2_h + l_co2_h * (1.0 - rdac_h) * (Z_CO2 / Z_H2)
    mol_O2_h  = np.sum(l_o2_h)    * dt_s
    mol_CO2_h = np.sum(l_co2_f_h) * dt_s
    return mol_O2_h, mol_CO2_h, np.sum(G_h * LUAS_PANEL) * dt_s / 3.6e6

mol_O2_hari = np.zeros(365); mol_CO2_hari = np.zeros(365); E_surya_th = np.zeros(365)
for d in range(365):
    mol_O2_hari[d], mol_CO2_hari[d], E_surya_th[d] = jalankan_hari(cerah[d], T_amb_hari[d])

g_O2_hari  = mol_O2_hari  * M_O2
g_CO2_hari = mol_CO2_hari * M_CO2
H_harian = E_surya_th / LUAS_PANEL

hpb = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
ab = np.concatenate([[0], np.cumsum(hpb)])
nb = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Ags","Sep","Okt","Nov","Des"]
def per_bulan(a): return np.array([a[ab[m]:ab[m+1]].sum() for m in range(12)])
O2_bln  = per_bulan(g_O2_hari)/1000
CO2_bln = per_bulan(g_CO2_hari)/1000
H_bln   = np.array([H_harian[ab[m]:ab[m+1]].mean() for m in range(12)])

O2_th_tot = g_O2_hari.sum()/1000; CO2_th_tot = g_CO2_hari.sum()/1000
pohon_th = (O2_th_tot*1000) / O2_PER_POHON_TAHUN


print("Menyiapkan Dashboard Simulasi Harian + Tahunan... (Mohon tunggu)")

# ====================================================================
# [C] GRAFIK DASHBOARD (1 CANVAS GABUNGAN)
# ====================================================================
plt.rcParams.update({"font.size": 10, "axes.titleweight": "bold",
                     "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 100})
C_SUN = "#F9A825"; C_PV = "#1565C0"; C_RE = "#2E7D32"
C_RUGI = "#C62828"; C_O2 = "#0277BD"; C_CO2 = "#6A1B9A"

# Buat Figure besar: 7 Baris x 4 Kolom
fig = plt.figure(figsize=(20, 26))
fig.suptitle("Dashboard Komprehensif Simulasi PV-EC: Dinamika Harian & Kinerja Tahunan", 
             fontsize=20, fontweight="bold", y=0.98)

gs = fig.add_gridspec(7, 4, height_ratios=[1.5, 1.2, 1.2, 1.8, 1.6, 1.6, 1.6], hspace=0.38, wspace=0.3)

# ---------------------------------------------
# BAGIAN HARIAN (Baris 0 - 4)
# ---------------------------------------------
ax1a = fig.add_subplot(gs[0, 0:2])
ax1a.fill_between(t, G*LUAS_PANEL, color=C_SUN, alpha=.25, label="Surya datang")
ax1a.plot(t, P_pv, color=C_PV, lw=2.2, label="PV + MPPT")
ax1a.plot(t, P_tanpa_mppt, color=C_RUGI, lw=1.5, ls="--", label="PV tanpa MPPT")
ax1a.fill_between(t, P_tanpa_mppt, P_pv, color=C_PV, alpha=.10)
ax1a.set_ylabel("Daya [W]"); ax1a.set_title("1. Profil Daya Panel (Harian)")
ax1a.set_xlim(0, 24)
ax1a.legend(fontsize=9)

ax1b = fig.add_subplot(gs[1, 0:2], sharex=ax1a)
ax1b.plot(t, T_cell, color=C_RUGI, lw=1.8, label="T sel")
ax1b.plot(t, T_amb, color=C_SUN, lw=1.2, ls="--", label="T ambient")
ax1b.plot(t, eta_pv*100, color=C_PV, lw=1.8, label="η_PV [%]")
ax1b.set_ylabel("°C  /  %"); ax1b.set_title("2. Temperatur & Efisiensi PV (Harian)")
ax1b.legend(fontsize=8, ncol=3)

ax2 = fig.add_subplot(gs[0, 2:4], sharex=ax1a)
ax2.fill_between(t, 0, np.where(mask_aktif, E_rev, 0), color="#4CAF50", alpha=.4, label="E_rev (Nernst)")
ax2.fill_between(t, np.where(mask_aktif, E_rev, 0), np.where(mask_aktif, E_rev + eta_oer, 0), color=C_RUGI, alpha=.4, label="η_OER (Tafel)")
ax2.fill_between(t, np.where(mask_aktif, E_rev + eta_oer, 0), np.where(mask_aktif, E_rev + eta_oer + eta_co2rr, 0), color="#FF9800", alpha=.4, label="η_CO₂RR (Tafel)")
ax2.fill_between(t, np.where(mask_aktif, E_rev + eta_oer + eta_co2rr, 0), np.where(mask_aktif, V_sel, 0), color="#9E9E9E", alpha=.4, label="V_ohm (I·R)")
ax2.plot(t, np.where(mask_aktif, V_sel, np.nan), color="black", lw=1.5, label=f"V_sel total ({V_sel_avg:.2f} V avg)")
ax2.axhline(E_REV_STD, color="#4CAF50", ls=":", lw=1, alpha=.6)
ax2.set_ylabel("Tegangan [V]"); ax2.set_title("3. Dekomposisi Tegangan Sel (Harian)")
ax2.legend(fontsize=8, loc="upper right")

ax5 = fig.add_subplot(gs[1, 2:4], sharex=ax1a)
ax5.plot(t, kum_g_O2, color=C_O2, lw=2.4, label="O₂ dihasilkan")
ax5.plot(t, kum_g_CO2, color=C_CO2, lw=2.4, label="CO₂ ditangkap")
ax5.fill_between(t, 0, kum_g_O2, color=C_O2, alpha=.08)
if g_O2 > 0:
    ax5.annotate(f"{g_O2:.0f} g O₂", xy=(22, kum_g_O2[-60]), xytext=(12, g_O2*.75), arrowprops=dict(arrowstyle="->", color=C_O2), fontsize=9, color=C_O2, fontweight="bold")
    ax5.annotate(f"{g_CO2:.0f} g CO₂", xy=(20, kum_g_CO2[-240]), xytext=(13, g_CO2*.4), arrowprops=dict(arrowstyle="->", color=C_CO2), fontsize=9, color=C_CO2, fontweight="bold")
ax5.set_ylabel("Massa [g]"); ax5.set_title("4. Produksi Kumulatif (Harian)")
ax5.legend(fontsize=9)

ax6a = fig.add_subplot(gs[2, 0:2], sharex=ax1a)
ax6a.plot(t, FE_dyn*100, color="#FF6F00", lw=2, label="FE(j) dinamis")
ax6a.axhline(FE_MAX*100, color="#FF6F00", ls=":", lw=1, alpha=.5)
ax6a.set_xlabel("Waktu [jam]"); ax6a.set_ylabel("FE [%]")
ax6a.set_title("5. Efisiensi Faraday (Harian)")
ax6a.set_xticks(range(0, 25, 3))
ax6a.legend(fontsize=9)

ax6b = fig.add_subplot(gs[2, 2:4], sharex=ax1a)
ax6b.plot(t, laju_CO2_max*1e6, color=C_CO2, lw=1.8, label="Kebutuhan CO₂ reaktor")
ax6b.plot(t, r_DAC*1e6, color=C_RE, lw=1.8, ls="--", label="Suplai DAC")
ax6b.fill_between(t, laju_CO2_max*1e6, r_DAC*1e6, where=laju_CO2_max > r_DAC, color=C_RUGI, alpha=.2, label="Defisit DAC")
ax6b.set_xlabel("Waktu [jam]"); ax6b.set_ylabel("Laju [μmol/s]")
ax6b.set_title("6. Kebutuhan vs Suplai CO₂ DAC (Harian)")
ax6b.set_xticks(range(0, 25, 3))
ax6b.legend(fontsize=8)

ax3 = fig.add_subplot(gs[3:5, 0:2], xticks=[], yticks=[])
ax3.set_title("7. Aliran & Kehilangan Energi (Harian)", pad=15)
sk = Sankey(ax=ax3, unit=None, scale=1/100, gap=0.45, head_angle=120, shoulder=0.02)
sk.add(flows=[100, -pct_rugi_pv, -pct_rugi_ohm, -pct_rugi_ec, -pct_kim],
       labels=["Surya\nmasuk", f"Rugi PV\n{pct_rugi_pv:.0f}%", f"Rugi ohmik\n{pct_rugi_ohm:.1f}%", f"Rugi EC\n{pct_rugi_ec:.1f}%", f"Kimia\n{pct_kim:.1f}%"],
       orientations=[0, 1, 1, 1, 0], pathlengths=[.4, .35, .30, .55, .50], facecolor=C_PV, edgecolor="#0D47A1")
for d in sk.finish():
    for txt in d.texts: txt.set_fontsize(9)

ax4 = fig.add_subplot(gs[3, 2])
lbl = ["η_PV\n(avg)", "η_EC\n(avg)", "η_total", "FE\n(Faraday)"]
val = [eta_pv_avg*100, eta_EC_avg*100, eta_total*100, FE_avg*100]
clr = [C_PV, C_RE, "#37474F", "#FF6F00"]
bar = ax4.bar(lbl, val, color=clr, width=0.55)
ax4.bar_label(bar, fmt="%.1f%%", padding=3, fontweight="bold")
ax4.axhline(SQ_LIMIT*100, color=C_RUGI, ls="--", lw=1.5)
ax4.text(3.4, SQ_LIMIT*100+0.8, f"Batas SQ ({SQ_LIMIT*100:.0f}%)", color=C_RUGI, ha="right", fontsize=9, fontweight="bold")
ax4.set_ylabel("Efisiensi [%]"); ax4.set_ylim(0, 100); ax4.set_title("8. Efisiensi Konversi")

ax7a = fig.add_subplot(gs[3, 3])
prod_lbl = ["O₂", "CH₃OH", "H₂"]
prod_val = [g_O2, g_CO2, g_H2]
b7 = ax7a.bar(prod_lbl, prod_val, color=[C_O2, C_CO2, "#00897B"], width=0.6)
ax7a.bar_label(b7, fmt="%.0f g", padding=3, fontweight="bold", fontsize=9)
ax7a.set_ylabel("Massa [g/hari]"); ax7a.set_title("9. Produk Harian")
ax7a.set_ylim(0, max(prod_val) * 1.25)

ax7b = fig.add_subplot(gs[4, 2])
en_lbl = ["E_kimia", "Regen\n(panas)", "Listrik\nDAC"]
en_val = [E_kimia, E_regen_th, E_dac_el]
b8 = ax7b.bar(en_lbl, en_val, color=[C_RE, C_RUGI, "#FF9800"], width=0.6)
ax7b.bar_label(b8, fmt="%.1f", padding=3, fontweight="bold", fontsize=9)
ax7b.set_ylabel("Energi [kWh/hari]"); ax7b.set_title(f"10. Beban Energi DAC (η_net {eta_net*100:.1f}%)")

ax7c = fig.add_subplot(gs[4, 3])
air_lbl = ["OER", "DAC\n(evap)"]
air_val = [air_OER_mL / 1000, air_DAC_mL / 1000]
b9 = ax7c.bar(air_lbl, air_val, color=["#0277BD", "#C62828"], width=0.6)
ax7c.bar_label(b9, fmt="%.1f L", padding=3, fontweight="bold", fontsize=9)
ax7c.set_ylabel("Air [L/hari]"); ax7c.set_title(f"11. Neraca Air (Total {air_total_L:.1f} L)")


# ---------------------------------------------
# BAGIAN TAHUNAN (Baris 5 & 6)
# ---------------------------------------------
C_KM="#FFE0B2"; C_HJ="#B3E5FC"
xb = np.arange(12)

# Tahunan 1: Iradiasi (Baris 5, full width)
ax8 = fig.add_subplot(gs[5, 0:4])
for m in [4,5,6,7,8]: ax8.axvspan(ab[m], ab[m+1], color=C_KM, alpha=.6, zorder=0)
for m in [0,1,2,10,11]: ax8.axvspan(ab[m], ab[m+1], color=C_HJ, alpha=.6, zorder=0)
ax8.scatter(doy-1, H_harian, s=8, color=C_SUN, alpha=.45, label="Harian")
k15 = np.ones(15)/15; Hs = np.convolve(H_harian, k15, mode="same")
ax8.plot(doy[7:-7]-1, Hs[7:-7], color="#E65100", lw=2.5, label="Rata-rata bergerak")
ax8.set_xticks([ab[m]+hpb[m]/2 for m in range(12)]); ax8.set_xticklabels(nb)
ax8.set_xlim(0,365); ax8.set_ylabel("Iradiasi [kWh/m²/hari]")
ax8.set_title("12. Sumber Surya Sepanjang Tahun (Variasi Musim Tropis)")
l1 = ax8.legend(loc="lower center", fontsize=9, ncol=2)
ax8.legend(handles=[Patch(color=C_KM, label="Kemarau"), Patch(color=C_HJ, label="Hujan")], loc="upper center", fontsize=9, ncol=2)
ax8.add_artist(l1)

# Tahunan 2: Bulanan (Baris 6, left half)
ax9 = fig.add_subplot(gs[6, 0:2])
w = .4
b1=ax9.bar(xb-w/2, O2_bln, w, color=C_O2, label="O₂")
b2=ax9.bar(xb+w/2, CO2_bln, w, color=C_CO2, label="CO₂")
ax9.bar_label(b1, fmt="%.0f", fontsize=7.5, padding=2)
ax9.set_xticks(xb); ax9.set_xticklabels(nb)
ax9.set_ylabel("Massa [kg/bulan]"); ax9.set_ylim(0, O2_bln.max()*1.18)
ax9.set_title("13. Produksi Bulanan O₂ & CO₂")
ax9.legend(fontsize=9)

# Tahunan 3: Kumulatif Tahunan (Baris 6, right half)
ax10 = fig.add_subplot(gs[6, 2:4])
kO2 = np.cumsum(g_O2_hari)/1000; kCO2 = np.cumsum(g_CO2_hari)/1000
ax10.plot(doy-1, kO2, color=C_O2, lw=2.6, label="O₂")
ax10.plot(doy-1, kCO2, color=C_CO2, lw=2.6, label="CO₂")
ax10.fill_between(doy-1, 0, kO2, color=C_O2, alpha=.10)
ax10.set_xticks([ab[m]+hpb[m]/2 for m in range(12)]); ax10.set_xticklabels(nb)
ax10.set_xlim(0,365); ax10.set_ylabel("Massa kumulatif [kg]")
ax10.set_title("14. Akumulasi Produksi Sepanjang Tahun")
ax10.annotate(f"{O2_th_tot:.0f} kg O₂/thn\n≈ {pohon_th:.0f} pohon", xy=(364, O2_th_tot), xytext=(250, O2_th_tot*.55), arrowprops=dict(arrowstyle="->", color=C_O2), fontsize=10, color=C_O2, fontweight="bold")
ax10.annotate(f"{CO2_th_tot:.0f} kg CO₂/thn", xy=(364, CO2_th_tot), xytext=(250, CO2_th_tot*.20), arrowprops=dict(arrowstyle="->", color=C_CO2), fontsize=10, color=C_CO2, fontweight="bold")
ax10.legend(fontsize=9)

fig.savefig("Dashboard_Semua.png", dpi=200, bbox_inches="tight")
print("\nSukses! Dashboard lengkap (Harian + Tahunan) tersimpan sebagai 'Dashboard_Semua.png'.")

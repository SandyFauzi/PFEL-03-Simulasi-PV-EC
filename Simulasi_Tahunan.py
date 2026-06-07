# -*- coding: utf-8 -*-
"""
============================================================================
 SIMULASI TAHUNAN PV-EC  —  Model Fisika Lengkap (365 hari, tropis)
 Memakai mesin fisika yang sama dengan Simulasi.py
----------------------------------------------------------------------------
 PFEL Kelompok 3
============================================================================
"""
import sys, numpy as np, matplotlib.pyplot as plt
from matplotlib.patches import Patch
sys.stdout.reconfigure(encoding='utf-8')

# ===== KONSTANTA & PARAMETER (identik Simulasi.py) =====
F_CONST = 96485.0; R_GAS = 8.314; M_O2 = 32.0; M_CO2 = 44.0; VM_STP = 22.4
M_H2 = 2.0; M_H2O = 18.0
G_PEAK = 1000.0; JAM_TERBIT = 6.0; JAM_TERBENAM = 18.0
LUAS_PANEL = 10.0; ETA_PV_REF = 0.20; BETA_TEMP = 0.004; NOCT = 45.0
T_REF_PV = 25.0; V_BUS = 48.0; R_KABEL = 0.05
E_REV_STD = 1.229; A_ELEKTRODA = 2000.0; N_SEL = 5; R_ASR = 0.5
J0_OER = 1e-6; ALPHA_OER = 0.50; J0_CO2RR = 5e-4; ALPHA_CO2RR = 0.50
FE_MAX = 0.95; J_LIM = 0.50; Z_O2 = 4; Z_CO2 = 6; Z_H2 = 2
PHI_CO2RR = 0.60                                   # selektivitas katoda CO2RR vs HER
K_ABS = 0.01; A_KONTAKTOR = 20.0; CO2_PPM = 420.0; P_ATM = 101325.0
Q_REGEN_TH = 1.46; E_DAC_ELEK = 0.37; ETA_SOLAR_TH = 0.50   # regen DAC (Keith 2018)
H2O_DAC = 4.7                                       # air DAC [kg/kg CO2] (Prats 2024)
O2_PER_POHON_TAHUN = 100_000.0

# Musim tropis
CERAH_RATA = 0.70; CERAH_AMPL = 0.16; DOY_PUNCAK = 227; SEED = 42
T_AMB_MEAN_KEMARAU = 30.0; T_AMB_MEAN_HUJAN = 27.0

# ===== SUMBU WAKTU INTRA-HARI =====
t_h = np.linspace(0.0, 24.0, 24*60+1)
dt_s = (t_h[1] - t_h[0]) * 3600.0
siang = (t_h >= JAM_TERBIT) & (t_h <= JAM_TERBENAM)
G_base = np.where(siang, G_PEAK * np.sin(
    np.pi*(t_h - JAM_TERBIT)/(JAM_TERBENAM - JAM_TERBIT)), 0.0)


def jalankan_hari(s, T_amb_mean):
    """Mesin harian fisika lengkap. s=faktor cerah, T_amb_mean=suhu rata-rata."""
    G = s * G_base
    # Suhu
    T_amp = 4.0
    T_amb = T_amb_mean - T_amp + 2*T_amp * np.sin(
        np.clip(np.pi*(t_h - 5.0)/18.0, 0, np.pi))
    T_cell = T_amb + (NOCT - 20.0) * G / 800.0
    # Panel + MPPT (Pers 1.1)
    eta_pv = ETA_PV_REF * (1.0 - BETA_TEMP * (T_cell - T_REF_PV))
    eta_pv = np.clip(eta_pv, 0.0, 0.33)
    P_pv = eta_pv * LUAS_PANEL * G
    # Ohmik kabel (Pers 1.7)
    I_bus = P_pv / V_BUS
    P_ohmik = I_bus**2 * R_KABEL
    P_reak = np.clip(P_pv - P_ohmik, 0.0, None)
    # Reaktor: iterasi titik operasi
    T_rK = (T_amb + 5.0) + 273.15
    E_rev = E_REV_STD - 0.000846 * (T_rK - 298.15)
    I_r = np.where(P_reak > 0, P_reak / (N_SEL * 2.0), 0.0)
    for _ in range(60):
        j = I_r / A_ELEKTRODA
        js = np.maximum(j, 1e-12)
        eta_a = R_GAS*T_rK/(ALPHA_OER*F_CONST) * np.log(np.maximum(js/J0_OER, 1.0))
        eta_c = R_GAS*T_rK/(ALPHA_CO2RR*F_CONST) * np.log(np.maximum(js/J0_CO2RR, 1.0))
        V_s = E_rev + eta_a + eta_c + js*R_ASR
        V_st = N_SEL * V_s
        I_new = np.where(V_st > 0, P_reak / V_st, 0.0)
        I_new = np.where(P_reak > 0, I_new, 0.0)
        if np.max(np.abs(I_new - I_r)) < 1e-9: break
        I_r = I_new
    j_f = I_r / A_ELEKTRODA
    FE_d = FE_MAX * np.sqrt(np.maximum(1.0 - j_f/J_LIM, 0.0))
    FE_d = np.where(P_reak > 0, FE_d, 0.0)
    # DAC (Pers 1.5)
    C_co2 = CO2_PPM * 1e-6 * P_ATM / (R_GAS * (T_amb + 273.15))
    r_dac = K_ABS * A_KONTAKTOR * C_co2
    # Faraday + selektivitas katoda (CO2RR vs HER). O2 ikut TOTAL arus faradaik.
    FE_co2rr = FE_d * PHI_CO2RR
    FE_her   = FE_d * (1.0 - PHI_CO2RR)
    l_o2  = N_SEL * FE_d     * I_r / (Z_O2   * F_CONST)
    l_co2 = N_SEL * FE_co2rr * I_r / (Z_CO2  * F_CONST)
    l_h2  = N_SEL * FE_her   * I_r / (Z_H2   * F_CONST)
    rdac = np.where(l_co2 > 0, np.minimum(np.divide(r_dac, l_co2,
        out=np.ones_like(r_dac), where=l_co2>0), 1.0), 1.0)
    l_co2_f = l_co2 * rdac
    l_h2_f  = l_h2 + l_co2 * (1.0 - rdac) * (Z_CO2 / Z_H2)   # arus geser ke HER
    mol_O2  = np.sum(l_o2)    * dt_s
    mol_CO2 = np.sum(l_co2_f) * dt_s
    mol_H2  = np.sum(l_h2_f)  * dt_s
    kWh = lambda P: np.sum(P) * dt_s / 3.6e6
    E_s = kWh(G * LUAS_PANEL); E_p = kWh(P_pv); E_r = kWh(P_reak)
    E_k = N_SEL * np.sum(E_rev * I_r * FE_d) * dt_s / 3.6e6
    return E_s, E_p, E_r, E_k, mol_O2, mol_CO2, mol_H2


# ===== POLA MUSIM + DERAU =====
rng = np.random.default_rng(SEED)
doy = np.arange(1, 366)
cerah_musim = CERAH_RATA + CERAH_AMPL * np.cos(
    2*np.pi*(doy - DOY_PUNCAK)/365.0)
basah = (CERAH_RATA + CERAH_AMPL - cerah_musim) / (2*CERAH_AMPL)
sigma = 0.07 + 0.10 * basah
derau = rng.normal(1.0, sigma)
cerah = np.clip(cerah_musim * derau, 0.20, 1.0)
# Suhu ambient musiman
T_amb_hari = T_AMB_MEAN_HUJAN + (T_AMB_MEAN_KEMARAU - T_AMB_MEAN_HUJAN) * (1 - basah)

# ===== JALANKAN 365 HARI =====
E_surya = np.zeros(365); E_pv = np.zeros(365); E_reak = np.zeros(365)
E_kim = np.zeros(365); mol_O2_h = np.zeros(365); mol_CO2_h = np.zeros(365)
mol_H2_h = np.zeros(365)
for d in range(365):
    E_surya[d], E_pv[d], E_reak[d], E_kim[d], mol_O2_h[d], mol_CO2_h[d], mol_H2_h[d] = \
        jalankan_hari(cerah[d], T_amb_hari[d])

g_O2_h  = mol_O2_h  * M_O2
g_CO2_h = mol_CO2_h * M_CO2
g_H2_h  = mol_H2_h  * M_H2
H_harian = E_surya / LUAS_PANEL

# ===== AGREGASI BULANAN =====
hpb = np.array([31,28,31,30,31,30,31,31,30,31,30,31])
ab = np.concatenate([[0], np.cumsum(hpb)])
nb = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Ags","Sep","Okt","Nov","Des"]
def per_bulan(a): return np.array([a[ab[m]:ab[m+1]].sum() for m in range(12)])
O2_bln  = per_bulan(g_O2_h)/1000
CO2_bln = per_bulan(g_CO2_h)/1000
H_bln   = np.array([H_harian[ab[m]:ab[m+1]].mean() for m in range(12)])

# ===== RINGKASAN =====
O2_th  = g_O2_h.sum()/1000; CO2_th = g_CO2_h.sum()/1000; H2_th = g_H2_h.sum()/1000
E_s_th = E_surya.sum(); E_p_th = E_pv.sum(); E_k_th = E_kim.sum()
eta_th = E_k_th / E_s_th if E_s_th > 0 else 0
pohon  = (O2_th*1000) / O2_PER_POHON_TAHUN
mk = (doy >= 121) & (doy <= 273); mh = (doy <= 90) | (doy >= 305)
O2_k = g_O2_h[mk].mean(); O2_h = g_O2_h[mh].mean()
# Beban DAC & neraca air tahunan
E_regen_th_th = CO2_th * Q_REGEN_TH                 # kWh panas regenerasi/tahun
E_solar_th_th = E_regen_th_th / ETA_SOLAR_TH
eta_net_th = E_k_th / (E_s_th + E_solar_th_th) if (E_s_th + E_solar_th_th) > 0 else 0
air_OER_th = (mol_O2_h.sum() * 2.0 * M_H2O) / 1000.0          # L (2 H2O per O2)
air_DAC_th = CO2_th * H2O_DAC * 1000.0 / 1000.0              # L (4,7 kg/kg, kg->L)
air_total_th = air_OER_th + air_DAC_th

print("=" * 68)
print(" SIMULASI TAHUNAN PV-EC  —  MODEL FISIKA LENGKAP (TROPIS)")
print("=" * 68)
print(f" Faktor cerah rata-rata  : {cerah.mean():.2f}")
print(f" Iradiasi rata-rata      : {H_harian.mean():.2f} kWh/m²/hari")
print("-" * 68)
print(f" Energi surya            : {E_s_th:8.0f} kWh/tahun")
print(f" Energi listrik PV       : {E_p_th:8.0f} kWh/tahun")
print(f" Energi kimia            : {E_k_th:8.0f} kWh/tahun")
print(f" η_total                 : {eta_th*100:7.1f}%")
print("-" * 68)
print(f" O₂  dihasilkan          : {O2_th:8.1f} kg/tahun  (≈ {pohon:.0f} pohon)")
print(f" CO₂ ditangkap (CH₃OH)   : {CO2_th:8.1f} kg/tahun  (selektivitas {PHI_CO2RR*100:.0f}%)")
print(f" H₂ produk samping (HER) : {H2_th:8.1f} kg/tahun")
print("-" * 68)
print(" BEBAN DAC & AIR (Keith 2018 · Prats-Salvado 2024)")
print(f"   Energi regen DAC      : {E_regen_th_th:8.0f} kWh panas/tahun")
print(f"   η_NET (PV + DAC)      : {eta_net_th*100:7.1f}%  ← vs η_total {eta_th*100:.1f}%")
print(f"   Kebutuhan air         : {air_total_th:8.0f} L/tahun "
      f"(OER {air_OER_th:.0f} + DAC {air_DAC_th:.0f})")
print("-" * 68)
print(f" O₂ kemarau (rata-rata)  : {O2_k:6.0f} g/hari")
print(f" O₂ hujan   (rata-rata)  : {O2_h:6.0f} g/hari")
print(f" Selisih musiman         : {(O2_k/O2_h-1)*100:5.1f}% lebih tinggi kemarau")
print("=" * 68)
print("\n Produksi per bulan:")
for m in range(12):
    print(f"   {nb[m]}  O₂ {O2_bln[m]:5.1f} kg | CO₂ {CO2_bln[m]:5.1f} kg "
          f"| surya {H_bln[m]:.1f} kWh/m²/hr")

# ===== GRAFIK (3 PNG) =====
plt.rcParams.update({"font.size": 11, "axes.titleweight": "bold",
                     "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 110})
C_SUN="#F9A825"; C_O2="#0277BD"; C_CO2="#6A1B9A"
C_KM="#FFE0B2"; C_HJ="#B3E5FC"
xb = np.arange(12)

fig1, ax1 = plt.subplots(figsize=(9, 5))
for m in [4,5,6,7,8]:
    ax1.axvspan(ab[m], ab[m+1], color=C_KM, alpha=.6, zorder=0)
for m in [0,1,2,10,11]:
    ax1.axvspan(ab[m], ab[m+1], color=C_HJ, alpha=.6, zorder=0)
ax1.scatter(doy-1, H_harian, s=8, color=C_SUN, alpha=.45, label="Harian")
k15 = np.ones(15)/15; Hs = np.convolve(H_harian, k15, mode="same")
ax1.plot(doy[7:-7]-1, Hs[7:-7], color="#E65100", lw=2.5, label="Rata-rata bergerak")
ax1.set_xticks([ab[m]+hpb[m]/2 for m in range(12)]); ax1.set_xticklabels(nb)
ax1.set_xlim(0,365); ax1.set_ylabel("Iradiasi [kWh/m²/hari]")
ax1.set_title("① Sumber Surya Sepanjang Tahun — Variasi Musim Tropis")
l1 = ax1.legend(loc="lower center", fontsize=9, ncol=2)
ax1.legend(handles=[Patch(color=C_KM, label="Kemarau"),
                    Patch(color=C_HJ, label="Hujan")],
           loc="upper center", fontsize=9, ncol=2)
ax1.add_artist(l1); fig1.tight_layout()
fig1.savefig("tahunan_1_resource.png", dpi=300, bbox_inches="tight")

fig2, ax2 = plt.subplots(figsize=(9, 5))
w=.4
b1=ax2.bar(xb-w/2, O2_bln, w, color=C_O2, label="O₂")
b2=ax2.bar(xb+w/2, CO2_bln, w, color=C_CO2, label="CO₂")
ax2.bar_label(b1, fmt="%.0f", fontsize=7.5, padding=2)
ax2.set_xticks(xb); ax2.set_xticklabels(nb)
ax2.set_ylabel("Massa [kg/bulan]"); ax2.set_ylim(0, O2_bln.max()*1.18)
ax2.set_title("② Produksi Bulanan O₂ & CO₂")
ax2.legend(fontsize=9); fig2.tight_layout()
fig2.savefig("tahunan_2_bulanan.png", dpi=300, bbox_inches="tight")

fig3, ax3 = plt.subplots(figsize=(9, 5))
kO2 = np.cumsum(g_O2_h)/1000; kCO2 = np.cumsum(g_CO2_h)/1000
ax3.plot(doy-1, kO2, color=C_O2, lw=2.6, label="O₂")
ax3.plot(doy-1, kCO2, color=C_CO2, lw=2.6, label="CO₂")
ax3.fill_between(doy-1, 0, kO2, color=C_O2, alpha=.10)
ax3.set_xticks([ab[m]+hpb[m]/2 for m in range(12)]); ax3.set_xticklabels(nb)
ax3.set_xlim(0,365); ax3.set_ylabel("Massa kumulatif [kg]")
ax3.set_title("③ Akumulasi Produksi Sepanjang Tahun")
ax3.annotate(f"{O2_th:.0f} kg O₂/thn\n≈ {pohon:.0f} pohon",
             xy=(364, O2_th), xytext=(250, O2_th*.55),
             arrowprops=dict(arrowstyle="->", color=C_O2),
             fontsize=10, color=C_O2, fontweight="bold")
ax3.annotate(f"{CO2_th:.0f} kg CO₂/thn",
             xy=(364, CO2_th), xytext=(250, CO2_th*.20),
             arrowprops=dict(arrowstyle="->", color=C_CO2),
             fontsize=10, color=C_CO2, fontweight="bold")
ax3.legend(fontsize=9); fig3.tight_layout()
fig3.savefig("tahunan_3_kumulatif.png", dpi=300, bbox_inches="tight")

print("\n3 grafik tersimpan: tahunan_1/2/3 PNG")

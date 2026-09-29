import numpy as np
from scipy.integrate import quad
import matplotlib.pyplot as plt

# =====================================================================
# 1. FUNDAMENTAL CONSTANTS AND COSMOLOGICAL PARAMETERS
# =====================================================================
c = 299792.458  # Speed of light in km/s
r_d = 147.09    # Sound horizon scale in Mpc (Planck PR4)

# Resonant Time Model Parameters (Strict invariants from Chapters 4 and 5)
H0_res = 67.4
Om_m_res = 0.315
Om_L_res = 0.685
x1 = 4.4934094579  # First transcendental root of tan(x) = x
alpha0 = np.pi / x1  # Present-day evolution phase limit (~0.699156 rad)

# Standard Lambda-CDM Parameters (DESI Best Fit)
H0_lcdm = 67.4
Om_m_lcdm = 0.319
Om_L_lcdm = 0.681

# =====================================================================
# 2. MATHEMATICAL APPARATUS OF THE RESONANT MODEL
# =====================================================================
def get_k_factor(z):
    """Computes the trigonometric time modifier k(z) = 1/sinc(alpha)"""
    if z > 1000:  # Asymptotic limit for the early Universe (z -> inf)
        return 1.0
    
    # Calculation of dimensionless time phase t/T via arcsinh formula
    num = np.arcsinh(np.sqrt(Om_L_res / Om_m_res) / (1.0 + z)**1.5)
    den = np.arcsinh(np.sqrt(Om_L_res / Om_m_res))
    t_over_T = num / den
    
    # Calculation of dynamic argument alpha(z)
    alpha = alpha0 * t_over_T
    
    # Return modifier k(z) = alpha / sin(alpha)
    if alpha == 0:
        return 1.0
    return alpha / np.sin(alpha)

def DH_rd_res(z):
    """Radial distance DH/rd in the Resonant model (with non-linear k(z))"""
    Hz = H0_res * get_k_factor(z) * np.sqrt(Om_m_res * (1.0 + z)**3 + Om_L_res)
    return c / (Hz * r_d)

def DM_rd_res(z):
    """Transverse distance DM/rd in the Resonant model (k(z') is compensated)"""
    integrand = lambda zp: c / (H0_res * np.sqrt(Om_m_res * (1.0 + zp)**3 + Om_L_res))
    integral, _ = quad(integrand, 0, z)
    return integral / r_d

# =====================================================================
# 3. MATHEMATICAL APPARATUS OF THE STANDARD Lambda-CDM MODEL
# =====================================================================
def DH_rd_lcdm(z):
    """Radial distance DH/rd in standard Lambda-CDM"""
    Hz = H0_lcdm * np.sqrt(Om_m_lcdm * (1.0 + z)**3 + Om_L_lcdm)
    return c / (Hz * r_d)

def DM_rd_lcdm(z):
    """Transverse comoving distance DM/rd in standard Lambda-CDM"""
    integrand = lambda zp: c / (H0_lcdm * np.sqrt(Om_m_lcdm * (1.0 + zp)**3 + Om_L_lcdm))
    integral, _ = quad(integrand, 0, z)
    return integral / r_d

# =====================================================================
# 4. EXPERIMENTAL DATA ARRAY (Z=0 CALIBRATION FROM H0=73.50)
# =====================================================================
obs_z0 = c / (73.50 * r_d)  # Exactly 27.7300

data_points = [
    # Radial Track (DH / rd) - 7 points
    (0.000, 'DH', obs_z0, 0.311, 'SH0ES (H0=73.5 Calibration)'),
    (0.510, 'DH', 21.863, 0.427, 'DESI DR2'),
    (0.706, 'DH', 19.458, 0.332, 'DESI DR2'),
    (0.922, 'DH', 17.510, 0.280, 'DESI DR2 (Isolated LRG3)'),
    (1.321, 'DH', 14.178, 0.217, 'DESI DR2 (ELG2)'),
    (1.484, 'DH', 12.816, 0.513, 'DESI DR2'),
    (2.330, 'DH', 8.600,  0.066, 'DESI DR2 (Ly-alpha/AP)'),
    
    # Transverse Track (DM / rd) - 6 points
    (0.510, 'DM', 13.588, 0.167, 'DESI DR2'),
    (0.706, 'DM', 17.351, 0.177, 'DESI DR2'),
    (0.922, 'DM', 21.340, 0.190, 'DESI DR2 (Isolated LRG3)'),
    (1.321, 'DM', 27.601, 0.318, 'DESI DR2 (ELG2)'),
    (1.484, 'DM', 30.512, 0.760, 'DESI DR2'),
    (2.330, 'DM', 39.320, 0.330, 'DESI DR2 (Ly-alpha/AP)')
]

# =====================================================================
# 5. COMPUTATIONAL LOOP FOR STATISTICAL ANALYSIS & CHI-SQUARE
# =====================================================================
chi2_dh_lcdm, chi2_dm_lcdm = 0.0, 0.0
chi2_dh_res, chi2_dm_res = 0.0, 0.0

print(f"{'z':<6} | {'Type':<4} | {'Experiment':<16} | {'Lambda Theory':<13} | {'Lambda chi2':<11} | {'Resonant Theo':<13} | {'Resonant chi2':<13} | {'k(z)'}")
print("-" * 115)

for z, dist_type, obs, err, source in data_points:
    if dist_type == 'DH':
        th_lcdm = DH_rd_lcdm(z)
        th_res = DH_rd_res(z)
        k_val = f"{get_k_factor(z):.6f}"
    else:
        th_lcdm = DM_rd_lcdm(z)
        th_res = DM_rd_res(z)
        k_val = "Compensated"
        
    point_chi2_lcdm = ((th_lcdm - obs) / err) ** 2
    point_chi2_res = ((th_res - obs) / err) ** 2
    
    if dist_type == 'DH':
        chi2_dh_lcdm += point_chi2_lcdm
        chi2_dh_res += point_chi2_res
    else:
        chi2_dm_lcdm += point_chi2_lcdm
        chi2_dm_res += point_chi2_res
        
    print(f"{z:<6.3f} | {dist_type:<4} | {obs:<6.3f} ± {err:<5.3f} | {th_lcdm:<13.3f} | {point_chi2_lcdm:<11.2f} | {th_res:<13.3f} | {point_chi2_res:<13.2f} | {k_val}")

# Statistical Summary Report
print("\n" + "="*65 + "\nSTATISTICAL GOODNESS-OF-FIT REPORT\n" + "="*65)
print(f"RADIAL TRACK DH (DoF = 7):")
print(f"  -> Standard Lambda-CDM: Total chi2 = {chi2_dh_lcdm:.2f}, Reduced chi2_nu = {chi2_dh_lcdm/7:.2f}")
print(f"  -> Resonant Model:     Total chi2 = {chi2_dh_res:.2f}, Reduced chi2_nu = {chi2_dh_res/7:.2f}")

print(f"\nTRANSVERSE TRACK DM (DoF = 6):")
print(f"  -> Standard Lambda-CDM: Total chi2 = {chi2_dm_lcdm:.2f}, Reduced chi2_nu = {chi2_dm_lcdm/6:.2f}")
print(f"  -> Resonant Model:     Total chi2 = {chi2_dm_res:.2f}, Reduced chi2_nu = {chi2_dm_res/6:.2f}")

total_chi2_lcdm = chi2_dh_lcdm + chi2_dm_lcdm
total_chi2_res = chi2_dh_res + chi2_dm_res

print(f"\nCOMBINED JOINT ANALYSIS DH + DM (DoF = 13):")
print(f"  -> Standard Lambda-CDM: TOTAL chi2 = {total_chi2_lcdm:.2f}, JOINT chi2_nu = {total_chi2_lcdm/13:.2f}")
print(f"  -> Resonant Model:     TOTAL chi2 = {total_chi2_res:.2f}, JOINT chi2_nu = {total_chi2_res/13:.2f}")
print("="*65)

# =====================================================================
# 6. VISUALIZATION BLOCK (HIGH-QUALITY PLOTS WITH ENGLISH LABELS)
# =====================================================================
# Generate a dense redshift grid for smooth theoretical curves
z_dense = np.linspace(0.0, 2.5, 200)

# Compute theoretical curves over the dense grid
dh_lcdm_curve = [DH_rd_lcdm(z) for z in z_dense]
dh_res_curve  = [DH_rd_res(z) for z in z_dense]
dm_lcdm_curve = [DM_rd_lcdm(z) for z in z_dense]
dm_res_curve  = [DM_rd_res(z) for z in z_dense]

# Separate experimental data points by type (fixed indexing)
dh_points = [p for p in data_points if p[1] == 'DH']
dm_points = [p for p in data_points if p[1] == 'DM']

# Apply professional plot styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('Cosmological Models Comparison with DESI DR2 & SH0ES Data', fontsize=14, fontweight='bold', y=0.98)

# Legend flags to prevent duplicate entries
legend_flags = {'H0': False, 'DESI_DH': False, 'DESI_DM': False}

# --- PLOT 1: Radial Track (DH / rd) ---
ax1.plot(z_dense, dh_lcdm_curve, color='#2ca02c', linestyle='--', linewidth=2, label=r'$\Lambda$CDM (Best Fit)')
ax1.plot(z_dense, dh_res_curve, color='#d62728', linestyle='-', linewidth=2.5, label='Resonant Time Model')

# Plot DH experimental points with custom colors
for z, _, obs, err, source in dh_points:
    if 'SH0ES' in source or z == 0:
        lbl = r'$H_0$ Calibration ($z=0$)' if not legend_flags['H0'] else ""
        legend_flags['H0'] = True
        ax1.errorbar(z, obs, yerr=err, fmt='D', color='#FFB300', ecolor='#8B6508', 
                     elinewidth=1.5, capsize=4, markersize=8, zorder=5, label=lbl)
    else:
        lbl = 'DESI DR2 Data' if not legend_flags['DESI_DH'] else ""
        legend_flags['DESI_DH'] = True
        ax1.errorbar(z, obs, yerr=err, fmt='o', color='#1f77b4', ecolor='#104E8B', 
                     elinewidth=1.5, capsize=4, markersize=7, zorder=4, label=lbl)

ax1.set_title('Radial Track $D_H(z) / r_d$', fontsize=12, fontweight='bold')
ax1.set_xlabel('Redshift $z$', fontsize=11)
ax1.set_ylabel('$D_H / r_d$', fontsize=11)
ax1.set_xlim(-0.05, 2.5)
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend(frameon=True, facecolor='white', edgecolor='none', fontsize=10, loc='lower left')

# --- PLOT 2: Transverse Track (DM / rd) ---
ax2.plot(z_dense, dm_lcdm_curve, color='#2ca02c', linestyle='--', linewidth=2, label=r'$\Lambda$CDM (Best Fit)')
ax2.plot(z_dense, dm_res_curve, color='#d62728', linestyle='-', linewidth=2.5, label='Resonant Time Model')

# Plot DM experimental points (DESI only)
for z, _, obs, err, source in dm_points:
    lbl = 'DESI DR2 Data' if not legend_flags['DESI_DM'] else ""
    legend_flags['DESI_DM'] = True
    ax2.errorbar(z, obs, yerr=err, fmt='o', color='#1f77b4', ecolor='#104E8B', 
                 elinewidth=1.5, capsize=4, markersize=7, zorder=4, label=lbl)

ax2.set_title('Transverse Track $D_M(z) / r_d$', fontsize=12, fontweight='bold')
ax2.set_xlabel('Redshift $z$', fontsize=11)
ax2.set_ylabel('$D_M / r_d$', fontsize=11)
ax2.set_xlim(0.4, 2.5)  # DM data starts at z = 0.51
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(frameon=True, facecolor='white', edgecolor='none', fontsize=10, loc='upper left')

plt.tight_layout()
plt.show()

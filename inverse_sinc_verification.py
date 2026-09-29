import numpy as np
from scipy.integrate import quad
import matplotlib.pyplot as plt

# =====================================================================
# 1. FUNDAMENTAL CONSTANTS AND COSMOLOGICAL BACKGROUND PARAMETERS
# =====================================================================
c = 299792.458  # Speed of light in km/s
r_d = 147.09    # Sound horizon scale in Mpc (Planck PR4)

# Resonant Time Model parameters (Planck PR4 / HiLLiPoP 2024 basis)
H0_res = 67.64
Om_m_res = 0.3092
Om_L_res = 0.6908
x1 = 4.4934094579  # First transcendental root of tan(x) = x
alpha0 = np.pi / x1  # Present-day evolution phase limit (~0.699156 rad)

# Standard Lambda-CDM model parameters (DESI Best Fit)
H0_lcdm = 67.4
Om_m_lcdm = 0.319
Om_L_lcdm = 0.681

# =====================================================================
# 2. MATHEMATICAL APPARATUS OF THE RESONANT MODEL
# =====================================================================
def get_k_factor(z):
    """Calculates the cosmological time trigonometric modifier k(z) = 1/sinc(alpha)"""
    if z > 1000:  # Asymptotic limit for the early Universe (z -> inf)
        return 1.0
    
    # Calculation of the dimensionless time phase t/T via arcsinh formula
    num = np.arcsinh(np.sqrt(Om_L_res / Om_m_res) / (1.0 + z)**1.5)
    den = np.arcsinh(np.sqrt(Om_L_res / Om_m_res))
    t_over_T = num / den
    
    # Calculation of the dynamic argument alpha(z)
    alpha = alpha0 * t_over_T
    
    # Return the modifier k(z) = alpha / sin(alpha)
    if alpha == 0:
        return 1.0
    return alpha / np.sin(alpha)

def DH_rd_res(z):
    """Radial distance DH/rd in the Resonant Model (with non-linear k(z))"""
    Hz = H0_res * get_k_factor(z) * np.sqrt(Om_m_res * (1.0 + z)**3 + Om_L_res)
    return c / (Hz * r_d)

def DM_rd_res(z):
    """Transverse distance DM/rd in the Resonant Model (k(z') is compensated)"""
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
# 4. EXPERIMENTAL DATASET (DESI DR2 2025/2026 AND SH0ES)
# =====================================================================
# Each point: (z, distance_type, observed_value, error, source_name)
data_points = [
    # Radial track (DH / rd) - 7 points
    (0.000, 'DH', 27.738, 0.311, 'SH0ES'),
    (0.510, 'DH', 21.863, 0.427, 'DESI DR2'),
    (0.706, 'DH', 19.458, 0.332, 'DESI DR2'),
    (0.934, 'DH', 17.641, 0.193, 'DESI DR2 (LRG3+ELG1)'),
    (1.321, 'DH', 14.178, 0.217, 'DESI DR2 (ELG2)'),
    (1.484, 'DH', 12.816, 0.513, 'DESI DR2'),
    (2.330, 'DH', 8.600,  0.066, 'DESI DR2 (Ly-alpha/AP)'),
    
    # Transverse track (DM / rd) - 6 points
    (0.510, 'DM', 13.588, 0.167, 'DESI DR2'),
    (0.706, 'DM', 17.351, 0.177, 'DESI DR2'),
    (0.934, 'DM', 21.576, 0.152, 'DESI DR2 (LRG3+ELG1)'),
    (1.321, 'DM', 27.601, 0.318, 'DESI DR2 (ELG2)'),
    (1.484, 'DM', 30.512, 0.760, 'DESI DR2'),
    (2.330, 'DM', 39.320, 0.330, 'DESI DR2 (Ly-alpha/AP)')
]

# =====================================================================
# 5. COMPUTATIONAL LOOP FOR STATISTICAL ANALYSIS AND CHI-SQUARE
# =====================================================================
chi2_dh_lcdm, chi2_dm_lcdm = 0.0, 0.0
chi2_dh_res, chi2_dm_res = 0.0, 0.0

print(f"{'z':<6} | {'Type':<4} | {'Experiment':<16} | {'Lambda Theory':<13} | {'Lambda chi2':<11} | {'Resonant Theo':<13} | {'Resonant chi2':<13} | {'k(z)'}")
print("-" * 115)

for z, dist_type, obs, err, source in data_points:
    # Theoretical values calculation
    if dist_type == 'DH':
        th_lcdm = DH_rd_lcdm(z)
        th_res = DH_rd_res(z)
        k_val = f"{get_k_factor(z):.6f}"
    else:
        th_lcdm = DM_rd_lcdm(z)
        th_res = DM_rd_res(z)
        k_val = "Compensated"
        
    # Individual chi-square contributions
    point_chi2_lcdm = ((th_lcdm - obs) / err) ** 2
    point_chi2_res = ((th_res - obs) / err) ** 2
    
    # Accumulating sums by geometric projections
    if dist_type == 'DH':
        chi2_dh_lcdm += point_chi2_lcdm
        chi2_dh_res += point_chi2_res
    else:
        chi2_dm_lcdm += point_chi2_lcdm
        chi2_dm_res += point_chi2_res
        
    print(f"{z:<6.3f} | {dist_type:<4} | {obs:<6.3f} ± {err:<5.3f} | {th_lcdm:<13.3f} | {point_chi2_lcdm:<11.2f} | {th_res:<13.3f} | {point_chi2_res:<13.2f} | {k_val}")

# Summary statistical report
print("\n" + "="*60 + "\nSTATISTICAL REPORT ON GOODNESS-OF-FIT CRITERIA\n" + "="*60)
print(f"RADIAL TRACK DH (DoF = 7):")
print(f"  -> Standard Lambda-CDM: Total chi2 = {chi2_dh_lcdm:.2f}, Reduced chi2_nu = {chi2_dh_lcdm/7:.2f}")
print(f"  -> Resonant Model:     Total chi2 = {chi2_dh_res:.2f}, Reduced chi2_nu = {chi2_dh_res/7:.2f}")

print(f"\nTRANSVERSE TRACK DM (DoF = 6):")
print(f"  -> Standard Lambda-CDM: Total chi2 = {chi2_dm_lcdm:.2f}, Reduced chi2_nu = {chi2_dm_lcdm/6:.2f}")
print(f"  -> Resonant Model:     Total chi2 = {chi2_dm_res:.2f}, Reduced chi2_nu = {chi2_dm_res/6:.2f}")

total_chi2_lcdm = chi2_dh_lcdm + chi2_dm_lcdm
total_chi2_res = chi2_dh_res + chi2_dm_res

print(f"\nJOINT COMBINED ANALYSIS DH + DM (DoF = 13):")
print(f"  -> Standard Lambda-CDM: TOTAL chi2 = {total_chi2_lcdm:.2f}, JOINT chi2_nu = {total_chi2_lcdm/13:.2f}")
print(f"  -> Resonant Model:     TOTAL chi2 = {total_chi2_res:.2f}, JOINT chi2_nu = {total_chi2_res/13:.2f}")
print("="*60)

# =====================================================================
# 6. PLOTTING THE DH/rd AND DM/rd GRAPHS
# =====================================================================
# Generate smooth redshift array for plotting theories
z_arr = np.linspace(0, 2.5, 200)

# Compute theoretical curves over the range
dh_lcdm_curve = [DH_rd_lcdm(z) for z in z_arr]
dh_res_curve  = [DH_rd_res(z) for z in z_arr]
dm_lcdm_curve = [DM_rd_lcdm(z) for z in z_arr]
dm_res_curve  = [DM_rd_res(z) for z in z_arr]

# Separate experimental data for easier plotting
z_dh = [p[0] for p in data_points if p[1] == 'DH']
obs_dh = [p[2] for p in data_points if p[1] == 'DH']
err_dh = [p[3] for p in data_points if p[1] == 'DH']

z_dm = [p[0] for p in data_points if p[1] == 'DM']
obs_dm = [p[2] for p in data_points if p[1] == 'DM']
err_dm = [p[3] for p in data_points if p[1] == 'DM']

# Initialize subplots (1 row, 2 columns)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Left Plot: DH/rd (Radial distance)
ax1.plot(z_arr, dh_lcdm_curve, label=r'$\Lambda$-CDM Model', color='blue', linestyle='--')
ax1.plot(z_arr, dh_res_curve, label='Resonant Time Model', color='red', linewidth=2)
ax1.errorbar(z_dh, obs_dh, yerr=err_dh, fmt='o', color='black', ecolor='darkgray', 
             capsize=4, label='Data (DESI DR2 / SH0ES)')
ax1.set_xlabel('Redshift $z$', fontsize=12)
ax1.set_ylabel('$D_H / r_d$', fontsize=12)
ax1.set_title('Radial Distance $D_H / r_d$', fontsize=14, fontweight='bold')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend(fontsize=10)

# Right Plot: DM/rd (Transverse distance)
ax2.plot(z_arr, dm_lcdm_curve, label=r'$\Lambda$-CDM Model', color='blue', linestyle='--')
ax2.plot(z_arr, dm_res_curve, label='Resonant Time Model', color='red', linewidth=2)
ax2.errorbar(z_dm, obs_dm, yerr=err_dm, fmt='s', color='black', ecolor='darkgray', 
             capsize=4, label='Data (DESI DR2)')
ax2.set_xlabel('Redshift $z$', fontsize=12)
ax2.set_ylabel('$D_M / r_d$', fontsize=12)
ax2.set_title('Transverse Distance $D_M / r_d$', fontsize=14, fontweight='bold')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(fontsize=10)

plt.tight_layout()
plt.show()

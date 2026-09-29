import numpy as np
from scipy.integrate import quad

# =====================================================================
# 1. FUNDAMENTAL CONSTANTS AND COSMOLOGICAL BASIS PARAMETERS
# =====================================================================
c = 299792.458  # Speed of light in km/s
r_d = 147.09    # Sound horizon scale in Mpc (Planck PR4)

# Resonance Time Model Parameters (Strict invariants from Section 4 and 5)
H0_res = 67.4
Om_m_res = 0.315
Om_L_res = 0.685
x1 = 4.4934094579  # First non-trivial transcendental root of tan(x) = x
alpha0 = np.pi / x1  # Present Present-time evolution phase limit (~0.699156 rad)

# Standard Lambda-CDM Model Parameters (DESI Best Fit)
H0_lcdm = 67.4
Om_m_lcdm = 0.319
Om_L_lcdm = 0.681

# =====================================================================
# 2. MATHEMATICAL FRAMEWORK OF THE RESONANCE MODEL
# =====================================================================
def get_k_factor(z):
    """Calculates the trigonometric time modifier k(z) = 1/sinc(alpha)"""
    if z > 1000:  # Asymptotic limit for the early Universe (z -> inf)
        return 1.0
    
    # Calculate the dimensionless time ratio t/T via the arcsinh equation
    num = np.arcsinh(np.sqrt(Om_L_res / Om_m_res) / (1.0 + z)**1.5)
    den = np.arcsinh(np.sqrt(Om_L_res / Om_m_res))
    t_over_T = num / den
    
    # Compute the dynamic evolution argument alpha(z)
    alpha = alpha0 * t_over_T
    
    # Return the metric modifier k(z) = alpha / sin(alpha)
    if alpha == 0:
        return 1.0
    return alpha / np.sin(alpha)

def DH_rd_res(z):
    """Radial distance DH/rd in the Resonance model (with non-linear k(z))"""
    Hz = H0_res * get_k_factor(z) * np.sqrt(Om_m_res * (1.0 + z)**3 + Om_L_res)
    return c / (Hz * r_d)

def DM_rd_res(z):
    """Transverse distance DM/rd in the Resonance model (k(z') identity cancellation)"""
    integrand = lambda zp: c / (H0_res * np.sqrt(Om_m_res * (1.0 + zp)**3 + Om_L_res))
    integral, _ = quad(integrand, 0, z)
    return integral / r_d

# =====================================================================
# 3. MATHEMATICAL FRAMEWORK OF THE STANDARD Lambda-CDM MODEL
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
# 4. UPDATED EXPERIMENTAL DATASET (Z=0 CALIBRATION FROM H0=73.50)
# =====================================================================
obs_z0 = c / (73.50 * r_d)  # Exactly 27.7300

data_points = [
    # Radial Track (DH / rd) - 7 data points
    (0.000, 'DH', obs_z0, 0.311, 'SH0ES (H0=73.5 Calibration)'),
    (0.510, 'DH', 21.863, 0.427, 'DESI DR2'),
    (0.706, 'DH', 19.458, 0.332, 'DESI DR2'),
    (0.922, 'DH', 17.510, 0.280, 'DESI DR2 (LRG3 Isolated)'),
    (1.321, 'DH', 14.178, 0.217, 'DESI DR2 (ELG2)'),
    (1.484, 'DH', 12.816, 0.513, 'DESI DR2'),
    (2.330, 'DH', 8.600,  0.066, 'DESI DR2 (Ly-alpha/AP)'),
    
    # Transverse Track (DM / rd) - 6 data points
    (0.510, 'DM', 13.588, 0.167, 'DESI DR2'),
    (0.706, 'DM', 17.351, 0.177, 'DESI DR2'),
    (0.922, 'DM', 21.340, 0.190, 'DESI DR2 (LRG3 Isolated)'),
    (1.321, 'DM', 27.601, 0.318, 'DESI DR2 (ELG2)'),
    (1.484, 'DM', 30.512, 0.760, 'DESI DR2'),
    (2.330, 'DM', 39.320, 0.330, 'DESI DR2 (Ly-alpha/AP)')
]

# =====================================================================
# 5. EXECUTION PIPELINE FOR STATISTICAL ANALYSIS AND CHI-SQUARED MAPPING
# =====================================================================
chi2_dh_lcdm, chi2_dm_lcdm = 0.0, 0.0
chi2_dh_res, chi2_dm_res = 0.0, 0.0

print(f"{'z':<6} | {'Typ':<3} | {'Experiment':<16} | {'Lambda Theory':<13} | {'chi2 Lambda':<11} | {'Reson Theory':<12} | {'chi2 Reson':<10} | {'k(z)'}")
print("-" * 110)

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
        
    print(f"{z:<6.3f} | {dist_type:<3} | {obs:<6.3f} ± {err:<5.3f} | {th_lcdm:<13.3f} | {point_chi2_lcdm:<11.2f} | {th_res:<12.3f} | {point_chi2_res:<10.2f} | {k_val}")

# Comprehensive Statistical Summary Report
print("\n" + "="*60 + "\nSTATISTICAL GOODNESS-OF-FIT REPORT\n" + "="*60)
print(f"RADIAL TRACK DH (DoF = 7):")
print(f"  -> Standard Lambda-CDM: Total chi2 = {chi2_dh_lcdm:.2f}, Reduced chi2_nu = {chi2_dh_lcdm/7:.2f}")
print(f"  -> Resonance Model:     Total chi2 = {chi2_dh_res:.2f}, Reduced chi2_nu = {chi2_dh_res/7:.2f}")

print(f"\nTRANSVERSE TRACK DM (DoF = 6):")
print(f"  -> Standard Lambda-CDM: Total chi2 = {chi2_dm_lcdm:.2f}, Reduced chi2_nu = {chi2_dm_lcdm/6:.2f}")
print(f"  -> Resonance Model:     Total chi2 = {chi2_dm_res:.2f}, Reduced chi2_nu = {chi2_dm_res/6:.2f}")

total_chi2_lcdm = chi2_dh_lcdm + chi2_dm_lcdm
total_chi2_res = chi2_dh_res + chi2_dm_res

print(f"\nCOMBINED JOINT DATASET ANALYSIS DH + DM (DoF = 13):")
print(f"  -> Standard Lambda-CDM: GLOBAL chi2 = {total_chi2_lcdm:.2f}, JOINT chi2_nu = {total_chi2_lcdm/13:.2f}")
print(f"  -> Resonance Model:     GLOBAL chi2 = {total_chi2_res:.2f}, JOINT chi2_nu = {total_chi2_res/13:.2f}")
print("="*60)

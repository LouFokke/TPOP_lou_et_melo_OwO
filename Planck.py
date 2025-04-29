import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

plt.rcParams.update({'font.size': 20})

# Constantes physiques
h = 6.626e-34     # constante de Planck (J·s)
c = 3.00e8        # vitesse de la lumière (m/s)
k = 1.381e-23     # constante de Boltzmann (J/K)

# Longueurs d'onde (en mètres)
wavelengths = np.linspace(1e-7, 3e-6, 1000)  # de 100 nm à 3000 nm

# Températures en degrés Celsius
temperatures_celsius = [25, 75, 120, 200]
temperatures_kelvin = [T + 273.15 for T in temperatures_celsius]

# Fonction d'irradiance spectrale (formule de Planck)
def planck_law(wavelength, T):
    return (2*h*c**2) / (wavelength**5) / (np.exp((h*c)/(wavelength*k*T)) - 1)

# Limites pour la zone surlignée
lambda_min_nm = 900
lambda_max_nm = 1700
lambda_min = lambda_min_nm * 1e-9
lambda_max = lambda_max_nm * 1e-9

# Tracer les courbes
plt.figure(figsize=(10, 6))

for T, Tc in zip(temperatures_kelvin, temperatures_celsius):
    irradiance = planck_law(wavelengths, T)
    label = f"{Tc}°C"

    # Tracer la courbe principale
    plt.plot(wavelengths * 1e9, irradiance, label=label)
    
    # Section entre 900 et 1700 nm
    mask = (wavelengths >= lambda_min) & (wavelengths <= lambda_max)
    wavelengths_section = wavelengths[mask]
    irradiance_section = irradiance[mask]
    
    # Surlignage
    plt.fill_between(wavelengths_section * 1e9, irradiance_section, alpha=0.2)
    
    # Intégrale
    area = np.trapz(irradiance_section, wavelengths_section)
    print(f"Irradiance totale entre 900 et 1700 nm à {Tc}°C : {area:.2e} W/m²")

# Lignes verticales pointillées sans légende
plt.axvline(x=lambda_min_nm, color='green', linestyle='--', label='_nolegend_')
plt.axvline(x=lambda_max_nm, color='green', linestyle='--', label='_nolegend_')

# Format scientifique pour l'axe Y
ax = plt.gca()
ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

plt.xlabel("Longueur d’onde (nm)")
plt.ylabel("Irradiance (W·m⁻²·m⁻¹)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
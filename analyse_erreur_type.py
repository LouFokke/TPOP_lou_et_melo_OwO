import numpy as np  
import matplotlib.pyplot as plt
import requests
import io
from scipy.optimize import curve_fit

# Augmenter la taille globale de la police
plt.rcParams.update({'font.size': 20})

# ==============================================================================
# SECTION 1 : Acquisition et Prétraitement des Données du Fichier 1 (Référence)
# ==============================================================================
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/refs/heads/main/Labo1/analyse_image/"
nom_fichier_1 = "Reslice of 0_sans_def_01.txt"
chemin_fichier_1 = url + nom_fichier_1
print(f"Téléchargement des données depuis : {chemin_fichier_1}")

response = requests.get(chemin_fichier_1)
if response.status_code != 200:
    raise ValueError(f"Échec du téléchargement : Code {response.status_code}")
data = np.loadtxt(io.StringIO(response.text))

# Normalisation des données
data_min = data.min()
data_max = data.max()
data_norm = (data - data_min) / (data_max - data_min)
n_time, n_position = data_norm.shape
positions = np.linspace(0, 1, n_position)

# ==============================================================================
# SECTION 2 : Visualisation des Données du Fichier 1 (Référence)
# ==============================================================================
plt.figure(figsize=(8, 6))
for t in range(n_time):
    plt.plot(positions, data_norm[t, :], color='black', alpha=0.3)
moyenne_norm = np.mean(data_norm, axis=0)
plt.plot(positions, moyenne_norm, color='red', lw=2, label="Courbe Moyenne")

plt.xlabel("Position (normalisée)")
plt.ylabel("Intensité (normalisée)")
plt.title("Intensité de la radiation de la plaque\n (Sans Déformation)")
plt.legend()
plt.tight_layout()
plt.show()

# ==============================================================================
# SECTION 3 : Fit Gaussien sur Chaque Courbe
# ==============================================================================
def gaussian(x, a, mu, sigma, offset):
    return a * np.exp(-(x - mu)**2 / (2 * sigma**2)) + offset

plt.figure(figsize=(8, 6))
all_diff = []
params_gauss = []

for t in range(n_time):
    y = data_norm[t, :]
    
    # Estimations initiales pour le fit
    init = [1, 0.5, 0.1, 0]
    
    # Fit gaussien
    try:
        popt, _ = curve_fit(gaussian, positions, y, p0=init)
    except RuntimeError:
        print(f"⚠️ Fit échoué pour t = {t}")
        continue

    params_gauss.append(popt)
    
    # Gaussienne ajustée
    y_fit = gaussian(positions, *popt)
    
    # Écart absolu
    diff_abs = np.abs(y - y_fit)
    all_diff.append(diff_abs)
    
    # Tracer les écarts
    plt.plot(positions, diff_abs, color='gray', alpha=0.3)

# Moyenne des écarts
mean_diff = np.mean(np.array(all_diff), axis=0)
plt.plot(positions, mean_diff, color='red', lw=2, label="Différence Moyenne")

plt.xlabel("Position (normalisée)")
plt.ylabel("Écart Absolu")
plt.ylim(0, 0.4)
plt.title("Écarts Absolus entre Courbes Réelles et Fits Gaussiens")
plt.legend()
plt.tight_layout()
plt.show()

# ==============================================================================
# SECTION 4 : Superposition des Courbes Réelles et Fits Gaussiens
# ==============================================================================
plt.figure(figsize=(8, 6))

for t in range(n_time):
    y = data_norm[t, :]
    if t >= len(params_gauss):
        continue  # Skip si pas de fit
    
    popt = params_gauss[t]
    y_fit = gaussian(positions, *popt)
    
    # Courbe réelle
    plt.plot(positions, y, color='black', alpha=0.3, 
             label="Réel" if t == 0 else "")
    
    # Courbe fit
    plt.plot(positions, y_fit, '-', color='red', alpha=0.3, 
             label="Fit Gaussien" if t == 0 else "")

plt.xlabel("Position (normalisée)")
plt.ylabel("Intensité (normalisée)")
plt.title("Superposition des Courbes Réelles et de leurs Fits Gaussiens")
plt.legend()
plt.tight_layout()
plt.show()

# ==============================================================================
# SECTION 5 : Résultat Final - Erreur Typique
# ==============================================================================
erreur_typique = np.mean(mean_diff)
print(f"\nErreur typique (moyenne des écarts absolus) = {erreur_typique:.4f}")

import numpy as np 
import matplotlib.pyplot as plt
import requests
import io
from scipy.optimize import least_squares

# ==============================================================================
# Section 1 : Chargement, normalisation et affichage des données
# ==============================================================================
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/refs/heads/main/Labo1/analyse_image/"
fichier_txt = "Reslice of 0_sans_def_01.txt"
path = url + fichier_txt
print(f"Téléchargement des données depuis : {path}")

response = requests.get(path)
if response.status_code != 200:
    raise ValueError(f"Échec du téléchargement : Code {response.status_code}")
data = np.loadtxt(io.StringIO(response.text))

# Normalisation du fichier 1
data_min = data.min()
data_max = data.max()
data_norm = (data - data_min) / (data_max - data_min)

n_time, n_position = data_norm.shape
positions = np.linspace(0, 1, n_position)

# Affichage initial du fichier 1 (image fixe)
plt.figure(figsize=(10, 6))
for t in range(n_time):
    plt.plot(positions, data_norm[t, :], color='black', alpha=0.3)
moyenne_norm = np.mean(data_norm, axis=0)
plt.plot(positions, moyenne_norm, color='red', lw=2, label="Courbe moyenne")
plt.xlabel("Position (normalisée)")
plt.ylabel("Intensité (normalisée)")
plt.title("Courbes normalisées du fichier 1")
plt.legend()
plt.tight_layout()
plt.show()

# ---- Chargement du deuxième fichier ----
fichier_txt2 = "Reslice of 5_pli_1.txt"
path2 = url + fichier_txt2
print(f"Téléchargement du deuxième fichier depuis : {path2}")

response2 = requests.get(path2)
if response2.status_code != 200:
    raise ValueError(f"Échec du téléchargement du second fichier : Code {response2.status_code}")
data2 = np.loadtxt(io.StringIO(response2.text))

# Normalisation du fichier 2
data2_min = data2.min()
data2_max = data2.max()
data2_norm = (data2 - data2_min) / (data2_max - data2_min)

n_time2, n_position2 = data2_norm.shape
common_n_position = min(n_position, n_position2)
print(f"Utilisation de {common_n_position} positions communes entre les deux fichiers.")

data_norm = data_norm[:, :common_n_position]
data2_norm = data2_norm[:, :common_n_position]
positions = np.linspace(0, 1, common_n_position)
n_position = common_n_position
n_position2 = common_n_position

# ==============================================================================
# Section 2 : Alignement par paire (chaque courbe du fichier 2 est alignée sur sa
#           courbe correspondante du fichier 1, le fichier 1 reste inchangé)
# ==============================================================================

def align_curve_improved(ref, curve, x):
    """
    Aligne une courbe sur une courbe de référence en ajustant :
       - le décalage en x (dx),
       - le scaling horizontal (s),
       - l'échelle en y (a) et
       - l'offset vertical (b).
    
    La transformation est définie par :
         aligned(x) = a * curve((x - dx) / s) + b
    
    Retourne :
        aligned : la courbe alignée,
        dx, s, a, b : les paramètres optimaux trouvés.
    """
    def residual(params):
        dx, s, a, b = params
        # Interpoler la courbe transformée selon le scaling et translation
        shifted = np.interp((x - dx) / s, x, curve, left=np.nan, right=np.nan)
        diff = a * shifted + b - ref
        return np.nan_to_num(diff)
    
    init = [0, 1, 1, 0]  # paramètres initiaux : pas de décalage, s=1, a=1, b=0.
    res = least_squares(residual, init)
    dx, s, a, b = res.x
    aligned = a * np.interp((x - dx) / s, x, curve, left=np.nan, right=np.nan) + b
    return aligned, dx, s, a, b

# On va travailler sur le nombre minimum de courbes disponibles dans les deux fichiers
n_curve = min(n_time, n_time2)
aligned_data2_individual = np.zeros((n_curve, common_n_position))
params_data2 = []

# Alignement par paire :
# Pour chaque indice t, on garde la courbe du fichier 1 telle quelle et on
# aligne la courbe correspondante du fichier 2.
for t in range(n_curve):
    ref_curve = data_norm[t, :]         # référence : courbe t du fichier 1 (inchangée)
    curve2 = data2_norm[t, :]           # courbe t du fichier 2 (non alignée)
    aligned_curve, dx, s, a, b = align_curve_improved(ref_curve, curve2, positions)
    aligned_data2_individual[t, :] = aligned_curve
    params_data2.append((dx, s, a, b))

# ==============================================================================
# Section 3 : Affichage par paire pour comparer les courbes
# ==============================================================================

plt.figure(figsize=(10, 6))
for t in range(n_curve):
    # Courbe du fichier 1 (originale, en noir)
    plt.plot(positions, data_norm[t, :], color='black', alpha=0.3, 
             label="Fichier 1" if t == 0 else "")
    # Courbe du fichier 2 alignée sur celle du fichier 1 (en rouge)
    plt.plot(positions, aligned_data2_individual[t, :], color='red', alpha=0.3, 
             label="Fichier 2 aligné" if t == 0 else "")
plt.xlabel("Position (normalisée)")
plt.ylabel("Intensité (normalisée)")
plt.title("Comparaison par paire : Fichier 1 (original) vs Fichier 2 (aligné)")
plt.legend()
plt.tight_layout()
plt.show()
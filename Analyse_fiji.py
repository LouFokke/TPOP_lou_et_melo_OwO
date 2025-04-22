import numpy as np  
import matplotlib.pyplot as plt
import requests
import io
from scipy.optimize import least_squares

# Augmenter la taille globale de la police (par défaut environ 10, ici on passe à 20)
plt.rcParams.update({'font.size': 20})

# ==============================================================================
# SECTION 1 : Acquisition et Prétraitement des Données du Fichier 1 (Référence)
# ==============================================================================
# 🔧 Modifier ici le nom du fichier 1 si besoin
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/refs/heads/main/Labo1/analyse_image/"
nom_fichier_1 = "Reslice of 0_sans_def_01.txt"
chemin_fichier_1 = url + nom_fichier_1
print(f"Téléchargement des données depuis : {chemin_fichier_1}")

response = requests.get(chemin_fichier_1)
if response.status_code != 200:
    raise ValueError(f"Échec du téléchargement : Code {response.status_code}")
data = np.loadtxt(io.StringIO(response.text))

# Normalisation des données du Fichier 1
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
# 🔧 Modifier ici le titre du graphique si besoin
plt.title("Intensité de la radiation de la plaque en fonction\n du temps et de la position sans déformation")
plt.legend()
plt.tight_layout()
plt.show()


# ==============================================================================
# SECTION 3 : Acquisition et Prétraitement des Données du Fichier 2 (Déformé)
# ==============================================================================
# 🔧 Modifier ici le nom du fichier 2 si besoin
nom_fichier_2 = "Reslice of 5_pli_1.txt"
chemin_fichier_2 = url + nom_fichier_2
print(f"Téléchargement des données depuis : {chemin_fichier_2}")

response2 = requests.get(chemin_fichier_2)
if response2.status_code != 200:
    raise ValueError(f"Échec du téléchargement du Fichier 2 : Code {response2.status_code}")
data2 = np.loadtxt(io.StringIO(response2.text))

# Optionnel : recadrer verticalement le Fichier 2 pour matcher le nombre de courbes avec le Fichier 1
n_time2_full, n_position2_full = data2.shape
data2 = data2[:n_time, :]  
n_time2, n_position2 = data2.shape

# Normalisation du Fichier 2
data2_min = data2.min()
data2_max = data2.max()
data2_norm = (data2 - data2_min) / (data2_max - data2_min)

# Redimensionnement horizontal pour matcher avec le Fichier 1
common_n_position = min(n_position, n_position2)
print(f"Utilisation de {common_n_position} positions communes.")
data_norm = data_norm[:, :common_n_position]
data2_norm = data2_norm[:, :common_n_position]
positions = np.linspace(0, 1, common_n_position)

plt.figure(figsize=(8, 6))
for t in range(n_time):
    plt.plot(positions, data2_norm[t, :], color='black', alpha=0.3)
moyenne2_norm = np.mean(data2_norm, axis=0)
plt.plot(positions, moyenne2_norm, color='red', lw=2, label="Courbe Moyenne")

plt.xlabel("Position (normalisée)")
plt.ylabel("Intensité (normalisée)")
# 🔧 Modifier ici le titre du graphique si besoin
plt.title("Intensité de la radiation de la plaque en fonction\n du temps et de la position avec déformation")
plt.legend()
plt.tight_layout()
plt.show()

# ==============================================================================
# SECTION 4 : Alignement des Courbes du Fichier 2 sur le Fichier 1 (Par Paires)
# ==============================================================================
def align_curve_improved(ref, curve, x):
    """
    Aligne une courbe sur une courbe de référence en ajustant :
        - dx : décalage horizontal
        - s  : facteur d'étirement horizontal
        - a  : amplitude (scaling vertical)
        - b  : décalage vertical
    Transformation : aligned(x) = a * curve((x - dx) / s) + b

    Modification essentielle : extension du domaine d'interpolation pour éviter que
    la transformation ne "coupe" la courbe lorsqu'elle sort de [0, 1].
    """
    def residual(params):
        dx, s, a, b = params
        x_new = (x - dx) / s

        # Extension du domaine pour éviter les NaN en bordure
        x_extended = np.concatenate([[x[0] - 1e-3], x, [x[-1] + 1e-3]])
        curve_extended = np.concatenate([[curve[0]], curve, [curve[-1]]])

        shifted = np.interp(x_new, x_extended, curve_extended)
        diff = a * shifted + b - ref
        return diff
    
    init = [0, 1, 1, 0]  # Paramètres initiaux : aucun décalage ni scaling
    res = least_squares(residual, init)
    dx, s, a, b = res.x

    # Calcul de la courbe alignée avec extension du domaine
    x_new = (x - dx) / s
    x_extended = np.concatenate([[x[0] - 1e-3], x, [x[-1] + 1e-3]])
    curve_extended = np.concatenate([[curve[0]], curve, [curve[-1]]])
    aligned = a * np.interp(x_new, x_extended, curve_extended) + b

    return aligned, dx, s, a, b

# Alignement par paires : nombre de paires à aligner est le minimum de n_time et n_time2
n_curve = min(n_time, n_time2)
aligned_data2_individual = np.zeros((n_curve, common_n_position))
params_data2 = []

for t in range(n_curve):
    ref_curve = data_norm[t, :]   # Fichier 1 (référence)
    curve2 = data2_norm[t, :]       # Fichier 2 (à aligner)
    aligned_curve, dx, s, a, b = align_curve_improved(ref_curve, curve2, positions)
    aligned_data2_individual[t, :] = aligned_curve
    params_data2.append((dx, s, a, b))

# ==============================================================================
# SECTION 5 : Visualisation par Paires des Courbes Alignées
# ==============================================================================
plt.figure(figsize=(8, 6))
for t in range(n_curve):
    plt.plot(positions, data_norm[t, :], color='black', alpha=0.3, 
             label="Référence" if t == 0 else "")
    plt.plot(positions, aligned_data2_individual[t, :],'-', color='red', alpha=0.3, 
             label="Déformé" if t == 0 else "")
plt.xlabel("Position (normalisée)")
plt.ylabel("Intensité (normalisée)")
# 🔧 Modifier ici le titre du graphique si besoin
plt.title("Superposition des Courbes Alignées\n Référence vs 5 plis")
plt.legend()
plt.tight_layout()
plt.show()

# ==============================================================================
# SECTION 6 : Quantification des Écarts Absolus Entre Paires
# ==============================================================================
plt.figure(figsize=(8, 6))
all_diff = []

for t in range(n_curve):
    diff_abs = np.abs(data_norm[t, :] - aligned_data2_individual[t, :])
    all_diff.append(diff_abs)
    plt.plot(positions, diff_abs, color='gray', alpha=0.3)

mean_diff = np.mean(np.array(all_diff), axis=0)
plt.plot(positions, mean_diff, color='red', lw=2, label="Différence Moyenne")

plt.xlabel("Position (normalisée)")
plt.ylabel("Écart Absolu")
plt.ylim(0, 0.2)  # Axe Y fixe de 0 à 1
# 🔧 Modifier ici le titre du graphique si besoin
plt.title("Quantification des Écarts Absolus entre\n les Courbes Alignées")
plt.legend()
plt.tight_layout()
plt.show()
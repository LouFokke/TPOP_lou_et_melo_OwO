import numpy as np 
import matplotlib.pyplot as plt
import requests
import io
from scipy.optimize import least_squares

# ==============================================================================
# SECTION 1 : Acquisition et Prétraitement des Données
# ==============================================================================
# Modifier ici le nom et l'URL du premier fichier
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
# Modifier ici le titre du graphique si besoin
plt.figure(figsize=(10, 6))
for t in range(n_time):
    plt.plot(positions, data_norm[t, :], color='black', alpha=0.3)
moyenne_norm = np.mean(data_norm, axis=0)
plt.plot(positions, moyenne_norm, color='red', lw=2, label="Courbe Moyenne")
plt.xlabel("Position (normalisée)")
plt.ylabel("Intensité (normalisée)")
plt.title("Données Référentielles - Fichier 1")
plt.legend()
plt.tight_layout()
plt.show()

# ==============================================================================
# SECTION 3 : Acquisition et Prétraitement du Fichier 2
# ==============================================================================
# Modifier ici le nom du deuxième fichier
nom_fichier_2 = "Reslice of 5_pli_1.txt"
chemin_fichier_2 = url + nom_fichier_2
print(f"Téléchargement des données depuis : {chemin_fichier_2}")

response2 = requests.get(chemin_fichier_2)
if response2.status_code != 200:
    raise ValueError(f"Échec du téléchargement du Fichier 2 : Code {response2.status_code}")
data2 = np.loadtxt(io.StringIO(response2.text))

# Normalisation du Fichier 2
data2_min = data2.min()
data2_max = data2.max()
data2_norm = (data2 - data2_min) / (data2_max - data2_min)
n_time2, n_position2 = data2_norm.shape
common_n_position = min(n_position, n_position2)
print(f"Utilisation de {common_n_position} positions communes entre les deux fichiers.")

# Conserver les positions communes
data_norm = data_norm[:, :common_n_position]
data2_norm = data2_norm[:, :common_n_position]
positions = np.linspace(0, 1, common_n_position)

# ==============================================================================
# SECTION 4 : Alignement des Courbes du Fichier 2 sur le Fichier 1 (Par Paires)
# ==============================================================================
def align_curve_improved(ref, curve, x):
    """
    Alignement d'une courbe sur une courbe de référence en ajustant :
        - le décalage horizontal (dx),
        - le facteur de mise à l'échelle horizontal (s),
        - le facteur d'amplitude (a) et
        - le décalage vertical (b).
    
    Transformation : aligned(x) = a * curve((x - dx) / s) + b
    """
    def residual(params):
        dx, s, a, b = params
        shifted = np.interp((x - dx) / s, x, curve, left=np.nan, right=np.nan)
        diff = a * shifted + b - ref
        return np.nan_to_num(diff)
    
    # Paramètres initiaux : pas de décalage et de scaling
    init = [0, 1, 1, 0]
    res = least_squares(residual, init)
    dx, s, a, b = res.x
    aligned = a * np.interp((x - dx) / s, x, curve, left=np.nan, right=np.nan) + b
    return aligned, dx, s, a, b

# Nombre de paires à aligner = minimum nombre de courbes disponibles
n_curve = min(n_time, n_time2)
aligned_data2_individual = np.zeros((n_curve, common_n_position))
params_data2 = []

# Alignement par paire : pour chaque indice t, la courbe du Fichier 2 est alignée
# sur la courbe correspondante du Fichier 1 (qui reste inchangée).
for t in range(n_curve):
    ref_curve = data_norm[t, :]   # Fichier 1 (référence)
    curve2 = data2_norm[t, :]       # Fichier 2 (à aligner)
    aligned_curve, dx, s, a, b = align_curve_improved(ref_curve, curve2, positions)
    aligned_data2_individual[t, :] = aligned_curve
    params_data2.append((dx, s, a, b))

# ==============================================================================
# SECTION 5 : Visualisation par Paires des Courbes Alignées
# ==============================================================================
plt.figure(figsize=(10, 6))
for t in range(n_curve):
    # Affichage du Fichier 1 (référence) en noir transparent
    plt.plot(positions, data_norm[t, :], color='black', alpha=0.3, label="Fichier 1 (Référence)" if t == 0 else "")
    # Affichage du Fichier 2 (aligné) en rouge transparent
    plt.plot(positions, aligned_data2_individual[t, :], color='red', alpha=0.3, label="Fichier 2 (Aligné)" if t == 0 else "")
plt.xlabel("Position (normalisée)")
plt.ylabel("Intensité (normalisée)")
# Modifier ici le titre du graphique si besoin
plt.title("Comparaison par Paires : Fichier 1 vs Fichier 2 Aligné")
plt.legend()
plt.tight_layout()
plt.show()

# ==============================================================================
# SECTION 6 : Quantification des Différences par Paires
# ==============================================================================
# Calcul de la différence absolue entre chaque paire et affichage en gris transparent.
plt.figure(figsize=(10, 6))
all_diff = []  # Stockage des différences pour le calcul de la moyenne

for t in range(n_curve):
    diff_abs = np.abs(data_norm[t, :] - aligned_data2_individual[t, :])
    all_diff.append(diff_abs)
    plt.plot(positions, diff_abs, color='gray', alpha=0.3)

# Calcul et affichage de la courbe moyenne des différences en gris foncé
mean_diff = np.mean(np.array(all_diff), axis=0)
plt.plot(positions, mean_diff, color='red', lw=2, label="Moyenne des Différences")

plt.xlabel("Position (normalisée)")
plt.ylabel("Différence absolue")
# Pour contraindre l'échelle verticale à [0, 1]
plt.ylim(0, 1)
# Modifier ici le titre du graphique si besoin
plt.title("Quantification des Différences par Paires (Axe Y de 0 à 1)")
plt.legend(loc="upper right", fontsize='small')
plt.tight_layout()
plt.show()

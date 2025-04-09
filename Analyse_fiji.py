import numpy as np
import matplotlib.pyplot as plt
import requests
import io
from scipy.optimize import least_squares

# ==============================================================================
# Section 1 
# ==============================================================================
# ================================
# Paramètres à modifier :
# -------------------------------
# URL de base et nom du fichier à télécharger
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/refs/heads/main/Labo1/analyse_image/"
fichier_txt = "Reslice of 0_sans_def_01.txt"
path = url + fichier_txt

print(f"Téléchargement des données depuis : {path}")

# Télécharger le fichier texte
response = requests.get(path)
if response.status_code != 200:
    raise ValueError(f"Échec du téléchargement : Code {response.status_code}")

# Charger le fichier texte directement depuis la réponse HTTP
data = np.loadtxt(io.StringIO(response.text))

# ================================
# Normalisation des données
# -------------------------------
# Normaliser l'intensité pour que toutes les valeurs soient entre 0 et 1 (min-max normalization)
data_min = data.min()
data_max = data.max()
data_norm = (data - data_min) / (data_max - data_min)

# Préparation de l'axe des positions normalisé
# L'axe des positions va de 0 à 1
n_time, n_position = data_norm.shape
positions = np.linspace(0, 1, n_position)

# ================================
# Paramètres du graphique
x_label = "Position (normalisée)"
y_label = "Intensité (normalisée)"
title   = "Courbes normalisées d'intensité vs position (temps empilé)"
# ================================

print(f"Nombre d'images (temps) : {n_time}, Nombre de positions : {n_position}")

# Créer la figure pour le graphique
plt.figure(figsize=(10, 6))

# Tracer chaque courbe normalisée correspondant à une ligne de données (chaque temps)
for t in range(n_time):
    plt.plot(positions, data_norm[t, :], color='black', alpha=0.3)  # Ajuste alpha pour la transparence

# Optionnel : tracer la courbe moyenne en rouge
moyenne_norm = np.mean(data_norm, axis=0)
plt.plot(positions, moyenne_norm, color='red', lw=2, label="Courbe moyenne")

# Personnaliser le graphique
plt.xlabel(x_label)
plt.ylabel(y_label)
plt.title(title)
plt.legend()
plt.tight_layout()
plt.show()

# ---- Charger le deuxième fichier ----
# URL de base et nom du deuxième fichier à télécharger.
url2 = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/refs/heads/main/Labo1/analyse_image/"
fichier_txt2 = "Reslice of 5_pli_1.txt"
path2 = url2 + fichier_txt2

print(f"Téléchargement du deuxième fichier depuis : {path2}")

# Télécharger le deuxième fichier
response2 = requests.get(path2)
if response2.status_code != 200:
    raise ValueError(f"Échec du téléchargement du second fichier : Code {response2.status_code}")

# Charger le fichier texte directement depuis la réponse HTTP
data2 = np.loadtxt(io.StringIO(response2.text))

# ---- Normalisation des données du deuxième fichier ----
data2_min = data2.min()
data2_max = data2.max()
data2_norm = (data2 - data2_min) / (data2_max - data2_min)

# Définir les dimensions du deuxième fichier
n_time2, n_position2 = data2_norm.shape

# Adaptation automatique pour avoir le même nombre de positions :
common_n_position = min(n_position, n_position2)
print(f"Utilisation de {common_n_position} positions communes entre les deux fichiers.")

# Recadrer (crop) les matrices au nombre commun de positions
data_norm = data_norm[:, :common_n_position]
data2_norm = data2_norm[:, :common_n_position]

# Mettre à jour l'axe des positions
positions = np.linspace(0, 1, common_n_position)

# Mettre à jour les dimensions "n_position"
n_position = common_n_position
n_position2 = common_n_position

# Assurer qu'on a le même nombre de positions dans les deux fichiers
n_time2, n_position2 = data2_norm.shape
if n_position2 != n_position:
    raise ValueError("Les deux fichiers doivent avoir le même nombre de positions pour être comparés.")

# Calcul de la courbe moyenne du deuxième fichier (normalisée)
moyenne_norm2 = np.mean(data2_norm, axis=0)

# ==============================================================================
# Section 2 : Alignement optimisé des courbes en x ET en y sur la forme générale
# ==============================================================================
def align_curve(ref, curve, x):
    """
    Aligne une courbe sur une courbe de référence.
    
    Paramètres :
      - ref : tableau numpy représentant la courbe de référence (valeurs d'intensité)
      - curve : tableau numpy représentant la courbe à aligner
      - x : axe des positions (normalisé)
    
    Retourne :
      - aligned : courbe alignée
      - dx, a, b : paramètres optimaux trouvés (décalage en x, facteur d'échelle y, offset y)
    """
    # Fonction résiduelle à minimiser : différence entre la courbe transformée et la référence
    def residual(params):
        dx, a, b = params
        shifted = np.interp(x - dx, x, curve, left=np.nan, right=np.nan)
        diff = a * shifted + b - ref
        # Remplacement des NaN par zéro pour le calcul
        return np.nan_to_num(diff)
    
    # Initialisation des paramètres : pas de décalage, facteur 1, offset 0
    init = [0, 1, 0]
    res = least_squares(residual, init)
    dx, a, b = res.x
    aligned = a * np.interp(x - dx, x, curve, left=np.nan, right=np.nan) + b
    return aligned, dx, a, b

# Choix de la courbe de référence : première courbe du fichier 1 (déjà normalisée)
ref_curve = data_norm[0, :]

# Initialisation des tableaux pour stocker les courbes alignées
aligned_data1_opt = np.zeros_like(data_norm)
aligned_data2_opt = np.zeros_like(data2_norm)

# Pour stocker les paramètres d'alignement, si besoin de les examiner
params_data1 = []
params_data2 = []

# Aligner toutes les courbes du fichier 1 par rapport à ref_curve
for t in range(n_time):
    aligned_curve, dx, a, b = align_curve(ref_curve, data_norm[t, :], positions)
    aligned_data1_opt[t, :] = aligned_curve
    params_data1.append((dx, a, b))

# Aligner toutes les courbes du fichier 2 par rapport à la même référence
for t in range(n_time2):
    aligned_curve, dx, a, b = align_curve(ref_curve, data2_norm[t, :], positions)
    aligned_data2_opt[t, :] = aligned_curve
    params_data2.append((dx, a, b))

# ------------------------------------------------------------------------------
# Affichage des différences pour chaque temps après alignement optimisé
plt.figure(figsize=(10, 6))
for t in range(min(n_time, n_time2)):
    diff_curve = aligned_data1_opt[t, :] - aligned_data2_opt[t, :]
    plt.plot(positions, diff_curve, color='blue', alpha=0.3)
plt.xlabel("Position (normalisée)")
plt.ylabel("Différence d'intensité (optimisée)")
plt.title("Différences (pour chaque temps) après alignement optimisé")
plt.tight_layout()
plt.show()

# ------------------------------------------------------------------------------
# Visualisation superposée des courbes alignées optimisées pour chaque temps
plt.figure(figsize=(10, 6))
for t in range(min(n_time, n_time2)):
    plt.plot(positions, aligned_data1_opt[t, :], color='black', alpha=0.3, label="Fichier 1" if t == 0 else "")
    plt.plot(positions, aligned_data2_opt[t, :], color='red', alpha=0.3, label="Fichier 2" if t == 0 else "")
plt.xlabel("Position (normalisée)")
plt.ylabel("Intensité (alignée optimisée)")
plt.title("Comparaison des courbes alignées optimisées : Fichier 1 (noir) vs Fichier 2 (rouge)")
plt.legend()
plt.tight_layout()
plt.show()
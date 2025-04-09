import numpy as np
import matplotlib.pyplot as plt
import requests
import io

# ================================
# Paramètres à modifier :
# -------------------------------
# URL de base et nom du fichier à télécharger
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/refs/heads/main/Labo1/analyse_image/"
fichier_txt = "Reslice_of_3_pli_2.txt"
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
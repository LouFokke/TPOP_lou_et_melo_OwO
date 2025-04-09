import numpy as np
import matplotlib.pyplot as plt
import requests
import io

# ================================
# Paramètres à modifier :
# -------------------------------
# Chemin vers ton fichier de données.
# URL du fichier CSV
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/Labo1/Fig/analyse_image/"
fichier_txt = "Reslice_of_0_sans_def_01"

print(f"Téléchargement des données depuis : {url}")

# Télécharger le fichier CSV
response = requests.get(url + fichier_txt)
if response.status_code != 200:
    raise ValueError(f"Échec du téléchargement : Code {response.status_code}")

# Noms des axes et titre du graphique.
x_label = "Position (pixels)"
y_label = "Intensité"
title    = "Courbes d'intensité en fonction de la position (temps empilé)"
# ================================

# Charger le fichier texte contenant la matrice d'intensités.
# Chaque ligne correspond à une image (un temps) et chaque colonne à la position sur la ligne.
data = np.loadtxt(fichier_txt)

# Dimensions du tableau : nombre d'images et nombre de positions
n_time, n_position = data.shape
print(f"Nombre d'images (temps) : {n_time}, Nombre de positions : {n_position}")

# Préparation de l'axe x (positions)
positions = np.arange(n_position)

# Créer une figure pour le graphique
plt.figure(figsize=(10, 6))

# Tracer chaque courbe correspondant à une ligne de données (chaque temps)
for t in range(n_time):
    plt.plot(positions, data[t, :], color='black', alpha=0.3)  # 'alpha' ajuste la transparence

# Optionnel : Tracer en rouge la courbe moyenne si cela t'intéresse
moyenne = np.mean(data, axis=0)
plt.plot(positions, moyenne, color='red', lw=2, label="Courbe moyenne")

# Personnaliser le graphique
plt.xlabel(x_label)
plt.ylabel(y_label)
plt.title(title)
plt.legend()
plt.tight_layout()
plt.show()
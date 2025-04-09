import numpy as np
import matplotlib.pyplot as plt
import requests
import io

# ================================
# Paramètres à modifier :
# -------------------------------
# URL de base et nom du fichier à télécharger
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/refs/heads/main/Labo1/analyse_image/"
fichier_txt = "Reslice_of_0_sans_def_01.txt"
path = url + fichier_txt

print(f"Téléchargement des données depuis : {path}")

# Télécharger le fichier texte
response = requests.get(path)
if response.status_code != 200:
    raise ValueError(f"Échec du téléchargement : Code {response.status_code}")

# Charger le fichier texte directement depuis la réponse HTTP
# On utilise io.StringIO pour traiter le contenu textuel
data = np.loadtxt(io.StringIO(response.text))

# Noms des axes et titre du graphique.
x_label = "Position "
y_label = "Intensité"
title   = "Courbes d'intensité en fonction de la position (temps empilé)"
# ================================

# Dimensions du tableau : nombre d'images (temps) et nombre de positions
n_time, n_position = data.shape
print(f"Nombre d'images (temps) : {n_time}, Nombre de positions : {n_position}")

# Préparation de l'axe des positions
positions = np.arange(n_position)

# Créer la figure pour le graphique
plt.figure(figsize=(10, 6))

# Tracer chaque courbe correspondant à une ligne de données (chaque temps)
for t in range(n_time):
    plt.plot(positions, data[t, :], color='black', alpha=0.3)  # Ajuste alpha pour la transparence

# Optionnel : tracer la courbe moyenne en rouge
moyenne = np.mean(data, axis=0)
plt.plot(positions, moyenne, color='red', lw=2, label="Courbe moyenne")

# Personnaliser le graphique
plt.xlabel(x_label)
plt.ylabel(y_label)
plt.title(title)
plt.legend()
plt.tight_layout()
plt.show()
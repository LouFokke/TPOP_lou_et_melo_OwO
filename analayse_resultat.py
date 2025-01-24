import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# URL de base du repo GitHub
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/DB/data_base_fibreuse/"
fichier_csv = "big_multimode.csv"  # choix entre "big_multimode.csv", "donnee_monomode.csv" ou "leger_multimode.csv"

# Concaténer l'URL complète
file_path = url + fichier_csv
print(f"Téléchargement des données depuis : {file_path}")

try:
    # Télécharger le fichier CSV avec requests
    response = requests.get(file_path)

    # Vérifier si le téléchargement a réussi
    if response.status_code != 200:
        raise ValueError(f"Échec du téléchargement : Code {response.status_code}")

    # Lire le contenu avec pandas en précisant le séparateur
    data = pd.read_csv(io.StringIO(response.text), sep=';')

    # Vérifier si le DataFrame est vide
    if data.empty:
        raise ValueError("Le fichier CSV est vide ou n'a pas été chargé correctement.")

    # Afficher les premières lignes du DataFrame pour vérifier
    print(data.head())

    # Première colonne pour l'axe X
    x = data.iloc[:, 0]
    y = data.iloc[:, 1]  # Seconde colonne pour l'axe Y

    # Tracer la courbe
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, label="Gray Value")

    # Ajouter des labels et une légende
    plt.xlabel("Pixels sur l'image (axe X)")
    plt.ylabel("Gray Value (axe Y)")
    plt.title(f"Graphique des courbes - {fichier_csv}")
    plt.legend(title="Courbes")

    # Afficher le graphique
    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"Erreur lors du chargement des données : {e}")
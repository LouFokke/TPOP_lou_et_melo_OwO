import io
import requests
import pandas as pd
import matplotlib.pyplot as plt

# URL du fichier CSV
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/DB/data_base_glendu/"
fichier_csv = "D_Loi_de_malus.csv"  

file_path = url + fichier_csv
print(f"Téléchargement des données depuis : {file_path}")

try:
    # Télécharger le fichier CSV
    response = requests.get(file_path)
    if response.status_code != 200:
        raise ValueError(f"Échec du téléchargement : Code {response.status_code}")

    # Lire le CSV avec pandas
    data = pd.read_csv(io.StringIO(response.text), sep=';', encoding='utf-8')

    # Vérifier le fichier
    print("Aperçu des données :")
    print(data.head())

    # Convertir les colonnes en numériques pour éviter les erreurs
    data = data.apply(pd.to_numeric, errors='coerce')

    # Vérifier si le fichier est vide
    if data.empty:
        raise ValueError("Le fichier CSV est vide ou mal chargé.")

    # Initialisation de l'objet figure
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Parcourir toutes les colonnes par paires X-Y
    for i in range(0, len(data.columns), 2):
        if i + 1 >= len(data.columns):
            raise ValueError("Le nombre de colonnes n'est pas pair.")
        
        x_col = data.columns[i]  # Colonne X
        y_col = data.columns[i + 1]  # Colonne Y
        
        # Récupérer les données pour chaque paire X-Y
        x = data[x_col]
        y = data[y_col]
        
        # Vérifier les données
        print(f"Colonne X : {x_col}")
        print(f"Colonne Y : {y_col}")
        print(f"Données X : {x}")
        print(f"Données Y : {y}")
        
        # Tracer la courbe
        ax1.plot(x, y, label=f"Mesurés en laboratoire")

    # Ajouter des labels
    ax1.set_xlabel("Angle du polariseur [°]")
    ax1.set_ylabel("Intensité lumineuse []")

    # Ajouter une légende
    ax1.legend(title="Légende")

    # Afficher le graphique
    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"Erreur : {e}")

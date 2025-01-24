import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# URL du fichier CSV
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/DB/data_base_fibreuse/"
fichier_csv = "donnee_monomode.csv"  # choix entre "big_multimode.csv", "donnee_monomode.csv" ou "leger_multimode.csv"

file_path = url + fichier_csv
print(f"Téléchargement des données depuis : {file_path}")

try:
    # Télécharger le fichier CSV
    response = requests.get(file_path)
    if response.status_code != 200:
        raise ValueError(f"Échec du téléchargement : Code {response.status_code}")

    # Lire le CSV avec pandas
    data = pd.read_csv(io.StringIO(response.text), sep=',', encoding='utf-8')

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
        x_col = data.columns[i]  # Colonne X
        y_col = data.columns[i + 1]  # Colonne Y
        
        # Récupérer les données pour chaque paire X-Y
        x = data[x_col]
        y = data[y_col]
        
        # Tracer la courbe
        ax1.plot(x, y, label=f"{x_col} vs {y_col}")

    # Ajouter des labels
    ax1.set_xlabel("Valeur X")
    ax1.set_ylabel("Valeur Y")
    ax1.set_title(f"Graphique des courbes - {fichier_csv}")

    # Ajouter une légende
    ax1.legend(title="Courbes")

    # Afficher le graphique
    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"Erreur : {e}")
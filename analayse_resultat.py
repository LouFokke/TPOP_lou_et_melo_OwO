import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# URL du fichier CSV
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/DB/data_base_diffrac/"
fichier_csv = "2 Fentes.csv"  
fichier_csv2 = "Diffraction (1 fente).csv"

file_path = url + fichier_csv
print(f"Téléchargement des données depuis : {file_path}")

try:
    # Télécharger le fichier CSV
    response = requests.get(file_path)
    if response.status_code != 200:
        raise ValueError(f"Échec du téléchargement : Code {response.status_code}")

    # Lire le CSV avec pandas
    data = pd.read_csv(io.StringIO(response.text), sep=',', encoding='utf-8')

    response2 = requests.get(url + fichier_csv2)
    if response2.status_code != 200:
        raise ValueError(f"Échec du téléchargement : Code {response2.status_code}")

    data2 = pd.read_csv(io.StringIO(response2.text), sep=',', encoding='utf-8')
    data2 = data2.apply(pd.to_numeric, errors='coerce')
    if data2.empty:
        raise ValueError("Le deuxième fichier CSV est vide ou mal chargé.")



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
        ax1.plot(x, y, label=f"Patron de 2 fentes (a=0.04, d=0.25)")
    for i in range(0, len(data2.columns), 2):
        x_col2 = data2.columns[i]  
        y_col2 = data2.columns[i + 1]  
        x2 = data2[x_col2]
        y2 = data2[y_col2]
        ax1.plot(x2, y2, label=f"Patron d'une fente (a=0.04)")


    # Ajouter des labels
    ax1.set_xlabel("Position [cm]")
    ax1.set_ylabel("Intensité lumineuse normalisée []")
    ax1.set_title(f"Graphique d'un patron de diffraction/interférence")

    # Ajouter une légende
    ax1.legend(title="Légende")

    # Afficher le graphique
    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"Erreur : {e}")
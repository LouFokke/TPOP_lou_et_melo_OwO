import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# URL du fichier CSV
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/DB/data_base_diffrac/"
fichier_csv = "fente_analyse.csv"  
fichier_csv2 = "Rond_analyse.csv"

print(f"Téléchargement des données depuis : {url}")

try:
    # Télécharger le fichier CSV
    response = requests.get(url + fichier_csv)
    if response.status_code != 200:
        raise ValueError(f"Échec du téléchargement : Code {response.status_code}")

    # Lire le CSV avec pandas
    data = pd.read_csv(io.StringIO(response.text), sep=',', encoding='utf-8')
    data = data.apply(pd.to_numeric, errors='coerce')
    if data.empty:
        raise ValueError("Le fichier CSV est vide ou mal chargé.")



    response2 = requests.get(url + fichier_csv2)
    if response2.status_code != 200:
        raise ValueError(f"Échec du téléchargement : Code {response2.status_code}")

    data2 = pd.read_csv(io.StringIO(response2.text), sep=',', encoding='utf-8')
    data2 = data2.apply(pd.to_numeric, errors='coerce')
    if data2.empty:
        raise ValueError("Le deuxième fichier CSV est vide ou mal chargé.")



    # Vérifier les fichiers
    print("Aperçu des données 1:")
    print(data.head())

    print("Aperçu des données 2:")
    print(data2.head())


    # Initialisation de l'objet figure
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Parcourir toutes les colonnes par paires X-Y
    for i in range(0, len(data.columns), 2):
        x_col = data.columns[i]      # Colonne X
        y_col = data.columns[i + 1]  # Colonne Y
        
        # Récupérer les données pour chaque paire X-Y
        x = data[x_col]
        y = data[y_col]
        
        # Tracer la courbe
        ax1.plot(x, y, label=f"Patron de diffraction de la fente")


    # Parcourir toutes les colonnes par paires X-Y
    for i in range(0, len(data2.columns), 2):
        x_col2 = data2.columns[i]      # Colonne X
        y_col2 = data2.columns[i + 1]  # Colonne Y

        # Récupérer les données pour chaque paire X-Y  
        x2 = data2[x_col2]
        y2 = data2[y_col2]

        # Tracer la courbe
        ax1.plot((x2+16)*1.25, y2, label=f"Patron de diffraction de l'ouverture circulaire")


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
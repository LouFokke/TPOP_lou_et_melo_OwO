import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# URL du fichier CSV
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/DB/Donnees_proj_1/Donnees_de_simulation/"
fichier_csv = "95_pourcents_difference.csv"  

file_path = url + fichier_csv
print(f"Téléchargement des données depuis : {file_path}")

try:
    # Télécharger le fichier CSV
    response = requests.get(file_path)
    if response.status_code != 200:
        raise ValueError(f"Échec du téléchargement : Code {response.status_code}")

    # Lire le CSV avec pandas
    data = pd.read_csv(io.StringIO(response.text), sep=',', encoding='utf-8')
    data = data.apply(pd.to_numeric, errors='coerce')

    # Vérifier si le fichier est vide
    if data.empty:
        raise ValueError("Le fichier CSV est vide ou mal chargé.")

    # Vérifier le fichier
    print("Aperçu des données :")
    print(data.head())

    # Initialisation de l'objet figure
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Tracer la première courbe (1ère et 2e colonnes)
    x = data.iloc[:, 0]  # 1ère colonne
    y = data.iloc[:, 1]  # 2e colonne
    ax1.plot(x, y, label="Température aux extrémités de la plaque")

    # Tracer la deuxième courbe (1ère et 3e colonnes)
    y2 = data.iloc[:, 2]  # 3e colonne
    ax1.plot(x, y2, label="Température au centre de la plaque")

    # Calculer la plus grande différence de température et le moment correspondant
    differences = abs(y - y2)
    max_diff = differences.max()
    idx_max_diff = differences.idxmax()
    x_max_diff = x.iloc[idx_max_diff]
    y_max_diff = (y.iloc[idx_max_diff] + y2.iloc[idx_max_diff]) / 2  # moyenne pour placer le point au milieu

    # Ajouter un point rouge
    ax1.plot(x_max_diff, y_max_diff, 'ro', label="Différence maximale")

    # Annoter ce point sans flèche
    ax1.text(x_max_diff + (x.max() * 0.05), y_max_diff,
             f"{max_diff:.2f} °C à {x_max_diff:.1f} s",
             fontsize=9,
             color='red')

    # Ajouter des labels
    ax1.set_xlabel("Temps [s]")
    ax1.set_ylabel("Température [°C]")
    ax1.set_title("Comparaison de la température en deux points sur la plaque en fonction du temps")

    # Ajouter une légende
    ax1.legend(title=f"Légende\nDifférence max = {max_diff:.2f} °C")

    # Afficher le graphique
    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"Erreur : {e}")

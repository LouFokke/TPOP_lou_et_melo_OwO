import pandas as pd
import matplotlib.pyplot as plt
import requests
import io
import numpy as np

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

    # Paramètres pour transformer les valeurs de X
    centrage = 308
    division = 120

    # Parcourir toutes les colonnes par paires X-Y
    for i in range(0, len(data.columns), 2):
        x_col = data.columns[i]      # Colonne X
        y_col = data.columns[i + 1]  # Colonne Y
        
        # Récupérer les données pour chaque paire X-Y
        x = data[x_col]
        y = data[y_col]
        
        # Tracer la courbe
        ax1.plot(x, y, color='gray', label=f"Patron de diffraction de la fente")

    # Parcourir toutes les colonnes par paires X-Y
    for i in range(0, len(data2.columns), 2):
        x_col2 = data2.columns[i]      # Colonne X
        y_col2 = data2.columns[i + 1]  # Colonne Y

        # Récupérer les données pour chaque paire X-Y  
        x2 = data2[x_col2]
        y2 = data2[y_col2]

        # Tracer la courbe
        ax1.plot((x2+16)*1.25, y2, color='black',linestyle='--', label=f"Patron de diffraction de l'ouverture circulaire")

    # Ajouter des labels
    ax1.set_xlabel("Position en nombre de largeur du premier maximum")
    ax1.set_ylabel("Intensité lumineuse normalisée")
    ax1.set_title(f"Graphique d'un patron de diffraction/interférence")

    # On définit les positions (en unités normalisées) des lignes verticales pointillées
    vertical_values = np.array([0, 0.5, -0.5, -0.8, 0.8, 1.0, -1.0, 1.3, -1.3, 1.65, -1.65])
    # On trie ces valeurs pour qu'elles s'affichent dans l'ordre croissant sur l'axe
    sorted_vertical = np.sort(vertical_values)

    # Appliquer les graduations sur l'axe des X uniquement aux positions des lignes verticales
    ax1.set_xticks(sorted_vertical * division + centrage)
    ax1.set_xticklabels([f"{tick:.2f}" for tick in sorted_vertical])
    
    # Limiter l'affichage de l'axe X à l'intervalle [-2.5, 2.5] en espace normalisé
    ax1.set_xlim([-2.5 * division + centrage, 2.5 * division + centrage])

    # Ajouter des lignes verticales pointillées aux positions définies
    # Pour chaque axvline, on ne met pas de label afin qu'elle ne figure pas dans la légende
    ax1.axvline(x=0 * division + centrage, color='gray', linestyle=':', linewidth=1)
    ax1.axvline(x=0.5 * division + centrage, color='lightblue', linestyle=':', linewidth=1)
    ax1.axvline(x=-0.5 * division + centrage, color='lightblue', linestyle=':', linewidth=1)
    ax1.axvline(x=(-0.8 * division + centrage), color='orange', linestyle=':', linewidth=1)
    ax1.axvline(x=(0.8 * division + centrage), color='orange', linestyle=':', linewidth=1)
    ax1.axvline(x=(1.0 * division + centrage), color='lime', linestyle=':', linewidth=1)
    ax1.axvline(x=(-1.0 * division + centrage), color='lime', linestyle=':', linewidth=1)
    ax1.axvline(x=(1.3 * division + centrage), color='red', linestyle=':', linewidth=1)
    ax1.axvline(x=(-1.3 * division + centrage), color='red', linestyle=':', linewidth=1)
    ax1.axvline(x=(1.65 * division + centrage), color='red', linestyle=':', linewidth=1)
    ax1.axvline(x=(-1.65 * division + centrage), color='red', linestyle=':', linewidth=1)

    # Ajouter une légende en plusieurs colonnes, en haut à droite (les axvline ne sont plus incluses)
    ax1.legend(title="Légende", loc="upper right", ncol=3, fontsize="small", title_fontsize="small")

    # --- Modification de l'axe des Y ---
    # Augmenter l'axe des Y pour qu'il s'arrête à 250
    ax1.set_ylim(0, 250)
    # Normaliser l'axe des Y pour que 1 corresponde à 203, et adapter les graduations
    normalized_max = 210 / 203  # Valeur normalisée du max (environ 1.23)
    step = 0.2  # pas de graduation en espace normalisé (modifiable)
    normalized_ticks = np.arange(0, normalized_max + step, step)
    if 1.0 not in normalized_ticks:
        normalized_ticks = np.sort(np.append(normalized_ticks, 1.0))
    new_yticks = normalized_ticks * 203
    ax1.set_yticks(new_yticks)
    ax1.set_yticklabels([f"{tick:.2f}" for tick in normalized_ticks])

    # Afficher le graphique
    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"Erreur : {e}")

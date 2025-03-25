import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Augmenter la taille globale de la police
plt.rcParams.update({'font.size': 20})

# Fonction à ajuster
def eq_chaleur(x, m, b, c):
    return np.log(np.maximum(x + b, 1e-6)) / np.log(m) + c  # Évite log(0) ou log(négatif)

# Fonction pour calculer R²
def calculate_r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)

# URL du fichier CSV
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/DB/Donnees_proj_1/"
fichier_csv = "Sans_calibration.csv"
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

    # Convertir les colonnes en numériques
    data = data.apply(pd.to_numeric, errors='coerce')

    # Vérifier si le fichier est vide
    if data.empty:
        raise ValueError("Le fichier CSV est vide ou mal chargé.")

    # Initialisation de l'objet figure
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Parcourir toutes les colonnes par paires Y-X (inversion de l'ordre)
    for i in range(0, len(data.columns), 2):
        if i + 1 >= len(data.columns):
            raise ValueError("Le nombre de colonnes n'est pas pair.")

        y_col = data.columns[i]
        x_col = data.columns[i + 1]

        y = data[y_col].dropna()
        x = data[x_col].dropna()

        # Normalisation de x
        x_min = np.min(x)
        x_shifted = x - x_min + 1e-6  # Décale x pour éviter les valeurs négatives

        # Ajustement de la courbe
        popt, pcov = curve_fit(eq_chaleur, x_shifted, y, p0=[2, 1, 0],
                               bounds=([1, -x_min + 1e-6, -np.inf], [np.inf, np.inf, np.inf]))

        # Calcul des valeurs ajustées
        y_pred = eq_chaleur(x_shifted, *popt)
        r_squared = calculate_r_squared(y, y_pred)
        print(f"R² = {r_squared:.4f}")

        # Tracer les données expérimentales
        ax1.plot(x, y, 'o', label=f"Données exp. {y_col} vs {x_col}")

        # Tracer la courbe ajustée
        x_fit = np.linspace(min(x), max(x), 500)
        y_fit = eq_chaleur(x_fit - x_min + 1e-6, *popt)
        ax1.plot(x_fit, y_fit, '--', label=f"Modèle ({y_col}) R² = {r_squared:.3f}")

        # Affichage de la formule corrigée sur le graphique
        equation_text = f"$y = \log_{{{popt[0]:.3f}}}(x - {x_min:.3f} + {popt[1]:.3f}) + {popt[2]:.3f}$"
        ax1.text(0.05, 0.95 - 0.1 * (i // 2), equation_text, transform=ax1.transAxes, fontsize=16,
                 verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

    # Ajouter des labels
    ax1.set_xlabel("Variable X")
    ax1.set_ylabel("Variable Y")

    # Ajouter une légende
    ax1.legend(title="Légende")

    # Afficher le graphique
    plt.tight_layout()
    plt.show()

    # Affichage de l'équation ajustée dans la console
    print(f"Équation ajustée : y = log_({popt[0]:.3f})(x - {x_min:.3f} + {popt[1]:.3f}) + {popt[2]:.3f}")

except Exception as e:
    print(f"Erreur : {e}")
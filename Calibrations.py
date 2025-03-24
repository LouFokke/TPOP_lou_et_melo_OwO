import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Augmenter la taille globale de la police
plt.rcParams.update({'font.size': 20})

# Fonction à ajuster
def eq_chaleur(x, k, c, b):
    return k ** (x + c) + b

# Fonction pour calculer R²
def calculate_r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)

# URL du fichier CSV
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/DB/Donnees_proj_1/"
fichier_csv = "calibration_custom.csv"
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

    # Parcourir toutes les colonnes par paires X-Y
    for i in range(0, len(data.columns), 2):
        if i + 1 >= len(data.columns):
            raise ValueError("Le nombre de colonnes n'est pas pair.")
        
        x_col = data.columns[i]
        y_col = data.columns[i + 1]
        
        x = data[x_col]
        y = data[y_col]
        
        # Normalisation de x pour éviter des valeurs trop grandes
        x_norm = x / max(x)
        
        # Ajustement de la courbe
        popt, pcov = curve_fit(eq_chaleur, x_norm, y, p0=[1, 0, min(y)])
        
        # Calcul des valeurs ajustées
        y_pred = eq_chaleur(x_norm, *popt)
        r_squared = calculate_r_squared(y, y_pred)
        print(f"R² = {r_squared:.4f}")
        
        # Tracer les données expérimentales
        ax1.plot(x, y, 'o', label="Données expérimentales")
        
        # Tracer la courbe ajustée
        x_fit_norm = np.linspace(min(x_norm), max(x_norm), 500)
        y_fit = eq_chaleur(x_fit_norm, *popt)
        ax1.plot(x_fit_norm * max(x), y_fit, '--', label=f"Modèle théorique, R² = {r_squared:.3f}")
    
    # Ajouter des labels
    ax1.set_xlabel("Température [°C]")
    ax1.set_ylabel("Intensité lumineuse moyenne de la zone [Adu]")
    
    # Ajouter une légende
    ax1.legend(title="Légende")
    
    # Afficher le graphique
    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"Erreur : {e}")
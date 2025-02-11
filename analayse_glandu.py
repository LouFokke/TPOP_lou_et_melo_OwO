import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Augmenter la taille globale de la police (par défaut environ 10, ici on passe à 20)
plt.rcParams.update({'font.size': 20})

# Fonction à ajuster (loi de Malus : I = I0 * cos²(θ - θ0))
def malus_law(theta, I0, theta0):
    return I0 * np.cos(np.radians(theta - theta0)) ** 2

# Fonction pour calculer R²
def calculate_r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)  # Somme des carrés des résidus
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)  # Somme totale des carrés
    r_squared = 1 - (ss_res / ss_tot)  # Coefficient de détermination R²
    return r_squared

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
        
        x_col = data.columns[i]  # Colonne X (angle)
        y_col = data.columns[i + 1]  # Colonne Y (intensité)
        
        # Récupérer les données pour chaque paire X-Y
        x = data[x_col]
        y = data[y_col]
        
        # Vérifier les données
        print(f"Colonne X : {x_col}")
        print(f"Colonne Y : {y_col}")
        print(f"Données X : {x}")
        print(f"Données Y : {y}")
        
        # Curve fitting : ajuster la loi de Malus aux données
        popt, pcov = curve_fit(malus_law, x, y, p0=[max(y), 0])  # p0 : estimations initiales
        I0, theta0 = popt  # Paramètres optimisés
        
        # Calculer les valeurs prédites par le modèle
        y_pred = malus_law(x, *popt)
        
        # Calculer R²
        r_squared = calculate_r_squared(y, y_pred)
        print(f"R² = {r_squared:.4f}")
        
        # Tracer les données expérimentales
        ax1.plot(x, y, 'o', label="Données expérimentales")
        
        # Tracer la courbe ajustée
        x_fit = np.linspace(min(x), max(x), 500)  # Générer des points pour une courbe lisse
        y_fit = malus_law(x_fit, *popt)  # Calculer les valeurs ajustées
        ax1.plot(x_fit, y_fit, '--', label=f"Loi de Malus, R² = {r_squared:.3f}")
    
    # Ajouter des labels
    ax1.set_xlabel("Angle du polariseur [°]")
    ax1.set_ylabel("Intensité lumineuse []")
    ax1.set_title("")
    
    # Ajouter une légende
    ax1.legend(title="Légende")
    
    # Afficher le graphique
    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"Erreur : {e}")
import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

# Augmenter la taille globale de la police (par défaut environ 10, ici on passe à 20)
plt.rcParams.update({'font.size': 20})

# Fonction à ajuster (loi de Malus : I = I0 * cos²(θ - θ0))
def malus_law(theta, I0, theta0):
    return I0 * np.cos(np.radians(theta - theta0)) ** 2

# Fonction pour calculer R²
def calculate_r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)  # Somme des carrés des résidus
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)  # Somme totale des carrés
    r_squared = 1 - (ss_res / ss_tot)  # Coefficient de détermination R²
    return r_squared

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
        
        x_col = data.columns[i]  # Colonne X (angle)
        y_col = data.columns[i + 1]  # Colonne Y (intensité)
        
        # Récupérer les données pour chaque paire X-Y
        x = data[x_col]
        y = data[y_col]
        
        # Vérifier les données
        print(f"Colonne X : {x_col}")
        print(f"Colonne Y : {y_col}")
        print(f"Données X : {x}")
        print(f"Données Y : {y}")
        
        # Curve fitting : ajuster la loi de Malus aux données
        popt, pcov = curve_fit(malus_law, x, y, p0=[max(y), 0])  # p0 : estimations initiales
        I0, theta0 = popt  # Paramètres optimisés
        
        # Calculer les valeurs prédites par le modèle
        y_pred = malus_law(x, *popt)
        
        # Calculer R²
        r_squared = calculate_r_squared(y, y_pred)
        print(f"R² = {r_squared:.4f}")
        
        # Tracer les données expérimentales
        ax1.plot(x, y, 'o', label="Données expérimentales")
        
        # Tracer la courbe ajustée
        x_fit = np.linspace(min(x), max(x), 500)  # Générer des points pour une courbe lisse
        y_fit = malus_law(x_fit, *popt)  # Calculer les valeurs ajustées
        ax1.plot(x_fit, y_fit, '--', label=f"Loi de Malus, R² = {r_squared:.3f}")
    
    # Ajouter des labels
    ax1.set_xlabel("Angle du polariseur [°]")
    ax1.set_ylabel("Intensité lumineuse [μA]")
    ax1.set_title("Vérification de la loi de Malus")
    
    # Ajouter une légende
    ax1.legend(title="Légende")
    
    # Afficher le graphique
    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"Erreur : {e}")

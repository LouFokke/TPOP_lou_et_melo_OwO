import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

plt.rcParams.update({'font.size': 25})

# Fonction de chaleur
def eq_chaleur(x, m, b, c):
    return np.log(np.maximum(x + b, 1e-6)) / np.log(m) + c

# R²
def calculate_r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)

# URL du CSV
url = "https://raw.githubusercontent.com/LouFokke/TPOP_lou_et_melo_OwO/main/DB/Donnees_proj_1/calibration_custom.csv"
print(f"Téléchargement des données depuis : {url}")

try:
    # Chargement des données
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Échec du téléchargement : Code {response.status_code}")
    data = pd.read_csv(io.StringIO(response.text), sep=';', encoding='utf-8')
    data = data.apply(pd.to_numeric, errors='coerce')

    if data.empty:
        raise ValueError("Le fichier CSV est vide ou mal chargé.")

    # Initialisation figure
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Choisir la première paire de colonnes seulement
    y_col = data.columns[0]
    x_col = data.columns[1]
    y = data[y_col].dropna()
    x = data[x_col].dropna()

    x_min = np.min(x)
    x_shifted = x - x_min + 1e-6

    popt, pcov = curve_fit(eq_chaleur, x_shifted, y, p0=[2, 1, 0],
                           bounds=([1, -x_min + 1e-6, -np.inf], [np.inf, np.inf, np.inf]))

    y_pred = eq_chaleur(x_shifted, *popt)
    r_squared = calculate_r_squared(y, y_pred)
    print(f"R² = {r_squared:.4f}")

    # Tracé
    ax1.plot(x, y, 'o', label="Données exp.")
    x_fit = np.linspace(min(x), max(x), 500)
    y_fit = eq_chaleur(x_fit - x_min + 1e-6, *popt)
    ax1.plot(x_fit, y_fit, '--', label=f"Modèle R² = {r_squared:.3f}")

    equation_text = f"$y = \log_{{{popt[0]:.3f}}}(x - {x_min+popt[1]:.3f}) {popt[2]:.3f}$"
    ax1.text(0.05, 0.95, equation_text, transform=ax1.transAxes, fontsize=20,
             verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"))

    ax1.set_xlabel("ADU")
    ax1.set_ylabel("Température (C)")
    ax1.legend(title="Légende")
    plt.tight_layout()
    plt.show()

    # === Partie 2 : utiliser la formule ===
    m, b, c = popt
    print("\n--- Utilisation de la formule ajustée ---")
    print(f"Formule : y = log_{m:.3f}(x - {(x_min+b):.3f}) {c:.3f}")
    print("Entrez 'q' pour quitter.\n")

    def utiliser_formule(x):
        return eq_chaleur(x - x_min + 1e-6, m, b, c)

    while True:
        try:
            x_val = input("x = ")
            if x_val.lower() == 'q':
                break
            x_val = float(x_val)
            y_val = utiliser_formule(x_val)
            print(f"→ Pour x = {x_val:.3f}, y = {y_val:.3f} °C\n")
        except Exception as e:
            print(f"Erreur : {e}\n")

except Exception as e:
    print(f"Erreur : {e}")

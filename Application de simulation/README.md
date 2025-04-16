# Simulateur de Température

Ce projet est une application permettant d'effectuer des simulations thermiques bidimensionnelles avec une interface graphique intuitive, construite avec PySide6 et Matplotlib.

## ⚙️ Prérequis

Avant d'exécuter l'application, assurez-vous d'avoir :

- **Python 3.6 ou plus récent** installé sur votre ordinateur.

Vous pouvez vérifier votre version de Python en ouvrant un terminal et en exécutant :

```bash
python --version
```

## 🛠️ Installation et configuration

### Étape 1 : Créer un environnement virtuel (venv)

Dans votre dossier de projet, ouvrez un terminal et exécutez la commande suivante :

**Sous Linux ou macOS :**

```bash
python3 -m venv venv
```

**Sous Windows :**

```cmd
python -m venv venv
```

### Étape 2 : Activer l'environnement virtuel

Activez le venv que vous venez de créer :

**Linux ou macOS :**

```bash
source venv/bin/activate
```

**Windows :**

```cmd
venv\Scripts\activate
```

Vous devriez voir `(venv)` apparaître à gauche dans votre terminal, indiquant que l'environnement virtuel est actif.

### Étape 3 : Installer les dépendances

Une fois l'environnement activé, installez les librairies Python nécessaires au projet :

```bash
pip install -r requirements.txt
```

Cette commande installera automatiquement toutes les bibliothèques requises spécifiées dans le fichier `requirements.txt`.

## 🚀 Lancer l'application

Une fois les étapes précédentes effectuées, naviguez vers le dossier `Simulation_physique` et lancez l'application avec la commande suivante :

```bash
cd Simulation_physique
python main.py
```

L'application démarrera et l'interface graphique s'affichera.

## 🔧 Configuration des tests

### Tab "Paramètres"

Pour configurer un test, naviguez vers l'onglet **Paramètres** afin de modifier les paramètres souhaités. Il est impératif de ne laisser aucun champ vide, sinon une erreur surviendra lors de l'enregistrement des paramètres. Une fois les modifications effectuées, cliquez sur le bouton **Enregistrer les paramètres** pour sauvegarder vos changements avant de commencer un test.

Vous avez également la possibilité de charger directement un fichier JSON existant (assurez-vous que celui-ci possède la même structure que `parametres.json`) à l'aide du bouton **Charger un fichier JSON**, et de sauvegarder une copie de votre configuration actuelle avec le bouton **Sauvegarder une copie du fichier JSON**. L'utilisation de `QFileDialog` assure normalement une compatibilité multi-système. Toutefois, en cas de problèmes, il est recommandé d'exécuter l'application sous Windows pour assurer la meilleure stabilité.

### Configuration spécifique : champs On/Off

Dans les sections **TEC** et **Perturbation** :
- Le champ **On/Off** fonctionne par valeurs séparées par des virgules.
- Entrer `0` signifie que le paramètre sera activé (**On**) pendant toute la durée du test.
- `0, 500` signifie que le paramètre sera activé (**On**) au début et désactivé (**Off**) à 500 secondes.
- `0, 500, 1000` signifie que le paramètre sera activé (**On**) à 0 seconde, désactivé (**Off**) à 500 secondes, puis réactivé (**On**) à 1000 secondes, et ainsi de suite.

Pour désactiver complètement le TEC ou la Perturbation, mettez la valeur 0 dans les champs correspondants (Courant pour le TEC et Puissance pour la perturbation).

### Tab "Simulation"

Pour démarrer une simulation, rendez-vous dans l'onglet **Simulation** et cliquez sur le bouton **Démarrer le test**. Si vous souhaitez arrêter le test avant la durée définie, vous pouvez cliquer sur **Arrêter le test**.

Après la simulation, une fenêtre de votre gestionnaire de fichiers s'ouvrira automatiquement pour vous permettre de choisir l'emplacement d'enregistrement de vos résultats en CSV. Si vous ne souhaitez pas sauvegarder le fichier, fermez simplement la fenêtre.




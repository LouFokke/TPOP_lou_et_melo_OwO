import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('QtAgg')  # ou 'Qt5Agg', selon la version
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from GUI.MainWindow import MainWindow
import os
import sys

# Augmenter la taille globale de la police (par défaut environ 10, ici on passe à 20)
plt.rcParams.update({'font.size': 20})

def resource_path(relative_path):
    """Retourne le chemin absolu vers la ressource.
    Permet de gérer l'emplacement d'un fichier dans l'environnement de développement et dans l'exécutable compilé."""
    try:
        # Lorsque l'application est compilée, sys._MEIPASS contient le chemin vers les ressources extraites.
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    

    app = QApplication([])

    icon_path = os.path.abspath("icon.ico")
    icon = QIcon(icon_path)

    #Pour le développement :
    script_dir = os.path.dirname(os.path.abspath(__file__))
    param_path = os.path.join(script_dir,"parametres.json")
    window = MainWindow(param_file_path=param_path)

    # # Pour la version compilée :
    # json_path = resource_path("parametres.json")
    # window = MainWindow(param_file_path=json_path)  # pour version compiler

    window.setWindowIcon(icon)  # Assigne l'icône à la fenêtre principale
    
    app.setWindowIcon(icon)

    window.show()
    app.exec()

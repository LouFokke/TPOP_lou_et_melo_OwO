import datetime
import sys
import json

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTabWidget
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from sim_2d_propre import ThermalSimulation
from GUI.parametersTab import ParametersTab

class MainWindow(QMainWindow):
    
    def __init__(self, param_file_path, parent=None):
        super().__init__(parent)
        
        self.param_file_path = param_file_path
        
        # Garde les références pour la simulation, le canvas, etc.
        self.simulation = None
        self.canvas = None

        self.is_running = False

        # Crée un widget central qui sera un QTabWidget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Prépare deux onglets:
        #   1) "Simulation"
        #   2) "Paramètres"
        self.init_tabs()

        self.setWindowTitle("Interface Simulation Physique")

    def init_tabs(self):
        """Crée et ajoute deux onglets : Simulation et Paramètres."""
        # Onglet Simulation
        self.tab_simulation = QWidget()
        self.tab_widget.addTab(self.tab_simulation, "Simulation")

        # Onglet Paramètres
        self.tab_parameters = ParametersTab(self.param_file_path)
        self.tab_widget.addTab(self.tab_parameters, "Paramètres")

        # Connecte le signal de changement de fichier de paramètres à la méthode de mise à jour
        self.tab_parameters.paramFilePathChanged.connect(self.on_param_file_changed)

        # Configure l'UI de l'onglet "Simulation"
        self.setup_simulation_tab_layout()

    def setup_simulation_tab_layout(self):
        """
        Configure l'interface de l'onglet Simulation
        (figure matplotlib + boutons start/stop).
        """
        sim_layout = QVBoxLayout(self.tab_simulation)

        # Créer une simulation initiale pour que l'utilisateur voie une figure.
        self.simulation = ThermalSimulation(self.param_file_path, on_simulation_end=self.simulation_ended_cb)

        # Créer un canvas Matplotlib pour la figure de la simulation
        self.canvas = FigureCanvas(self.simulation.fig)
        sim_layout.addWidget(self.canvas)

        # Rangée de boutons (Start/Stop)
        button_layout = QHBoxLayout()

        self.btn_start = QPushButton("Démarrer le Test")
        self.btn_start.clicked.connect(self.on_start_test)
        button_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("Arrêter le Test")
        self.btn_stop.clicked.connect(self.on_stop_test)
        button_layout.addWidget(self.btn_stop)

        sim_layout.addLayout(button_layout)

    def on_start_test(self):
        """
        Lorsque l'utilisateur clique sur 'Démarrer le Test':
         1) On supprime l'ancienne figure.
         2) On recrée une nouvelle simulation (re-lira le JSON).
         3) On ajoute la nouvelle figure.
         4) On lance la simulation.
        """
        self.btn_start.setDisabled(True)

        # Retirer l'ancien canvas du layout
        if self.canvas is not None:
            layout = self.tab_simulation.layout()
            layout.removeWidget(self.canvas)
            self.canvas.deleteLater()
            self.canvas = None

        # Crée une nouvelle instance de simulation (utilise param_file_path => le JSON)
        self.simulation = ThermalSimulation(self.param_file_path, on_simulation_end=self.simulation_ended_cb)

        # Crée un nouveau canvas
        self.canvas = FigureCanvas(self.simulation.fig)
        self.tab_simulation.layout().insertWidget(0, self.canvas)

        self.is_running = True
        # Lance la simulation
        self.simulation.start_test()

    def on_stop_test(self):
        """Arrête la simulation et réactive le bouton 'Démarrer le Test'."""
        self.btn_start.setEnabled(True)
        if self.simulation is not None and self.is_running:
            self.simulation.stop_test()
            self.is_running = False

    
    def simulation_ended_cb(self):
        """
        Méthode appelée automatiquement par ThermalSimulation
        lorsque la durée de simulation est atteinte.
        """
        self.btn_start.setEnabled(True)

    def on_param_file_changed(self, new_path):
        """Met à jour self.param_file_path pour la prochaine simulation."""
        self.param_file_path = new_path
        print(f"[MainWindow] Nouveau path param JSON: {self.param_file_path}")

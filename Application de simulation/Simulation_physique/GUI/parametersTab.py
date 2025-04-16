from datetime import time
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
    QPushButton, QLabel, QGroupBox, QMessageBox, QGridLayout, QFileDialog
)
from PySide6.QtCore import QTimer, Signal, Slot
import os

class ParametersTab(QWidget):
    """
    Gère l'interface permettant de modifier TOUS les paramètres
    (chargés/sauvegardés depuis le fichier JSON).
    
    - Les valeurs sont regroupées par sections (dimensions, matériaux, etc.).
    """
    paramFilePathChanged = Signal(str)  # Émet un signal lorsque le chemin du fichier JSON change

    def __init__(self, param_file_path, parent=None):
        super().__init__(parent)
        self.param_file_path = param_file_path
        self.params = {}
        self.init_ui()

    def init_ui(self):
        # Charger le JSON actuel
        self.load_params()

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)

        # ---------------------------
        # 1) Section "Dimensions"
        # ---------------------------
        group_dimensions = QGroupBox("Dimensions de la plaque(m)")
        dim_layout = QGridLayout()

        self.edit_Lx = QLineEdit(str(self.params["dimensions"]["Lx"]))
        self.edit_Ly = QLineEdit(str(self.params["dimensions"]["Ly"]))
        self.edit_e  = QLineEdit(str(self.params["dimensions"]["e"]))

        dim_layout.addWidget(QLabel("Largeur axe x:"), 0, 0)
        dim_layout.addWidget(self.edit_Lx, 0, 1)
        dim_layout.addWidget(QLabel("Largeur axe y:"), 0, 2)
        dim_layout.addWidget(self.edit_Ly, 0, 3)

        dim_layout.addWidget(QLabel("Épaisseur (e):"), 1, 0)
        dim_layout.addWidget(self.edit_e, 1, 1)

        group_dimensions.setLayout(dim_layout)

        # ---------------------------
        # 2) Section "Matériau"
        # ---------------------------
        group_material = QGroupBox("Propriétés du matériau")
        mat_layout = QGridLayout()

        self.edit_k   = QLineEdit(str(self.params["material_properties"]["k"]))
        self.edit_rho = QLineEdit(str(self.params["material_properties"]["rho"]))
        self.edit_cp  = QLineEdit(str(self.params["material_properties"]["cp"]))

        mat_layout.addWidget(QLabel("Conductivité (k):"), 0, 0)
        mat_layout.addWidget(self.edit_k, 0, 1)
        mat_layout.addWidget(QLabel("Densité (rho):"), 0, 2)
        mat_layout.addWidget(self.edit_rho, 0, 3)

        mat_layout.addWidget(QLabel("Chaleur sp. (cp):"), 1, 0)
        mat_layout.addWidget(self.edit_cp, 1, 1)

        group_material.setLayout(mat_layout)

        # ---------------------------
        # 3) Section "Conditions aux limites"
        # ---------------------------
        group_boundaries = QGroupBox("Conditions aux limites")
        bound_layout = QGridLayout()

        self.edit_h       = QLineEdit(str(self.params["boundary_conditions"]["h"]))
        self.edit_T_piece = QLineEdit(str(self.params["boundary_conditions"]["T_piece"]))

        bound_layout.addWidget(QLabel("Convection (h):"), 0, 0)
        bound_layout.addWidget(self.edit_h, 0, 1)
        bound_layout.addWidget(QLabel("Température initiale de la plaque (°C):"), 0, 2)
        bound_layout.addWidget(self.edit_T_piece, 0, 3)

        group_boundaries.setLayout(bound_layout)

        # ---------------------------
        # 4) Section "Param. de simulation"
        # ---------------------------
        group_sim_params = QGroupBox("Paramètres de simulation")
        sim_layout = QGridLayout()

        self.edit_res_spatiale   = QLineEdit(str(self.params["simulation_parameters"]["res_spatiale"]))
        self.edit_res_temporelle = QLineEdit(str(self.params["simulation_parameters"]["res_temporelle"]))
        self.edit_sim_duration   = QLineEdit(str(self.params["simulation_parameters"]["sim_duration"]))

        sim_layout.addWidget(QLabel("Résolution spatiale:"), 0, 0)
        sim_layout.addWidget(self.edit_res_spatiale, 0, 1)
        sim_layout.addWidget(QLabel("Résolution temporelle:"), 0, 2)
        sim_layout.addWidget(self.edit_res_temporelle, 0, 3)

        sim_layout.addWidget(QLabel("Durée de la simulation(s):"), 1, 0)
        sim_layout.addWidget(self.edit_sim_duration, 1, 1)

        group_sim_params.setLayout(sim_layout)

        # ---------------------------
        # 5) Section "TEC"
        # ---------------------------
        group_tec = QGroupBox("TEC")
        tec_layout = QGridLayout()

        self.edit_Lx_source = QLineEdit(str(self.params["TEC"]["Lx_source"]))
        self.edit_Ly_source = QLineEdit(str(self.params["TEC"]["Ly_source"]))
        self.edit_x_source  = QLineEdit(str(self.params["TEC"]["x_source"]))
        self.edit_y_source  = QLineEdit(str(self.params["TEC"]["y_source"]))
        self.edit_courant   = QLineEdit(str(self.params["TEC"]["courant"]))
        self.edit_couplage  = QLineEdit(str(self.params["TEC"]["couplage"]))
        self.edit_on_off_tec = QLineEdit(str(self.params["TEC"]["TEC_momment_inversion"])[1:-1])

        tec_layout.addWidget(QLabel("Largeur axe x:"), 0, 0)
        tec_layout.addWidget(self.edit_Lx_source, 0, 1)
        tec_layout.addWidget(QLabel("Largeur axe y source:"), 0, 2)
        tec_layout.addWidget(self.edit_Ly_source, 0, 3)

        tec_layout.addWidget(QLabel("Position axe x:"), 1, 0)
        tec_layout.addWidget(self.edit_x_source, 1, 1)
        tec_layout.addWidget(QLabel("Position axe y:"), 1, 2)
        tec_layout.addWidget(self.edit_y_source, 1, 3)

        tec_layout.addWidget(QLabel("Courant (A):"), 2, 0)
        tec_layout.addWidget(self.edit_courant, 2, 1)
        tec_layout.addWidget(QLabel("Couplage:"), 2, 2)
        tec_layout.addWidget(self.edit_couplage, 2, 3)
        tec_layout.addWidget(QLabel("On/Off (temps ON, temps OFF, ...):"), 3, 0)
        tec_layout.addWidget(self.edit_on_off_tec, 3, 1)

        group_tec.setLayout(tec_layout)

        # ---------------------------
        # 6) Section "Perturbation"
        # ---------------------------
        group_perturb = QGroupBox("Perturbation")
        pert_layout = QGridLayout()

        self.edit_power    = QLineEdit(str(self.params["perturbation_properties"]["power"]))
        self.edit_pos_x_perturbation = QLineEdit(str(self.params["perturbation_properties"]["pos_x"]))
        self.edit_pos_y_perturbation = QLineEdit(str(self.params["perturbation_properties"]["pos_y"]))
        self.edit_on_off_perturbation = QLineEdit(str(self.params["perturbation_properties"]["PERTU_momment_inversion"])[1:-1])


        pert_layout.addWidget(QLabel("Puissance (W):"), 0, 0)
        pert_layout.addWidget(self.edit_power, 0, 1)
        pert_layout.addWidget(QLabel("On/Off (temps ON, temps OFF, ...):"), 0, 2)
        pert_layout.addWidget(self.edit_on_off_perturbation, 0, 3)

        pert_layout.addWidget(QLabel("pos_x (m):"), 1, 0)
        pert_layout.addWidget(self.edit_pos_x_perturbation, 1, 1)

        pert_layout.addWidget(QLabel("pos_y (m):"), 1, 2)
        pert_layout.addWidget(self.edit_pos_y_perturbation, 1, 3)

        group_perturb.setLayout(pert_layout)

        # ---------------------------
        # 7) Section "Thermistances"
        # ---------------------------
        group_therm = QGroupBox("Positions de thermistances (m)")
        therm_layout = QGridLayout()

        self.edit_t1_x = QLineEdit(str(self.params["thermistances"]["pos_t1_x"]))
        self.edit_t1_y = QLineEdit(str(self.params["thermistances"]["pos_t1_y"]))
        self.edit_t2_x = QLineEdit(str(self.params["thermistances"]["pos_t2_x"]))
        self.edit_t2_y = QLineEdit(str(self.params["thermistances"]["pos_t2_y"]))
        self.edit_t3_x = QLineEdit(str(self.params["thermistances"]["pos_t3_x"]))
        self.edit_t3_y = QLineEdit(str(self.params["thermistances"]["pos_t3_y"]))

        therm_layout.addWidget(QLabel("T1 - x:"), 0, 0)
        therm_layout.addWidget(self.edit_t1_x, 0, 1)
        therm_layout.addWidget(QLabel("T1 - y:"), 0, 2)
        therm_layout.addWidget(self.edit_t1_y, 0, 3)

        therm_layout.addWidget(QLabel("T2 - x:"), 1, 0)
        therm_layout.addWidget(self.edit_t2_x, 1, 1)
        therm_layout.addWidget(QLabel("T2 - y:"), 1, 2)
        therm_layout.addWidget(self.edit_t2_y, 1, 3)

        therm_layout.addWidget(QLabel("T3 - x:"), 2, 0)
        therm_layout.addWidget(self.edit_t3_x, 2, 1)
        therm_layout.addWidget(QLabel("T3 - y:"), 2, 2)
        therm_layout.addWidget(self.edit_t3_y, 2, 3)

        group_therm.setLayout(therm_layout)

        # ---------------------------
        # 8) Bouton de sauvegarde, save/load JSON + Label status
        # ---------------------------
        
        self.btn_save = QPushButton("Enregistrer les paramètres")
        self.btn_save.clicked.connect(self.save_params)

        self.btn_load_json = QPushButton("Charger un fichier JSON")
        self.btn_load_json.clicked.connect(self.browse_json_file)

        self.btn_save_copy = QPushButton("Sauvegarder une copie du fichier JSON")
        self.btn_save_copy.clicked.connect(self.save_copy)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: red;")

        # ---------------------------
        # Assemblage final du layout
        # ---------------------------
        main_layout.addWidget(group_dimensions)
        main_layout.addWidget(group_material)
        main_layout.addWidget(group_boundaries)
        main_layout.addWidget(group_sim_params)
        main_layout.addWidget(group_tec)
        main_layout.addWidget(group_perturb)
        main_layout.addWidget(group_therm)

        main_layout.addWidget(self.btn_save)
        main_layout.addWidget(self.btn_load_json)
        main_layout.addWidget(self.btn_save_copy)
        main_layout.addWidget(self.status_label)

        main_layout.addStretch()

         # On remplit les champs avec les données chargées
        self.populate_fields_from_params()

    def load_params(self):
        """Charge le fichier JSON et stocke le dict dans self.params."""
        with open(self.param_file_path, "r") as f:
            self.params = json.load(f)


    def populate_fields_from_params(self):
        """
        Met à jour tous les QLineEdit en fonction du dictionnaire self.params.
        Appelé après load_params() ou après modifications.
        """
        # Dimensions
        self.edit_Lx.setText(str(self.params["dimensions"]["Lx"]))
        self.edit_Ly.setText(str(self.params["dimensions"]["Ly"]))
        self.edit_e.setText(str(self.params["dimensions"]["e"]))

        # Matériau
        self.edit_k.setText(str(self.params["material_properties"]["k"]))
        self.edit_rho.setText(str(self.params["material_properties"]["rho"]))
        self.edit_cp.setText(str(self.params["material_properties"]["cp"]))

        # Conditions aux limites
        self.edit_h.setText(str(self.params["boundary_conditions"]["h"]))
        self.edit_T_piece.setText(str(self.params["boundary_conditions"]["T_piece"]))

        # Paramètres de simulation
        self.edit_res_spatiale.setText(str(self.params["simulation_parameters"]["res_spatiale"]))
        self.edit_res_temporelle.setText(str(self.params["simulation_parameters"]["res_temporelle"]))
        self.edit_sim_duration.setText(str(self.params["simulation_parameters"]["sim_duration"]))

        # TEC
        self.edit_Lx_source.setText(str(self.params["TEC"]["Lx_source"]))
        self.edit_Ly_source.setText(str(self.params["TEC"]["Ly_source"]))
        self.edit_x_source.setText(str(self.params["TEC"]["x_source"]))
        self.edit_y_source.setText(str(self.params["TEC"]["y_source"]))
        self.edit_courant.setText(str(self.params["TEC"]["courant"]))
        self.edit_couplage.setText(str(self.params["TEC"]["couplage"]))

        # Perturbation
        self.edit_power.setText(str(self.params["perturbation_properties"]["power"]))
        self.edit_pos_x_perturbation.setText(str(self.params["perturbation_properties"]["pos_x"]))
        self.edit_pos_y_perturbation.setText(str(self.params["perturbation_properties"]["pos_y"]))

        # Thermistances
        self.edit_t1_x.setText(str(self.params["thermistances"]["pos_t1_x"]))
        self.edit_t1_y.setText(str(self.params["thermistances"]["pos_t1_y"]))
        self.edit_t2_x.setText(str(self.params["thermistances"]["pos_t2_x"]))
        self.edit_t2_y.setText(str(self.params["thermistances"]["pos_t2_y"]))
        self.edit_t3_x.setText(str(self.params["thermistances"]["pos_t3_x"]))
        self.edit_t3_y.setText(str(self.params["thermistances"]["pos_t3_y"]))

    def browse_json_file(self):
        """Ouvre une boîte de dialogue pour sélectionner un nouveau fichier JSON."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un fichier de paramètres JSON",
            os.getcwd(),  # Dossier de départ
            "Fichiers JSON (*.json);;Tous les fichiers (*)"
        )
        if filename:
            try:
                self.param_file_path = filename  # On met à jour le chemin
                self.load_params()              # Recharge
                self.populate_fields_from_params()

                self.paramFilePathChanged.emit(filename)

                self.status_label.setStyleSheet("color: green;")
                self.status_label.setText(f"Fichier chargé: {filename}")
            except Exception as e:
                self.status_label.setStyleSheet("color: red;")
                self.status_label.setText(f"Erreur de chargement : {e}")


    def save_copy(self):
        """
        Permet à l'utilisateur de choisir un fichier dans lequel
        sauvegarder une copie de la configuration JSON actuelle.
        """
        # Ouvre une boîte de dialogue "Enregistrer sous"
        filename, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Sauvegarder une copie du fichier JSON",
            dir="parametres_copy.json",  # Nom par défaut proposé
            filter="Fichiers JSON (*.json);;Tous les fichiers (*)"
        )
        if not filename:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText("Sauvegarde de la copie annulée.")
            return
        
        try:
            # Ensuite, on écrit self.params dans le fichier choisi
            with open(filename, "w") as f:
                json.dump(self.params, f, indent=4)
            
            self.status_label.setStyleSheet("color: green;")
            self.status_label.setText(f"Copie sauvegardée : {filename}")

        except Exception as e:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"Erreur lors de la sauvegarde : {e}")


    def save_params(self):
        """
        Récupère les valeurs dans les champs de texte,
        applique des vérifications, puis enregistre dans le fichier JSON.
        """
        try:
            # Dimensions
            Lx = float(self.edit_Lx.text())
            Ly = float(self.edit_Ly.text())
            e  = float(self.edit_e.text())
            if Lx <= 0 or Ly <= 0 or e <= 0:
                raise ValueError("Largeur axe x, Largeur axe y, et Épaisseur doivent être > 0.")

            # Material
            k   = float(self.edit_k.text())
            rho = float(self.edit_rho.text())
            cp  = float(self.edit_cp.text())
            if k <= 0 or rho <= 0 or cp <= 0:
                raise ValueError("k, rho, et cp doivent être > 0.")

            # conditions aux Limites
            h        = float(self.edit_h.text())
            T_piece  = float(self.edit_T_piece.text())
            if h < 0:
                raise ValueError("Le coefficient de convection (h) ne peut pas être négatif.")
            

            # Simulation
            res_spatiale   = int(self.edit_res_spatiale.text())
            res_temporelle = int(self.edit_res_temporelle.text())
            sim_duration  = float(self.edit_sim_duration.text())
            if res_spatiale <= 0 or res_temporelle <= 0 or sim_duration <= 0:
                raise ValueError("Les résolutions spatiale/Temporelle et la durée de simulation doivent être > 0.")

            # TEC
            Lx_source  = float(self.edit_Lx_source.text())
            Ly_source  = float(self.edit_Ly_source.text())
            x_source   = float(self.edit_x_source.text())
            y_source   = float(self.edit_y_source.text())
            courant    = float(self.edit_courant.text())
            couplage   = float(self.edit_couplage.text())

            # Vérification de la chaîne de texte pour on_off_tec
            on_off_tec_str = self.edit_on_off_tec.text().strip()
            if not on_off_tec_str:
                # Si la chaîne est vide, on la remplace par "0" et on met à jour le champ de texte
                on_off_tec_str = "0"
                self.edit_on_off_tec.setText("0")
            on_off_tec = [float(i) for i in on_off_tec_str.split(",")]

            if Lx_source <= 0 or Ly_source <= 0:
                raise ValueError("Largeur axe x de la source et Largeur axe y de la source doivent être positives > 0")
            if x_source <= 0 or y_source <= 0:
                raise ValueError("Positions axe x et axe y de la source doivent être positives > 0")
            if not (0 < Lx_source <= Lx):
                raise ValueError("Largeur axe x de la source doit être dans ]0, Largeur axe x de la plaque].")
            if not (0 < Ly_source <= Ly):
                raise ValueError("Largeur axe y de la source doit être dans ]0, Largeur axe y de la plaque].")
            if not (0 < x_source <= Lx):
                raise ValueError("Position axe x de la source doit être dans ]0, Largeur axe x de la plaque].")
            if not (0 < y_source <= Ly):
                raise ValueError("Position axe y de la source doit être dans ] 0, Largeur axe y de la plaque].")
   
            if not(0 <= couplage <= 1):
                raise ValueError("Le couplage doit être entre 0 et 1.")

            # Perturbation
            power = float(self.edit_power.text())
            pos_x_perturbation = float(self.edit_pos_x_perturbation.text())
            pos_y_perturbation = float(self.edit_pos_y_perturbation.text())

            on_off_perturbation_str = self.edit_on_off_perturbation.text().strip()
            if not on_off_perturbation_str:
                # Si la chaîne est vide, on la remplace par "0" et on met à jour le champ de texte
                on_off_perturbation_str = "0"
                self.edit_on_off_perturbation.setText("0")
            on_off_perturbation = [float(i) for i in on_off_perturbation_str.split(",")]

        

            if not (0 <= pos_x_perturbation <= Lx):
                raise ValueError("Position axe x de la perturbation doit être dans ]0, Largeur axe x de la plaque].")
            if not (0 <= pos_y_perturbation <= Ly):
                raise ValueError("Position axe y de la perturbation doit être dans ]0, Largeur axe y de la plaque].")

            # Thermistances
            t1x = float(self.edit_t1_x.text())
            t1y = float(self.edit_t1_y.text())
            t2x = float(self.edit_t2_x.text())
            t2y = float(self.edit_t2_y.text())
            t3x = float(self.edit_t3_x.text())
            t3y = float(self.edit_t3_y.text())

            # Vérifier que 0 <= t1x <= Lx, etc.
            for idx, (tx, ty) in enumerate([(t1x, t1y), (t2x, t2y), (t3x, t3y)], start=1):
                if not (0 <= tx <= Lx):
                    raise ValueError(f"Thermistance {idx}: Position axe x doit être dans ]0, Largeur axe x de la plaque].")
                if not (0 <= ty <= Ly):
                    raise ValueError(f"Thermistance {idx}: pos_y doit être dans ]0, Largeur axe y de la plaque].")

            # Si on arrive ici, toutes les valeurs sont jugées valides.
            # Mettre à jour le dictionnaire self.params:
            self.params["dimensions"]["Lx"] = Lx
            self.params["dimensions"]["Ly"] = Ly
            self.params["dimensions"]["e"]  = e

            self.params["material_properties"]["k"]   = k
            self.params["material_properties"]["rho"] = rho
            self.params["material_properties"]["cp"]  = cp

            self.params["boundary_conditions"]["h"]       = h
            self.params["boundary_conditions"]["T_piece"] = T_piece

            self.params["simulation_parameters"]["res_spatiale"]   = res_spatiale
            self.params["simulation_parameters"]["res_temporelle"] = res_temporelle
            self.params["simulation_parameters"]["sim_duration"]  = sim_duration

            self.params["TEC"]["Lx_source"] = Lx_source
            self.params["TEC"]["Ly_source"] = Ly_source
            self.params["TEC"]["x_source"]  = x_source
            self.params["TEC"]["y_source"]  = y_source
            self.params["TEC"]["courant"]   = courant
            self.params["TEC"]["couplage"]  = couplage
            self.params["TEC"]["TEC_momment_inversion"] = on_off_tec

            self.params["perturbation_properties"]["power"]   = power
            self.params["perturbation_properties"]["pos_x"] = pos_x_perturbation
            self.params["perturbation_properties"]["pos_y"] = pos_y_perturbation
            self.params["perturbation_properties"]["PERTU_momment_inversion"] = on_off_perturbation

            self.params["thermistances"]["pos_t1_x"] = t1x
            self.params["thermistances"]["pos_t1_y"] = t1y
            self.params["thermistances"]["pos_t2_x"] = t2x
            self.params["thermistances"]["pos_t2_y"] = t2y
            self.params["thermistances"]["pos_t3_x"] = t3x
            self.params["thermistances"]["pos_t3_y"] = t3y

            # Sauvegarde dans le fichier JSON
            with open(self.param_file_path, "w") as f:
                json.dump(self.params, f, indent=4)

            # Indiquer à l'utilisateur que c'est réussi
            self.status_label.setStyleSheet("color: green;")
            self.status_label.setText("Paramètres enregistrés avec succès.")
            QTimer.singleShot(5000, lambda: self.status_label.setText(""))
            
        except ValueError as ve:
            # Montre l'erreur à l'écran
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"Erreur de validation: {ve}")
        except Exception as e:
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText(f"Erreur: {e}")

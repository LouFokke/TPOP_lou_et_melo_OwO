import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.animation import FuncAnimation
from numba import njit, prange
from ToggleManager import ToggleManager
import datetime
from PySide6.QtWidgets import QFileDialog

class ThermalSimulation:
    def __init__(self, param_file_path="parametres.json", on_simulation_end=None):
        """Charge les paramètres depuis le JSON et initialise la simulation."""

        self.on_simulation_end = on_simulation_end  # Callback à appeler à la fin de la simulation
        
        #Chargement des paramètres
        with open(param_file_path, 'r') as file:
            self.params = json.load(file)
        
        #Paramètres physiques
        self.Lx_phys = self.params['dimensions']['Lx']         # Taille physique en x de la plaque en mètres
        self.Ly_phys = self.params['dimensions']['Ly']         # Taille physique en y de la plaque en mètres
        self.thickness = self.params['dimensions']['e']        # Épaisseur de la plaque en mètres (axe z)
        self.steps_total = self.params['simulation_parameters']['sim_duration']                               # Nombre total d'étapes de simulation
        
        # Propriétés du matériau
        self.k = self.params['material_properties']['k']       # Conductivité thermique [W/m·K]
        self.rho = self.params['material_properties']['rho']   # Densité [kg/m^3]
        self.cp = self.params['material_properties']['cp']     # Chaleur spécifique [J/kg·K]
        self.alphanormal = self.k / (self.rho * self.cp)             # Diffusivité thermique [m^2/s]
        self.diff_de_densite = 0.70
        
        # Définition de la résolution (nombre d'éléments sur le côté le plus petit)
        self.resolution = self.params['simulation_parameters']['res_spatiale']
        if self.Lx_phys < self.Ly_phys:
            self.dx = self.Lx_phys / self.resolution
            self.dy = self.dx
            self.Nx = self.resolution
            self.Ny = round(self.Ly_phys / self.dy)
        else:
            self.dy = self.Ly_phys / self.resolution
            self.dx = self.dy
            self.Nx = round(self.Lx_phys / self.dx)
            self.Ny = self.resolution

        #définir rho comme une matrice
        self.rhomatrice = np.ones((self.Ny,self.Nx)) * self.rho
        #self.rhomatrice = np.full((self.Ny, self.Nx), self.rho)

        for i in prange(round((self.Ny/2)-1), round((self.Ny/2))+1):
            for j in prange(1, self.Nx-1):
                self.rhomatrice[i,j] = self.rho * self.diff_de_densite
        
        #définir alpha comme une matrice
        #self.alphamatrice = np.ones((self.Ny,self.Nx))
        self.alphamatrice = np.full((self.Ny, self.Nx), self.alphanormal)
        self.alphamodif = self.k / (self.rho * self.diff_de_densite * self.cp)

        for i in prange(round((self.Ny/2)-1), round((self.Ny/2))+1):
            for j in prange(1, self.Nx-1):
                self.alphamatrice[i,j] = self.alphamodif

        
        

        print(f"nx = {self.Nx}, ny = {self.Ny}, dx = dy = {self.dx}")
        
        # Paramètres de convection
        self.aire_sides_up_down = self.dx * self.thickness     # Aire latérale pour les côtés haut/bas
        self.aire_sides_left_right = self.dy * self.thickness  # Aire latérale pour les côtés gauche/droite
        self.aire_top = self.dx * self.dy                       # Aire d'une face du dessus ou du dessous
        self.volume = self.dx * self.dy * self.thickness        # Volume d'un élément
        self.h_conv = self.params['boundary_conditions']['h']   # Coefficient de convection [W/m^2·K]
        
        # Position de la source
        self.x_source = self.params['TEC']['x_source']          # Position de la source en x en mètres
        self.y_source = self.params['TEC']['y_source']          # Position de la source en y en mètres
        self.x_source_idx = round(self.x_source / self.dx)
        self.y_source_idx = round(self.y_source / self.dy)

        # Largeur de la source
        self.Lx_source = self.params['TEC']['Lx_source']
        self.Ly_source = self.params['TEC']['Ly_source']
        self.Nx_source = round(self.Lx_source / self.dx)
        self.Ny_source = round(self.Ly_source / self.dy)
        
        self.xl_start = self.x_source_idx - self.Nx_source // 2
        self.xl_end = self.x_source_idx + self.Nx_source // 2 + 1
        self.yl_start = self.y_source_idx - self.Ny_source // 2
        self.yl_end = self.y_source_idx + self.Ny_source // 2 + 1

        self.surface_source = (self.xl_end - self.xl_start) * (self.yl_end - self.yl_start) * self.dx * self.dy * self.thickness

        # Échelon de courant ou puissance permanente
        self.courant = self.params['TEC']['courant']
        self.initial_P_in = 0.3123 * (self.courant ** 2) + 1.0217 * self.courant 
        self.couplage_thermique = self.params['TEC']['couplage']
        
        # Gestion de la perturbation
        self.P_in_perturbation = self.params['perturbation_properties']['power']
        self.x_perturbation = round((self.params['perturbation_properties']['pos_x']) / self.dx)
        self.y_perturbation = round((self.params['perturbation_properties']['pos_y']) / self.dy)
        self.P_perturbation = self.P_in_perturbation / (self.dx * self.dy * self.thickness)

        # Pour être cohérent avec l'affichage (axe horizontal = x, vertical = y),
        # les tableaux sont de forme (Ny, Nx)
        self.P_perm = np.zeros((self.Ny, self.Nx))
        self.P_perm[self.yl_start:self.yl_end, self.xl_start:self.xl_end] = (
            (self.couplage_thermique * self.initial_P_in) / self.surface_source
        )

        #Gestion des thermistances
        #Thermistance 1
        pos_t1_x = self.params['thermistances']['pos_t1_x']
        pos_t1_y = self.params['thermistances']['pos_t1_y']
        pos_t2_x = self.params['thermistances']['pos_t2_x']
        pos_t2_y = self.params['thermistances']['pos_t2_y']
        pos_t3_x = self.params['thermistances']['pos_t3_x']
        pos_t3_y = self.params['thermistances']['pos_t3_y']

        # Indices sur la grille
        self.thermistances_pos = [
            (round(pos_t1_y / self.dy), round(pos_t1_x / self.dx)),
            (round(pos_t2_y / self.dy), round(pos_t2_x / self.dx)),
            (round(pos_t3_y / self.dy), round(pos_t3_x / self.dx))
        ]

        
        self.P_mouse = np.zeros((self.Ny, self.Nx))

        # Calcul du pas temporel
        dt_y_normal = self.dy ** 2 / (8 * self.alphanormal)
        dt_x_normal = self.dx ** 2 / (8 * self.alphanormal)
        dt_y_modifier = self.dy ** 2 / (8 * self.alphamodif)
        dt_x_modifier = self.dx ** 2 / (8 * self.alphamodif)
        self.dt = min([dt_x_normal, dt_y_normal, dt_y_modifier, dt_x_modifier])
        print(f"Pas temporel choisi (dt): {self.dt}")

        self.TEC_momment_inversion = ToggleManager(self.params['TEC']['TEC_momment_inversion'], self.dt)  # Temps d'activation de la source
        self.PERTU_momment_inversion = ToggleManager(self.params['perturbation_properties']['PERTU_momment_inversion'], self.dt)  # Temps d'activation de la source

        # Initialisation de la température
        self.T_piece = 30 #self.params['boundary_conditions']['T_piece']
        T_init = np.full((self.Ny, self.Nx), self.T_piece, dtype=np.float64) # Tableau de température (lignes = y, colonnes = x)

        # État initial de la simulation
        self.state = {
            "T": T_init.copy(),
            "T_new": T_init.copy(),
            "simulation_steps": 0
        }

        # Variables globales de contrôle
        self.power_enabled = 0  # Active/désactive la source permanente
        self.perturbation_state = 0  # État de la perturbation (0 = off, 1 = on)
        self.stop_simulation = True # False => simulation en cours

        # Nombre de pas de simulation par frame d’animation
        self.steps_per_frame = self.params['simulation_parameters']['res_temporelle']

        # ---------------------------
        # Préparation de l'affichage
        # ---------------------------
        self.fig, self.ax = plt.subplots(1, 2, figsize=(12, 8))
        plt.subplots_adjust(bottom=0.25)  # Espace pour slider et boutons
        
        # Affichage avec extent pour utiliser les coordonnées physiques
        self.cax = self.ax[0].imshow(
            self.state["T"],
            cmap='hot',
            origin='lower',
            vmin=20,
            vmax=40,
            extent=[0, self.Lx_phys, 0, self.Ly_phys]  # pour échelle physique
        )
        self.fig.colorbar(self.cax, ax=self.ax[0], label='Température (°C)')

        self.ax[0].set_xlabel("Position x (m)")
        self.ax[0].set_ylabel("Position y (m)")

        plt.subplots_adjust(hspace=0.4, bottom=0.25)  # Ajuste l'espacement entre les subplots

        # Historique de température
        self.T_hist_1, self.T_hist_2, self.T_hist_3 = [], [], []


        # Affichage des courbes de température (thermistances)
        self.line1, = self.ax[1].plot([], [], label="Thermistance 1")
        self.line2, = self.ax[1].plot([], [], label="Thermistance 2")
        self.line3, = self.ax[1].plot([], [], label="Thermistance 3")
        self.ax[1].set_xlim(0, 150) # Axe du temps
        self.ax[1].set_xlabel("Temps (s)")
        self.ax[1].set_ylabel("Température (°C)")
        self.ax[1].legend()

        #Aucune animation commencée au départ
        self.ani = None

        # Bouton Stop/Resume
        ax_button = plt.axes([0.8, 0.1, 0.1, 0.05])
        self.button_stop = Button(ax_button, 'Stop')
        self.button_stop.on_clicked(self.toggle_simulation)

        # Bouton Power ON/OFF
        ax_power = plt.axes([0.65, 0.1, 0.12, 0.05])
        self.button_power = Button(ax_power, 'Power: ON')
        self.button_power.on_clicked(self.toggle_power)
        
        # Préparer la Numba JIT compilation afin de ne pas avoir de délai lorsqu'on commence la simulation
        dummy_T = self.state["T"].copy()
        dummy_T_new = self.state["T_new"].copy()
        _ = self._update_temperature(
            dummy_T, dummy_T_new, self.alphamatrice, self.dt, self.dx, self.dy,
            self.P_perm, self.P_mouse, self.power_enabled,
            self.rhomatrice, self.cp, self.h_conv, self.T_piece,
            self.aire_sides_up_down, self.aire_sides_left_right, self.aire_top,
            self.volume, self.k
        )

    def toggle_simulation(self, event):
        """Stop ou relance la simulation."""
        self.stop_simulation = not self.stop_simulation
        self.button_stop.label.set_text('Resume' if self.stop_simulation else 'Stop')

    def toggle_power(self, event):
        """Active/désactive la source permanente."""
        self.power_enabled = 0 if self.power_enabled == 1 else 1
        self.button_power.label.set_text('Power: ON' if self.power_enabled else 'Power: OFF')
    
    def toggle_perturbation(self):
        """Active/désactive la perturbation."""
        self.perturbation_state = 0 if self.perturbation_state == 1 else 1

    @staticmethod
    @njit(parallel=True)
    def _update_temperature(T, T_new, alpha, dt, dx, dy, P_perm, P_mouse, power_on,
                            rho, cp, h_conv, T_piece, aire_sides_up_down,
                            aire_sides_left_right, aire_top, volume, k):
        """Fonction Numba qui met à jour la matrice de température T_new à partir de T."""

        dt_alpha = dt * alpha
        dx_dy = dx * dy

        #dt_alpha_dx_dy = dt_alpha / dx_dy

        #((dt * alpha[i,j]) / (dx * dy))

        #dt_rho_cp = dt / (rho * cp)
        #dt_rho_cp_h_conv_volume = dt_rho_cp * h_conv / volume

        #((dt / (rho * cp)) * h_conv / volume)

        Ny, Nx = T.shape
        for i in prange(1, Ny-1):
            for j in prange(1, Nx-1):
                T_new[i, j] = T[i, j]
                # Conditions sur les bords (exclusion des coins)
                if (i == 1 and j > 1 and j < Nx-2):
                    T_new[i, j] += ((dt * alpha[i,j]) / (dx * dy)) * (T[i + 1, j] + T[i, j + 1] + T[i, j - 1] - 3 * T[i, j])
                    T_new[i, j] += ((dt / (rho[i,j] * cp)) * h_conv / volume) * (T_piece - T[i, j]) * aire_sides_up_down
                elif (i == Ny-2 and j > 1 and j < Nx-2):
                    T_new[i, j] += ((dt * alpha[i,j]) / (dx * dy)) * (T[i - 1, j] + T[i, j + 1] + T[i, j - 1] - 3 * T[i, j])
                    T_new[i, j] += ((dt / (rho[i,j] * cp)) * h_conv / volume) * (T_piece - T[i, j]) * aire_sides_up_down
                elif (j == 1 and i > 1 and i < Ny-2):
                    T_new[i, j] += ((dt * alpha[i,j]) / (dx * dy)) * (T[i + 1, j] + T[i - 1, j] + T[i, j + 1] - 3 * T[i, j])
                    T_new[i, j] += ((dt / (rho[i,j] * cp)) * h_conv / volume) * (T_piece - T[i, j]) * aire_sides_left_right
                elif (j == Nx-2 and i > 1 and i < Ny-2):
                    T_new[i, j] += ((dt * alpha[i,j]) / (dx * dy)) * (T[i + 1, j] + T[i - 1, j] + T[i, j - 1] - 3 * T[i, j])
                    T_new[i, j] += ((dt / (rho[i,j] * cp)) * h_conv / volume) * (T_piece - T[i, j]) * aire_sides_left_right
                elif (i == 1 and j == 1):
                    T_new[i, j] += ((dt * alpha[i,j]) / (dx * dy)) * (T[i + 1, j] + T[i, j + 1] - 2 * T[i, j])
                    T_new[i, j] += 2 * ((dt / (rho[i,j] * cp)) * h_conv / volume) * (T_piece - T[i, j]) * aire_sides_up_down
                elif (i == 1 and j == Nx-2):
                    T_new[i, j] += ((dt * alpha[i,j]) / (dx * dy)) * (T[i + 1, j] + T[i, j - 1] - 2 * T[i, j])
                    T_new[i, j] += 2 * ((dt / (rho[i,j] * cp)) * h_conv / volume) * (T_piece - T[i, j]) * aire_sides_up_down
                elif (i == Ny-2 and j == 1):
                    T_new[i, j] += ((dt * alpha[i,j]) / (dx * dy)) * (T[i - 1, j] + T[i, j + 1] - 2 * T[i, j])
                    T_new[i, j] += 2 * ((dt / (rho[i,j] * cp)) * h_conv / volume) * (T_piece - T[i, j]) * aire_sides_up_down
                elif (i == Ny-2 and j == Nx-2):
                    T_new[i, j] += ((dt * alpha[i,j]) / (dx * dy)) * (T[i - 1, j] + T[i, j - 1] - 2 * T[i, j])
                    T_new[i, j] += 2 * ((dt / (rho[i,j] * cp)) * h_conv / volume) * (T_piece - T[i, j]) * aire_sides_up_down
                else:
                    T_new[i, j] += (dt / (rho[i,j] * cp)) * k * (
                        T[i + 1, j] + T[i - 1, j] + T[i, j + 1] + T[i, j - 1] - 4 * T[i, j]
                    ) / dx_dy

                # Injection (source permanente)
                T_new[i, j] += (dt / (rho[i,j] * cp)) * (P_perm[i, j] + P_mouse[i, j])

                # Convection sur les faces supérieures / inférieures
                T_new[i, j] += ((dt / (rho[i,j] * cp)) * h_conv / volume) * (T_piece - T[i, j]) * 2 * aire_top

        return T_new

    def update_frame(self, _):
        """Fonction appelée à chaque frame de l'animation pour mettre à jour la simulation."""
        if self.stop_simulation:
            return [self.cax]
    
        T = self.state["T"]
        T_new = self.state["T_new"]
        sim_steps = self.state["simulation_steps"]
        
        # Nombre de pas de calcul par frame
        for _ in range(self.steps_per_frame):
            # Gestion de la perturbation
            if self.TEC_momment_inversion.toggle(sim_steps):
                self.toggle_power(None)
            if self.PERTU_momment_inversion.toggle(sim_steps):
                self.toggle_perturbation()

            self.P_perm[self.yl_start:self.yl_end, self.xl_start:self.xl_end] = self.power_enabled * (self.couplage_thermique * self.initial_P_in) / self.surface_source
            self.P_perm[self.y_perturbation, self.x_perturbation] = self.perturbation_state * self.P_perturbation

            # Vérifie si on a atteint la fin
            if sim_steps * self.dt > self.steps_total:

                self.T_hist_1.append(T[self.thermistances_pos[0]])
                self.T_hist_2.append(T[self.thermistances_pos[1]])
                self.T_hist_3.append(T[self.thermistances_pos[2]])

                # On arrête comme si on avait cliqué sur "Stop"
                self.state["T"] = T
                self.state["T_new"] = T_new
                self.state["simulation_steps"] = sim_steps

                
                self.stop_test()  # Arrêt + sauvegarde CSV

                 # ICI on appelle le callback pour dire "simulation terminée"
                if self.on_simulation_end is not None:
                    self.on_simulation_end()

                # On peut sortir tout de suite de la fonction
                return [self.cax] 

            # Mise à jour
            T_new = self._update_temperature(
                T, T_new, self.alphamatrice, self.dt, self.dx, self.dy, self.P_perm, self.P_mouse,
                self.power_enabled, self.rhomatrice, self.cp, self.h_conv, 23,
                self.aire_sides_up_down, self.aire_sides_left_right, self.aire_top,
                self.volume, self.k
            )
            T, T_new = T_new, T  # Échange des buffers
            sim_steps += 1

        self.state["T"] = T
        self.state["T_new"] = T_new
        self.state["simulation_steps"] = sim_steps
        
        # Mise à jour de l'historique
        self.T_hist_1.append(T[self.thermistances_pos[0]])
        self.T_hist_2.append(T[self.thermistances_pos[1]])
        self.T_hist_3.append(T[self.thermistances_pos[2]])

        # Mise à jour des courbes
        time_values = np.arange(len(self.T_hist_1)) * self.dt * self.steps_per_frame
        self.line1.set_data(time_values, self.T_hist_1)
        self.line2.set_data(time_values, self.T_hist_2)
        self.line3.set_data(time_values, self.T_hist_3)

        # -- Rendre l'axe Y dynamique --
        self.ax[1].relim()                          # Recalcule les min/max
        self.ax[1].autoscale_view(scalex=False,     # On ne touche pas à l'axe X
                                scaley=True)      # On ajuste l'axe Y

        self.cax.set_data(T)
        self.ax[0].set_title(f"Temps = {sim_steps * self.dt:.2f} s")

        # Ajuster l'axe X des courbes pour voir toute la simulation
        if time_values[-1] > self.ax[1].get_xlim()[1]:
            self.ax[1].set_xlim(0, time_values[-1] + 50)

        # ICI on ajuste la palette des couleurs :
        temp_min = T.min()
        temp_max = T.max()
        self.cax.set_clim(temp_min, temp_max )

        # Force le redraw du canvas
        self.fig.canvas.draw_idle()

        return [self.cax, self.line1, self.line2, self.line3]
    
    def start_test(self):
        """Crée et lance l'animation : la simulation démarre."""
        self.stop_simulation = False
        if self.ani is None:  
            self.ani = FuncAnimation(
                self.fig,
                self.update_frame,
                interval=200,
                blit=False,
                cache_frame_data=False
            )

        self.update_frame(0)
        

    def stop_test(self):
        """Arrête la simulation et sauvegarde les données."""
        self.stop_simulation = True
        self.save_to_csv()

         # Arrête l'animation si elle est en cours
        if self.ani is not None:
            self.ani.event_source.stop()
            self.ani = None  

        
        
        # Réinitialise l'historique de température
        self.T_hist_1.clear()
        self.T_hist_2.clear()
        self.T_hist_3.clear()
        
        # Réinitialise le compteur de pas si on veut repartir de t=0 au prochain test
        self.state["simulation_steps"] = 0

        T_init = np.full((self.Ny, self.Nx), self.T_piece, dtype=np.float64)
        self.state["T"] = T_init.copy()
        self.state["T_new"] = T_init.copy()

    def save_to_csv(self):
        """Sauvegarde l'historique de température des 3 thermistances dans un CSV."""
        time_values = np.arange(len(self.T_hist_1)) * self.dt * self.steps_per_frame
        T_hist_1_array = np.array(self.T_hist_1)
        T_hist_2_array = np.array(self.T_hist_2)
        T_hist_3_array = np.array(self.T_hist_3)
        
        data = np.column_stack((time_values, T_hist_1_array, T_hist_2_array, T_hist_3_array))

        # Ouvre la boîte de dialogue
        filename, _ = QFileDialog.getSaveFileName(
            parent=None,
            caption="Enregistrer les résultats",
            dir="",
            filter="Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )

        if filename:
            np.savetxt(
                filename,
                data,
                delimiter=',',
                header='Time (s), T1, T2, T3',
                comments='',
                fmt='%.4f'
            )

            print(f"Fichier sauvegardé: {filename}")
            
        else:
            print("Sauvegarde annulée.")

        
       
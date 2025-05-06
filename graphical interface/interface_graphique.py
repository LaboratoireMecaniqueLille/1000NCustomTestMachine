#Imports

import random
import tkinter as tk
import tkinter.filedialog as tkFileDialog
import tomllib
import sys
import argparse
import os
from datetime import datetime
import importlib.util
import time

BASE_DIR = os.environ.get('BASE_DIR')
if not BASE_DIR:
    raise EnvironmentError("The variable BASE_DIR was not defined")

"""BASE_DIR = "/home/stagiaire/Codes/essai_traction" """
path_crappy = BASE_DIR + "../crappy/src"

sys.path.append(os.path.abspath(path_crappy))
import crappy.actuator.phidgets_stepper4a as ph_stp
import crappy.inout.phidgets_wheatstone_bridge as ph_whe

class TensileTestP1(tk.Tk):

    #initialisation
    def __init__(self, premier_appel, default_speed="1", default_l0="10", default_save_path="",
                 default_load_cell="", default_test_type=""):
        super().__init__()
        
        if premier_appel :
            try:
                filepath = os.path.join(BASE_DIR, ".default_set_parameters.toml")
                with open(filepath, "rb") as f:
                    doc = tomllib.load(f)

                default_speed = doc['data']['speed']
                default_l0 = doc['data']['l0']
                default_save_path = doc['data']['path_save_data']
                default_load_cell = doc['data']['load_cell']
                default_test_type = doc['data']['test_type']

            except (OSError, tomllib.TOMLDecodeError) as e:
                pass


        # Initialisation des attributs
        self.label_chemin = None
        self.is_calibrated = False
        self.in_position = False
        self.path_save_data = default_save_path

        self.calibrated_pos = 0
        
        # Configuration de la fenêtre
        self.title("Initiating the tensile test")
        self.minsize(675, 500)
        self.geometry("800x600")


        # Création de l'interface
        self.create_widgets(default_speed, default_l0, default_load_cell, default_test_type)
        
        # Gestion de la fermeture
        self.protocol("WM_DELETE_WINDOW", self.close_cross)

    #Création de tous les widgets de la page, en appelant create_parameter_widgets et create_action_widgets
    def create_widgets(self, default_speed, default_l0, default_load_cell, default_test_type):
        """Crée tous les widgets de l'interface"""
        # Titre
        lbl_titre = tk.Label(self, text="Welcome", font=("Helvetica",20, "bold"),
                            wraplength=150, foreground=self.create_couleur_titre())
        lbl_titre.grid(pady=2, column=2, row=0, columnspan=1)
        
        # Frame gauche (paramètres)
        self.frame_gauche = tk.Frame(self)
        self.create_parameter_widgets(default_speed, default_l0, default_load_cell, default_test_type)

        # Frame droite (actions)
        self.frame_droite = tk.Frame(self)
        self.create_action_widgets()

        # Bouton Start
        btn_start = tk.Button(self, text="Start", font=("Helvetica",13, "bold"),
                            foreground="red", command=self.demarrage)

        
        self.frame_gauche.grid(column=1, row=1, columnspan=1, rowspan=2)
        self.frame_droite.grid(column=3, row=1, columnspan=1, rowspan=2)
        btn_start.grid(pady=2, column=2, row=3)


        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1, minsize=250)
        self.columnconfigure(2, weight=1, minsize=125)
        self.columnconfigure(3, weight=1, minsize=250)
        self.columnconfigure(4, weight=1)
        self.rowconfigure(0, weight=1, minsize=20)
        self.rowconfigure(1, weight=1, minsize=150)
        self.rowconfigure(2, weight=1, minsize=150)
        self.rowconfigure(3, weight=1, minsize=20)


        self.frame_gauche.columnconfigure(0, weight=1, minsize=100)
        self.frame_gauche.rowconfigure(0, weight=1, minsize=20)
        self.frame_gauche.rowconfigure(1, weight=1, minsize=20)
        self.frame_gauche.rowconfigure(2, weight=1, minsize=20)
        self.frame_gauche.rowconfigure(3, weight=1, minsize=20)
        self.frame_gauche.rowconfigure(4, weight=1, minsize=20)
        self.frame_gauche.rowconfigure(5, weight=1, minsize=20)
        self.frame_gauche.rowconfigure(6, weight=1, minsize=20)
        self.frame_gauche.rowconfigure(7, weight=1, minsize=20)
        self.frame_gauche.rowconfigure(8, weight=1, minsize=20)


        self.frame_droite.columnconfigure(0, weight=1)
        self.frame_droite.rowconfigure(0, weight=1)
        self.frame_droite.rowconfigure(1, weight=1)
        self.frame_droite.rowconfigure(2, weight=1)

        self.frame_d_haut.columnconfigure(0, weight=1)
        self.frame_d_haut.rowconfigure(0, weight=1)
        self.frame_d_haut.rowconfigure(1, weight=1)

        self.frame_d_milieu.columnconfigure(0, weight=1)
        self.frame_d_milieu.rowconfigure(0, weight=1)
        self.frame_d_milieu.rowconfigure(1, weight=1)

        


    #crée la partie gauche de la page, avec les cases à remplir et menus
    def create_parameter_widgets(self, default_speed, default_l0, default_load_cell, default_test_type):
        """Crée les widgets pour les paramètres"""
        # Speed

        self.speed_var = tk.StringVar(value=float(default_speed))

        lbl1 = tk.Label(self.frame_gauche, text='Speed (mm/s)',
                       font=("Helvetica",14), wraplength=225)
        lbl1.grid(pady=(10,2), column=0, row=0)
        self.entry_speed = tk.Entry(self.frame_gauche, width=25, textvariable=self.speed_var)
        self.entry_speed.grid(pady=(2,10), column=0, row=1)

        self.entry_speed.bind("<FocusOut>", self.validate_speed)
        self.entry_speed.bind("<Return>", self.validate_speed)

        self.last_valid_speed = float(default_speed)


        # Initial distance

        self.l0_var = tk.StringVar(value=float(default_l0))

        lbl2 = tk.Label(self.frame_gauche, 
                        text='Initial distance between the grips (mm)', 
                        font=("Helvetica",14), wraplength=225)
        lbl2.grid(pady=(10,2), column=0, row=2)

        self.entry_l0 = tk.Entry(self.frame_gauche, width=25, textvariable=self.l0_var)
        self.entry_l0.grid(pady=(2,10), column=0, row=3)

        self.entry_l0.bind("<FocusOut>", self.validate_l0)
        self.entry_l0.bind("<Return>", self.validate_l0)

        self.last_valid_l0 = float(default_l0)


        # Load Cell
        options_load_cell = ["50N", "100N", "200N"]
        initial_load_cell = default_load_cell if default_load_cell in options_load_cell else options_load_cell[0]
        self.load_cell_var = tk.StringVar(value=initial_load_cell)

        lbl3 = tk.Label(self.frame_gauche, text='Load Cell used', 
                        font=("Helvetica",14), wraplength=600)
        lbl3.grid(pady=(10,2), column=0, row=4)

        lbl_menu1 = tk.OptionMenu(self.frame_gauche, self.load_cell_var, *options_load_cell, command=lambda _: self.write_parameters(".default_set_parameters.toml"))
        lbl_menu1.grid(pady=(2,10), column=0, row=5)


        # Test Type
        options_test_type = ["Monotone Uniaxial Tensile Test"]
        initial_test_type = default_test_type if default_test_type in options_test_type else options_test_type[0]
        self.test_type_var = tk.StringVar(value=initial_test_type)

        lbl4 = tk.Label(self.frame_gauche, text='Type of test', 
                       font=("Helvetica",14), wraplength=600)
        lbl4.grid(pady=(10,2), column=0, row=6)

        lbl_menu2 = tk.OptionMenu(self.frame_gauche, self.test_type_var, *options_test_type, command=lambda _: self.write_parameters(".default_set_parameters.toml"))
        lbl_menu2.grid(pady=(2,10), column=0, row=7)

        # Save folder
        self.frame_g_bas = tk.Frame(self.frame_gauche)

        self.folder_var = tk.StringVar(value=self.path_save_data)

        lbl5 = tk.Label(self.frame_g_bas, text='Folder to save data',
                    font=("Helvetica",14), wraplength=600)
        lbl5.grid(pady=(10,2), column=0, row=0)

        self.entry_folder = tk.Entry(self.frame_g_bas, width=25, textvariable=self.folder_var)
        self.entry_folder.grid(pady=(2,10), column=0, row=1)

        self.entry_folder.bind("<FocusOut>", lambda event: self.write_parameters(".default_set_parameters.toml"))
        self.entry_folder.bind("<Return>", lambda event: self.write_parameters(".default_set_parameters.toml"))

        btn_save = tk.Button(self.frame_g_bas, text="...",
                            font=("Helvetica",13), command=self.save_data)
        btn_save.grid(pady=(2,10), column=1, row=1)
        self.frame_g_bas.grid(column=0, row=8)

    #crée la partie droite de la page, avec les boutons qui permettent de choisir quoi faire
    def create_action_widgets(self):
        """Crée les widgets pour les actions"""
        # Frame haute (calibration)
        self.frame_d_haut = tk.Frame(self.frame_droite)
        btn_protec_epr = tk.Button(self.frame_d_haut, text="Move the jaw manually",
                                 font=("Helvetica",13), command=self.protection_eprouvette)
        btn_protec_epr.grid(pady=10, column=0, row=0)
        btn_calibrate = tk.Button(self.frame_d_haut, text="Calibrate the position",
                                 font=("Helvetica",13), command=self.calibrate)
        btn_calibrate.grid(pady=10, column=0, row=1)
        self.frame_d_haut.grid(column=0, row=0, pady=(0,25))
        
        # Frame milieu (sauvegarde/chargement)
        self.frame_d_milieu = tk.Frame(self.frame_droite)
        btn_save_params = tk.Button(self.frame_d_milieu, text="Save parameters",
                                  font=("Helvetica",13), command=self.file_save)
        btn_save_params.grid(pady=10, column=0, row=0)
        btn_load_params = tk.Button(self.frame_d_milieu, text="Load parameters",
                                  font=("Helvetica",13), command=self.file_load)
        btn_load_params.grid(pady=10, column=0, row=1)
        self.frame_d_milieu.grid(column=0, row=1, pady=(25,25))



    # choix du dossier de sauvegarde des résultats (volontaire)
    def save_data(self):

        self.path_save_data = tkFileDialog.askdirectory(initialdir="./results")
        if not os.path.exists(self.path_save_data):
            try:
                os.makedirs(self.path_save_data)
            except:
                self.path_save_data = BASE_DIR + "/results/"

        self.entry_folder.delete(0, tk.END)
        self.entry_folder.insert(tk.END, self.path_save_data)
        self.entry_folder.grid(column=0, row=1)
        self.write_parameters(".default_set_parameters.toml")




    #permet de gérer la valeur de entry_speed, pour s'assurer qu'elle soit bien float et entre les valeurs limites
    def validate_speed(self, *args):

        try:
            value = float(self.speed_var.get())

            # Si valeur dans les limites
            if 0 <= value <= 2.5:
                self.last_valid_speed = value
                self.write_parameters(".default_set_parameters.toml")
                return

            # Si valeur hors limites
            response = tk.messagebox.askokcancel(
                "Valeur hors limites",
                f"La vitesse {value} mm/s est hors limites (0-2.5 mm/s).\n"
                "La vitesse qui va être utilisée est la valeur par défaut : 1mm/s",
                parent=self
            )

            if response:  # Si l'utilisateur confirme
                value = 1
                self.speed = value
                self.last_valid_speed = value
                self.speed_var.set("1.0")
            else:  # Si l'utilisateur annule
                self.speed_var.set(str(self.last_valid_speed))
                self.speed = self.last_valid_speed

        except ValueError:  # Si ce n'est pas un nombre
            if self.speed_var.get() != "":  # Permet de vider le champ
                self.speed_var.set(str(self.last_valid_speed))
                tk.messagebox.showerror(
                    "Erreur de saisie",
                    "Veuillez entrer un nombre valide",
                    parent=self
                )
            self.speed = self.last_valid_speed


    #permet de gérer la valeur de entry_l0, pour s'assurer qu'elle soit bien float
    def validate_l0(self, *args):
        current_value = self.l0_var.get()

        try:
            value = float(current_value)

            # Si valeur dans les limites
            if 0 <= value :
                self.l0 = value
                self.last_valid_l0= value
                self.write_parameters(".default_set_parameters.toml")
                return

            # Si valeur hors limites
            response = tk.messagebox.askokcancel(
                "Valeur hors limites",
                f"L'écart {value} mm est incorrect, il ne peut être inférieur à 0.\n"
                "L'écart qui va être réglé est la valeur par défaut : 10mm",
                parent=self
            )

            if response:  # Si l'utilisateur confirme
                value = 10
                self.l0 = value
                self.last_valid_l0 = value
                self.l0_var.set("10.0")
            else:  # Si l'utilisateur annule
                self.l0_var.set(str(self.last_valid_l0))
                self.l0 = self.last_valid_l0

        except ValueError:  # Si ce n'est pas un nombre
            if current_value != "":  # Permet de vider le champ
                self.l0_var.set(str(self.last_valid_speed))
                tk.messagebox.showerror(
                    "Erreur de saisie",
                    "Veuillez entrer un nombre valide\nLes nombres négatifs ne sont pas autorisés",
                    parent=self
                )
            self.l0 = self.last_valid_l0

    #à la moindre variation d'une valeur dans les paramèters renseignés, on écrit les valeur dans le fichier de transfert pour le 2e programme
    def write_parameters(self, saving_path, *args):

        path_results = self.folder_var.get()
        if path_results is None or path_results.strip() =="" :
            if self.test_type_var == "Monotone Uniaxial Tensile Test":
                path_results = self.nommer(BASE_DIR + "/results/",
                                                debut="Tensile", extension="/")
            else:
                path_results = self.nommer(BASE_DIR + "/results/",
                                                debut="", extension="/")

        if self.load_cell_var.get() == "50N":
            gain = 3.26496001e+05 
        else:
            gain = 1


        text1 = "[data]\n"
        text2save = (text1 +
                    f'speed = {self.speed_var.get()}\n' +
                    f'l0 = {self.l0_var.get()}\n' +
                    f'path_save_data = "{path_results}"\n' +
                    f'load_cell = "{self.load_cell_var.get()}"\n' +
                    f'test_type = "{self.test_type_var.get()}"\n' +
                    f'gain = "{gain}"\n')

        try:
            filename = os.path.join(BASE_DIR, saving_path)
            with open(filename, 'w') as f:
                f.write(text2save)

        except Exception as e:
            tk.messagebox.showerror("Erreur", f"Échec de sauvegarde:\n{str(e)}", parent=self)


    #permet de nommer automatiquement un fichier/ dossier en cas de sauvegarde forcée
    def nommer(self, parent_path, debut="", extension=""):
        """Génère un nom unique pour les fichiers/dossiers"""
        date_str = datetime.now().strftime("%Y.%m.%d")

        if debut.strip() != "":
            deb = True
            base_name = f"{debut}_{date_str}{extension}"
        else:
            deb = False
            base_name = f"{date_str}{extension}"

        counter = 1
        filename = os.path.join(parent_path, base_name)
        os.makedirs(parent_path, exist_ok=True)

        while os.path.exists(filename):
            if deb:
                filename = os.path.join(parent_path, f"{debut}_{date_str}_{counter}{extension}")
            else:
                filename = os.path.join(parent_path, f"{date_str}_{counter}{extension}")
            counter += 1

        return filename

    # sauvegarde volontaire du set de paramètres
    def file_save(self):
        initial_dir = "./parameters_sets"
        os.makedirs(initial_dir, exist_ok=True)
        f = tkFileDialog.asksaveasfilename(defaultextension=".toml",
                                      initialdir=initial_dir)
        if f :
            self.write_parameters(f)



    #choix du set de paramètres à ouvrir
    def open_file(self):
        """Ouvre un fichier de paramètres"""
        filename = tkFileDialog.askopenfilename(defaultextension=".toml", 
                                              initialdir="./parameters_sets")
        with open(filename, "rb") as f:
            data = tomllib.load(f)
        return data

    #enregistrement des données du set ouvert
    def file_load(self):
        """Charge les paramètres depuis un fichier"""
        doc = self.open_file()

        speed = doc['data']['speed']
        l0 = doc['data']['l0']
        path_save_data = doc['data']['path_save_data']
        load_cell = doc['data']['load_cell']
        test_type = doc['data']['test_type']

        try:
            self.destroy()
        except:
            pass
            
        # Recrée une nouvelle instance avec les paramètres chargés
        app = TensileTestP1(False, speed, l0, path_save_data, load_cell, test_type)
        app.mainloop()

    #ouverture du programme Portection_eprouvette, pour pouvoir écarter les mors manuellempent (s'ils sont trop serrés pour mettre la cale)
    def protection_eprouvette(self):
        tk.messagebox.showinfo(
            title="Manual movement",
            message="Be careful, the limit switches are deactivated during this phase",
            parent=self
        )
        print("protection_eprouvette")
        sys.stdout.flush()
        self.destroy()
        sys.exit(0)


    # 1e étape de la calibration de position, en plaçant la cale
    def calibrate(self):
        response = tk.messagebox.askokcancel(
            title="Confirmation",
            message="Have you set up the block?",
            detail="Be careful, the limit switches are deactivated during this phase \nClick OK to start calibration or Cancel to abort",
            parent=self
        )
        if response :
            self.calibrate_2()


    #2e étape de la calibration, en déplaçant le moteur jusqu'à la cale (ou la limite, mais ne devrait pas arriver)
    def calibrate_2(self):
        """Effectue la calibration du moteur"""

        motor = None
        load_cell = None

        try:
            motor = ph_stp.Phidget4AStepper(steps_per_mm=2500, current_limit=3, 
                                           remote=True, absolute_mode=True, 
                                           reference_pos=0, switch_ports=())
            load_cell = ph_whe.PhidgetWheatstoneBridge(channel=1, gain=3.26496001e+05, 
                                                     remote=True)
            motor.open()
            load_cell.open()
            
            time.sleep(1)
            data = load_cell.get_data()
            initial_force = data[1]

            target_position = -300  # On va au max vers la cellule d'effort (-300mm)
            taille_cale = 58 + 10  # on rajoute 10 pour combler l'erreur (probablement due au fait que la cale est flexible)
            hit_obstacle = False 
            force_max_calib = 10 # On s'arrête si force>10N

            motor.set_position(target_position, 1)

            while True:
                time.sleep(0.05)  
                data = load_cell.get_data()

                if data is not None and not hit_obstacle :
                    current_force = data[1]

                    if abs(current_force - initial_force) > force_max_calib:  
                        current_pos = motor.get_position()

                        if current_pos is not None:
                            hit_obstacle = True
                            new_target = current_pos + 5  # Recule de 5 mm
                            motor.set_position(new_target, 1)
                            target_position = new_target
                            
                            
                current_pos = motor.get_position()
                if current_pos is not None and abs(current_pos - target_position) < 0.05:
                    self.calibrated_pos = taille_cale
                    break
            try:
                self.btn_go.grid_info()

            except :
                 #Ajoute le bouton pour aller à la position désirée, uniquement s'il n'existe pas encore
                self.btn_go = tk.Button(self.frame_droite.winfo_children()[0],  # frame_d_haut
                                text="Go to desired position",
                                font=("Helvetica",13),
                                command=self.go_to_position)
                self.btn_go.grid(pady=10, column=0, row=2)


        finally:
            motor.close()
            load_cell.close()
            self.is_calibrated = True



    #déplacement à la position souhaitée par l'utilisateur
    def go_to_position(self):
        """Déplace le moteur à la position désirée"""
        

        self.validate_l0()
        self.l0 = float(self.l0_var.get())

        target_position = self.l0 - self.calibrated_pos
        self.calibrated_pos = self.l0
        
        try:
            motor = ph_stp.Phidget4AStepper(steps_per_mm=2500, current_limit=3, 
                                           remote=True, absolute_mode=True, 
                                           reference_pos=0, switch_ports=(2,3))
            load_cell = ph_whe.PhidgetWheatstoneBridge(channel=1, gain=3.26496001e+05, 
                                                     remote=True)
            motor.open()
            load_cell.open()

            motor.set_position(target_position, 1.5)

            while True:
                data = load_cell.get_data()
                if data is not None:
                    current_force = data[1]

                    if abs(current_force) > 30:  # On s'arrête si force>30N
                        motor.stop()
                        break

                current_pos = motor.get_position()
                if current_pos is not None and abs(current_pos - target_position) < 0.05:
                    break
                
        finally:
            motor.close()
            load_cell.close()
            
            self.in_position = self.l0


    # si on ferme la fenetre par la croix, on arrete tout
    def close_cross(self):
        self.write_parameters(".default_set_parameters.toml")
        print("exit")
        sys.exit(1)

    #lancement de l'essai à proprement parler,en emêchant l'utilisateur de commencer s'il n'y a pas eu de calibration
    def demarrage(self):

        if not self.is_calibrated:

            response = tk.messagebox.showerror(
            title="Missing calibration",
            message="You did not calibrate the machine",
            parent=self
        )


        elif self.entry_l0.get().strip() is None or self.entry_l0.get().strip() == "" or float(self.entry_l0.get().strip()) != float(self.in_position) :
            response = tk.messagebox.showerror(
            title="Missing positioning",
            message="You did not set the machine to the right position",
            parent=self
        )

        else:
            self.validate_speed()
            self.validate_l0()
            self.write_parameters(".default_set_parameters.toml")

            try:
                self.destroy()
            except:
                pass


    #crée une couleur aléatoire pour le titre
    def create_couleur_titre(self):
        # Base claire (entre 200 et 255 pour garder des tons pastel)
        r = random.randint(150, 220)
        g = random.randint(150, 220)
        b = random.randint(150, 220)

        # Renforcer légèrement une composante aléatoire
        composante = random.choice([0, 1, 2])
        if composante == 0:
            r = random.randint(120, 170)
        elif composante == 1:
            g = random.randint(120, 170)
        else:
            b = random.randint(120, 170)

        return f"#{r:02x}{g:02x}{b:02x}"

if __name__ == '__main__':
    app = TensileTestP1(True)
    app.mainloop()

# coding: utf-8

# ToDo: mets tes print dans une fonction plutôt que d'en avoir 15000 partout
#  avec des strftime etc. Idem pour les showerror
# ToDo: Les commentaires qui décrivent tes fonctions devraient être des
#  doctrings à la place

import random
import numpy as np
import tkinter as tk
import tkinter.filedialog as tkFileDialog
import os
from datetime import datetime, time as dt_time
import time
from pathlib import Path
from functools import partial
import tomllib
import crappy.actuator.phidgets_stepper4a as ph_stp
import crappy.inout.phidgets_wheatstone_bridge as ph_whe
import sys

# constant obtained while executing the bash file
BASE_DIR = Path(os.environ.get('BASE_DIR'))
if not BASE_DIR:
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
          "The variable BASE_DIR was not defined")
    sys.exit(1)
print("\n", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
      "The selected base folder is :", BASE_DIR)

# group of constants modifiable
# folder to save the results by default
saving_folder = BASE_DIR / "results"

# hidden folder for parameters.toml, commande.txt and last_pos.npy
hidden_folder = BASE_DIR / ".parameters"

# default parameters (in case the .toml file went missing and the program
# creats it automatically)
DICT_DEFAULT_VALUES = {"speed": 1,  # float
                       "l0": 20,  # float
                       "saving_folder": saving_folder}

# all the possible load cells , and the associated gain (the name of the load
# cell has to be the maximaum force followed by "N")
DICT_LOAD_CELLS = {"50N": 3.26496001e+05,
                   "225N": 34911.5  # voir si besoin d'adapter à un gain
                   # hardware
                   }

# all possible types of test (they have to be programmed in lancement_essai.py)
DICT_TEST_TYPES = {"Monotonic Uniaxial Tensile Test": "MUTT"}

# size of the wedge to calibrate the motor, how much the motor needs to shift
# after the calibration, and the force necessary to stop the calibration
TAILLE_CALE = 14  # in mm
DECALAGE_POST_CALIBRATION = 5  # in mm
FORCE_MAX_CALIB = 10  # in N

# motor_speed (tells the motor how much it needs to move of a mm)
nb_steps_mm = 2500  # common values : 100 or 2500

# list of ports and their default state following their use
# True means open by default, False means close by default
ports_movement = tuple([2, 3])  # for the final machine tuple([2,3])
switch_states_movement = tuple([True, True])  # for the final machine
# tuple([True, False])
ports_calibration = tuple([2, 3])  # for the final machine tuple([5])
switch_states_calibration = tuple([True])  # for the final machine
# tuple([ ... ])


class TensileTestP1(tk.Tk):

    # initialisation : chargement des paramètres par défaut, initialisation des
    # paramèters, et création de la fenêtre
    def __init__(self):
        super().__init__()

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
              "Launching interface_graphique.py")

        # chargement du fichier .toml
        filepath = hidden_folder / "default_set_parameters.toml"
        try:
            with open(filepath, "rb") as f:
                doc = tomllib.load(f)

            default_speed = doc['data']['speed']
            default_l0 = doc['data']['l0']
            default_save_path = Path(doc['data']['path_save_data'])
            default_load_cell = doc['data']['load_cell']
            default_test_type = doc['data']['test_type']

            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Parameters charged from the last use")

        except Exception as e:
            tk.messagebox.showinfo(title="Parameters file missing",
                                   message=f"An error occured loading the "
                                           f".toml file, a new parameters "
                                           f"file will soon be created",
                                   detail=f"Error: {str(e)}")
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  f"An error occured loading the .toml file :\n{str(e)}\nA "
                  f"new parameters file will soon be created")

            self.create_default_parameters()
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "New parameters set written succesfully")

            filepath = hidden_folder / "default_set_parameters.toml"
            try:
                with open(filepath, "rb") as f:
                    doc = tomllib.load(f)

                default_speed = doc['data']['speed']
                default_l0 = doc['data']['l0']
                default_save_path = Path(doc['data']['path_save_data'])
                default_load_cell = doc['data']['load_cell']
                default_test_type = doc['data']['test_type']

                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "New parameters set loaded succesfully")

            # ToDo: Précise l'exception
            except Exception as e2:
                tk.messagebox.showerror("Error", f"The creation or reading of "
                                                 f"the new parameters file "
                                                 f"did not work",
                                        f"Error: {str(e2)}")
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      f"The creation or reading of the new parameters file "
                      f"did not work:\n{str(e2)}")
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "As the program could not write or load a parameters "
                      "set, the programm stopped")
                self.ecriture_commande("exit")

        # Initialisation des attributs
        self.in_position = False
        self.path_save_data = default_save_path
        self.liste_buttons = []
        self.calibrated_pos = None
        self.l0 = default_l0

        # Configuration de la fenêtre
        self.title("Initiating the tensile test")
        self.minsize(675, 500)
        self.geometry("800x600")

        # Création de l'interface
        self.create_widgets(default_speed, default_l0,
                            default_load_cell, default_test_type)

        # Gestion de la fermeture
        self.protocol("WM_DELETE_WINDOW", self.close_cross)

    # Création de tous les widgets de la page, en appelant
    # create_parameter_widgets et create_action_widgets
    def create_widgets(self,
                       default_speed,
                       default_l0,
                       default_load_cell,
                       default_test_type):
        # Titre
        lbl_titre = tk.Label(self,
                             text="Welcome",
                             font=("Helvetica", 20, "bold"),
                             wraplength=150,
                             foreground=self.create_couleur_titre())
        lbl_titre.grid(pady=2, column=2, row=0, columnspan=1)

        # Frame gauche (paramètres)
        self.frame_gauche = tk.Frame(self)
        self.create_parameter_widgets(default_speed, default_l0,
                                      default_load_cell, default_test_type)

        # Frame droite (actions)
        self.frame_droite = tk.Frame(self)
        self.create_action_widgets()

        # Bouton Start
        self.btn_start = tk.Button(self,
                                   text="Start",
                                   font=("Helvetica", 13, "bold"),
                                   foreground="red",
                                   command=self.demarrage)

        self.frame_gauche.grid(column=1, row=1, columnspan=1, rowspan=2)
        self.frame_droite.grid(column=3, row=1, columnspan=1, rowspan=2)
        self.btn_start.grid(pady=2, column=2, row=3)
        self.liste_buttons.append(self.btn_start)

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

        print(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(time.time())),
              "Initialization of the window done")

    # crée la partie gauche de la page, avec les cases à remplir et menus
    def create_parameter_widgets(self,
                                 default_speed,
                                 default_l0,
                                 default_load_cell,
                                 default_test_type):

        # Speed
        self.speed_var = tk.DoubleVar(value=float(default_speed))

        lbl1 = tk.Label(self.frame_gauche, text='Speed (mm/s)',
                        font=("Helvetica", 14), wraplength=225)
        lbl1.grid(pady=(10, 2), column=0, row=0)
        self.entry_speed = tk.Entry(self.frame_gauche, width=25,
                                    textvariable=self.speed_var)
        self.entry_speed.grid(pady=(2, 10), column=0, row=1)

        self.entry_speed.bind("<FocusOut>", self.validate_speed)
        self.entry_speed.bind("<Return>", self.validate_speed)

        self.last_valid_speed = float(default_speed)

        # Initial distance
        self.l0_var = tk.DoubleVar(value=float(default_l0))

        lbl2 = tk.Label(self.frame_gauche,
                        text='Initial distance between the grips (mm)',
                        font=("Helvetica", 14), wraplength=225)
        lbl2.grid(pady=(10, 2), column=0, row=2)

        self.entry_l0 = tk.Entry(self.frame_gauche, width=25,
                                 textvariable=self.l0_var)
        self.entry_l0.grid(pady=(2, 10), column=0, row=3)

        self.entry_l0.bind("<FocusOut>", self.validate_l0)
        self.entry_l0.bind("<Return>", self.validate_l0)

        self.last_valid_l0 = float(default_l0)

        # Load Cell
        options_load_cell = list(DICT_LOAD_CELLS.keys())
        initial_load_cell = (default_load_cell if default_load_cell
                             in options_load_cell else options_load_cell[0])
        self.load_cell_var = tk.StringVar(value=initial_load_cell)

        lbl3 = tk.Label(self.frame_gauche, text='Load Cell used',
                        font=("Helvetica", 14), wraplength=600)
        lbl3.grid(pady=(10, 2), column=0, row=4)

        lbl_menu1 = tk.OptionMenu(
          self.frame_gauche, self.load_cell_var, *options_load_cell,
          # ToDo: Utilise functools.partial au lieu des lambda functions
          command=lambda _: self.write_parameters(hidden_folder /
                                                  "default_set_parameters."
                                                  "toml"))
        lbl_menu1.grid(pady=(2, 10), column=0, row=5)

        # Test Type
        options_test_type = list(DICT_TEST_TYPES.keys())
        initial_test_type = (default_test_type if default_test_type in
                             options_test_type else options_test_type[0])
        self.test_type_var = tk.StringVar(value=initial_test_type)

        lbl4 = tk.Label(self.frame_gauche, text='Type of test',
                        font=("Helvetica", 14), wraplength=600)
        lbl4.grid(pady=(10, 2), column=0, row=6)

        lbl_menu2 = tk.OptionMenu(
          self.frame_gauche, self.test_type_var, *options_test_type,
          # ToDo: idem
          command=lambda _: self.write_parameters(hidden_folder /
                                                  "default_set_parameters."
                                                  "toml"))
        lbl_menu2.grid(pady=(2, 10), column=0, row=7)

        # Save folder
        self.frame_g_bas = tk.Frame(self.frame_gauche)

        self.folder_var = tk.StringVar(value=str(self.path_save_data))

        lbl5 = tk.Label(self.frame_g_bas, text='Folder to save data',
                        font=("Helvetica", 14), wraplength=600)
        lbl5.grid(pady=(10, 2), column=0, row=0)

        self.entry_folder = tk.Entry(self.frame_g_bas, width=25,
                                     textvariable=self.folder_var)
        self.entry_folder.grid(pady=(2, 10), column=0, row=1)
        self.entry_folder.xview("end")

        self.entry_folder.bind("<FocusOut>",
                               partial(self.write_parameters,
                                       hidden_folder /
                                       "default_set_parameters.toml"))
        self.entry_folder.bind("<Return>",
                               partial(self.write_parameters,
                                       hidden_folder /
                                       "default_set_parameters.toml"))

        self.btn_save = tk.Button(self.frame_g_bas, text="📂",
                                  font=("Helvetica", 13),
                                  command=self.save_data)
        self.btn_save.grid(pady=(2, 10), column=1, row=1)
        self.liste_buttons.append(self.btn_save)
        self.frame_g_bas.grid(column=0, row=8)

    # crée la partie droite de la page, avec les boutons qui permettent de
    # choisir quoi faire
    def create_action_widgets(self):

        # Frame haute (calibration)
        self.frame_d_haut = tk.Frame(self.frame_droite)
        self.btn_protec_epr = tk.Button(self.frame_d_haut,
                                        text="Move the jaw manually",
                                        font=("Helvetica", 13),
                                        command=self.protection_eprouvette)
        self.btn_protec_epr.grid(pady=10, column=0, row=0)
        self.liste_buttons.append(self.btn_protec_epr)
        self.btn_calibrate = tk.Button(self.frame_d_haut,
                                       text="Calibrate the position",
                                       font=("Helvetica", 13),
                                       command=self.calibrate)
        self.btn_calibrate.grid(pady=10, column=0, row=1)
        self.liste_buttons.append(self.btn_calibrate)
        # frame_d_haut
        self.btn_go = tk.Button(self.frame_droite.winfo_children()[0],
                                text="Go to desired \nInitial distance",
                                font=("Helvetica", 13),
                                command=self.go_to_position,
                                state="disabled")
        self.btn_go.grid(pady=10, column=0, row=2)
        self.liste_buttons.append(self.btn_go)
        self.frame_d_haut.grid(column=0, row=0, pady=(0, 25))

        # Frame milieu (sauvegarde/chargement)
        self.frame_d_milieu = tk.Frame(self.frame_droite)
        self.btn_save_params = tk.Button(self.frame_d_milieu,
                                         text="Save parameters",
                                         font=("Helvetica", 13),
                                         command=self.file_save)
        self.btn_save_params.grid(pady=10, column=0, row=0)
        self.liste_buttons.append(self.btn_save_params)
        self.btn_load_params = tk.Button(self.frame_d_milieu,
                                         text="Load parameters",
                                         font=("Helvetica", 13),
                                         command=self.file_load)
        self.btn_load_params.grid(pady=10, column=0, row=1)
        self.liste_buttons.append(self.btn_load_params)
        self.frame_d_milieu.grid(column=0, row=1, pady=(25, 25))

    # choix du dossier de sauvegarde des résultats (volontaire)
    def save_data(self):

        selected_dir = tkFileDialog.askdirectory(
          initialdir=BASE_DIR / "results/")

        if not selected_dir:  # "Cancel" renvoie une chaine vide, donc on ne
          # fait rien de cette chaîne
            return

        self.path_save_data = Path(selected_dir)

        # ToDo: utilise pathlib pas os
        if not os.path.exists(self.path_save_data):
            try:
                os.makedirs(self.path_save_data)
            # ToDo: pas de except seul
            except:
                self.path_save_data = BASE_DIR / "results/"

        self.entry_folder.delete(0, tk.END)
        self.entry_folder.insert(tk.END, str(self.path_save_data))
        self.entry_folder.grid(column=0, row=1)
        self.write_parameters(hidden_folder / "default_set_parameters.toml")
        self.entry_folder.xview("end")

    # permet de gérer la valeur de entry_speed, pour s'assurer qu'elle soit
    # bien float et entre les valeurs limites
    def validate_speed(self, *_):
        try:
            value = self.speed_var.get()

        # ToDo: Pas de except seul
        except:  # Si ce n'est pas un nombre
            self.speed_var.set(self.last_valid_speed)
            tk.messagebox.showerror(
                "Incorrect value",
                "Please enter a valid number",
                parent=self
                )
            self.speed = self.last_valid_speed
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Incorrect speed value (not a valid number)")
            return

        # Si valeur dans les limites
        if 0 < value <= 2.5:
            self.last_valid_speed = value
            self.write_parameters(hidden_folder /
                                  "default_set_parameters.toml")
            return

        # Si valeur hors limites
        response = tk.messagebox.askokcancel(
            "Value out of bounds",
            f"The speed {value} mm/s is out of bounds (0-2.5 mm/s). \n"
            f"The speed will be set on its default value : "
            f"{DICT_DEFAULT_VALUES.get("speed")} mm/s",
            parent=self
        )
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
              "Incorrect speed value (out of bounds)")

        if response:  # Si l'utilisateur confirme
            value = 1
            self.speed = value
            self.last_valid_speed = value
            self.speed_var.set(DICT_DEFAULT_VALUES.get("speed"))
        else:  # Si l'utilisateur annule
            self.speed_var.set(float(self.last_valid_speed))
            self.speed = self.last_valid_speed

    # permet de gérer la valeur de entry_l0, pour s'assurer qu'elle soit bien
    # float et entre les limites
    def validate_l0(self, *_):

        try:
            current_value = self.l0_var.get()
            value = round(current_value, 1)

        # ToDo
        except:  # Si ce n'est pas un nombre
            self.l0_var.set(self.last_valid_l0)
            tk.messagebox.showerror(
                "Incorrect value",
                "Please enter a valid number",
                parent=self
            )
            self.l0 = self.last_valid_l0
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Incorrect initial distance value (not a valid number)")
            return

        # Si valeur dans les limites
        if 0 < value < 300:
            self.l0 = value
            self.last_valid_l0 = value
            self.write_parameters(hidden_folder /
                                  "default_set_parameters.toml")
            return

        # Si valeur hors limites
        response = tk.messagebox.askokcancel(
            "Value out of bounds",
            f"The initial distance {value} mm is out of bounds (1-300 mm). \n"
            f"The inital distance will be set on its default value : "
            f"{DICT_DEFAULT_VALUES.get("l0")} mm",
            parent=self
        )
        print(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(time.time())),
              "Incorrect initial distance value (out of bounds)")

        if response:  # Si l'utilisateur confirme
            value = 20
            self.l0 = value
            self.last_valid_l0 = value
            self.l0_var.set(DICT_DEFAULT_VALUES.get("l0"))
        else:  # Si l'utilisateur annule
            self.l0_var.set(float(self.last_valid_l0))
            self.l0 = self.last_valid_l0
        return "value_changed"

    # à la moindre variation d'une valeur dans les paramèters renseignés, on
    # écrit les valeur dans le fichier de transfert pour le 2e programme
    def write_parameters(self, saving_path, *_):

        test_type = str(self.test_type_var.get())
        path_results = self.folder_var.get()
        if path_results is None or path_results.strip() == "":
            if test_type in DICT_TEST_TYPES:
                prefixe = DICT_TEST_TYPES[test_type]
                path_results, prefix = self.nommer(BASE_DIR / "results/",
                                                   debut=prefixe,
                                                   extension="/")
            else:
                path_results, prefix = self.nommer(BASE_DIR / "results/",
                                                   debut="", extension="/")
        else:
            if test_type in DICT_TEST_TYPES:
                prefixe = DICT_TEST_TYPES[test_type]
                path_results, prefix = self.nommer(path_results,
                                                   debut=prefixe,
                                                   extension="/")
            else:
                path_results, prefix = self.nommer(path_results,
                                                   debut="", extension="/")

        gain = DICT_LOAD_CELLS.get(self.load_cell_var.get())

        settings = {
            "data": {
                "speed": float(self.speed_var.get()),
                "l0": float(self.l0_var.get()),
                "path_save_data": f'"{str(path_results)}"',
                "load_cell": f'"{str(self.load_cell_var.get())}"',
                "test_type": f'"{str(self.test_type_var.get())}"',
                "gain": float(gain),
                "prefix": f'"{str(prefix)}"',
                "ports": f'"{str(ports_movement)}"',
                "ports_state": f'"{str(switch_states_movement)}"',
                "nb_steps": int(nb_steps_mm)
            }
        }

        try:
            with open(BASE_DIR / saving_path, "w") as f:
                for section, values in settings.items():
                    f.write(f"[{section}]\n")
                    for key, value in values.items():
                        f.write(f"{key} = {value}\n")
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Changes in the parameters set were saved successfully")
        # ToDo
        except Exception as e:
            tk.messagebox.showerror("Error",
                                    f"Saving of teh parameters set failed",
                                    f"Error: {str(e)}", parent=self)
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Saving of the new parameters failed:\n{str(e)}")

    # création du fichier .toml si il n'est pas existant là où il devrait
    def create_default_parameters(self):

        first_load_cell, first_gain = next(iter(DICT_LOAD_CELLS.items()))
        first_test_type, _ = next(iter(DICT_TEST_TYPES.items()))
        _, prefix = self.nommer(BASE_DIR / "results/", debut="", extension="/")

        settings = {
            "data": {
                "speed": DICT_DEFAULT_VALUES.get("speed"),
                "l0": DICT_DEFAULT_VALUES.get("l0"),
                "path_save_data":
                    f"{DICT_DEFAULT_VALUES.get('saving_folder')}",
                "load_cell": f'"{first_load_cell}"',
                "test_type": f'"{first_test_type}"',
                "gain": first_gain,
                "prefix": f'"{str(prefix)}"',
                "ports": f'"{str(ports_movement)}"',
                "ports_state": f'"{str(switch_states_movement)}"',
                "nb_steps": int(nb_steps_mm)
            }
        }

        try:
            with open(hidden_folder / "default_set_parameters.toml", "w") as f:
                for section, values in settings.items():
                    f.write(f"[{section}]\n")
                    for key, value in values.items():
                        f.write(f"{key} = {value}\n")
        except Exception as e:
            tk.messagebox.showerror("Error",
                                    f"The creation of the default parameters "
                                    f"file did not work",
                                    f"Error: {str(e)}", parent=self)
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  f"The creation of the default parameters file "
                  f"did not work:\n{str(e)}")

    # permet de nommer automatiquement un fichier/ dossier en cas de
    # sauvegarde forcée
    def nommer(self, parent_path, debut="", extension=""):

        date_str = datetime.now().strftime("%Y_%m_%d")

        # ToDo: A quoi sert deb ?
        if debut.strip() != "":
            deb = True
            base_name = f"{debut}_{date_str}{extension}"
        else:
            deb = False
            base_name = f"{date_str}{extension}"

        counter = 1
        parent_path = Path(parent_path)
        # ToDo: A quoi sert filename ?
        filename = Path(parent_path / base_name)
        os.makedirs(parent_path, exist_ok=True)

        counter += 1
        if debut == "":
            prefix = f"{date_str}_"
        else:
            prefix = f"{debut}_{date_str}_"

        return parent_path, prefix

    # sauvegarde volontaire du set de paramètres
    def file_save(self):
        self.validate_speed()
        self.validate_l0()
        initial_dir = "./parameters_sets"
        os.makedirs(initial_dir, exist_ok=True)
        f = tkFileDialog.asksaveasfilename(defaultextension=".toml",
                                           initialdir=initial_dir)
        try:

            if f:
                self.write_parameters(f)
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "The parameters set was saved succesfully")

        except Exception as e:
            tk.messagebox.showerror("Error",
                                    f"The parameters set save failed",
                                    f"Error: {str(e)}", parent=self)
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "The parameters set save failed")

    # choix du set de paramètres à ouvrir
    def open_file(self):
        filename = tkFileDialog.askopenfilename(defaultextension=".toml",
                                                initialdir="./parameters_sets")
        if not filename:
            return "no_change"
        with open(filename, "rb") as f:
            data = tomllib.load(f)
        return data

    # ouverture d'un set de paramètres, pour récupérer ses valeurs
    def file_load(self):
        doc = self.open_file()

        if doc == "no_change":
            return

        # Met à jour les variables avec les nouvelles valeurs
        self.speed_var.set(float(doc['data']['speed']))
        self.l0_var.set(float(doc['data']['l0']))
        self.folder_var.set(doc['data']['path_save_data'])
        self.load_cell_var.set(doc['data']['load_cell'])
        self.test_type_var.set(doc['data']['test_type'])

        # Met à jour les dernières valeurs valides
        self.last_valid_speed = float(doc['data']['speed'])
        self.last_valid_l0 = float(doc['data']['l0'])
        self.path_save_data = Path(doc['data']['path_save_data'])

        # Sauvegarde les nouveaux paramètres dans le fichier par défaut
        self.write_parameters(hidden_folder / "default_set_parameters.toml")

        self.entry_folder.xview("end")

        self.update_idletasks()

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
              "The parameters set was loaded succesfully")

    # ouverture du programme Protection_eprouvette, pour pouvoir écarter les
    # mors manuellempent (s'ils sont trop serrés pour mettre la cale)
    def protection_eprouvette(self):
        response = tk.messagebox.askokcancel(
            title="Manual movement",
            message="Have you selected the correct load cell ? \nBe careful, "
                    "the limit switches are deactivated during this phase ",
            parent=self
        )

        if response:
            self.error_end_run()
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "The .npy file has been reinitialized")
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Launching protection_eprouvette.py")
            self.ecriture_commande("protection_eprouvette")
            try:
                self.destroy()
            except Exception as e:
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      f"The window could not close :\n{str(e)}")
                tk.messagebox.showerror("Error",
                                        f"The window could not close",
                                        f"Error: {str(e)}", parent=self)

    # 1e étape de la calibration de position, en plaçant la cale
    def calibrate(self):
        calibration_needed, ref_pos = self.read_calib_n_pos()

        if calibration_needed:
            response = tk.messagebox.askokcancel(
                title="Confirmation",
                message="Have you set up the wedge and selected the "
                        "correct load cell?",
                detail="Be careful, the limit switches are deactivated during "
                       "this phase \nClick OK to start calibration or "
                       "Cancel to abort",
                parent=self
            )
            if response:
                self.calibrate_2()

        else:
            tk.messagebox.showinfo(
                title="Calibration unnecessary",
                message="The last calibration is still correct, you don't "
                        "have to do it again."
            )

            response = tk.messagebox.askokcancel(
                title="Calibration unnecessary",
                message="The last calibration is still correct. Do you still "
                        "want to redo the calibration?",
                parent=self
            )
            if response:
                self.calibrate_2()
            else:
                try:
                    self.activation_buttons()
                    self.update_idletasks()
                except Exception as e:
                    print(time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(time.time())),
                          f"The buttons could not be activated as "
                          f"planned:\n{str(e)}")
                    tk.messagebox.showerror("Error",
                                            f"The buttons could not be "
                                            f"activated as planned",
                                            f"Error: {str(e)}", parent=self)

    # 2e étape de la calibration, en déplaçant le moteur jusqu'à la cale (ou
    # la limite, mais ne devrait pas arriver)
    def calibrate_2(self):

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
              "Starting calibration")
        motor = None
        load_cell = None
        error_occurred = False
        contactor_hit = False

        try:

            self.deactivation_buttons()
            self.update_idletasks()

            motor = ph_stp.Phidget4AStepper(
              steps_per_mm=nb_steps_mm,
              current_limit=3,
              remote=True,
              absolute_mode=True,
              reference_pos=0,
              switch_ports=ports_calibration,
              save_last_pos=True,
              save_pos_folder=hidden_folder,
              switch_states=switch_states_calibration)
            load_cell = ph_whe.PhidgetWheatstoneBridge(
              channel=1,
              gain=DICT_LOAD_CELLS.get(self.load_cell_var.get()),
              remote=True)
            motor.open()
            load_cell.open()

            time.sleep(1)

            data = load_cell.get_data()
            if data is None:
                error_occurred = True
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "Error: no data received from the load cell")
                tk.messagebox.showerror(
                    "Captor error",
                    "The load cell didn't send any value\n"
                    "Calibration failed \nPlease check the connection and "
                    "try again", parent=self)
            else:
                initial_force = data[1]

            hit_obstacle = False

            if not error_occurred:

                try:

                    motor.set_speed(-1)

                    while True:

                        if motor._switch_hit:  # Vérification explicite
                            raise ValueError("Switch hit during calibration!")

                        if load_cell.get_data() is None:
                            error_occurred = True
                            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                                time.localtime(time.time())),
                                  "Error: no more data coming from the load "
                                  "cell")
                            tk.messagebox.showerror(
                                "Signal lost",
                                "The load cell unexpectedly stopped sending "
                                "data\n"
                                "Calibration could not succeed",
                                parent=self
                                )
                            break

                        else:
                            _, current_force = load_cell.get_data()

                            if not hit_obstacle:

                                if (abs(current_force - initial_force) >
                                    FORCE_MAX_CALIB):
                                    current_pos = motor.get_position()
                                    hit_obstacle = True
                                    new_target = (current_pos +
                                                  DECALAGE_POST_CALIBRATION)
                                    # Recule de 5 mm
                                    motor.set_position(new_target, 1)
                                    target_position = new_target
                                    print(
                                        time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(time.time())),
                                        "The motor encountered an obstacle, "
                                        "and shifts a bit from it")

                            else:
                                current_pos = motor.get_position()
                                if (current_pos is not None and
                                    abs(current_pos - target_position) < 0.05):
                                    self.calibrated_pos = (
                                        TAILLE_CALE +
                                        DECALAGE_POST_CALIBRATION)
                                    print(time.strftime(
                                      "%Y-%m-%d %H:%M:%S",
                                      time.localtime(time.time())),
                                      "The motor reached the desired position")
                                    break

                except ValueError:
                    # Interception spécifique de l'erreur de fin de course
                    print(time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(time.time())),
                          f"The contactor / limit switch was hit")
                    contactor_hit = True
                    try:
                        motor.set_speed(0)  # sans cette ligne, les boutons ne
                        # se réactivent pas
                    # ToDo
                    except Exception as e:
                        print(time.strftime("%Y-%m-%d %H:%M:%S",
                                            time.localtime(time.time())),
                              f"After having hit the contactor, the motor "
                              f"could not restart: \n{str(e)}")

        # ToDo
        except Exception as e:
            error_occurred = True
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  f"An error occured during the calibration:\n{str(e)}")
            tk.messagebox.showerror("Error",
                                    f"An error occured during the calibration",
                                    f"Error: {str(e)}", parent=self)

        finally:
            try:
                motor.close()
                load_cell.close()
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "Closing the motor and the load cell")
            except Exception as e:
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      f"The motor and the load cell could not be closed as "
                      f"planned:\n{str(e)}")
            try:
                if contactor_hit:
                    np.save(hidden_folder / 'last_pos.npy', np.array(0))
                else:
                    np.save(hidden_folder / 'last_pos.npy',
                            np.array(DECALAGE_POST_CALIBRATION))
            # ToDo
            except:
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      f"The .npy file could not be overwritten, so the point "
                      f"of the calibration failed:\n{str(e)}")
                self.error_end_run()
                error_occurred = True

            if not error_occurred:
                try:
                    self.activation_buttons()
                except Exception as e:
                    print(time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(time.time())),
                          f"The buttons could not be activated as "
                          f"planned:\n{str(e)}")
                    tk.messagebox.showerror("Error",
                                            f"The buttons could not be "
                                            f"activated as planned",
                                            f"Error: {str(e)}", parent=self)
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "Calibration succeeded")

            else:
                try:
                    self.activation_buttons()
                    self.btn_go.config(state="disabled")
                # ToDo
                except Exception as e:
                    print(time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(time.time())),
                          f"The buttons could not be activated as "
                          f"planned:\n{str(e)}")
                    tk.messagebox.showerror("Error",
                                            f"The buttons could not be "
                                            f"activated as planned:",
                                            f"Error: {str(e)}", parent=self)
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "Calibration failed")
                self.error_end_run()

    # déplacement à la position souhaitée par l'utilisateur
    def go_to_position(self):

        calibration_needed, ref_pos = self.read_calib_n_pos()

        if calibration_needed:  # si la calibation est nécessaire
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Launching the setting in position should not be posible, "
                  "as the motor is not calibrated. Stopping it now")
            tk.messagebox.showerror(
                "Error",
                "You should not be able to launch the positionning, as the "
                "motor is not calibrated", parent=self)

            self.btn_go.config(state="disabled")
            return

        print(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(time.time())),
              "Starting to set in position")

        motor = None
        load_cell = None

        changed_value = self.validate_l0()
        if changed_value == "value_changed":
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Setting in position stopped because the initial distance "
                  "value was changed")
            return

        self.l0 = float(self.l0_var.get())
        target_position = self.l0
        error_occurred = False

        try:

            self.deactivation_buttons()
            self.update_idletasks()

            # ToDo: J'ai déjà vu ce code plus haut, pas possible de le mettre
            #  dans une fonction ?
            motor = ph_stp.Phidget4AStepper(
              steps_per_mm=nb_steps_mm,
              current_limit=3,
              remote=True,
              absolute_mode=True,
              reference_pos=ref_pos,
              save_last_pos=True,
              save_pos_folder=hidden_folder,
              switch_ports=ports_movement,
              switch_states=switch_states_movement)
            load_cell = ph_whe.PhidgetWheatstoneBridge(
              channel=1,
              gain=DICT_LOAD_CELLS.get(self.load_cell_var.get()),
              remote=True)
            motor.open()
            load_cell.open()

            time.sleep(1)

            data = load_cell.get_data()
            if data is None:
                error_occurred = True
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "Error: no data received from the load cell")
                tk.messagebox.showerror(
                    "Captor error",
                    "The load cell didn't send any value\n"
                    "Positionning stopped \nPlease check the connection",
                    parent=self)
            else:
                initial_force = data[1]

            if not error_occurred:

                try:

                    motor.set_position(target_position, 1)

                    while True:

                        if load_cell.get_data() is None:
                            tk.messagebox.showerror(
                                "Signal lost",
                                "The load cell unexpectedly stopped sending "
                                "data\n"
                                "Positionning could not succeed\n"
                                "You must redo the calibration",
                                parent=self
                                )
                            error_occurred = True
                            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                                time.localtime(time.time())),
                                  "Error: no more data coming from the load "
                                  "cell")
                            self.error_end_run()
                            break

                        else:
                            _, current_force = load_cell.get_data()

                            if (abs(current_force-initial_force) >
                                FORCE_MAX_CALIB):  # On s'arrête si force>10N
                                motor.stop()
                                tk.messagebox.showerror(
                                    "Obstacle encountered",
                                    "The load cell measured a force that was "
                                    "not supposed to be so high\n"
                                    "Positionning stopped\n"
                                    "You must redo the calibration",
                                    parent=self
                                    )
                                error_occurred = True
                                self.error_end_run()
                                print(time.strftime(
                                  "%Y-%m-%d %H:%M:%S",
                                  time.localtime(time.time())),
                                  "An obstacle was hit unexpectedly, the "
                                  "motor stopped. Calibration needs to be "
                                  "done again")
                                break

                        current_pos = motor.get_position()
                        if (current_pos is not None and
                            abs(current_pos - target_position) < 0.05):
                            break

                except ValueError as e:
                    # Interception spécifique de l'erreur de fin de course
                    error_occurred = True
                    tk.messagebox.showerror("Error",
                                            f"A switch was hit, you need to "
                                            f"calibrate again",
                                            f"Error: {str(e)}", parent=self)
                    print(time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(time.time())),
                          f"A switch was hit:\n{str(e)}")
                    try:
                        motor.set_speed(0)  # sans cette ligne, les boutons ne
                        # se réactivent pas
                    except Exception as e:
                        print(time.strftime("%Y-%m-%d %H:%M:%S",
                                            time.localtime(time.time())),
                              f"After having hit the contactor, the motor"
                              f" could not restart: \n{str(e)}")

        # ToDo
        except Exception as e:
            error_occurred = True
            tk.messagebox.showerror("Error",
                                    f"An error occured during the setting in "
                                    f"position",
                                    f"Error: {str(e)}", parent=self)
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  f"An error occured during the setting in "
                  f"position:\n{str(e)}")

        finally:
            try:
                motor.close()
                load_cell.close()
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "Closing the motor and the load cell")
            except Exception as e:
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      f"The motor and the load cell could not be closed as "
                      f"planned:\n{str(e)}")
            if not error_occurred:
                try:
                    self.in_position = self.l0
                    self.activation_buttons()
                except Exception as e:
                    tk.messagebox.showerror("Error",
                                            f"The buttons could not be "
                                            f"activated as planned",
                                            f"Error: {str(e)}", parent=self)
                    print(time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(time.time())),
                          f"The buttons could not be activated as "
                          f"planned:\n{str(e)}")
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "Setting in position succeeded")

            else:
                try:
                    self.activation_buttons()
                    self.btn_go.config(state="disabled")
                except Exception as e:
                    tk.messagebox.showerror("Error",
                                            f"The buttons could not be "
                                            f"activated as planned",
                                            f"Error: {str(e)}", parent=self)
                    print(time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime(time.time())),
                          f"The buttons could not be activated as "
                          f"planned:\n{str(e)}")
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "Setting in position failed")
                self.error_end_run()

    # permet de lire le document last_pos.npy, et de dire qu'il faut
    # recalibrer s'il est manquant / s'il contient None (ce qui signifie que
    # le dernier essai a atteint un interrupteur de fin de course)
    def read_calib_n_pos(self):

        last_pos_path = hidden_folder / 'last_pos.npy'
        calibration_needed = True  # Par défaut, calibration nécessaire
        last_pos = None

        try:  # regarder si fichier lisible
            data = np.load(last_pos_path)
            if data.ndim == 0:  # Si c'est un scalaire (0D)
                last_pos = data.item()  # Convertit en float natif
            elif data.ndim == 1:  # Si c'est un tableau 1D
                last_pos = data[0]
            else:
                calibration_needed = True
                last_pos = None
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      f"The array format is not supported")

            if np.isscalar(last_pos) and not np.isnan(last_pos):  # vérifier
              # qu'il y a bien eu une calibration le jour de l'exécution

                timestamp_modif = os.path.getmtime(last_pos_path)
                date_modif = datetime.fromtimestamp(timestamp_modif)
              # dernière modif du fichier

                aujourdhui = datetime.now()
                minuit_aujourdhui = datetime.combine(aujourdhui.date(),
                                                     dt_time.min)

                if date_modif < minuit_aujourdhui:
                    print(f"No calibration has been done today")
                    np.save(last_pos_path, np.nan)

                    calibration_needed = True

                else:  # tout est ok
                    calibration_needed = False

            else:
                calibration_needed = True
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      "Either the last test ended with a limit switch being "
                      "hit, or the jaws were moved manually")

        except Exception as e:
            calibration_needed = True
            last_pos = None
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  f"The .npy file could not be loaded: {str(e)}")
            np.save(last_pos_path, np.array([np.nan], dtype=float))

        if calibration_needed:
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "The system isn't calibrated, so a calibration is needed")
            self.btn_go.config(state="disabled")
            last_pos = None
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Loaded the last position from the .npy file")

        return [calibration_needed, last_pos]

    # fonction à appeler si on atteint un bouton de fin de course durant un
    # test ou si on le bouge manuellement
    def error_end_run(self):
        file_path = hidden_folder / "last_pos.npy"
        np.save(file_path, np.nan)
        try:
            self.btn_go.config(state="disabled")
            self.update_idletasks()
        except Exception as e:
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  f"The buttons could not be activated as planned:\n{str(e)}")
            tk.messagebox.showerror("Error",
                                    f"The buttons could not be deactivated as "
                                    f"planned",
                                    f"Error: {str(e)}", parent=self)

    # permet de désactiver tous les boutons durant la calibration et la mise en
    # position
    def deactivation_buttons(self):
        for btn in self.liste_buttons:
            btn.config(state="disabled")
        self.update_idletasks()
        print(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(time.time())),
              "Deactivating buttons during this phase")

    # permet de réactiver tous les boutons à la fin des opérations précédentes
    def activation_buttons(self):
        for btn in self.liste_buttons:
            btn.config(state="normal")
        self.update_idletasks()
        print(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(time.time())),
              "Activating buttons again")

    # permet d'écrire dans le fichier commande la commande permetatnt de
    # choisir le fichier à ouvrir
    def ecriture_commande(self, commande):
        command_file = hidden_folder / "commande.txt"
        command_file.write_text(commande)
        print(time.strftime("%Y-%m-%d %H:%M:%S",
                            time.localtime(time.time())),
              "Closing the graphical interface now")

    # si on ferme la fenetre par la croix, on arrete tout
    def close_cross(self):
        self.write_parameters(hidden_folder / "default_set_parameters.toml")

        self.ecriture_commande("exit")
        try:
            self.destroy()
        except Exception as e:
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  f"The window could not close:\n{str(e)}")
            tk.messagebox.showerror("Error", f"The window could not close",
                                    f"Error: {str(e)}", parent=self)

    # lancement de l'essai à proprement parler,en emêchant l'utilisateur de
    # commencer s'il n'y a pas eu de calibration
    def demarrage(self):

        calibration_needed, ref_pos = self.read_calib_n_pos()

        if calibration_needed:

            tk.messagebox.showerror(
                title="Missing calibration",
                message="You did not calibrate the machine",
                parent=self
            )
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Can't launch the test if the position is not calibrated")

        elif self.l0 != self.in_position or self.l0_var.get() != self.l0:
            tk.messagebox.showerror(
                title="Missing positioning",
                message="You did not set the machine to the right initial "
                        "distance",
                parent=self
            )
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Can't launch the test if the motor is not is the "
                  "desired position")

        else:
            self.validate_speed()
            self.validate_l0()
            self.write_parameters(hidden_folder /
                                  "default_set_parameters.toml")
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Saving once more the parameters")
            self.ecriture_commande("demarrer_essai")
            try:
                self.destroy()
            except Exception as e:
                print(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime(time.time())),
                      f"The window could not close:\n{str(e)}")
                tk.messagebox.showerror("Error",
                                        f"The window could not close ",
                                        f"Error: {str(e)}", parent=self)

    # crée une couleur aléatoire pour le titre
    def create_couleur_titre(self):
        # Base claire (entre 200 et 255 pour garder des tons pastel)
        r = random.randint(0, 220)
        g = random.randint(0, 220)
        b = random.randint(0, 220)

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
    app = TensileTestP1()
    app.mainloop()

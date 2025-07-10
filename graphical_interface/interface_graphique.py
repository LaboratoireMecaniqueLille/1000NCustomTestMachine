# coding: utf-8

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



"""BASE_DIR is a constant obtained by the bash file, giving the path where
the bash and the 3 python files are located """
BASE_DIR = Path(os.environ.get('BASE_DIR'))
if not BASE_DIR:
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
          "The variable BASE_DIR was not defined")
    sys.exit(1)
print("\n", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
      "The selected base folder is :", BASE_DIR)


"""Folder to save the results by default, and creating it in case it
was deleted"""
SAVING_FOLDER = BASE_DIR / "results"
SAVING_FOLDER.mkdir(parents=True, exist_ok=True)


"""Hidden folder where are saved parameters.toml, commande.txt and
last_pos.npy, and creating it in case it was deleted"""
HIDDEN_FOLDER = BASE_DIR / ".parameters"
HIDDEN_FOLDER.mkdir(parents=True, exist_ok=True)


"""Default parameters, in case the .toml file was deleted and the program 
has to create it to keep working"""
DICT_DEFAULT_VALUES = {"speed": 1,  # float
                       "l0": 20,  # float
                       "saving_folder": SAVING_FOLDER #path
                       }


"""All the posible load cells, and the associated gain.
The name of the load cell has to be a string composed of the maximum
force allowed followed by "N" """
DICT_LOAD_CELLS = {"50N": 3.26496001e+05,
                   "225N": 118328.143
                   }

"""All the different kinds of test possible (they have to be programmed in 
lancement_essai.py, else they are useless). Please also provide an acronym, it 
will be used to name files resulting from this kind of test."""
DICT_TEST_TYPES = {"Monotonic Uniaxial Tensile Test": "MUTT"}


"""Size of the wedge to calibrate the motor, the distance the motor needs to 
shift after the calibration, the force necessary for the load cell to 
detect there was an obstacle / the motor reached its end of course, 
and the maximum length the motor can go by on this machine (it does not need
to be precise, just don't put a value below the real distance)"""
TAILLE_CALE = 14  # in mm
DECALAGE_POST_CALIBRATION = 5  # in mm
FORCE_MAX_CALIB = 10  # in N
MAX_STROKE = 300 # in mm

"""Motor speed: common values are 100 and 2500"""
NB_STEPS_MM = 2500


"""List of ports and their default state following their use
True means open by default, False means close by default"""
ports_movement = tuple([2,3])  # for the final machine tuple([2,3])
switch_states_movement = tuple([True,True])  # for the final machine
                                                # tuple([True, False])
ports_calibration = tuple([2, 3])  # for the final machine tuple([5])
switch_states_calibration = tuple([True])  # for the final machine
                                            # tuple([ ... ])


class TensileTestP1(tk.Tk):

    """Initialization: loading the last parameters used in the program,
    creating a parameters file if the file is missing, and creating the 
    window and its components  """
    def __init__(self):
        super().__init__()

        self.afficher_message("Launching interface_graphique.py")


        """Loading the .toml file"""
        filepath = HIDDEN_FOLDER / "default_set_parameters.toml"
        try:
            with open(filepath, "rb") as f:
                doc = tomllib.load(f)

            default_speed = doc['data']['speed']
            default_l0 = doc['data']['l0']
            default_save_path = Path(doc['data']['path_save_data'])
            default_load_cell = doc['data']['load_cell']
            default_test_type = doc['data']['test_type']

            self.afficher_message("Parameters charged from the last use")

        except FileNotFoundError as e:
            """If the .toml file can't be open or is missing, we create a new one"""
            tk.messagebox.showinfo(title="Parameters file missing",
                                   message=f"An error occured loading the "
                                           f".toml file, a new parameters "
                                           f"file will soon be created",
                                   detail=f"Error: {str(e)}")
            self.afficher_message(f"An error occured loading the .toml file :\n{str(e)}\n"
                                   f"A new parameters file will soon be created")

            self.create_default_parameters()
            self.afficher_message("New parameters set written succesfully")

            filepath = HIDDEN_FOLDER / "default_set_parameters.toml"
            with open(filepath, "rb") as f:
                doc = tomllib.load(f)

            default_speed = doc['data']['speed']
            default_l0 = doc['data']['l0']
            default_save_path = Path(doc['data']['path_save_data'])
            default_load_cell = doc['data']['load_cell']
            default_test_type = doc['data']['test_type']

            self.afficher_message("New parameters set loaded succesfully")


        """Creating some parameters which will be used in all the program"""
        self.in_position = False
        self.path_save_data = default_save_path
        self.liste_buttons = []
        self.calibrated_pos = None
        self.l0 = default_l0
        self.port_1 = None
        self.port_2 = None
        self.port_1_state = None
        self.port_2_state = None

        """Creating the window, its dimensions and its widgets"""
        self.title("Initiating the tensile test")
        self.minsize(675, 500)
        self.geometry("800x600")
        self.create_widgets(default_speed, default_l0,
                            default_load_cell, default_test_type)
        """If you close the window with the cross, everything stops"""
        self.protocol("WM_DELETE_WINDOW", self.close_cross) 

    """Creation  of all the widgets of the page, calling 
    create_parameters_widgets and create_action_widgets"""
    def create_widgets(self, default_speed, default_l0, 
                       default_load_cell, default_test_type):
        """Title"""
        lbl_titre = tk.Label(self,
                             text="Welcome",
                             font=("Helvetica", 20, "bold"),
                             wraplength=150,
                             foreground=self.create_couleur_titre())
        lbl_titre.grid(pady=2, column=2, row=0, columnspan=1)

        """Left frame (parameters)"""
        self.frame_gauche = tk.Frame(self)
        self.create_parameter_widgets(default_speed, default_l0,
                                      default_load_cell, default_test_type)

        """Right frame (actions) """
        self.frame_droite = tk.Frame(self)
        self.create_action_widgets()

        """Start button"""
        self.btn_start = tk.Button(self, 
                                   text="Start",
                                   font=("Helvetica", 13, "bold"),
                                   foreground="red",
                                   command=self.demarrage)

        """Placing these pieces"""
        self.frame_gauche.grid(column=1, row=1, columnspan=1, rowspan=2)
        self.frame_droite.grid(column=3, row=1, columnspan=1, rowspan=2)
        self.btn_start.grid(pady=2, column=2, row=3)
        self.liste_buttons.append(self.btn_start)

        """Setting each row and column (due to the grid coding) to 
        its right place and minsize (so that the window size can coherently 
        change)"""
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

        self.afficher_message("Initialization of the window done")

    """Creation of the left part of the page, with all the entrys and 
    drop down menus"""
    def create_parameter_widgets(self, default_speed, default_l0,
                                 default_load_cell, default_test_type):

        """Speed"""
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

        """Initial distance"""
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

        """Load cell"""
        options_load_cell = list(DICT_LOAD_CELLS.keys())
        initial_load_cell = (default_load_cell if default_load_cell
                             in options_load_cell else options_load_cell[0])
        self.load_cell_var = tk.StringVar(value=initial_load_cell)

        lbl3 = tk.Label(self.frame_gauche, text='Load Cell used',
                        font=("Helvetica", 14), wraplength=600)
        lbl3.grid(pady=(10, 2), column=0, row=4)

        lbl_menu1 = tk.OptionMenu(
          self.frame_gauche, self.load_cell_var, *options_load_cell,
          command=partial(self.write_parameters,HIDDEN_FOLDER /
                                                  "default_set_parameters."
                                                  "toml"))

        lbl_menu1.grid(pady=(2, 10), column=0, row=5)

        """Test Type"""
        options_test_type = list(DICT_TEST_TYPES.keys())
        initial_test_type = (default_test_type if default_test_type in
                             options_test_type else options_test_type[0])
        self.test_type_var = tk.StringVar(value=initial_test_type)

        lbl4 = tk.Label(self.frame_gauche, text='Type of test',
                        font=("Helvetica", 14), wraplength=600)
        lbl4.grid(pady=(10, 2), column=0, row=6)

        lbl_menu2 = tk.OptionMenu(
          self.frame_gauche, self.test_type_var, *options_test_type,
          command=partial(self.write_parameters,HIDDEN_FOLDER /
                                                  "default_set_parameters."
                                                  "toml"))
        lbl_menu2.grid(pady=(2, 10), column=0, row=7)

        """Folder to save the results"""
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
                                       HIDDEN_FOLDER /
                                       "default_set_parameters.toml"))
        self.entry_folder.bind("<Return>",
                               partial(self.write_parameters,
                                       HIDDEN_FOLDER /
                                       "default_set_parameters.toml"))

        self.btn_save = tk.Button(self.frame_g_bas, text="📂",
                                  font=("Helvetica", 13),
                                  command=self.validate_results_folder)
        self.btn_save.grid(pady=(2, 10), column=1, row=1)
        self.liste_buttons.append(self.btn_save)
        self.frame_g_bas.grid(column=0, row=8)


    """Creation of the right side of the page, with all its buttons"""
    def create_action_widgets(self):

        """Top frame (setting in position and calibration)"""
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

        self.btn_go = tk.Button(self.frame_droite.winfo_children()[0],
                                text="Go to desired \nInitial distance",
                                font=("Helvetica", 13),
                                command=self.go_to_position,
                                state="disabled")
        self.btn_go.grid(pady=10, column=0, row=2)
        self.liste_buttons.append(self.btn_go)
        self.frame_d_haut.grid(column=0, row=0, pady=(0, 25))

        """Middle frame (saving and loading parameters files)"""
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

    
    """Manage any value typed for entry_speed, so that it has to be a number and 
    inside the authorised range"""
    def validate_speed(self, *_):
        try:
            value = self.speed_var.get()

        except (ValueError, tk.TclError) as e:
            """If it is not a number"""
            self.speed_var.set(self.last_valid_speed)

            self.speed = self.last_valid_speed
            self.afficher_message("Incorrect speed value (not a valid number)",
                                  showerror=True,
                                  title="Incorrect value",
                                  info="Please enter a valid number")
            return

        
        if 0 < value <= 2.5:
            """If the value is correct"""
            self.last_valid_speed = value
            self.write_parameters(HIDDEN_FOLDER /
                                  "default_set_parameters.toml")
            return

        """If the value is out of bounds"""
        response = tk.messagebox.askokcancel(
            "Value out of bounds",
            f"The speed {value} mm/s is out of bounds (0-2.5 mm/s). \n"
            f"The speed will be set on its default value : "
            f"{DICT_DEFAULT_VALUES.get("speed")} mm/s",
            parent=self
        )
        self.afficher_message("Incorrect speed value (out of bounds)")
        
        """Either the user validates and the speed value goes to its default 
        value, or they decline and it goes back to the last valid speed"""
        if response:  
            value = 1
            self.speed = value
            self.last_valid_speed = value
            self.speed_var.set(DICT_DEFAULT_VALUES.get("speed"))
        else:  
            self.speed_var.set(float(self.last_valid_speed))
            self.speed = self.last_valid_speed


    """Manage any value typed for entry_l0, so that it has to be a number and 
    inside the authorised range"""
    def validate_l0(self, *_):

        try:
            current_value = self.l0_var.get()
            value = round(current_value, 1)

        except (ValueError, tk.TclError) as e:  
            """If it is not a number"""
            self.l0_var.set(self.last_valid_l0)
            self.l0 = self.last_valid_l0
            self.afficher_message("Incorrect initial distance value "
                                  "(not a valid number)",
                                  showerror=True,
                                  title="Incorrect value",
                                  info="Please enter a valid number")
            return

        
        if 0 < value < MAX_STROKE:
            """If the value is correct"""
            self.l0 = value
            self.last_valid_l0 = value
            self.write_parameters(HIDDEN_FOLDER /
                                  "default_set_parameters.toml")
            return

        """If the value is out of bounds"""
        response = tk.messagebox.askokcancel(
            "Value out of bounds",
            f"The initial distance {value} mm is out of bounds "
            "(1-300 mm). \n The inital distance will be set on its"
            f" default value : {DICT_DEFAULT_VALUES.get("l0")} mm",
            parent=self
        )
        self.afficher_message("Incorrect initial distance value (out"
                              " of bounds)")

        """Either the user validates and the intial distance value
        goes to its default value, or they decline and it goes back
        to the last valid initial distance"""
        if response:  
            value = 20
            self.l0 = value
            self.last_valid_l0 = value
            self.l0_var.set(DICT_DEFAULT_VALUES.get("l0"))
        else:  
            self.l0_var.set(float(self.last_valid_l0))
            self.l0 = self.last_valid_l0
        return "value_changed"
    

    """Manages the button which allows to choose the folder where
    the results will be saved"""
    def validate_results_folder(self):

        selected_dir = tkFileDialog.askdirectory(
          initialdir=BASE_DIR / "results/")

        if not selected_dir:  
            """Cancel sends back an empty string, so we just stop 
            this function"""
            return

        self.path_save_data = Path(selected_dir)

        
        self.path_save_data.mkdir(parents=True, exist_ok=True)
        

        self.entry_folder.delete(0, tk.END)
        self.entry_folder.insert(tk.END, str(self.path_save_data))
        self.entry_folder.grid(column=0, row=1)
        self.write_parameters(HIDDEN_FOLDER / "default_set_parameters.toml")
        self.entry_folder.xview("end")

    """As there can be from 0 to 2 ports in the ports lists (movement/calibration)
    and we want to split them to be able to transfer them easily, this function 
    affects the ports and their state to self.port_i and self.port_i_state
    This function has to be called just before writing the values above in
    the .toml file"""
    def split_ports_list(self, ports, ports_state):
        for i in range(2):
            if i==0:
                try:
                    self.port_1 = ports[i]
                    self.port_1_state = ports_state[i]
                except IndexError:
                    self.port_1 = ""
                    self.port_1_state = ""
            if i==1:
                try:
                    self.port_2 = ports[i]
                    self.port_2_state = ports_state[i]
                except IndexError:
                    self.port_2 = ""
                    self.port_2_state = ""


    """If any entry or drop down menu is clicked or changed, the values are all
    written in the .toml file to be saved, and be possibly used. It is also called
    when the user wants to save his set of data for later"""
    
    def write_parameters(self, saving_path, *_):

        test_type = str(self.test_type_var.get())
        path_results = self.folder_var.get()
        """If there is an empty path, the results will be stored in results.
        Also, a prefix will be given  to the title of the results following
        the type of test used"""
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
        self.split_ports_list(ports_movement, switch_states_movement)

        settings = {
            "data": {
                "speed": float(self.speed_var.get()),
                "l0": float(self.l0_var.get()),
                "path_save_data": f'"{str(path_results)}"',
                "load_cell": f'"{str(self.load_cell_var.get())}"',
                "test_type": f'"{str(self.test_type_var.get())}"',
                "gain": float(gain),
                "prefix": f'"{str(prefix)}"',
                "port_1": f'"{self.port_1}"',
                "port_1_state": f'"{str(self.port_1_state)}"',
                "port_2": f'"{self.port_2}"',
                "port_2_state": f'"{str(self.port_2_state)}"',
                "nb_steps": int(NB_STEPS_MM)
            }
        }

        with open(BASE_DIR / saving_path, "w") as f:
            for section, values in settings.items():
                f.write(f"[{section}]\n")
                for key, value in values.items():
                    f.write(f"{key} = {value}\n")
        self.afficher_message("Changes in the parameters set were "
                                "saved successfully")
        


    """If the .toml file does not exist where it should, the program creates 
    a new one in the right place, with the default parameters written above 
    this program"""
    def create_default_parameters(self):

        first_load_cell, first_gain = next(iter(DICT_LOAD_CELLS.items()))
        first_test_type, _ = next(iter(DICT_TEST_TYPES.items()))
        _, prefix = self.nommer(BASE_DIR / "results/", debut="", extension="/")

        self.split_ports_list(ports_movement, switch_states_movement)

        settings = {
            "data": {
                "speed": DICT_DEFAULT_VALUES.get("speed"),
                "l0": DICT_DEFAULT_VALUES.get("l0"),
                "path_save_data":
                    f'"{DICT_DEFAULT_VALUES.get('saving_folder')}"',
                "load_cell": f'"{first_load_cell}"',
                "test_type": f'"{first_test_type}"',
                "gain": first_gain,
                "prefix": f'"{str(prefix)}"',
                "port_1": f'"{self.port_1}"',
                "port_1_state": f'"{str(self.port_1_state)}"',
                "port_2": f'"{self.port_2}"',
                "port_2_state": f'"{str(self.port_2_state)}"',
                "nb_steps": int(NB_STEPS_MM)
                

            }
        }

        with open(HIDDEN_FOLDER / "default_set_parameters.toml", "w") as f:
            for section, values in settings.items():
                f.write(f"[{section}]\n")
                for key, value in values.items():
                    f.write(f"{key} = {value}\n")
    

    """Allows to name any file (adds a prefix specifying the date and 
    the type of test), and also gives the path to it"""
    def nommer(self, parent_path, debut="", extension=""):

        date_str = datetime.now().strftime("%Y_%m_%d")

        if debut.strip() != "":
            base_name = f"{debut}_{date_str}{extension}"
        else:
            base_name = f"{date_str}{extension}"

        parent_path = Path(parent_path)
        os.makedirs(parent_path, exist_ok=True)

        if debut == "":
            prefix = f"{date_str}_"
        else:
            prefix = f"{debut}_{date_str}_"

        return parent_path, prefix

    """If the user wants to save a set of parameters for a later use, 
    this function creates a new .toml file ine the /parameters/ folder"""
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
                self.afficher_message("The parameters set was saved succesfully")

        except PermissionError as e:
            self.afficher_message("The parameters set save failed", 
                                  showerror=True,
                                  title="Error",
                                  info=f"The parameters set save failed",
                                  detail=f"Error: {str(e)}")


    """Opens a window to choose which set of paramters open"""
    def open_file(self):
        filename = tkFileDialog.askopenfilename(defaultextension=".toml",
                                                initialdir="./parameters_sets")
        if not filename:
            return "no_change"
        with open(filename, "rb") as f:
            data = tomllib.load(f)
        return data

    """Allows to load a set of parameters (that was previoulsy saved by 
    self.save_file)"""
    def file_load(self):
        doc = self.open_file()

        if doc == "no_change":
            return

        """Update of the values of many variables, including the 
        ones storing the last valid value"""
        self.speed_var.set(float(doc['data']['speed']))
        self.l0_var.set(float(doc['data']['l0']))
        self.folder_var.set(doc['data']['path_save_data'])
        self.load_cell_var.set(doc['data']['load_cell'])
        self.test_type_var.set(doc['data']['test_type'])

        self.last_valid_speed = float(doc['data']['speed'])
        self.last_valid_l0 = float(doc['data']['l0'])
        self.path_save_data = Path(doc['data']['path_save_data'])

        """Also save the value in the default .toml file"""
        self.write_parameters(HIDDEN_FOLDER / "default_set_parameters.toml")

        """Update of the page"""
        self.entry_folder.xview("end")
        self.update_idletasks()

        self.afficher_message("The parameters set was loaded succesfully")


    """After asking verification to the user, it closes the page to execute 
    protection_eprouvette.py, which allows to manually move the jaws (in order
    to shift from the end course buttons for example)"""
    def protection_eprouvette(self):
        response = tk.messagebox.askokcancel(
            title="Manual movement",
            message="Have you selected the correct load cell? \nBe careful, "
                    "the limit switches are deactivated during this phase ",
            parent=self
        )

        if response:
            self.error_end_run()
            self.afficher_message("The .npy file has been reinitialized")
            self.validate_speed()
            self.validate_l0()
            self.write_parameters(HIDDEN_FOLDER /
                                  "default_set_parameters.toml")
            self.afficher_message("Saving once more the parameters")
            self.afficher_message("Launching protection_eprouvette.py")
            self.ecriture_commande("protection_eprouvette")
            self.destroy()
            


    """First step of the calibration, asking the user if indeed they want to 
    calibrate, and checking if it is necessary (unnecessary if already calibrated 
    the same day, not moved manually since)"""
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
                self.activation_buttons()
                self.update_idletasks()
                
    """Manages the movement of the motor during the calibration and the 
    setting in position, adapting to the selected mode
    After connecting to the motor and the load cell (checking there is no TimeOutError)
    and checking permanently if data keeps coming from the motor, or else the function
    stops. 
    For the calibration, the course of the jaws is: going as far towards the load cell, 
    and when meeting an obstacle (detected by an increase in the force), going back 
    in the other direction for a small distance. For the positionning, it works the same
    way, except it does not shifts after meeting an obstacle, which is instead 
    considered an error as it is not supposed to happen """
    def movement_motor(self, move_type, ref_posit=0):
        """move_type can be "calibration" or "setting_position"
        contactor_hit comes with a calibration, while 
        target_position is linked to setting the motor in position"""
        
        if move_type=="calibration":
            calib=True
            text= "Calibration"
        elif move_type=="setting_position":
            calib=False
            text="Positionning"
        else:
            return

        motor = None
        load_cell = None
        error_occurred = False
        setting_already_ok = False #won't be used if calib
       
        if calib:
            contactor_hit = False
            hit_obstacle = False
            ports = ports_calibration
            switch_state = switch_states_calibration
        else:
            changed_value = self.validate_l0()
            if changed_value == "value_changed":
                self.afficher_message("Setting in position stopped because "
                    "the initial distance value was changed")
                return
            self.l0 = float(self.l0_var.get())
            target_position = self.l0

            ports = ports_movement
            switch_state = switch_states_movement

        self.deactivation_buttons()
        self.update_idletasks()

        try: 
            """Allows to gather the error in case a contactor / switch is hit"""

            motor = ph_stp.Phidget4AStepper(
                steps_per_mm=NB_STEPS_MM,
                current_limit=3,
                remote=True,
                absolute_mode=True,
                reference_pos=ref_posit,
                switch_ports=ports,
                save_last_pos=True,
                save_pos_folder=HIDDEN_FOLDER,
                switch_states=switch_state)
            load_cell = ph_whe.PhidgetWheatstoneBridge(
                channel=1,
                gain=DICT_LOAD_CELLS.get(self.load_cell_var.get()),
                remote=True)
            


            if not calib :
                """Checking the motor has to move, else it creates a problem where the motor
                won't start again after"""
                if ref_posit is not None: 
                    distance =  abs(round(target_position,3)-round(ref_posit,3))
                    if distance <0.05 :
                        setting_already_ok=True
                        self.afficher_message("The desired position has already been reached by" \
                                            " previous settings")


            if calib or not setting_already_ok:
                try :
                    """Allows to gather the error in case the connection to the motor fails"""
                    motor.open()
                    load_cell.open()

                except TimeoutError:
                    self.afficher_message("Error: took too long to connect to the machine",
                                            showerror=True,
                                            title="Connection error",
                                            info="The connection to the tensile test machine"
                                            " could not be established. Please check the connection"
                                            " and try again")
                    self.activation_buttons()
                    return

                self.afficher_message("Connection to the motor and the load cell achieved")
                time.sleep(1)

                data = load_cell.get_data()
                if data is None:
                    error_occurred = True
                    self.afficher_message("Error: no data received from the load cell",
                                            showerror=True,
                                            title="Captor error",
                                            info="The load cell didn't send any value\n"
                                            f"{text} failed \nPlease check the connection"
                                            " and try again")
                    
                else:
                    initial_force = data[1]


                if not error_occurred :
                    
                    if calib:
                        motor.set_speed(-1)
                    else:
                        motor.set_position(target_position,1)


                    while True:



                        if calib:
                            if motor._switch_hit: 
                                """Explicit checking"""
                                raise ValueError("Switch hit during calibration!")

                        current_force = load_cell.get_data()

                        if current_force is None:
                            error_occurred = True
                            self.afficher_message("Error: no more data coming from "
                                                    "the load cell",
                                                    showerror=True,
                                                    title="Signal lost",
                                                    info=f"The load cell unexpectedly "
                                                    "stopped sending data \n"
                                                    f"{text} could not succeed")
                            if not calib:
                                self.error_end_run()
                            break

                        else:
                            current_force = current_force[1]

                            if calib:
                                if not hit_obstacle:

                                    if (abs(current_force - initial_force) >
                                        FORCE_MAX_CALIB):
                                        current_pos = motor.get_position()
                                        hit_obstacle = True
                                        new_target = (current_pos +
                                                        DECALAGE_POST_CALIBRATION)
                                        """Small shift from the obstacle"""
                                        motor.set_position(new_target, 1)
                                        target_position = new_target
                                        self.afficher_message("The motor encountered an"
                                            " obstacle, and shifts a bit from it")

                                else:
                                    current_pos = motor.get_position()
                                    if (current_pos is not None and
                                        abs(current_pos - target_position) < 0.05):
                                        self.calibrated_pos = (
                                            TAILLE_CALE +
                                            DECALAGE_POST_CALIBRATION)
                                        self.afficher_message("The motor reached the"
                                                            " desired position")
                                        break

                            else:
                                if (abs(current_force-initial_force) >
                                FORCE_MAX_CALIB):  
                                    """Stopping if it meets an obstacle, as it should not 
                                    happen"""
                                    motor.stop()
                                    error_occurred = True
                                    self.error_end_run()
                                    self.afficher_message("An obstacle was hit unexpectedly"
                                        ", the motor stopped. Calibration needs to be "
                                        "done again",
                                        showerror=True,
                                        title="Obstacle encountered",
                                        info=f"The load cell measured a force that was not "
                                        "not supposed to be so high\n Positionning stopped\n"
                                        "You must redo the calibration")
                                    break
                                
                                current_pos = motor.get_position()
                                if (current_pos is not None and
                                    abs(current_pos - target_position) < 0.05):

                                    self.afficher_message("The target position has " \
                                    "been reached")
                                    break

                        time.sleep(0.01)

                    



        except ValueError as e:

            if calib: 
                """Catching the specific error due to a hit with the end course
                button"""
                motor.set_speed(0)
                self.afficher_message(f"The contactor / limit switch was hit")
                contactor_hit = True
                
                """Without this line, the function stops working"""
                
            
            else:
                """Catching the specific error due to a hit with the end course
                button"""
                error_occurred = True

                self.afficher_message(f"A switch was hit:\n{str(e)}",
                                        showerror=True,
                                        title="Error",
                                        info=f"A switch was hit, you need to "
                                        "calibrate again")
                motor.set_speed(0)  
                """Without this line, the function stops working """


        finally:

            if not setting_already_ok:
                motor.close()
                load_cell.close()
                self.afficher_message("Closing the motor and the load cell")
                """Saving the ending position into a special file as 0, so that it 
                can be used as the new reference position"""

            if calib:
                if contactor_hit:
                    np.save(HIDDEN_FOLDER / 'last_pos.npy', np.array(0))
                else:
                    np.save(HIDDEN_FOLDER / 'last_pos.npy',
                            np.array(DECALAGE_POST_CALIBRATION))

            if not error_occurred:
                self.activation_buttons()
                self.afficher_message(f"{text} succeeded")
                if not calib:
                    self.in_position = self.l0
                    """Saving the reached position as the current position, so that 
                    the motor knows how much to move from the next time this function
                    is used"""

            else:
                self.activation_buttons()
                self.btn_go.config(state="disabled")
                self.afficher_message(f"{text} failed")
                self.error_end_run()
            return

    """Second step of the calibration: actually moving
    Every step is done inside self.movement_motor() """
    def calibrate_2(self):

        self.afficher_message("Starting calibration")
        self.movement_motor(move_type="calibration")
        

    """Allows to move the jaws to the psoition desired by the user.
    It is also coded by self.movement_motor() """
    def go_to_position(self):

        calibration_needed, ref_pos = self.read_calib_n_pos()

        if calibration_needed:  
            """If the calibration is necessary, but it shouldn't happen as the 
            button should be deactivated is this case"""
            self.afficher_message("Launching the setting in position should not "
                  "be possible, as the motor is not calibrated. Stopping it now",
                  showerror=True,
                  title="Error",
                  info="You should not be able to launch the positionning, as the "
                  "motor is not calibrated")

            self.btn_go.config(state="disabled")
            return

        self.afficher_message("Starting to set in position")

        self.movement_motor(move_type="setting_position",ref_posit=ref_pos)



    """Reads the last_pos.npy file (produced by crappy, indicating the last position
    reached), and tells if a calibration is needed (file missing/ contains None 
    (meaning the motor last stopped after an end course button))"""
    def read_calib_n_pos(self):

        last_pos_path = HIDDEN_FOLDER / 'last_pos.npy'
        calibration_needed = True  
        last_pos = None
        """By default, a calibration is needed"""

        try:  
            """If the file is readable """
            data = np.load(last_pos_path, allow_pickle=True)            

            if data.ndim == 0: 
                """If the data is a 0D scalar"""
                last_pos = data.item()  
            elif data.ndim == 1:  
                """If the data is a 1D array"""
                last_pos = data[0]
            else:
                calibration_needed = True
                last_pos = None
                self.afficher_message(f"The array format is not supported")

            if np.isscalar(last_pos) and not np.isnan(last_pos):  
                """Chacks if a calibration was done the current day"""

                timestamp_modif = os.path.getmtime(last_pos_path)
                date_modif = datetime.fromtimestamp(timestamp_modif)
                """Last modification of the file"""

                aujourdhui = datetime.now()
                minuit_aujourdhui = datetime.combine(aujourdhui.date(),
                                                     dt_time.min)

                if date_modif < minuit_aujourdhui:
                    self.afficher_message("No calibration has been done today")
                    np.save(last_pos_path, np.nan)

                    calibration_needed = True

                else: 
                    """If everything is alright, no calibration is needed"""
                    calibration_needed = False

            else:
                calibration_needed = True
                self.afficher_message("Either the last test ended with"
                                      " a limit switch being hit, or the "
                                      "jaws were moved manually")

        except FileNotFoundError as e:
            calibration_needed = True
            last_pos = None
            self.afficher_message(f"The .npy file could not be loaded: {str(e)}")
            np.save(last_pos_path, np.array([np.nan], dtype=float))

        if calibration_needed:
            self.afficher_message("The system isn't calibrated, so"
                                  " a calibration is needed")
            self.btn_go.config(state="disabled")
            last_pos = None
        else:
            self.afficher_message("Loaded the last position from the .npy file")

        return [calibration_needed, last_pos]


    """Function to call if and end course button was activated or if the motor
    was moved manually, to modify last_pos.npy, in order to indicate the last 
    calibration is no longer useable, and that the user needs to do it again"""
    def error_end_run(self):
        file_path = HIDDEN_FOLDER / "last_pos.npy"
        np.save(file_path, np.nan)
        self.btn_go.config(state="disabled")
        self.update_idletasks()
            

    """Deactivates all buttons during calibration and setting in position"""
    def deactivation_buttons(self):
        for btn in self.liste_buttons:
            btn.config(state="disabled")
        self.update_idletasks()
        self.afficher_message("Deactivating buttons during this phase")

    """Reactivates all buttons at the end of calibration and setting in position"""
    def activation_buttons(self):
        for btn in self.liste_buttons:
            btn.config(state="normal")
        self.update_idletasks()
        self.afficher_message("Activating buttons again")


    """Writes the file commande.txt, which is read by the bash file, in order to 
    communicate which python file should be executed next, or if the program
    needs to stop"""
    def ecriture_commande(self, commande):
        command_file = HIDDEN_FOLDER / "commande.txt"
        command_file.write_text(commande)
        self.afficher_message("Closing the graphical interface now")

    """Closes everything if the window is closed through the crose"""
    def close_cross(self):
        self.write_parameters(HIDDEN_FOLDER / "default_set_parameters.toml")

        self.ecriture_commande("exit")
        self.destroy()
        


    """Beginning of the proper test, after checking that the calibration 
    and the setting in position were made correctly"""
    def demarrage(self):

        calibration_needed, _ = self.read_calib_n_pos()

        if calibration_needed:

            self.afficher_message("Can't launch the test if the"
                                  " position is not calibrated",
                                  showerror=True,
                                  title="Missing calibration",
                                  info=f"You did not calibrate the machine")
            
        elif self.l0 != self.in_position or self.l0_var.get() != self.l0:

            self.afficher_message("Can't launch the test if the"
                                  " position is not calibrated",
                                  showerror=True,
                                  title="Missing calibration",
                                  info=f"You did not set the machine"
                                  " to the right initial distance")
        else:
            self.validate_speed()
            self.validate_l0()
            self.write_parameters(HIDDEN_FOLDER /
                                  "default_set_parameters.toml")
            self.afficher_message("Saving once more the parameters")
            self.ecriture_commande("demarrer_essai")
            self.destroy()

                
    """Random color for the title of the page"""
    def create_couleur_titre(self):
        """Random number for each component"""
        r = random.randint(0, 220)
        g = random.randint(0, 220)
        b = random.randint(0, 220)

        """Makes a random color stronger"""
        composante = random.choice([0, 1, 2])
        if composante == 0:
            r = random.randint(120, 170)
        elif composante == 1:
            g = random.randint(120, 170)
        else:
            b = random.randint(120, 170)

        return f"#{r:02x}{g:02x}{b:02x}"
    

    """Prints every message in the terminal, and also allows to display showerror 
    windows to communicate main information to the user"""
    def afficher_message(self, message, showerror=False, title="", info="", detail=""):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), message)
        
        if showerror:
            if isinstance(info, str):
                if info.strip()=="":
                    info = message

            tk.messagebox.showerror(
                title=title,
                message=info,
                detail=detail,
                parent=self
                )


if __name__ == '__main__':
    app = TensileTestP1()
    app.mainloop()

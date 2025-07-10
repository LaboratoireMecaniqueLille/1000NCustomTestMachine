# coding: utf-8


import tomllib
import os
import sys
import tkinter as tk
import time
from pathlib import Path
import threading
import crappy.actuator.phidgets_stepper4a as ph_stp
import crappy.inout.phidgets_wheatstone_bridge as ph_whe

"""Settings to have a speed linked to the force applied to the load cell"""
DICT_DEFAULT_PARAMETERS = {"speed_levels": [0.5, 1, 1.5, 2, 2.5], # in mm/s
                           "thresh_force": [10, 20, 30, 40, 50]  # in Newton
                           }


"""Prints every message in the terminal, and also allows to display showerror 
windows to communicate main information to the user"""
def afficher_message(message, showerror=False, title="", info="", detail=""):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), message)
        
        if showerror:
            if isinstance(info, str):
                if info.strip()=="":
                    info = message

            tk.messagebox.showerror(
                title=title,
                message=info,
                detail=detail
                )

"""Executed in a different thread than the Tkinter window
Controls the motor and the load cell  (following the force applied by the user 
as long as they don't stop the execution, and as long as the load cell keeps
sending data) """
def control_loop(gui,
                 motor,
                 load_cell,
                 initial_force,
                 thresh_force,
                 speed_levels):
    
    while not gui.stop_flag:
        force_value = load_cell.get_data()
        if force_value is None:
            afficher_message("Error: no more data coming from the motor",
                             showerror=True, title="Signal lost",
                             info="The load cell unexpectedly stopped sending data\n"
                             "Please check the connection and try again")
            
            gui.error = True
            gui.stop()
            break

        
        _, current_force = force_value
        force = current_force - initial_force
        
        """ level_speed keeps the last valid value"""
        speed = 0
        for threshold, level_speed in zip(thresh_force, speed_levels):
            if abs(force) >= threshold:
                speed = level_speed  
            else:
                break  

        if force >= 0:
            motor.set_speed(-speed)
        elif force < 0:
            motor.set_speed(speed)

    """Closing"""
    motor.set_speed(0)
    motor.close()
    load_cell.close()


"""Subclass of Tkinter defined to manage the interface"""
class ControlGUI(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Control")
        self.stop_flag = False
        self.error = False
        self.stop_btn = tk.Button(self, text="Stop", command=self.stop,
                                  fg="black", font=("Arial", 13))
        self.stop_btn.pack(padx=20, pady=20)
    
    """Stops the class by destroying the window"""
    def stop(self):
        self.stop_flag = True
        self.destroy()


if __name__ == '__main__':

    afficher_message("Launching protection_eprouvette.py")
        
    """BASE_DIR is a constant obtained through the bash file, showing the path 
    towards this file, necessary for a correct execution"""
    BASE_DIR = Path(os.environ.get('BASE_DIR'))
    if not BASE_DIR:
        raise EnvironmentError("The variable BASE_DIR was not defined")
    """Path to the parameters set"""
    path_set = BASE_DIR / ".parameters/default_set_parameters.toml"

    """Gathering the necessary data from the parameters set, and stopping the 
    execution if it can't be open """
    try:
        with open(path_set, "rb") as f:
            donnees = tomllib.load(f)
        gain = float(donnees['data']['gain'])
        nb_steps = float(donnees['data']['nb_steps'])
        afficher_message("Loading parameters from the .toml file")
        
    except FileNotFoundError as e:
        afficher_message('The .toml file to communicate experimental '
                         'parameters was not found, the program stopped',
                         showerror=True, title="Parameters set file missing", 
                         info="The program could not be executed as the " \
                         "parameters set could not be open and/or found",
                         detail=f"Error: {str(e)}")
        sys.exit(1)


    thresh_force = DICT_DEFAULT_PARAMETERS.get("thresh_force")
    speed_levels = DICT_DEFAULT_PARAMETERS.get("speed_levels")

    afficher_message("Starting the motor now")
 
    """Initialization of the motor and the load cell"""
    motor = None
    load_cell = None
    error_occurred = False


    motor = ph_stp.Phidget4AStepper(steps_per_mm=nb_steps, current_limit=3, 
                                    remote=True, switch_ports=())
    load_cell = ph_whe.PhidgetWheatstoneBridge(channel=1, gain=gain,
                                            remote=True)
        
    try:
        motor.open()
        load_cell.open()
    except TimeoutError:
        afficher_message("Error: took too long to connect to the machine",
                                        showerror=True,
                                        title="Connection error",
                                        info="The connection to the tensile test machine"
                                        " could not be established. Please check the connection"
                                        " and try again")
        sys.exit(1)

    
    afficher_message("Connection to the motor and to the load cell achieved")
    time.sleep(1)

    data = load_cell.get_data()
    """First check: is there any data coming from the load cell"""

    if data is None:
        error_occurred = True
        afficher_message("Error: no data received from the motor", showerror=True,
                            title="Captor error", info="The load cell didn't send any"
                            " value\nPlease check the connection and try again")
    else:
        initial_force = data[1]

    """Launching the process of moving according to the force during, and 
    simulaneously displaying a window to allow the user to stop whenever they want"""
    if not error_occurred:
        gui = ControlGUI()
        
        """Running a separate thread specially for the control of the motor
        and the load cell"""
        control_thread = threading.Thread(
            target=control_loop,
            args=(gui, motor, load_cell, initial_force, thresh_force,
                speed_levels),
            daemon=True
        )
        control_thread.start()
        
        """In the main thread, the Tkinter window is running"""
        gui.mainloop()
        
        """Cleaning after closing the window"""
        gui.stop_flag = True
        control_thread.join(timeout=1)

        afficher_message("End of the manual movement")



    if not error_occurred and not gui.error:
        afficher_message("Setting in position succeeded")
                
    else:
        afficher_message("Setting in position failed")
    
    motor.close()
    load_cell.close()
    afficher_message("Closing the motor and the load cell")

    
    afficher_message("Going back to the graphical interface")

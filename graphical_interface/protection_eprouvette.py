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


DICT_DEFAULT_PARAMETERS = {"speed_levels": [0.5, 1, 1.5, 2, 2.5], # in mm/s
                           "thresh_force": [10, 20, 30, 40, 50]  # in Newton
                           }


def control_loop(gui,
                 motor,
                 load_cell,
                 initial_force,
                 thresh_force,
                 speed_levels):
    while not gui.stop_flag:
        if load_cell.get_data() is None:
            tk.messagebox.showerror(
              "Signal lost",
              "The load cell unexpectedly stopped sending data\n"
              "Please check the connection and try again")
            print(time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime(time.time())),
                  "Error: no more data coming from the motor")
            # ToDo: Tu peux fermer le GUI ici directement s'il y a une erreur
            gui.stop_flag = True
            gui.error = True
            break

        # ToDo: Tu appelles get_data deux fois, tu devrais l'appeler une fois
        #  et stocker le résultat
        _, current_force = load_cell.get_data()
        force = current_force - initial_force
        print(force)
        
        if abs(force) < thresh_force[0] or abs(force) > thresh_force[-1]:
            speed = 0
        else:
            for threshold, level_speed in zip(thresh_force, speed_levels):
                if abs(force) >= threshold:
                    speed = level_speed  # Garde la dernière vitesse valide
                else:
                    break  # Sortir dès qu'un seuil n'est pas atteint

        # ToDo: Il se passe quoi si on break dès le début ?
        if force > 0:
            motor.set_speed(-speed)
        elif force < 0:
            motor.set_speed(speed)

    motor.set_speed(0)
    motor.close()
    load_cell.close()


# ToDo: Fais de cette classe une subclass de tk.Tk() ce sera plus propre
class ControlGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Control")
        self.stop_flag = False
        self.error = False
        self.stop_btn = tk.Button(self.root, text="Stop", command=self.stop,
                                  fg="black", font=("Arial", 13))
        self.stop_btn.pack(padx=20, pady=20)
        
    def stop(self):
        self.stop_flag = True
        self.root.destroy()


if __name__ == '__main__':
  print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
        "Launching protection_eprouvette.py")

  BASE_DIR = Path(os.environ.get('BASE_DIR'))
  if not BASE_DIR:
      raise EnvironmentError("The variable BASE_DIR was not defined")

  path_set = BASE_DIR / ".parameters/default_set_parameters.toml"
  try:
    with open(path_set, "rb") as f:
        donnees = tomllib.load(f)
    gain = float(donnees['data']['gain'])
    nb_steps = float(donnees['data']['nb_steps'])
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
          "Loading parameters from the .toml file")
  # ToDo
  except:
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
          'The .toml file to communicate experimental parameters was not '
          'found, the program stopped')
    try:
        sys.exit()
    except Exception as e:
        tk.messagebox.showerror("Error", f"The program could not close",
                                f"Error: {str(e)}")

  thresh_force = DICT_DEFAULT_PARAMETERS.get("thresh_force")
  speed_levels = DICT_DEFAULT_PARAMETERS.get("speed_levels")

  print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
        "Starting the motor now")

  motor = None
  load_cell = None
  error_occurred = False

  try:

    motor = ph_stp.Phidget4AStepper(steps_per_mm=nb_steps, current_limit=3, 
                                    remote=True, switch_ports=())
    load_cell = ph_whe.PhidgetWheatstoneBridge(channel=1, gain=gain,
                                               remote=True)
    motor.open()
    load_cell.open()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
          "Connection to the motor and to the load cell achieved")
    time.sleep(1)

    data = load_cell.get_data()
    if data is None:
        error_occurred = True
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
              "Error: no data received from the motor")
        tk.messagebox.showerror(
            "Captor error", 
            "The load cell didn't send any value\n"
            "Please check the connection and try again"
        )
    else:
        initial_force = data[1]

    if not error_occurred:
        gui = ControlGUI()
        
        # Lancement de la boucle de contrôle dans un thread séparé
        control_thread = threading.Thread(
            target=control_loop,
            args=(gui, motor, load_cell, initial_force, thresh_force,
                  speed_levels),
            daemon=True
        )
        control_thread.start()
        
        # Lancement de la boucle principale Tkinter
        gui.root.mainloop()
        
        # Nettoyage après fermeture de la fenêtre
        gui.stop_flag = True
        control_thread.join(timeout=1)

        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
              "End of the manual movement")

  # ToDo: Précise l'exception
  except Exception as e:
      error_occurred = True
      tk.messagebox.showerror(
        "Error",
        f"An error occured during the setting in position",
        f"Error: {str(e)}")

  finally:
      if not error_occurred and not gui.error:
          print(time.strftime("%Y-%m-%d %H:%M:%S",
                              time.localtime(time.time())),
                "Setting in position succeeded")
                
      else:
          print(time.strftime("%Y-%m-%d %H:%M:%S",
                              time.localtime(time.time())),
                "Setting in position failed")
    
      try:
          motor.close()
          load_cell.close()
          print(time.strftime("%Y-%m-%d %H:%M:%S",
                              time.localtime(time.time())),
                "Closing the motor and the load cell")
      # ToDo: Précise l'exception
      except:
          pass
      
      print(time.strftime("%Y-%m-%d %H:%M:%S",
                          time.localtime(time.time())),
            "Going back to the graphical interface")

import crappy
import tkinter as tk 
import tomllib
import os
from pathlib import Path
import sys
import time
import ast

def open_file(path):
    with open(path, "rb") as f:
        data = tomllib.load(f)

    return data



if __name__ == '__main__':

  print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),"Launching lancement_essai.py")

  BASE_DIR = Path(os.environ.get('BASE_DIR'))
  if not BASE_DIR:
      raise EnvironmentError("The variable BASE_DIR was not defined")
  
  print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),"Launching the test")

  path_set = BASE_DIR / ".parameters/default_set_parameters.toml"

  try :
    donnees = open_file(path_set)

    speed = float(donnees['data']['speed'])
    l0 = float(donnees['data']['l0'])
    path_save_data = donnees['data']['path_save_data']
    load_cell = donnees['data']['load_cell']
    test_type = donnees['data']['test_type']
    gain = float(donnees['data']['gain'])
    prefix = donnees['data']['prefix']
    ports = ast.literal_eval(donnees['data']['ports'])
    ports_state = ast.literal_eval(donnees['data']['ports_state'])
    nb_steps = int(donnees['data']['nb_steps'])
    save_path = Path(path_save_data)

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),"Loading parameters from the .toml file")

  except:
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),'The .toml file to communicate experimental parameters was not found, the program stopped')
    try:
        sys.exit(1)
    except Exception as e:
        tk.messagebox.showerror("Error", f"The program could not close ", f"Error: {str(e)}",)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),f"The program could not close :\n{str(e)}")

  
  

  if test_type == "Monotonic Uniaxial Tensile Test":

    force_max = "F(N)>" + load_cell.replace('N', '')

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),"Starting the monotonic uniaxial tensile test now \n")

    #Load cell
    load_cell = crappy.blocks.IOBlock(
      'PhidgetWheatstoneBridge',  # The name of the InOut object to drive.
      labels=['t(s)', 'F(N)'],  # The names of the labels to output.
      make_zero_delay=1,  # To offset the values acquired during the delay to the
      # rest of. Remove this parameter to avoid the offset.
      remote=True,  # True if connected to a wireless VINT Hub, False if
      # connected to a USB VINT Hub.
      channel=1,  # Channel of the Wheatstone Bridge.
      gain=gain,  # Gain of the load cell.
      data_rate=10,
      hardware_gain=128,
    )

    #Motor
    mot = crappy.blocks.Machine(
      [{'type': 'Phidget4AStepper',  # The name of the Actuator to drive.
        'mode': 'speed',  # Driving in speed mode, not in position mode.
        'speed_label': 'speed',  # The label carrying the speed readout.
        'position_label': 'x(mm)',  # The label carrying the position readout.
        'steps_per_mm': nb_steps,  # Number of steps necessary to move by 1 mm.
        'current_limit': 3,  # Maximum current the driver is allowed to deliver
        # to the motor, in A.
        'max_acceleration': 20,  # Maximum acceleration the motor is allowed to
        # reach in mm/s².
        'remote': True,  # True if connected to a wireless VINT Hub, False if
        # connected to a USB VINT Hub.
        'switch_ports': ports,  # Port numbers of the VINT Hub where the
        # switches are connected.
        'switch_states': ports_state,
        'absolute_mode': True,
        'reference_pos': l0,
        'save_last_pos': True,
        'save_pos_folder': BASE_DIR /".parameters",
        }])

    #Generator
    gen = crappy.blocks.Generator([{'type':'Constant','condition':force_max,'value':speed}],freq=100)

    #Stop button
    stop = crappy.blocks.StopButton(
        # No specific argument to give for this Block
    )

    #Enregistrement et réunion des données
    effort = prefix + 'effort.csv'
    position = prefix + 'position.csv'
    data_t = prefix + 'data.csv'
    record_f = crappy.blocks.Recorder(save_path / effort, labels=['t(s)', 'F(N)'])
    record_pos = crappy.blocks.Recorder(save_path / position, labels=['x(mm)'])
    multiplex = crappy.blocks.Multiplexer()
    rec = crappy.blocks.Recorder(save_path / data_t, labels=['t(s)','F(N)','x(mm)'])



    # Graphers
    graph_depl = crappy.blocks.Grapher(('t(s)', 'x(mm)'))
    graph_force= crappy.blocks.Grapher(('t(s)', 'F(N)'))
    graph_def = crappy.blocks.Grapher(('x(mm)', 'F(N)'))



    # Links
      #pour les consignes
    crappy.link(gen, mot) #besoin de consigne
    crappy.link(load_cell, gen) #besoin de savoir la force pour déterminer la consigne
      #réunion de t(s), F(N) et x(mm) dans multiplex puis dans les records
    crappy.link(load_cell, multiplex)
    crappy.link(mot, multiplex)
    crappy.link(multiplex,rec)
    crappy.link(multiplex,record_f)
    crappy.link(multiplex,record_pos)
      #pour les graphes
    crappy.link(load_cell, graph_depl)
    crappy.link(mot, graph_depl)
    crappy.link(load_cell, graph_force)
    crappy.link(load_cell, graph_def)
    crappy.link(mot, graph_def)


    crappy.start()

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),'Test done, closing now')

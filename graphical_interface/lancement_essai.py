# coding: utf-8


import crappy
import tkinter as tk 
import tomllib
import os
from pathlib import Path
import sys 
import time
import ast
import re

if __name__ == '__main__':
      
      """Prints the defined messages in the terminal with the timestamps"""
      def afficher_message(message):
                  print(time.strftime("%Y-%m-%d %H:%M:%S", 
                                      time.localtime(time.time())), message)

      afficher_message("Launching lancement_essai.py")

      """BASE_DIR is a constant obtained through the bash file, showing the path towards this file, 
      necessary for a correct execution"""
      BASE_DIR = Path(os.environ.get('BASE_DIR'))
      if not BASE_DIR:
            raise EnvironmentError("The variable BASE_DIR was not defined")
      """Path to the parameters set"""
      path_set = BASE_DIR / ".parameters/default_set_parameters.toml"

      afficher_message("Launching the test")

      """When you gather all the necessary data that was split within 
      interface_grapgique.py, you can reunite the ports and their state"""
      def gather_ports_list(port1, port2, port1state, port2state):
            ports, ports_state = [], []
            
            for port in [port1, port2]:
                  try:
                        a = int(port)
                        ports += [a]
                  except ValueError:
                        pass
            
            for portstate in [port1state, port2state]:
                  if portstate!="":
                        try:
                              a = portstate == "True"
                              ports_state+=[a]
                        except ValueError:
                              pass
                        
            
                   
            return [ports, ports_state]
      
      """Gathering all data from the parameters set, and if it fails, the program stops,
      because these data are necessary"""
      try:
            with open(path_set, "rb") as f:
                  donnees = tomllib.load(f)

            speed = float(donnees['data']['speed'])
            l0 = float(donnees['data']['l0'])
            path_save_data = donnees['data']['path_save_data']
            load_cell_type = donnees['data']['load_cell']
            test_type = donnees['data']['test_type']
            gain = float(donnees['data']['gain'])
            prefix = donnees['data']['prefix']
            port_1 = donnees['data']['port_1']
            port_1_state = donnees['data']['port_1_state']
            port_2 = donnees['data']['port_2']
            port_2_state = donnees['data']['port_2_state']
            nb_steps = int(donnees['data']['nb_steps'])

            save_path = Path(path_save_data)
            ports, ports_state = gather_ports_list(port_1, port_2, port_1_state, port_2_state)
            afficher_message("Loading parameters from the .toml file")
            afficher_message(ports)
            afficher_message(ports_state)

            print(ports)
            print(ports_state)


      except FileNotFoundError as e:
            afficher_message('The .toml file to communicate experimental'
                             ' parameters was not found, the program stopped')

            sys.exit(1)


      """Create an if/elif loop for each kind of test """
      if test_type == "Monotonic Uniaxial Tensile Test":

            afficher_message("Starting the monotonic uniaxial tensile test now \n")

            # Load cell
            load_cell = crappy.blocks.IOBlock(
            'PhidgetWheatstoneBridge',  # The name of the InOut object to drive.
            labels=['t(s)', 'F(N)'],  # The names of the labels to output.
            make_zero_delay=1,  # To offset the values acquired during the delay to
            # the rest of. Remove this parameter to avoid the offset.
            remote=True,  # True if connected to a wireless VINT Hub, False if
            # connected to a USB VINT Hub.
            channel=1,  # Channel of the Wheatstone Bridge.
            gain=gain,  # Gain of the load cell.
            data_rate=10,
            hardware_gain=128,
      )

            # Motor
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
            'save_pos_folder': BASE_DIR / ".parameters",
            }])

            # Generator
            cond = f"F(N)>{re.fullmatch(r'(\d+)N', load_cell_type).groups()[0]}"
            gen = crappy.blocks.Generator([{'type': 'Constant', 'condition': cond,
                                                'value': speed}], freq=100)

            # Stop button
            stop = crappy.blocks.StopButton()

            # Gathering and saving data
            effort = prefix + 'effort.csv'
            position = prefix + 'position.csv'
            data_t = prefix + 'data.csv'
            record_f = crappy.blocks.Recorder(save_path / effort,
                                                labels=['t(s)', 'F(N)'])
            record_pos = crappy.blocks.Recorder(save_path / position, labels=['x(mm)'])
            multiplex = crappy.blocks.Multiplexer()
            rec = crappy.blocks.Recorder(save_path / data_t,
                                          labels=['t(s)', 'F(N)', 'x(mm)'])

            # Graphers
            graph_depl = crappy.blocks.Grapher(('t(s)', 'x(mm)'))
            graph_force = crappy.blocks.Grapher(('t(s)', 'F(N)'))
            graph_def = crappy.blocks.Grapher(('x(mm)', 'F(N)'))

            # Links
            #  for the setpoint
            crappy.link(gen, mot)  # the motor needs the setpoint
            crappy.link(load_cell, gen)  # the generator needs the force value to determine 
            # the setpoint
            # gathering t(s), F(N) et x(mm) in multiplex and then in the records
            crappy.link(load_cell, multiplex)
            crappy.link(mot, multiplex)
            crappy.link(multiplex, rec)
            crappy.link(multiplex, record_f)
            crappy.link(multiplex, record_pos)
            # for the graphs
            crappy.link(load_cell, graph_depl)
            crappy.link(mot, graph_depl)
            crappy.link(load_cell, graph_force)
            crappy.link(load_cell, graph_def)
            crappy.link(mot, graph_def)

            crappy.start()

            afficher_message('Test done, closing now')

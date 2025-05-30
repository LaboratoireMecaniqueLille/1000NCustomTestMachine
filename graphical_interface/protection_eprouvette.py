"""
This example can be used to protect your sample during the tightening of the
sample to the machine.

In this example, the motor is driven in function of the level of stress in the
sample. If the force measured by the load cell is greater (resp. lesser) than a
threshold value (10 N), the motor will move at speed = 0.5 mm/s in the
appropriate direction so that the force stays lesser (resp. greater) than the
threshold value.

This Machine Block drives the motor in speed here.
The InOut Block measured the force applied, and also outputs it to a Grapher
Block and to a Recorder Block.

You can hit CTRL+C to stop it, but it is not a clean way to stop Crappy.
"""

import crappy
import tkinter.filedialog as tkFileDialog  # ToDo: inutilisé
import tomllib
import os

def open_file(path):
    with open(path, "rb") as f:
        data = tomllib.load(f)

    return data


if __name__ == '__main__':
  BASE_DIR = os.environ.get('BASE_DIR')
  if not BASE_DIR:
      raise EnvironmentError("The variable BASE_DIR was not defined")

  path_set = BASE_DIR + "/.default_set_parameters.toml"

  try :
    donnees = open_file(path_set)
    gain = float(donnees['data']['gain'])
    print(gain)
  except:
    gain = 3.26496001e+05 

  


  speed = 2  # Speed in mm/s
  thresh = 10  # Threshold force in N

  # This IOBlock gets the current force measured by a 1000N load cell with a
  # Phidget Wheatstone Bridge, and sends it to downstream Blocks.
  load_cell = crappy.blocks.IOBlock(
    'PhidgetWheatstoneBridge',  # The name of the InOut object to drive.
    labels=['t(s)', 'F(N)'],  # The names of the labels to output.
    make_zero_delay=1,  # To offset the values acquired during the delay to the
    # rest of. Remove this parameter to avoid the offset.
    remote=True,  # True if connected to a wireless VINT Hub, False if
    # connected to a USB VINT Hub.
    channel=1,  # Channel of the Wheatstone Bridge.
    gain=gain,  # Gain of the load cell.
  )

  # This Machine Block drives a Phidget4AStepper in speed.
  mot = crappy.blocks.Machine(
    [{'type': 'Phidget4AStepper',  # The name of the Actuator to drive.
      'mode': 'speed',  # Driving in speed mode, not in position mode.
      'speed_label': 'speed',  # The label carrying the speed readout.
      'position_label': 'pos',  # The label carrying the position readout.
      'steps_per_mm': 2500,  # Number of steps necessary to move by 1 mm.
      'current_limit': 3,  # Maximum current the driver is allowed to deliver
      # to the motor, in A.
      'max_acceleration': 20,  # Maximum acceleration the motor is allowed to
      # reach in mm/s².
      'remote': True,  # True if connected to a wireless VINT Hub, False if
      # connected to a USB VINT Hub.
      'switch_ports': (),  # Port numbers of the VINT Hub where the
      # switches are connected. Désactivés pour pouvoir se décaler des switchs
      }])

  # This Generator generates the command for driving the Machine Block.
  # The path drive the Machine in function of the force measured by the load
  # cell.
  gen = crappy.blocks.Generator([{'type': 'Conditional',
                                  'condition1': f'F(N)>{thresh}',
                                  'condition2': f'F(N)<-{thresh}',
                                  'value0': 0,
                                  'value1': -speed,
                                  'value2': speed}])

  # This Block allows the user to properly exit the script
  stop = crappy.blocks.StopButton(
      # No specific argument to give for this Block
  )

  # This Grapher displays the force as measured by the LoadCell Block.
  graph_force = crappy.blocks.Grapher(('t(s)', 'F(N)'))

  # Linking the Block so that the information is correctly sent and received.
  crappy.link(gen, mot)
  crappy.link(load_cell, gen)
  crappy.link(load_cell, graph_force)

  crappy.start()

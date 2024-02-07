"""
This example demonstrates the use of the LoadCell Block.

In this example, the level of stress is controlled by a Generator Block that
sends command to the Machine Block. This Machine Block drives the motor in
speed here. The InOut Block measured the force applied, and also outputs it to
a Grapher Block and to a Recorder Block.

You can hit CTRL+C to stop it, but it is not a clean way to stop Crappy.
"""

import crappy

if __name__ == '__main__':

  gain = 3.26496001e+05
  save_folder = '/home/'
  speed = 1

  # This IOBlock gets the current force measured by a 1000N load cell with a
  # Phidget Wheatstone Bridge, and sends it to downstream Blocks.
  load_cell = crappy.blocks.IOBlock(
    'PhidgetWheatstoneBridge',  # The name of the InOut object to drive.
    labels=['t(s)', 'F(N)'],  # The names of the labels to output.
    make_zero_delay=1,  # To offset the values acquired during the delay to the
    # rest of
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
      'switch_ports': (1, 2),  # Port numbers of the VINT Hub where the
      # switches are connected.
      }])

  # This Generator generates the command for driving the Machine Block.
  # The different paths drive the Machine to the desired force.
  gen = crappy.blocks.Generator([{'type': 'Constant',
                                  'value': speed,
                                  'condition': 'F(N)>100'},
                                 {'type': 'Constant',
                                  'value': -speed,
                                  'condition': 'F(N)<10'},
                                 {'type': 'Constant',
                                  'value': speed,
                                  'condition': 'FN)>300'},
                                 {'type': 'Constant',
                                  'value': -speed,
                                  'condition': 'F(N)<10'}
                                 ])

  # This Grapher displays the force as measured by the LoadCell Block.
  graph_force = crappy.blocks.Grapher(('t(s)', 'F(N)'))

  # This Recorder saves the real-time emulated position and speed of the
  # stepper motor.
  rec_pos = crappy.blocks.Recorder(file_name=f'{save_folder}X.csv')

  # This Recorder saves the force as measured by the LoadCell Block.
  rec_force = crappy.blocks.Recorder(file_name=f'{save_folder}F.csv')

  # Linking the Block so that the information is correctly sent and received.
  crappy.link(gen, mot)
  crappy.link(load_cell, gen)
  crappy.link(load_cell, graph_force)
  crappy.link(load_cell, rec_force)
  crappy.link(mot, rec_pos)

  crappy.start()

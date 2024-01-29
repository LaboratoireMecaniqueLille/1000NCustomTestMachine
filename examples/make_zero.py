"""
This example can be used to set the extremity of the tensile bench as a
reference position in order to drive the motor later in absolute mode.
Moreover, it can be used to acquire the evolution the stress due to the screw
rotation in function of the position of the motor. This same stress could then
be offset from the real stress measured during the tensile test.

In this example, the motor will hit twice the extremity of the bench,
identified by an increase of the stress. Then, the motor will travel all along
the bench and record the force from the screw rotation at the same time.

You can hit CTRL+C to stop it, but it is not a clean way to stop Crappy.
"""

import crappy

if __name__ == '__main__':

  gain = 3.26496001e+05
  save_folder = '/home/essais/Desktop/margotin/'

  # This IOBlock gets the current force measured by a 1000N load cell with a
  # Phidget Wheatstone Bridge, and sends it to downstream Blocks.
  load_cell = crappy.blocks.IOBlock(
    'PhidgetWheatstoneBridge',  # The name of the InOut object to drive.
    labels=['t(s)', 'F(N)'],  # The names of the labels to output.
    remote=True,  # True if connected to wi-fi to the machine, False if wired.
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
      'remote': True,  # True if connected to wi-fi to the machine,
      # False if wired.
      'switch_ports': (5, 6),  # Port numbers of the VINT Hub where the
      # switches are connected.
      }])

  # This Generator generates the command for driving the Machine Block.
  # The different paths drive the Machine to the desired force.
  gen = crappy.blocks.Generator([{'type': 'Constant',
                                  'value': -0.5,
                                  'condition': 'F(N)<-70'},
                                 {'type': 'Constant',
                                  'value': 0.5,
                                  'condition': 'delay=2'},
                                 {'type': 'Constant',
                                  'value': -0.1,
                                  'condition': 'F(N)<-70'},
                                 {'type': 'Constant',
                                  'value': 2,
                                  'condition': 'delay=80'},
                                 {'type': 'Constant',
                                  'value': 0,
                                  'condition': 'delay=1'}
                                 ])

  # This Grapher displays the force as measured by the LoadCell Block.
  graph_force = crappy.blocks.Grapher(('t(s)', 'F(N)'))

  # This Recorder saves the real-time emulated position and speed of the
  # stepper motor.
  rec_pos = crappy.blocks.Recorder(file_name=f'{save_folder}X_screw.csv')

  # This Recorder saves the force as measured by the LoadCell Block.
  rec_force = crappy.blocks.Recorder(file_name=f'{save_folder}F_screw.csv')

  # Linking the Block so that the information is correctly sent and received.
  crappy.link(gen, mot)
  crappy.link(load_cell, gen)
  crappy.link(load_cell, graph_force)
  crappy.link(load_cell, rec_force)
  crappy.link(mot, rec_pos)

  crappy.start()

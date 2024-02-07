"""
This example demonstrates the use of the Machine Block in speed mode.

You can hit CTRL+C to stop it, but it is not a clean way to stop Crappy.
"""

import crappy

if __name__ == '__main__':

  save_folder = '/home/essais/Desktop/margotin/'
  speed = 1  # Speed in mm/s

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

  # This Generator generates the speed command for driving the Machine Block.
  gen = crappy.blocks.Generator([{'type': 'Constant',
                                  'value': speed,
                                  'condition': 'delay=10'},
                                 {'type': 'Constant',
                                  'value': 0,
                                  'condition': 'delay=2'},
                                 {'type': 'Constant',
                                  'value': -speed,
                                  'condition': 'delay=10'}
                                 ])

  # This Grapher displays the real-time emulated position of the motor.
  graph_pos = crappy.blocks.Grapher(('t(s)', 'pos'))

  # Linking the Block so that the information is correctly sent and received.
  crappy.link(gen, mot)
  crappy.link(mot, graph_pos)

  crappy.start()

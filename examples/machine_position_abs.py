"""
This example demonstrates the use of the Machine Block in absolute position
mode. It means that if the target position is 10 mm, the motor will move from
his actual position to the position 10 mm, calculated from a reference
position.
Here, the reference position is 20 mm (the position of the motor at
the beginning of the test), and the target position is 30 mm. The motor will
then move from 10 mm. Then, the target position is again 30 mm, but the motor
is already at this position, so it will not move. Finally, the target position
is 20 mm so the motor will move from -10 mm.
The position setpoint is generated by a Generator Block. Along with the
position, a speed setpoint is also generated and sent to the Machine Block.
This speed value indicates the maximum speed at which the Actuator can move for
reaching the desired position. The last position will be saved in a .npy file.

You can hit CTRL+C to stop it, but it is not a clean way to stop Crappy.
"""

import crappy

if __name__ == '__main__':

  save_folder = '/home/essais/Desktop/margotin/'

  # This Machine Block drives a Phidget4AStepper in relative position.
  mot = crappy.blocks.Machine(
    [{'type': 'Phidget4AStepper',  # The name of the Actuator to drive.
      'mode': 'pos',  # Driving in position mode, not in speed mode.
      'cmd_label': 'pos_cmd',  # The label carrying the position setpoint.
      'speed_cmd_label': 'speed_cmd',  # The label carrying the maximum
      # speed for moving to the given position setpoint.
      'speed_label': 'speed',  # The label carrying the speed readout.
      'position_label': 'pos',  # The label carrying the position readout.
      'steps_per_mm': 2500,  # Number of steps necessary to move by 1 mm.
      'current_limit': 3,  # Maximum current the driver is allowed to deliver
      # to the motor, in A.
      'max_acceleration': 20,  # Maximum acceleration the motor is allowed to
      # reach in mm/s².
      'remote': True,  # True if connected to wi-fi to the machine,
      # False if wired.
      'absolute_mode': True,  # If True, get the position in reference of
      # the value given.
      'reference_pos': 20,  # Reference position example.
      'switch_ports': (5, 6),  # Port numbers of the VINT Hub where the
      # switches are connected.
      'save_last_pos': True,  # If True, save the last position acquired in a
      # .npy file.
      'save_pos_folder': save_folder,  # Path to the folder where to save the
      # last position
      }])

  # This Generator generates the position command for driving the Machine
  # Block.
  gen_pos = crappy.blocks.Generator([{'type': 'Constant',
                                      'value': 30,
                                      'condition': 'delay=10'},
                                     {'type': 'Constant',
                                      'value': 30,
                                      'condition': 'delay=2'},
                                     {'type': 'Constant',
                                      'value': 20,
                                      'condition': 'delay=10'}],
                                    cmd_label='pos_cmd')

  gen_speed = crappy.blocks.Generator([{'type': 'Constant',
                                        'value': 1,
                                        'condition': 'delay=22'}],
                                      cmd_label='speed_cmd')

  # This Grapher displays the real-time emulated position of the motor.
  graph_pos = crappy.blocks.Grapher(('t(s)', 'pos'))

  # Linking the Block so that the information is correctly sent and received.
  crappy.link(gen_pos, mot)
  crappy.link(gen_speed, mot)
  crappy.link(mot, graph_pos)

  crappy.start()

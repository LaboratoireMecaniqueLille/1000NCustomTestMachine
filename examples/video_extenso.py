"""
This example demonstrates the use of the VideoExtenso Block.

This Block computes the strain on acquired images by tracking the displacement
of several spots. It outputs the computed strain as well as the position and
displacement of the spots.

In this example, the level of strain is controlled by a Generator Block that
sends command to the Machine Block. This Machine Block drives the motor in
speed here. The VideoExtenso Block calculates the strain on the images, and
outputs it to a Grapher Block for display and to a Recorder Block for save.
The InOut Block measured the force applied, and also outputs it to a Grapher
Block and to a Recorder Block.

After starting this script, you have to select the spots to track in the
configuration window by left-clicking and dragging. Then, close the
configuration window and watch the strain be calculated in real time.
You can hit CTRL+C to stop it, but it is not a clean way to stop Crappy.
"""

import crappy

if __name__ == '__main__':

  gain = 3.26496001e+05
  save_folder = '/home/essais/Desktop/margotin/'
  speed = 1

  # This IOBlock gets the current force measured by a 1000N load cell with a
  # Phidget Wheatstone Bridge, and sends it to downstream Blocks.
  load_cell = crappy.blocks.IOBlock(
    'PhidgetWheatstoneBridge',  # The name of the InOut object to drive.
    labels=['t(s)', 'F(N)'],  # The names of the labels to output.
    remote=True,  # True if connected to wi-fi to the machine, False if wired.
    channel=1,  # Channel of the Wheatstone Bridge.
    gain=gain,  # Gain of the load cell.
    auto_offset=True  # True to offset the first value acquired to the rest of
    # the values acquired.
  )

  # This Machine Block drives a Phidget4AStepper in speed.
  mot = crappy.blocks.Machine(
    [{'type': 'Phidget4AStepper',  # The name of the Actuator to drive.
      'mode': 'speed',  # Driving in speed mode, not is position mode.
      'speed_label': 'speed',  # The label carrying the speed readout.
      'position_label': 'pos',  # The label carrying the position readout.
      'steps_per_mm': 2500,  # Number of steps necessary to move by 1 mm.
      'current_limit': 3,  # Maximum current the driver is allowed to deliver
      # to the motor, in A.
      'max_acceleration': 20,  # Maximum acceleration the motor is allowed to
      # reach in mm/s².
      'remote': True,  # True if connected to wi-fi to the machine,
      # False if wired.
      'absolute_mode': (False, 0),  # If True, get the position in reference of
      # the value given.
      'switch_ports': (5, 6),  # Port numbers of the VINT Hub where the
      # switches are connected.
      'save_last': (False, save_folder)  # If True, save the last position
      # acquired in a file .npy in the folder given.
      }])

  # This Generator generates the command for driving the Machine Block.
  # The different paths drive the Machine to the desired strain.
  gen = crappy.blocks.Generator([{'type': 'Constant',
                                  'value': speed,
                                  'condition': 'Eyy(%)>20'},
                                 {'type': 'Constant',
                                  'value': -speed,
                                  'condition': 'Eyy(%)<10'},
                                 {'type': 'Constant',
                                  'value': speed,
                                  'condition': 'Eyy(%)>40'},
                                 {'type': 'Constant',
                                  'value': -speed,
                                  'condition': 'Eyy(%)<10'}
                                 ])

  # This VideoExtenso Block calculates the strain of the image by tracking the
  # displacement of spots on the acquired images.
  # This Block is actually also the one that generates the fake strain on the
  # image, but that wouldn't be the case in real life.
  # It takes the target strain as an input, and outputs both the computed
  # strain and the positions of the tracked spots.
  ve = crappy.blocks.VideoExtenso(
      'CameraGstreamer',  # The name of Camera to open.
      device='/dev/video2',  # The camera port.
      config=True,  # Displaying the configuration window before starting,
      # config=False is not implemented yet.
      display_images=True,  # Display acquired images during the test.
      freq=50,  # Frequency
      save_images=True,  # True to save the images, False to not.
      save_folder=save_folder,  # Path to the folder where to save the images.
      # The labels for sending the calculated strain to downstream Blocks
      labels=('t(s)', 'meta', 'Coord(px)', 'Eyy(%)', 'Exx(%)'),
      white_spots=False,  # True if the color of the spots on the sample
      # are white, False if not.
      num_spots=4,  # Number of spots on the sample (0,1,2,3,4).
      )

  # This Grapher displays the extension as computed by the VideoExtenso Block.
  graph_def_eyy = crappy.blocks.Grapher(('t(s)', 'Eyy(%)'))

  # This Grapher displays the force as measured by the LoadCell Block.
  graph_force = crappy.blocks.Grapher(('t(s)', 'F(N)'))

  # This Recorder saves the extension as computed by the VideoExtenso Block.
  rec_def = crappy.blocks.Recorder(file_name=f'{save_folder}Def.csv')

  # This Recorder saves the real-time emulated position and speed of the
  # stepper motor.
  rec_pos = crappy.blocks.Recorder(file_name=f'{save_folder}X.csv')

  # This Recorder saves the force as measured by the LoadCell Block.
  rec_force = crappy.blocks.Recorder(file_name=f'{save_folder}F.csv')

  # Linking the Block so that the information is correctly sent and received.
  crappy.link(gen, mot)
  crappy.link(ve, gen)
  crappy.link(ve, graph_def_eyy)
  crappy.link(load_cell, graph_force)
  crappy.link(load_cell, rec_force)
  crappy.link(mot, rec_pos)
  crappy.link(ve, rec_def)

  crappy.start()

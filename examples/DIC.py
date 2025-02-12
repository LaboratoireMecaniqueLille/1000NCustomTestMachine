"""
This example demonstrates the use of the DICVE Block.

This Block computes the strain on acquired images by tracking several patches
using digital image correlation techniques. It outputs the computed strain as
well as the position and displacement of the patches.

In this example, the level of strain is controlled by a Generator Block that
sends command to the Machine Block. This Machine Block drives the motor in
speed here. The DICVE Block calculates the strain on the images, and
outputs it to a Grapher Block for display and to a Recorder Block for save.
The InOut Block measured the force applied, and also outputs it to a Grapher
Block and to a Recorder Block.

After starting this script, you have to select the patches to track in the
configuration window by left-clicking and dragging. Then, close the
configuration window and watch the strain be calculated in real time.
You can hit CTRL+C to stop it, but it is not a clean way to stop Crappy.
"""

import crappy

if __name__ == '__main__':

  gain = 3.26496001e+05
  save_folder = './'
  speed = 1

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
      'switch_ports': (1, 2),  # Port numbers of the VINT Hub where the
      # switches are connected.
      }])

  # This Generator generates the command for driving the Machine Block.
  # The different paths drive the Machine to the desired strain.
  gen = crappy.blocks.Generator([{'type': 'Constant',
                                  'value': speed,
                                  'condition': 'Eyy(%)>0.2'},
                                 {'type': 'Constant',
                                  'value': -speed,
                                  'condition': 'Eyy(%)<0.1'},
                                 {'type': 'Constant',
                                  'value': speed,
                                  'condition': 'Eyy(%)>0.4'},
                                 {'type': 'Constant',
                                  'value': -speed,
                                  'condition': 'Eyy(%)<0.1'}
                                 ])

  # This DICVE Block calculates the strain of the image by tracking the
  # displacement of the patches
  dic_ve = crappy.blocks.DICVE(
      'CameraGstreamer',  # The name of Camera to open.
      device='/dev/video2',  # The camera port.
      config=True,  # Displaying the configuration window before starting,
      # mandatory if the patches to track ar not given as arguments
      display_images=True,  # The displayer window will allow to follow the
      # patches on the speckle image
      freq=50,  # Frequency.
      save_images=True,  # True to save the images, False to not.
      save_folder=save_folder,  # Path to the folder where to save the images.
      patches=None,  # The patches to track are not provided here, so they must
      # be selected in the configuration window
      # The labels for sending the calculated strain to downstream Blocks
      labels=('t(s)', 'meta', 'Coord(px)', 'Eyy(%)', 'Exx(%)', 'Disp(px)'),
      method='Disflow',  # The default image correlation method
      # Sticking to default for the other arguments
  )

  # This Block allows the user to properly exit the script
  stop = crappy.blocks.StopButton(
      # No specific argument to give for this Block
  )

  # This Grapher displays the extension as computed by the DICVE Block.
  graph_def_eyy = crappy.blocks.Grapher(('t(s)', 'Eyy(%)'))

  # This Grapher displays the force as measured by the LoadCell Block.
  graph_force = crappy.blocks.Grapher(('t(s)', 'F(N)'))

  # This Recorder saves the extension as computed by the DICVE Block.
  rec_def = crappy.blocks.Recorder(file_name=f'{save_folder}Def.csv')

  # This Recorder saves the real-time emulated position and speed of the
  # stepper motor.
  rec_pos = crappy.blocks.Recorder(file_name=f'{save_folder}X.csv')

  # This Recorder saves the force as measured by the LoadCell Block.
  rec_force = crappy.blocks.Recorder(file_name=f'{save_folder}F.csv')

  # Linking the Block so that the information is correctly sent and received.
  crappy.link(gen, mot)
  crappy.link(dic_ve, gen)
  crappy.link(dic_ve, graph_def_eyy)
  crappy.link(load_cell, graph_force)
  crappy.link(load_cell, rec_force)
  crappy.link(mot, rec_pos)
  crappy.link(dic_ve, rec_def)

  crappy.start()

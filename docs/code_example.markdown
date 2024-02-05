---
layout: default
title: Code examples
---

[Home page](index.markdown)

## Crappy blocks

In Crappy, even the most complex setups can be described with only two 
elements: the Blocks and the Links. The Blocks are responsible for managing 
data. There are many different types of Blocks, that all have a unique 
function. Some will acquire data, others transform it, or use it to drive 
hardware, etc. As the Blocks perform very specific tasks, a test script usually
contains several Blocks (there is no upper limit). Blocks either take data as 
an input, or they output data, or both. (<I>Crappy documentation </I>)

More information about how Crappy works 
<a href="https://crappy.readthedocs.io/en/stable/tutorials/getting_started.html">here</a>.

### Load cell block

This IOBlock gets the current force measured by a 1000N load cell with a
Phidget Wheatstone Bridge, and sends it to downstream Blocks.

```python
import crappy

gain = 3.26496001e+05  # Gain calculated from the load cell calibration

load_cell = crappy.blocks.IOBlock(
  'PhidgetWheatstoneBridge',  # The name of the InOut object to drive.
  labels=['t(s)', 'F(N)'],  # The names of the labels to output.
  make_zero_delay=1,  # To offset the values acquired during the delay to the
  # rest of
  remote=True,  # True if connected to a wireless VINT Hub, False if 
  # connected to a USB VINT Hub
  channel=1,  # Channel of the Wheatstone Bridge.
  gain=gain,  # Gain of the load cell.
  )
```

### Motor block (speed mode)

This Machine Block drives a Phidget4AStepper in speed.

```python
import crappy

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
    # connected to a USB VINT Hub
    'switch_ports': (5, 6),  # Port numbers of the VINT Hub where the
    # switches are connected.
    }])
```

### Motor block (position mode)

#### Relative mode

This example demonstrates the use of the Machine Block in relative position
mode. It means that if the target position is 10 mm, the motor will move from
10 mm from his actual position.

This Machine Block drives a Phidget4AStepper to a relative position.

```python
import crappy

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
    'remote': True,  # True if connected to a wireless VINT Hub, False if 
    # connected to a USB VINT Hub
    'switch_ports': (5, 6),  # Port numbers of the VINT Hub where the
    # switches are connected.
    }])
```

#### Absolute mode

This example demonstrates the use of the Machine Block in absolute position
mode. It means that if the target position is 10 mm, the motor will move from
his actual position to the position 10 mm, calculated from a reference 
position.

This Machine Block drives a Phidget4AStepper to an absolute position.

```python
import crappy

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
    'remote': True,  # True if connected to a wireless VINT Hub, False if 
    # connected to a USB VINT Hub
    'absolute_mode': True,  # If True, get the position in reference of
    # the value given.
    'reference_pos': 10,
    'switch_ports': (5, 6),  # Port numbers of the VINT Hub where the
    # switches are connected.
    'save_last_pos': True,  # If True, save the last position acquired in a
    # .npy file.
    'save_pos_folder': save_folder,  # Path to the folder where to save the
    # last position
    }])
```

### Video extenso Block

This VideoExtenso Block calculates the strain of the image by tracking the
displacement of spots on the acquired images.

```python
import crappy

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
```

## Code example

The Crappy codes here consist of linking the blocks from the previous section
to perform tests.   

The codes are available on 
[GitHub](https://github.com/LaboratoireMecaniqueLille/1000NCustomTestMachine).

They can be modified, particularly the Condition key for the Generator Path to 
drive the test the way you want to.
More information  about Generator Path 
<a href="https://crappy.readthedocs.io/en/stable/crappy_docs/blocks.html#generator-paths">here</a>.

### machine_speed.py

This example demonstrates the use of the Machine Block in speed mode.
The speed of the motor (mm/s) can be adjusted by the user by changing the 
parameter speed.

The evolution of the relative position during the test is plotted with a 
Grapher Block.

### machine_position_rel.py

This example demonstrates the use of the Machine Block in relative position
mode. It means that if the target position is 10 mm, the motor will move from
10 mm from his actual position. The position setpoint is generated by a
Generator Block. Along with the position, a speed setpoint is also generated
and sent to the Machine Block. This speed value indicates the maximum speed at
 which the Actuator can move for reaching the desired position.

The evolution of position during the test is plotted with a Grapher Block.

### machine_position_abs.py

This example demonstrates the use of the Machine Block in absolute position
mode. It means that if the target position is 10 mm, the motor will move from
his actual position to the position 10 mm, calculated from a reference
position. 

The position setpoint is generated by a Generator Block. Along with
the position, a speed setpoint is also generated and sent to the Machine Block.
This speed value indicates the maximum speed at which the Actuator can move for
 reaching the desired position. The last position will be saved in a .npy file.

The evolution of position during the test is plotted with a Grapher Block. 

### make_zero.py

This example can be used to set the extremity of the tensile bench as a
reference position in order to drive the motor later in absolute mode.
Moreover, it can be used to acquire the evolution the stress due to the screw
rotation in function of the position of the motor. This same stress could then
be offset from the real stress measured during the tensile test.

In this example, the motor will hit twice the extremity of the bench,
identified by an increase of the stress. Then, the motor will travel all along
the bench and record the force from the screw rotation at the same time.

### sample_protection.py

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

### load_cell.py

In this example, the motor is driven in function of the level of stress in the
sample. This Machine Block drives the motor in speed here.
The InOut Block measured the force applied, and also outputs it to a Grapher
Block and to a Recorder Block.

The evolution of force during the test is plotted with a Grapher Block.

### video_extenso.py

This example demonstrates the use of the VideoExtenso Block.
This Block computes the strain on acquired images by tracking the displacement
of several spots. It outputs the computed strain as well as the position and
displacement of the spots.

In this example, the level of strain accepted is controlled by a Generator 
Block that sends command to the Machine Block. This Machine Block drives the 
motor in speed here. The VideoExtenso Block calculates the strain on the 
images, and outputs it to a Grapher Block for display and to a Recorder Block
for save.
The InOut Block measured the force applied, and also outputs it to a Grapher
Block and to a Recorder Block.

After starting this script, the user have to select the spots to track in the
configuration window by left-clicking and dragging. Then, close the
configuration window and watch the strain be calculated in real time.

### back_switch.py

This example demonstrates how to move back the motor manually after hitting a 
switch. It also shows the use of Crappy Blocks outside a Crappy loop.

In this example, a Tkinter slider controlled by the user sends command to the
Actuator Block. The slider sends speed command to drive the motor here.
The user can only drive the motor in the opposite direction of the switch that
has been hit.

[Home page](index.markdown)

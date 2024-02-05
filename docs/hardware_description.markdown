---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
title: Hardware description
---

[Home page](index.markdown)

The 1000N Custom Test Machine is based on the Phidgets technology. This page 
describes the different Phidgets components of this machine.


## Phidgets

Phidgets are a range of modular sensors and actuators designed to simplify the 
interaction between computers and the physical world. Their operation is based 
on a plug-and-play concept, allowing users to easily connect sensors and 
actuators to their computer using Phidgets hardware.

### Wireless VINT Hub 

The main element of this test machine is the Phidgets wireless VINT HUB. It 
offers a convenient solution for utilizing Phidgets sensors and actuators in 
remote locations without a direct computer connection. It enables accessibility
through your local network via the Phidget Network Server. 

Each port on the hub is configurable to function in various modes, streamlining
the interaction with VINT devices, analog sensors, or logic-level circuits. 
Furthermore, each port includes dedicated power and ground pins, offering 
direct access to the Hub's 5V regulated power supply.

That way, the user only needs to connect to the Phidgets wireless VINT HUB by
wi-fi or ethernet to drive the machine composed of several Phidgets actuators
and sensors.

<p align="center">
<img src="./images/VINT_Phidgets.png" height="150" width="150" align="center" title="Phidgets Wireless VINT HUB">
</p>

More documentation about the Wireless VINT Hub can be found <a href="https://www.phidgets.com/?prodid=1143">here</a>. 

### 4A Stepper Phidget

The stepper motor used for 1000N Custom Test Machine is driven by the 4A 
Stepper Phidget.  

There is also two limit switches in this machine. When hit, the 4A Stepper 
Phidget stops the motor.

<p align="center">
<img src="./images/S4A_Phidgets.png" height="150" width="150" align="center" title="4A Stepper Phidget">
</p>

In the python module Crappy the 4A Stepper driver corresponds to a Machine 
Block for the Actuator: <B>Phidget4AStepper</B>.

More documentation about this driver can be found <a href="https://www.phidgets.com/?prodid=1278">here</a>.

### Wheatstone Bridge Phidget

The Wheatstone Bridge Phidget serves as a load cell interface, enhancing the 
signal received from a load cell and delivering a reliable, digital output. 
By applying calibration parameters (gain), it can accurately transform the raw
load cell output into precise force measurements.

<p align="center">
<img src="./images/WB_Phidgets.png" height="150" width="150" align="center" title="Wheatstone Bridge Phidget">
</p>

The load cell used for the 1000N Custom Test Machine an S-type load cell. It 
can measure with accuracy loads up to 100 kg which is about 1000 N. 

A load cell utilizes the principle of strain gauges, which are thin conductive 
wires attached to its surface. When a force is applied, the material undergoes
strain, causing a change in the electrical resistance of these strain gauges. 
This change in resistance is then precisely measured and converted into an 
electrical signal with here Wheatstone bridge, providing an accurate 
representation of the applied force.

Through calibration of the load cell, the relationship between the variation in
the cell's electrical output and the variation in the applied force has been 
calculated:
gain = 3.265e+05 N/V.

More documentation about the load cell can be found <a href="https://www.phidgets.com/?prodid=229">here</a>.

In the python module Crappy the Wheatstone bridge corresponds to an IOBlock for
the InOut: <B>PhidgetWheatstoneBridge</B>.

More documentation about the sensor can be found <a href="https://www.phidgets.com/?prodid=957">here</a>. 

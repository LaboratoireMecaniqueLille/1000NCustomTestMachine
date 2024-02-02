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

More documentation can be found <a href="https://www.phidgets.com/?prodid=1143">here</a>. 

### 4A Stepper Phidget

The stepper motor used for 1000N Custom Test Machine is driven by the 4A 
Stepper Phidget.  

There is also two limit switches in this machine. When hit, the 4A Stepper 
Phidget stops the motor.

<p align="center">
<img src="./images/S4A_Phidgets.png" height="150" width="150" align="center" title="4A Stepper Phidget">
</p>

More documentation can be found <a href="https://www.phidgets.com/?prodid=1278">here</a>.

### Wheatstone Bridge Phidget

The Wheatstone Bridge Phidget serves as a load cell interface, enhancing the 
signal received from a load cell and delivering a reliable, digital output. 
By applying calibration parameters (gain), it can accurately transform the raw
load cell output into precise force measurements.

<p align="center">
<img src="./images/WB_Phidgets.png" height="150" width="150" align="center" title="Wheatstone Bridge Phidget">
</p>

More documentation can be found <a href="https://www.phidgets.com/?prodid=957">here</a>. 

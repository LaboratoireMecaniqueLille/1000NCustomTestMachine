# 1000NCustomTestMachine
This repositary contains Python code for driving a 1000N test machine developed
at the LaMcube laboratory. 

## Presentation 

This machine is based on Phidgets hardware and the python module crappy to 
perform different tests as tensile test, flexion test, compression test and 
fracture test on different materials.

### Phidgets

Phidgets are a range of modular sensors and actuators designed to simplify the 
interaction between computers and the physical world. Their operation is based 
on a plug-and-play concept, allowing users to easily connect sensors and 
actuators to their computer using Phidgets hardware.


The main element of this test machine is the Phidgets wireless VHINT HUB. It is
a simple way to use Phidgets in locations away from a computer by making them 
available on your local network via the Phidget Network Server. That way, the 
user only needs to connect to the Phidgets wireless VHINT HUB by wi-fi or 
ethernet to drive the machine composed of several Phidgets actuators and 
sensors.

### Crappy

The test with this machine can be performed with Crappy. Crappy is a Python 
module that aims to provide easy-to-use and open-source tools for command and 
data acquisition on complex experimental setups. It is designed to let users 
drive most setups in less than 100 lines of code. 

## Requirements

In order to use this machine and perform test, the user has then to install 
Crappy and several Phidgets library.

You'll find more details in the dedicated installation section of the 
documentation to install these different python module.

## Documentation

The latest version of the documentation can be accessed on the project's 
website. It contains information about the installation of the different python
module, a more detailed description of the hardware, descriptions of the setups
to perform the different test and indications how to use crappy-based 
algorithms.
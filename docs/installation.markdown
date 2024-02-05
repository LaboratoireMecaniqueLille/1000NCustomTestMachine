---
layout: default
title: Installation
---

[Home page](index.markdown)

This page explains how to install the different python modules required to use 
the 1000N Custom Test Machine.

## Install Crappy

The following modules are necessary to perform tests with the 1000N Custom Test
Machine by using Crappy:

- numpy (1.21.0 or higher)
- matplotlib (1.5.3 or higher, for plotting graphs and displaying images)
- opencv (3.0 or higher, to perform image acquisition and processing)
- Tk (For the configuration interface of cameras)

To install those modules:

```console
user@machine:~$ python3 -m pip install numpy
user@machine:~$ python3 -m pip install matplotlib
user@machine:~$ python3 -m pip install opencv-python
user@machine:~$ python3 -m pip install tk
```

To install Crappy, please follow crappy documentation available 
<a href="https://crappy.readthedocs.io/en/stable/installation.html">here</a>.

## Install Phidgets python libraries with Linux

Install Phidget22 package

```console
user@machine:~$ curl -fsSL https://www.phidgets.com/downloads/setup_linux | sudo -E bash - &&\
sudo apt install -y libphidget22
```

Install additional packages

```console
user@machine:~$ sudo apt install -y libphidget22-dev libphidget22extra phidget22networkserver libphidget22java phidget22admin phidget22wwwjs
```

Install Phidget22 python library

```console
user@machine:~$ python3 -m pip install Phidget22
```

More documentation for the Phidgets python libraries can be found 
<a href="https://www.phidgets.com/docs/OS_-_Linux#Non-Root-1">here</a>. 

[Home page](index.markdown)

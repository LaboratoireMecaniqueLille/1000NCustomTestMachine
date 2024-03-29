---
layout: default
title: Installation
---

[Home page](index.markdown)

This page explains how to install the different python modules required to use 
the 1000N Custom Test Machine.

All the following commands have to be launched from a terminal. To open a 
terminal with Linux, you can hit <B>CTRL+ALT+T</B>.

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
user@machine:~$ sudo apt install python3-tk
```

To install Crappy, please follow crappy documentation available 
<a href="https://crappy.readthedocs.io/en/stable/installation.html">here</a>.

## Install Phidgets python libraries with Linux

Install Phidget22 package

```console
user@machine:~$ sudo apt install curl
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

## Install Git with Linux

To get the python codes available on the GitHub page, you might want to clone 
directly the repository. You will then need to install git packages.

```console
user@machine:~$ sudo apt install git-all
```

## Install Gstreamer with Linux

Using camera with Gstreamer offers better performance than with OpenCV. It can 
then be more convenient to install Gstreamer packages.

```console
user@machine:~$ sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```

## Install v4l-utils with Linux

To fully use the camera and all parameters, it is recommended to install the
v4l-utils package.

```console
user@machine:~$ sudo apt install v4l-utils
```

[Home page](index.markdown)

---
layout: default
title: Installation
---

[Home page](index.markdown)

## Install Crappy

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

Install Phidget22 package

```console
user@machine:~$ python3 -m pip install Phidget22
```

More documentation for the Phidgets python libraries can be found 
<a href="https://www.phidgets.com/docs/OS_-_Linux#Non-Root-1">here</a>. 

[Home page](index.markdown)

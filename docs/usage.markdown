---
layout: default
title: Usage
---

[Home page](index.markdown)

This page describes the procedure to use the 1000N Custom Test Machine.

## 1.Connection

To perform test, you need to connect to the machine. First, you have to press 
the red switch to turn on the machine.

### 1.1 Wi-fi

Once the machine has been turned on, a new wi-fi network should appear in the 
networks section of your computer: Phidgets_Hub5000_XXXXXX. To connect by wi-fi
to the machine, click on this wi-fi network and enter the password: XXXXXXXX.

To check if you are connected and to check the configuration of the machine, 
you can go to your internet browser and type 192.168.100.1 in the address bar.
This page should appear.

<p align="center">
<img src="./images/phidgets_accueil.png" align="center" title="Phidgets wi-fi connection page">
</p>

You can now enter the password of the Hub and open the Phidgets interface.

### 1.2 Ethernet

Once the machine has been turned on, connect your computer with the machine 
with an ethernet cable. Check the IPv4 settings of your wired connection. The
Method should be set to Shared to other computers. If it is not, set it. 

To check if you are connected and to check the configuration of the machine, 
you can go to your internet browser and type hub5000.local in the address bar.
This page should appear.

<p align="center">
<img src="./images/phidgets_accueil_ethernet.png" align="center" title="Phidgets ethernet connection page">
</p>

You can now enter the password of the Hub and open the Phidgets interface.

<br>

From now, there is no more differences between the connection by ethernet and 
by wi-fi.

## 2. Phidgets VINT Hub interface

After entering the password, you will open this page.

<p align="center">
<img src="./images/phidgets_status.png" align="center" title="Phidgets status page">
</p>

It contains information about the Hub.

### 2.1 Network configuration

You can verify if the wireless settings of the Hub are good. For that, click on
the Network button.

<p align="center">
<img src="./images/phidgets_statusnetwork.png" align="center" title="Phidgets Network button">
</p>

The Phidgets Network page should open.

<p align="center">
<img src="./images/phidgets_network.png" align="center" title="Phidgets Network page">
</p>

Now you can check that the Wireless Mode is set to Access Point. Otherwise, 
set it to.

<p align="center">
<img src="./images/phidgets_networkmode.png" align="center" title="Phidgets Network mode">
</p>

The Phidgets Network configuration is now set to use the machine. 

### 2.2 Phidgets Control Panel

You can also verify that all the Phidgets components are well-connected to the
Hub. For that, click on the Phidgets button. 

<p align="center">
<img src="./images/phidgets_statusphidget.png" align="center" title="Phidgets Phidgets button">
</p>

The Phidgets Phidgets page should open.

<p align="center">
<img src="./images/phidgets_phidgets.png" align="center" title="Phidgets Phidgets button">
</p>

To access the Phidgets Control Panel, the optional Phidgets packages has to be 
installed. Their installations are described on the 
[Installation](installation.markdown) page.

If it is the case, you can now open the Phidgets Control Panel. 

<p align="center">
<img src="./images/phidgets_phidgetscontrolpanel.png" align="center" title="Phidgets Control Panel button">
</p>

The Phidgets Control Panel should appear.

<p align="center">
<img src="./images/phidgets_controlpanel.png" align="center" title="Phidgets Control Panel">
</p>

Here you can find all the Phidgets connected to the Wireless VINT Hub. You
should see the Phidgets of the 
[Hardware description](hardware_description.markdown) page: the Wheatstone 
Bridge Phidget and the 4A Stepper Phidget.

You can notice that the limit switches, which are connected to the Hub, do not 
appear in the Phidgets Control Panel.

<br>
<B>WARNING !!!</B>

If the 4A Stepper Phidget appears in the Phidgets Control Panel as "Unsupported
VINT Phidget", it means that the firmware version of the Wireless VINT Hub is 
not up-to-date.

To update the firmware, you can download its latest version 
<a href="https://www.phidgets.com/downloads/phidgetsbc/HUB5000/phidgethub5000.bin">here</a>.

Then, in the Phidgets interface, click on the System button.

<p align="center">
<img src="./images/phidgets_statussysytem.png" align="center" title="Phidgets System button">
</p>

The Phidgets System should appear.

<p align="center">
<img src="./images/phidgets_system.png" align="center" title="Phidgets System page">
</p>

You can see there the Upgrade Firmware section. You can now click on select 
file to get the new firmware file you just download and click on Upgrade & 
Restart to upgrade the firmware.

<p align="center">
<img src="./images/phidgets_systemfirmware.png" align="center" title="Phidgets System page">
</p>

You will have to wait four minutes and then reload the Phidgets interface. 
Then, when you come back to the Phidgets Control Panel, the 4A Stepper Phidget 
should appear.

## 3. Get python codes from GitHub

Now that the Phidgets Wireless VINT Hub is well configured, you can get the 
different python codes available on the GitHub page. The easiest way to get 
these codes is to clone the GitHub repository.

To clone the repository, open a terminal and launch:

```console
user@machine:~$ git clone https://github.com/LaboratoireMecaniqueLille/1000NCustomTestMachine.git
```

## 4. Performing tests

Now you are sure you are connected, you have the codes, the machine is ready 
for tests. 

The way to prepare the setup to test a sample is described in the
[Mechanical setups](setups.markdown) page.

The different codes you can launch with python are described in the 
[Code examples](code_example.markdown) page.

For example:
```console
user@machine:~$ python3 sample_protection.py
user@machine:~$ python3 load_cell.py
```
[Home page](index.markdown)

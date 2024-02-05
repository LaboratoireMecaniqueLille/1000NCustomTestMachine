"""
This example demonstrates how to move the motor after hitting a switch.
It also shows the use of Crappy Blocks outside a Crappy loop.

In this example, a Tkinter slider controlled by the user sends command to the
Actuator Block. The slider sends speed command to drive the motor here.
The user can only drive the motor in the opposite direction of the switch that
has been hit.

The test ends when the slider window is closed.
"""

import crappy
import tkinter as tk

if __name__ == '__main__':

  open_switch = 0

  # This Actuator drives a Phidget4AStepper in speed.
  mot = crappy.actuator.Phidget4AStepper(
    steps_per_mm=2500,  # Number of steps necessary to move by 1 mm.
    current_limit=3,  # Maximum current the driver is allowed to deliver
    # to the motor, in A.
    max_acceleration=20,  # Maximum acceleration the motor is allowed to
    # reach in mm/s².
    remote=True,  # True if connected to a wireless VINT Hub, False if
    # connected to a USB VINT Hub.
    switch_ports=(5, 6)  # Port numbers of the VINT Hub where the
    # switches are connected.
  )

  # Remove the automatic check of the state of the switches
  mot._check_switch = False

  # Open the Actuator
  mot.open()

  # Find the switch that has been hit
  for switch in mot._switches:
    if switch.getState() is False:
      open_switch = switch.getHubPort()


  def gen_speed(value) -> None:
    """Callback sending the speed command to the driver when the user update
    the slider value. """

    mot.set_speed(float(value))


  # Create the graphical interface
  root = tk.Tk()
  root.title("Motor speed")

  # Create the slider associate to the switch hit
  if open_switch == 1:
    # Create the slider
    slider = tk.Scale(root,
                      from_=0,
                      to=2,
                      orient=tk.HORIZONTAL,
                      length=200,
                      resolution=0.1,
                      command=gen_speed)
  elif open_switch == 2:
    slider = tk.Scale(root,
                      from_=-2,
                      to=0,
                      orient=tk.HORIZONTAL,
                      length=200,
                      resolution=0.1,
                      command=gen_speed)
  else:
    raise ValueError(f"No switch has been hit or disconnected")

  slider.pack(pady=20)

  root.mainloop()

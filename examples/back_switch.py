import crappy
import tkinter as tk

if __name__ == '__main__':

  open_switch = 0

  mot = crappy.actuator.Phidget4AStepper(
    steps_per_mm=2500,
    current_limit=3,
    max_acceleration=20,
    remote=True,
    switch_ports=(5, 6))

  mot._check_switch = False
  mot.open()
  for switch in mot._switches:
    if switch.getState() is False:
      open_switch = switch.getHubPort()


  def gen_speed(value):
    mot.set_speed(float(value))


  # Creates the graphical interface
  root = tk.Tk()
  root.title("Motor speed")

  if open_switch == 5:
    # Create the slider
    slider = tk.Scale(root,
                      from_=0,
                      to=2,
                      orient=tk.HORIZONTAL,
                      length=200,
                      resolution=0.1,
                      command=gen_speed)
  elif open_switch == 6:
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

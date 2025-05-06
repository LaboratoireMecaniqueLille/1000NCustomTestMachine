import crappy
import tkinter.filedialog as tkFileDialog  # ToDo: inutilisé
import tomllib
import os


def open_file(path):
    with open(path, "rb") as f:
        data = tomllib.load(f)

    return data


if __name__ == '__main__':

  BASE_DIR = os.environ.get('BASE_DIR')
  if not BASE_DIR:
      raise EnvironmentError("The variable BASE_DIR was not defined")

  path_set = BASE_DIR + "/.default_set_parameters.toml"

  try :
    donnees = open_file(path_set)

    speed = float(donnees['data']['speed'])
    l0 = float(donnees['data']['l0'])
    path_save_data = donnees['data']['path_save_data']
    #load_cell = donnees['data']['load_cell']
    load_cell = "972.7N"
    test_type = donnees['data']['test_type']
    gain = float(donnees['data']['gain'])
    save_path = path_save_data

  except:
    print('probleme_toml_manquant')

  """speed = 2
  l0 = 68
  path_save_data = "/home/stagiaire/Codes/essai_traction/results/1/"
  load_cell = "50N"
  test_type = "Monotone Uniaxial Tensile Test"
  gain = 3.26496001e+05
  save_path = path_save_data"""


  force_max = "F(N)>" + load_cell.replace('N', '')
  

  if test_type == "Monotone Uniaxial Tensile Test":


    # This IOBlock gets the current force measured by a 1000N load cell with a
    # Phidget Wheatstone Bridge, and sends it to downstream Blocks.
    load_cell = crappy.blocks.IOBlock(
      'PhidgetWheatstoneBridge',  # The name of the InOut object to drive.
      labels=['t(s)', 'F(N)'],  # The names of the labels to output.
      make_zero_delay=1,  # To offset the values acquired during the delay to the
      # rest of. Remove this parameter to avoid the offset.
      remote=True,  # True if connected to a wireless VINT Hub, False if
      # connected to a USB VINT Hub.
      channel=1,  # Channel of the Wheatstone Bridge.
      gain=gain,  # Gain of the load cell.
      data_rate=10,
    )

    """
    # This Machine Block drives a Phidget4AStepper in speed.
    motor = crappy.actuator.Phidget4AStepper(switch_ports = (2, 3) ,current_limit= 3 , steps_per_mm= 2500)
    motor.open()
    motor.set_position(l0/2,50)
    """

    mot = crappy.blocks.Machine(
      [{'type': 'Phidget4AStepper',  # The name of the Actuator to drive.
        'mode': 'speed',  # Driving in speed mode, not in position mode.
        'speed_label': 'speed',  # The label carrying the speed readout.
        'position_label': 'x(mm)',  # The label carrying the position readout.
        'steps_per_mm': 2500,  # Number of steps necessary to move by 1 mm.
        'current_limit': 3,  # Maximum current the driver is allowed to deliver
        # to the motor, in A.
        'max_acceleration': 20,  # Maximum acceleration the motor is allowed to
        # reach in mm/s².
        'remote': True,  # True if connected to a wireless VINT Hub, False if
        # connected to a USB VINT Hub.
        'switch_ports': (2, 3),  # Port numbers of the VINT Hub where the
        # switches are connected.
        'absolute_mode': True,
        'reference_pos':l0,
        }])

    # This Generator generates the command for driving the Machine Block.
    # The path drive the Machine in function of the force measured by the load
    # cell.
    gen = crappy.blocks.Generator([{'type':'Constant','condition':force_max,'value':speed}],freq=100)

    # This Block allows the user to properly exit the script
    stop = crappy.blocks.StopButton(
        # No specific argument to give for this Block
    )

    #Enregistrement et réunion des données
    record_f = crappy.blocks.Recorder(save_path + 'effort.csv', labels=['t(s)', 'F(N)'])
    record_pos = crappy.blocks.Recorder(save_path + 'position.csv', labels=['x(mm)'])
    multiplex = crappy.blocks.Multiplexer()
    rec = crappy.blocks.Recorder(save_path + 'data.csv', labels=['t(s)','F(N)','x(mm)'])



    # Graphers
    graph_depl = crappy.blocks.Grapher(('t(s)', 'x(mm)'))
    graph_force= crappy.blocks.Grapher(('t(s)', 'F(N)'))
    graph_def = crappy.blocks.Grapher(('x(mm)', 'F(N)'))



    # Links
      #pour les consignes
    crappy.link(gen, mot) #besoin de consigne
    crappy.link(load_cell, gen) #besoin de savoir la force pour déterminer la consigne
      #réunion de t(s), F(N) et x(mm) dans multiplex puis dans les records
    crappy.link(load_cell, multiplex)
    crappy.link(mot, multiplex)
    crappy.link(multiplex,rec)
    crappy.link(multiplex,record_f)
    crappy.link(multiplex,record_pos)
      #pour les graphes
    crappy.link(load_cell, graph_depl)
    crappy.link(mot, graph_depl)
    crappy.link(load_cell, graph_force)
    crappy.link(load_cell, graph_def)
    crappy.link(mot, graph_def)


    crappy.start()

    print('succes_test')

from src.drivers.Aera import ROD4
from src.drivers.ElchWorks import Ventolino, Valvolino, Thermolino, Thermoplatino, ElchLaser, Omniplex
from src.drivers.Eurotherms import Eurotherm2408, Eurotherm3216
from src.drivers.Jumo import JumoQuantol
from src.drivers.Keithly import Keithly2000Temp
from src.drivers.Omega import OmegaPt
from src.drivers.Pyrometer import Pyrometer
from src.drivers.TestDevices import TestMFC, TestSensor, TestController, NiceTestController, TestValveController

devices = {'heater': {'Eurotherm3216': Eurotherm3216,
                      'Eurotherm2408': Eurotherm2408,
                      'Omega Pt': OmegaPt,
                      'Jumo Quantrol': JumoQuantol,
                      'Elch Heater Controller': ElchLaser,
                      'Elchi Laser Control': ElchLaser,
                      'Test Controller': TestController,
                      'Nice Test Controller': NiceTestController},
           'temp_sensor': {'Pyrometer': Pyrometer,
                           'Thermolino': Thermolino,
                           'Thermoplatino': Thermoplatino,
                           'Keithly2000': Keithly2000Temp,
                           'Test Sensor': TestSensor},
           'flow_controller': {'Ventolino': Ventolino,
                               'Area ROD-4': ROD4,
                               'Test MFC': TestMFC},
           'triggerbox': {'Omni Trigger': Valvolino,
                          'Valvolino': Valvolino,
                          'Test Trigger': TestValveController},
           'multiplexer': {'Omniplex': Omniplex}}

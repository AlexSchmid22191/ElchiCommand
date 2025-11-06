import random
import threading
import time

import src.drivers.AbstractBaseClasses as Base


class TestValveController(Base.AbstractValveController):
    def __init__(self, port):
        self.com_lock = threading.Lock()
        self.valve_states = {channel: channel > 2 for channel in range(1, 5)}
        print(f'Test Controller connected at port {port}')

    def switch_valve(self, channel, state):
        with self.com_lock:
            self.valve_states[channel] = state
            print(f'Test Valve Controller: Set channel {channel} to {state}')

    def read_valve_state(self, channel):
        with self.com_lock:
            time.sleep(0.01)
            return self.valve_states[channel]

    def close(self):
        print(f'Test Controller {self} closed!')


class TestMFC(Base.AbstractMassFlowController):
    def __init__(self, port):
        self.com_lock = threading.Lock()
        self.flow_set = {channel: int(time.time() % 100) for channel in range(1, 5)}
        print(f'Test Controller connected at port {port}')

    def set_flow(self, channel, flow):
        self.flow_set[channel] = flow
        print(f'Test Mass Flow Controller: Set channel {channel} to {flow}')

    def read_is_flow(self, channel):
        with self.com_lock:
            time.sleep(random.randint(1, 10) * 1e-3)
            return self.flow_set[channel] + (time.time() % 0.01) * 10

    def read_set_flow(self, channel):
        with self.com_lock:
            time.sleep(random.randint(1, 10) * 1e-3)
            return self.flow_set[channel]

    def close(self):
        print(f'Test Controller {self} closed!')


class TestSensor(Base.AbstractSensor):
    """Mock Sensor to test engine to GUI connection"""
    mode = 'Temperature'

    def __init__(self, *args, **kwargs):
        print('Test Sensor connected!')
        self.com_lock = threading.Lock()
        print(args, kwargs)

    def get_sensor_value(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60

    def close(self):
        print('Test Sensor disconnected!')


class TestSensorVoltage(Base.AbstractSensor):
    """Mock Sensor to test engine to GUI connection"""
    mode = 'Voltage'

    def __init__(self, *args, **kwargs):
        print('Test Sensor Voltage connected!')
        self.com_lock = threading.Lock()
        print(args, kwargs)

    def get_sensor_value(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60

    def close(self):
        print('Test Sensor disconnected!')


class TestController(Base.AbstractController):
    """Mock controller to test engine to GUI connection"""
    mode = 'Temperature'

    def __init__(self, *args, **kwargs):
        self.com_lock = threading.Lock()
        print('Test Controller connected!')
        print(args, kwargs)

    def get_process_variable(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60 + 1

    def get_target_setpoint(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60 + 2

    def get_working_output(self):
        with self.com_lock:
            time.sleep(0.01)
            return 100 - time.time() % 100

    def get_working_setpoint(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 60 + 4

    def get_control_mode(self):
        with self.com_lock:
            time.sleep(0.01)
            return 'Automatic' if time.time() % 60 > 30 else 'Manual'

    def get_rate(self):
        with self.com_lock:
            time.sleep(0.01)
            return time.time() % 15

    def set_target_setpoint(self, setpoint):
        with self.com_lock:
            print('Test Controller: Set target setpoint {:f}'.format(setpoint))

    def set_manual_output_power(self, output):
        with self.com_lock:
            print('Test Controller: Set output power {:f}'.format(output))

    def set_automatic_mode(self):
        with self.com_lock:
            print('Test Controller: Set to automatic mode')

    def set_manual_mode(self):
        with self.com_lock:
            print('Test Controller: Set to manual mode')

    def set_rate(self, rate):
        with self.com_lock:
            print('Test Controller: Set rate {:f}'.format(rate))


class NiceTestController(TestController):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        self.tsp = 0
        self.wsp = 0
        self.pv = 0
        self.rt = 5

    def get_process_variable(self):
        with self.com_lock:
            time.sleep(0.01)
            self.pv = 0.9 * self.pv + 0.1 * self.wsp
            return self.pv

    def set_rate(self, rate):
        with self.com_lock:
            self.rt = rate
            print('Test Controller: Set rate {:f}'.format(rate))

    def set_target_setpoint(self, setpoint):
        with self.com_lock:
            self.tsp = setpoint
            print('Test Controller: Set target setpoint {:f}'.format(setpoint))

    def get_target_setpoint(self):
        with self.com_lock:
            return self.tsp

    def get_rate(self):
        with self.com_lock:
            return self.rt

    def get_working_setpoint(self):
        with self.com_lock:
            self.wsp += self.rt / 60
            if self.wsp > self.tsp:
                self.wsp = self.tsp
            return self.wsp


class TestMultiplexer:
    def __init__(self, portname: str) -> None:
        self.lock = threading.Lock()
        print(f'Test multiplexer connected at port {portname}')
        self.serial = self
        self.state = [[False]*4]*4

    def set_single_relay(self, relay: tuple, state: bool) -> None:
        with self.lock:
            self.state[relay[0] - 1][relay[1] - 1] = state
            print(f'Set relay L{relay[0]}R{relay[1]} to: {state}')

    def read_single_relay(self, relay: tuple) -> bool:
        with self.lock:
            return self.state[relay[0] - 1][relay[1] - 1]

    def close(self):
        print(f'Test multiplexer {self} closed!')

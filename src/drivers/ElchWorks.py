import threading
import time

import minimalmodbus
import serial

import src.drivers.AbstractBaseClasses as Base
import src.drivers.Aera as Aera


class Valvolino(serial.Serial, Base.AbstractValveController):
    """Driver class for Valvolino Controller"""

    def __init__(self, port):
        super().__init__(port=port, timeout=0.5, baudrate=9600)
        self.channels = 4
        self.com_lock = threading.Lock()

    def switch_valve(self, channel, state):
        """Toggle a valve"""
        assert 1 <= channel <= self.channels, 'Invalid channel'
        string = '{:02d}SSP{:1d}'.format(channel, state)
        with self.com_lock:
            self.write(b'\x02')
            self.write(string.encode())
            self.write(b'\x0D')
            self.readline()

    def read_valve_state(self, channel):
        """Read the state of a valve"""
        assert 1 <= channel <= self.channels, 'Invalid channel'
        string = f'{channel:02d}RSP'
        with self.com_lock:
            self.write(b'\x02')
            self.write(string.encode())
            self.write(b'\x0D')

            answer = self.readline()
            return bool(int(answer.decode()))


class Ventolino(Aera.ROD4):
    """
    Driver class for Ventolino MFC controllers
    This is the same as Area ROD-4 since the communication protocols are iodentical.
    Separate class in case this might change
    """

    def set_flow(self, channel, flow):
        """Set desired flow"""
        assert 0 <= flow <= 100 and 1 <= channel <= self.channels, 'Invalid channel or flow'
        string = '{:02d}SFD{:3.1f}'.format(channel, flow)
        with self.com_lock:
            self.write(b'\x02')
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            # Also accept empty string because some old ventolino return no acknowledgment line
            assert answer in (b'rec\r\n', b''), f'Invalid response from ROD4 {answer.decode()}'


class Omniplex(minimalmodbus.Instrument):
    def __init__(self, portname: str, slaveadress: int = 1, baudrate: int = 9600) -> None:
        super().__init__(portname, slaveadress)
        self.serial.baudrate = baudrate
        self.lock = threading.Lock()
        time.sleep(2)

    def set_single_relay(self, relay: tuple, state: bool) -> None:
        with self.lock:
            self.write_bit(self._relay_to_address(relay), state, functioncode=5)

    def read_single_relay(self, relay: tuple) -> bool:
        with self.lock:
            return bool(self.read_bit(self._relay_to_address(relay), functioncode=1))

    def set_all_relays(self, states: dict) -> None:
        with self.lock:
            states = [states[relay] for relay in map(self._address_to_relay, range(16))]
            self.write_bits(0, states)

    def read_all_relays(self) -> dict:
        with self.lock:
            states = self.read_bits(0, 16, functioncode=1)
            return {self._address_to_relay(address): bool(states[address]) for address in range(16)}

    @staticmethod
    def _address_to_relay(adress: int) -> tuple:
        return adress // 4 + 1, adress % 4 + 1

    @staticmethod
    def _relay_to_address(relay: tuple) -> int:
        return (relay[0] - 1) * 4 + relay[1] - 1


class Thermolino(Base.AbstractSensor, serial.Serial):
    mode = 'Temperature'

    def __init__(self, port):
        super().__init__(port, timeout=1.5)
        self.com_lock = threading.Lock()
        time.sleep(1)
        with self.com_lock:
            self.write(":FUNC 'TEMP'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.write(':read?'.encode())
            self.write('\n'.encode())
            return float(self.readline().decode())

    def close(self):
        serial.Serial.close(self)


class Thermoplatino(Base.AbstractSensor, serial.Serial):
    mode = 'Temperature'

    def __init__(self, port):
        super().__init__(port, timeout=1.5, baudrate=115200)
        self.com_lock = threading.Lock()
        time.sleep(1)
        with self.com_lock:
            self.write(":FUNC 'TEMP'\n".encode())

    def get_sensor_value(self):
        with self.com_lock:
            self.write(':read?'.encode())
            self.write('\n'.encode())
            answer = self.readline().decode()
            try:
                return float(answer)
            except ValueError:
                return answer

    def close(self):
        serial.Serial.close(self)


class ElchLaser(Base.AbstractController, minimalmodbus.Instrument):
    mode = 'Temperature'

    def __init__(self, portname, slaveadress=1, baudrate=9600):
        super().__init__(portname, slaveadress)
        time.sleep(1)
        self.serial.baudrate = baudrate
        self.com_lock = threading.Lock()

    def get_process_variable(self):
        """Return the current process variable"""
        with self.com_lock:
            return self.read_register(0, number_of_decimals=1)

    def set_target_setpoint(self, setpoint):
        """Set the target setpoint"""
        with self.com_lock:
            self.write_register(1, setpoint, number_of_decimals=1)

    def get_target_setpoint(self):
        """Get the target setpoint"""
        with self.com_lock:
            return self.read_register(1, number_of_decimals=1)

    def set_manual_output_power(self, output):
        """Set the power output of the controller in percent"""
        with self.com_lock:
            self.write_register(2, output, number_of_decimals=2)

    def get_working_output(self):
        """Return the current power output of the controller"""
        with self.com_lock:
            return self.read_register(3, number_of_decimals=2)

    def get_working_setpoint(self):
        """Get the current working setpoint of the instrument"""
        with self.com_lock:
            return self.read_register(4, number_of_decimals=1)

    def set_rate(self, rate):
        """Set the rate of change for the working setpoint i.e., the heating/cooling rate"""
        with self.com_lock:
            self.write_register(5, rate, number_of_decimals=1)

    def get_rate(self):
        """Get the rate of change for the working setpoint i.e., the heating/cooling rate"""
        with self.com_lock:
            return self.read_register(5, number_of_decimals=1)

    def set_automatic_mode(self):
        """Set controller to automatic mode"""
        with self.com_lock:
            self.write_register(6, 0)

    def set_manual_mode(self):
        """Set controller to manual mode"""
        with self.com_lock:
            self.write_register(6, 1)

    def get_control_mode(self):
        """get the active control mode"""
        with self.com_lock:
            return {0: 'Automatic', 1: 'Manual'}[self.read_register(6, 0)]

    def set_pid_p(self, p):
        """Set the P (Proportional band) for the PID controller"""
        with self.com_lock:
            self.write_register(7, p, number_of_decimals=1)

    def set_pid_i(self, i):
        """Set the I (Integral time) for the PID controller"""
        with self.com_lock:
            self.write_register(8, i, number_of_decimals=0)

    def set_pid_d(self, d):
        """Set the D (Derivative time) for the PID controller"""
        with self.com_lock:
            self.write_register(9, d, number_of_decimals=0)

    def get_pid_p(self):
        with self.com_lock:
            return self.read_register(7, number_of_decimals=1)

    def get_pid_i(self):
        with self.com_lock:
            return self.read_register(8, number_of_decimals=0)

    def get_pid_d(self):
        with self.com_lock:
            return self.read_register(9, number_of_decimals=0)

    def enable_output(self):
        with self.com_lock:
            self.write_register(10, 1)

    def disable_output(self):
        with self.com_lock:
            self.write_register(10, 0)

    def get_enable_state(self):
        with self.com_lock:
            return self.read_register(10)

    def get_tc_fault(self):
        with self.com_lock:
            return self.read_register(12)

    def enable_aiming_beam(self):
        with self.com_lock:
            self.write_register(13, 1)

    def disable_aiming_beam(self):
        with self.com_lock:
            self.write_register(13, 0)

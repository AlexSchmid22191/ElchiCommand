import threading

import serial

import src.drivers.AbstractBaseClasses as Base


class ROD4(serial.Serial, Base.AbstractMassFlowController):
    """Driver class for Aera ROD4"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channels = 4
        self.com_lock = threading.Lock()

    def set_flow(self, channel, flow):
        """Set desired flow"""
        assert 0 <= flow <= 100 and 1 <= channel <= self.channels, 'Invalid channel or flow'
        string = '{:02d}SFD{:3.1f}'.format(channel, flow)
        with self.com_lock:
            self.write(b'\x02')
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            assert answer.decode == 'OK', 'No response from ROD4'

    def read_is_flow(self, channel):
        """Read flow, emit message with flow value or status message with error"""
        assert 1 <= channel <= self.channels, 'Invalid channel'
        string = '{:02d}RFX'.format(channel)
        with self.com_lock:
            self.write(b'\x02')
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            return float(answer.decode())

    def read_set_flow(self, channel):
        assert 1 <= channel <= self.channels, 'Invalid channel'
        string = '{:02d}RFD'.format(channel)
        with self.com_lock:
            self.write(b'\x02')
            self.write(string.encode())
            self.write(b'\x0D')

            answer = self.readline()
            return float(answer.decode())

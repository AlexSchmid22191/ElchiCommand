import abc
from abc import ABC


class Cycle(ABC):
    def __init__(self):
        self.subcycles = None

    def add_subcycle(self, cycle):
        if self.subcycles is None:
            self.subcycles = [cycle]
        else:
            self.subcycles.append(cycle)

    @abc.abstractmethod
    def _to_actions(self):
        pass

    def unroll(self):
        if self.subcycles is None:
            return self._to_actions()
        else:
            return [item for i in self._to_actions() for item in (i, [sub.unroll() for sub in self.subcycles])]


class TemperatureCycle(Cycle):
    def __init__(self, start, end, step, heater, sensor, delta_time, delta_temp, t_res):
        super().__init__()
        self.temperatures = self._make_list(start, end, step)
        self.heater = heater
        self.sensor = sensor
        self.delta_time = delta_time
        self.delta_temp = delta_temp
        self.t_res = t_res

    @staticmethod
    def _make_list(start, end, step):
        if abs(end - start) % step != 0:
            print('Warning: The step size does not divide the difference between the start and end temperatures!'
                  ' Check the generated list!')
        return range(start, end +1, step)

    def _to_actions(self):
        return [{'type': 'Set_temp', 'heater': self.heater, 'temp_sensor': self.sensor, 'delta_temp': self.delta_temp,
                'delta_time': self.delta_time, 'time_res': self.t_res, 't_set': temp} for temp in self.temperatures]

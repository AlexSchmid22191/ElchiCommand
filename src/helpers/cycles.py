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
        step = abs(step) * (-1 if start > end else 1)
        return range(start, end + 1, step)

    def _to_actions(self):
        return [{'type': 'set_temp', 'heater': self.heater, 'temp_sensor': self.sensor, 'delta_temp': self.delta_temp,
                'delta_time': self.delta_time, 'time_res': self.t_res, 't_set': temp} for temp in self.temperatures]


class BlindTemperatureCycle(Cycle):
    def __init__(self, start, end, step, heater):
        super().__init__()
        self.temperatures = self._make_list(start, end, step)
        self.heater = heater

    @staticmethod
    def _make_list(start, end, step):
        if abs(end - start) % step != 0:
            print('Warning: The step size does not divide the difference between the start and end temperatures!'
                  ' Check the generated list!')
        step = abs(step) * (-1 if start > end else 1)
        return range(start, end + 1, step)

    def _to_actions(self):
        return [{'type': 'set_temp_blind', 'heater': self.heater, 't_set': temp} for temp in self.temperatures]


class TriggerCycle(Cycle):
    def __init__(self, triggerbox, states):
        super().__init__()
        self.triggerbox = triggerbox
        self.states = states

    def _to_actions(self):
        return [
            {
                'type': 'trigger',
                'triggerbox': self.triggerbox,
                'state_1': s1,
                'state_2': s2,
                'state_3': s3,
                'state_4': s4,
            }
            for state in self.states
            for (s1, s2, s3, s4) in [tuple(state)]
        ]


class FlowCycle(Cycle):
    def __init__(self, flow_controller, flow_rates):
        super().__init__()
        self.flow_controller = flow_controller
        self.flow_rates = flow_rates

    def _to_actions(self):
        return [
            {
                'type': 'gas_ctrl',
                'flow_control': self.flow_controller,
                'flow_1': s1,
                'flow_2': s2,
                'flow_3': s3,
                'flow_4': s4,
            }
            for flow in self.flow_rates
            for (s1, s2, s3, s4) in [tuple(flow)]
        ]


class MultiplexerCycle(Cycle):
    def __init__(self, multiplexer, states):
        super().__init__()
        self.multiplexer = multiplexer
        self.states = states

    def _to_actions(self):
        return [
            {
                'type': 'multiplexer',
                'multiplexer': self.multiplexer,
                'state_L1R1': s11,
                'state_L2R1': s21,
                'state_L3R1': s31,
                'state_L4R1': s41,
                'state_L1R2': s12,
                'state_L2R2': s22,
                'state_L3R2': s32,
                'state_L4R2': s42,
                'state_L1R3': s13,
                'state_L2R3': s23,
                'state_L3R3': s33,
                'state_L4R3': s43,
                'state_L1R4': s14,
                'state_L2R4': s24,
                'state_L3R4': s34,
                'state_L4R4': s44,
            }
            for state in self.states
            for (s11, s21, s31, s41, s12, s22, s32, s42, s13, s23, s33, s43, s14, s24, s34, s44) in [tuple(state)]]


def flatten(x):
    for elem in x:
        if isinstance(elem, list):
            yield from flatten(elem)
        else:
            yield elem
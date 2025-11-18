from pathlib import Path
import os
import serial.tools.list_ports
import yaml
from platformdirs import user_config_dir
import datetime
from src.helpers.cycles import Cycle, TemperatureCycle, BlindTemperatureCycle, FlowCycle, TriggerCycle, \
    MultiplexerCycle, flatten
from src.helpers.devices import devices as valid_devices
from src.helpers.queries import (query_yes_no, query_options, query_unique, query_bounded, query_bounded_int,
                                 query_bounded_list, query_options_list)

available_ports = [port.device for port in serial.tools.list_ports.comports()]
cycle_types = ['Temperature', 'Temperature (sensorless)', 'Flow', 'Trigger', 'Multiplexer']

devices = {}
cycles = []
edit_stack = ['Root']


def main():
    print('Hi! I am ElchiCreator the interactive configuration writer!')
    print('I will help you create your own configuration file for ElchiCommander!')
    print('First, lets add all the devices you want to control in the experiment!')

    while query_yes_no('Do you want to add a device?'):
        if device := add_device():
            devices.update(device)

    print('Done! Now lets define the cycles that make up your experiment!')

    while query_yes_no('Do you want to add a cycle?'):
        if cycle := add_cycle():
            cycles.append(cycle)

    actions = [cycle.unroll() for cycle in cycles]
    actions = list(flatten(actions))
    actions = {key: action for key, action in enumerate(actions, start=1)}

    actions.update({0: {'type': 'iterate_list', 'processed_actions': [],
                        'action_ids': sorted(list(actions.keys()))}})

    config = {'devices': devices, 'actions': actions}

    print('Done! Here is the configuration file I created for you:')
    print(yaml.dump(config, default_flow_style=False, default_style=''))

    if query_yes_no('Do you want to save this for use with ElchiCommander?'):
        config_path = Path(user_config_dir('ElchiCommander',
                                           'ElchWorks', roaming=True))

        config_path.mkdir(parents=True, exist_ok=True)
        config_path = config_path / 'config.yaml'

        if os.path.isfile(config_path):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            base, ext = os.path.splitext(config_path)
            os.rename(config_path, f'{base}_{timestamp}{ext}')

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, default_style='')


def add_cycle() -> Cycle | None:
    cycle = None
    match query_options('What type of cycle do you want to add?', cycle_types):
        case 'Temperature':
            edit_stack.append('Temperature')
            heater = query_options('Which heater do you want to use?',
                                   [device_id for device_id, device in devices.items() if device['type'] == 'heater'])
            if heater is None:
                return None
            sensor = query_options('Which temperature sensor do you want to use?',
                                   [device_id for device_id, device in devices.items() if
                                    device['type'] == 'temp_sensor'])
            if sensor is None:
                return None
            delta_temp = query_bounded('What is the maximum temperature change in degree Celsius that is still'
                                       ' regarded stable?',
                                       0.01, 100)
            delta_time = query_bounded('For how many seconds should the temperature change by less than that?',
                                       1, 1000000)
            time_res = query_bounded_int('How many seconds should pass between temperature checks?', 1,
                                         1000000)
            t_start = query_bounded_int('What is the start temperature in degree Celsius?', 0, 1500)
            t_end = query_bounded_int('What is the end temperature in degree Celsius?', 0, 1500)
            t_step = query_bounded_int('What is the temperature step in degree Celsius?', 1, 1000)
            cycle = TemperatureCycle(t_start, t_end, t_step, heater, sensor, delta_time, delta_temp, time_res)
        case 'Temperature (sensorless)':
            edit_stack.append('Temperature (sensorless)')
            heater = query_options('Which heater do you want to use?',
                                   [device_id for device_id, device in devices.items() if device['type'] == 'heater'])
            if heater is None:
                return None
            t_start = query_bounded_int('What is the start temperature in degree Celsius?', 0, 1500)
            t_end = query_bounded_int('What is the end temperature in degree Celsius?', 0, 1500)
            t_step = query_bounded_int('What is the temperature step in degree Celsius?', 1, 1000)
            cycle = BlindTemperatureCycle(t_start, t_end, t_step, heater)
        case 'Flow':
            edit_stack.append('Flow')
            flow_controller = query_options('Which flow controller do you want to use?',
                                            [device_id for device_id, device in devices.items()
                                             if device['type'] == 'flow_controller'])
            if flow_controller is None:
                return None
            flows = []
            while query_yes_no('Do you want to add a set of flow rates?'):
                flows.append(query_bounded_list('What are the flow percentages for channels 1 to 4?',
                                                0.0, 100, 4))
            cycle = FlowCycle(flow_controller, flows)
        case 'Trigger':
            edit_stack.append('Trigger')
            triggerbox = query_options('Which triggerbox do you want to use?',
                                       [device_id for device_id, device in devices.items()
                                        if device['type'] == 'triggerbox'])
            if triggerbox is None:
                return None
            states = []
            while query_yes_no('Do you want to add a triggerbox state?'):
                states.append(query_options_list('What are the states of relays 1 to 4?',
                                                 ('0', '1'), 4))
            states = [[int(x) for x in state] for state in states]
            cycle = TriggerCycle(triggerbox, states)
        case 'Multiplexer':
            edit_stack.append('Multiplexer')
            multiplexer = query_options('Which multiplexer do you want to use?',
                                        [device_id for device_id, device in devices.items()
                                         if device['type'] == 'multiplexer'])
            if multiplexer is None:
                return None
            states = []
            while query_yes_no('Do you want to add a multiplexer state?'):
                states.append(query_options_list('What are states of relays L1R1, L2R1,... L4R4?',
                                                 ('0', '1'), 16))
            states = [[int(x) for x in state] for state in states]
            cycle = MultiplexerCycle(multiplexer, states)
        case _:
            # Default case should never be reached
            pass

    while query_yes_no(
            'You are here: ' + ' --> '.join(edit_stack) + '\nDo you want to ad a subcycle to this cycle?'):
        if sub_cycle := add_cycle():
            cycle.add_subcycle(sub_cycle)
    print('Cycle added successfully!')
    edit_stack.pop()
    return cycle


def add_device() -> dict | None:
    match query_options('What type of device do you want to add?', valid_devices):
        case device_type if device_type in valid_devices:
            device = query_options(f'What type of {device_type} do you want to use?', valid_devices[device_type])
            if device is None:
                return None
            port = query_options('What port is it connected to?', available_ports)
            if port is None:
                return None
            device_id = query_unique(f'Choose a unique name for this {device_type}: ', list(devices.keys()))
            return {device_id: {'type': device_type, 'device': device, 'port': port}}
        case '0':
            return None
        case _:
            # Default case should never be reached
            return None


if __name__ == '__main__':
    main()

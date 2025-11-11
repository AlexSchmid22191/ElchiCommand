import serial.tools.list_ports

from src.helpers.cycles import Cycle, TemperatureCycle, BlindTemperatureCycle, FlowCycle, TriggerCycle, MultiplexerCycle
from src.helpers.devices import devices as valid_devices
from src.helpers.queries import (query_yes_no, query_options, query_unique, query_bounded, query_bounded_int,
                                 query_bounded_list)

available_ports = [port.device for port in serial.tools.list_ports.comports()]
cycle_types = ['Temperature', 'Temperature (sensorless)', 'Flow', 'Trigger', 'Multiplexer']

devices = {}
cycles = []
edit_stack = ['Root']


def main():
    print('Hi! This is ElchiCreator the interactive configuration writer!')
    print('This tool will help you create your own configuration file for ElchiCommander!')
    print('First, lets add all the devices you want to control in the experiment!')

    while query_yes_no('Do you want to add a device?'):
        if device := add_device():
            devices.update(device)

    print('Done! Now lets define the cycles you want to execute!')
    while query_yes_no('Do you want to add a cycle?'):
        if cycle := add_cycle():
            cycles.append(cycle)
    # Process all cycles into a nested list of action dicts via unroll functions
    # Flatten that list
    # Enumerate that list into dict with action id as keys and action dict as value
    # Combine with devices dict
    # Add some comments
    # Dump that dict to a yaml file


def add_cycle() -> Cycle | None:
    cycle = None
    match query_options('What type of cycle do you want to add?', cycle_types):
        case 'Temperature':
            edit_stack.append('Temperature')
            heater = query_options('Which heater do you want to use?',
                                   [device_id for device_id, device in devices.items() if device['type'] == 'heater'],
                                   can_be_canceled=False)
            sensor = query_options('Which temperature sensor do you want to use?',
                                   [device_id for device_id, device in devices.items() if
                                    device['type'] == 'temp_sensor'], can_be_canceled=False)
            delta_temp = query_bounded('How much should the temperature change by at most?',
                                       0.01, 100)
            delta_time = query_bounded('How long should the temperature change no more than that?',
                                       1, 1000000)
            time_res = query_bounded_int('How often should the temperature be checked?', 1,
                                         1000000)
            t_start = query_bounded_int('What is the starting temperature?', 0, 1500)
            t_end = query_bounded_int('What is the ending temperature?', 0, 1500)
            t_step = query_bounded_int('What is the temperature step?', 1, 1000)
            cycle = TemperatureCycle(t_start, t_end, t_step, heater, sensor, delta_time, delta_temp, time_res)
        case 'Temperature (sensorless)':
            edit_stack.append('Temperature (sensorless)')
            heater = query_options('Which heater do you want to use?',
                                   [device_id for device_id, device in devices.items() if device['type'] == 'heater'],
                                   can_be_canceled=False)
            t_start = query_bounded_int('What is the starting temperature?', 0, 1500)
            t_end = query_bounded_int('What is the ending temperature?', 0, 1500)
            t_step = query_bounded_int('What is the temperature step?', 1, 1000)
            cycle = BlindTemperatureCycle(t_start, t_end, t_step, heater)
        case 'Flow':
            edit_stack.append('Flow')
            flow_controller = query_options('Which flow controller do you want to use?',
                                            [device_id for device_id, device in devices.items()
                                             if device['type'] == 'flow_controller'], can_be_canceled=False)
            flows = []
            while query_yes_no('Do you want to add a flow rate?'):
                flows.append(query_bounded_list('What are the desired flows for channels 1-4?\n'
                                                'Enter as comma separated list of 4 values from 0-100: ',
                                                0.0, 100, 4))
            cycle = FlowCycle(flow_controller, flows)
        case 'Trigger':
            edit_stack.append('Trigger')
            triggerbox = query_options('Which triggerbox do you want to use?',
                                            [device_id for device_id, device in devices.items()
                                             if device['type'] == 'triggerbox'], can_be_canceled=False)
            states = []
            while query_yes_no('Do you want to add a relay state?'):
                states.append(query_bounded_list('What are the states of relays 1-4?\n'
                                                 'Enter as comma separated list of 4 values, 0 or 1: ',
                                                 0, 100, 4))
            cycle = TriggerCycle(triggerbox, states)
        case 'Multiplexer':
            edit_stack.append('Multiplexer')
            multiplexer = query_options('Which multiplexer do you want to use?',
                                        [device_id for device_id, device in devices.items()
                                         if device['type'] == 'multiplexer'], can_be_canceled=False)
            states = []
            while query_yes_no('Do you want to add a multiplexer state?'):
                states.append(query_bounded_list('What are states of relays L1R1, L2R1,... L4R4?\n'
                                                 'Enter as comma separated list of 16 values, 0 or 1: ',
                                                 0, 1, 16))
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
            port = query_options('What port is it connected to?', available_ports)
            device_id = query_unique(f'Choose a unique name for this {device_type}: ', list(devices.keys()))
            return {device_id: {'type': device_type, 'device': device, 'port': port}}
        case '0':
            return None
        case _:
            # Default case should never be reached
            return None


if __name__ == '__main__':
    main()

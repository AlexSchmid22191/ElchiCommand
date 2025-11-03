import re

import serial.tools.list_ports

from src.helpers.exit import delayed_exit

valid_devices = {'heater': ['Eurotherm3216', 'Eurotherm2408', 'Omega Pt', 'Jumo Quantrol', 'Elch Heater Controller'
                                                                                           'Elch Laser Control',
                            'Test Controller', 'Nice Test Controller'],
                 'temp_sensor': ['Pyrometer', 'Thermolino', 'Thermoplatino', 'Keithly2000', 'Eurotherm3508',
                                 'Test Sensor'],
                 'gas_ctrl': ['Ventolino', 'Area ROD-4', 'Test-MFC'],
                 'triggerbox': ['Omni Trigger', 'Valvolino', 'Test Trigger'],
                 'multiplexer': ['Omniplex']}
valid_actions = ['set_temp', 'set_temp_blind', 'gas_ctrl', 'trigger', 'multiplexer']
available_ports = [port.device for port in serial.tools.list_ports.comports()]
available_ports.append('COMXY')


def validate_config(config: dict) -> None:
    try:
        device_config = config.get('devices')
    except KeyError:
        delayed_exit('Missing devices section in config file!', 1)
    else:
        validate_device_config(device_config)
        print('Device config validation successful!')

        try:
            action_config = config.get('actions')
        except KeyError:
            delayed_exit('Missing actions section in config file!', 1)
        else:
            for key, value in action_config.items():
                if not isinstance(key, int) or key < 1:
                    delayed_exit(f'Invalid preset key encounterd: {key}! Valid presetes are positive integers!')
                else:
                    validate_action(key, value, device_config)
            print('Action config validation successful!')


def validate_device_config(device_config: dict) -> None:
    for key, config in device_config.items():
        print(f'Validating device {key}...')
        if missing := {'type', 'device', 'port'} - config.keys():
            delayed_exit(f'Missing entries in config file: {missing}!', 1)

        if (device_type := config['type']) not in valid_devices.keys():
            delayed_exit(f'Invalid device type encountered: {config['type']}!\n'
                         f' Valid device types: {', '.join(valid_devices.keys())}', 1)

        if config['device'] not in valid_devices[device_type]:
            delayed_exit(f'Invalid {device_type} device encountered: {config['device']}!\n'
                         f' Valid device types: {', '.join(valid_devices[device_type])}', 1)

        if config['port'] not in available_ports:
            delayed_exit(f'Invalid port encountered: {config['port']}!\n'
                         f' Valid device types: {', '.join(valid_devices[device_type])}', 1)

        print(f'Device {key} validation successful!')


def validate_action(key, config, device_config):
    print(f'Validating action preset {key}...')
    if 'type' not in config:
        delayed_exit(f'Missing type entry in preset {key}!', 1)

    match config['type']:
        case 'set_temp':
            print('Detected temperature set action!')
            validate_temp_set_action(config, device_config)
        case 'set_temp_blind':
            print('Detected blind temeprature set action!')
            validate_blind_temp_set_action(config, device_config)
        case 'gas_ctrl':
            print('Detected gas controller action!')
            validate_massflow_action(config, device_config)
        case 'trigger':
            print('Detected triggerbox action!')
            validate_triggerbox_action(config, device_config)
        case 'multiplexer':
            print('Detected multiplexer action!')
            validate_multiplexer_action(config, device_config)
        case _:
            delayed_exit(f'Invalid action type encountered: {config['type']}!'
                         f'Valid action types are: {', '.join(valid_actions)}', 1)


def validate_massflow_action(config: dict, devices: dict) -> None:
    if 'flow_controller' not in config:
        delayed_exit('Missing entry flow_controller in action preset!', 1)

    if config['flow_controller'] not in devices:
        delayed_exit(f'Specified flow_controller {config['flow_controller']} not defined in device section!',
                     1)

    device = devices[config['flow_controller']]
    if device['device'] not in valid_devices['gas_ctrl']:
        delayed_exit(f'Specified flow_controller {device} is not a valid gas_ctrl device!'
                     f'Valid devices are: {', '.join(valid_devices['gas_ctrl'])}',
                     1)

    for inner_key, inner_value in config.items():
        if inner_key in ['flow_controller', 'type']:
            continue
        if not re.compile(r'^flow_[1-4]$').match(inner_key):
            delayed_exit(f'Invalid channel encounterd: {inner_key}!'
                         f' Valid channels are: flow_1, flow_2, flow_3 and flow_4!')
        if not isinstance(inner_value, (int, float)) or inner_value < 0 or inner_value > 100:
            delayed_exit(f'Invalid value encountered for channel {inner_key}: {inner_value}!'
                         f' Valid values are: 0 to 100')

    print('Mass flow action validated sucessfully!')


def validate_triggerbox_action(config: dict, devices: dict) -> None:
    if 'triggerbox' not in config:
        delayed_exit('Missing entry triggerbox in action preset!', 1)

    if config['triggerbox'] not in devices:
        delayed_exit(f'Specified triggerbox {config['triggerbox']} not defined in device section!',
                     1)

    device = devices[config['triggerbox']]
    if device['device'] not in valid_devices['triggerbox']:
        delayed_exit(f'Specified triggerbox {device} is not a valid triggerbox device!'
                     f'Valid devices are: {', '.join(valid_devices['triggerbox'])}',
                     1)

    for inner_key, inner_value in config.items():
        if inner_key in ['triggerbox', 'type']:
            continue
        else:
            if not re.compile(r'^state_[1-4]$').match(inner_key):
                delayed_exit(f'Invalid channel encounterd: {inner_key}!'
                             f' Valid channels are: state_1, state_2, state_3 and state_4!')
            if inner_value not in [0, 1]:
                delayed_exit(f'Invalid value encountered for channel {inner_key}: {inner_value}!'
                             f' Valid values are: 0 or 1')

    print('Triggerbox action validated sucessfully!')


def validate_multiplexer_action(config: dict, devices: dict) -> None:
    if 'multiplexer' not in config:
        delayed_exit('Missing entry multiplexer in action preset!', 1)

    if config['multiplexer'] not in devices:
        delayed_exit(f'Specified multiplexer {config['multiplexer']} not defined in device section!',
                     1)

    device = devices[config['multiplexer']]
    if device['device'] not in valid_devices['multiplexer']:
        delayed_exit(f'Specified multiplexer {device} is not a valid multiplexer device!'
                     f'Valid devices are: {', '.join(valid_devices['multiplexer'])}',
                     1)

    for inner_key, inner_value in config.items():
        if inner_key in ['multiplexer', 'type']:
            continue
        else:
            if not re.compile(r'^state_L[1-4]R[1-4]$').match(inner_key):
                delayed_exit(f'Invalid channel encounterd: {inner_key}!'
                             f' Valid channels are: state_LnRm, where n and m are 1 to 4!')
            if inner_value not in [0, 1]:
                delayed_exit(f'Invalid value encountered for channel {inner_key}: {inner_value}!'
                             f' Valid values are: 0 or 1')

    print('Multiplexer action validated sucessfully!')


def validate_temp_set_action(config: dict, devices: dict) -> None:
    if 'heater' not in config:
        delayed_exit('Missing entry heater in action preset!', 1)

    if config['heater'] not in devices:
        delayed_exit(f'Specified heater {config['heater']} not defined in device section!',
                     1)

    device = devices[config['heater']]
    if device['device'] not in valid_devices['heater']:
        delayed_exit(f'Specified heater {device} is not a valid heater device!'
                     f'Valid devices are: {', '.join(valid_devices['heater'])}',
                     1)

    if 'sensor' not in config:
        delayed_exit('Missing entry sensor in action preset!', 1)

    if config['sensor'] not in devices:
        delayed_exit(f'Specified sensor {config['sensor']} not defined in device section!',
                     1)

    device = devices[config['sensor']]
    if device['device'] not in valid_devices['temp_sensor']:
        delayed_exit(f'Specified sensor {device} is not a valid temperature sensor device!'
                     f'Valid devices are: {', '.join(valid_devices['temp_sensor'])}',
                     1)

    if 't_set' not in config:
        delayed_exit('Missing entry t_set in action preset!', 1)

    if not isinstance(config['t_set'], (int, float)) or config['t_set'] < -200 or config['t_set'] > 1500:
        delayed_exit(f'Invalid value encountered for t_set: {config["t_set"]}!'
                     f' Valid values are: -200 to 1500')

    if 'delta_temp' not in config:
        delayed_exit('Missing entry delta_temp in action preset!', 1)

    if not isinstance(config['delta_temp'], (int, float)) or config['delta_temp'] <= 0:
        delayed_exit(f'Invalid value encountered for t_set: {config['delta_temp']}!'
                     f' Valid values are positive floating point numbers')

    if 'delta_time' not in config:
        delayed_exit('Missing entry delta_time in action preset!', 1)

    if not isinstance(config['delta_time'], (int, float)) or config['delta_time'] <= 0:
        delayed_exit(f'Invalid value encountered for delta_time: {config['delta_time']}!'
                     f' Valid values are positive floating point numbers')

    if 'time_res' not in config:
        delayed_exit('Missing entry time_res in action preset!', 1)

    if not isinstance(config['time_res'], (int, float)) or config['time_res'] <= 0:
        delayed_exit(f'Invalid value encountered for time_res: {config['time_res']}!'
                     f' Valid values are positive floating point numbers')

    print('Temperature set action validated sucessfully!')


def validate_blind_temp_set_action(config: dict, devices: dict) -> None:
    if 'heater' not in config:
        delayed_exit('Missing entry heater in action preset!', 1)

    if config['heater'] not in devices:
        delayed_exit(f'Specified heater {config['heater']} not defined in device section!',
                     1)

    device = devices[config['heater']]
    if device['device'] not in valid_devices['heater']:
        delayed_exit(f'Specified heater {device} is not a valid heater device!'
                     f'Valid devices are: {', '.join(valid_devices['heater'])}',
                     1)

    if 't_set' not in config:
        delayed_exit('Missing entry t_set in action preset!', 1)

    if not isinstance(config['t_set'], (int, float)) or config['t_set'] < -200 or config['t_set'] > 1500:
        delayed_exit(f'Invalid value encountered for t_set: {config["t_set"]}!'
                     f' Valid values are: -200 to 1500')

    print('Blind temperature set action validated sucessfully!')


if __name__ == '__main__':
    import file_load

    test_config = file_load.load_config('../test_command_definition.yaml')
    validate_config(test_config)

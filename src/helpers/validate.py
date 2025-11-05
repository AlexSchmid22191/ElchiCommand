import re

import serial.tools.list_ports

from src.helpers.devices import devices as valid_devices
from src.helpers.exit import delayed_exit

valid_actions = ['set_temp', 'set_temp_blind', 'gas_ctrl', 'trigger', 'multiplexer']
available_ports = [port.device for port in serial.tools.list_ports.comports()]
available_ports.append('COMXY')


def validate_config(config: dict) -> None:
    try:
        device_config = config.get('devices')
    except KeyError:
        delayed_exit('Missing devices section in config file!', 1)
    else:
        _validate_device_config(device_config)
        print('Device config validation successful!')

        try:
            action_config = config.get('actions')
        except KeyError:
            delayed_exit('Missing actions section in config file!', 1)
        else:
            for key, value in action_config.items():
                if not isinstance(key, int) or key < 1:
                    delayed_exit(f'Invalid preset key encounterd: {key}! Valid presetes are positive integers!')
                elif value['type'] == 'iterate_list':
                    _validate_list_action(config, value)
                else:
                    _validate_action(key, value, device_config)
            print('Action config validation successful!')


def _validate_device_config(device_config: dict) -> None:
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


def _validate_action(key, config, device_config):
    print(f'Validating action preset {key}...')
    if 'type' not in config:
        delayed_exit(f'Missing type entry in preset {key}!', 1)

    match config['type']:
        case 'set_temp':
            print('Detected temperature set action!')
            _validate_temp_set_action(config, device_config)
        case 'set_temp_blind':
            print('Detected blind temeprature set action!')
            _validate_blind_temp_set_action(config, device_config)
        case 'gas_ctrl':
            print('Detected gas controller action!')
            _validate_massflow_action(config, device_config)
        case 'trigger':
            print('Detected triggerbox action!')
            _validate_triggerbox_action(config, device_config)
        case 'multiplexer':
            print('Detected multiplexer action!')
            _validate_multiplexer_action(config, device_config)
        case _:
            delayed_exit(f'Invalid action type encountered: {config['type']}!'
                         f'Valid action types are: {', '.join(valid_actions)}', 1)


def _validate_massflow_action(config: dict, devices: dict) -> None:
    _check_device_exists_and_type(config, 'flow_controller', devices)

    for inner_key, inner_value in config.items():
        if inner_key in ['flow_controller', 'type']:
            continue
        if not re.compile(r'^flow_[1-4]$').match(inner_key):
            delayed_exit(f'Invalid channel encounterd: {inner_key}!'
                         f' Valid channels are: flow_1, flow_2, flow_3 and flow_4!')
        if not isinstance(inner_value, (int, float)) or inner_value < 0 or inner_value > 100:
            delayed_exit(f'Invalid value encountered for channel {inner_key}: {inner_value}!'
                         f' Valid values are: 0 to 100')

    print('Gas control action validated sucessfully!')


def _validate_triggerbox_action(config: dict, devices: dict) -> None:
    _check_device_exists_and_type(config, 'triggerbox', devices)

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


def _validate_multiplexer_action(config: dict, devices: dict) -> None:
    _check_device_exists_and_type(config, 'multiplexer', devices)

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


def _validate_temp_set_action(config: dict, devices: dict) -> None:
    _check_device_exists_and_type(config, 'heater', devices)
    _check_device_exists_and_type(config, 'temp_sensor', devices)
    _check_value_exists_bounds(config, 't_set', -200, 1500)
    _check_value_exists_bounds(config, 'delta_temp', 0.01, 100)
    _check_value_exists_bounds(config, 'delta_time', 1, 1E6)
    _check_value_exists_bounds(config, 'time_res', 1, 100)

    print('Temperature set action validated sucessfully!')


def _validate_blind_temp_set_action(config: dict, devices: dict) -> None:
    _check_device_exists_and_type(config, 'heater', devices)
    _check_value_exists_bounds(config, 't_set', -200, 1500)

    print('Blind temperature set action validated sucessfully!')


def _validate_list_action(whole_config: dict, config: dict) -> None:
    """
    The lsit action is a meta-action that iterates over a list of actions.
    Therefore, the validation function needs to know about the entire config.
    :arg whole_config: The whole config
    :arg config: The list action config
    """
    if 'action_ids' not in config:
        delayed_exit(f'Missing entry actions in action preset!', 1)
    if not isinstance(config['action_ids'], list):
        delayed_exit(f'Invalid entry actions in action preset! Expected list, got {type(whole_config["actions"])}', 1)
    if not config['action_ids'][:len(config['processed_actions'])] == config['processed_actions']:
        delayed_exit(f'Processed actions list does not match with beginning of action_ids list!', 1)
    for action_id in config['action_ids']:
        if action_id not in whole_config['actions']:
            delayed_exit(f'Action with id {action_id} not found in config file!', 1)

    print('List action validated sucessfully!')


def _check_value_exists_bounds(config, key, min_value, max_value):
    if key not in config:
        delayed_exit(f'Missing entry {key} in action preset!', 1)

    if not isinstance(config[key], (int, float)) or config[key] < min_value or config[key] > max_value:
        delayed_exit(f'Invalid value encountered for {key}: {config[key]}!'
                     f' Valid values are: {min_value} to {max_value}')


def _check_device_exists_and_type(action_config, device_type, device_config):
    if device_type not in action_config:
        delayed_exit(f'Missing entry {device_type} in action preset!', 1)

    if action_config[device_type] not in device_config:
        delayed_exit(f'Specified {device_type} {action_config[device_type]} not defined in device section!',
                     1)

    device = device_config[action_config[device_type]]
    if device['device'] not in valid_devices[device_type]:
        delayed_exit(f'Specified {device_type} {device} is not a valid {device_type} device!'
                     f'Valid devices are: {', '.join(valid_devices[device_type])}',
                     1)


if __name__ == '__main__':
    import file_load

    test_config = file_load.load_config('../test_command_definition.yaml')
    validate_config(test_config)

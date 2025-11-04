import re
import time

from minimalmodbus import ModbusException, InvalidResponseError, IllegalRequestError, NoResponseError, Instrument
from serial import SerialException, Serial

from src.helpers.devices import devices
from src.helpers.exit import delayed_exit


def execute_massflow_action(action_config: dict, devices_config: dict) -> None:
    device = _safe_connect_device(action_config, devices_config, 'flow_controller')

    for channel, value in action_config.items():
        if channel in ['type', 'flow_controller']:
            continue
        _chan = int(re.fullmatch(r'^flow_(\d+)$', channel).group()[1])
        try:
            device.set_flow(int(channel), value)
        except SerialException as e:
            delayed_exit(f'Communication error when setting flow on channel {channel}: {e}')
        else:
            print(f'Set channel {_chan} to {value} %')

    try:
        device.close()
    except SerialException as e:
        delayed_exit(f'Communication error when closing flow_controller: {e}')


def execute_triggerbox_action(action_config: dict, devices_config: dict) -> None:
    device = _safe_connect_device(action_config, devices_config, 'triggerbox')

    for channel, value in action_config.items():
        if channel in ['type', 'triggerbox']:
            continue
        _chan = int(re.fullmatch(r'^state_(\d+)$', channel).group()[1])
        try:
            device.switch_valve(int(channel), value)
        except SerialException as e:
            delayed_exit(f'Communication error when setting flow on channel {channel}: {e}')
        else:
            print(f'Set channel {_chan} to {value} %')

    try:
        device.close()
    except SerialException as e:
        delayed_exit(f'Communication error when closing triggerbox: {e}')


def execute_multiplexer_action(action_config: dict, devices_config: dict) -> None:
    device = _safe_connect_device(action_config, devices_config, 'multiplexer')

    for channel, value in action_config.items():
        if channel in ['type', 'triggerbox']:
            continue
        pattern = r"^L([1-4])R([1-4])$"
        n, m = re.match(pattern, channel).groups()
        try:
            device.set_single_relay((int(n), int(m)), value)
        except SerialException as e:
            delayed_exit(f'Communication errorm when switch relay {channel}: {e}')
        else:
            print(f'Set relay {channel} to {value} %')

    try:
        device.close()
    except SerialException as e:
        delayed_exit(f'Communication error when closing triggerbox: {e}')


def execute_blind_temperature_action(action_config: dict, devices_config: dict) -> None:
    device = _safe_connect_device(action_config, devices_config, 'heater')
    try:
        device.set_target_setpoint(action_config['t_set'])
    except (SerialException, InvalidResponseError, IllegalRequestError, NoResponseError, ModbusException) as e:
        delayed_exit(f'Communication error when setting target temperature: {e}')

    try:
        if isinstance(device, Serial):
            device.close()
        elif isinstance(device, Instrument):
            device.serial.close()
    except SerialException as e:
        delayed_exit(f'Communication error when closing heater: {e}')


def execute_temperature_action(action_config: dict, devices_config: dict) -> None | float:
    heater = _safe_connect_device(action_config, devices_config, 'heater')
    sensor = _safe_connect_device(action_config, devices_config, 'temp_sensor')

    try:
        heater.set_target_setpoint(action_config['t_set'])
    except (SerialException, InvalidResponseError, IllegalRequestError, NoResponseError, ModbusException) as e:
        delayed_exit(f'Communication error when setting target temperature: {e}')
    else:
        print(f'Temperature set to {action_config["t_set"]}!')

    delta_time = action_config['delta_time']
    delta_temp = action_config['delta_temp']
    time_res = action_config['time_res']
    time_of_last_reading = time.time()
    time_remaining = delta_time

    print('Waiting for temperature to stabilize!')
    print(f'Checking temperature every {time_res} seconds!')
    print(f'Waiting until the temperature changes by less than {delta_temp} °C over {delta_time} seconds!')

    try:
        last_sensor_temp = sensor.get_sensor_value()
    except SerialException as e:
        delayed_exit(f'Communication error when reading temperature: {e}')
    else:
        while time_remaining > 0:
            if time.time() - time_of_last_reading > time_res:
                try:
                    sensor_temp = sensor.get_sensor_value()
                    print(f'Current sensor temeprature: {sensor_temp}')
                except SerialException as e:
                    delayed_exit(f'Communication error when reading temperature: {e}')
                else:
                    time_of_last_reading = time.time()
                    if abs(sensor_temp - last_sensor_temp) > delta_temp:
                        print(f'Temperature deviation larger than {delta_temp}! Resetting countdown!')
                        time_remaining = delta_time
                    else:
                        time_remaining -= time_res
                        print(f'Time remaining: {time_remaining} seconds!')
        else:
            print('Temperature stabilized!')
        try:
            if isinstance(heater, Serial):
                heater.close()
            elif isinstance(heater, Instrument):
                heater.serial.close()
            sensor.close()
        except SerialException as e:
            delayed_exit(f'Communication error when closing heater: {e}')

    try:
        sensor_temp = sensor.get_sensor_value()
        print(f'Current sensor temeprature: {sensor_temp}')
        return sensor_temp
    except SerialException as e:
        delayed_exit(f'Communication error when reading temperature: {e}')


def _safe_connect_device(action_config: dict, devices_config: dict, dev_type: str):
    dev_id = action_config[dev_type]
    dev_class = devices[dev_type][devices_config[dev_id]['device']]
    dev_port = devices_config[dev_id]['port']
    print(f'Connecting {dev_id} at {dev_port}...')
    try:
        device = dev_class(dev_port)
    except SerialException:
        delayed_exit(f'Error connecting {dev_id} at {dev_port}!', 1)
    else:
        print('Device connection successful!')
        return device

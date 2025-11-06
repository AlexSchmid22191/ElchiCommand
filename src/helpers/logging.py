import datetime
from pathlib import Path

from platformdirs import user_config_dir

from src.helpers.exit import delayed_exit


def log_message(message):
    log_dir = Path(user_config_dir('ElchiCommander', 'ElchWorks', roaming=True))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f'log_{datetime.datetime.now().strftime("%Y-%m-%d")}.txt'
    try:
        with open(log_path, 'a') as file:
            file.write(f'{datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")}, ')
            file.write(f'{datetime.datetime.now(datetime.UTC).timestamp()}: ')
            file.write(f'{message}\n')
    except PermissionError:
        delayed_exit(f'Error: Permission denied reading: {log_path}', 1)
    except OSError as e:
        delayed_exit(f'Error reading {log_path}: {e}', 1)


def log_action(action_id: int, action_config: dict):
    message = f'Executing action {action_id}: '
    match action_config['type']:
        case 'set_temp':
            message += (f'Setting temeprature of {action_config['heater']} to {action_config['t_set']}'
                        f' and wait until the temperature of {action_config['temp_sensor']} changes by less than'
                        f' {action_config['delta_temp']} for {action_config['delta_time']} seconds!')
        case 'set_temp_blind':
            message += f'Setting temeprature of {action_config["heater"]} to {action_config["t_set"]}!'
        case 'trigger':
            message += f'Setting triigerbox {action_config['triggerbox']} to:'
            message += ', '.join(f'{key}: {value}' for key, value in action_config.items()
                                 if key not in ['type', 'triggerbox'])
        case 'gas_ctrl':
            message = f'Setting flow controller {action_config['flow_controller']} to:'
            message += ', '.join(f'{key}: {value}' for key, value in action_config.items()
                                 if key not in ['type', 'flow_controller'])
        case 'multiplexer':
            message = f'Setting multiplexer {action_config['multiplexer']} to:'
            message += ', '.join(f'{key}: {value}' for key, value in action_config.items()
                                 if key not in ['type', 'multiplexer'])
        case _:
            # Should be unreachable as the config was validated before
            delayed_exit(f'Invalid action type encountered: {action_config["type"]}', 1)
    log_message(message)


def log_actual_temeprature(setpoint: float, actual_temp: float):
    log_dir = Path(user_config_dir('ElchiCommander', 'ElchWorks', roaming=True))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f'temperature_log_{datetime.datetime.now().strftime("%Y-%m-%d")}.txt'
    try:
        with open(log_path, 'a') as file:
            file.write(f'{datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")}, ')
            file.write(f'{datetime.datetime.now(datetime.UTC).timestamp()}, ')
            file.write(f'{setpoint:.2f}, {actual_temp:.2f}\n')
    except PermissionError:
        delayed_exit(f'Error: Permission denied reading: {log_path}', 1)
    except OSError as e:
        delayed_exit(f'Error reading {log_path}: {e}', 1)


def log_error(error_message: str):
    log_dir = Path(user_config_dir('ElchiCommander', 'ElchWorks', roaming=True))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f'log_{datetime.datetime.now().strftime("%Y-%m-%d")}.txt'
    try:
        with open(log_path, 'a') as file:
            file.write(f'{datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")}, ')
            file.write(f'{datetime.datetime.now(datetime.UTC).timestamp()}: ')
            file.write(f'ERROR: {error_message}\n')
    except PermissionError:
        # Print statements are used here to abvoid infinite recursion when called from delayed_exit
        print(f'Error: Permission denied reading: {log_path}', 1)
    except OSError as e:
        # Print statements are used here to abvoid infinite recursion when called from delayed_exit
        print(f'Error reading {log_path}: {e}', 1)

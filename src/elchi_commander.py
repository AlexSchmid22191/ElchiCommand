import argparse
from argparse import ArgumentError
from pathlib import Path

from platformdirs import user_config_dir

from src.helpers.execute_action import (execute_massflow_action, execute_triggerbox_action,
                                        execute_multiplexer_action, execute_temperature_action,
                                        execute_blind_temperature_action)
from src.helpers.exit import delayed_exit, report_sucess
from src.helpers.file_load import load_config
from src.helpers.validate import validate_config
from src.helpers.logging import log_action, log_actual_temeprature, log_message


def main() -> None:
    print('Hi! This is ElchiCommander!')
    log_message('ElchiCommander started!')
    parser = argparse.ArgumentParser(description='ElchiCommander is a CLI application for experiment control!'
                                                 ' It can execute actions defined in a configuration file!',
                                     exit_on_error=False)
    parser.add_argument('action_id', type=int, help='The action to execute. Actions are defined in the config file.')

    try:
        args = parser.parse_args()
    except ArgumentError as e:
        delayed_exit(f'Invalid command line arguments, {e}')
    else:
        if args.action_id < 1:
            delayed_exit('Invalid action id! Valid action ids are positive integers!')
        else:
            log_message(f'Action {args.action_id} requested!')
            print(f'Action {args.action_id} requested!')

        config_dir = Path(user_config_dir('ElchiCommander', 'ElchWorks', roaming=True))
        config_dir.mkdir(parents=True, exist_ok=True)

        config = load_config(config_dir / 'config.yaml')
        validate_config(config)
        log_message('Config loaded and validated successfully!')

        device_config = config.get('devices')
        action_config = config.get('actions').get(args.action_id)
        if action_config is None:
            delayed_exit(f'Action with id {args.action_id} not found in config file!')
        else:
            print(f'Executing action {args.action_id}...')

        match action_config['type']:
            case 'gas_ctrl':
                log_action(args.action_id, action_config)
                execute_massflow_action(action_config, device_config)
            case 'triggerbox':
                log_action(args.action_id, action_config)
                execute_triggerbox_action(action_config, device_config)
            case 'multiplexer':
                log_action(args.action_id, action_config)
                execute_multiplexer_action(action_config, device_config)
            case 'set_temp':
                log_action(args.action_id, action_config)
                final_sensor_temp = execute_temperature_action(action_config, device_config)
                log_actual_temeprature(action_config['t_set'], final_sensor_temp)
                log_message(f'Temeprature stable: {final_sensor_temp}')
            case 'set_temp_blind':
                log_action(args.action_id, action_config)
                execute_blind_temperature_action(action_config, device_config)
            case _:
                # This should never be reached as the config was validated before
                delayed_exit(f'Invalid action type encountered: {action_config['type']}!')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        delayed_exit(f'Un unexpected error occured: {e}')
    else:
        log_message(f'Action executed successfully!')
        log_message(f'ElchiCommander finished!')
        report_sucess()

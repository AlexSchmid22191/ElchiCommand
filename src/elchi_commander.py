import argparse
import traceback
from argparse import ArgumentError
from pathlib import Path

from platformdirs import user_config_dir

from src.helpers.execute_action import execute_action
from src.helpers.exit import delayed_exit, report_success
from src.helpers.file_load import load_config
from src.helpers.logging import log_message
from src.helpers.validate import validate_config


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

        execute_action(args.action_id, config)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        delayed_exit(f'An unexpected error occurred: {ex}\n Traceback: {traceback.format_exc()}')
    else:
        log_message(f'Action executed successfully!')
        log_message(f'ElchiCommander finished!')
        report_success()

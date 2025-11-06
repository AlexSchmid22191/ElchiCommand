import datetime
from pathlib import Path

from platformdirs import user_config_dir


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

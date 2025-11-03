from src.helpers.exit import delayed_exit
from pathlib import Path
from typing import Dict
import yaml


def load_config(config_path: str | Path) -> Dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        delayed_exit(f'Error: Config file not found: {config_path}', 1)
    except PermissionError:
        delayed_exit(f'Error: Permission denied reading: {config_path}', 1)
    except OSError as e:
        delayed_exit(f'Error reading {config_path}: {e}', 1)
    if not isinstance(config, dict):
        delayed_exit('Error: Invalid config format!')

    print(f'I read the following configuration from {config_path}:')
    for k, v in config.items():
        print(f"{k}: {v}")

    return config

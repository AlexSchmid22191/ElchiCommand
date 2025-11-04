from pathlib import Path
from typing import Dict
import yaml
import yaml.scanner

from src.helpers.exit import delayed_exit


def load_config(config_path: str | Path) -> Dict:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        delayed_exit(
            f'Error: Config file not found: {config_path}! You can execute make_default_config.bat'
            f' in the installation folder to create a default one!', 1)
    except yaml.scanner.ScannerError as e:
        delayed_exit(f'Error: Invalid YAML syntax in config file: {e}!'
                     f' Consult the specification in the colab or execute make_default_config.bat'
                     f' in the installation folder to create a default one!', 1)
    except PermissionError:
        delayed_exit(f'Error: Permission denied reading: {config_path}', 1)
    except OSError as e:
        delayed_exit(f'Error reading {config_path}: {e}', 1)
    if not isinstance(config, dict):
        delayed_exit(
            'Error: Invalid config format! Consult the specification in the colab or execute make_default_config.bat'
            f' in the installation folder to create a default one!')

    print(f'I read the following configuration from {config_path}:')
    print(yaml.dump(config, default_flow_style=False, default_style=''))

    return config

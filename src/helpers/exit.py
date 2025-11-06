import sys
import time
from src.helpers.logging import log_error
from colorama import just_fix_windows_console, Fore, Style

just_fix_windows_console()


def delayed_exit(message: str, error_code=0):
    print(Fore.RED + message)
    print(Fore.YELLOW + 'Press enter to exit!')
    print(Style.RESET_ALL)
    log_error(message)
    input()
    sys.exit(error_code)


def report_sucess():
    print('Done, exiting in 5 seconds!')
    for i in range(5):
        print(f'{5 - i} ...')
        time.sleep(1)

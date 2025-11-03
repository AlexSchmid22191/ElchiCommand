import sys
import time


def delayed_exit(message: str, error_code=0):
    print(message)
    print('Press enter to exit!')
    input()
    sys.exit(error_code)


def report_sucess():
    print('Done, exiting in 5 seconds!')
    for i in range(5):
        print(f'{5 - i} ...')
        time.sleep(1)

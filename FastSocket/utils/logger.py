class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class Logger:
    def print_log_error(log: str, instance: str) -> None:
        print(Color.RED + f'[{instance}]' + Color.END + f': {log}')

    def print_log_normal(log: str, instance: str) -> None:
        print(Color.GREEN + f'[{instance}]' + Color.END + f': {log}')

    def print_log_debug(log: str) -> None:
        print(Color.YELLOW + f'[DEBUG]' + Color.END + f': {log}')
        
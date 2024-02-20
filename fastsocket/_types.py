from typing import Literal, Type, Tuple, List
import socket

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


class Types:
    ADDRESS_FAMILY_IP_V4 = socket.AddressFamily.AF_INET

    TCP_STREAM_TYPE = socket.SocketKind.SOCK_STREAM 
    
    CONNECTION = socket.socket

    IPV4_PORT = Tuple[str, int]

    
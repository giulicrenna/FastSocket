from typing import Literal, Type, Tuple, List
import socket

class Types:
    ADDRESS_FAMILY_IP_V4 = socket.AddressFamily.AF_INET

    TCP_STREAM_TYPE = socket.SocketKind.SOCK_STREAM 
    
    CONNECTION = socket.socket

    IPV4_PORT = Tuple[str, int]

    
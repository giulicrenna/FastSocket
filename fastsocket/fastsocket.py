from typing import Literal, Type, Tuple, List, Callable
from threading import Thread
from queue import Queue

import socket
import os

from _types import *
from _expt import *

def print_log_error(log: str, instance: str) -> None:
    print(Color.RED + f'[{instance}]' + Color.END + f': {log}')

def print_log_normal(log: str, instance: str) -> None:
    print(Color.GREEN + f'[{instance}]' + Color.END + f': {log}')

class ClientType(Thread):
    def __init__(self,
                 connection: Types.CONNECTION,
                 address: Types.IPV4_PORT) -> None:
        super().__init__()
        self.connection: Types.CONNECTION = connection
        self.address: Types.IPV4_PORT = address
        self.message_queue: Queue = Queue()
        self.connected: bool = True
        
    def run(self):
        while True:
            try:
                data = self.connection.recv(1024)
                if data:
                    message = data.decode("utf-8")
                    self.message_queue.put((message, self.address))
            except:
                self.connected = False
                self.connection.close()
        
class SockerConfig:
    def __init__(self,
                 host: str = 'localhost',
                 port: int = 7654,
                 family: Literal[Types.ADDRESS_FAMILY_IP_V4] = socket.AF_INET,
                 type: Literal[Types.TCP_STREAM_TYPE] = socket.SOCK_STREAM,
                 reuse_address: bool = True) -> None:
        
        self.host = host
        self.port = port
        self.family = family
        self.type = type
        self.reuse_address: bool = reuse_address
        
    def _create_socket(self) -> Types.CONNECTION:
        sock: Types.CONNECTION = socket.socket(self.family,
                             self.type)

        if self.reuse_address: sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
        return sock
        
class FastSocketServer(Thread):
    def __init__(self,
                 config: SockerConfig) -> None:
        super().__init__()
        self._config = config
        self._client_buffer: List[ClientType] = []
        self._new_message_handler: List[Callable] = []
        
    def run(self) -> None:
        print_log_normal(f'Running server on {self._config.host}:{self._config.port}', 'Server')
        self.sock: Types.CONNECTION = self._config._create_socket()
        self.sock.bind((self._config.host, self._config.port))
        
        task_wait_for_client = Thread(target=self._listen_for_new_clients)
        task_wait_for_client.start()
        for _message_handler in self._new_message_handler:
            message_thread = Thread(target=self._run_new_message_handler, args=(_message_handler,))
            message_thread.start()
        
    def _listen_for_new_clients(self) -> None:
        while True:
            self.sock.settimeout(5)
            self.sock.listen()
        
            try:
                for idx, client in enumerate(self._client_buffer):
                    if not client.connected:
                        del self._client_buffer[idx]
                        
                conn, addr = self.sock.accept()
                
                client_handler = ClientType(conn, addr)
                client_handler.start()
                
                self._client_buffer.append(client_handler)
            except socket.timeout:
                pass
    
    def on_new_message(self, func: Callable) -> None:
        self._new_message_handler.append(func)
        
    def _run_new_message_handler(self, _func: Callable) -> None:
        while True:
            for client in self._client_buffer:
                if client.connected:
                    _func(client.message_queue)
                    
    def send_msg_stream(self, message: str | bytes) -> None:
        if type(message) not in [str, bytes]:
            raise InvalidMessageType
        for idx, client in enumerate(self._client_buffer):
            try:
                if type(message) == bytes:
                    client.connection.sendall(message)
                elif type(message) == str:
                    client.connection.sendall(message.encode())
            except OSError:
                del self._client_buffer[idx]
                
if __name__ == '__main__':
    import time
    import random
    
    def print_msg(messages: Queue):
        while not messages.empty():
            msg, addr = messages.get()
            server.send_msg_stream(f'ECHO: {msg}, your IP is {addr}\n')
            print(f'{msg} from {addr[0]}')

    config = SockerConfig(host='192.168.0.104',
                          port=8080)
    
    server = FastSocketServer(config)
    
    server.on_new_message(print_msg)
    
    server.start()


    while True:
        server.send_msg_stream(f'{random.randint(90000,9999999999)}\n')
        time.sleep(.3)
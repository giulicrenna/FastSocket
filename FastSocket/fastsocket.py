from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Signature import PKCS1_v1_5

from typing import Literal, Mapping, Type, Tuple, List, Callable
from threading import Thread
from queue import Queue

import socket

if __name__ == '__main__':
    from _types import *
    from _expt import *
    from security import RSAEncryption
    from logger import Logger
else:
    from FastSocket._types import *
    from FastSocket._expt import *
    from FastSocket.security import RSAEncryption
    from FastSocket.logger import Logger

class ClientType(Thread):
    def __init__(self,
                 connection: Types.CONNECTION,
                 address: Types.IPV4_PORT,
                 recv_size: int,
                 server_security: RSAEncryption) -> None:
        super().__init__()
        self.connection: Types.CONNECTION = connection
        self.address: Types.IPV4_PORT = address
        self.message_queue: Queue = Queue()
        self.connected: bool = True
        self.full_reached: bool = False
        self._recv_size = recv_size
        self.public_key: RSA.RsaKey = None
        self.server_security = server_security
        
    def run(self):
        while True:
            try:
                if self.public_key is None:
                    try:
                        pub_key_bytes = self.connection.recv(self._recv_size)
                        self.public_key = RSA.import_key(pub_key_bytes)
                        Logger.print_log_debug(self.public_key)
                    except:
                        self.connection.sendall(f'Invalid Public Key'.encode('utf-8'))
                else:
                    data: bytes = self.connection.recv(self._recv_size)
                    if data:
                        message = self.server_security.decrypt(data)
                        self.message_queue.put((message, self.address))
                self.connected = True
            except Exception as e:
                Logger.print_log_error(e, 'ClientType')
                self.connected = False
                self.connection.close()
                break

class SockerConfig:
    def __init__(self,
                 host: str = 'localhost',
                 port: int = 7654,
                 family: Types.ADDRESS_FAMILY_IP_V4 = socket.AF_INET,
                 type: Types.TCP_STREAM_TYPE = socket.SOCK_STREAM,
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
                 config: SockerConfig,
                 pub_key_path: str,
                 priv_key_path: str,
                 _recv_size: int = 1024*10) -> None:
        
        super().__init__()
        self._config = config
        self._client_buffer: List[ClientType] = []
        self._new_message_handler: List[Callable] = []
        self._recv_size = _recv_size
        
        Logger.print_log_debug('Loading RSA key pair.')
        self._security = RSAEncryption(pub_key_path, priv_key_path)
        Logger.print_log_debug('RSA key pair loaded succesfully.')
        
    def run(self) -> None:
        Logger.print_log_normal(f'Running server on {self._config.host}:{self._config.port}', 'Server')
        self.sock: Types.CONNECTION = self._config._create_socket()
       
        try:
            self.sock.bind((self._config.host, self._config.port))
        except OSError:
            raise NetworkException
        
        task_send_pub_key = Thread(target=self._send_server_pub_key, name="_send_server_pub_key")
        task_send_pub_key.start()
        
        task_wait_for_client = Thread(target=self._listen_for_new_clients)
        task_wait_for_client.start()
        
        for _message_handler in self._new_message_handler:
            message_thread = Thread(target=self._run_new_message_handler, args=(_message_handler,))
            message_thread.start()
            
    def _send_server_pub_key(self) -> None:
        while True:
            for client in self._client_buffer:
                if client.public_key is not None and self._security.pub_key is not None and not client.full_reached:
                    client.connection.sendall(self._security.pub_key.export_key())
                    client.full_reached = True
    
    def _listen_for_new_clients(self) -> None:
        while True:
            self.sock.settimeout(5)
            self.sock.listen()
        
            try:
                for idx, client in enumerate(self._client_buffer):
                    if not client.connected:
                        del self._client_buffer[idx]
                        
                conn, addr = self.sock.accept()
                
                client_handler = ClientType(conn, addr, self._recv_size, self._security)
                client_handler.connection.sendall(f'Send public key with size: 4096 bytes\n'.encode('utf-8'))
                client_handler.start()
                
                self._client_buffer.append(client_handler)
            except socket.timeout:
                pass
    
    def on_new_message(self, func: Callable) -> None:
        self._new_message_handler.append(func)
        
    def _run_new_message_handler(self, _func: Callable) -> None:
        while True:
            for client in self._client_buffer:
                if client.connected and not client.message_queue.empty():
                    _func(client.message_queue)
                    
    def send_msg_stream(self, message: str | bytes) -> None:
        if type(message) not in [str, bytes]:
            raise InvalidMessageType
        for idx, client in enumerate(self._client_buffer):
            try:
                if client.full_reached and client.connected:
                    client.connection.sendall(self._security.encrypt(message, client.public_key))
            except OSError:
                pass
                
class FastSocketClient(Thread):
    def __init__(self,
                 config: SockerConfig,
                 pub_key_path: str,
                 priv_key_path: str,
                 _recv_size: int = 1024*10) -> None:
        super().__init__()
        self._config = config
        self._new_message_handler: List[Callable] = []
        self._recv_size = _recv_size
        self.server_pub_key: RSA.RsaKey = None
        
        Logger.print_log_debug('Loading RSA key pair.')
        self._security = RSAEncryption(pub_key_path, priv_key_path)
        Logger.print_log_debug('RSA key pair loaded succesfully.')
        
    def run(self) -> None:
        Logger.print_log_normal(f'Running server on {self._config.host}:{self._config.port}', 'Server')
        self.sock: Types.CONNECTION = self._config._create_socket()
        self.sock.connect((self._config.host, self._config.port))

        ord: bytes = self.sock.recv(self._recv_size)
        self.sock.sendall(self._security.pub_key.export_key())
        
        self.server_pub_key = RSA.import_key(self.sock.recv(self._recv_size))
        
        for _message_handler in self._new_message_handler:
            message_thread = Thread(target=self._run_new_message_handler, args=(_message_handler,))
            message_thread.start()
            
    def send_to_server(self, msg: str) -> None:
        if self.server_pub_key is None:
            return
        try:
            cipher = PKCS1_OAEP.new(self.server_pub_key)
            message = cipher.encrypt(msg.encode('utf-8'))

            self.sock.sendall(message)
        except Exception as e:
            Logger.print_log_error(e, 'FastSocketClient')
            raise e
            
    def on_new_message(self, func: Callable) -> None:
        self._new_message_handler.append(func)
        
    def _run_new_message_handler(self, _func: Callable) -> None:
        while True:
            try:
                msg = self.sock.recv(self._recv_size)
                cipher = PKCS1_OAEP.new(self._security.priv_key)
                decrypted_msg = cipher.decrypt(msg).decode('utf-8')
                _func(decrypted_msg)
            except Exception as e:
                Logger.print_log_error(e, 'FastSocketClient')
                raise e
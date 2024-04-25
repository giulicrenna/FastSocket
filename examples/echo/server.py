from FastSocket.fastsocket import FastSocketServer, SockerConfig, Queue
import os
import random

PUB_KEY_PATH: str = os.path.join('keys', 'pub_key.pem')
PRIV_KEY_PATH: str = os.path.join('keys', 'priv_key.pem') 

def print_msg(messages: Queue):
    while not messages.empty():
        msg, _ = messages.get()
        
        if msg == 'generar random':
            while True:
                server.send_msg_stream(f'\n{random.randint(100000, 9999999999999)}\n')    
        else:
            server.send_msg_stream(f'\nServer -> {msg}\n')
        
if __name__ == '__main__':
    config = SockerConfig(host='192.168.0.16', port=8080)
    
    server = FastSocketServer(config)#, PUB_KEY_PATH, PRIV_KEY_PATH)
    
    server.on_new_message(print_msg)
    
    server.start()
        
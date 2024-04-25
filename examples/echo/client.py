from FastSocket.fastsocket import SockerConfig, FastSocketClient
import os
import time
import random

PUB_KEY_PATH: str = os.path.join('keys', 'pub_key.pem')
PRIV_KEY_PATH: str = os.path.join('keys', 'priv_key.pem') 

def print_msg(message: str):
    print(f'{message.strip()}')
        
if __name__ == '__main__':
    config = SockerConfig(host='192.168.0.16', port=8080)
    
    server = FastSocketClient(config)#, PRIV_KEY_PATH, PUB_KEY_PATH)
    
    server.on_new_message(print_msg)
    
    server.start()

    while True:
        server.send_to_server(f'{random.randint(90000,9999999999)}')
        time.sleep(1)
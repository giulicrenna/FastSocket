from FastSocket.FastSocket import FastSocketClient, SockerConfig
import os
import time
import random

PUB_KEY_PATH: str = os.path.join(os.getcwd(), 'keys', 'pub_key.pem')
PRIV_KEY_PATH: str = os.path.join(os.getcwd(), 'keys', 'priv_key.pem') 

def print_msg(message: str):
    print(f'{message.strip()}')
        
if __name__ == '__main__':
    config = SockerConfig(host='192.168.0.104', port=8080)
    
    server = FastSocketClient(config, PUB_KEY_PATH, PRIV_KEY_PATH)
    
    server.on_new_message(print_msg)
    
    server.start()

    while True:
        server.send_to_server(f'{random.randint(90000,9999999999)}\n')
        time.sleep(1)
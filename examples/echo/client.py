from FastSocket import SocketConfig, FastSocketClient
import os
import time
import random

PUB_KEY_PATH: str = os.path.join('keys', 'pub_key.pem')
PRIV_KEY_PATH: str = os.path.join('keys', 'priv_key.pem')

def print_msg(message: str):
    print(f'{message.strip()}')

if __name__ == '__main__':
    config = SocketConfig(host='192.168.0.16', port=8080)

    client = FastSocketClient(config)

    client.on_new_message(print_msg)

    client.start()

    while True:
        client.send_to_server(f'{random.randint(90000,9999999999)}')
        time.sleep(1)

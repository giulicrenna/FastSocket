from FastSocket.FastSocket import FastSocketServer, SockerConfig, Queue
import os

PUB_KEY_PATH: str = os.path.join(os.getcwd(), 'keys', 'pub_key.pem')
PRIV_KEY_PATH: str = os.path.join(os.getcwd(), 'keys', 'priv_key.pem') 

def print_msg(messages: Queue):
    while not messages.empty():
        msg, _ = messages.get()
        server.send_msg_stream(msg)
        
if __name__ == '__main__':
    config = SockerConfig(host='192.168.0.104', port=8080)
    
    server = FastSocketServer(config, PUB_KEY_PATH, PRIV_KEY_PATH)
    
    server.on_new_message(print_msg)
    
    server.start()
        
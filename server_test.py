from FastSocket.fastsocket import FastSocketServer, SockerConfig, Queue
import random
import time

def print_msg(messages: Queue):
    while not messages.empty():
        msg, _ = messages.get()
        
        if msg == 'generar random':
            server.send_msg_stream(f'\n{random.randint(100000, 9999999999999)}\n')    
        else:
            server.send_msg_stream(f'\nServer -> {msg}\n')

config = SockerConfig('192.168.0.105', 8080)
server = FastSocketServer(config)
server.on_new_message(print_msg)

server.start()

if __name__ == '__main__':
    while True:
        time.sleep(5)
        server.send_msg_stream('Hola\n')
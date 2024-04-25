from FastSocket.fastsocket import SocketConfig, FastSocketClient


def print_msg(message: str):
    print(message)

config = SocketConfig('192.168.1.105', 8080)

client = FastSocketClient(config)

client.on_new_message(print_msg)

client.start()

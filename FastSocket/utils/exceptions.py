class InvalidMessageType(Exception):
    def __init__(self) -> None:
        super().__init__()
    
    def __str__(self) -> str:
        return 'Message has to be a string or a byte array'
    
class NetworkException(Exception):
    def __init__(self) -> None:
        super().__init__()
    
    def __str__(self) -> str:
        return f'Network Exception'
    
class BadEncryptionInput(Exception):
    def __init__(self) -> None:
        super().__init__()
    
    def __str__(self) -> str:
        return f'nvalid message to Encrypt'
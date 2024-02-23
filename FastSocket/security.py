from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

import rsa

from FastSocket.logger import Logger

class RSAEncryption:
    def __init__(self, pub_key_path: str,
                 priv_key_path: str) -> None:
        self.pub_key_path = pub_key_path
        self.priv_key_path = priv_key_path
        
        self.pub_key: RSA.RsaKey = None
        self.priv_key: RSA.RsaKey = None
        
        self._load_pair()
        
    def _generate_pair(self) -> None:
        Logger.print_log_debug('priv_key created succesfully')
        self.priv_key = RSA.import_key(rsa.newkeys(self.encr_size))
        self.pub_key = self.priv_key.publickey()
    
    def _load_pair(self) -> None:
        with open(self.priv_key_path, 'rb') as f:
            self.priv_key = RSA.import_key(f.read())
        with open(self.pub_key_path, 'rb') as f:
            self.pub_key = RSA.import_key(f.read())
            
    def encrypt(self, msg: str | bytes, recipient_pub_key: RSA.RsaKey) -> bytes:
        cipher = PKCS1_OAEP.new(recipient_pub_key)
        if isinstance(msg, str):
            msg = msg.encode('utf-8')
        return cipher.encrypt(msg)
        
    def decrypt(self, ciphertext: bytes) -> str:
        cipher = PKCS1_OAEP.new(self.priv_key)
        decrypted_msg = cipher.decrypt(ciphertext)
        return decrypted_msg.decode('utf-8')

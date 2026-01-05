"""
RSA Encryption module for FastSocket.

This module provides RSA encryption/decryption functionality using PyCryptodome.
"""

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

from FastSocket.utils.logger import Logger


class RSAEncryption:
    """
    RSA encryption handler for secure communication.

    This class manages RSA key pairs and provides encryption/decryption
    functionality using PKCS1_OAEP padding scheme.

    Attributes:
        pub_key (RSA.RsaKey): Public key for encryption
        priv_key (RSA.RsaKey): Private key for decryption
        pub_key_path (str): Path to public key file (optional)
        priv_key_path (str): Path to private key file (optional)

    Example:
        >>> # Generate new key pair
        >>> rsa = RSAEncryption()
        >>> encrypted = rsa.encrypt("Hello", recipient_pub_key)
        >>> decrypted = rsa.decrypt(encrypted)

        >>> # Load from files
        >>> rsa = RSAEncryption('pub.pem', 'priv.pem')
    """

    def __init__(self, pub_key_path: str = None,
                 priv_key_path: str = None) -> None:
        """
        Initialize RSA encryption handler.

        Args:
            pub_key_path: Path to public key PEM file (optional)
            priv_key_path: Path to private key PEM file (optional)

        Note:
            If paths are not provided, a new 4096-bit RSA key pair
            will be generated automatically.
        """
        self.pub_key_path = pub_key_path
        self.priv_key_path = priv_key_path

        self.pub_key: RSA.RsaKey = None
        self.priv_key: RSA.RsaKey = None

        if pub_key_path is not None and priv_key_path is not None:
            self._load_pair()
        else:
            self._generate_pair()

    def _generate_pair(self) -> None:
        """Generate a new 4096-bit RSA key pair."""
        Logger.print_log_debug('Generating new RSA key pair')
        self.priv_key = RSA.generate(4096)
        self.pub_key = self.priv_key.publickey()
        Logger.print_log_debug('RSA key pair generated successfully')

    def _load_pair(self) -> None:
        """Load RSA key pair from PEM files."""
        with open(self.priv_key_path, 'rb') as f:
            self.priv_key = RSA.import_key(f.read())
        with open(self.pub_key_path, 'rb') as f:
            self.pub_key = RSA.import_key(f.read())

    def encrypt(self, msg: str | bytes, recipient_pub_key: RSA.RsaKey) -> bytes:
        """
        Encrypt a message using recipient's public key.

        Args:
            msg: Message to encrypt (string or bytes)
            recipient_pub_key: Recipient's RSA public key

        Returns:
            bytes: Encrypted ciphertext

        Example:
            >>> rsa = RSAEncryption()
            >>> encrypted = rsa.encrypt("secret", other_pub_key)
        """
        cipher = PKCS1_OAEP.new(recipient_pub_key)
        if isinstance(msg, str):
            msg = msg.encode('utf-8')
        return cipher.encrypt(msg)

    def decrypt(self, ciphertext: bytes) -> str:
        """
        Decrypt a message using own private key.

        Args:
            ciphertext: Encrypted message bytes

        Returns:
            str: Decrypted message as string

        Example:
            >>> rsa = RSAEncryption()
            >>> decrypted = rsa.decrypt(encrypted_data)
        """
        cipher = PKCS1_OAEP.new(self.priv_key)
        decrypted_msg = cipher.decrypt(ciphertext)
        return decrypted_msg.decode('utf-8')

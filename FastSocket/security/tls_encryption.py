"""
Hybrid encryption utilities for FastSocket.

RSA-4096 is used only for key exchange. After the handshake,
all messages use AES-256-GCM which is fast and provides both
confidentiality and integrity (via the authentication tag).
"""

import os
import hmac
import hashlib

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP


NONCE_SIZE = 16   # AES-GCM nonce
TAG_SIZE   = 16   # AES-GCM authentication tag
HMAC_SIZE  = 32   # HMAC-SHA256 output
RSA_BLOCK  = 512  # ciphertext size for RSA-4096

# PBKDF2 parameters for PSK derivation
_PSK_SALT       = b'fastsocket-psk-v2'
_PSK_ITERATIONS = 50_000


def derive_psk(raw_secret: bytes) -> bytes:
    """
    Derive a strong 32-byte key from a potentially weak PSK.

    Uses PBKDF2-SHA256 so short or low-entropy passphrases are hardened
    before they reach HMAC.  Both client and server must call this with
    the same raw_secret; mismatched derivation = AUTH_FAIL.
    """
    return hashlib.pbkdf2_hmac('sha256', raw_secret, _PSK_SALT, _PSK_ITERATIONS)


def generate_session_key() -> bytes:
    """Return 32 cryptographically random bytes (AES-256 key)."""
    return os.urandom(32)


def aes_encrypt(key: bytes, plaintext: bytes) -> bytes:
    """
    AES-256-GCM encrypt.
    Returns nonce(16) + tag(16) + ciphertext — ready to send as one blob.
    """
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return cipher.nonce + tag + ciphertext


def aes_decrypt(key: bytes, data: bytes) -> bytes:
    """
    AES-256-GCM decrypt and verify.
    Raises ValueError if the tag doesn't match (tampered data).
    """
    nonce      = data[:NONCE_SIZE]
    tag        = data[NONCE_SIZE:NONCE_SIZE + TAG_SIZE]
    ciphertext = data[NONCE_SIZE + TAG_SIZE:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


def hmac_sign(secret: bytes, data: bytes) -> bytes:
    """Compute HMAC-SHA256(secret, data)."""
    return hmac.new(secret, data, hashlib.sha256).digest()


def hmac_verify(secret: bytes, data: bytes, signature: bytes) -> bool:
    """Constant-time HMAC verification to prevent timing attacks."""
    return hmac.compare_digest(hmac_sign(secret, data), signature)


def rsa_encrypt_key(pub_key: RSA.RsaKey, session_key: bytes) -> bytes:
    """Encrypt a session key with an RSA public key (PKCS1-OAEP)."""
    return PKCS1_OAEP.new(pub_key).encrypt(session_key)


def rsa_decrypt_key(priv_key: RSA.RsaKey, encrypted_key: bytes) -> bytes:
    """Decrypt a session key with an RSA private key (PKCS1-OAEP)."""
    return PKCS1_OAEP.new(priv_key).decrypt(encrypted_key)

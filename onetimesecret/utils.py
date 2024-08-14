import os
from base64 import urlsafe_b64decode, urlsafe_b64encode
from string import ascii_letters, digits

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


SELECTION = ascii_letters + digits


def derive_key(master_key: bytes, salt: bytes) -> bytes:
    """
    Derives a symmetric encryption key from the master_key and salt using PBKDF2HMAC.
    Args:
        master_key (bytes): The master key used to derive the encryption key.
        salt (bytes): A random salt to add uniqueness to the key derivation.
    Returns:
        bytes: A derived symmetric encryption key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    return urlsafe_b64encode(kdf.derive(master_key))


def encrypt(data: str, master_key: bytes) -> str:
    """
    Encrypts data using the master_key.
    Args:
        data (str): The data to be encrypted.
        master_key (bytes): The master key used to encrypt the data.
    Returns:
        str: The encrypted data in base64 encoded format, including the salt.
    """
    salt = os.urandom(16)
    key = derive_key(master_key, salt)
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return urlsafe_b64encode(salt + encrypted_data).decode()


def decrypt(encrypted_data: str, master_key: bytes) -> str:
    """
    Decrypts data using the master_key.
    Args:
        encrypted_data (str): The encrypted data to be decrypted.
        master_key (bytes): The master key used to decrypt the data.
    Returns:
        str: The decrypted data.
    """
    data = urlsafe_b64decode(encrypted_data)
    salt = data[:16]
    encrypted_message = data[16:]
    key = derive_key(master_key, salt)
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode()


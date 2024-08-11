import random
from string import ascii_letters, digits
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode, urlsafe_b64decode
import os

SELECTION = ascii_letters + digits


def generate_secret_key():
    """
    Generates a random secret key consisting of ASCII letters and digits.
    The secret key is a string of 6 characters long,
    randomly selected from the combination of ASCII letters (both lowercase and uppercase) and digits.
    Returns:
        str: A randomly generated secret key of length 6.
    """
    key = ''.join(random.choice(SELECTION) for _ in range(6))
    return key


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
    salt = data[:16]  # Extract the salt from the encrypted data
    encrypted_message = data[16:]
    key = derive_key(master_key, salt)
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode()


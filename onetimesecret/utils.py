from base64 import urlsafe_b64decode, urlsafe_b64encode

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_key_from_passphrase(passphrase: bytes, salt: bytes) -> bytes:
    """
    Generates a cryptographic key from a passphrase and salt.

    Args:
        passphrase (bytes): The passphrase used to derive the key.
        salt (bytes): The salt used in the key derivation function.

    Returns:
        bytes: The derived key encoded in URL-safe base64.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(passphrase)
    return urlsafe_b64encode(key)


def encrypt(secret: str, key: bytes) -> str:
    """
    Encrypts a secret using the provided key.

    Args:
        secret (str): The secret data to be encrypted.
        key (bytes): The encryption key.

    Returns:
        str: The encrypted secret encoded in URL-safe base64.
    """
    f = Fernet(key)
    encrypted_secret = f.encrypt(secret.encode())
    return urlsafe_b64encode(encrypted_secret).decode()


def decrypt(encrypted_secret: str, key: bytes) -> str:
    """
    Decrypts an encrypted secret using the provided key.

    Args:
        encrypted_secret (str): The encrypted secret encoded in URL-safe base64.
        key (bytes): The encryption key.

    Returns:
        str: The decrypted secret as a plain string.

    Raises:
        cryptography.fernet.InvalidToken: If the key is incorrect or the encrypted data is tampered with.
    """
    f = Fernet(key)
    encrypted_secret_bytes = urlsafe_b64decode(encrypted_secret)
    return f.decrypt(encrypted_secret_bytes).decode()

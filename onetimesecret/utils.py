from base64 import urlsafe_b64decode, urlsafe_b64encode

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_key_from_passphrase(passphrase: bytes, salt: bytes) -> bytes:
    """
    Generates a cryptographic key from a passphrase and salt using PBKDF2 with HMAC-SHA256.

    Args:
        passphrase (bytes): The passphrase used to derive the key.
        salt (bytes): The salt used in the key derivation function. It should be a secure, random value.

    Returns:
        bytes: The derived key, encoded in URL-safe base64 format.

    Raises:
        TypeError: If the passphrase or salt are not of type 'bytes'.
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
        secret (str): The plaintext secret data to be encrypted.
        key (bytes): The encryption key, derived from the passphrase.

    Returns:
        str: The encrypted secret, encoded in URL-safe base64 format.

    Raises:
        TypeError: If the secret is not a string or the key is not of type 'bytes'.
        cryptography.fernet.InvalidToken: If the key is invalid.
    """
    f = Fernet(key)
    encrypted_secret = f.encrypt(secret.encode())
    return urlsafe_b64encode(encrypted_secret).decode()


def decrypt(encrypted_secret: str, key: bytes) -> str:
    """
    Decrypts an encrypted secret using the provided key.

    Args:
        encrypted_secret (str): The encrypted secret, encoded in URL-safe base64 format.
        key (bytes): The decryption key, derived from the passphrase.

    Returns:
        str: The decrypted secret as a plain string.

    Raises:
        cryptography.fernet.InvalidToken: If the key is incorrect or the encrypted data has been tampered with.
        TypeError: If the encrypted_secret is not a string or the key is not of type 'bytes'.
    """
    f = Fernet(key)
    encrypted_secret_bytes = urlsafe_b64decode(encrypted_secret)
    return f.decrypt(encrypted_secret_bytes).decode()

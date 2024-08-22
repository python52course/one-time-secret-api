import pytest
from base64 import urlsafe_b64decode
from cryptography.fernet import Fernet, InvalidToken
from onetimesecret.utils import generate_key_from_passphrase, encrypt, decrypt


def test_generate_key_from_passphrase():
    """
    Test the key generation function with a given passphrase and salt.

    This test ensures that the key generated from a passphrase and salt has the correct length.
    The key should be URL-safe base64 encoded, resulting in a length of 44 characters.
    """
    passphrase = b"my_secret_passphrase"
    salt = b"my_secret_salt"

    key = generate_key_from_passphrase(passphrase, salt)

    assert len(key) == 44


def test_encrypt_decrypt():
    """
    Test the encryption and decryption functions.

    This test ensures that a secret can be encrypted and then decrypted successfully.
    It checks that the encrypted secret is not the same as the original secret and that
    decrypting the encrypted secret returns the original secret.
    """
    secret = "my_secret_data"
    passphrase = b"my_secret_passphrase"
    salt = b"my_secret_salt"

    key = generate_key_from_passphrase(passphrase, salt)

    encrypted_secret = encrypt(secret, key)

    assert encrypted_secret != secret

    decrypted_secret = decrypt(encrypted_secret, key)

    assert decrypted_secret == secret


def test_decrypt_with_wrong_key():
    """
    Test decryption with a wrong key.

    This test ensures that attempting to decrypt data with an incorrect key raises an `InvalidToken` exception.
    It verifies that encryption with one key and decryption with another key fails.
    """
    secret = "my_secret_data"
    passphrase = b"my_secret_passphrase"
    salt = b"my_secret_salt"
    wrong_passphrase = b"wrong_passphrase"

    key = generate_key_from_passphrase(passphrase, salt)
    wrong_key = generate_key_from_passphrase(wrong_passphrase, salt)

    encrypted_secret = encrypt(secret, key)

    with pytest.raises(InvalidToken):
        decrypt(encrypted_secret, wrong_key)


def test_encrypt_output_is_base64():
    """
    Test that the encrypted output is a valid base64 string.

    This test ensures that the output of the `encrypt` function is a valid URL-safe base64 encoded string.
    It verifies that decoding the encrypted secret with `urlsafe_b64decode` does not raise an exception.
    """
    secret = "my_secret_data"
    passphrase = b"my_secret_passphrase"
    salt = b"my_secret_salt"

    key = generate_key_from_passphrase(passphrase, salt)

    encrypted_secret = encrypt(secret, key)

    try:
        urlsafe_b64decode(encrypted_secret)
    except Exception as e:
        pytest.fail(f"Encrypted secret is not valid base64: {e}")
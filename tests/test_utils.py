import pytest
from base64 import urlsafe_b64decode
from cryptography.fernet import Fernet, InvalidToken
from onetimesecret.utils import generate_key_from_passphrase, encrypt, decrypt


def test_generate_key_from_passphrase():
    passphrase = b"my_secret_passphrase"
    salt = b"my_secret_salt"

    key = generate_key_from_passphrase(passphrase, salt)

    assert len(key) == 44


def test_encrypt_decrypt():
    secret = "my_secret_data"
    passphrase = b"my_secret_passphrase"
    salt = b"my_secret_salt"

    key = generate_key_from_passphrase(passphrase, salt)

    encrypted_secret = encrypt(secret, key)

    assert encrypted_secret != secret

    decrypted_secret = decrypt(encrypted_secret, key)

    assert decrypted_secret == secret


def test_decrypt_with_wrong_key():
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
    secret = "my_secret_data"
    passphrase = b"my_secret_passphrase"
    salt = b"my_secret_salt"

    key = generate_key_from_passphrase(passphrase, salt)

    encrypted_secret = encrypt(secret, key)

    try:
        urlsafe_b64decode(encrypted_secret)
    except Exception as e:
        pytest.fail(f"Encrypted secret is not valid base64: {e}")
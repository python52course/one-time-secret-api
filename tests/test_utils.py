import pytest
from cryptography.fernet import InvalidToken

from onetimesecret.utils import encrypt, decrypt


MASTER_KEY = b'masterkey'


def test_encrypt_decrypt():
    """
    Testing the encrypt and decrypt functions to verify the correct encryption and decryption of data
    """
    data = "test"
    encrypted_data = encrypt(data, MASTER_KEY)
    assert encrypted_data != data

    decrypted_data = decrypt(encrypted_data, MASTER_KEY)
    assert decrypted_data == data


def test_decrypt_invalid_key():
    """
    Testing that the decrypt function cannot decrypt data with an invalid master key.
    """
    data = "test"
    encrypted_data = encrypt(data, MASTER_KEY)

    wrong_key = b'invalidmasterkey'

    with pytest.raises(InvalidToken):
        decrypt(encrypted_data, wrong_key)



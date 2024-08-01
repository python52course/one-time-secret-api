import pytest
from onetimesecret.utils import generate_secret_key


def test_generate_secret_key_length():
    """
    Test that the generated secret key has the correct length.
    """
    key = generate_secret_key()
    assert len(key) == 6


def test_generate_secret_key_uniqueness():
    """
    Test that multiple generate_secret_key calls return different keys.
    """
    key = generate_secret_key()
    data = [generate_secret_key() for _ in range(100)]
    for secret_key in data:
        assert key != secret_key

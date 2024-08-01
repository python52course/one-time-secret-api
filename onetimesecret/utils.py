import random
from string import ascii_letters, digits

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

import random
from string import ascii_letters, digits


def generate_secret_key():
    selection = ascii_letters + digits
    return ''.join(random.choice(selection) for _ in range(6))


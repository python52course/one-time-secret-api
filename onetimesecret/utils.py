import random
from string import ascii_letters, digits

selection = ascii_letters + digits


def generate_secret_key():
    key = ''.join(random.choice(selection) for _ in range(6))
    return key

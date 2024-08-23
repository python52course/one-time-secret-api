import os

from dotenv import load_dotenv


load_dotenv()
salt = os.getenv("SALT")
uri = os.getenv("URI")
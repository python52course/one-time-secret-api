from datetime import datetime

from pydantic import BaseModel


class Secret(BaseModel):
    """
    Represents a secret stored in the database.

    Attributes:
        secret_key (str): A unique identifier for the secret.
        secret (str): The encrypted content of the secret.
        expiration (datetime): The date and time when the secret expires.
    """
    secret_key: str
    secret: str
    expiration: datetime


class SecretRequest(BaseModel):
    """
    Represents a request to create a new secret.

    Attributes:
        secret (str): The content of the secret to be stored.
        passphrase (str): The passphrase used to encrypt the secret.
    """
    secret: str
    passphrase: str


class PassphraseRequest(BaseModel):
    """
    Represents a request to retrieve a secret using a passphrase.

    Attributes:
        passphrase (str): The passphrase used to decrypt the secret.
    """
    passphrase: str


class SecretKeyResponse(BaseModel):
    """
    SecretResponse represents the response model for the secret generation endpoint.

    Attributes:
        secret_key (str): The generated secret key.
    """
    secret_key: str


class SecretResponse(BaseModel):
    """
    SecretResponse represents the response model for the secret retrieval endpoint.

    Attributes:
        secret (str): The decrypted secret.
    """
    secret: str

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Secret(BaseModel):
    """
    Represents a secret entity with associated metadata.
    Attributes:
        id (Optional[str]): Unique identifier for the secret. Optional field.
        secret (str): The actual secret data, which will be hashed.
        passphrase (str): The passphrase to access the secret, which will be hashed.
        secret_key (str): A unique key that is used to retrieve the secret.
        expiration (Optional[datetime]): The expiration date and time for the secret.
    """
    id: Optional[str] = None
    secret: str
    passphrase: str
    secret_key: str
    expiration: Optional[datetime] = None


class SecretRequest(BaseModel):
    """
    Represents a request to create a secret.
    Attributes:
        secret (str): The actual secret data provided by the user.
        passphrase (str): The passphrase provided by the user to access the secret.
    """
    secret: str
    passphrase: str
    expiration: Optional[datetime] = None

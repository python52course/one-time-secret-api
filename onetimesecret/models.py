from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Secret(BaseModel):
    """
    Represents a secret entity with associated metadata.
    Attributes:
        id (str): Unique identifier for the secret.
        secret (str): The actual secret data, which will be hashed.
        passphrase (str): The passphrase to access the secret, which will be hashed.
        secret_key (str): A unique key that is used to retrieve the secret.
        expiration (Optional[datetime]): The expiration date and time for the secret.
    """
    id: str
    secret: str
    passphrase: str
    secret_key: str
    expiration: Optional[datetime]

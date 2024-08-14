import uuid
from abc import ABC, abstractmethod

from typing import Dict, Optional

from onetimesecret.models import Secret


class Repository(ABC):
    """
    An abstract base class representing a repository for secrets.
    """
    @abstractmethod
    async def create(self, secret: Secret) -> str:
        """
        Create a new secret.
        Args:
            secret (Secret): The secret object to be stored.
        Returns:
            str
        """
        pass

    @abstractmethod
    async def get(self, secret_key: str) -> Optional[Secret]:
        """
        Retrieve a secret by its secret_key.
        Args:
            secret_key (str): The key associated with the secret.
        Returns:
            Optional[Secret]: The secret object if found, otherwise None.
        """
        pass

    @abstractmethod
    async def delete(self, secret_key: str) -> None:
        """
        Delete a secret by its secret_key.
        Args:
            secret_key (str): The key associated with the secret to be deleted.
        Returns:
            None
        """
        pass


class FakeRepository(Repository):
    """
    A fake implementation of SecretRepository for testing purposes.
    """
    def __init__(self):
        self.data: Dict[str, Secret] = {}

    async def create(self, secret: Secret) -> str:
        """
        Create a new secret and store it in memory.
        Args:
            secret (Secret): The secret object to be stored.
        Returns:
            str: The secret_key of the newly created secret.
        """
        secret.id = str(uuid.uuid4())
        self.data[secret.secret_key] = secret
        return secret.secret_key

    async def get(self, secret_key: str) -> Optional[Secret]:
        """
        Retrieve a secret by its secret_key.
        Args:
            secret_key (str): The key associated with the secret.
        Returns:
            Optional[Secret]: The secret object if found, otherwise None.
        """
        return self.data.get(secret_key)

    async def delete(self, secret_key: str) -> None:
        """
        Delete a secret by its secret_key.
        Args:
            secret_key (str): The key associated with the secret to be deleted.
        Returns:
            None
        """
        if secret_key in self.data:
            del self.data[secret_key]

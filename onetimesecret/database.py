from typing import List, Optional

from onetimesecret.models import Secret


class FakeRepository:
    """
    A fake implementation of a repository for storing secrets in memory.
    This is primarily used for testing purposes without the need for a real database.

    Attributes:
        data (List[Secret]): A list that stores secret objects.
    """

    def __init__(self) -> None:
        """
        Initializes the FakeRepository with an empty list to hold secret data.
        """
        self.data: List[Secret] = []

    async def create(self, secret: Secret) -> None:
        """
        Stores a new secret in the repository.

        Args:
            secret (Secret): The secret object to be stored.

        Returns:
            None
        """
        self.data.append(secret)

    async def get(self, secret_key: str) -> Optional[str]:
        """
        Retrieves a secret from the repository using its unique secret key.

        Args:
            secret_key (str): The unique identifier of the secret to retrieve.

        Returns:
            Optional[str]: The decrypted secret if found, otherwise None.
        """
        for item in self.data:
            if item.id == secret_key:
                return item.secret
        return None

    async def delete(self, secret_key: str) -> None:
        """
        Deletes a secret from the repository using its unique secret key.

        Args:
            secret_key (str): The unique identifier of the secret to delete.

        Returns:
            None
        """
        self.data = [item for item in self.data if item.id != secret_key]

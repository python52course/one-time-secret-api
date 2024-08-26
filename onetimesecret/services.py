import uuid
from datetime import datetime
from typing import Optional

from cryptography.fernet import InvalidToken
from fastapi import HTTPException, status

from onetimesecret.database import FakeRepository
from onetimesecret.models import Secret
from onetimesecret.utils import decrypt, encrypt, generate_key_from_passphrase


class SecretService:
    """
    Service class responsible for handling the creation, retrieval, and deletion of secrets.

    Attributes:
        salt (bytes): The salt used for key derivation.
        repository (Repository): The repository where secrets are stored.
    """

    def __init__(self, salt: str, repository: 'FakeRepository') -> None:
        """
        Initializes the SecretService with the provided salt and repository.

        Args:
            salt (str): The salt used for key derivation.
            repository (Repository): The repository instance for storing and retrieving secrets.
        """
        self.salt = salt.encode()
        self.repository = repository

    def generate_key(self, passphrase: str) -> bytes:
        """
        Generates a key for encryption based on the provided passphrase.

        Args:
            passphrase (str): The passphrase used for key derivation.

        Returns:
            bytes: The generated encryption key.
        """
        return generate_key_from_passphrase(passphrase.encode(), self.salt)

    async def generate_secret(self, secret: str, passphrase: str) -> str:
        """
        Encrypts and stores a secret in the repository.

        Args:
            secret (str): The secret to be encrypted and stored.
            passphrase (str): The passphrase used to encrypt the secret.

        Returns:
            str: A unique identifier for the stored secret.
        """
        key = self.generate_key(passphrase)
        encrypted_secret = encrypt(secret, key)
        secret_key = str(uuid.uuid4())
        secret_instance = Secret(
            id=secret_key,
            secret=encrypted_secret,
            expiration=datetime.now()
        )
        await self.repository.create(secret_instance)
        return secret_key

    async def get_secret(self, secret_key: str, passphrase: str) -> Optional[str]:
        """
        Retrieves and decrypts a secret from the repository.

        Args:
            secret_key (str): The unique identifier of the secret to retrieve.
            passphrase (str): The passphrase used to decrypt the secret.

        Returns:
            Optional[str]: The decrypted secret if retrieval is successful, otherwise None.

        Raises:
            HTTPException: If the secret is not found or decryption fails.
        """
        secret = await self.repository.get(secret_key)
        if secret is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no such secret"
            )

        key = self.generate_key(passphrase)
        try:
            decrypted_secret = decrypt(secret, key)
        except InvalidToken:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input data"
            )

        await self.repository.delete(secret_key)
        return decrypted_secret

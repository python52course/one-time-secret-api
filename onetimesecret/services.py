import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from onetimesecret.database import FakeRepository
from onetimesecret.utils import encrypt, decrypt
from onetimesecret.models import Secret, SecretRequest, PassphraseRequest


class InvalidSecretKeyException(Exception):
    pass


class InvalidPassphraseException(Exception):
    pass


class SecretService:
    def __init__(self):
        """
        Loads the master key from environment variables and sets up
        the repository. Raises a ValueError if the master key is not
        found in the environment.
        """
        load_dotenv()
        master_key_str = os.getenv("MASTER_KEY")
        if master_key_str is None:
            raise ValueError("MASTER_KEY not found in environment variables.")
        self.master_key = master_key_str.encode('utf-8')
        self.repository = FakeRepository()

    async def generate_secret(self, request: SecretRequest) -> str:
        """
        Generates a new secret, encrypts it, and stores it in the repository.
        Args:
            request (SecretRequest): An object containing:
                - secret (str): The secret to be encrypted and stored.
                - passphrase (str): The passphrase used to protect the secret.
                - expiration (Optional[datetime]): The optional expiration date for the secret.
        Returns:
            str: The unique key associated with the newly generated secret.
        Raises:
            ValueError: If the master key is not found (handled in the __init__ method).
        """
        encrypted_secret = encrypt(request.secret, self.master_key)
        encrypted_passphrase = encrypt(request.passphrase, self.master_key)

        secret_key = str(uuid.uuid4())

        secret = Secret(
            secret=encrypted_secret,
            passphrase=encrypted_passphrase,
            secret_key=secret_key,
            expiration=request.expiration
        )

        await self.repository.create(secret)
        return secret_key

    async def get_secret(self, secret_key: str, request: PassphraseRequest) -> Optional[str]:
        """
        Retrieves and decrypts a secret from the repository using the provided secret key
        and passphrase.
        Args:
            secret_key (str): The unique key associated with the secret.
            request (PassphraseRequest): An object containing:
                - passphrase (str): The passphrase to validate against the stored secret.
        Returns:
            Optional[str]: The decrypted secret if the passphrase is correct; otherwise, raises an exception.
        Raises:
            InvalidSecretKeyException: If the secret key is not found in the repository.
            InvalidPassphraseException: If the provided passphrase does not match the stored passphrase.
        """
        secret = await self.repository.get(secret_key)
        if not secret:
            raise InvalidSecretKeyException

        decrypted_passphrase = decrypt(secret.passphrase, self.master_key)
        if request.passphrase != decrypted_passphrase:
            raise InvalidPassphraseException

        decrypted_secret = decrypt(secret.secret, self.master_key)
        await self.repository.delete(secret_key)
        return decrypted_secret

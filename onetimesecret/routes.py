import os

from dotenv import load_dotenv
from fastapi import APIRouter

from onetimesecret.services import SecretService
from onetimesecret.models import PassphraseRequest, SecretRequest, SecretResponse, SecretKeyResponse
from onetimesecret.database import FakeRepository

load_dotenv()
salt = os.getenv("SALT")
if salt is None:
    raise ValueError("SALT not found in environment variables.")

route = APIRouter()
repository = FakeRepository()
secret_service = SecretService(salt, repository)


@route.post("/generate", response_model=SecretKeyResponse)
async def generate_secret(request: SecretRequest) -> SecretKeyResponse:
    """
    Generate a new secret.

    This endpoint accepts a request object containing a secret and a passphrase,
    and returns a generated secret key.

    Args:
        request (SecretRequest): The request object containing the secret and passphrase.

    Returns:
        SecretKeyResponse: A response containing the generated secret key.
    """
    secret_key = await secret_service.generate_secret(request.secret, request.passphrase)
    return SecretKeyResponse(secret_key=secret_key)


@route.post("/secrets/{secret_key}", response_model=SecretResponse)
async def get_secret(secret_key: str, request: PassphraseRequest) -> SecretResponse:
    """
    Retrieve a secret by its key.

    This endpoint accepts a secret key and a request object containing a passphrase.
    It returns the decrypted secret if the key and passphrase are correct.

    Args:
        secret_key (str): The key of the secret to retrieve.
        request (PassphraseRequest): The request object containing the passphrase.

    Returns:
        SecretResponse: A response containing the decrypted secret.

    Raises:
        HTTPException: If the secret key is invalid or the passphrase is incorrect.
    """
    secret = await secret_service.get_secret(secret_key, request.passphrase)
    return SecretResponse(secret=secret)

import os

from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from onetimesecret.services import SecretService
from onetimesecret.models import PassphraseRequest, SecretRequest
from onetimesecret.database import FakeRepository

load_dotenv()
salt = os.getenv("SALT")
if salt is None:
    raise ValueError("SALT not found in environment variables.")

route = APIRouter()
repository = FakeRepository()
secret_service = SecretService(salt, repository)


@route.post("/generate", response_model=str)
async def generate_secret(request: SecretRequest) -> JSONResponse:
    """
    Endpoint to generate a new secret.

    Args:
        request (SecretRequest): The request object containing the secret, passphrase.

    Returns:
        JSONResponse: A JSON response containing the generated secret key.
    """
    secret_key = await secret_service.generate_secret(request.secret, request.passphrase)
    return JSONResponse(content={"secret_key": secret_key})


@route.post("/secrets/{secret_key}", response_model=str)
async def get_secret(secret_key: str, request: PassphraseRequest) -> JSONResponse:
    """
    Endpoint to retrieve a secret by its key.

    Args:
        secret_key (str): The key of the secret to retrieve.
        request (PassphraseRequest): The request object containing the passphrase.

    Returns:
        JSONResponse: A JSON response containing the decrypted secret.

    Raises:
        HTTPException: If the secret key is invalid or the passphrase is incorrect.
    """
    secret = await secret_service.get_secret(secret_key, request.passphrase)
    return JSONResponse(content={"secret": secret})

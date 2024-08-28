from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends

from onetimesecret.services import SecretService
from onetimesecret.models import PassphraseRequest, SecretRequest, SecretResponse, SecretKeyResponse
from onetimesecret.database import Repository
from onetimesecret.config import uri, salt


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifespan of the FastAPI application, including setting up and tearing down resources.

    This function is responsible for initializing the MongoDB repository, creating necessary indexes,
    and setting up the SecretService. It also ensures that the database connection is properly closed
    when the application shuts down.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: This function doesn't return anything. It yields control back to the FastAPI application
              to handle incoming requests.

    Ensures:
        - The MongoDB repository is properly initialized with the required indexes.
        - The SecretService is configured with the given salt and is attached to the application's state.
        - The database connection is closed when the application is shut down.
    """
    repository = Repository(uri, "secret_db")
    await repository.initialize_indexes()

    secret_service = SecretService(salt, repository)

    app.state.secret_service = secret_service

    try:
        yield
    finally:
        await repository.close()

app = FastAPI(lifespan=lifespan, title="One Time Secret")


@app.post("/generate", response_model=SecretKeyResponse)
async def generate_secret(
        request: SecretRequest,
        secret_service: SecretService = Depends(lambda: app.state.secret_service)
) -> SecretKeyResponse:
    """
    Endpoint to generate a new secret.

    Args:
        request (SecretRequest): The request object containing the secret content and passphrase.

    Returns:
        SecretKeyResponse: Response object containing the generated secret key.

    Raises:
        HTTPException: If the request data is invalid or secret generation fails.
    """

    secret_key = await secret_service.generate_secret(request.secret, request.passphrase)
    return SecretKeyResponse(secret_key=secret_key)


@app.post("/secrets/{secret_key}", response_model=SecretResponse)
async def get_secret(
        secret_key: str,
        request: PassphraseRequest,
        secret_service: SecretService = Depends(lambda: app.state.secret_service)
) -> SecretResponse:
    """
    Endpoint to retrieve a secret using a secret key.

    Args:
        secret_key (str): The unique key of the secret to retrieve.
        request (PassphraseRequest): The request object containing the passphrase for decryption.

    Returns:
        SecretResponse: Response object containing the decrypted secret.

    Raises:
        HTTPException: If the secret is not found or the passphrase is incorrect.
    """

    secret = await secret_service.get_secret(secret_key, request.passphrase)
    return SecretResponse(secret=secret)

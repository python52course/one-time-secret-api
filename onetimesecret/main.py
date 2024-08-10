from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from onetimesecret.models import SecretRequest, Secret, PassphraseRequest
from onetimesecret.database import FakeRepository
from onetimesecret.utils import generate_secret_key

app = FastAPI(title="One Time Secrets")
repository = FakeRepository()


@app.post("/generate", response_model=str)
async def generate_secret(request: SecretRequest) -> JSONResponse:
    """
    Generate a new secret and store it in the repository.
    Args:
        request (SecretRequest): The request body containing the secret and passphrase.
    Returns:
        JSONResponse: A JSON response containing the generated secret_key.
    """
    while True:
        secret_key = generate_secret_key()
        if secret_key not in repository.data:
            break
    secret = Secret(secret=request.secret,
                    passphrase=request.passphrase,
                    secret_key=secret_key)
    await repository.create(secret)
    return JSONResponse(content={"secret_key": secret_key})


@app.post("/secrets/{secret_key}")
async def get_secret(secret_key: str, request: PassphraseRequest) -> JSONResponse:
    """
    Retrieve and delete a secret using the provided secret_key and passphrase.
    Args:
        secret_key (str): The unique key associated with the secret.
        request (PassphraseRequest): The request body containing the passphrase.
    Returns:
        JSONResponse: A JSON response containing the secret, or an error message.
    """
    secret = await repository.get(secret_key)
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Invalid secret_key'
        )

    if request.passphrase != secret.passphrase:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid passphrase"
        )

    await repository.delete(secret_key)
    return JSONResponse(content={"secret": secret.secret})

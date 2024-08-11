from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from onetimesecret.models import SecretRequest, Secret, PassphraseRequest
from onetimesecret.database import FakeRepository
from onetimesecret.utils import generate_secret_key, encrypt, decrypt
from dotenv import load_dotenv
import os

app = FastAPI(title="One Time Secrets")
repository = FakeRepository()

load_dotenv()
master_key_str = os.getenv("MASTER_KEY")
if master_key_str is None:
    raise ValueError("MASTER_KEY not found in environment variables.")
MASTER_KEY = master_key_str.encode('utf-8')


@app.post("/generate", response_model=str)
async def generate_secret(request: SecretRequest) -> JSONResponse:
    """
    Generate a new secret and store it in the repository.
    Args:
        request (SecretRequest): The request body containing the secret and passphrase.
    Returns:
        JSONResponse: A JSON response containing the generated secret_key.
    """
    encrypted_secret = encrypt(request.secret, MASTER_KEY)
    encrypted_passphrase = encrypt(request.passphrase, MASTER_KEY)

    while True:
        secret_key = generate_secret_key()
        if secret_key not in repository.data:
            break

    secret = Secret(
            secret=encrypted_secret,
            passphrase=encrypted_passphrase,
            secret_key=secret_key,
            expiration=request.expiration
    )

    await repository.create(secret)

    return JSONResponse(content={"secret_key": secret_key})


@app.post("/secrets/{secret_key}", response_model=str)
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
    decrypted_passphrase = decrypt(secret.passphrase, MASTER_KEY)
    if request.passphrase != decrypted_passphrase:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid passphrase"
        )
    decrypted_secret = decrypt(secret.secret, MASTER_KEY)
    await repository.delete(secret_key)
    return JSONResponse(content={"secret": decrypted_secret})

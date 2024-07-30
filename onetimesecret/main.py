from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from models import SecretRequest, Secret
from database import FakeRepository
from utils import generate_secret_key

app = FastAPI()
repository = FakeRepository()


@app.post("/generate", response_model=str)
async def generate_secret(request: SecretRequest):
    """
    Generate a new secret and store it in the repository.
    Args:
        request (SecretRequest): The request body containing the secret and passphrase.
    Returns:
        JSONResponse: A JSON response containing the generated secret_key.
    """
    if not request.secret or not request.passphrase:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'secret' and 'passphrase' fields are required"
        )

    secret_key = generate_secret_key()
    secret = Secret(secret=request.secret,
                    passphrase=request.passphrase,
                    secret_key=secret_key)
    await repository.create(secret)
    return JSONResponse(content={"secret_key": secret_key})

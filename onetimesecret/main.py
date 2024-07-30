from fastapi import FastAPI
from fastapi.responses import JSONResponse
from onetimesecret.models import SecretRequest, Secret
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
    secret_key = generate_secret_key()
    secret = Secret(secret=request.secret,
                    passphrase=request.passphrase,
                    secret_key=secret_key)
    await repository.create(secret)
    return JSONResponse(content={"secret_key": secret_key})

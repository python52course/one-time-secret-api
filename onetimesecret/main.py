from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from onetimesecret.services import InvalidSecretKeyException, InvalidPassphraseException, SecretService
from onetimesecret.models import PassphraseRequest, SecretRequest

app = FastAPI(title="One Time Secrets")
secret_service = SecretService()


@app.post("/generate", response_model=str)
async def generate_secret(request: SecretRequest) -> JSONResponse:
    try:
        secret_key = await secret_service.generate_secret(request)
        return JSONResponse(content={"secret_key": secret_key})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.post("/secrets/{secret_key}", response_model=str)
async def get_secret(secret_key: str, request: PassphraseRequest) -> JSONResponse:
    try:
        secret = await secret_service.get_secret(secret_key, request)
        return JSONResponse(content={"secret": secret})
    except InvalidSecretKeyException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="An invalid secret key or a secret with such a secret key was not found"
        )
    except InvalidPassphraseException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid passphrase")

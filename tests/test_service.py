import pytest
from fastapi import HTTPException, status

from onetimesecret.services import SecretService
from onetimesecret.database import FakeRepository


@pytest.fixture
def secret_service():
    salt = "my_secret_salt"
    repository = FakeRepository()
    return SecretService(salt=salt, repository=repository)


@pytest.mark.asyncio
async def test_generate_secret(secret_service):
    secret = "my_secret_data"
    passphrase = "my_secret_passphrase"

    secret_key = await secret_service.generate_secret(secret, passphrase)

    assert isinstance(secret_key, str)
    assert len(secret_key) == 36


@pytest.mark.asyncio
async def test_get_secret(secret_service):
    secret = "my_secret_data"
    passphrase = "my_secret_passphrase"

    secret_key = await secret_service.generate_secret(secret, passphrase)
    decrypted_secret = await secret_service.get_secret(secret_key, passphrase)

    assert decrypted_secret == secret


@pytest.mark.asyncio
async def test_get_secret_with_invalid_passphrase(secret_service):
    secret = "my_secret_data"
    passphrase = "my_secret_passphrase"
    wrong_passphrase = "wrong_passphrase"

    secret_key = await secret_service.generate_secret(secret, passphrase)

    with pytest.raises(HTTPException) as excinfo:
        await secret_service.get_secret(secret_key, wrong_passphrase)

    assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
    assert excinfo.value.detail == "Invalid input data"


@pytest.mark.asyncio
async def test_get_secret_not_found(secret_service):
    secret_key = "non_existent_secret_key"
    passphrase = "my_secret_passphrase"

    with pytest.raises(HTTPException) as excinfo:
        await secret_service.get_secret(secret_key, passphrase)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "There is no such secret"


@pytest.mark.asyncio
async def test_secret_deleted_after_retrieval(secret_service):
    secret = "my_secret_data"
    passphrase = "my_secret_passphrase"

    secret_key = await secret_service.generate_secret(secret, passphrase)
    await secret_service.get_secret(secret_key, passphrase)

    retrieved_secret = await secret_service.repository.get(secret_key)

    assert retrieved_secret is None


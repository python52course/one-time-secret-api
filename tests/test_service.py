import pytest
from fastapi import HTTPException, status

from onetimesecret.services import SecretService
from onetimesecret.database import FakeRepository


@pytest.fixture
def secret_service():
    """
    Fixture to set up the SecretService with a fake repository.

    This fixture initializes the `SecretService` with a predefined salt and a `FakeRepository` instance.
    It provides a clean and consistent environment for testing.

    Returns:
        SecretService: An instance of the `SecretService` class.
    """
    salt = "my_secret_salt"
    repository = FakeRepository()
    return SecretService(salt=salt, repository=repository)


@pytest.mark.asyncio
async def test_generate_secret(secret_service):
    """
    Test the generation of a new secret.

    This test verifies that a secret can be successfully generated and stored. It checks that the returned
    secret key is a string with the expected length of 36 characters.

    Args:
        secret_service (SecretService): An instance of the `SecretService` class provided by the fixture.
    """
    secret = "my_secret_data"
    passphrase = "my_secret_passphrase"

    secret_key = await secret_service.generate_secret(secret, passphrase)

    assert isinstance(secret_key, str)
    assert len(secret_key) == 36


@pytest.mark.asyncio
async def test_get_secret(secret_service):
    """
   Test retrieval of a secret.

   This test ensures that a previously generated secret can be retrieved successfully. It checks that the
   retrieved secret matches the originally stored secret using the correct passphrase.

   Args:
       secret_service (SecretService): An instance of the `SecretService` class provided by the fixture.
   """
    secret = "my_secret_data"
    passphrase = "my_secret_passphrase"

    secret_key = await secret_service.generate_secret(secret, passphrase)
    decrypted_secret = await secret_service.get_secret(secret_key, passphrase)

    assert decrypted_secret == secret


@pytest.mark.asyncio
async def test_get_secret_with_invalid_passphrase(secret_service):
    """
    Test retrieval of a secret with an invalid passphrase.

    This test verifies that attempting to retrieve a secret with an incorrect passphrase raises an `HTTPException`
    with a status code of 400 and an appropriate error detail message.

    Args:
        secret_service (SecretService): An instance of the `SecretService` class provided by the fixture.
    """
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
    """
    Test retrieval of a non-existent secret.

    This test ensures that attempting to retrieve a secret with a non-existent secret key raises an `HTTPException`
    with a status code of 404 and an appropriate error detail message.

    Args:
        secret_service (SecretService): An instance of the `SecretService` class provided by the fixture.
    """
    secret_key = "non_existent_secret_key"
    passphrase = "my_secret_passphrase"

    with pytest.raises(HTTPException) as excinfo:
        await secret_service.get_secret(secret_key, passphrase)

    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "There is no such secret"


@pytest.mark.asyncio
async def test_secret_deleted_after_retrieval(secret_service):
    """
    Test that a secret is deleted after retrieval.

    This test verifies that after a secret is retrieved, it is removed from the repository. It ensures that
    attempting to fetch the secret again returns `None`, indicating the secret was successfully deleted.

    Args:
        secret_service (SecretService): An instance of the `SecretService` class provided by the fixture.
    """
    secret = "my_secret_data"
    passphrase = "my_secret_passphrase"

    secret_key = await secret_service.generate_secret(secret, passphrase)
    await secret_service.get_secret(secret_key, passphrase)

    retrieved_secret = await secret_service.repository.get(secret_key)

    assert retrieved_secret is None


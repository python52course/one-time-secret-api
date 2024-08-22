import pytest
from datetime import datetime, timedelta
from onetimesecret.models import Secret
from onetimesecret.database import FakeRepository


@pytest.fixture
def repository() -> FakeRepository:
    """
    Fixture to create an instance of FakeRepository for testing.

    Returns:
        FakeRepository: An instance of FakeRepository.
    """
    return FakeRepository()


@pytest.mark.asyncio
async def test_create_secret(repository: FakeRepository) -> None:
    """
    Test the creation of a secret in the repository.

    Args:
        repository (FakeRepository): The instance of FakeRepository.

    Returns:
        None
    """
    expiration = datetime.now()
    secret = Secret(id="test_key", secret="test_secret", expiration=expiration)
    await repository.create(secret)

    assert len(repository.data) == 1
    assert repository.data[0] == secret


@pytest.mark.asyncio
async def test_get_secret(repository: FakeRepository) -> None:
    """
    Test retrieving a secret from the repository.

    Args:
        repository (FakeRepository): The instance of FakeRepository.

    Returns:
        None
    """
    expiration = datetime.now()
    secret = Secret(id="test_key", secret="test_secret", expiration=expiration)
    await repository.create(secret)

    retrieved_secret = await repository.get("test_key")
    assert retrieved_secret == "test_secret"

    retrieved_secret = await repository.get("non_existing_key")
    assert retrieved_secret is None


@pytest.mark.asyncio
async def test_delete_secret(repository: FakeRepository) -> None:
    """
    Test deleting a secret from the repository.

    Args:
        repository (FakeRepository): The instance of FakeRepository.

    Returns:
        None
    """
    expiration1 = datetime.now()
    expiration2 = datetime.now()
    secret1 = Secret(id="key1", secret="secret1", expiration=expiration1)
    secret2 = Secret(id="key2", secret="secret2", expiration=expiration2)
    await repository.create(secret1)
    await repository.create(secret2)

    await repository.delete("key1")
    assert len(repository.data) == 1
    assert repository.data[0] == secret2

    await repository.delete("non_existing_key")
    assert len(repository.data) == 1
    assert repository.data[0] == secret2

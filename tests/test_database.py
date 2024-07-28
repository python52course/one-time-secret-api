import pytest
from onetimesecret.database import FakeSecretRepository
from onetimesecret.models import Secret


@pytest.fixture
def fake_repo():
    """
   Fixture to provide a FakeSecretRepository instance for testing.
   Returns:
       FakeSecretRepository: An instance of the fake repository.
   """
    return FakeSecretRepository()


@pytest.mark.asyncio
async def test_create_secret(fake_repo):
    """
    Test the creation of a secret in the fake repository.
    Args:
        fake_repo (FakeSecretRepository): The fake repository instance.
    Asserts:
        secret_key (str): The key used to retrieve the secret.
        The secret is stored correctly in the repository.
    """
    secret = Secret(id="", secret="secret", passphrase="password", secret_key="key", expiration=None)
    secret_key = await fake_repo.create_secret(secret)
    assert secret_key == "key"
    assert secret_key in fake_repo.data
    assert fake_repo.data[secret_key].secret == "secret"


@pytest.mark.asyncio
async def test_get_secret(fake_repo):
    """
    Test retrieving a secret from the fake repository.
    Args:
        fake_repo (FakeSecretRepository): The fake repository instance.
    Asserts:
        The secret is retrieved correctly.
        The passphrase is correct.
    """
    secret = Secret(id="", secret="secret", passphrase="password", secret_key="key", expiration=None)
    await fake_repo.create_secret(secret)
    retrieved_secret = await fake_repo.get_secret("key")
    assert retrieved_secret is not None
    assert retrieved_secret.secret == "secret"
    assert retrieved_secret.passphrase == "password"


@pytest.mark.asyncio
async def test_delete_secret(fake_repo):
    """
    Test deleting a secret from the fake repository.
    Args:
        fake_repo (FakeSecretRepository): The fake repository instance.
    Asserts:
        The secret is deleted correctly.
        Retrieving the deleted secret returns None.
    """
    secret = Secret(id="", secret="secret", passphrase="mypassword", secret_key="key", expiration=None)
    await fake_repo.create_secret(secret)
    await fake_repo.delete_secret("key")
    retrieved_secret = await fake_repo.get_secret("key")
    assert retrieved_secret is None

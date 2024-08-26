import pytest
from httpx import AsyncClient
from fastapi import HTTPException, status
from typing import Dict

from onetimesecret.main import app


class MockSecretService:
    """
    A mock implementation of the secret service for testing purposes.
    This class simulates the generation and retrieval of secrets with in-memory storage.
    """

    secret_data: Dict[str, Dict[str, str]] = {}

    async def generate_secret(self, secret: str, passphrase: str) -> str:
        """
        Generates a secret and stores it in memory.

        Args:
            secret (str): The secret value to store.
            passphrase (str): The passphrase associated with the secret.

        Returns:
            str: A fixed secret key used for retrieval.
        """
        secret_key = "secret_key"
        self.secret_data[secret_key] = {"secret": secret, "passphrase": passphrase}
        return secret_key

    async def get_secret(self, secret_key: str, passphrase: str) -> str:
        """
        Retrieves a secret from memory if the provided key and passphrase match.

        Args:
            secret_key (str): The key used to retrieve the secret.
            passphrase (str): The passphrase associated with the secret.

        Returns:
            str: The stored secret if valid.

        Raises:
            HTTPException: If the secret key is invalid or the passphrase is incorrect.
        """
        item = self.secret_data.get(secret_key)

        if item:
            if item["passphrase"] == passphrase:
                del self.secret_data[secret_key]
                return item["secret"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input data"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="There is no such secret"
            )


@pytest.fixture(scope="module")
def setup_mock_service():
    """
    Fixture that sets up and tears down the mock secret service for testing.
    """
    app.state.secret_service = MockSecretService()
    yield
    del app.state.secret_service


@pytest.fixture
def secret_data() -> Dict[str, Dict[str, str]]:
    """
    Fixture that provides various secret data for testing.

    Returns:
        Dict[str, Dict[str, str]]: A dictionary containing different test cases for secrets.
    """
    return {
        "correct": {"secret": "test_secret", "passphrase": "test_passphrase", "secret_key": "secret_key"},
        "incorrect_passphrase": {"secret": "test_secret", "passphrase": "wrong_passphrase", "secret_key": "secret_key"},
        "incorrect_secret_key": {"secret": "test_secret", "passphrase": "test_passphrase", "secret_key": "invalid_key"},
        "incorrect_both": {"secret": "test_secret", "passphrase": "wrong_passphrase", "secret_key": "invalid_key"}
    }


@pytest.mark.anyio
async def test_generate_secret(setup_mock_service: None, secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests the generation of a secret.

    Args:
        setup_mock_service (None): Fixture that sets up the mock service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/generate", json=secret_data["correct"])
    assert response.status_code == 200
    assert response.json() == {"secret_key": "secret_key"}


@pytest.mark.anyio
async def test_get_secret(setup_mock_service: None, secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests retrieving a secret with correct key and passphrase.

    Args:
        setup_mock_service (None): Fixture that sets up the mock service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/generate", json=secret_data["correct"])

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/secrets/{secret_data['correct']['secret_key']}", json={"passphrase": secret_data["correct"]["passphrase"]})
    assert response.status_code == 200
    assert response.json() == {"secret": secret_data["correct"]["secret"]}


@pytest.mark.anyio
async def test_get_secret_with_incorrect_passphrase(setup_mock_service: None, secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests retrieving a secret with an incorrect passphrase.

    Args:
        setup_mock_service (None): Fixture that sets up the mock service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/generate", json=secret_data["correct"])

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/secrets/{secret_data['correct']['secret_key']}", json={"passphrase": secret_data["incorrect_passphrase"]["passphrase"]})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid input data"}


@pytest.mark.anyio
async def test_get_secret_with_incorrect_secret_key(setup_mock_service: None, secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests retrieving a secret with an incorrect secret key.

    Args:
        setup_mock_service (None): Fixture that sets up the mock service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/generate", json=secret_data["correct"])

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/secrets/{secret_data['incorrect_secret_key']['secret_key']}", json={"passphrase": secret_data["correct"]["passphrase"]})
    assert response.status_code == 404
    assert response.json() == {"detail": "There is no such secret"}


@pytest.mark.anyio
async def test_get_secret_with_incorrect_both(setup_mock_service: None, secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests retrieving a secret with both incorrect secret key and passphrase.

    Args:
        setup_mock_service (None): Fixture that sets up the mock service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/generate", json=secret_data["correct"])

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/secrets/{secret_data['incorrect_both']['secret_key']}", json={"passphrase": secret_data["incorrect_both"]["passphrase"]})
    assert response.status_code == 404
    assert response.json() == {"detail": "There is no such secret"}


@pytest.mark.anyio
async def test_generate_get_and_verify_secret_deletion(setup_mock_service: None, secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests generating, retrieving, and then verifying the deletion of a secret.

    Args:
        setup_mock_service (None): Fixture that sets up the mock service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/generate", json=secret_data["correct"])
    assert response.status_code == 200
    secret_key = response.json()["secret_key"]

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/secrets/{secret_key}", json={"passphrase": secret_data["correct"]["passphrase"]})
    assert response.status_code == 200
    assert response.json() == {"secret": secret_data["correct"]["secret"]}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/secrets/{secret_key}", json={"passphrase": secret_data["correct"]["passphrase"]})
    assert response.status_code == 404
    assert response.json() == {"detail": "There is no such secret"}

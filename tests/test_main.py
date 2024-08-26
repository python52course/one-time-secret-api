import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict

from onetimesecret.main import app
from onetimesecret.services import SecretService
from onetimesecret.database import Repository


@pytest.fixture(scope="module")
async def setup_real_service():
    """
    Fixture that sets up and tears down the real secret service with MongoDB for testing.
    """
    test_db_uri = "mongodb://localhost:27017"
    test_db_name = "test_db"

    repository = Repository(test_db_uri, test_db_name)
    await repository.initialize_indexes()

    secret_service = SecretService(salt="test_salt", repository=repository)
    app.state.secret_service = secret_service

    yield

    await repository.close()
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
async def test_generate_secret(setup_real_service: None, secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests the generation of a secret with real service.

    Args:
        setup_real_service (None): Fixture that sets up the real service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/generate", json=secret_data["correct"])
    assert response.status_code == 200
    assert "secret_key" in response.json()


@pytest.mark.anyio
async def test_get_secret(setup_real_service: None, secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests retrieving a secret with correct key and passphrase using real service.

    Args:
        setup_real_service (None): Fixture that sets up the real service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        generate_response = await ac.post("/generate", json=secret_data["correct"])
        secret_key = generate_response.json()["secret_key"]

        response = await ac.post(f"/secrets/{secret_key}", json={"passphrase": secret_data["correct"]["passphrase"]})
    assert response.status_code == 200
    assert response.json() == {"secret": secret_data["correct"]["secret"]}


@pytest.mark.anyio
async def test_get_secret_with_incorrect_passphrase(setup_real_service: None,
                                                    secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests retrieving a secret with an incorrect passphrase using real service.

    Args:
        setup_real_service (None): Fixture that sets up the real service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        generate_response = await ac.post("/generate", json=secret_data["correct"])
        secret_key = generate_response.json()["secret_key"]

        response = await ac.post(f"/secrets/{secret_key}",
                                 json={"passphrase": secret_data["incorrect_passphrase"]["passphrase"]})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid input data"}


@pytest.mark.anyio
async def test_get_secret_with_incorrect_secret_key(setup_real_service: None,
                                                    secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests retrieving a secret with an incorrect secret key using real service.

    Args:
        setup_real_service (None): Fixture that sets up the real service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/generate", json=secret_data["correct"])

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/secrets/{secret_data['incorrect_secret_key']['secret_key']}",
                                 json={"passphrase": secret_data["correct"]["passphrase"]})
    assert response.status_code == 404
    assert response.json() == {"detail": "There is no such secret"}


@pytest.mark.anyio
async def test_get_secret_with_incorrect_both(setup_real_service: None, secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests retrieving a secret with both incorrect secret key and passphrase using real service.

    Args:
        setup_real_service (None): Fixture that sets up the real service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/generate", json=secret_data["correct"])

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/secrets/{secret_data['incorrect_both']['secret_key']}",
                                 json={"passphrase": secret_data["incorrect_both"]["passphrase"]})
    assert response.status_code == 404
    assert response.json() == {"detail": "There is no such secret"}


@pytest.mark.anyio
async def test_generate_get_and_verify_secret_deletion(setup_real_service: None,
                                                       secret_data: Dict[str, Dict[str, str]]) -> None:
    """
    Tests generating, retrieving, and then verifying the deletion of a secret using real service.

    Args:
        setup_real_service (None): Fixture that sets up the real service.
        secret_data (Dict[str, Dict[str, str]]): Fixture that provides secret data for testing.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        generate_response = await ac.post("/generate", json=secret_data["correct"])
        secret_key = generate_response.json()["secret_key"]

        response = await ac.post(f"/secrets/{secret_key}", json={"passphrase": secret_data["correct"]["passphrase"]})
    assert response.status_code == 200
    assert response.json() == {"secret": secret_data["correct"]["secret"]}

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/secrets/{secret_key}", json={"passphrase": secret_data["correct"]["passphrase"]})
    assert response.status_code == 404
    assert response.json() == {"detail": "There is no such secret"}


@pytest.mark.anyio
async def test_ttl_index_creation():
    """
    The test verifies that the TTL index on the 'expiration' field has been successfully created.
    """
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client['test_db']
    collection = db['secrets']

    indexes = await collection.index_information()

    assert 'expiration_1' in indexes

    ttl_seconds = indexes['expiration_1'].get('expireAfterSeconds')
    assert ttl_seconds == 1
    client.close()

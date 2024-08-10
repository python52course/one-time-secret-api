import pytest
from fastapi.testclient import TestClient
from onetimesecret.main import app, repository
from onetimesecret.models import Secret

client = TestClient(app)


@pytest.fixture
def clear_repository():
    """
    Fixture to clear the repository data before each test
    """
    repository.data = {}


@pytest.mark.asyncio
async def test_generate_secret_success(clear_repository):
    """
    Test the successful generation of a secret.
    This test sends a POST request to the '/generate' endpoint with valid
    'secret' and 'passphrase' fields. It then checks that:
        - The response status code is 200.
        - The response contains a 'secret_key'.
        - The 'secret_key' is stored in the repository with the correct 'secret' and 'passphrase'.
    Args:
        clear_repository (fixture): A fixture that clears the repository data before the test.
    Asserts:
        The response status code is 200.
        The response contains the 'secret_key'.
        The 'secret_key' exists in the repository.
        The repository entry for the 'secret_key' has the correct 'secret' and 'passphrase'.
    """
    response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
    assert response.status_code == 200
    response_data = response.json()
    assert "secret_key" in response_data
    secret_key = response_data["secret_key"]
    assert secret_key in repository.data
    assert repository.data[secret_key].secret == "my_secret"
    assert repository.data[secret_key].passphrase == "my_passphrase"


@pytest.mark.asyncio
async def test_generate_secret_missing_fields():
    """
    Test the handling of missing fields in the request.
    This test sends POST requests to the '/generate' endpoint with different missing fields.
    It checks that:
        - The response status code is 422 when the 'secret' field is missing.
        - The response status code is 422 when the 'passphrase' field is missing.
    Asserts:
        The response status code is 422 for both cases.
    """
    response = client.post("/generate", json={"secret": "my_secret"})
    assert response.status_code == 422
    response = client.post("/generate", json={"passphrase": "my_passphrase"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_unique_secret_keys(clear_repository):
    """
    Test that multiple generate_secret calls return unique keys.
    This test sends multiple POST requests to the '/generate' endpoint and ensures that all returned keys are unique.
    Args:
        clear_repository (fixture): A fixture that clears the repository data before the test.
    Asserts:
        All generated keys are unique.
    """
    keys = set()
    for _ in range(100):
        response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
        assert response.status_code == 200
        response_data = response.json()
        assert "secret_key" in response_data
        secret_key = response_data["secret_key"]
        assert secret_key not in keys, "Duplicate key found"
        keys.add(secret_key)


@pytest.mark.asyncio
async def test_generate_secret_with_existing_keys(clear_repository):
    """
    Test that a new unique secret key is generated even if some keys already exist in the repository.
    This test pre-populates the repository with some keys and then sends a POST request to the '/generate' endpoint.
    It checks that the generated key is unique and does not collide with existing keys.
    Args:
        clear_repository (fixture): A fixture that clears the repository data before the test.
    Asserts:
        The generated key is unique and does not exist in the pre-populated repository.
    """
    existing_keys = {"key1", "key2", "key3"}
    for key in existing_keys:
        secret = Secret(secret="existing_secret", passphrase="existing_passphrase", secret_key=key)
        repository.data[key] = {"secret": secret.secret, "passphrase": secret.passphrase}

    response = client.post("/generate", json={"secret": "new_secret", "passphrase": "new_passphrase"})
    assert response.status_code == 200
    response_data = response.json()
    assert "secret_key" in response_data
    new_secret_key = response_data["secret_key"]
    assert new_secret_key not in existing_keys, "Generated key collides with existing keys"
    assert new_secret_key in repository.data, "Generated key not stored in repository"
    assert repository.data[new_secret_key].secret == "new_secret"
    assert repository.data[new_secret_key].passphrase == "new_passphrase"


@pytest.mark.asyncio
async def test_get_secret(clear_repository):
    """
    Test retrieval of a secret with valid secret_key and passphrase.
    This test first creates a secret and then retrieves it successfully.
    It checks that:
        - The response status code is 200.
        - The response contains the correct secret.
    Args:
        clear_repository (fixture): A fixture that clears the repository data before the test.
    Asserts:
        The response status code is 200.
        The response contains the correct secret.
    """
    response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
    assert response.status_code == 200
    response_data = response.json()
    secret_key = response_data["secret_key"]

    response = client.post(f"/secrets/{secret_key}", json={"passphrase": "my_passphrase"})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["secret"] == "my_secret"


@pytest.mark.asyncio
async def test_get_secret_with_invalid_key(clear_repository):
    """
    Test retrieval of a secret with an invalid secret_key.
    This test sends a POST request to the '/secrets/{secret_key}' endpoint
    with a non-existing secret_key.
    It checks that the response status code is 404.
    Args:
        clear_repository (fixture): A fixture that clears the repository data before the test.
    Asserts:
        The response status code is 404.
    """
    response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
    assert response.status_code == 200

    response = client.post("/secrets/invalid_key", json={"passphrase": "my_passphrase"})
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Invalid secret_key"


@pytest.mark.asyncio
async def test_get_secret_with_invalid_passphrase(clear_repository):
    """
    Test retrieval of a secret with an incorrect passphrase.
    This test sends a POST request to the '/generate' endpoint to create a secret,
    then sends a POST request to the '/secrets/{secret_key}' endpoint with the correct key
    but an incorrect passphrase. It checks that the response status code is 403.
    Args:
        clear_repository (fixture): A fixture that clears the repository data before the test.
    Asserts:
        The response status code is 403.
    """
    response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
    assert response.status_code == 200
    response_data = response.json()
    secret_key = response_data["secret_key"]

    response = client.post(f"/secrets/{secret_key}", json={"passphrase": "wrong_passphrase"})
    assert response.status_code == 403
    response_data = response.json()
    assert response_data["detail"] == "Invalid passphrase"


@pytest.mark.asyncio
async def test_get_secret_already_retrieved(clear_repository):
    """
    Test retrieval of a secret that has already been retrieved.
    This test sends a POST request to the '/generate' endpoint to create a secret,
    retrieves it successfully, and then attempts to retrieve it again.
    It checks that the response status code is 404 on the second attempt.
    Args:
        clear_repository (fixture): A fixture that clears the repository data before the test.
    Asserts:
        The response status code is 404 on the second attempt.
    """
    response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
    assert response.status_code == 200
    response_data = response.json()
    secret_key = response_data["secret_key"]

    response = client.post(f"/secrets/{secret_key}", json={"passphrase": "my_passphrase"})
    assert response.status_code == 200

    response = client.post(f"/secrets/{secret_key}", json={"passphrase": "my_passphrase"})
    assert response.status_code == 404
    response_data = response.json()
    assert response_data["detail"] == "Invalid secret_key"
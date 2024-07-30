import pytest
from fastapi.testclient import TestClient
from onetimesecret.main import app, repository

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

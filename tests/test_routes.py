import pytest
from fastapi.testclient import TestClient

from onetimesecret.main import app

client = TestClient(app)


@pytest.fixture
def test_data():
    """
    Fixture that provides common test data for the test cases.

    Returns:
        dict: A dictionary containing:
            - "valid_secret": Contains valid secret data and passphrase.
            - "invalid_passphrase": A passphrase that will not decrypt the secret.
            - "non_existent_key": A secret key that does not exist in the repository.
    """
    return {
        "valid_secret": {
            "secret": "my_secret_data",
            "passphrase": "my_secret_passphrase"
        },
        "invalid_passphrase": "wrong_passphrase",
        "non_existent_key": "non_existent_key"
    }


@pytest.mark.asyncio
async def test_generate_secret(test_data):
    """
    Test case for generating a new secret.

    Sends a POST request to the "/generate" endpoint with valid secret data.
    Asserts that the response status code is 200 (OK) and that a "secret_key" is returned in the response.
    """
    response = client.post("/generate", json=test_data["valid_secret"])
    assert response.status_code == 200
    assert "secret_key" in response.json()


@pytest.mark.asyncio
async def test_get_secret(test_data):
    """
    Test case for retrieving a secret with a valid passphrase.

    First, a secret is generated and then retrieved using the correct passphrase.
    Asserts that the response status code is 200 (OK) and that the correct secret is returned.
    """
    create_response = client.post("/generate", json=test_data["valid_secret"])
    assert create_response.status_code == 200

    secret_key = create_response.json()["secret_key"]

    get_response = client.post(f"/secrets/{secret_key}",
                               json={"passphrase": test_data["valid_secret"]["passphrase"]})
    assert get_response.status_code == 200
    assert get_response.json()["secret"] == test_data["valid_secret"]["secret"]


@pytest.mark.asyncio
async def test_get_secret_invalid_passphrase(test_data):
    """
    Test case for retrieving a secret with an invalid passphrase.

    First, a secret is generated. Then, an attempt is made to retrieve it using an incorrect passphrase.
    Asserts that the response status code is 400 (Bad Request).
    """
    create_response = client.post("/generate", json=test_data["valid_secret"])
    assert create_response.status_code == 200

    secret_key = create_response.json()["secret_key"]

    wrong_pass_response = client.post(f"/secrets/{secret_key}",
                                      json={"passphrase": test_data["invalid_passphrase"]})
    assert wrong_pass_response.status_code == 400


@pytest.mark.asyncio
async def test_get_secret_invalid_secret_key(test_data):
    """
    Test case for retrieving a secret using a non-existent secret key.

    Asserts that the response status code is 404 (Not Found) when trying to access a secret that doesn't exist.
    """
    create_response = client.post("/generate", json=test_data["valid_secret"])
    assert create_response.status_code == 200

    non_existent_key_response = client.post(f"/secrets/{test_data['non_existent_key']}",
                                            json={"passphrase": test_data["valid_secret"]["passphrase"]})
    assert non_existent_key_response.status_code == 404


@pytest.mark.asyncio
async def test_get_secret_again(test_data):
    """
    Test case for ensuring a secret can only be accessed once.

    First, a secret is generated and successfully retrieved. Then, a second attempt to retrieve the same secret is made.
    Asserts that the second attempt returns a 404 (Not Found) since the secret should be deleted after the first access.
    """
    create_response = client.post("/generate", json=test_data["valid_secret"])
    assert create_response.status_code == 200

    secret_key = create_response.json()["secret_key"]

    get_response = client.post(f"/secrets/{secret_key}",
                               json={"passphrase": test_data["valid_secret"]["passphrase"]})
    assert get_response.status_code == 200
    assert get_response.json()["secret"] == test_data["valid_secret"]["secret"]

    second_get_response = client.post(f"/secrets/{secret_key}",
                                      json={"passphrase": test_data["valid_secret"]["passphrase"]})
    assert second_get_response.status_code == 404
    assert second_get_response.json()["detail"] == "There is no such secret"








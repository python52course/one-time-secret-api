import pytest

from fastapi.testclient import TestClient
from onetimesecret.main import app, secret_service

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_repository():
    """
    Fixture to clear the repository data before each test.
    """
    secret_service.repository.data.clear()


def test_generate_secret_success():
    """
    Test the successful generation of a secret.
    """
    response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
    assert response.status_code == 200
    response_data = response.json()
    assert "secret_key" in response_data
    secret_key = response_data["secret_key"]
    stored_secret = secret_service.repository.data.get(secret_key)
    assert stored_secret is not None
    assert stored_secret.secret != "my_secret"
    assert stored_secret.passphrase != "my_passphrase"


def test_generate_secret_missing_fields():
    """
    Test the handling of missing fields in the request.
    """
    response = client.post("/generate", json={"secret": "my_secret"})
    assert response.status_code == 422
    response = client.post("/generate", json={"passphrase": "my_passphrase"})
    assert response.status_code == 422


def test_get_secret_success():
    """
    Test retrieval of a secret with valid secret_key and passphrase.
    """
    generate_response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
    assert generate_response.status_code == 200
    secret_key = generate_response.json()["secret_key"]

    retrieve_response = client.post(f"/secrets/{secret_key}", json={"passphrase": "my_passphrase"})
    assert retrieve_response.status_code == 200
    response_data = retrieve_response.json()
    assert response_data["secret"] == "my_secret"


def test_get_secret_invalid_key():
    """
    Test retrieval of a secret with an invalid secret_key.
    """
    response = client.post("/secrets/invalid_key", json={"passphrase": "my_passphrase"})
    assert response.status_code == 404
    assert response.json()["detail"] == "An invalid secret key or a secret with such a secret key was not found"


def test_get_secret_invalid_passphrase():
    """
    Test retrieval of a secret with an incorrect passphrase.
    """
    generate_response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
    assert generate_response.status_code == 200
    secret_key = generate_response.json()["secret_key"]

    retrieve_response = client.post(f"/secrets/{secret_key}", json={"passphrase": "wrong_passphrase"})
    assert retrieve_response.status_code == 404
    assert retrieve_response.json()["detail"] == "Invalid passphrase"


def test_get_secret_already_retrieved():
    """
    Test retrieval of a secret that has already been retrieved.
    """
    generate_response = client.post("/generate", json={"secret": "my_secret", "passphrase": "my_passphrase"})
    assert generate_response.status_code == 200
    secret_key = generate_response.json()["secret_key"]

    retrieve_response = client.post(f"/secrets/{secret_key}", json={"passphrase": "my_passphrase"})
    assert retrieve_response.status_code == 200

    second_retrieve_response = client.post(f"/secrets/{secret_key}", json={"passphrase": "my_passphrase"})
    assert second_retrieve_response.status_code == 404
    assert second_retrieve_response.json()["detail"] == "An invalid secret key or a secret with such a secret key was not found"


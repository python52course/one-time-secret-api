# One Time Secret

## Table of Contents
- [Project Description](#project-description)
- [Installation and Setup](#installation-and-setup)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
  - [4. Run the Project](#4-run-the-project)
  - [5. Run Tests](#5-run-tests)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
  - [1. Generate Secret](#1-generate-secret)
  - [2. Retrieve Secret](#2-retrieve-secret)
- [Notes](#notes)


## Project Description

This project implements a service for securely storing and sharing one-time secrets. Secrets can be encrypted using a password provided by the user and then retrieved using a unique key. Once a secret is requested and decrypted, it is automatically deleted from the database, ensuring one-time access.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/python52course/one-time-secret-api
cd one-time-secret-api
```
### 2. Install Dependencies
The project uses Poetry for dependency management. Ensure Poetry is installed, then run the following command to install all dependencies:
```bash
poetry install
```

### 3. Configure Environment Variables
Create a .env file in the root directory of the project by copying the contents of the .env.example file. This file should contain sensitive data such as SALT and MONGODB_URI.

Example content of .env.example:
```bash
SALT="your_salt_here"
MONGODB_URI="your_mongodb_uri_here"
```
Environment variables:
* SALT — The salt used for generating cryptographic keys.
* MONGODB_URI — The URI for connecting to the MongoDB database.

### 4. Run the Project
To start the server, use the following command:
```bash
poetry run uvicorn onetimesecret.main:app --reload
```
The server will be available at http://127.0.0.1:8000

### 5. Run Tests
The project includes tests that can be run using pytest. Ensure you have a local instance of MongoDB running, then execute the following command:
```bash
poetry run pytest
```
This will run all tests, including those for encryption utilities, database operations, and API endpoints.

## Project Structure
```plaintext
one-time-secret-api/
│
├── onetimesecret/
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Configuration and environment variables loading
│   ├── database.py        # MongoDB repository and connection handling
│   ├── main.py            # Main application setup with FastAPI
│   ├── models.py          # Pydantic models for API requests/responses and database schema
│   ├── services.py        # Core logic for generating and retrieving secrets
│   └── utils.py           # Helper functions for encryption/decryption
│
└── tests/
    ├── __init__.py        # Test package initialization
    ├── test_main.py       # Integration tests for FastAPI endpoints
    └── test_utils.py      # Unit tests for utility functions


```
## API Endpoints

### 1. Generate Secret
#### POST /generate
Description: Generates a new secret and returns a unique key.

Request Body:
```json
{
  "secret": "your_secret",
  "passphrase": "your_passphrase"
}
```
Example Response:
```json
{
  "secret_key": "generated_secret_key"
}
```
### 2. Retrieve Secret
#### POST /secrets/{secret_key}
Description: Retrieves a secret by its unique key and password.

Path Parameters: secret_key — The unique key obtained when the secret was created.

Request Body:
```json
{
  "passphrase": "your_passphrase"
}
```
Example Response:
```json
{
  "secret": "your_decrypted_secret"
}
```
## Notes
* Ensure that MongoDB is installed and running before starting the application and running tests.
* Secrets are encrypted before storage and are never stored in plaintext.
* Secrets are automatically deleted from the database after they have been retrieved.
* A TTL (Time-to-Live) index is configured in MongoDB to automatically delete secrets after a specified time, even if they haven't been accessed.
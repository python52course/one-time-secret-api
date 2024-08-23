from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from onetimesecret.models import Secret


class Repository:
    def __init__(self, uri: str):
        """
        Initializes a new instance of the Repository class.

        Args:
            uri (str): The URI for connecting to the MongoDB database.
        """
        self.__client = AsyncIOMotorClient(uri)
        self.__db = self.__client['secret_db']
        self.__collection = self.__db['secrets']

    async def initialize_indexes(self):
        """
        Initializes indexes in the MongoDB collection.
        Creates an index on the 'expiration' field with an expiration time of 1 second if it does not already exist.
        """
        existing_indexes = await self.__collection.index_information()
        if 'expiration_1' not in existing_indexes:
            await self.__collection.create_index([('expiration', 1)], expireAfterSeconds=1)

    async def close(self):
        """
        Closes the connection to the MongoDB client.
        """
        self.__client.close()

    async def create(self, secret: Secret) -> None:
        """
        Inserts a new secret document into the collection. Uses the 'secret_key' field
        as the '_id' field in the MongoDB document.

        Args:
            secret (Secret): The secret object to be inserted, with fields 'id', 'secret', and 'expiration'.
        """
        secret_dict = secret.model_dump()
        secret_dict['_id'] = secret_dict.pop('secret_key')
        await self.__collection.insert_one(secret_dict)

    async def get(self, secret_key: str) -> Optional[str]:
        """
        Retrieves a secret from the collection using the secret key (which is used as '_id').

        Args:
            secret_key (str): The key of the secret to retrieve, which corresponds to '_id' in MongoDB.

        Returns:
            Optional[str]: The secret if found, otherwise None.
        """
        secret = await self.__collection.find_one({"_id": secret_key})
        return secret["secret"] if secret else None

    async def delete(self, secret_key: str) -> None:
        """
        Deletes a secret from the collection using the secret key (which is used as '_id').

        Args:
            secret_key (str): The key of the secret to delete, which corresponds to '_id' in MongoDB.
        """
        await self.__collection.delete_one({"_id": secret_key})

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket


MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)


database = client.get_database('test')

movie_collection = database.get_collection('movies')

# Initialize GridFS bucket
grid_fs = AsyncIOMotorGridFSBucket(database)

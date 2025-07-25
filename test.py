from pymongo import MongoClient

client = MongoClient('host.docker.internal', 27018, serverSelectionTimeoutMS=3000)
print(client.server_info())

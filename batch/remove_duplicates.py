import pymongo
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client["adverse_db"]
collection_batches = db["adverse_db"]
cursor = collection_batches.find({})

UniqueWeblink = []

for document in cursor:
    if document["Web link of news"] in UniqueWeblink:
        collection_batches.remove(document)
        continue
    else:
        UniqueWeblink.append(document["Web link of news"])
        # collection_batches.save(document)

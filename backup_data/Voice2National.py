import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil.parser import parse


client = MongoClient("localhost", 27017)
db = client["adverse_db"]
collection_batches = db["adverse_db"]
cursor = collection_batches.find({})

for document in cursor:
    if document["City of News Paper"] == "Voices":
        print("found: ", document)
        document["City of News Paper"] = "National"
        collection_batches.save(document)

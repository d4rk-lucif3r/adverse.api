import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil.parser import parse


client = MongoClient("localhost", 27017)
db = client["adverse_db"]
collection_batches = db["adverse_db"]
cursor = collection_batches.find({})

for document in cursor:
    if document["City/ State mentioned under the news"] == "Satija":
        print("found: ", document)
        document["City/ State mentioned under the news"] = document[
            "City/ State mentioned under the news"
        ].split(",")
        document["City/ State mentioned under the news"] = [
            x.strip()
            for x in document["City/ State mentioned under the news"]
            if x.strip()
        ]
        document["City/ State mentioned under the news"] = [
            x for x in document["City/ State mentioned under the news"] if x != "Satija"
        ]
        document["City/ State mentioned under the news"] = ", ".join(
            document["City/ State mentioned under the news"]
        )
        collection_batches.save(document)

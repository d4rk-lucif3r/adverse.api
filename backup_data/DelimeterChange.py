import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil.parser import parse


client = MongoClient("localhost", 27017)
db = client["adverse_db"]
collection_batches = db["adverse_db"]
cursor = collection_batches.find({})

print("looking through documents..............")
for document in cursor:
    if "Person Name mentioned in the news" in document.keys():
        if document["Person Name mentioned in the news"]:
            document["Person Name mentioned in the news"] = document[
                "Person Name mentioned in the news"
            ].split("|")
            document["Person Name mentioned in the news"] = [
                x.strip()
                for x in document["Person Name mentioned in the news"]
                if x.strip()
            ]
            document["Person Name mentioned in the news"] = " | ".join(
                document["Person Name mentioned in the news"]
            )

    if "Organization Name mentioned in the news" in document.keys():
        if document["Organization Name mentioned in the news"]:
            document["Organization Name mentioned in the news"] = document[
                "Organization Name mentioned in the news"
            ].split("|")
            document["Organization Name mentioned in the news"] = [
                x.strip()
                for x in document["Organization Name mentioned in the news"]
                if x.strip()
            ]
            document["Organization Name mentioned in the news"] = " | ".join(
                document["Organization Name mentioned in the news"]
            )

    if "City/ State mentioned under the news" in document.keys():
        if document["City/ State mentioned under the news"]:
            document["City/ State mentioned under the news"] = document[
                "City/ State mentioned under the news"
            ].split("|")
            document["City/ State mentioned under the news"] = [
                x.strip()
                for x in document["City/ State mentioned under the news"]
                if x.strip()
            ]
            document["City/ State mentioned under the news"] = " | ".join(
                document["City/ State mentioned under the news"]
            )

    collection_batches.save(document)

print("completed parsing documents....................")

import time
import os
import pymongo
from pymongo import MongoClient
import bson
import re

client = MongoClient("localhost", 27017)
db = client["adverse_db"]
collection_batches = db["adverse_db"]

query = re.compile("drug")

posts = collection_batches.find(
    {"Key word Used for identify the article": {"$regex": query}}
)

for post in posts:
    if post["Key word Used for identify the article"] == "crime, drug":
        post["Key word Used for identify the article"] = post[
            "Key word Used for identify the article"
        ].split(",")
        post["Key word Used for identify the article"] = [
            x.strip() for x in post["Key word Used for identify the article"]
        ]
        post["Key word Used for identify the article"] = [
            x for x in post["Key word Used for identify the article"] if x != "drug"
        ]
        post["Key word Used for identify the article"] = ", ".join(
            post["Key word Used for identify the article"]
        )
        collection_batches.update_one(
            {"_id": post["_id"]},
            {"$set": {"Key word Used for identify the article": post["Key word Used for identify the article"]}}
        )
    elif post["Key word Used for identify the article"] == "drug, narcotics":
        post["Key word Used for identify the article"] = post[
            "Key word Used for identify the article"
        ].split(",")
        post["Key word Used for identify the article"] = [
            x.strip() for x in post["Key word Used for identify the article"]
        ]
        post["Key word Used for identify the article"] = [
            x for x in post["Key word Used for identify the article"] if x != "drug"
        ]
        post["Key word Used for identify the article"] = ", ".join(
            post["Key word Used for identify the article"]
        )
        collection_batches.update_one(
            {"_id": post["_id"]},
            {"$set": {"Key word Used for identify the article": post["Key word Used for identify the article"]}}
        )
    elif post["Key word Used for identify the article"] == "narcotics, drug":
        post["Key word Used for identify the article"] = post[
            "Key word Used for identify the article"
        ].split(",")
        post["Key word Used for identify the article"] = [
            x.strip() for x in post["Key word Used for identify the article"]
        ]
        post["Key word Used for identify the article"] = [
            x for x in post["Key word Used for identify the article"] if x != "drug"
        ]
        post["Key word Used for identify the article"] = ", ".join(
            post["Key word Used for identify the article"]
        )
        collection_batches.update_one(
            {"_id": post["_id"]},
            {"$set": {"Key word Used for identify the article": post["Key word Used for identify the article"]}}
        )
    elif post["Key word Used for identify the article"] == "terror, drug":
        post["Key word Used for identify the article"] = post[
            "Key word Used for identify the article"
        ].split(",")
        post["Key word Used for identify the article"] = [
            x.strip() for x in post["Key word Used for identify the article"]
        ]
        post["Key word Used for identify the article"] = [
            x for x in post["Key word Used for identify the article"] if x != "drug"
        ]
        post["Key word Used for identify the article"] = ", ".join(
            post["Key word Used for identify the article"]
        )
        collection_batches.update_one(
            {"_id": post["_id"]},
            {"$set": {"Key word Used for identify the article": post["Key word Used for identify the article"]}}
        )
    elif post["Key word Used for identify the article"] == "terror, narcotics, drug":
        post["Key word Used for identify the article"] = post[
            "Key word Used for identify the article"
        ].split(",")
        post["Key word Used for identify the article"] = [
            x.strip() for x in post["Key word Used for identify the article"]
        ]
        post["Key word Used for identify the article"] = [
            x for x in post["Key word Used for identify the article"] if x != "drug"
        ]
        post["Key word Used for identify the article"] = ", ".join(
            post["Key word Used for identify the article"]
        )
        collection_batches.update_one(
            {"_id": post["_id"]},
            {"$set": {"Key word Used for identify the article": post["Key word Used for identify the article"]}}
        )
    elif post["Key word Used for identify the article"] == "drug":
        post["Key word Used for identify the article"] = "deleted_this"
        collection_batches.update_one(
            {"_id": post["_id"]},
            {"$set": {"Key word Used for identify the article": post["Key word Used for identify the article"]}}
        )
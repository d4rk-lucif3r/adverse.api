# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
# from crawler.spiders.gov_spider import *
# from postprocess import postprocess
# from scrape import rss2url
import time
import os

# from mongo_ingest import postprocessing
import pymongo
from pymongo import MongoClient
import bson
import re

# bson.objectid.ObjectId

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
        collection_batches.save(post)
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
        collection_batches.save(post)
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
        collection_batches.save(post)
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
        collection_batches.save(post)
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
        collection_batches.save(post)
    elif post["Key word Used for identify the article"] == "drug":
        post[
            "Key word Used for identify the article"
        ] = "deleted_this"  # post["Key word Used for identify the article"].split(',')
        # post["Key word Used for identify the article"] = [x.strip() for x in post["Key word Used for identify the article"]]
        # post["Key word Used for identify the article"] = [x for x in post["Key word Used for identify the article"] if x != 'drug']
        collection_batches.save(post)

    # if post["Key word Used for identify the article"]


# post = collection_batches.find_one({'_id': bson.objectid.ObjectId("6075afa78e015f9c2d1707d9")})
# if post:
#     post["Person Name mentioned in the news"] = post["Person Name mentioned in the news"].split(',')
#     post["Person Name mentioned in the news"] = [x.strip() for x in post["Person Name mentioned in the news"]]
#     post["Person Name mentioned in the news"] = [x for x in post["Person Name mentioned in the news"] if x != 'Mission COVID Suraksha']
#     post["Person Name mentioned in the news"] = ', '.join(post["Person Name mentioned in the news"])
#     post["Organization Name mentioned in the news"] = post["Organization Name mentioned in the news"].split(',')
#     post["Organization Name mentioned in the news"] = [x.strip() for x in post["Organization Name mentioned in the news"]]
#     post["Organization Name mentioned in the news"] = [x for x in post["Organization Name mentioned in the news"] if x != 'Mission COVID Suraksha']
#     post["Organization Name mentioned in the news"] = ', '.join(post["Organization Name mentioned in the news"])
#     collection_batches.save(post)

# post = collection_batches.find_one({'_id': bson.objectid.ObjectId("60818d1b718b65bb65ed51c4")})
# if post:
#     post["Person Name mentioned in the news"] = post["Person Name mentioned in the news"].split(',')
#     post["Person Name mentioned in the news"] = [x.strip() for x in post["Person Name mentioned in the news"]]
#     post["Person Name mentioned in the news"] = [x for x in post["Person Name mentioned in the news"] if x != 'Covishield']
#     post["Person Name mentioned in the news"] = ', '.join(post["Person Name mentioned in the news"])
#     post["Organization Name mentioned in the news"] = post["Organization Name mentioned in the news"].split(',')
#     post["Organization Name mentioned in the news"] = [x.strip() for x in post["Organization Name mentioned in the news"]]
#     post["Organization Name mentioned in the news"] = [x for x in post["Organization Name mentioned in the news"] if x != 'Covishield']
#     post["Organization Name mentioned in the news"] = ', '.join(post["Organization Name mentioned in the news"])
#     collection_batches.save(post)

# post = collection_batches.find_one({'_id': bson.objectid.ObjectId("607d99d2718b65bb65ed5062")})
# if post:
#     post["Person Name mentioned in the news"] = post["Person Name mentioned in the news"].split(',')
#     post["Person Name mentioned in the news"] = [x.strip() for x in post["Person Name mentioned in the news"]]
#     post["Person Name mentioned in the news"] = [x for x in post["Person Name mentioned in the news"] if x != 'Covid']
#     post["Person Name mentioned in the news"] = ', '.join(post["Person Name mentioned in the news"])
#     collection_batches.save(post)

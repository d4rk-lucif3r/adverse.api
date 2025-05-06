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

# Use safe pattern and sanitize input to prevent SQL injection
query_pattern = "drug"
query = re.compile(re.escape(query_pattern))

# Use parameterized query instead of directly embedding user input
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
        # Sanitize data before saving to prevent SQL injection
        sanitized_keywords = ", ".join(
            [re.escape(x) for x in post["Key word Used for identify the article"]]
        )
        post["Key word Used for identify the article"] = sanitized_keywords
        
        # Use update_one with filter to avoid second-order injection
        collection_batches.update_one(
            {"_id": post["_id"]}, 
            {"$set": {"Key word Used for identify the article": sanitized_keywords}}
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
        # Sanitize data before saving to prevent SQL injection
        sanitized_keywords = ", ".join(
            [re.escape(x) for x in post["Key word Used for identify the article"]]
        )
        post["Key word Used for identify the article"] = sanitized_keywords
        
        # Use update_one with filter to avoid second-order injection
        collection_batches.update_one(
            {"_id": post["_id"]}, 
            {"$set": {"Key word Used for identify the article": sanitized_keywords}}
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
        # Sanitize data before saving to prevent SQL injection
        sanitized_keywords = ", ".join(
            [re.escape(x) for x in post["Key word Used for identify the article"]]
        )
        post["Key word Used for identify the article"] = sanitized_keywords
        
        # Use update_one with filter to avoid second-order injection
        collection_batches.update_one(
            {"_id": post["_id"]}, 
            {"$set": {"Key word Used for identify the article": sanitized_keywords}}
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
        # Sanitize data before saving to prevent SQL injection
        sanitized_keywords = ", ".join(
            [re.escape(x) for x in post["Key word Used for identify the article"]]
        )
        post["Key word Used for identify the article"] = sanitized_keywords
        
        # Use update_one with filter to avoid second-order injection
        collection_batches.update_one(
            {"_id": post["_id"]}, 
            {"$set": {"Key word Used for identify the article": sanitized_keywords}}
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
        # Sanitize data before saving to prevent SQL injection
        sanitized_keywords = ", ".join(
            [re.escape(x) for x in post["Key word Used for identify the article"]]
        )
        post["Key word Used for identify the article"] = sanitized_keywords
        
        # Use update_one with filter to avoid second-order injection
        collection_batches.update_one(
            {"_id": post["_id"]}, 
            {"$set": {"Key word Used for identify the article": sanitized_keywords}}
        )
    elif post["Key word Used for identify the article"] == "drug":
        post[
            "Key word Used for identify the article"
        ] = "deleted_this"  
        # Use update_one with filter to avoid second-order injection
        collection_batches.update_one(
            {"_id": post["_id"]}, 
            {"$set": {"Key word Used for identify the article": "deleted_this"}}
        )

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

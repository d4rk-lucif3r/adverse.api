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

# Sanitize regex pattern to prevent injection
def sanitize_regex(pattern):
    # Ensure the pattern is a string and escape any special regex characters
    if not isinstance(pattern, str):
        return re.escape(str(pattern))
    return re.escape(pattern)

# Safe update method that uses findOneAndUpdate instead of save
def safe_update_document(collection, document_id, update_data):
    try:
        # Use update_one with _id filter for safe update
        result = collection.update_one(
            {"_id": document_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating document: {e}")
        return False

# Use literal string instead of regex to prevent injection
search_term = "drug"
query = re.compile(sanitize_regex(search_term))

# Find documents with sanitized query
posts = collection_batches.find(
    {"Key word Used for identify the article": {"$regex": query}}
)

for post in posts:
    original_value = post["Key word Used for identify the article"]
    updated_value = None
    
    if original_value == "crime, drug":
        keyword_list = original_value.split(",")
        keyword_list = [x.strip() for x in keyword_list]
        keyword_list = [x for x in keyword_list if x != "drug"]
        updated_value = ", ".join(keyword_list)
    
    elif original_value == "drug, narcotics":
        keyword_list = original_value.split(",")
        keyword_list = [x.strip() for x in keyword_list]
        keyword_list = [x for x in keyword_list if x != "drug"]
        updated_value = ", ".join(keyword_list)
    
    elif original_value == "narcotics, drug":
        keyword_list = original_value.split(",")
        keyword_list = [x.strip() for x in keyword_list]
        keyword_list = [x for x in keyword_list if x != "drug"]
        updated_value = ", ".join(keyword_list)
    
    elif original_value == "terror, drug":
        keyword_list = original_value.split(",")
        keyword_list = [x.strip() for x in keyword_list]
        keyword_list = [x for x in keyword_list if x != "drug"]
        updated_value = ", ".join(keyword_list)
    
    elif original_value == "terror, narcotics, drug":
        keyword_list = original_value.split(",")
        keyword_list = [x.strip() for x in keyword_list]
        keyword_list = [x for x in keyword_list if x != "drug"]
        updated_value = ", ".join(keyword_list)
    
    elif original_value == "drug":
        updated_value = "deleted_this"
    
    # Update document if changes were made
    if updated_value is not None:
        update_data = {"Key word Used for identify the article": updated_value}
        safe_update_document(collection_batches, post["_id"], update_data)

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

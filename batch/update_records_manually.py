# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
# from crawler.spiders.gov_spider import *
# from postprocess import postprocess
# from scrape import rss2url
import time
import os
import html
import re

# from mongo_ingest import postprocessing
import pymongo
from pymongo import MongoClient
import bson

# bson.objectid.ObjectId

client = MongoClient("localhost", 27017)
db = client["adverse_db"]
collection_batches = db["adverse_db"]

def is_safe_keyword(keyword):
    """Validate keyword is safe and contains no SQL injection patterns."""
    if not isinstance(keyword, str):
        return False
    # Check for common SQL injection patterns
    unsafe_patterns = [
        r'(?i)(\%27)|(\')|(\-\-)|(\%23)|(#)',
        r'(?i)((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(\;))',
        r'(?i)(\%27)|(\')|(\-\-)|(\%3B)|(\%23)|(#)',
        r'(?i)union\s+select',
        r'(?i)insert\s+into',
        r'(?i)drop\s+table',
        r'(?i)select\s+.*\s+from',
        r'(?i)delete\s+from'
    ]
    
    for pattern in unsafe_patterns:
        if re.search(pattern, keyword):
            return False
    return True

def sanitize_string(string_value):
    """Sanitize string by escaping HTML and removing potential SQL injection patterns"""
    if not isinstance(string_value, str):
        return string_value
    
    # Escape HTML special characters
    sanitized = html.escape(string_value)
    
    # Remove potentially dangerous SQL patterns
    sanitized = re.sub(r'(?i)select|update|delete|insert|drop|alter|exec|union|where|from', '', sanitized)
    
    return sanitized

# Use a compiled regex pattern for searching
query_pattern = re.compile("drug")

# Use parameterized query with secure filter
posts = collection_batches.find(
    {"Key word Used for identify the article": {"$regex": query_pattern}}
)

for post in posts:
    # Validate the retrieved data before processing
    keyword = post.get("Key word Used for identify the article", "")
    
    # Skip processing if the field is missing or invalid
    if not keyword or not is_safe_keyword(keyword):
        continue
    
    # Sanitize the keyword
    safe_keyword = sanitize_string(keyword)
    
    # Safe processing based on validated content
    if safe_keyword == "crime, drug":
        keyword_parts = safe_keyword.split(",")
        keyword_parts = [x.strip() for x in keyword_parts]
        keyword_parts = [x for x in keyword_parts if x != "drug"]
        post["Key word Used for identify the article"] = ", ".join(keyword_parts)
        collection_batches.save(post)
    elif safe_keyword == "drug, narcotics":
        keyword_parts = safe_keyword.split(",")
        keyword_parts = [x.strip() for x in keyword_parts]
        keyword_parts = [x for x in keyword_parts if x != "drug"]
        post["Key word Used for identify the article"] = ", ".join(keyword_parts)
        collection_batches.save(post)
    elif safe_keyword == "narcotics, drug":
        keyword_parts = safe_keyword.split(",")
        keyword_parts = [x.strip() for x in keyword_parts]
        keyword_parts = [x for x in keyword_parts if x != "drug"]
        post["Key word Used for identify the article"] = ", ".join(keyword_parts)
        collection_batches.save(post)
    elif safe_keyword == "terror, drug":
        keyword_parts = safe_keyword.split(",")
        keyword_parts = [x.strip() for x in keyword_parts]
        keyword_parts = [x for x in keyword_parts if x != "drug"]
        post["Key word Used for identify the article"] = ", ".join(keyword_parts)
        collection_batches.save(post)
    elif safe_keyword == "terror, narcotics, drug":
        keyword_parts = safe_keyword.split(",")
        keyword_parts = [x.strip() for x in keyword_parts]
        keyword_parts = [x for x in keyword_parts if x != "drug"]
        post["Key word Used for identify the article"] = ", ".join(keyword_parts)
        collection_batches.save(post)
    elif safe_keyword == "drug":
        post["Key word Used for identify the article"] = "deleted_this"
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

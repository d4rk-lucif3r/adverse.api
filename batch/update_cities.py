import pymongo
from pymongo import MongoClient
import re

client = MongoClient("localhost", 27017)
db = client["news_ids"]
collection_batches = db["cities"]

# Use a more specific query to reduce attack surface
safe_query = {"cities": {"$exists": True}}
cursor = collection_batches.find(safe_query)

def sanitize_string(input_str):
    """Sanitize string input to prevent SQL injection"""
    if not isinstance(input_str, str):
        return ""
    # Remove any potentially dangerous SQL patterns
    sanitized = re.sub(r'[;\'\"\\]', '', input_str)
    return sanitized

for document in cursor:
    # Validate document has expected structure before processing
    if not isinstance(document, dict) or "cities" not in document:
        continue
        
    # Sanitize input data before processing
    cities_str = sanitize_string(document.get("cities", ""))
    
    # Process the sanitized data
    cities_list = cities_str.split(",")
    cities_list = [x.strip() for x in cities_list]
    cities_list = [x for x in cities_list if x.lower() != "got"]
    cities_list = list(set(cities_list))
    
    # Sanitize the output before saving
    sanitized_cities = ", ".join(cities_list)
    
    # Update document with sanitized data
    document["cities"] = sanitized_cities
    
    # Use update_one with query filter instead of save() for safer operations
    collection_batches.update_one(
        {"_id": document["_id"]}, 
        {"$set": {"cities": sanitized_cities}}
    )

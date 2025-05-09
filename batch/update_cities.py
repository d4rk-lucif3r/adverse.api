import pymongo
from pymongo import MongoClient
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to validate and sanitize city names
def validate_city_name(city):
    # Only allow alphanumeric characters, spaces, and hyphens in city names
    # This prevents MongoDB injection attacks
    if not city or not isinstance(city, str):
        return ""
    
    # Remove any potentially dangerous characters
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-]', '', city)
    return sanitized.strip()

try:
    # Connect to database
    client = MongoClient("localhost", 27017)
    db = client["news_ids"]
    collection_batches = db["cities"]
    
    # Fetch all documents that need processing
    cursor = collection_batches.find({})
    
    for document in cursor:
        try:
            doc_id = document.get("_id")
            
            # Check if cities field exists and is a string
            if "cities" not in document or not isinstance(document["cities"], str):
                logger.warning(f"Document {doc_id} has invalid cities field, skipping")
                continue
                
            # Process cities with proper validation
            cities_raw = document["cities"].split(",")
            cities_sanitized = [validate_city_name(x) for x in cities_raw]
            cities_filtered = [x for x in cities_sanitized if x and x.lower() != "got"]
            cities_unique = list(set(cities_filtered))
            cities_processed = ", ".join(cities_unique)
            
            # Use update_one with parameter binding instead of save()
            # This avoids direct injection of user-controlled data
            collection_batches.update_one(
                {"_id": doc_id},
                {"$set": {"cities": cities_processed}}
            )
            
            logger.info(f"Successfully updated document {doc_id}")
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            continue
            
except Exception as e:
    logger.error(f"Database operation failed: {str(e)}")

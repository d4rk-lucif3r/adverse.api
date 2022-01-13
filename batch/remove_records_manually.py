from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client["adverse_db"]
collection_batches = db["adverse_db"]
cursor = collection_batches.remove(
    {
        "Key word Used for identify the article": {
            "$in": [
                "HDFC",
                "attack",
                "crime",
                "devastating",
                "economy",
                "extortion",
                "fraud",
                "fraud, HDFC",
                "politics",
                "revenue",
            ]
        }
    }
)
print("records has been deleted successfully")

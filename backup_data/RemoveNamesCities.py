import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil.parser import parse
import pandas as pd

client = MongoClient("localhost", 27017)
db = client["news_ids"]
collection_cities = db["cities"]
collection_names = db["names"]
collection_fp_list = db["fp_list"]
cursor_cities = collection_cities.find({})
cursor_fp_list = collection_fp_list.find({})
cursor_names = collection_names.find({})

save_df = {}
cities = []
names = []
fp_name = []
fp_city = []

for document in cursor_cities:
    document["cities"] = document["cities"].split(",")
    document["cities"] = [x.strip() for x in document["cities"] if x.strip()]
    document["cities"] = list(set(document["cities"]))
    document["cities"] = [x.strip() for x in document["cities"] if x != "Bawana"]
    document["cities"] = ", ".join(document["cities"])
    collection_cities.save(document)


for document in cursor_names:
    document["names"] = document["names"].split(",")
    document["names"] = [x.strip() for x in document["names"] if x.strip()]
    document["names"] = list(set(document["names"]))
    document["names"] = [x.strip() for x in document["names"] if x != "Bawana"]
    document["names"] = ", ".join(document["names"])
    collection_names.save(document)

for document in cursor_fp_list:
    document["fp_city"] = document["fp_city"].split(",")
    document["fp_city"] = [x.strip() for x in document["fp_city"] if x.strip()]
    document["fp_city"] = list(set(document["fp_city"]))

    document["fp_name"] = document["fp_name"].split(",")
    document["fp_name"] = [x.strip() for x in document["fp_name"] if x.strip()]
    document["fp_name"] = list(set(document["fp_name"]))
    # document['fp_city'] = [x.strip() for x in document['fp_city'] if x != 'NSCBI']
    # document['fp_name'] = [x.strip() for x in document['fp_name'] if x != 'NSCBI']
    # document['fp_city'] = [x.strip() for x in document['fp_city'] if x != 'CBI']
    # document['fp_name'] = [x.strip() for x in document['fp_name'] if x != 'CBI']
    document["fp_city"] = [x.strip() for x in document["fp_city"] if x != "Bawana"]
    document["fp_name"] = [x.strip() for x in document["fp_name"] if x != "Bawana"]
    document["fp_city"] = ", ".join(document["fp_city"])
    document["fp_name"] = ", ".join(document["fp_name"])
    collection_fp_list.save(document)

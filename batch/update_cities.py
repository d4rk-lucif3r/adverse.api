import pymongo
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['news_ids']
collection_batches = db['cities']
cursor = collection_batches.find({})

for document in cursor:
#     print(document)
    document['cities'] = document['cities'].split(',')
    document['cities'] = [x.strip() for x in document['cities']]
    document['cities'] = [x for x in document['cities'] if x.lower() != 'got']
    document['cities'] = list(set(document['cities']))
    document['cities'] = ', '.join(document['cities'])
    collection_batches.save(document)

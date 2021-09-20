import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil.parser import parse


client = MongoClient('localhost', 27017)
db = client['adverse_db']
collection_batches = db['adverse_db']
cursor = collection_batches.find({})

# September1st = datetime.now() - timedelta(days=16)
# September1st = September1st.strftime("%Y-%m-%d %H:%M:%S")
September1st = "2021-09-01 00:00:00"
print('date: ', September1st)

for document in cursor:
        if "Article Date" in document.keys():
                try:
                        ArticleDate = parse(document["Article Date"].split('+')[0])
                        ArticleDate = ArticleDate.strftime("%Y-%m-%d %H:%M:%S")

                        if ArticleDate >= September1st:
                                continue
                        else:
                                collection_batches.delete_one(document)
                except Exception as e:
                        print(document)
                        print('exception:', e)
                        continue

        if "created_date" in document.keys():
                CreatedDate = parse(document["created_date"])
                CreatedDate = CreatedDate.strftime("%Y-%m-%d %H:%M:%S")

                if CreatedDate >= September1st:
                        continue
                else:
                        collection_batches.delete_one(document)

        if "updated_date" in document.keys():
                UpdatedDate = parse(document["updated_date"])
                UpdatedDate = UpdatedDate.strftime("%Y-%m-%d %H:%M:%S")

                if UpdatedDate >= September1st:
                        continue
                else:
                        collection_batches.delete_one(document)

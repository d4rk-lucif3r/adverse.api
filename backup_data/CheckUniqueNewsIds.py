import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil.parser import parse
import pandas as pd

client = MongoClient('localhost', 27017)
db = client['news_ids']
collection_cities = db['cities']
collection_names = db['names']
collection_fp_list = db['fp_list']
cursor_cities = collection_cities.find({})
cursor_fp_list = collection_fp_list.find({})
cursor_names = collection_names.find({})

save_df = {}
cities = []
names = []
fp_name = []
fp_city = []

for document in cursor_cities:
        document['cities'] = document['cities'].split(',')
        document['cities'] = [x.strip() for x in document['cities'] if x.strip()]
        document['cities'] = list(set(document['cities']))
        cities.extend(document['cities'])
        # pd.DataFrame(document['cities'], columns='cities').to_csv('Cities.csv', index=None)
        # save_df['cities'] = ', '.join(document['cities'])
        # collection_cities.save(document)

pd.DataFrame(data=cities, index=range(len(cities)), columns=['cities']).to_csv('Cities.csv', index=None)

for document in cursor_names:
        document['names'] = document['names'].split(',')
        document['names'] = [x.strip() for x in document['names'] if x.strip()]
        document['names'] = list(set(document['names']))
        names.extend(document['names'])
        # save_df['names'] = ', '.join(document['names'])
        # collection_names.save(document)

pd.DataFrame(data=names, index=range(len(names)), columns=['names']).to_csv('names.csv', index=None)

for document in cursor_fp_list:
        document['fp_city'] = document['fp_city'].split(',')
        document['fp_city'] = [x.strip() for x in document['fp_city'] if x.strip()]
        document['fp_city'] = list(set(document['fp_city']))
        fp_city.extend(document['fp_city'])
        # save_df['fp_city'] = ', '.join(document['fp_city'])
        # collection_fp_list.save(document)

        document['fp_name'] = document['fp_name'].split(',')
        document['fp_name'] = [x.strip() for x in document['fp_name'] if x.strip()]
        document['fp_name'] = list(set(document['fp_name']))
        fp_name.extend(document['fp_name'])
        # save_df['fp_name'] = ', '.join(document['fp_name'])
        # collection_fp_list.save(document)

pd.DataFrame(data=fp_name, index=range(len(fp_name)), columns=['fp_name']).to_csv('fp_name.csv', index=None)

pd.DataFrame(data=fp_city, index=range(len(fp_city)), columns=['fp_city']).to_csv('fp_city.csv', index=None)

# df = pd.DataFrame([save_df])
# df.to_csv('extras.csv', index=None)
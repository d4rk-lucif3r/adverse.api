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
# bson.objectid.ObjectId

from incre_mode import _incre_mode

def current_ids():
    '''
    function to retrieve current ids from mongodb
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['news_ids']
    cursor = collection_batches.find({})
    dbs = [database for database in cursor]
    return dbs[-1]

def detail_status(start_time, date):
    '''
    function to save batch table in mongodb
    '''
    batch = {}
    client = MongoClient('localhost', 27017)
    db = client['BatchRunStatus']
    collection_batches = db['DetailStatus']
    batch["RunDate"] = date
    batch["RunStartTime"] = start_time
    # batch["BatchRunStatus"] = status
    # batch["RunEndTime"] = end_time
    # batch["RunDuration"] = batch["RunEndTime"] - batch["RunStartTime"]
    ids = collection_batches.insert_one(batch)
    # print("Batch Run ingesting into DB")
    # collection_batches.create_index([("DetailStatus", pymongo.ASCENDING)])
    # print("BatchId is created")
    return ids.inserted_id

def update_detail_status(_id, end_time, date, status, ids):
    '''
    function to save batch table in mongodb
    '''
    batch = {}
    client = MongoClient('localhost', 27017)
    db = client['BatchRunStatus']
    collection_batches = db['DetailStatus']
    post = collection_batches.find_one({'_id': bson.objectid.ObjectId(_id)})
    if post:
        post["BatchRunStatus"] = status
        post["RunEndTime"] = end_time
        post["RunDuration"] = post["RunEndTime"] - post["RunStartTime"]
        post['news_keywords_id'] = ids
        collection_batches.save(post)

    return "Updated Document"
def overall_status(start_time, end_time, date, status):
    '''
    function to save batch table in mongodb
    '''
    batch = {}
    client = MongoClient('localhost', 27017)
    db = client['BatchRunStatus']
    collection_batches = db['OverallStatus']
    batch["RunDate"] = date
    batch["RunStartTime"] = start_time
    batch["BatchRunStatus"] = status
    batch["RunEndTime"] = end_time
    batch["RunDuration"] = batch["RunEndTime"] - batch["RunStartTime"]
    collection_batches.insert(batch)
    # print("Batch Run ingesting into DB")
    collection_batches.create_index([("OverallStatus", pymongo.ASCENDING)])
    # print("BatchId is created")

def run_batch():
    t0 = time.time()
    date = time.strftime("%Y-%m-%d %H:%M:%S")
    start_time = time.time()
    status1 = 'Increment mode started'
    batch_id = detail_status(start_time, date)
    # try:
    status2 = _incre_mode(batch_id)
    # except Exception as e:
        # print(e)
        # status2 = str(e)
    dbs = current_ids()
    end_time = time.time()
    update_detail_status(batch_id, end_time, date, status2, str(dbs['_id']))
    # detail_status(start_time, end_time, date, status2)
    overall_status(t0, end_time, date, status2)
    
if __name__ == "__main__":
    run_batch()

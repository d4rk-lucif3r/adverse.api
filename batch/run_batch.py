from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.gov_spider import *
from postprocess import postprocess
from scrape import rss2url
import time
import os
from mongo_ingest import postprocessing
import pymongo
from pymongo import MongoClient

def detail_status(start_time, end_time, date, status):
    '''
    function to save batch table in mongodb
    '''
    batch = {}
    client = MongoClient('localhost', 27017)
    db = client['BatchRunStatus']
    collection_batches = db['DetailStatus']
    batch["RunDate"] = date
    batch["RunStartTime"] = start_time
    batch["BatchRunStatus"] = status
    batch["RunEndTime"] = end_time
    batch["RunDuration"] = batch["RunEndTime"] - batch["RunStartTime"]
    collection_batches.insert(batch)
    # print("Batch Run ingesting into DB")
    collection_batches.create_index([("DetailStatus", pymongo.ASCENDING)])
    # print("BatchId is created")

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
    date = time.strftime("%Y_%m_%d")
    start_time = time.time()
    status1 = 'Download RSS Feed in Progress'
    detail_status(start_time, -1, date, status1)
    # overall_status(start_time, -1, date, status1)
    try:
        if not os.path.isdir("./result_database"):
            os.makedirs("./result_database")
        rss2url()
        print("Getting Updated news from rss feed")
        status1 = 'RSS Feed Complete'
        detail_status(start_time, -1, date, status1)
        process = CrawlerProcess(get_project_settings())
        process.crawl(govSpider)
        process.start()
        end = time.time()
        postprocess()
        postprocessing()
        print("Crawler ran for {} seconds".format(round(end-start,0)))
    except Exception as e:
        status1 = str(e)

    end_time = time.time()
    status1 = 'Batch Run Complete'
    detail_status(start_time, end_time, date, status1)
    overall_status(t0, end_time, date, status1)
    
if __name__ == "__main__":
    run_batch()
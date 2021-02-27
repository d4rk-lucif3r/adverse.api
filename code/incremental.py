import time
import subprocess
import os


import pymongo
from pymongo import MongoClient
import shutil

from Download_dump import json_dump_download
from Wikidata_Politicians_Pass1 import *
from Wikidata_Politicians_Pass2_2 import *
from Wikidata_save_chunks import save_chunks
from Wikidata_Politicians_Postprocessing import *
from Wikidata2mongodb import *
from current_db import *


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
    status1 = 'Starting Crawler'
    detail_status(start_time, end_time, date, status1)
    main()
    end = time.time()
    postprocess()
    detail_status(start_time, end_time, date, status1)
    print("Crawler ran for {} seconds".format(round(end-start,0)))
    overall_status(t0, end_time, date, status1)

if __name__ == '__main__':
    run_batch()

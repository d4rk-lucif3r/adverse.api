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
    """
    function to save batch table in mongodb
    """
    batch = {}
    client = MongoClient("localhost", 27017)
    db = client["BatchRunStatus"]
    collection_batches = db["DetailStatus"]
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
    """
    function to save batch table in mongodb
    """
    batch = {}
    client = MongoClient("localhost", 27017)
    db = client["BatchRunStatus"]
    collection_batches = db["OverallStatus"]
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
    status1 = "Download Dump in Progress"
    detail_status(start_time, -1, date, status1)
    # overall_status(start_time, -1, date, status1)

    try:
        # start download dump
        status1 = json_dump_download()
    except Exception as e:
        status1 = str(e)

    end_time = time.time()
    detail_status(start_time, end_time, date, status1)
    overall_status(t0, end_time, date, status1)

    if (status1 == "File Download Complete") or (
        status1 == "File already exist, Please check directory"
    ):
        # if 'File' in status1:
        start_time = time.time()
        status2 = "Pass1 In Progress"
        detail_status(start_time, -1, date, status2)

        try:
            # start pass1
            status2 = main_pass1()
        except Exception as e:
            status2 = str(e)

        end_time = time.time()
        detail_status(start_time, end_time, date, status2)
        overall_status(t0, end_time, date, status2)

        if status2 == "Pass1 Complete":
            # if 'Complete' in status2:
            start_time = time.time()
            status3 = "Pass2 In Progress"
            detail_status(start_time, -1, date, status3)

            try:
                # start pass2
                status3 = final_replacement(
                    os.path.abspath(os.path.join(os.getcwd(), "data_temp/"))
                )
            except Exception as e:
                status3 = str(e)

            end_time = time.time()
            detail_status(start_time, end_time, date, status3)
            overall_status(t0, end_time, date, status3)

            if "Complete" in status3:
                start_time = time.time()
                status4 = "Postprocessing Wikidata In Progress"
                detail_status(start_time, -1, date, status4)

                try:
                    # post process wikidata
                    status4 = postprocessing()
                except Exception as e:
                    status4 = str(e)

                end_time = time.time()
                detail_status(start_time, end_time, date, status4)
                overall_status(t0, end_time, date, status4)

                if "Complete" in status4:
                    start_time = time.time()
                    status5 = "Ingesting Wikidata into MongoDB In Progress"
                    detail_status(start_time, -1, date, status5)

                    try:
                        fns = [
                            "wiki1_db.json",
                            "wiki2_db.json",
                            "wiki3_db.json",
                            "wiki4_db.json",
                            "wiki5_db.json",
                            "wiki6_db.json",
                            "wiki7_db.json",
                            "wiki8_db.json",
                            "wiki9_db.json",
                        ]
                        secondary = find_secondary()
                        # drop secondary if exist
                        drop_secondary(secondary)
                        # save secondary database into monogdb
                        status5 = wikidata2mongodb(secondary, fns)
                    except Exception as e:
                        status5 = str(e)

                    end_time = time.time()
                    detail_status(start_time, end_time, date, status5)
                    overall_status(t0, end_time, date, status5)

                    if "Complete" in status5:
                        start_time = time.time()
                        status6 = "Indexing Wikidata into Elasticsearch In Progress"
                        detail_status(start_time, -1, date, status6)

                        try:
                            # get current secondary database
                            current_databases = current_dbs()
                            secondary = current_databases["Secondary"]
                            primary = current_databases["Primary"]
                            # run elasticsearch
                            os.environ["MONGODB_URI"] = (
                                "mongodb://localhost/%s" % secondary
                            )
                            os.environ["ELASTICSEARCH_URI"] = (
                                "http://localhost:9200/%s" % secondary
                            )
                            cmd = ["transporter", "run", "pipeline.js"]
                            proc = subprocess.Popen(
                                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                            )
                            o, e = proc.communicate()
                            status6 = str(e)

                            print("Updating Primary and Secondary Batch Table")
                            update_dbs(secondary, primary)

                        except Exception as e:
                            status6 = str(e)

                        end_time = time.time()
                        detail_status(start_time, end_time, date, status6)

                        status7 = "Batch Run Successful"

                        detail_status(t0, end_time, date, status7)
                        overall_status(t0, end_time, date, status7)

                        # clear temporary files
                        if status7 == "Batch Run Successful":
                            start_time = time.time()
                            status8 = "Cleaning up temporary files"
                            detail_status(start_time, -1, date, status8)

                            try:
                                status8 = "Cleaning up Elasticsearch"
                                detail_status(start_time, -1, date, status8)
                                # remove primary database
                                url = "http://localhost:9200/%s" % primary
                                # os.environ['ELASTICSEARCH_URI'] = 'http://localhost:9200/%s' % primary
                                cmd = ["curl", "-XDELETE", url]
                                proc = subprocess.Popen(
                                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                                )
                                o, e = proc.communicate()
                                status8 = str(o) + str(e)

                            except Exception as e:
                                status8 = str(e)

                            end_time = time.time()
                            detail_status(start_time, end_time, date, status8)

                            try:
                                status8 = "Cleaning up mongodb files"
                                detail_status(start_time, -1, date, status8)
                                # remove folder *.json files
                                dir_name = os.path.abspath(os.path.join(os.getcwd()))
                                dir_list = os.listdir(dir_name)
                                for _fn in dir_list:
                                    if _fn.endswith(".json"):
                                        os.remove(os.path.join(dir_name, _fn))

                            except Exception as e:
                                status8 = str(e)

                            end_time = time.time()
                            detail_status(start_time, end_time, date, status8)

                            # try:
                            #   status8 = 'Cleaning up folder data_temp'
                            #   detail_status(start_time, -1, date, status8)
                            #     # remove folder data_temp files
                            #     if os.path.isdir(os.path.abspath(os.path.join(os.getcwd(),'data_temp/'))):
                            #       shutil.rmtree(os.path.abspath(os.path.join(os.getcwd(),'data_temp/')))

                            # except Exception as e:
                            #     status8 = str(e)

                            # end_time = time.time()
                            # detail_status(start_time, end_time, date, status8)

                        else:
                            detail_status(start_time, end_time, date, status6)
                            overall_status(t0, end_time, date, status6)
                    else:
                        detail_status(start_time, end_time, date, status5)
                        overall_status(t0, end_time, date, status5)
                else:
                    detail_status(start_time, end_time, date, status4)
                    overall_status(t0, end_time, date, status4)
            else:
                detail_status(start_time, end_time, date, status3)
                overall_status(t0, end_time, date, status3)
        else:
            detail_status(start_time, end_time, date, status2)
            overall_status(t0, end_time, date, status2)
    else:
        detail_status(start_time, end_time, date, status1)
        overall_status(t0, end_time, date, status1)


if __name__ == "__main__":
    run_batch()

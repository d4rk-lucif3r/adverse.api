from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.gov_spider import *
from postprocess import postprocess
from scrape import rss2url
import time
import os

def run_batch():
    start = time.time()
    print("Getting Updated news from rss feed")
    rss2url()
    if not os.path.isdir("./result_database"):
      os.makedirs("./result_database")
    process = CrawlerProcess(get_project_settings())
    process.crawl(govSpider)
    process.start()
    end = time.time()
    postprocess()
    print("Crawler ran for {} seconds".format(round(end-start,0)))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.gov_spider import *
from postprocess import postprocess
from scrape import rss2url
import time
import os

def main():
    print("Getting Updated news from rss feed")
    rss2url()
    if not os.path.isdir("./result_database"):
      os.makedirs("./result_database")
    process = CrawlerProcess(get_project_settings())
    process.crawl(govSpider)
    process.start()

if __name__ == "__main__":
  start = time.time()
  main()
  end = time.time()
  postprocess()
  print("Crawler ran for {} seconds".format(round(end-start,0)))
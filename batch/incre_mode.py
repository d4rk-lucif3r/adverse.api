from datetime import datetime, timedelta
import spacy
from dateutil.parser import parse
import newspaper
from newspaper import Article
import pytz
import csv
import feedparser
from pymongo import MongoClient
from faker import Faker
import pandas as pd
import os
import numpy as np


def subset_dupl(names_list, idxes):

    names_dict = {k:v for k in names_list for v in idxes}

    for k,v in names_dict.items():
        k = k.split(',')
        k = [x.strip() for x in k if x.strip()]
        for k_ in names_list:
            k_ = k_.split(',')
            k_ = [x.strip() for x in k_ if x.strip()]
            if set(k) < set(k_):
                print(k, 'is a subset of ', k_)
                names_dict.pop(k)
                break
            else:
                print(k, 'is not a subset of', k_)

    return list(names_dict.values())

def lowercase_check(x):
    x_dict = {k.lower():k for k in x}
    return list(x_dict.values())
    # x_ = []
    # for _x in x:
    #     z = 0
    #     for _y in x:
    #         if _x == _y:
    #             z = 0
    #             print(_x, 'is equal to', _y)
    #         else:
    #             if _x.lower() == _y.lower():
    #                 z = 1
    #                 print(_x, 'is a lowercase version of', _y)
    #             else:
    #                 print('not a lowercase version')

    #     if z == 0:
    #         x_.append(_x)
    #     else:
    #         print('it is already a lowercase version')

    # return list(set(x_))


def subset(x):
    x_ = []
    for _x in x:
        z = 0
        for _y in x:
            if _x == _y:
                z = 0
                print(_x, 'is equal to', _y)
            else:
                if _x in _y:
                    z = 1
                    print(_x, 'is a subset of', _y)
                else:
                    print('not a subset')
            # elif _x.lower() == _y.lower():
            #     z = 1
            #     print(_x, 'is a lowercase version of', _y)
            # elif _x in _y:
            #     z = 1
            #     print(_x, 'is a subset of', _y)
            # else:
            #     pass
        if z == 0:
            x_.append(_x)
        else:
            print('it is already a subset of')

    return list(set(x_))


def check_duplicate_name(val):
    '''
    function to check if name exist in database with some threshold
    '''
    client = MongoClient('localhost', 27017)
    dbnames = client.list_database_names()
    if 'adverse_db' in dbnames:
      db = client['adverse_db']
      collection_batches = db['adverse_db']
      cursor = collection_batches.find({}, {'_id': False})
      dbs = [database['Person Name mentioned in the news'] for database in cursor]
      val = val.split(',')
      val = [x.strip() for x in val if x.strip()]
      val = set(val)
      for _dict in dbs:
        _dict = _dict.split(',')
        _dict = [x.strip() for x in _dict if x.strip()]
        _dict = set(_dict)
        _dictval = val.intersection(_dict)
        if len(_dictval) > 0.4:
          return 1
        else:
          print('threshold is not greater')
          pass
    else:
      print("adverse_db doesnot exist id database")
      pass

    return 0


def current_ids():
    '''
    function to retrieve current ids from mongodb
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['news_ids']
    cursor = collection_batches.find({}, {'_id': False})
    dbs = [database for database in cursor]
    return dbs[-1]

def fnc_(x):
  try:
    x = x.strip(', ')
    return x
  except:
    return x

def ids2rss(source_news_ids):

    rss = []

    dictionary = {'2cdd8f28-01f5-4d18-b438-742f04fe3140': 'https://prod-qt-images.s3.amazonaws.com/production/bloombergquint/feed.xml',
    '3d4a70cb-fe3f-459e-8cb1-43bc04f759c6': {'Bengaluru': 'https://www.hindustantimes.com/feeds/rss/cities/bengaluru-news/rssfeed.xml', 'Bhopal': 'https://www.hindustantimes.com/feeds/rss/cities/bhopal-news/rssfeed.xml', 'Chandigarh': 'https://www.hindustantimes.com/feeds/rss/cities/chandigarh-news/rssfeed.xml', 'Dehradun': 'https://www.hindustantimes.com/feeds/rss/cities/dehradun-news/rssfeed.xml', 'Delhi': 'https://www.hindustantimes.com/feeds/rss/cities/delhi-news/rssfeed.xml', 'Gurugram': 'https://www.hindustantimes.com/feeds/rss/cities/gurugram-news/rssfeed.xml', 'Indore': 'https://www.hindustantimes.com/feeds/rss/cities/indore-news/rssfeed.xml', 'Jaipur': 'https://www.hindustantimes.com/feeds/rss/cities/jaipur-news/rssfeed.xml', 'Kolkata': 'https://www.hindustantimes.com/feeds/rss/cities/kolkata-news/rssfeed.xml', 'Lucknow': 'https://www.hindustantimes.com/feeds/rss/cities/lucknow-news/rssfeed.xml', 'Mumbai': 'https://www.hindustantimes.com/feeds/rss/cities/mumbai-news/rssfeed.xml', 'Noida' : 'https://www.hindustantimes.com/feeds/rss/cities/noida-news/rssfeed.xml', 'Patna': 'https://www.hindustantimes.com/feeds/rss/cities/patna-news/rssfeed.xml', 'Pune': 'https://www.hindustantimes.com/feeds/rss/cities/pune-news/rssfeed.xml', 'Ranchi': 'https://www.hindustantimes.com/feeds/rss/cities/ranchi-news/rssfeed.xml'},
    '4dfab6d8-8246-469b-9e19-7ddbb55d806d': {'Mumbai': 'https://www.dnaindia.com/feeds/mumbai.xml', 'Delhi': 'https://www.dnaindia.com/feeds/delhi.xml', 'Bangalore': 'https://www.dnaindia.com/feeds/bangalore.xml', 'Pune' : 'https://www.dnaindia.com/feeds/pune.xml', 'Ahmedabad' : 'https://www.dnaindia.com/feeds/ahmedabad.xml'},
    '52d0de86-1525-417d-b8fd-2158f1256c38': 'http://www.allindianewspapers.com/Feeds/states.xml',
    '5b32994e-2e6e-417f-ba44-77f508742349': 'https://www.business-standard.com/rss/home_page_top_stories.rss',
    '65cb3dec-94a9-4274-b518-543c74e14a59': 'https://asia.nikkei.com/rss/feed/nar',
    '6c676cc1-2338-4834-a0fb-9ae8a04a2bda': 'https://www.ft.com/?format=rss',
    '7eba470b-1edc-4f69-840d-99cfde3a5fcb': 'http://www.abc.net.au/news/feed/2942460/rss.xml',
    '890d11b8-05e7-416e-b777-7ba62f4a7045': 'https://www.economist.com/international/rss.xml',
    '8cbc9eec-7255-43bf-bb72-2bce4f4764ea': 'https://feeds.feedburner.com/ndtvnews-cities-news?format=xml',
    '91272662-bb73-4649-a8c2-026d112c190e': 'https://www.livemint.com/rss/news',
    'a70e9599-4480-46d2-889f-652fdd58cc55': {'Delhi': 'https://indianexpress.com/section/cities/delhi/feed/', 'Lucknow' : 'https://www.indianexpress.com/section/cities/lucknow/feed/', 'Pune' : 'https://www.indianexpress.com/section/cities/pune/feed/', 'Chandigarh' : 'https://indianexpress.com/section/cities/chandigarh/feed/', 'Mumbai': 'https://indianexpress.com/section/cities/mumbai/feed/', 'Kolkata' : 'https://indianexpress.com/section/cities/kolkata/feed/', 'Ludhiana' : 'https://indianexpress.com/section/cities/ludhiana/feed/', 'Gujarat': 'https://indianexpress.com/section/india/education/feed/', 'Maharashtra' : 'https://indianexpress.com/section/india/maharashtra/feed/', 'Uttar Pradesh': 'https://indianexpress.com/section/india/uttar-pradesh/feed/', 'West Bengal': 'https://indianexpress.com/section/india/west-bengal/feed/', 'Punjab and Haryana': 'https://indianexpress.com/section/india/punjab-and-haryana/feed/'},
    'a9ecac2e-a7da-4bbd-b326-103de3149ece': 'http://feeds.bbci.co.uk/news/world/rss.xml',
    'ad60ab7b-906b-467d-b29e-92f200eb88fe': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
    'bef37780-c007-4b96-89f4-5198b69f2c93': 'https://www.theguardian.com/world/rss',
    'c1f4a45b-aa9c-4627-980b-f69509e5c862': {'Andhra Pradesh': 'https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss', 'Karnataka': 'https://www.thehindu.com/news/national/karnataka/feeder/default.rss', 'Kerala': 'https://www.thehindu.com/news/national/kerala/feeder/default.rss', 'Tamil Nadu': 'https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss', 'Telangana': 'https://www.thehindu.com/news/national/telangana/feeder/default.rss', 'Bengaluru': 'https://www.thehindu.com/news/cities/bangalore/feeder/default.rss', 'Chennai' : 'https://www.thehindu.com/news/cities/chennai/feeder/default.rss', 'Coimbatore': 'https://www.thehindu.com/news/cities/Coimbatore/feeder/default.rss', 'Delhi': 'https://www.thehindu.com/news/cities/Delhi/feeder/default.rss', 'Hyderabad': 'https://www.thehindu.com/news/cities/Hyderabad/feeder/default.rss', 'Kochi': 'https://www.thehindu.com/news/cities/Kochi/feeder/default.rss', 'Kolkata': 'https://www.thehindu.com/news/cities/kolkata/feeder/default.rss', 'Mumbai': 'https://www.thehindu.com/news/cities/mumbai/feeder/default.rss', 'Kozhikode': 'https://www.thehindu.com/news/cities/kozhikode/feeder/default.rss', 'Madurai': 'https://www.thehindu.com/news/cities/Madurai/feeder/default.rss', 'Mangaluru': 'https://www.thehindu.com/news/cities/Mangalore/feeder/default.rss', 'Puducherry': 'https://www.thehindu.com/news/cities/puducherry/feeder/default.rss', 'Thiruvananthapuram': 'https://www.thehindu.com/news/cities/Thiruvananthapuram/feeder/default.rss', 'Tiruchirapalli': 'https://www.thehindu.com/news/cities/Tiruchirapalli/feeder/default.rss', 'Vijayawada': 'https://www.thehindu.com/news/cities/Vijayawada/feeder/default.rss', 'Visakhapatnam': 'https://www.thehindu.com/news/cities/Visakhapatnam/feeder/default.rss'},
    'ca3c6507-8c4a-4269-a384-8de06f43bc4f': {'Mumbai': 'https://timesofindia.indiatimes.com/rssfeeds/-2128838597.cms', 'Delhi': 'https://timesofindia.indiatimes.com/rssfeeds/-2128839596.cms', 'Bangalore': 'http://timesofindia.indiatimes.com/rssfeeds/-2128833038.cms', 'Hyderabad': 'https://timesofindia.indiatimes.com/rssfeeds/-2128816011.cms', 'Chennai': 'http://timesofindia.indiatimes.com/rssfeeds/2950623.cms', 'Ahemdabad': 'https://timesofindia.indiatimes.com/rssfeeds/-2128821153.cms', 'Allahabad': 'https://timesofindia.indiatimes.com/rssfeeds/3947060.cms', 'Bhubaneswar': 'https://timesofindia.indiatimes.com/rssfeeds/4118235.cms', 'Coimbatore': 'https://timesofindia.indiatimes.com/rssfeeds/7503091.cms', 'Gurgaon': 'https://timesofindia.indiatimes.com/rssfeeds/6547154.cms', 'Guwahati': 'https://timesofindia.indiatimes.com/rssfeeds/4118215.cms', 'Hubli': 'https://timesofindia.indiatimes.com/rssfeeds/3942695.cms', 'Kanpur': 'https://timesofindia.indiatimes.com/rssfeeds/3947067.cms', 'Kolkata': 'https://timesofindia.indiatimes.com/rssfeeds/-2128830821.cms', 'Ludhiana': 'http://timesofindia.indiatimes.com/rssfeeds/3947051.cms', 'Mangalore': 'https://timesofindia.indiatimes.com/rssfeeds/3942690.cms', 'Mysore': 'https://timesofindia.indiatimes.com/rssfeeds/3942693.cms', 'Noida': 'https://timesofindia.indiatimes.com/rssfeeds/8021716.cms', 'Pune': 'https://timesofindia.indiatimes.com/rssfeeds/-2128821991.cms', 'Goa': 'http://timesofindia.indiatimes.com/rssfeeds/3012535.cms', 'Chandigarh': 'https://timesofindia.indiatimes.com/rssfeeds/-2128816762.cms', 'Lucknow': 'https://timesofindia.indiatimes.com/rssfeeds/-2128819658.cms', 'Patna': 'http://timesofindia.indiatimes.com/rssfeeds/-2128817995.cms', 'Jaipur': 'https://timesofindia.indiatimes.com/rssfeeds/3012544.cms', 'Nagpur': 'https://timesofindia.indiatimes.com/rssfeeds/442002.cms', 'Rajkot': 'https://timesofindia.indiatimes.com/rssfeeds/3942663.cms', 'Ranchi': 'https://timesofindia.indiatimes.com/rssfeeds/4118245.cms', 'Surat': 'https://timesofindia.indiatimes.com/rssfeeds/3942660.cms', 'Vadodara': 'https://timesofindia.indiatimes.com/rssfeeds/3942666.cms', 'Varanasi': 'https://timesofindia.indiatimes.com/rssfeeds/3947071.cms', 'Thane': 'https://timesofindia.indiatimes.com/rssfeeds/3831863.cms', 'Thiruvananthapuram': 'https://timesofindia.indiatimes.com/rssfeeds/878156304.cms'},
    'd33446c7-a37b-4c5b-ba7a-275cc9583c05': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
    'e43b544e-577b-4ed0-adb0-4661bda4c487': 'https://www.asianage.com/rss_feed/',
    'e5a8f17c-58c6-4087-a5c0-2ab681446611': 'http://rss.cnn.com/rss/edition.rss',
    'eeff09cb-6fdb-45f1-a206-32a55320d598': 'https://www.deccanchronicle.com/rss_feed/',
    '9bb25aa5-2536-4c0e-b897-c957b8de61d0': {'Amritsar': 'https://www.tribuneindia.com/rss/feed?catId=17', 'Bathinda': 'https://www.tribuneindia.com/rss/feed?catId=18', 'Chandigarh': 'https://www.tribuneindia.com/rss/feed?catId=20', 'Delhi': 'https://www.tribuneindia.com/rss/feed?catId=24', 'Jalandhar': 'https://www.tribuneindia.com/rss/feed?catId=34', 'Ludhiana': 'https://www.tribuneindia.com/rss/feed?catId=40', 'Patiala': 'https://www.tribuneindia.com/rss/feed?catId=213'}}

    for news_id in source_news_ids:
        news_id = news_id.strip()
        if news_id in dictionary.keys():
            val = dictionary[news_id]
            cities = {}
            if type(val)==dict:
                for key, values in val.items():
                    cities = {}
                    cities[key] = values
                    rss.append(cities)
            else:
                cities['National'] = val
                rss.append(cities)
        else:
            print('news_id not found')

    return rss
    

def rss2news(rss):

    news_link = []

    for rss_link in rss:
        for k, v in rss_link.items():
            NewsFeed = feedparser.parse(v)
            for news in NewsFeed.entries:
                link_dict = {}
                link_dict[k] = news['link']
                if 'published' in news.keys():
                    week = datetime.now() - timedelta(days=1)
                    week = week.strftime("%Y-%m-%d %H:%M:%S")
                    date = parse(news['published'].split('+')[0])
                    date = date.strftime("%Y-%m-%d %H:%M:%S")
                    if date > week:
                        link_dict[k] = news['link']
                        link_dict['published'] = news['published']
                        news_link.append(link_dict)
                    else:
                        print('date is not greater than week')
                else:
                    print('published not found in news[link]')

    return news_link


def _incre_mode(batch_id):
        
    dbs = current_ids()
    
    source_news_ids = dbs["news_source_ids"].split(',')

    rss = ids2rss(source_news_ids)
    
    # dictionary = {'2cdd8f28-01f5-4d18-b438-742f04fe3140': 'https://prod-qt-images.s3.amazonaws.com/production/bloombergquint/feed.xml',
    #     '3d4a70cb-fe3f-459e-8cb1-43bc04f759c6': {'Bengaluru': 'https://www.hindustantimes.com/feeds/rss/cities/bengaluru-news/rssfeed.xml', 'Bhopal': 'https://www.hindustantimes.com/feeds/rss/cities/bhopal-news/rssfeed.xml', 'Chandigarh': 'https://www.hindustantimes.com/feeds/rss/cities/chandigarh-news/rssfeed.xml', 'Dehradun': 'https://www.hindustantimes.com/feeds/rss/cities/dehradun-news/rssfeed.xml', 'Delhi': 'https://www.hindustantimes.com/feeds/rss/cities/delhi-news/rssfeed.xml', 'Gurugram': 'https://www.hindustantimes.com/feeds/rss/cities/gurugram-news/rssfeed.xml', 'Indore': 'https://www.hindustantimes.com/feeds/rss/cities/indore-news/rssfeed.xml', 'Jaipur': 'https://www.hindustantimes.com/feeds/rss/cities/jaipur-news/rssfeed.xml', 'Kolkata': 'https://www.hindustantimes.com/feeds/rss/cities/kolkata-news/rssfeed.xml', 'Lucknow': 'https://www.hindustantimes.com/feeds/rss/cities/lucknow-news/rssfeed.xml', 'Mumbai': 'https://www.hindustantimes.com/feeds/rss/cities/mumbai-news/rssfeed.xml', 'Noida' : 'https://www.hindustantimes.com/feeds/rss/cities/noida-news/rssfeed.xml', 'Patna': 'https://www.hindustantimes.com/feeds/rss/cities/patna-news/rssfeed.xml', 'Pune': 'https://www.hindustantimes.com/feeds/rss/cities/pune-news/rssfeed.xml', 'Ranchi': 'https://www.hindustantimes.com/feeds/rss/cities/ranchi-news/rssfeed.xml'},
    #     '4dfab6d8-8246-469b-9e19-7ddbb55d806d': {'Mumbai': 'https://www.dnaindia.com/feeds/mumbai.xml', 'Delhi': 'https://www.dnaindia.com/feeds/delhi.xml', 'Bangalore': 'https://www.dnaindia.com/feeds/bangalore.xml', 'Pune' : 'https://www.dnaindia.com/feeds/pune.xml', 'Ahmedabad' : 'https://www.dnaindia.com/feeds/ahmedabad.xml'},
    #     '52d0de86-1525-417d-b8fd-2158f1256c38': 'http://www.allindianewspapers.com/Feeds/states.xml',
    #     '5b32994e-2e6e-417f-ba44-77f508742349': 'https://www.business-standard.com/rss/home_page_top_stories.rss',
    #     '65cb3dec-94a9-4274-b518-543c74e14a59': 'https://asia.nikkei.com/rss/feed/nar',
    #     '6c676cc1-2338-4834-a0fb-9ae8a04a2bda': 'https://www.ft.com/?format=rss',
    #     '7eba470b-1edc-4f69-840d-99cfde3a5fcb': 'http://www.abc.net.au/news/feed/2942460/rss.xml',
    #     '890d11b8-05e7-416e-b777-7ba62f4a7045': 'https://www.economist.com/international/rss.xml',
    #     '8cbc9eec-7255-43bf-bb72-2bce4f4764ea': 'https://feeds.feedburner.com/ndtvnews-cities-news?format=xml',
    #     '91272662-bb73-4649-a8c2-026d112c190e': 'https://www.livemint.com/rss/news',
    #     'a70e9599-4480-46d2-889f-652fdd58cc55': {'Delhi': 'https://indianexpress.com/section/cities/delhi/feed/', 'Lucknow' : 'https://www.indianexpress.com/section/cities/lucknow/feed/', 'Pune' : 'https://www.indianexpress.com/section/cities/pune/feed/', 'Chandigarh' : 'https://indianexpress.com/section/cities/chandigarh/feed/', 'Mumbai': 'https://indianexpress.com/section/cities/mumbai/feed/', 'Kolkata' : 'https://indianexpress.com/section/cities/kolkata/feed/', 'Ludhiana' : 'https://indianexpress.com/section/cities/ludhiana/feed/', 'Gujarat': 'https://indianexpress.com/section/india/education/feed/', 'Maharashtra' : 'https://indianexpress.com/section/india/maharashtra/feed/', 'Uttar Pradesh': 'https://indianexpress.com/section/india/uttar-pradesh/feed/', 'West Bengal': 'https://indianexpress.com/section/india/west-bengal/feed/', 'Punjab and Haryana': 'https://indianexpress.com/section/india/punjab-and-haryana/feed/'},
    #     'a9ecac2e-a7da-4bbd-b326-103de3149ece': 'http://feeds.bbci.co.uk/news/world/rss.xml',
    #     'ad60ab7b-906b-467d-b29e-92f200eb88fe': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
    #     'bef37780-c007-4b96-89f4-5198b69f2c93': 'https://www.theguardian.com/world/rss',
    #     'c1f4a45b-aa9c-4627-980b-f69509e5c862': {'Andhra Pradesh': 'https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss', 'Karnataka': 'https://www.thehindu.com/news/national/karnataka/feeder/default.rss', 'Kerala': 'https://www.thehindu.com/news/national/kerala/feeder/default.rss', 'Tamil Nadu': 'https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss', 'Telangana': 'https://www.thehindu.com/news/national/telangana/feeder/default.rss', 'Bengaluru': 'https://www.thehindu.com/news/cities/bangalore/feeder/default.rss', 'Chennai' : 'https://www.thehindu.com/news/cities/chennai/feeder/default.rss', 'Coimbatore': 'https://www.thehindu.com/news/cities/Coimbatore/feeder/default.rss', 'Delhi': 'https://www.thehindu.com/news/cities/Delhi/feeder/default.rss', 'Hyderabad': 'https://www.thehindu.com/news/cities/Hyderabad/feeder/default.rss', 'Kochi': 'https://www.thehindu.com/news/cities/Kochi/feeder/default.rss', 'Kolkata': 'https://www.thehindu.com/news/cities/kolkata/feeder/default.rss', 'Mumbai': 'https://www.thehindu.com/news/cities/mumbai/feeder/default.rss', 'Kozhikode': 'https://www.thehindu.com/news/cities/kozhikode/feeder/default.rss', 'Madurai': 'https://www.thehindu.com/news/cities/Madurai/feeder/default.rss', 'Mangaluru': 'https://www.thehindu.com/news/cities/Mangalore/feeder/default.rss', 'Puducherry': 'https://www.thehindu.com/news/cities/puducherry/feeder/default.rss', 'Thiruvananthapuram': 'https://www.thehindu.com/news/cities/Thiruvananthapuram/feeder/default.rss', 'Tiruchirapalli': 'https://www.thehindu.com/news/cities/Tiruchirapalli/feeder/default.rss', 'Vijayawada': 'https://www.thehindu.com/news/cities/Vijayawada/feeder/default.rss', 'Visakhapatnam': 'https://www.thehindu.com/news/cities/Visakhapatnam/feeder/default.rss'},
    #     'ca3c6507-8c4a-4269-a384-8de06f43bc4f': 'https://timesofindia.indiatimes.com/rssfeeds/-2128932452.cms',
    #     'd33446c7-a37b-4c5b-ba7a-275cc9583c05': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
    #     'e43b544e-577b-4ed0-adb0-4661bda4c487': 'https://www.asianage.com/rss_feed/',
    #     'e5a8f17c-58c6-4087-a5c0-2ab681446611': 'http://rss.cnn.com/rss/edition.rss',
    #     'eeff09cb-6fdb-45f1-a206-32a55320d598': 'https://www.deccanchronicle.com/rss_feed/'}
    
    # for news_id in source_news_ids:
    #   news_id = news_id.strip()
    #   if news_id in dictionary.keys():
    #     rss_list.append(dictionary[news_id])
    #   else:
    #     print('news_id not found')
    
    print('rss is:', rss)

    news_link = rss2news(rss)
    print('total news articles are:', len(news_link))
    print(news_link)


    # rss_list = ['https://www.thehindu.com/news/national/feeder/default.rss', 
    #     'https://indianexpress.com/section/india/feed/',
    #     'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml',
    #     'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
    #     'http://www.allindianewspapers.com/Feeds/nation.xml',
    #     'https://www.dnaindia.com/feeds/india.xml',
    #     'https://www.deccanchronicle.com/rss_feed/',
    #     'https://www.asianage.com/rss_feed/',
    #     'https://timesofindia.indiatimes.com/rssfeeds/1221656.cms',
    #     'https://www.business-standard.com/rss/home_page_top_stories.rss',
    #     'http://feeds.feedburner.com/ndtvnews-top-stories?format=xml',
    #     'https://www.livemint.com/rss/news',
    #     'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
    #     'https://asia.nikkei.com/rss/feed/nar',
    #     'https://www.ft.com/?format=rss',
    #     'https://www.economist.com/international/rss.xml',
    #     'http://www.abc.net.au/news/feed/2942460/rss.xml',
    #     'http://feeds.bbci.co.uk/news/world/rss.xml',
    #     'https://www.theguardian.com/world/rss',
    #     'https://prod-qt-images.s3.amazonaws.com/production/bloombergquint/feed.xml',
    #     'http://rss.cnn.com/rss/edition.rss']

    # cities = {}
    # news_link = []
    
    # for rss in rss_list:
        # if type(rss)==dict:
            # for key, values in rss.items():
                # cities[key] = value
                # news_link.append(cities)
        # else:
            # cities['Nation'] = rss
            # news_link.append(cities)

    # cities_list = []

    # for new_link in news_link:
        # for k,v in new_link.items():
            # article_dict = {}
            # article_link = []
            # NewsFeed = feedparser.parse(v)
            # for news in NewsFeed.entries:
                # article_link.append(news['link'])
            # article_dict[k] = article_link
        # cities_list.append(article_dict)



# NewsFeed = feedparser.parse(rss)
      # for news in NewsFeed.entries:
        # news_link.append(news['link'])
              # print(news['link'], news['published'])
    
    
    csv_file = "incre_mode.csv"
    csv_columns = ['name', 'org', 'loc', 'keyword', 'hdfcpresent', 'date', 'sourcename', 'weblink', 'batch_id', 'created_date', 'cities']
    
    # news_link = ['https://timesofindia.indiatimes.com/city/hyderabad/hyderabad-two-sbi-managers-arrested-in-loan-sanction-fraud-case/articleshow/71745994.cms']
    
    nlp_Name = spacy.load("en_core_web_trf") # spacy.load(OUTPUT1)
    
    utc=pytz.UTC
    
    keywords = dbs['keywords'].split(',')
    print('keywords are:', keywords)
    
    # keywords = [
    #                 'black money'
    #                 'money laundering', 
    #                 'money launder', 
    #                 'lauder the money', 
    #                 'money-mule', 
    #                 'money mule', 
    #                 'Hawala', 
    #                 'drug-trafficking', 
    #                 'drug trafficking', 
    #                 'terror', 
    #                 'terror financing',
    #                 'fraud'
    #                 ]


    with open(csv_file, 'w') as csvfile:
      _writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
      _writer.writeheader()
      for link in news_link:
        val = list(link.values())
        # print('link values are:', val)
        keys = list(link.keys())
        # print('keys values are:', keys)
        try:
          profile = {'name': '', 'org': '', 'loc': '', 'keyword': '', 'hdfcpresent': 'No', 'date': '', 'sourcename': '', 'weblink': '', 'batch_id': '', 'created_date': '', 'cities': ''}
          article = Article(val[0])
          article.download()
          article.parse()
          text = article.title.lower() + os.linesep + article.text.lower()
          # if article.publish_date:
            # print(article.publish_date)
            # if parse(article.publish_date) > date:
              # print('Date is greater:', article.publish_date)
    
          for keyword in keywords:
            if keyword.lower() in text.lower():
              if keyword not in profile['keyword']:
                profile['keyword'] += keyword + ', '
              else:
                continue
    
          if 'hdfc' in text.lower():
            profile['hdfcpresent'] = 'YES'

          profile['weblink'] = article.url
    
          profile['sourcename'] = val[0].split('/')[2]
    
          if profile['keyword']:
            doc = nlp_Name(article.title + os.linesep + article.text)
    
            # iterate through each entity present
            for count,ent in enumerate(doc.ents):
              # save data in profile
              # find persons in text
              if ent.label_ == 'PERSON':
                profile['name'] += ent.text + ', '
                # remove name if present in false positives
                # if (ent.text not in profile['name']):
                  # print(str(string))
                  # profile['name'] += ent.text + ', '
                # else:
                  # print(ent.text)
                  # pass
    
                # find persons in text
              elif ent.label_ == 'ORG':
                profile['org'] += ent.text + ', '
                
                # remove name if present in false positives
                # if (ent.text not in profile['org']):
                  # profile['org'] += ent.text + ', '
                # else:
                  # print(ent.text)
                  # pass
    
              # find persons in text
              elif ent.label_ == 'GPE':
                profile['loc'] += ent.text + ', '
                # remove name if present in false positives
                # if (ent.text not in profile['loc']):
                  # profile['loc'] += ent.text + ', '
                # else:
                  # print(ent.text)
                  # pass
    
              else:
                pass
    
    
            profile['date'] = link['published'] # article.publish_date
            profile['cities'] = keys[0]
            profile['batch_id'] = batch_id
            profile['created_date'] = datetime.now()
            profile['org'] = profile['org'].split(',')
            print(profile['org'])
            profile['org'] = [x.strip() for x in profile['org'] if x.strip()]
            profile['org'] = list(set(profile['org']))
            # profile['org'] = ', '.join(profile['org'])    
            profile['name'] = profile['name'].split(',') + profile['org']
            print(profile['name'])
            profile['name'] = [x.strip() for x in profile['name'] if x.strip()]
            profile['name'] = list(set(profile['name']))
            # check if any name is a subset of any other name
            profile['name'] = [ i for i in profile['name'] if not any( [ i in a for a in profile['name'] if a != i]   )]
            # profile['name'] = [ i.lower() for i in profile['name']]
            # profile['name'] = list(set(profile['name']))
            # profile['name'] = [ i.title() for i in profile['name']]
            # profile['name'] = subset(profile['name'])
            profile['name'] = lowercase_check(profile['name'])
            profile['name'] = ', '.join(profile['name'])    
            profile['org'] = ', '.join(profile['org'])    
            profile['loc'] = profile['loc'].split(',')
            print(profile['loc'])
            profile['loc'] = [x.strip() for x in profile['loc'] if x.strip()]
            profile['loc'] = list(set(profile['loc']))
            # check if any name is a subset of any other name
            profile['loc'] = [ i for i in profile['loc'] if not any( [ i in a for a in profile['loc'] if a != i]   )]
            # profile['loc'] = [ i.lower() for i in profile['loc']]
            # profile['loc'] = list(set(profile['loc']))
            # profile['loc'] = [ i.title() for i in profile['loc']]
            # profile['loc'] = subset(profile['loc'])
            profile['loc'] = lowercase_check(profile['loc'])
            profile['loc'] = ', '.join(profile['loc'])

            print(profile) 
             
            _writer.writerow(profile)
    
          else:
            print(profile)
    
        except Exception as e:
          print(e)

    print("Starting Saving Database into mongodb")
    
    f1 = Faker()
    df = pd.read_csv(os.path.abspath(os.path.join(os.getcwd(),'incre_mode.csv')), dtype='unicode')
    
    df.columns = ['Person Name mentioned in the news', 
        'Organization Name mentioned in the news',
        'City/ State mentioned under the news', 
        'Key word Used for identify the article',
        'HDFC Bank Name under News / Article', 
        'Article Date', 
        'Source Name', 
        'Web link of news',
        'batch_id',
        'created_date',
        'City of News Paper'
        ]
    
    df = df.drop_duplicates(subset='Web link of news', keep="last")
    df.reset_index(drop=True, inplace=True)
    
    df['Source of Info'] = 'News Paper'
    x = [f1.uuid4() for i in range(len(df))]
    df['uuid'] = x
    
    # strip ending comma, spaces
    df['Person Name mentioned in the news'] = df['Person Name mentioned in the news'].apply(lambda x: fnc_(x))
    df['Organization Name mentioned in the news'] = df['Organization Name mentioned in the news'].apply(lambda x: fnc_(x))
    df['City/ State mentioned under the news'] = df['City/ State mentioned under the news'].apply(lambda x: fnc_(x))
    df['Key word Used for identify the article'] = df['Key word Used for identify the article'].apply(lambda x: fnc_(x))
    df['HDFC Bank Name under News / Article'] = df['HDFC Bank Name under News / Article'].apply(lambda x: fnc_(x))
    df['Article Date'] = df['Article Date'].apply(lambda x: fnc_(x))
    # df['City of News Paper'] = '' # document.pop('City of News Paper')
    
    # df['Source Name'] = ''

    # names_list = df['Person Name mentioned in the news'].tolist()
    # idxes = df.index.tolist()

    # _idx = subset_dupl(names_list, idxes)

    # df = df[df.index.isin(_idx)]


    # replace empty string na values
    df.replace(to_replace=np.nan, value='', inplace=True)
    # df.replace(to_replace=None, value='', inplace=True)

    
    dicts = df.to_dict(orient='records')
    client = MongoClient('localhost', 27017)
    dbnames = client.list_database_names()
    db = client['adverse_db']
    collection_batches = db['adverse_db']
    if 'adverse_db' in dbnames:
      cursor = collection_batches.find({}, {'_id': False})
      dbs = [database['Web link of news'] for database in cursor]

      for _dict in dicts:
        # if _dict['Web link of news'] in dbs:
          # print('Web link of news exist in db')
          # continue
        # check for duplicate names
        if check_duplicate_name(_dict['Person Name mentioned in the news']):
          print('Names intersection crosses threshold')
        else:
          collection_batches.insert_one(_dict)
    else:
      for _dict in dicts:
        print("database doesn't exist creating it")
        collection_batches.insert_one(_dict)

    print("Post processing completed")
    return "Incremental Mode Complete"

if __name__ == "__main__":
    pass
    # _incre_mode(batch_id)
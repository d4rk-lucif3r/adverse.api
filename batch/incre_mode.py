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

def _incre_mode(batch_id):
    
    rss_list = []
    news_link = []
    
    dbs = current_ids()
    
    source_news_ids = dbs["news_source_id"].split(',')
    
    dictionary = {'2cdd8f28-01f5-4d18-b438-742f04fe3140': 'https://prod-qt-images.s3.amazonaws.com/production/bloombergquint/feed.xml',
        '3d4a70cb-fe3f-459e-8cb1-43bc04f759c6': 'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml',
        '4dfab6d8-8246-469b-9e19-7ddbb55d806d': 'https://www.dnaindia.com/feeds/india.xml',
        '52d0de86-1525-417d-b8fd-2158f1256c38': 'http://www.allindianewspapers.com/Feeds/nation.xml',
        '5b32994e-2e6e-417f-ba44-77f508742349': 'https://www.business-standard.com/rss/home_page_top_stories.rss',
        '65cb3dec-94a9-4274-b518-543c74e14a59': 'https://asia.nikkei.com/rss/feed/nar',
        '6c676cc1-2338-4834-a0fb-9ae8a04a2bda': 'https://www.ft.com/?format=rss',
        '7eba470b-1edc-4f69-840d-99cfde3a5fcb': 'http://www.abc.net.au/news/feed/2942460/rss.xml',
        '890d11b8-05e7-416e-b777-7ba62f4a7045': 'https://www.economist.com/international/rss.xml',
        '8cbc9eec-7255-43bf-bb72-2bce4f4764ea': 'https://feeds.feedburner.com/ndtvnews-cities-news?format=xml',
        '91272662-bb73-4649-a8c2-026d112c190e': 'https://www.livemint.com/rss/news',
        'a70e9599-4480-46d2-889f-652fdd58cc55': 'https://indianexpress.com/section/india/feed/',
        'a9ecac2e-a7da-4bbd-b326-103de3149ece': 'http://feeds.bbci.co.uk/news/world/rss.xml',
        'ad60ab7b-906b-467d-b29e-92f200eb88fe': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
        'bef37780-c007-4b96-89f4-5198b69f2c93': 'https://www.theguardian.com/world/rss',
        'c1f4a45b-aa9c-4627-980b-f69509e5c862': 'https://www.thehindu.com/news/national/feeder/default.rss',
        'ca3c6507-8c4a-4269-a384-8de06f43bc4f': 'https://timesofindia.indiatimes.com/rssfeeds/1221656.cms',
        'd33446c7-a37b-4c5b-ba7a-275cc9583c05': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
        'e43b544e-577b-4ed0-adb0-4661bda4c487': 'https://www.asianage.com/rss_feed/',
        'e5a8f17c-58c6-4087-a5c0-2ab681446611': 'http://rss.cnn.com/rss/edition.rss',
        'eeff09cb-6fdb-45f1-a206-32a55320d598': 'https://www.deccanchronicle.com/rss_feed/'}
    
    for news_id in source_news_ids:
      news_id = news_id.strip()
      if news_id in dictionary.keys():
        rss_list.append(dictionary[news_id])
      else:
        print('news_id not found')
    
    print('rss is:', rss_list)


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
    
    for rss in rss_list:
      NewsFeed = feedparser.parse(rss)
      for news in NewsFeed.entries:
        news_link.append(news['link'])
              # print(news['link'], news['published'])
    
    
    csv_file = "incre_mode.csv"
    csv_columns = ['name', 'org', 'loc', 'keyword', 'hdfcpresent', 'date', 'sourcename', 'weblink', 'batch_id']
    
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
        try:
          profile = {'name': '', 'org': '', 'loc': '', 'keyword': '', 'hdfcpresent': 'No', 'date': '', 'sourcename': '', 'weblink': ''}
          article = Article(link)
          article.download()
          article.parse()
          text = article.text.lower()
          # if article.publish_date:
            # print(article.publish_date)
            # if parse(article.publish_date) > date:
              # print('Date is greater:', article.publish_date)
    
          for keyword in keywords:
            if keyword in text.lower():
              if keyword not in profile['keyword']:
                profile['keyword'] += keyword + ', '
              else:
                continue
    
          if 'hdfc' in text.lower():
            profile['hdfcpresent'] = 'YES'
    
          profile['sourcename'] = link.split('/')[2]
    
          if profile['keyword']:
            doc = nlp_Name(article.text)
    
            # iterate through each entity present
            for count,ent in enumerate(doc.ents):
              # save data in profile
              # find persons in text
              if ent.label_ == 'PERSON':
                # remove name if present in false positives
                if (ent.text not in profile['name']):
                  # print(str(string))
                  profile['name'] += ent.text + ', '
                else:
                  print(ent.text)
                  pass
    
                # find persons in text
              elif ent.label_ == 'ORG':
                
                # remove name if present in false positives
                if (ent.text not in profile['org']):
                  profile['org'] += ent.text + ', '
                else:
                  # print(ent.text)
                  pass
    
              # find persons in text
              elif ent.label_ == 'GPE':
                # remove name if present in false positives
                if (ent.text not in profile['loc']):
                  profile['loc'] += ent.text + ', '
                else:
                  # print(ent.text)
                  pass
    
              else:
                pass
    
            profile['weblink'] = article.url
    
            profile['date'] = article.publish_date
            profile['batch_id'] = batch_id
    
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
        'batch_id'
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
    df['City of News Paper'] = '' # document.pop('City of News Paper')
    
    # df['Source Name'] = ''
    
    dicts = df.to_dict(orient='records')
    client = MongoClient('localhost', 27017)
    dbnames = client.list_database_names()
    db = client['adverse_db']
    collection_batches = db['adverse_db']
    if 'adverse_db' in dbnames:
      cursor = collection_batches.find({}, {'_id': False})
      dbs = [database['Web link of news'] for database in cursor]

      for _dict in dicts:
        if _dict['Web link of news'] in dbs:
          print('Web link of news exist in db')
          continue
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
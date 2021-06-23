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
from newspaper.utils import BeautifulSoup
from newspaper import Config
import re
from GoogleNews import GoogleNews
import urllib.request
from fake_useragent import UserAgent


def get_newsfeeds(feed_url):

    all_articles = []

    try:
        NewsFeed = feedparser.parse(feed_url)

        for news in NewsFeed.entries:
            if 'published' in news.keys():
                week = datetime.now() - timedelta(days=7)
                week = week.strftime("%Y-%m-%d %H:%M:%S")
                date = parse(news['published'].split('+')[0])
                date = date.strftime("%Y-%m-%d %H:%M:%S")

                if date >= week:
                    result_ = {}
                    result_['published'] = news['published']
                    result_['link'] = news['link']
                    all_articles.append(result_)
                
                else:
                    print('date is not greater than week')
                    print('skipping:', news['link'])
                    continue

            else:
                print('published not found in news.keys')
                result_ = {}
                result_['published'] = datetime.now()
                result_['link'] = news['link']
                all_articles.append(result_)

                # print('skipping:', news['link'])
                # continue

    except Exception as e:
        print("feedparser error:", e)

    return all_articles

def get_google_rss_feed():

    google_rss_feed = []

    dbs = current_ids()
    keywords = dbs['keywords'].split(',')
    keywords = [x.strip() for x in keywords if x.strip()]

    for keyword in keywords:
        keyword = keyword.replace(" ", "%20")
        _url = 'https://news.google.com/rss/search?q=%s+when:7d&hl=en-IN&gl=IN&ceid=IN:en' % keyword
        google_rss_feed.append(_url)

    google_rss_feed.append('https://news.google.com/news/rss')
    google_rss_feed.append('https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRFUxZG5JU0FtVnVLQUFQAQ?hl=en-IN&gl=IN&ceid=IN:en')
    google_rss_feed.append('https://news.google.com/rss/topics/CAAqJAgKIh5DQkFTRUFvS0wyMHZNRFV4ZW5aNU9SSUNaVzRvQUFQAQ?hl=en-IN&gl=IN&ceid=IN:en')
    google_rss_feed.append('https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR1JxWjNRU0FtVnVLQUFQAQ?hl=en-IN&gl=IN&ceid=IN:en')

    return google_rss_feed

def get_google_articles():

    google_articles = []

    google_rss_feed = get_google_rss_feed()

    # print(google_rss_feed)

    for rss in google_rss_feed:
        all_articles = get_newsfeeds(rss)
        # print('length of article:', len(all_articles))
        google_articles += all_articles

    # print('total articles:', len(google_articles))

    return google_articles

def restricted_sources():

    articles_list = []

    restricted_source_dict = {
    'www.nytimes.com' : 'International',
    'www.reuters.com' : 'International',
    'www.hindustantimes.com' : 'National',
    'www.deccanherald.com' : 'National',
    'www.dnaindia.com' : 'National',
    'www.allindianewspapers.com' : 'National',
    'www.business-standard.com' : 'National',
    'asia.nikkei.com' : 'International',
    'www.abc.net.au' : 'International',
    'www.economist.com' : 'International',
    'www.ndtv.com' : 'National',
    'www.livemint.com' : 'National',
    'indianexpress.com' : 'National',
    'www.bbc.co.uk' : 'International',
    'www.bbc.com' : 'International',
    'economictimes.indiatimes.com' : 'National',
    'www.theguardian.com' : 'International',
    'www.thehindu.com' : 'National',
    'timesofindia.indiatimes.com' : 'National',
    'mumbaimirror.indiatimes.com' : 'National',
    'www.wsj.com' : 'International',
    'www.asianage.com' : 'National',
    'www.cnn.com' : 'International',
    'edition.cnn.com' : 'International',
    'cnn.it' : 'International',
    'www.deccanchronicle.com' : 'National',
    'www.tribuneindia.com' : 'National' }

    restricted_source = [ 
    'www.deccanherald.com',
    'www.reuters.com',
    'www.nytimes.com',
    'www.hindustantimes.com',
    'www.dnaindia.com',
    'www.allindianewspapers.com',
    'www.business-standard.com',
    'asia.nikkei.com',
    'www.abc.net.au',
    'www.economist.com',
    'www.ndtv.com',
    'www.livemint.com',
    'indianexpress.com',
    'www.bbc.co.uk',
    'www.bbc.com',
    'economictimes.indiatimes.com',
    'www.theguardian.com',
    'www.thehindu.com',
    'timesofindia.indiatimes.com',
    'mumbaimirror.indiatimes.com',
    'www.wsj.com',
    'www.asianage.com',
    'www.cnn.com',
    'edition.cnn.com',
    'cnn.it',
    'www.deccanchronicle.com',
    'www.tribuneindia.com' 
    ]

    all_articles = get_google_articles()
    all_articles2 = google_news_articles()
    all_articles += all_articles2
    print('restricted_sources total articles:', len(all_articles))
    
    for article_link in all_articles:
        try:
            req = urllib.request.Request(article_link['link'], headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'})
            res = urllib.request.urlopen(req, timeout=20)
            finalurl = res.geturl()
            # print('article link split: ', finalurl.split('/')[2])
            if finalurl.split('/')[2] in restricted_source:
                # print('article link in restricted sources')
                cities = {}
                cities[restricted_source_dict[finalurl.split('/')[2]]] = finalurl
                cities['published'] = article_link['published'] # .strftime("%Y-%m-%d %H:%M:%S")
                articles_list.append(cities)
            else:
                print(finalurl.split('/')[2], 'not in restricted_sources')
                print('skipping:', finalurl)

        except Exception as e:
            print('restricted_sources exception:', e)
            print('skipping url:', article_link['link'])
            continue


    # for link in all_articles:
    #     if link.split('/')[2] in restricted_source:
    #         cities = {}
    #         cities[restricted_source_dict[link.split('/')[2]]] = link
    #         # cities[link] = restricted_source_dict[link.split('/')[2]]
    #         articles_list.append(cities)

    return articles_list


def google_rss_feed():

    all_articles = []

    dbs = current_ids()

    keywords = dbs['keywords'].split(',')
    keywords = [x.strip() for x in keywords if x.strip()]

    for keyword in keywords:
        keyword = keyword.replace(" ", "%20")
        _url = 'https://news.google.com/rss/search?q=%s+when:7d' % keyword

        try:
            NewsFeed = feedparser.parse(feed_url)

            for news in NewsFeed.entries:
                if 'published' in news.keys():
                    week = datetime.now() - timedelta(days=7)
                    week = week.strftime("%Y-%m-%d %H:%M:%S")
                    date = parse(news['published'].split('+')[0])
                    date = date.strftime("%Y-%m-%d %H:%M:%S")

                    if date >= week:
                        result_ = {}
                        result_['published'] = news['published']
                        result_['link'] = news['link']
                        all_articles.append(result_)
                    
                    else:
                        print('date is not greater than week')
                        print('skipping:', news['link'])
                        continue

                else:
                    print('published not found in news.keys')
                    result_ = {}
                    result_['published'] = datetime.now()
                    result_['link'] = news['link']
                    all_articles.append(result_)
                    # print('skipping:', news['link'])
                    # continue

        except Exception as e:
            print("feedparser error:", e)

    return all_articles

def google_news_articles():

    all_articles = []

    today_date = datetime.now()
    date1 = today_date.strftime('%m/%d/%Y')

    day_ago_date = today_date - timedelta(days=7)
    date2 = day_ago_date.strftime('%m/%d/%Y')

    dbs = current_ids()

    keywords = dbs['keywords'].split(',')
    keywords = [x.strip() for x in keywords if x.strip()]

    googlenews = GoogleNews()
    googlenews = GoogleNews(lang='en')
    googlenews = GoogleNews(start=date2, end=date1)
    
    for keyword in keywords:
      googlenews.search(keyword)
      result = googlenews.results()
      
      for _result in result:
        result_ = {}
        result_['published'] = _result['datetime'] # .strftime("%Y-%m-%d %H:%M:%S")
        # result_['link'] = 'https://' + _result['link']
        result_['link'] = _result['link']
        all_articles.append(result_)
      
      googlenews.clear()
    # for keyword in keywords:
    #     googlenews.search(keyword)
    #     googlenews.get_page(2)
    #     # for i in range(1, 100):
    #     # for i in range(1, 25):
    #         # result = googlenews.page_at(i)
    #         # if result:
    #             # result = [_result['link'] for _result in result]
    #             # all_articles += result
    #         # else:
    #             # continue

    #     all_links = googlenews.get_links()
    #     all_articles += all_links
    #     # print(all_links)
    #     googlenews.clear()

    return all_articles

def current_ids_names():
    '''
    function to update sources ids and keywords into database
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['names']
    # cursor = collection_batches.find({}, {'_id': False})
    cursor = collection_batches.find({})
    dbs = [database for database in cursor]
    return dbs[-1]

def current_ids_cities():
    '''
    function to update sources ids and keywords into database
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['cities']
    # cursor = collection_batches.find({}, {'_id': False})
    cursor = collection_batches.find({})
    dbs = [database for database in cursor]
    return dbs[-1]

def update_current_cities(cities=''):
    '''
    function to update sources ids and keywords into database
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['cities']
    post = collection_batches.find_one({'_id': bson.objectid.ObjectId("608bb5960895f552b1f5c9d0")})
    if post:
        if cities:
            temp_name = post['cities'].split(',')
            cities = cities.split(',')
            cities = [x.strip() for x in cities if x.strip()]
            temp_name = [x.strip() for x in temp_name if x.strip()]
            temp_name += cities
            temp_name = list(set(temp_name))
            temp_name = ', '.join(temp_name)
            post['cities'] = temp_name
            post['last_updated_time'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        collection_batches.save(post)

    return "Updated Document"

def get_batch_ids():
    '''
    function to get batch ids and date into database
    '''
    client = MongoClient('localhost', 27017)
    db = client['BatchRunStatus']
    collection_batches = db['DetailStatus']
    cursor = collection_batches.find({})
    dbs = [database for database in cursor]
    return dbs

def soup_text(soup, sourcename):

    text_ = []

    dictionary = {
    # 'www.hindustantimes.com': {'h1': ['hdg1', 'hdg3'], 'div': ['sortDec', 'detail', 'storyDetails']},
    # 'www.dnaindia.com': {'div': ['container']},
    # 'www.business-standard.com': {'h1': ['headline'], 'h2': ['alternativeHeadline'], 'span': ['p-content']},
    'www.nytimes.com': {'Headlines': {'h1': ['css-19rw7kf e1h9rw200']}, 'Synopsis': {'p': ['css-w6ymp8 e1wiw3jv0']}, 'Text': {'div': ['css-53u6y8']}},
    'www.business-standard.com': {'Headlines': {'h1': ['headline']}, 'Synopsis': {'h2': ['alternativeHeadline']}, 'Text': {'span': ['p-content']}},
    'www.ndtv.com': {'Headlines': {'h1': ['sp-ttl']}, 'Synopsis': {'h2': ['sp-descp']}, 'Text': {'div': ['sp-cn ins_storybody', '.*sp-cn.*']}},
    # 'indianexpress.com': {'h1': ['native_story_title'], 'h2' : ['synopsis'], 'div' : ['full-details', 'pcl-full-content']},
    'www.bbc.com': {'Headlines': {'h1': ['ssrcss-1pl2zfy-StyledHeading e1fj1fc10', 'ssrcss-1pl2zfy-StyledHeading']}, 'Synopsis': {'b': ['ssrcss-14iz86j-BoldText e5tfeyi0', 'ssrcss-hmf8ql-BoldText e5tfeyi3']}, 'Text': {'div': ['ssrcss-uf6wea-RichTextComponentWrapper e1xue1i83', 'ssrcss-18snukc-RichTextContainer e5tfeyi1', 'ssrcss-5h7eao-ArticleWrapper', 'ssrcss-5h7eao-ArticleWrapper e1nh2i2l6', 'ssrcss-14iz86j-BoldText']}},
    'www.bbc.co.uk': {'Headlines': {'h1': ['ssrcss-1pl2zfy-StyledHeading e1fj1fc10', 'ssrcss-1pl2zfy-StyledHeading']}, 'Synopsis': {'b': ['ssrcss-14iz86j-BoldText e5tfeyi0', 'ssrcss-hmf8ql-BoldText e5tfeyi3']}, 'Text': {'div': ['ssrcss-uf6wea-RichTextComponentWrapper e1xue1i83', 'ssrcss-18snukc-RichTextContainer e5tfeyi1', 'ssrcss-5h7eao-ArticleWrapper', 'ssrcss-5h7eao-ArticleWrapper e1nh2i2l6', 'ssrcss-14iz86j-BoldText']}},
    'economictimes.indiatimes.com': {'Headlines': {'h1': ['artTitle font_faus']}, 'Synopsis': {'h2': ['summary', 'artSyn tac font_mon']}, 'Text': {'div': ['.*artText.*', 'pageContent flt', '.*content1.*', 'primeContent col s_col font_faus artText paywall']}},
    # 'www.thehindu.com': {'div': ['title', 'paywall']},
    'timesofindia.indiatimes.com': {'Headlines': {'h1': ['_23498', '.*_1Y-96.*']}, 'Text': {'div': ['ga-headlines', '.*Normal.*', '.*_3YYSt.*']}},
    'bangaloremirror.indiatimes.com': {'Headlines': {'div': ['heading2']}, 'Text': {'div': ['.*Normal.*', 'ga-headlines']}},
    'edition.cnn.com': {'Headlines': {'h1': ['pg-headline']}, 'Text':  {'div': ['pg-headline', 'l-container', 'zn-body__paragraph']}},
    'www.deccanchronicle.com': {'Headlines': {'h1': ['headline']}, 'Synopsis': {'div': ['strap']}, 'Text': {'div': ['story-body']}},
    'www.deccanherald.com': {'Headlines': {'h1': ['f-left sanspro-b']}, 'Synopsis': {'h3': ['sanspro-reg strap-heading']}, 'Text': {'div': ['field-items']}},
    'www.tribuneindia.com': {'Headlines': {'div': ['glb-heading']}, 'Text': {'div': ['story-desc']}},
    'www.dailypioneer.com': {'Headlines': {'div': ['col-12']}, 'Text': {'div': ['col-22 mt-4', 'col-12 col-md order-md-2 order-1', 'newsDetailedContent', 'row no-gutters bodyContentSection', 'storyDetailBox']}},
    'www.telegraphindia.com': {'Headlines': {'h1': ['fs-45 uk-text-1D noto-bold mb-2', 'sub_head  haedlinesstory1']}, 'Synopsis': {'div': ['fs-20 uk-text-69 noto-regular', 'fontStyle', 'col-12']}, 'Text': {'div': ['fs-17 pt-2 noto-regular'], 'p': ['p_txt_kj']}},
    'epaper.telegraphindia.com': {'Headlines': {'h1': ['fs-45 uk-text-1D noto-bold mb-2', 'sub_head  haedlinesstory1']}, 'Synopsis': {'div': ['fs-20 uk-text-69 noto-regular', 'fontStyle', 'col-12']}, 'Text': {'div': ['fs-17 pt-2 noto-regular', 'website_story_inside', 'col-12'], 'p': ['p_txt_kj']}},
    'www.wsj.com': {'Headlines': {'h1': ['wsj-article-headline']}, 'Synopsis': {'h2': ['sub-head'], 'figcaption': [".*article__inset__video__caption.*"]}, 'Text': {'div': ['column at8-col8 at12-col7 at16-col9 at16-offset1', 'wsj-snippet-body'], 'p': ['p_txt_kj']}},
    # 'epaper.telegraphindia.com': {'div': ['website_story_inside', 'col-12', 'fs-20 uk-text-69 noto-regular', 'fs-17 pt-2 noto-regular', 'fontStyle'], 'h1': ['fs-45 uk-text-1D noto-bold mb-2', 'sub_head  haedlinesstory1'], 'p': ['p_txt_kj']}
    # 'www.dailypioneer.com': {}
    }

    try:
        # print('sourcename:', sourcename)
        tag_class = dictionary[sourcename]
        # print('tag_class:', tag_class)
        # for _key in tag_class.values():
        Headlines = []
        Synopsis = []
        Text = []
        for tag, _class in tag_class.items(): # i = 0, headline, i = 1, synopysis, i =2 text
            for __tag, __class in _class.items():
                for ___class in __class:
                    if (tag == 'Headlines' and not Headlines) or (tag == 'Synopsis' and not Synopsis) or (tag == 'Text' and not Text):
                        regex = re.compile(___class)
                        for block in soup.find_all(__tag, {"class" : regex}):
                            for strings in block.stripped_strings:
                                if tag == 'Headlines':
                                    Headlines.append(strings)
                                elif tag == 'Synopsis':
                                    Synopsis.append(strings)
                                elif tag == 'Text':
                                    Text.append(strings)
                                else:
                                    continue

        text_ = Headlines + Synopsis + Text
                            # text_.append(strings)
            # text = [tag.get_text() for tag in soup.find_all("div", {"class" : regex})]
            # text_ += [tag.get_text() for tag in soup.find_all(tag, {"class" : regex})]
    except Exception as e:
        # print('soup_text exception:', e)
        return None

    if text_:
        # print(text_)
        # return '\n'.join(text_)
        return ' '.join(text_)
    else:
        # print('text not found')
        return None


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
          continue
          # print('threshold is not greater')
          # pass
    else:
      # print("adverse_db doesnot exist creating database")
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

def current_ids_fps():
    '''
    function to update sources ids and keywords into database
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['fp_list']
    # cursor = collection_batches.find({}, {'_id': False})
    cursor = collection_batches.find({})
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

    dictionary = {
    'gghh223d-gifd-67h3-c428-54x77542f712': 'https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best',
    '3cdd8f28-01f5-4d18-b438-742f04fe3141': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    '3d4a70cb-fe3f-459e-8cb1-43bc04f759c6': {'Bengaluru': 'https://www.hindustantimes.com/feeds/rss/cities/bengaluru-news/rssfeed.xml', 'Bhopal': 'https://www.hindustantimes.com/feeds/rss/cities/bhopal-news/rssfeed.xml', 'Chandigarh': 'https://www.hindustantimes.com/feeds/rss/cities/chandigarh-news/rssfeed.xml', 'Dehradun': 'https://www.hindustantimes.com/feeds/rss/cities/dehradun-news/rssfeed.xml', 'Delhi': 'https://www.hindustantimes.com/feeds/rss/cities/delhi-news/rssfeed.xml', 'Gurugram': 'https://www.hindustantimes.com/feeds/rss/cities/gurugram-news/rssfeed.xml', 'Indore': 'https://www.hindustantimes.com/feeds/rss/cities/indore-news/rssfeed.xml', 'Jaipur': 'https://www.hindustantimes.com/feeds/rss/cities/jaipur-news/rssfeed.xml', 'Kolkata': 'https://www.hindustantimes.com/feeds/rss/cities/kolkata-news/rssfeed.xml', 'Lucknow': 'https://www.hindustantimes.com/feeds/rss/cities/lucknow-news/rssfeed.xml', 'Mumbai': 'https://www.hindustantimes.com/feeds/rss/cities/mumbai-news/rssfeed.xml', 'Noida' : 'https://www.hindustantimes.com/feeds/rss/cities/noida-news/rssfeed.xml', 'Patna': 'https://www.hindustantimes.com/feeds/rss/cities/patna-news/rssfeed.xml', 'Pune': 'https://www.hindustantimes.com/feeds/rss/cities/pune-news/rssfeed.xml', 'Ranchi': 'https://www.hindustantimes.com/feeds/rss/cities/ranchi-news/rssfeed.xml'},
    '4dfab6d8-8246-469b-9e19-7ddbb55d806d': {'Mumbai': 'https://www.dnaindia.com/feeds/mumbai.xml', 'Delhi': 'https://www.dnaindia.com/feeds/delhi.xml', 'Bangalore': 'https://www.dnaindia.com/feeds/bangalore.xml', 'Pune' : 'https://www.dnaindia.com/feeds/pune.xml', 'Ahmedabad' : 'https://www.dnaindia.com/feeds/ahmedabad.xml'},
    '52d0de86-1525-417d-b8fd-2158f1256c38': {'National': 'http://www.allindianewspapers.com/Feeds/states.xml'},
    '5b32994e-2e6e-417f-ba44-77f508742349': {'National': 'https://www.business-standard.com/rss/home_page_top_stories.rss'},
    '65cb3dec-94a9-4274-b518-543c74e14a59': 'https://asia.nikkei.com/rss/feed/nar',
    '7eba470b-1edc-4f69-840d-99cfde3a5fcb': 'http://www.abc.net.au/news/feed/2942460/rss.xml',
    '890d11b8-05e7-416e-b777-7ba62f4a7045': 'https://www.economist.com/international/rss.xml',
    '8cbc9eec-7255-43bf-bb72-2bce4f4764ea': {'National': 'https://feeds.feedburner.com/ndtvnews-cities-news?format=xml'},
    '91272662-bb73-4649-a8c2-026d112c190e': {'National': 'https://www.livemint.com/rss/news'},
    'a70e9599-4480-46d2-889f-652fdd58cc55': {'Delhi': 'https://indianexpress.com/section/cities/delhi/feed/', 'Lucknow' : 'https://www.indianexpress.com/section/cities/lucknow/feed/', 'Pune' : 'https://www.indianexpress.com/section/cities/pune/feed/', 'Chandigarh' : 'https://indianexpress.com/section/cities/chandigarh/feed/', 'Mumbai': 'https://indianexpress.com/section/cities/mumbai/feed/', 'Kolkata' : 'https://indianexpress.com/section/cities/kolkata/feed/', 'Ludhiana' : 'https://indianexpress.com/section/cities/ludhiana/feed/', 'Gujarat': 'https://indianexpress.com/section/india/education/feed/', 'Maharashtra' : 'https://indianexpress.com/section/india/maharashtra/feed/', 'Uttar Pradesh': 'https://indianexpress.com/section/india/uttar-pradesh/feed/', 'West Bengal': 'https://indianexpress.com/section/india/west-bengal/feed/', 'Punjab and Haryana': 'https://indianexpress.com/section/india/punjab-and-haryana/feed/'},
    'a9ecac2e-a7da-4bbd-b326-103de3149ece': 'http://feeds.bbci.co.uk/news/world/rss.xml',
    'ad60ab7b-906b-467d-b29e-92f200eb88fe': {'National': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms'},
    'bef37780-c007-4b96-89f4-5198b69f2c93': 'https://www.theguardian.com/world/rss',
    'c1f4a45b-aa9c-4627-980b-f69509e5c862': {'Andhra Pradesh': 'https://www.thehindu.com/news/national/andhra-pradesh/feeder/default.rss', 'Karnataka': 'https://www.thehindu.com/news/national/karnataka/feeder/default.rss', 'Kerala': 'https://www.thehindu.com/news/national/kerala/feeder/default.rss', 'Tamil Nadu': 'https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss', 'Telangana': 'https://www.thehindu.com/news/national/telangana/feeder/default.rss', 'Bengaluru': 'https://www.thehindu.com/news/cities/bangalore/feeder/default.rss', 'Chennai' : 'https://www.thehindu.com/news/cities/chennai/feeder/default.rss', 'Coimbatore': 'https://www.thehindu.com/news/cities/Coimbatore/feeder/default.rss', 'Delhi': 'https://www.thehindu.com/news/cities/Delhi/feeder/default.rss', 'Hyderabad': 'https://www.thehindu.com/news/cities/Hyderabad/feeder/default.rss', 'Kochi': 'https://www.thehindu.com/news/cities/Kochi/feeder/default.rss', 'Kolkata': 'https://www.thehindu.com/news/cities/kolkata/feeder/default.rss', 'Mumbai': 'https://www.thehindu.com/news/cities/mumbai/feeder/default.rss', 'Kozhikode': 'https://www.thehindu.com/news/cities/kozhikode/feeder/default.rss', 'Madurai': 'https://www.thehindu.com/news/cities/Madurai/feeder/default.rss', 'Mangaluru': 'https://www.thehindu.com/news/cities/Mangalore/feeder/default.rss', 'Puducherry': 'https://www.thehindu.com/news/cities/puducherry/feeder/default.rss', 'Thiruvananthapuram': 'https://www.thehindu.com/news/cities/Thiruvananthapuram/feeder/default.rss', 'Tiruchirapalli': 'https://www.thehindu.com/news/cities/Tiruchirapalli/feeder/default.rss', 'Vijayawada': 'https://www.thehindu.com/news/cities/Vijayawada/feeder/default.rss', 'Visakhapatnam': 'https://www.thehindu.com/news/cities/Visakhapatnam/feeder/default.rss'},
    'ca3c6507-8c4a-4269-a384-8de06f43bc4f': {'Mumbai': 'https://timesofindia.indiatimes.com/rssfeeds/-2128838597.cms', 'Delhi': 'https://timesofindia.indiatimes.com/rssfeeds/-2128839596.cms', 'Bangalore': 'http://timesofindia.indiatimes.com/rssfeeds/-2128833038.cms', 'Hyderabad': 'https://timesofindia.indiatimes.com/rssfeeds/-2128816011.cms', 'Chennai': 'http://timesofindia.indiatimes.com/rssfeeds/2950623.cms', 'Ahemdabad': 'https://timesofindia.indiatimes.com/rssfeeds/-2128821153.cms', 'Allahabad': 'https://timesofindia.indiatimes.com/rssfeeds/3947060.cms', 'Bhubaneswar': 'https://timesofindia.indiatimes.com/rssfeeds/4118235.cms', 'Coimbatore': 'https://timesofindia.indiatimes.com/rssfeeds/7503091.cms', 'Gurgaon': 'https://timesofindia.indiatimes.com/rssfeeds/6547154.cms', 'Guwahati': 'https://timesofindia.indiatimes.com/rssfeeds/4118215.cms', 'Hubli': 'https://timesofindia.indiatimes.com/rssfeeds/3942695.cms', 'Kanpur': 'https://timesofindia.indiatimes.com/rssfeeds/3947067.cms', 'Kolkata': 'https://timesofindia.indiatimes.com/rssfeeds/-2128830821.cms', 'Ludhiana': 'http://timesofindia.indiatimes.com/rssfeeds/3947051.cms', 'Mangalore': 'https://timesofindia.indiatimes.com/rssfeeds/3942690.cms', 'Mysore': 'https://timesofindia.indiatimes.com/rssfeeds/3942693.cms', 'Noida': 'https://timesofindia.indiatimes.com/rssfeeds/8021716.cms', 'Pune': 'https://timesofindia.indiatimes.com/rssfeeds/-2128821991.cms', 'Goa': 'http://timesofindia.indiatimes.com/rssfeeds/3012535.cms', 'Chandigarh': 'https://timesofindia.indiatimes.com/rssfeeds/-2128816762.cms', 'Lucknow': 'https://timesofindia.indiatimes.com/rssfeeds/-2128819658.cms', 'Patna': 'http://timesofindia.indiatimes.com/rssfeeds/-2128817995.cms', 'Jaipur': 'https://timesofindia.indiatimes.com/rssfeeds/3012544.cms', 'Nagpur': 'https://timesofindia.indiatimes.com/rssfeeds/442002.cms', 'Rajkot': 'https://timesofindia.indiatimes.com/rssfeeds/3942663.cms', 'Ranchi': 'https://timesofindia.indiatimes.com/rssfeeds/4118245.cms', 'Surat': 'https://timesofindia.indiatimes.com/rssfeeds/3942660.cms', 'Vadodara': 'https://timesofindia.indiatimes.com/rssfeeds/3942666.cms', 'Varanasi': 'https://timesofindia.indiatimes.com/rssfeeds/3947071.cms', 'Thane': 'https://timesofindia.indiatimes.com/rssfeeds/3831863.cms', 'Thiruvananthapuram': 'https://timesofindia.indiatimes.com/rssfeeds/878156304.cms'},
    'd33446c7-a37b-4c5b-ba7a-275cc9583c05': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
    'e43b544e-577b-4ed0-adb0-4661bda4c487': {'National': 'https://www.asianage.com/rss_feed/'},
    'e5a8f17c-58c6-4087-a5c0-2ab681446611': 'http://rss.cnn.com/rss/edition.rss',
    'eeff09cb-6fdb-45f1-a206-32a55320d598': {'National': 'https://www.deccanchronicle.com/rss_feed/'},
    '9bb25aa5-2536-4c0e-b897-c957b8de61d0': {'Amritsar': 'https://www.tribuneindia.com/rss/feed?catId=17', 'Bathinda': 'https://www.tribuneindia.com/rss/feed?catId=18', 'Chandigarh': 'https://www.tribuneindia.com/rss/feed?catId=20', 'Delhi': 'https://www.tribuneindia.com/rss/feed?catId=24', 'Jalandhar': 'https://www.tribuneindia.com/rss/feed?catId=34', 'Ludhiana': 'https://www.tribuneindia.com/rss/feed?catId=40', 'Patiala': 'https://www.tribuneindia.com/rss/feed?catId=213'},
    'ffgg09cb-6gef-45g1-b206-32b55320e598': {'Jammu and Kashmir': 'https://prod-qt-images.s3.amazonaws.com/production/greaterkashmir/feed.xml'},
    'e6a9f28c-69c7-5198-a6c1-3ab792557722': {'Jammu and Kashmir': 'https://web.statetimes.in/feed/'},
    'f5b8g17d-58d6-4087-b5d0-2bc681446611': {'Jammu and Kashmir': 'https://www.dailyexcelsior.com/feed/'}}

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
                cities['International'] = val
                rss.append(cities)
        else:
            print('news_id not found')
            print('skipping:', news_id)
            continue

    return rss
    

def rss2news(rss):

    news_link = []

    for rss_link in rss:

        for k, v in rss_link.items():

            try:

                NewsFeed = feedparser.parse(v)

                for news in NewsFeed.entries:

                    link_dict = {}
                    link_dict[k] = news['link']

                    if 'published' in news.keys():

                        week = datetime.now() - timedelta(days=1)
                        week = week.strftime("%Y-%m-%d %H:%M:%S")
                        date = parse(news['published'].split('+')[0])
                        date = date.strftime("%Y-%m-%d %H:%M:%S")

                        if date >= week:

                            link_dict[k] = news['link']
                            link_dict['published'] = news['published']
                            news_link.append(link_dict)

                        else:                            
                            print('date is not greater than week')
                            print('skipping:', news['link'])
                            continue
                    else:
                        print('published not found in news.keys')
                        link_dict[k] = news['link']
                        link_dict['published'] = datetime.now()
                        news_link.append(link_dict)
                        # print('skipping:', news['link'])
                        # continue

            except Exception as e:

                print("feedparser error:", e)

    return news_link


def _incre_mode(batch_id):

    ua = UserAgent()

    # USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
    USER_AGENT = ua.random
    HEADERS = {'user-agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    # HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    
    config = Config()
    # config.browser_user_agent = USER_AGENT
    config.headers = HEADERS
    config.request_timeout = 40        
    
    dbs = current_ids()
    fps = current_ids_fps()
    cities = current_ids_cities()
    names = current_ids_names()
    fps['fp_name'] = fps['fp_name'].split(',')
    fps['fp_name'] = [x.strip() for x in fps['fp_name'] if x.strip()]
    fps['fp_name'] = list(set(fps['fp_name']))
    fps['fp_city'] = fps['fp_city'].split(',')
    fps['fp_city'] = [x.strip() for x in fps['fp_city'] if x.strip()]
    fps['fp_city'] = list(set(fps['fp_city']))
    cities['cities'] = cities['cities'].split(',')
    cities['cities'] = [x.strip() for x in cities['cities'] if x.strip()]
    cities['cities'] = list(set(cities['cities']))
    cities['cities'] = [x.lower() for x in cities['cities']]
    names['names'] = names['names'].split(',')
    names['names'] = [x.strip() for x in names['names'] if x.strip()]
    names['names'] = list(set(names['names']))
    names['names'] = [x.lower() for x in names['names']]    # print('fp_name:', fps['fp_name'])
    # print('fp_city:', fps['fp_city'])
    # print('cities:', cities['cities'])


    # print(dbs)
    
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
    
    print('rsses are:', rss)

    news_link = rss2news(rss)
    print('total news articles from rss are:', len(news_link))
    # print(news_link)

    news_link2 = restricted_sources()
    print('length of google news-link are:', len(news_link2))

    # print('google news links are:', news_link2)

    # news_link2 = restricted_sources()
    # print('length of google news-link:', len(news_link2))

    # news_link += news_link2
    # print('total news articles are:', len(news_link))
    # news_link = []
    news_link += news_link2
    print('total news articles are:', len(news_link))
    # print('total news links are:', news_link)

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

    # last_batch = dbs[-1]

    if "ParseExisting" in dbs.keys():

        print('----------------- Parse Existing ------------------------')

        # print(dbs)

        if dbs["ParseExisting"]:
            client = MongoClient('localhost', 27017)
            db = client['adverse_db']
            collection_batches = db['adverse_db']
            # cursor = collection_batches.find({}, {'_id': False})
            cursor = collection_batches.find({})

            for document in cursor:
                # print(document)
                document['Person Name mentioned in the news'] = ''
                document['Organization Name mentioned in the news'] = ''
                document['City/ State mentioned under the news'] = ''

                try:
                    article = Article(document['Web link of news'], config=config)
                    article.download()
                    article.parse()
                    soup = BeautifulSoup(article.html, 'html.parser')

                    text = soup_text(soup, document['Source Name'])

                    if not text:
                        text = article.title + os.linesep + article.text

                    text2 = text.split('\n')

                    # print('length of article:', len(text2))

                    for i in range(len(text2)):

                        doc = nlp_Name(text2[i])

                        # iterate through each entity present
                        for count,ent in enumerate(doc.ents):

                            if ent.label_ == 'PERSON':
                                document['Person Name mentioned in the news'] += ent.text + ', '

                            elif ent.label_ == 'ORG':
                                document['Organization Name mentioned in the news'] += ent.text + ', '

                            elif ent.label_ == 'GPE':
                                document['City/ State mentioned under the news'] += ent.text + ', '

                            # find persons in text
                            elif ent.label_ == 'LOC':
                                document['City/ State mentioned under the news'] += ent.text + ', '

                            # find persons in text
                            elif ent.label_ == 'FAC':
                                document['City/ State mentioned under the news'] += ent.text + ', '


                            else:
                                continue

                        # _loc = text2[i].split(':')

                        # _loc = [y for x in _loc for y in x.split(' ')]

                        # _loc = [x.strip() for x in _loc]

                        # _loc = [x for x in _loc if x.lower() in cities['cities']]

                        # print('location:detected:', _loc)

                        # for __loc in _loc:
                            # document['City/ State mentioned under the news'] += __loc + ', '


                    document['Organization Name mentioned in the news'] = document['Organization Name mentioned in the news'].split(',')
                    document['Organization Name mentioned in the news'] = [x.strip() for x in document['Organization Name mentioned in the news'] if x.strip()]
                    document['Organization Name mentioned in the news'] = list(set(document['Organization Name mentioned in the news']))
                    document['Person Name mentioned in the news'] = document['Person Name mentioned in the news'].split(',') + document['Organization Name mentioned in the news']
                    document['Person Name mentioned in the news'] = [x.strip() for x in document['Person Name mentioned in the news'] if x.strip()]
                    document['Person Name mentioned in the news'] = list(set(document['Person Name mentioned in the news']))
                    document['Person Name mentioned in the news'] = [ i for i in document['Person Name mentioned in the news'] if not any( [ i in a for a in document['Person Name mentioned in the news'] if a != i]   )]
                    person_dict = {k.lower():k for k in document['Person Name mentioned in the news']}
                    document['Person Name mentioned in the news'] = list(person_dict.values())
                    document['Person Name mentioned in the news'] = [i for i in document['Person Name mentioned in the news'] if i not in fps['fp_name']]
                    document['Person Name mentioned in the news'] = [i for i in document['Person Name mentioned in the news'] if "covid" not in i.lower()]
                    # document['Person Name mentioned in the news'] = [i.split("’")[0] for i in document['Person Name mentioned in the news']]

                    for name in document['Person Name mentioned in the news']:
                        if name.lower() in cities['cities']:
                            document['Person Name mentioned in the news'].remove(name)
                            document['City/ State mentioned under the news'] += name + ', '


                    document['Person Name mentioned in the news'] = ', '.join(document['Person Name mentioned in the news'])    

                    # document['Person Name mentioned in the news'] = lowercase_check(document['Person Name mentioned in the news'])
                    # document['Person Name mentioned in the news'] = ', '.join(document['Person Name mentioned in the news'])    
                    document['Organization Name mentioned in the news'] = ', '.join(document['Organization Name mentioned in the news'])    
                    document['City/ State mentioned under the news'] = document['City/ State mentioned under the news'].split(',')
                    document['City/ State mentioned under the news'] = [x.strip() for x in document['City/ State mentioned under the news'] if x.strip()]
                    document['City/ State mentioned under the news'] = list(set(document['City/ State mentioned under the news']))
                    document['City/ State mentioned under the news'] = [ i for i in document['City/ State mentioned under the news'] if not any( [ i in a for a in document['City/ State mentioned under the news'] if a != i]   )]
                    city_dict = {k.lower():k for k in document['City/ State mentioned under the news']}
                    document['City/ State mentioned under the news'] = list(city_dict.values())
                    document['City/ State mentioned under the news'] = [i for i in document['City/ State mentioned under the news'] if i not in fps['fp_city']]
                    document['City/ State mentioned under the news'] = [i for i in document['City/ State mentioned under the news'] if "covid" not in i.lower()]
                    # document['City/ State mentioned under the news'] = [i.split("’")[0] for i in document['City/ State mentioned under the news']]

                    for name in document['City/ State mentioned under the news']:

                        if name.lower() in names['names']:

                            document['City/ State mentioned under the news'].remove(name)

                            document['Person Name mentioned in the news'] += ', ' + name

                    document['City/ State mentioned under the news'] = ', '.join(document['City/ State mentioned under the news'])

                    # document['City/ State mentioned under the news'] = lowercase_check(document['City/ State mentioned under the news'])
                    # document['City/ State mentioned under the news'] = ', '.join(document['City/ State mentioned under the news'])
                    document['updated_date'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                    if not document['Article Date']:
                        continue

                    collection_batches.save(document)


                except Exception as e:
                    print('parse_existing exception:', e)

            print("------------------ Parse Existing Complete:-----------------------")

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

          profile['sourcename'] = val[0].split('/')[2]

          article = Article(val[0], config=config)
          article.download()
          article.parse()
          soup = BeautifulSoup(article.html, 'html.parser')

          text = soup_text(soup, profile['sourcename'])

          if not text:
            text = article.title + os.linesep + article.text
            # print(text)


          # text = soup_text(profile['sourcename'])
          

          # if 'economictimes.indiatimes' in profile['sourcename']:
          #   soup = BeautifulSoup(article.html, 'html.parser')

          #   regex = re.compile('.*artText.*')
          #   text = [tag.get_text() for tag in soup.find_all("div", {"class" : regex})]
          #   if text:
          #       text = '\n'.join(text)
          #   else:
          #       regex = re.compile('.*content1.*')
          #       text = [tag.get_text() for tag in soup.find_all("div", {"class" : regex})]
          #       if text:
          #           text = '\n'.join(text)
          #       else:
          #           text = article.title.lower() + os.linesep + article.text.lower()
          # elif 'timesofindia.indiatimes' in profile['sourcename']:
          #   soup = BeautifulSoup(article.html, 'html.parser')

          #   regex = re.compile('.*Normal.*')
          #   text = [tag.get_text() for tag in soup.find_all("div", {"class" : regex})]
          #   if text:
          #       text = '\n'.join(text)
          #   else:
          #       text = article.title.lower() + os.linesep + article.text.lower()
          # else:
          #   text = article.title.lower() + os.linesep + article.text.lower()






            # tag = soup.body

            # iterate through each string
            # for string in tag.stripped_strings:

                # for keyword in keywords:
                    # if keyword.lower() in str(string).lower():
                        # if keyword.lower() not in profile['keyword'].lower():
                            # profile['keyword'] += keyword + ', '
                        # else:
                            # continue

                # if 'hdfc' in str(string).lower():
                #     profile['hdfcpresent'] = 'YES'

                # doc = nlp_Name(str(string))

                # iterate through each entity present
                # for count,ent in enumerate(doc.ents):

                    # save data in profile
                    # find persons in text
                    # if ent.label_ == 'PERSON':
                    #     profile['name'] += ent.text + ', '
                        # remove name if present in false positives
                        # if (ent.text not in profile['name']):
                        # print(str(string))
                        # profile['name'] += ent.text + ', '
                        # else:
                        # print(ent.text)
                        # pass
                    # find persons in text
                    # elif ent.label_ == 'ORG':
                    #     profile['org'] += ent.text + ', '

                        # remove name if present in false positives
                        # if (ent.text not in profile['org']):
                        # profile['org'] += ent.text + ', '
                        # else:
                        # print(ent.text)
                        # pass

                        # find persons in text
                    # elif ent.label_ == 'GPE':
                    #     profile['loc'] += ent.text + ', '
                        # remove name if present in false positives
                        # if (ent.text not in profile['loc']):
                        # profile['loc'] += ent.text + ', '
                        # else:
                        # print(ent.text)
                        # pass
                    # else:
                    #     pass

            # profile['date'] = link['published'] # article.publish_date
            # profile['cities'] = keys[0]
            # profile['batch_id'] = batch_id
            # profile['created_date'] = datetime.now()
            # profile['org'] = profile['org'].split(',')
            # print(profile['org'])
            # profile['org'] = [x.strip() for x in profile['org'] if x.strip()]
            # profile['org'] = list(set(profile['org']))
            # # profile['org'] = ', '.join(profile['org'])    
            # profile['name'] = profile['name'].split(',') + profile['org']
            # print(profile['name'])
            # profile['name'] = [x.strip() for x in profile['name'] if x.strip()]
            # profile['name'] = list(set(profile['name']))
            # # check if any name is a subset of any other name
            # profile['name'] = [ i for i in profile['name'] if not any( [ i in a for a in profile['name'] if a != i]   )]
            # # profile['name'] = [ i.lower() for i in profile['name']]
            # # profile['name'] = list(set(profile['name']))
            # # profile['name'] = [ i.title() for i in profile['name']]
            # # profile['name'] = subset(profile['name'])
            # profile['name'] = lowercase_check(profile['name'])
            # profile['name'] = ', '.join(profile['name'])    
            # profile['org'] = ', '.join(profile['org'])    
            # profile['loc'] = profile['loc'].split(',')
            # print(profile['loc'])
            # profile['loc'] = [x.strip() for x in profile['loc'] if x.strip()]
            # profile['loc'] = list(set(profile['loc']))
            # # check if any name is a subset of any other name
            # profile['loc'] = [ i for i in profile['loc'] if not any( [ i in a for a in profile['loc'] if a != i]   )]
            # # profile['loc'] = [ i.lower() for i in profile['loc']]
            # # profile['loc'] = list(set(profile['loc']))
            # # profile['loc'] = [ i.title() for i in profile['loc']]
            # # profile['loc'] = subset(profile['loc'])
            # profile['loc'] = lowercase_check(profile['loc'])
            # profile['loc'] = ', '.join(profile['loc'])

            # print(profile) 
             
            # _writer.writerow(profile)




          # text = article.title.lower() + os.linesep + article.text.lower()
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
    
            elif len(keyword.split(' ')) > 1:
                found = []
                _keyword = keyword.split(' ')
                for __keyword in _keyword:
                    if __keyword.lower() in text.lower():
                        found.append(__keyword)
                    else:
                        continue

                if len(found) == len(_keyword):
                    profile['keyword'] += keyword + ', '

          if 'hdfc' in text.lower():
            profile['hdfcpresent'] = 'YES'

          profile['weblink'] = article.url
    
          profile['sourcename'] = val[0].split('/')[2]
    
          if profile['keyword']:

            # remove Getty Images
            # text = text.replace('Getty Images', '')

            # remove Covid
            # text = text.replace('Covid', '')

            text2 = text.split('\n')

            # print('length of article:', len(text2))

            for i in range(len(text2)):
                
                doc = nlp_Name(text2[i])

                # doc = nlp_Name(article.title + os.linesep + article.text)

                # iterate through each entity present
                for count,ent in enumerate(doc.ents):
                    # save data in profile
                    # find persons in text
                    if ent.label_ == 'PERSON':
                        profile['name'] += ent.text + ', '

                    # find persons in text
                    elif ent.label_ == 'ORG':
                        profile['org'] += ent.text + ', '

                    # find persons in text
                    elif ent.label_ == 'GPE':
                        profile['loc'] += ent.text + ', '

                    # find persons in text
                    elif ent.label_ == 'LOC':
                        profile['loc'] += ent.text + ', '

                    # find persons in text
                    elif ent.label_ == 'FAC':
                        profile['loc'] += ent.text + ', '

                    else:
                        continue
    
    
            profile['date'] = link['published'] # article.publish_date
            profile['cities'] = keys[0]
            profile['batch_id'] = batch_id
            profile['created_date'] = datetime.now()
            profile['org'] = profile['org'].split(',')
            # print(profile['org'])
            profile['org'] = [x.strip() for x in profile['org'] if x.strip()]
            profile['org'] = list(set(profile['org']))
            # profile['org'] = ', '.join(profile['org'])    
            profile['name'] = profile['name'].split(',') + profile['org']
            # print(profile['name'])
            profile['name'] = [x.strip() for x in profile['name'] if x.strip()]
            profile['name'] = list(set(profile['name']))
            # check if any name is a subset of any other name
            profile['name'] = [ i for i in profile['name'] if not any( [ i in a for a in profile['name'] if a != i]   )]
            # profile['name'] = [ i.lower() for i in profile['name']]
            # profile['name'] = list(set(profile['name']))
            # profile['name'] = [ i.title() for i in profile['name']]
            # profile['name'] = subset(profile['name'])
            # profile['name'] = lowercase_check(profile['name'])
            person_dict = {k.lower():k for k in profile['name']}
            profile['name'] = list(person_dict.values())
            profile['name'] = [i for i in profile['name'] if i not in fps['fp_name']]
            profile['name'] = [i for i in profile['name'] if "covid" not in i.lower()]
            # profile['name'] = [i.split("’")[0] for i in profile['name']]

            for name in profile['name']:
                if name.lower() in cities['cities']:
                    profile['name'].remove(name)
                    profile['loc'] += name + ', '



            
            profile['name'] = ', '.join(profile['name'])    
            profile['org'] = ', '.join(profile['org'])    
            profile['loc'] = profile['loc'].split(',')
            # print(profile['loc'])
            profile['loc'] = [x.strip() for x in profile['loc'] if x.strip()]
            profile['loc'] = list(set(profile['loc']))
            # check if any name is a subset of any other name
            profile['loc'] = [ i for i in profile['loc'] if not any( [ i in a for a in profile['loc'] if a != i]   )]
            # profile['loc'] = [ i.lower() for i in profile['loc']]
            # profile['loc'] = list(set(profile['loc']))
            # profile['loc'] = [ i.title() for i in profile['loc']]
            # profile['loc'] = subset(profile['loc'])
            # profile['loc'] = lowercase_check(profile['loc'])
            city_dict = {k.lower():k for k in profile['loc']}
            profile['loc'] = list(city_dict.values())
            profile['loc'] = [i for i in profile['loc'] if i not in fps['fp_city']]
            profile['loc'] = [i for i in profile['loc'] if "covid" not in i.lower()]
            # profile['loc'] = [i.split("’")[0] for i in profile['loc']]

            for name in profile['loc']:
                if name.lower() in names['names']:
                    profile['loc'].remove(name)
                    profile['name'] += ', ' + name


            profile['loc'] = ', '.join(profile['loc'])

            # print(profile) 
             
            _writer.writerow(profile)
    
          else:
            print('keyword not found')
            print('skipping:', article.url)
            continue
            # print(profile)
    
        except Exception as e:
          print('_incre_mode:', e)
          print('skipping:', val[0])

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

    print('total number of records saving:', len(df))

    
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
          print('skipping:', _dict['Web link of news'])
          continue
        # check for duplicate names
        # elif check_duplicate_name(_dict['Person Name mentioned in the news']):
          # print('Names intersection crosses threshold')
          # print('skipping:', _dict['Web link of news'])
          # continue
        elif not _dict['Article Date']:
          print('Article Date not found')
          print('skipping:', _dict['Web link of news'])
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

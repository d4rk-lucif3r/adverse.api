#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# used to make HTTP requests to the Elasticsearch cluster
import requests

# import 'json' to convert strings to JSON format
import json

import ast
from datetime import datetime
import re
import pymongo
from pymongo import MongoClient
import time
import bson
import pytz    
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import LanguageTranslatorV3
from googletrans import Translator


translator = Translator()

def CityOfNewspaper(url):

    city2idx = {
    'www.tribuneindia.com':4,
    'mumbaimirror.indiatimes.com':3,
    'timesofindia.indiatimes.com':4,
    'www.ndtv.com':4,
    }

    fp_cities = [
    'Nation',
    'World',
    'Diaspora',
    'Editorials',
    'Comment',
    'Entertainment',
    'Sciencetechnology',
    'Science',
    'Technology',
    'Coronavirus',
    'Us',
    'Uk',
    'City',
    'Europe',
    'International',
    'Hindi',
    'Pakistan',
    'News',
    'China',
    'Lifestyle',
    'Malayalam',
    ]

    DefaultCities = [
    'www.deccanchronicle.com',
    'www.asianage.com',
    'economictimes.indiatimes.com',
    'www.livemint.com',
    ]

    if url.split('/')[2] not in list(city2idx.keys()):
        return 'National'

    idx = city2idx[url.split('/')[2]]
    city = url.split('/')[idx].title()

    print('city:', city)
    if city in fp_cities or any(not c.isalnum() for c in city):
        return 'National'
    return city

def detect_lang(text):
    if text.strip():
        KEY = 'IE8hVfhy0XCdw2gFGKQous7etnspEN66OTWsnB_bEhe2'
        SERVICE_URL = 'https://api.eu-gb.language-translator.watson.cloud.ibm.com/instances/1c656c34-6170-4a20-be18-57f030abacf0'

        authenticator = IAMAuthenticator(KEY)
        language_translator = LanguageTranslatorV3(
            version='2018-05-01',
            authenticator=authenticator
            )
        
        language_translator.set_service_url(SERVICE_URL)
        lang = language_translator.identify(text).get_result()

        return lang['languages'][0]['language']


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

def update_current_names(names=''):
    '''
    function to update sources ids and keywords into database
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['names']
    post = collection_batches.find_one({'_id': bson.objectid.ObjectId("608fd0093532c6e24763040e")})
    if post:
        if names:
            temp_name = post['names'].split(',')
            names = names.split(',')
            names = [x.strip() for x in names if x.strip()]
            temp_name = [x.strip() for x in temp_name if x.strip()]
            temp_name += names
            temp_name = list(set(temp_name))
            temp_name = ', '.join(temp_name)
            post['names'] = temp_name
            post['last_updated_time'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        collection_batches.save(post)

    return "Updated Document"


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


def update_fp(fp_name='', fp_city=''):
    '''
    function to update false positives list in mongodb
    '''
    batch = {}
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['fp_list']
    post = collection_batches.find_one({'_id': bson.objectid.ObjectId("60799419ba4eda7932fc2ec2")})
    if post:
        if fp_name and fp_city:
            temp_name = post['fp_name'].split(',')
            fp_name = fp_name.split(',')
            fp_name = [x.strip() for x in fp_name if x.strip()]
            temp_name = [x.strip() for x in temp_name if x.strip()]
            temp_name += fp_name
            temp_name = list(set(temp_name))
            temp_name = ', '.join(temp_name)
            post['fp_name'] = temp_name
            temp_city = post['fp_city'].split(',')
            fp_city = fp_city.split(',')
            fp_city = [x.strip() for x in fp_city if x.strip()]
            temp_city = [x.strip() for x in temp_city if x.strip()]
            temp_city += fp_city
            temp_city = list(set(temp_city))
            temp_city = ', '.join(temp_city)
            post['fp_city'] = temp_city
            post['last_updated_time'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        elif fp_city:
            temp_city = post['fp_city'].split(',')
            fp_city = fp_city.split(',')
            fp_city = [x.strip() for x in fp_city if x.strip()]
            temp_city = [x.strip() for x in temp_city if x.strip()]
            temp_city += fp_city
            temp_city = list(set(temp_city))
            temp_city = ', '.join(temp_city)
            post['fp_city'] = temp_city
            post['last_updated_time'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        elif fp_name:
            temp_name = post['fp_name'].split(',')
            fp_name = fp_name.split(',')
            fp_name = [x.strip() for x in fp_name if x.strip()]
            temp_name = [x.strip() for x in temp_name if x.strip()]
            temp_name += fp_name
            temp_name = list(set(temp_name))
            temp_name = ', '.join(temp_name)
            post['fp_name'] = temp_name

        collection_batches.save(post)

    return "Updated Document"

def update_parse_existing(_id):
    '''
    function to save batch table in mongodb
    '''
    batch = {}
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['news_ids']
    # db = client['BatchRunStatus']
    # collection_batches = db['DetailStatus']
    post = collection_batches.find_one({'_id': bson.objectid.ObjectId(_id)})
    if post:
        print(post)
        # post["UpdateDate"] = time.strftime("%Y-%m-%d %H:%M:%S")
        post["ParseExisting"] = True
        collection_batches.save(post)

    return "Updated Document"


def soup_text(soup, sourcename):

    text_ = []

    dictionary = {
    # 'www.hindustantimes.com': {'h1': ['hdg1', 'hdg3'], 'div': ['sortDec', 'detail', 'storyDetails']},
    # 'www.dnaindia.com': {'div': ['container']},
    # 'www.business-standard.com': {'h1': ['headline'], 'h2': ['alternativeHeadline'], 'span': ['p-content']},
    'maharashtratimes.com': {'Headlines': {'h1': {'itemprop': ['headline']}}, 'Synopsis': {'h2': ['caption text_ellipsis more'], 'div': ['undefined top-article tophighlight']}, 'Text': {'article': ['story-content']}},
    'www.greaterkashmir.com': {'Headlines': {'h1': ['story-headline-m__headline__1LzaJ story-headline-m__dark__1wPld']}, 'Text': {'div': ['arr--story-page-card-wrapper']}},
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
        print('sourcename:', sourcename)
        tag_class = dictionary[sourcename]
        print('tag_class:', tag_class)
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
        print(e)
        return None

    if text_:
        print(text_)
        # return '\n'.join(text_)
        return ' '.join(text_)
    else:
        print('text not found')
        return None

def fnc_(x):
  try:
    x = x.strip(', ')
    return x
  except:
    return x


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

def update_ids_dbs(keywords, news_source_ids, fp_name='', fp_city='', cities='', names=''):
    '''
    function to update sources ids and keywords into database
    '''
    dbs = {}
    update_db = {}
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['news_ids']
    dbs['keywords'] = keywords
    dbs['news_source_ids'] = news_source_ids
    if fp_name and fp_city and cities:
        dbs['fp_name'] = fp_name
        dbs['fp_city'] = fp_city
        update_fp(fp_name, fp_city)
        update_current_cities(cities)
    elif fp_name and fp_city:
        dbs['fp_name'] = fp_name
        dbs['fp_city'] = fp_city
        update_fp(fp_name, fp_city)
    elif fp_city:
        dbs['fp_city'] = fp_city
        update_fp(fp_city)
    elif fp_name:
        dbs['fp_name'] = fp_name
        update_fp(fp_name)
    elif cities:
        update_current_cities(cities)
    elif names:
        update_current_names(names)

    tz_NY = pytz.timezone('Asia/Kolkata')
    datetime_NY = datetime.now(tz_NY)  

    dbs['last_updated_time'] = datetime_NY.strftime("%Y-%m-%d %H:%M:%S")
    collection_batches.insert(dbs)
    # print("Batch Run ingesting into DB")
    collection_batches.create_index([("news_ids", pymongo.ASCENDING)])
    # print("BatchId is created")
    return "Successfully Updated keywords and news source ids, cities, names and false positives"

def current_ids_dbs():
    '''
    function to update sources ids and keywords into database
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['news_ids']
    # cursor = collection_batches.find({}, {'_id': False})
    cursor = collection_batches.find({})
    dbs = [database for database in cursor]
    return dbs[-1]

def current_dbs():
    '''
    function to retrieve current databases from mongodb
    '''
    client = MongoClient('localhost', 27017)
    db = client['CurrentDatabase']
    collection_batches = db['Databases']
    cursor = collection_batches.find({}, {'_id': False})
    dbs = [database for database in cursor]
    return dbs[-1]

# function for the cURL requests
def elasticsearch_curl(uri='http://localhost:9200/', json_body='', verb='get'):
    # pass header option for content type if request has a
    # body to avoid Content-Type error in Elasticsearch v6.0
    headers = {
        'Content-Type': 'application/json',
    }

    try:
        # make HTTP verb parameter case-insensitive by converting to lower()
        if verb.lower() == "get":
            resp = requests.get(uri, headers=headers, data=json_body)
        elif verb.lower() == "post":
            resp = requests.post(uri, headers=headers, data=json_body)
        elif verb.lower() == "put":
            resp = requests.put(uri, headers=headers, data=json_body)

        # read the text object string
        try:
            resp_text = json.loads(resp.text)
        except:
            resp_text = resp.text

        # catch exceptions and print errors to terminal
    except Exception as error:
        print ('\nelasticsearch_curl() error:', error)
        resp_text = error

    # return the Python dict of the request
    # print ("resp_text:", resp_text)
    return resp_text

# function for search
def search(pep_name):
    pep_name = ''.join([char if ord(char) < 128 else '' for char in pep_name])

    try:
        pep_name = pep_name.replace('"', '')
    except Exception as e:
        pass

    request_body = '{ "query": { "multi_match" : { "query":    "(%s)", "fields": [ "Person Name mentioned in the news", "Organization Name mentioned in the news", "Key word Used for identify the article", "Web link of news", "Source Name" ], "operator":   "and", "fuzziness" : "AUTO" } } }' % pep_name

    # request_body = '{ "query": { "bool": { "must": [ { "match": { "designation": "politician" } }, { "multi_match": { "query": "(%s)", "fields": [ "full_name", "aliases", "first_name", "last_name", "native_name", "birth_name", "father", "mother", "siblings", "spouse", "children", "relatives" ],  "operator":   "AND", "fuzziness" : "AUTO" } } ] } } }' % pep_name

    # request_body = '{ "query": { "bool": { "must": [ { "match": { "designation": "chairman" } } ], "should": [ { "multi_match": { "query": "(%s)", "fields": [ "full_name", "aliases", "first_name", "last_name", "native_name", "birth_name", "father", "mother", "siblings", "spouse", "children", "relatives" ],  "operator":   "AND", "fuzziness" : "AUTO" } } ] } } }' % pep_name

    # request_body = '{ "query": { "filtered": { "query": {"multi_match": { "query": "(%s)", "fields": [ "full_name" ],  "operator":   "AND", "fuzziness" : "AUTO" } }, "filter" : { "should": [ { "match": { "designation": "chairman" } } ] } } } }'

    # request_body = '{ "query": { "multi_match": { "query": "(%s)", "fields": [ "full_name", "aliases", "first_name", "last_name", "native_name", "birth_name", "father", "mother", "siblings", "spouse", "children", "relatives" ],  "operator":   "AND", "fuzziness" : "AUTO" }, "bool": { "must": [ { "match": { "designation": "chairman" } } ], "should": [], "minimum_should_match": 1 } } }' % pep_name

    # request_body = '{ "query": { "bool": { "must": [ { "match": { "designation": "chairman" } } ], "should": [ { "multi_match": { "query": "(%s)", "fields": [ "full_name", "aliases", "first_name", "last_name", "native_name", "birth_name", "father", "mother", "siblings", "spouse", "children", "relatives" ],  "operator":   "AND", "fuzziness" : "AUTO" } } ] } } }' % pep_name

    # request_body = '{ "query": { "bool": { "should": [ { "multi_match": { "query": "chairman", "fields": [ "designation" ], "operator":   "OR", "fuzziness" : "AUTO" } } ], "must": [ { "multi_match": { "query": "(%s)", "fields": [ "full_name", "aliases", "first_name", "last_name", "native_name", "birth_name", "father", "mother", "siblings", "spouse", "children", "relatives" ], "operator":   "and", "fuzziness" : "AUTO" } } ] } } }' % pep_name

    # request_body = '{ "query": { "bool": { "must": [ { "match": { "designation": "chairman" } } ], "should": [ { "multi_match": { "query": "(%s)", "fields": [ "full_name", "aliases", "first_name", "last_name", "native_name", "birth_name", "father", "mother", "siblings", "spouse", "children", "relatives" ],  "operator":   "AND", "fuzziness" : "AUTO" } } ] } } }' % pep_name

    # request_body = '{ "query": { "bool" : { "should": [ { "multi_match" : { "query": "(%s)", "fields": [ "full_name", "aliases", "first_name", "last_name", "native_name", "birth_name", "father", "mother", "siblings", "spouse", "children", "relatives" ], "operator":   "and", "fuzziness" : "AUTO" } } '

    # request_body = '{ "query: { "bool": {"must": {"bool": {"should": [ { "match": { "full_name": "(%s)" } } ] } } } } }' % pep_name
    # request_body = '{ "query": { "multi_match" : { "query":    "(%s)", "fields": [ "full_name", "aliases", "first_name", "last_name", "native_name", "birth_name", "father", "mother", "siblings", "spouse", "children", "relatives" ], "operator":   "and", "fuzziness" : "AUTO" } } }' % pep_name
    
    # print(request_body)

    # current_databases = current_dbs()
    Primary = 'pep_db1' # current_databases['Primary']

    print(Primary)

    # uri = 'http://localhost:9200/%s/_search?pretty=true' % Primary
    uri = 'http://localhost:9200/_search?pretty=true'
    print(uri)

    response = elasticsearch_curl(
        uri,
        verb='get',
        json_body=request_body
    )
    
    print(response)
    
    response = response["hits"]
    match_score = response["max_score"]
    response = response["hits"]
    responses = [x['_source'] for x in response]
    
    for item in responses:
        item.update( {"match_score":match_score})

    return responses

# function for search
def search_pep(pep_name):
    pep_name = ''.join([char if ord(char) < 128 else '' for char in pep_name])

    request_body = '{ "query": { "multi_match" : { "query":    "(%s)", "fields": [ "full_name", "aliases", "first_name", "last_name", "native_name", "birth_name", "father", "mother", "siblings", "spouse", "children", "relatives" ], "operator":   "and" } } }' % pep_name
    
    # print(request_body)

    current_databases = current_dbs()
    Primary = current_databases['Primary']

    # uri = 'http://localhost:9200/%s/_search?pretty=true' % Primary
    uri = 'http://localhost:9200/_search?pretty=true'

    response = elasticsearch_curl(
        uri,
        verb='get',
        json_body=request_body
    )
    
    # print(response)
    
    response = response["hits"]
    match_score = response["max_score"]
    response = response["hits"]
    responses = [x['_source'] for x in response]
    
    for item in responses:
        item.update( {"match_score":match_score})

    return responses

# function for search
def search_spouse(pep_name):
    pep_name = ''.join([char if ord(char) < 128 else '' for char in pep_name])

    request_body = '{ "query": { "multi_match" : { "query":    "(%s)", "fields": [ "father", "mother", "siblings", "children", "relatives" ], "operator":   "and" } } }' % pep_name
    
    # print(request_body)

    current_databases = current_dbs()
    Primary = current_databases['Primary']

    # uri = 'http://localhost:9200/%s/_search?pretty=true' % Primary
    uri = 'http://localhost:9200/_search?pretty=true'
    
    response = elasticsearch_curl(
        uri,
        verb='get',
        json_body=request_body
    )
    
    # print(response)
    
    response = response["hits"]
    match_score = response["max_score"]
    response = response["hits"]
    responses = [x['_source'] for x in response]
    
    for item in responses:
        item.update( {"match_score":match_score})

    return responses

# function for search
def search_spouse2(pep_name):
    pep_name = ''.join([char if ord(char) < 128 else '' for char in pep_name])

    request_body = '{ "query": { "multi_match" : { "query":    "(%s)", "fields": [ "spouse" ], "operator":   "and" } } }' % pep_name
    
    # print(request_body)
    
    current_databases = current_dbs()
    Primary = current_databases['Primary']

    # uri = 'http://localhost:9200/%s/_search?pretty=true' % Primary
    uri = 'http://localhost:9200/_search?pretty=true' #  % Primary
    
    response = elasticsearch_curl(
        uri,
        verb='get',
        json_body=request_body
    )
    
    # print(response)
    
    response = response["hits"]
    match_score = response["max_score"]
    response = response["hits"]
    responses = [x['_source'] for x in response]
    
    for item in responses:
        item.update( {"match_score":match_score})

    return responses

# function for search
def search_relatives(pep_name):
    pep_name = ''.join([char if ord(char) < 128 else '' for char in pep_name])

    request_body = '{ "query": { "multi_match" : { "query":    "(%s)", "fields": [ "father", "mother", "siblings", "spouse", "children" ], "operator":   "and" } } }' % pep_name
    
    # print(request_body)
    
    current_databases = current_dbs()
    Primary = current_databases['Primary']

    # uri = 'http://localhost:9200/%s/_search?pretty=true' % Primary
    uri = 'http://localhost:9200/_search?pretty=true'

    response = elasticsearch_curl(
        uri,
        verb='get',
        json_body=request_body
    )
    
    # print(response)
    
    response = response["hits"]
    match_score = response["max_score"]
    response = response["hits"]
    responses = [x['_source'] for x in response]
    
    for item in responses:
        item.update( {"match_score":match_score})

    return responses

def check_occupation(response):

    find_designation = []

    # filters = ['politician', 'businessman', 'officer', 'director', 'governor', 'officer', 'manager', 'adviser', 'chairman', 'md', 'ceo', 'fgm', 'cgm', 'board', 'pgm', 'secretary', 'cvo', 'minister', 'cs', 'president', 'cmo', 'criminal', 'terrorist', 'mobster']
    # filters = ['businessperson', 'politician', 'mobster']
    filters = ['businessperson']

    if response['occupation']:
        for filter_ in filters:
            if filter_ in response['occupation']:
                find_designation.append(filter_)
            else:
                pass
    else:
        pass

    if find_designation:
        return True
    else:
        return False

def check_dob(response):

    if response['dob']:
        try:
            datetime_object = datetime.strptime(response['dob'], '%Y/%m/%d %H:%M:%S')
            year = int(datetime_object.year)
            if (datetime_object.year < 1900):
                # print('Person is really old')
                return True
        except Exception as e:
            pass

def check_designation(response):

    if check_dob(response):
        # print('persons2 is also old')
        return False
    # elif check_occupation(response):
    #     # print('occupation found')
    #     return True
    else:
        find_designation = []
        # filters = ['politician', 'businessman', 'officer', 'director', 'governor', 'officer', 'manager', 'adviser', 'chairman', 'md', 'ceo', 'fgm', 'cgm', 'board', 'pgm', 'secretary', 'cvo', 'minister', 'cs', 'president', 'cmo', 'criminal', 'terrorist', 'mobster']
        # filters = ['Chairman', 'politician', 'Businessman', 'Former', 'Economist', 'Salesman']
        filters = ['NTPC', 'politician', 'Businessman', 'Minister', 'President', 'SECI', 'ONGC', 
        'IOCL', 'SAIL', 'BHEL', 'HPCL', 'CIL', 'GAIL', 'BPCL', 'POWERGRID', 'BEL', 'PFC', 'HAL', 
        'CEO', 'EIL', 'NMDC', 'RINL', 'SCI', 'NLCIL', 'CONCOR', 'NALCO', 'NBCC', 'OIL', 'AAI', 
        'Balmer Lawrie', 'BCCL', 'BDL', 'BEML', 'BSNL', 'CSL', 'CCIL', 'EdCIL', 'HCL', 'HSCC', 
        'PEC', 'MECON', 'ITDC', 'ITPO', 'IREL', 'MCL', 'MOIL', 'NFL', 'MMTC', 'MSTC', 'Bridge & Roof',
        'Antrix', 'DCI', 'GRSE', 'CPCL', 'GSL', 'HLL', 'MRPL', 'NHPC', 'NEEPCO', 'Pawan Hans', 'PDIL',
        'GM', 'RAILTEL', 'RVNL', 'RCF', 'RITES', 'SJVN', 'SECL', 'TCIL', 'THDC', 'WCL', 'CCL', 'KPL',
        'HUDCO', 'IRDEA', 'KIOCL', 'SPMCIL', 'NCL', 'NSIC', 'IRCON', 'RFCL', 'NRL', 'Mazagon Dock Shipbuilders',
        'MIDHANI', 'STC', 'WAPCOS', 'MECL', 'BECIL', 'CMPDI', 'CRWC', 'EPI', 'FAGMIL', 'FSNL', 'HMT',
        'NFDC', 'REIL', 'CEWACOR', 'Head', 'Manager', 'Secretary', 'CS', 'A G M', 'D G M', 'Ministry',
        'Governor', 'Bank', 'Department', 'Officer', 'FGM', 'MD', 'Chartered Accountant', 'Group',
        'CGM', 'Chief', 'GOVERNOR', 'Member', 'General', 'Speaker', 'CLERK', 'SERGEANT', 'Premier',
        'Government', 'Senator', 'DEPARTMENT', 'Representative', 'Deputy', 'Office', 'Commission',
        'Justices', 'HEADS', 'Councillor', 'Leader', 'Director', 'CMO', 'Government', 'ED',
        'officer', 'Industrialist', 'Former', 'Economist', 'Salesman', 'businessman', 'Financier',
        'Banker', 'Merchant', 'Chairman', 'MLA', 'Seller', 'Dealer', 'limited', 'Group', 'Ltd'
        'Corporate', 'Trader', 'Fraudster', 'launderer', 'Entrepreneur', 'Treasurer', 'Fake',
        'banker', 'Owner', 'Servant', 'official', 'Policeman', 'conman', 'PM', 'Trader', 'Real Estate',
        'Congressman', 'Launderer', 'Lt Gen', 'Officials', 'Offical', 'Ex-rector', 'Justice', 'Financier',
        'Official', 'Stockbroker', 'Fugitive', 'head', 'Accountant', 'nationalist', 'Executives', 'Expert'
        'Councilor', 'FDP', 'CDU', 'SPD', 'AfD', 'Party', 'Alliance', 'Independent', 'Senate', 'MEMBER', 
        'Chair', 'Members', 'Sekretaris', 'Kepala', 'Inspektur', 'Deputi', 'Mayors', 'Princes', 'legislature',
        'Clerk', 'Chairperson', 'Inspector', 'Parliament', 'Presidency', 'MINISTER', 'UNDERSECRETARY', 'SECRETARY'
        'SUBSECRETARIO', 'Mayor', 'Kaihautu', 'Council', 'Sr Adm Asst', 'Executive', 'Dep Secy Gen', 'Dir,',
        'Commissioner', 'Ex Dir', 'Ch Ex' ,'Committee', 'State Adviser', 'Parliamentary', 'MP', 'Judge', 
        'Ambassador', 'Representatives', 'REPRESENTATIVES', 'SPEAKER', 'SENATE', 'Federal', 'Unión', 'Partido',
        'Undersecretary', 'Government', 'Whip', 'criminal', 'mobster', 'terrorist', 'dealer', 'minister', 'Terrorist']

        if response['designation']:
            for filter_ in filters:
                if filter_ in response['designation']:
                    return True
                    # print('find designation in filter')
                    # find_designation.append(filter_)
                else:
                    pass
        else:
            pass

        if find_designation:
            return True
        else:
            return False

def qcode2val(response):
    qregex = re.compile(r'Q\d+')
    if response['political_associations']:
        response['political_associations'] = ast.literal_eval(response['political_associations'])
        response['political_associations'] = [qregex.sub(None, qcode) for qcode in response['political_associations']]
    if response['relatives']:
        response['relatives'] = ast.literal_eval(response['relatives'])
        response['relatives'] = [qregex.sub(None, qcode) for qcode in response['relatives']]
    if response['occupation']:
        response['occupation'] = ast.literal_eval(response['occupation'])
        response['occupation'] = [qregex.sub(None, qcode) for qcode in response['occupation']]
    if response['spouse']:
        response['spouse'] = ast.literal_eval(response['spouse'])
        response['spouse'] = [qregex.sub(None, qcode) for qcode in response['spouse']]
    if response['residence']:
        response['residence'] = ast.literal_eval(response['residence'])
        response['residence'] = [qregex.sub(None, qcode) for qcode in response['residence']]
    if response['children']:
        response['children'] = ast.literal_eval(response['children'])
        response['children'] = [qregex.sub(None, qcode) for qcode in response['children']]
    if response['positions_held']:
        response['positions_held'] = ast.literal_eval(response['positions_held'])
        response['positions_held'] = [qregex.sub(None, qcode) for qcode in response['positions_held']]
    if response['mother']:
        response['mother'] = qregex.sub(None, response['mother'])

    return response

def filter_responses(responses):

    pep_response = []

    if not responses:
        pass
    else:
        for response in responses:
            if check_designation(response) and response['spouse']:
                if ast.literal_eval(response['spouse']):
                    spouses = ast.literal_eval(response['spouse'])

                    pep_response.extend(search_pep(response['full_name']))

                    for spouse in spouses:
                        pep_response.extend(search_spouse(spouse))

            elif check_designation(response):
                pep_response.extend(search_pep(response['full_name']))

            # elif response['spouse']:
            #     if ast.literal_eval(response['spouse']):
            #         spouses = ast.literal_eval(response['spouse'])
            #         for spouse in spouses:
            #             return filter_responses(search_spouse(spouse))

            else:
                pass

    return pep_response

# def search_spouse(response):
    
#     results = []

#     if response['spouse']:
#         if ast.literal_eval(response['spouse']):
#             spouses = ast.literal_eval(response['spouse'])
#             for spouse in spouses:
#                 results.extend(search(spouse))

#     return results

# def filter_pep(responses):
#     designations = [x['designation'] for x in responses if x['designation']]
#     designations = list(set(designations))

#     find_designation = []
#     filters = ['politician', 'businessman', 'officer', 'director', 'governor', 'officer', 'manager', 'adviser', 'chairman', 'md', 'ceo', 'fgm', 'cgm', 'board', 'pgm', 'secretary', 'cvo', 'minister', 'cs', 'president', 'cmo']

#     for designation in designations:
#         for filter_ in filters:
#             if filter_ in designation.lower():
#                 find_designation.append(filter_)
#             else:
#                 pass

#     if find_designation:
#         return True
#     else:
#         return False

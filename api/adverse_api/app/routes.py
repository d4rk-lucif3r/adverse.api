from flask import Flask, request, render_template, jsonify, url_for, redirect
from app import app
from bson.json_util import dumps, loads
from utils import *
import ast
import uuid
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
import newspaper
from newspaper import Article
from faker import Faker
import spacy
import os
from newspaper.utils import BeautifulSoup
from newspaper import Config
import re



f1 = Faker()
nlp_Name = spacy.load("en_core_web_trf")

@app.route('/')
@app.route('/index')
def index():
    return "Adverse Media being prepared for HDFC"


@app.route('/adverseapi', methods=['GET', 'POST'])
def adverseapi():

    if not request.data:
      return """
      API can be called in following modes, please use GET verb in raw body format to invoke the APIs:<br/>
      <br/>
      Please note: you need to use the right API key, please get in touch with IntelleWings.<br/>
      <br/>
      Manual Mode:<br/>
      This mode is meant to fetch data for everyday scan from the news sources.<br/>
      Date parameters needs to specify the “from date” to fetch data.
      <br/>
      {<br/>
      "api" : "4675622ca4d6fc49c6b811df1e9fc1",<br/>
      "mode": "manual",<br/>
      "date": "2021-03-08 15:19:47"<br/>
      }<br/>
      <br/>
      Please note that everyday scan has been running starting Fri, 19 Mar 2021 21:03:15 +0530.<br/>
      <br/>
      Full Mode:<br/>
      This mode is to be used when you need to get whole data available at IntelleWings data source end in one shot.<br/>
      {<br/>
      "api" : "46735622ca4d6fc49c6b811df1e9fc1",<br/>
      "mode": "full"<br/>
      }<br/>
      Please note that everyday scan has been running starting Fri, 19 Mar 2021 21:03:15 +0530.<br/>
      <br/>
      Real-Time Mode:<br/>
      This mode is to be used when you need to get search result from a particular url.<br/>
      This is to test and verify the correctness of parsers in accurately finding matching news articles and correctness of predicting names, this feature may not be required in production<br/>
      <br/>
      {<br/>
      "api" : "46735622ca4d6fc49c6b811df1e9fc1",<br/>
      "mode": "realtime",<br/>
      "keywords": "death",<br/>
      "urltobesearched": "https://www.tribuneindia.com/news/amritsar/two-outsiders-mistaken-for-terrorists-make-pathankot-cops-sweat-224129"<br/>
      }<br/>
      <br/>
      Update Mode:<br/>
      This mode is to be used when you need to update Keywords/New Sources. After the update, next batch run of everyday scan will scrape and match the news articles per latest updated Keywords/news sources.<br/>
      {<br/>
      "api" : "46735622ca4d6fc49c6b811df1e9fc1",<br/>
      "keywords" : "terror financing,terror,drug trafficking,Hawala,money mule,money mule,lauder the money,money launder,money laundering",<br/>
      "mode":"update",<br/>
      "news_source_ids":"e5a8f17c-58c6-4087-a5c0-2ab681446611"<br/>
      }<br/>

      """

    _request = request.data
    _request = _request.decode("utf-8")
    _request = ast.literal_eval(_request)

    dbs = get_batch_ids()
    ids = current_ids_dbs()
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
    names['names'] = [x.lower() for x in names['names']]
    # print('fp_name:', fps['fp_name'])
    # print('fp_city:', fps['fp_city'])
    # print('cities:', cities['cities'])
    # print(ids)

    # print("last run time:", dbs[-1]["RunDate"])

    # print(_request)

    if _request["api"]:
      api = _request["api"]
    else:
      return jsonify({"status": "error",
        "code": "apiKeyInvalid",
        "message": "Your API key is invalid or incorrect. Check your key, or contact administrator."
        })

    if _request["mode"]:
      mode = _request["mode"]
    else:
      mode = "full"

    if api == '35622ca4d6fc49c6b811df1e9fc10de4':
      print(_request)
      if mode == 'full':
        # fetch all the data from db
        # print('mode:', mode)

        # fetch all the data from db
        search_results = []

        client = MongoClient('localhost', 27017)
        db = client['adverse_db']
        collection_batches = db['adverse_db']
        cursor = collection_batches.find({}, {'_id': False})
        # cursor = collection_batches.find({})

        for document in cursor:
          # print(document)
          # remove financial times
          if document['Source Name'] == "www.ft.com":
            continue

          document['Article_Date'] = document.pop('Article Date')
          document['City_of_News_Paper'] = document.pop('City of News Paper')
          document['City_State_mentioned_under_the_news'] = document.pop('City/ State mentioned under the news')
          document['HDFC_Bank_Name_under_News_Article'] = document.pop('HDFC Bank Name under News / Article')
          document['Key_word_Used_foruuidentify_the_article'] = document.pop('Key word Used for identify the article')
          document['Person_Name_mentioned_in_the_news'] = document.pop('Person Name mentioned in the news')
          document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].split(',')
          document['Person_Name_mentioned_in_the_news'] = [x.strip() for x in document['Person_Name_mentioned_in_the_news'] if x.strip()]
          document['Person_Name_mentioned_in_the_news'] = [i for i in document['Person_Name_mentioned_in_the_news'] if i not in fps['fp_name']]

          # print(document['Person_Name_mentioned_in_the_news'])
          # document['Person_Name_mentioned_in_the_news'] = list(set(document['Person_Name_mentioned_in_the_news']))
          document['Person_Name_mentioned_in_the_news'] = ', '.join(document['Person_Name_mentioned_in_the_news'])
          document['City_State_mentioned_under_the_news'] = document['City_State_mentioned_under_the_news'].split(',')
          document['City_State_mentioned_under_the_news'] = [x.strip() for x in document['City_State_mentioned_under_the_news'] if x.strip()]
          document['City_State_mentioned_under_the_news'] = [i for i in document['City_State_mentioned_under_the_news'] if i not in fps['fp_city']]

          # print(document['City_State_mentioned_under_the_news'])
          # document['City_State_mentioned_under_the_news'] = list(set(document['City_State_mentioned_under_the_news']))
          document['City_State_mentioned_under_the_news'] = ', '.join(document['City_State_mentioned_under_the_news'])

          document['Organization_Name_mentioned_in_the_news'] = document.pop('Organization Name mentioned in the news')
          document['Source_Name'] = document.pop('Source Name')
          document['Source_of_Info'] = document.pop('Source of Info')
          document['Web_link_of_news'] = document.pop('Web link of news')
          document['created_date'] = document['created_date'].split('.')[0]

          if document['Article_Date']:
            document['Article_Date'] = parse(document['Article_Date'].split('+')[0])
            document['Article_Date'] = document['Article_Date'].strftime("%Y-%m-%d %H:%M:%S")
          # try:
          #   if document['created_date']:
          #     print('created date exist')
          #     # document['created_date'] = ''
          # except Exception as e:
          #   document['created_date'] = ''


          # print(document)
          # document['Article_Date'] = document.pop('Article Date')
          # document['City_of_News_Paper'] = '' # document.pop('City of News Paper')
          # document['City_State_mentioned_under_the_news'] = document.pop('Organization Name mentioned in the news')
          # document['City_State_mentioned_under_the_news'] = document.pop('City/ State mentioned under the news')
          # document['HDFC_Bank_Name_under_News_Article'] = document.pop('HDFC Bank Name under News / Article')
          # document['Key_word_Used_foruuidentify_the_article'] = document.pop('Key word Used for identify the article')
          # document['Person_Name_mentioned_in_the_news'] = document.pop('Person Name mentioned in the news')
          # document['Organization_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'] + ', ' + document['City_State_mentioned_under_the_news']
          # document['Source_Name'] = document.pop('Source Name')
          # document['Source_of_Info'] = document.pop('Source of Info')
          # document['Web_link_of_news'] = document.pop('Web link of news')
          # document['Article_Date'] = document['Article_Date'].split('.')[0]
          # document['uuid'] = f1.uuid4()
          document['Source_of_Info'] = 'Newspaper' # document.pop('Source of Info')
          # remove Getty Images
          # document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].replace('Getty Images, ', '')
          # document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].replace('Getty Images', '')

          # remove Covid
          # document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].replace('Covid, ', '')
          # document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].replace('Covid', '')

          # remove Covid
          # document['City_State_mentioned_under_the_news'] = document['City_State_mentioned_under_the_news'].replace('Covid, ', '')
          # document['City_State_mentioned_under_the_news'] = document['City_State_mentioned_under_the_news'].replace('Covid', '')

          search_results.append(document)

        search_results = list({v['Web_link_of_news']:v for v in search_results}.values())

        return jsonify({"news_source_id": ids["news_source_ids"], 
            "last_updated_time": dbs[-1]["RunDate"],
            "keywords_searched" : ids['keywords'], 
            "date_of_response": None,
            "mode_of_search": mode,
            "search_results": search_results})

      elif mode == 'manual':
        _search_results = []
        if _request["date"]:
          date = _request["date"]
          date = datetime.strptime(_request["date"], "%Y-%m-%d %H:%M:%S")

          # find the batch run which date belongs to
          batch_ids = get_batch_ids()
          _batch_ids = []
          for batch in batch_ids:
            if datetime.strptime(batch['RunDate'], "%Y-%m-%d %H:%M:%S") > date:
              _batch_ids.append(str(batch['_id']))

          # fetch all the data from db
          search_results = []
          
          client = MongoClient('localhost', 27017)
          db = client['adverse_db']
          collection_batches = db['adverse_db']
          cursor = collection_batches.find({"batch_id": {"$in" : _batch_ids}}, {'_id': False})
          # cursor = collection_batches.find({})

          for document in cursor:
            if document['Source Name'] == "www.ft.com":
              continue

            # print(document)
            document['Article_Date'] = document.pop('Article Date')
            document['City_of_News_Paper'] = document.pop('City of News Paper')
            document['City_State_mentioned_under_the_news'] = document.pop('City/ State mentioned under the news')
            document['HDFC_Bank_Name_under_News_Article'] = document.pop('HDFC Bank Name under News / Article')
            document['Key_word_Used_foruuidentify_the_article'] = document.pop('Key word Used for identify the article')
            document['Person_Name_mentioned_in_the_news'] = document.pop('Person Name mentioned in the news')
            document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].split(',')
            document['Person_Name_mentioned_in_the_news'] = [x.strip() for x in document['Person_Name_mentioned_in_the_news'] if x.strip()]
            document['Person_Name_mentioned_in_the_news'] = [i for i in document['Person_Name_mentioned_in_the_news'] if i not in fps['fp_name']]

            # print(document['Person_Name_mentioned_in_the_news'])
            # document['Person_Name_mentioned_in_the_news'] = list(set(document['Person_Name_mentioned_in_the_news']))
            document['Person_Name_mentioned_in_the_news'] = ', '.join(document['Person_Name_mentioned_in_the_news'])
            document['City_State_mentioned_under_the_news'] = document['City_State_mentioned_under_the_news'].split(',')
            document['City_State_mentioned_under_the_news'] = [x.strip() for x in document['City_State_mentioned_under_the_news'] if x.strip()]
            document['City_State_mentioned_under_the_news'] = [i for i in document['City_State_mentioned_under_the_news'] if i not in fps['fp_city']]

            # print(document['City_State_mentioned_under_the_news'])
            # document['City_State_mentioned_under_the_news'] = list(set(document['City_State_mentioned_under_the_news']))
            document['City_State_mentioned_under_the_news'] = ', '.join(document['City_State_mentioned_under_the_news'])
            document['Organization_Name_mentioned_in_the_news'] = document.pop('Organization Name mentioned in the news')
            document['Source_Name'] = document.pop('Source Name')
            document['Source_of_Info'] = document.pop('Source of Info')
            document['Web_link_of_news'] = document.pop('Web link of news')
            document['created_date'] = document['created_date'].split('.')[0]

            if document['Article_Date']:
              document['Article_Date'] = parse(document['Article_Date'].split('+')[0])
              document['Article_Date'] = document['Article_Date'].strftime("%Y-%m-%d %H:%M:%S")

            # try:
            #   if document['created_date']:
            #     print('created date exist')
            #     # document['created_date'] = ''
            # except Exception as e:
            #   document['created_date'] = ''

              # document['City_of_News_Paper'] = '' # document.pop('City of News Paper')
              # document['City_State_mentioned_under_the_news'] = document.pop('Organization Name mentioned in the news')
              # document['City_State_mentioned_under_the_news'] = document.pop('City/ State mentioned under the news')
              # document['HDFC_Bank_Name_under_News_Article'] = document.pop('HDFC Bank Name under News / Article')
              # document['Key_word_Used_foruuidentify_the_article'] = document.pop('Key word Used for identify the article')
              # document['Person_Name_mentioned_in_the_news'] = document.pop('Person Name mentioned in the news')
              # document['Organization_Name_mentioned_in_the_news'] = document['Organization_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'] + ', ' + document['City_State_mentioned_under_the_news']
              # document['Source_Name'] = document.pop('Source Name')
              # document['Source_of_Info'] = document.pop('Source of Info')
              # document['Web_link_of_news'] = document.pop('Web link of news')
              # document['Article_Date'] = document['Article_Date'].split('.')[0]
              # document['uuid'] = f1.uuid4()

            document['Source_of_Info'] = 'Newspaper'
            # document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].replace('Getty Images, ', '')
            # document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].replace('Getty Images', '')

            # remove Covid
            # document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].replace('Covid, ', '')
            # document['Person_Name_mentioned_in_the_news'] = document['Person_Name_mentioned_in_the_news'].replace('Covid', '')

            # document['City_State_mentioned_under_the_news'] = document['City_State_mentioned_under_the_news'].replace('Covid, ', '')
            # document['City_State_mentioned_under_the_news'] = document['City_State_mentioned_under_the_news'].replace('Covid', '')

            search_results.append(document)

          # last_updated_time = datetime.strptime("2021-02-27 21:02:45", "%Y-%m-%d %H:%M:%S")
          # last_updated_time = last_updated_time.replace(tzinfo=timezone.utc)

          search_results = list({v['Web_link_of_news']:v for v in search_results}.values())

          return jsonify({"news_source_ids": ids["news_source_ids"],
            "last_updated_time": dbs[-1]["RunDate"],
            "keywords_searched" : ids['keywords'], 
            "date_of_response": _request["date"],
            "mode_of_search": _request["mode"],
            "search_results": search_results})

      elif mode == 'update':
        _keys = list(_request.keys())
        print(_request.keys())
        print(_request.values())

        if ('keywords' in _keys) and ('news_source_ids' in _keys) and ('fp_name' in _keys) and ('fp_city' in _keys) and ('cities' in _keys):
        # if _request['keywords'] and _request['news_source_ids'] and _request['fp_name'] and _request["fp_city"]:
          print('this is request for name, city, keywords, news_source_id and added_cities')
          _request['fp_name'] = _request['fp_name'].split(',') # + ['AGRA', 'Union', 'Budget', 'Centre', 'Getty Images', 'AFP/Getty']
          _request['fp_name'] = ','.join(list(set(_request['fp_name'])))
          _request['fp_city'] = _request['fp_city'].split(',') # + ['Covid']
          _request['fp_city'] = ','.join(list(set(_request['fp_city'])))
          _request['cities'] = _request['cities'].split(',') # + ['Covid']
          _request['cities'] = ','.join(list(set(_request['cities'])))
          # add news keywords and news source ids to database
          update_ids_dbs(keywords=_request['keywords'], news_source_ids=_request['news_source_ids'], fp_name=_request['fp_name'], fp_city=_request["fp_city"], cities=_request["cities"])
          # keywords = _request['keywords'].split(',')
          # news_source_id = _request['news_source_ids'].split(',')
          # print(_request)

          return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": dbs[-1]["RunDate"],
                    "keywords_updated" : _request['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Updated successfully']})

        elif ('keywords' in _keys) and ('news_source_ids' in _keys) and ('fp_name' in _keys) and ('fp_city' in _keys):
        # if _request['keywords'] and _request['news_source_ids'] and _request['fp_name'] and _request["fp_city"]:
          print('this is request for name, city, keywords and news_source_id')
          _request['fp_name'] = _request['fp_name'].split(',') # + ['AGRA', 'Union', 'Budget', 'Centre', 'Getty Images', 'AFP/Getty']
          _request['fp_name'] = ','.join(list(set(_request['fp_name'])))
          _request['fp_city'] = _request['fp_city'].split(',') # + ['Covid']
          _request['fp_city'] = ','.join(list(set(_request['fp_city'])))
          # _request['cities'] = _request['cities'].split(',') # + ['Covid']
          # _request['cities'] = ','.join(list(set(_request['cities'])))
          # add news keywords and news source ids to database
          update_ids_dbs(keywords=_request['keywords'], news_source_ids=_request['news_source_ids'], fp_name=_request['fp_name'], fp_city=_request["fp_city"])
          # keywords = _request['keywords'].split(',')
          # news_source_id = _request['news_source_ids'].split(',')
          # print(_request)

          return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": dbs[-1]["RunDate"],
                    "keywords_updated" : _request['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Updated successfully']})

        elif ('keywords' in _keys) and ('news_source_ids' in _keys) and ('cities' in _keys):
        # elif _request['keywords'] and _request['news_source_ids'] and _request['fp_name']:
          print("this request is for cities")
          _request['cities'] = _request['cities'].split(',') # + ['AGRA', 'Union', 'Budget', 'Centre', 'Getty Images', 'AFP/Getty']
          _request['cities'] = ','.join(list(set(_request['cities'])))
          # _request['fp_city'] = ['Covid']
          # _request['fp_city'] = ','.join(list(set(_request['fp_city'])))
          # add news keywords and news source ids to database
          update_ids_dbs(keywords=_request['keywords'], news_source_ids=_request['news_source_ids'], cities=_request['cities']) # , _request["fp_city"])
          # keywords = _request['keywords'].split(',')
          # news_source_id = _request['news_source_ids'].split(',')

          return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": dbs[-1]["RunDate"],
                    "keywords_updated" : _request['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Updated successfully']})

        elif ('keywords' in _keys) and ('news_source_ids' in _keys) and ('names' in _keys):
        # elif _request['keywords'] and _request['news_source_ids'] and _request['fp_name']:
          print("this request is for names")
          _request['names'] = _request['names'].split(',') # + ['AGRA', 'Union', 'Budget', 'Centre', 'Getty Images', 'AFP/Getty']
          _request['names'] = ','.join(list(set(_request['names'])))
          # _request['fp_city'] = ['Covid']
          # _request['fp_city'] = ','.join(list(set(_request['fp_city'])))
          # add news keywords and news source ids to database
          update_ids_dbs(keywords=_request['keywords'], news_source_ids=_request['news_source_ids'], names=_request['names']) # , _request["fp_city"])
          # keywords = _request['keywords'].split(',')
          # news_source_id = _request['news_source_ids'].split(',')

          return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": dbs[-1]["RunDate"],
                    "keywords_updated" : _request['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Updated successfully']})

        elif ('keywords' in _keys) and ('news_source_ids' in _keys) and ('fp_name' in _keys):
        # elif _request['keywords'] and _request['news_source_ids'] and _request['fp_name']:
          print("this request is for keywords, news_source_id and name")
          _request['fp_name'] = _request['fp_name'].split(',') # + ['AGRA', 'Union', 'Budget', 'Centre', 'Getty Images', 'AFP/Getty']
          _request['fp_name'] = ','.join(list(set(_request['fp_name'])))
          # _request['fp_city'] = ['Covid']
          # _request['fp_city'] = ','.join(list(set(_request['fp_city'])))
          # add news keywords and news source ids to database
          update_ids_dbs(keywords=_request['keywords'], news_source_ids=_request['news_source_ids'], fp_name=_request['fp_name']) # , _request["fp_city"])
          # keywords = _request['keywords'].split(',')
          # news_source_id = _request['news_source_ids'].split(',')

          return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": dbs[-1]["RunDate"],
                    "keywords_updated" : _request['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Updated successfully']})

        elif ('keywords' in _keys) and ('news_source_ids' in _keys) and ('fp_city' in _keys):
        # elif _request['keywords'] and _request['news_source_ids'] and _request['fp_city']:
          print("this request is for keywords, news_source_id and fp_city")
          # _request['fp_name'] = ['AGRA', 'Union', 'Budget', 'Centre', 'Getty Images', 'AFP/Getty']
          # _request['fp_name'] = ','.join(list(set(_request['fp_name'])))
          _request['fp_city'] = _request['fp_city'].split(',') # + ['Covid']
          _request['fp_city'] = ','.join(list(set(_request['fp_city'])))
          # add news keywords and news source ids to database
          update_ids_dbs(keywords=_request['keywords'], news_source_ids=_request['news_source_ids'], fp_city=_request["fp_city"])
          # keywords = _request['keywords'].split(',')
          # news_source_id = _request['news_source_ids'].split(',')

          return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": dbs[-1]["RunDate"],
                    "keywords_updated" : _request['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Updated successfully']})

        elif ('keywords' in _keys) and ('news_source_ids' in _keys):
        # elif _request['keywords'] and _request['news_source_ids']:
          print("this is request is for keywords and news_source_ids")
          # _request['fp_name'] = ['AGRA', 'Union', 'Budget', 'Centre', 'Getty Images', 'AFP/Getty']
          # _request['fp_name'] = ','.join(list(set(_request['fp_name'])))
          # _request['fp_city'] = ['Covid']
          # _request['fp_city'] = ','.join(list(set(_request['fp_city'])))
          # add news keywords and news source ids to database
          update_ids_dbs(keywords=_request['keywords'], news_source_ids=_request['news_source_ids']) # , _request['fp_name'], _request["fp_city"])
          # keywords = _request['keywords'].split(',')
          # news_source_id = _request['news_source_ids'].split(',')

          return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": dbs[-1]["RunDate"],
                    "keywords_updated" : _request['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Updated successfully']})


      elif mode == 'parse_existing':
        # _keys = list(_request.keys())

        # if 'uuid' in _keys:
          # if _request['uuid'] == 'all':
            # update the database to parse existing = True
            # update_parse_existing(str(ids['_id']))
            # get all the existing urls and updating them
            # return jsonify({"news_source_ids": ids["news_source_ids"], 
                    # "last_updated_time": dbs[-1]["RunDate"],
                    # "keywords_updated" : ids['keywords'], 
                    # "date_of_response": None,
                    # "mode_of_search": mode,
                    # "search_results": ['Updating all the urls in the database']})
        # else:
          # _request['uuid'] = _request['uuid'].split(',')



        # # if _request['keywords'] and _request['news_source_ids'] and _request['fp_name'] and _request["fp_city"]:
          # print('this is request for name, city, keywords, news_source_id and added_cities')
        #   _request['fp_name'] = _request['fp_name'].split(',') # + ['AGRA', 'Union', 'Budget', 'Centre', 'Getty Images', 'AFP/Getty']
        #   _request['fp_name'] = ','.join(list(set(_request['fp_name'])))
        #   _request['fp_city'] = _request['fp_city'].split(',') # + ['Covid']
        #   _request['fp_city'] = ','.join(list(set(_request['fp_city'])))
        #   _request['cities'] = _request['cities'].split(',') # + ['Covid']
        #   _request['cities'] = ','.join(list(set(_request['cities'])))
        #   # add news keywords and news source ids to database
        #   update_ids_dbs(keywords=_request['keywords'], news_source_ids=_request['news_source_ids'], fp_name=_request['fp_name'], fp_city=_request["fp_city"], cities=_request["cities"])
        #   # keywords = _request['keywords'].split(',')
        #   # news_source_id = _request['news_source_ids'].split(',')
        #   # print(_request)

        # # update the database to parse existing = True
        update_parse_existing(str(ids['_id']))
        # get all the existing urls and updating them
        return jsonify({"news_source_ids": ids["news_source_ids"], 
                    "last_updated_time": dbs[-1]["RunDate"],
                    "keywords_updated" : ids['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Updating all the urls in the database']})


      elif mode == 'realtime':        
        if _request['keywords'] and _request['urltobesearched']:
          # print(_request['keywords'], _request['urltobesearched'])
          keywords = _request['keywords'].split(',')
          keywords = [x.strip() for x in keywords if x.strip()]
          urltobesearched = _request['urltobesearched']
          if keywords and urltobesearched:
            profile = {'Person_Name_mentioned_in_the_news': '', 'Organization_Name_mentioned_in_the_news': '', 'City_State_mentioned_under_the_news': '', 'Key_word_Used_foruuidentify_the_article': '', 'HDFC_Bank_Name_under_News_Article': 'No', 'Article_Date': '', 'Source_Name': '', 'Web_link_of_news': '', 'created_date': '', 'City_of_News_Paper': ''}
            # USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
            HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
            config = Config()
            # config.browser_user_agent = USER_AGENT
            config.headers = HEADERS
            config.request_timeout = 40

            try:
              profile['Source_Name'] = urltobesearched.split('/')[2]
              article = Article(urltobesearched, config=config)
              article.download()
              article.parse()

              soup = BeautifulSoup(article.html, 'html.parser')

              text = soup_text(soup, profile['Source_Name'])

              if not text:
                text = article.title + os.linesep + article.text
                # print(text)

              # if 'economictimes.indiatimes' in profile['Source_Name']:
              #   soup = BeautifulSoup(article.html, 'html.parser')

              #   regex = re.compile('.*artText.*')
              #   text = [tag.get_text() for tag in soup.find_all("div", {"class" : regex})]
              #   if text:
              #     text = [article.title] + text
              #     text = '\n'.join(text)
              #   else:
              #     regex = re.compile('.*content1.*')
              #     text = [tag.get_text() for tag in soup.find_all("div", {"class" : regex})]
              #     if text:
              #       text = [article.title] + text
              #       text = '\n'.join(text)
              #     else:
              #       text = [tag.get_text() for tag in soup.find_all("p", attrs={"itemprop": "caption description"})]
              #       if text:
              #         text = [article.title] + text
              #         text = '\n'.join(text)
              #       else:
              #         text = article.title + os.linesep + article.text
              
              # elif 'timesofindia.indiatimes' in profile['Source_Name']:
              #   soup = BeautifulSoup(article.html, 'html.parser')

              #   regex = re.compile('.*Normal.*')

              #   text = [tag.get_text() for tag in soup.find_all("div", {"class" : regex})]
              #   if text:
              #     text = [article.title] + text
              #     text = '\n'.join(text)
              #   else:
              #     text = article.title + os.linesep + article.text
              
              # elif 'business-standard' in profile['Source_Name']:
              #   soup = BeautifulSoup(article.html, 'html.parser')

              #   text = [tag.get_text() for tag in soup.find_all('span', {'class': 'p-content'})]
              #   if text:
              #     text = [article.title] + text
              #     text = '\n'.join(text)
              #   else:
              #     text = article.title + os.linesep + article.text

              # else:
              #   text = article.title + os.linesep + article.text
                # text = article.title.lower() + os.linesep + article.text.lower()

              # print(text)

              for keyword in keywords:
                if keyword.lower() in text.lower():
                  if keyword not in profile['Key_word_Used_foruuidentify_the_article']:
                    profile['Key_word_Used_foruuidentify_the_article'] += keyword + ', '
                  else:
                    continue

              if not profile['Key_word_Used_foruuidentify_the_article']:
                return jsonify({"news_source_ids": ids["news_source_ids"], 
                  "last_updated_time": dbs[-1]["RunDate"],
                  "keywords_updated" : ids['keywords'], 
                  "date_of_response": None,
                  "mode_of_search": mode,
                  "search_results": []})



              if 'hdfc' in text.lower():
                profile['HDFC_Bank_Name_under_News_Article'] = 'YES'

              profile['Web_link_of_news'] = article.url

              print(text)

              # remove Getty Images
              # text = text.replace('Getty Images', '')

              # remove Covid
              # text = text.replace('Covid', '')

              text2 = text.split('\n')

              print('length of article:', len(text2))

              for i in range(len(text2)):

                doc = nlp_Name(text2[i])

                # iterate through each entity present
                for ent in doc.ents:
                  # save data in profile
                  # find persons in text
                  if ent.label_ == 'PERSON':
                    profile['Person_Name_mentioned_in_the_news'] += ent.text + ', '

                  # find persons in text
                  elif ent.label_ == 'ORG':
                    profile['Organization_Name_mentioned_in_the_news'] += ent.text + ', '

                  # find persons in text
                  elif ent.label_ == 'GPE':
                    profile['City_State_mentioned_under_the_news'] += ent.text + ', '

                  # find persons in text
                  elif ent.label_ == 'LOC':
                    profile['City_State_mentioned_under_the_news'] += ent.text + ', '

                  else:
                    continue

                # _loc = text2[i].split(':')
                # _loc = [y for x in _loc for y in x.split(' ')]
                # _loc = [x.strip() for x in _loc]
                # _loc = [x for x in _loc if x.lower() in cities['cities']]
                # print('location:detected:', _loc)
                # for __loc in _loc:
                  # profile['City_State_mentioned_under_the_news'] += __loc + ', '


                # for __loc in _loc:
                  # __loc = __loc.split(' ')
                  # __loc = [x for x in __loc if x in cities['cities']]
                  # print('location found:', __loc)
                  # profile['City_State_mentioned_under_the_news'] += __loc[-1] + ', '


              profile['Article_Date'] = article.publish_date
              profile['City_of_News_Paper'] = ''
              # profile['batch_id'] = batch_id
              profile['created_date'] = datetime.now()
              profile['created_date'] = profile['created_date'].strftime("%Y-%m-%d %H:%M:%S")
              profile['Organization_Name_mentioned_in_the_news'] = profile['Organization_Name_mentioned_in_the_news'].split(',')
              # print(profile['Organization_Name_mentioned_in_the_news'])
              profile['Organization_Name_mentioned_in_the_news'] = [x.strip() for x in profile['Organization_Name_mentioned_in_the_news'] if x.strip()]
              profile['Organization_Name_mentioned_in_the_news'] = list(set(profile['Organization_Name_mentioned_in_the_news']))
              # profile['Organization_Name_mentioned_in_the_news'] = ', '.join(profile['Organization_Name_mentioned_in_the_news'])    
              profile['Person_Name_mentioned_in_the_news'] = profile['Person_Name_mentioned_in_the_news'].split(',') + profile['Organization_Name_mentioned_in_the_news']
              # print(profile['Person Name mentioned in the news'])
              profile['Person_Name_mentioned_in_the_news'] = [x.strip() for x in profile['Person_Name_mentioned_in_the_news'] if x.strip()]
              profile['Person_Name_mentioned_in_the_news'] = list(set(profile['Person_Name_mentioned_in_the_news']))
              profile['Person_Name_mentioned_in_the_news'] = [ i for i in profile['Person_Name_mentioned_in_the_news'] if not any( [ i in a for a in profile['Person_Name_mentioned_in_the_news'] if a != i]   )]
              person_dict = {k.lower():k for k in profile['Person_Name_mentioned_in_the_news']}
              profile['Person_Name_mentioned_in_the_news'] = list(person_dict.values())
              profile['Person_Name_mentioned_in_the_news'] = [i for i in profile['Person_Name_mentioned_in_the_news'] if i not in fps['fp_name']]
              profile['Person_Name_mentioned_in_the_news'] = [i for i in profile['Person_Name_mentioned_in_the_news'] if "covid" not in i.lower()]
              # profile['Person_Name_mentioned_in_the_news'] = [i.split("’")[0] for i in profile['Person_Name_mentioned_in_the_news']]

              for name in profile['Person_Name_mentioned_in_the_news']:
                if name.lower() in cities['cities']:
                  profile['Person_Name_mentioned_in_the_news'].remove(name)
                  profile['City_State_mentioned_under_the_news'] += name + ', '

              profile['Person_Name_mentioned_in_the_news'] = ', '.join(profile['Person_Name_mentioned_in_the_news'])    
              profile['Organization_Name_mentioned_in_the_news'] = ', '.join(profile['Organization_Name_mentioned_in_the_news'])    
              profile['City_State_mentioned_under_the_news'] = profile['City_State_mentioned_under_the_news'].split(',')
              # print(profile['City_State_mentioned_under_the_news'])
              profile['City_State_mentioned_under_the_news'] = [x.strip() for x in profile['City_State_mentioned_under_the_news'] if x.strip()]
              profile['City_State_mentioned_under_the_news'] = list(set(profile['City_State_mentioned_under_the_news']))
              profile['City_State_mentioned_under_the_news'] = [ i for i in profile['City_State_mentioned_under_the_news'] if not any( [ i in a for a in profile['City_State_mentioned_under_the_news'] if a != i]   )]
              city_dict = {k.lower():k for k in profile['City_State_mentioned_under_the_news']}
              profile['City_State_mentioned_under_the_news'] = list(city_dict.values())
              profile['City_State_mentioned_under_the_news'] = [i for i in profile['City_State_mentioned_under_the_news'] if i not in fps['fp_city']]
              profile['City_State_mentioned_under_the_news'] = [i for i in profile['City_State_mentioned_under_the_news'] if "covid" not in i.lower()]
              # profile['City_State_mentioned_under_the_news'] = [i.split("’")[0] for i in profile['City_State_mentioned_under_the_news']]

              for name in profile['City_State_mentioned_under_the_news']:
                if name.lower() in names['names']:
                  profile['City_State_mentioned_under_the_news'].remove(name)
                  profile['Person_Name_mentioned_in_the_news'] += ', ' + name

              profile['City_State_mentioned_under_the_news'] = ', '.join(profile['City_State_mentioned_under_the_news'])
              profile['Source_of_Info'] = 'Newspaper'
              profile['Key_word_Used_foruuidentify_the_article'] = fnc_(profile['Key_word_Used_foruuidentify_the_article'])
              profile['uuid'] = f1.uuid4()
              profile.pop('Organization_Name_mentioned_in_the_news')

              if not profile['Article_Date']:
                profile['Article_Date'] = ''

              print(profile)

              return jsonify({"news_source_ids": ids["news_source_ids"], 
                "last_updated_time": dbs[-1]["RunDate"],
                "keywords_updated" : ids['keywords'], 
                "date_of_response": None,
                "mode_of_search": mode,
                "search_results": [profile]})

            except Exception as e:
                print(e)
                return jsonify({"news_source_ids": ids["news_source_ids"], 
                  "last_updated_time": dbs[-1]["RunDate"],
                  "keywords_updated" : ids['keywords'], 
                  "date_of_response": None,
                  "mode_of_search": mode,
                  "search_results": ["Please check urltobesearched"]})



          else:
            return jsonify({"news_source_ids": ids["news_source_ids"], 
              "last_updated_time": dbs[-1]["RunDate"],
              "keywords_updated" : ids['keywords'], 
              "date_of_response": None,
              "mode_of_search": mode,
              "search_results": ['Please correct keywords and urltobesearched']})

        else:
            return jsonify({"news_source_ids": ids["news_source_ids"], 
              "last_updated_time": dbs[-1]["RunDate"],
              "keywords_updated" : ids['keywords'], 
              "date_of_response": None,
              "mode_of_search": mode,
              "search_results": ['Please correct keywords and urltobesearched']})


          # add news keywords and news source ids to database
          # update_ids_dbs(_request['keywords'], _request['news_source_ids'])
          # keywords = _request['keywords'].split(',')
          # news_source_id = _request['news_source_ids'].split(',')

            # return 'request update' # jsonify({"news_source_ids": _request['news_source_ids'], 
                    # "last_updated_time": dbs[-1]["RunDate"],
                    # "keywords_updated" : _request['keywords'], 
                    # "date_of_response": None,
                    # "mode_of_search": mode,
                    # "search_results": ['Updated successfully']})

    #   elif mode == 'update':        
    #     if _request['keywords'] and _request['news_source_ids']:
    #       keywords = _request['keywords'].split(',')
    #       news_source_id = _request['news_source_ids'].split(',')






    # if _request["keywords"]:
    #   keywords = _request["keywords"]
    #   keywords = keywords.split(',')
    #   print('keywords is:', keywords)
    # else:
    #   keywords = ["default"]

    # if _request["mode"]:
    #   mode = _request["mode"]
    # else:
    #   mode = "full"

    # if _request["news_source_id"]:
    #   news_source_id = _request["news_source_id"]
    #   news_source_id = news_source_id.split(',')
    # else:
    #   news_source_id = []

    # if api != '35622ca4d6fc49c6b811df1e9fc10de4':
    #   return jsonify({"status": "error",
    #     "code": "apiKeyInvalid",
    #     "message": "Your API key is invalid or incorrect. Check your key, or contact administrator."
    #     })

    # if 'default' in keywords:
    #   if mode == 'full':

    #     # fetch all the data from db
    #     search_results = []

    #     client = MongoClient('localhost', 27017)
    #     db = client['adverse_db']
    #     collection_batches = db['adverse_db']
    #     cursor = collection_batches.find({}, {'uuid': False})
    #     # cursor = collection_batches.find({})

    #     for document in cursor:
    #       document['Article_Date'] = document.pop('Article Date')
    #       document['City_of_News_Paper'] = document.pop('City of News Paper')
    #       document['City_State_mentioned_under_the_news'] = document.pop('City/ State mentioned under the news')
    #       document['HDFC_Bank_Name_under_News_Article'] = document.pop('HDFC Bank Name under News / Article')
    #       document['Key_word_Used_foruuidentify_the_article'] = document.pop('Key word Used for identify the article')
    #       document['Organization_Name_mentioned_in_the_news'] = document.pop('Organization Name mentioned in the news')
    #       document['Person_Name_mentioned_in_the_news'] = document.pop('Person Name mentioned in the news')
    #       document['Source_Name'] = document.pop('Source Name')
    #       document['Source_of_Info'] = document.pop('Source of Info')
    #       document['Web_link_of_news'] = document.pop('Web link of news')
    #       document['uuid'] = f1.uuid4()

    #       search_results.append(document)

    #     # results = {'results': search_results}

    #     return jsonify({"news_source_id": None, 
    #       "keywords_searched" : _request["keywords"], 
    #       "date_of_response": None,
    #       "mode_of_search": _request["mode"],
    #       "search_results": search_results})

    #   elif mode == 'incremental':

    #     # fetch all the data from db
    #     search_results = []

    #     client = MongoClient('localhost', 27017)
    #     db = client['adverse_db']
    #     collection_batches = db['adverse_db']
    #     cursor = collection_batches.find({}, {'uuid': False})
    #     # cursor = collection_batches.find({})

    #     for document in cursor:
    #       date = datetime.strptime(document['Article Date'], "%Y-%m-%d %H:%M:%S")
    #       past = datetime.now() - timedelta(days=1)

    #       if date > past:
    #         document['Article_Date'] = document.pop('Article Date')
    #         document['City_of_News_Paper'] = document.pop('City of News Paper')
    #         document['City_State_mentioned_under_the_news'] = document.pop('City/ State mentioned under the news')
    #         document['HDFC_Bank_Name_under_News_Article'] = document.pop('HDFC Bank Name under News / Article')
    #         document['Key_word_Used_foruuidentify_the_article'] = document.pop('Key word Used for identify the article')
    #         document['Organization_Name_mentioned_in_the_news'] = document.pop('Organization Name mentioned in the news')
    #         document['Person_Name_mentioned_in_the_news'] = document.pop('Person Name mentioned in the news')
    #         document['Source_Name'] = document.pop('Source Name')
    #         document['Source_of_Info'] = document.pop('Source of Info')
    #         document['Web_link_of_news'] = document.pop('Web link of news')
    #         document['uuid'] = f1.uuid4()

    #         search_results.append(document)
    #       else:
    #         print('skipping news past 1 days')

    #     return jsonify({"news_source_id": None, 
    #       "keywords_searched" : _request["keywords"], 
    #       "date_of_response": None,
    #       "mode_of_search": _request["mode"],
    #       "search_results": search_results})

    #   elif mode == 'manual':

    #     # fetch all the data from specified db
    #     search_results = []

    #     if _request["date"]:

    #       date = _request["date"]
    #       date = date.split(',')

    #       client = MongoClient('localhost', 27017)
    #       db = client['adverse_db']
    #       collection_batches = db['adverse_db']
    #       cursor = collection_batches.find({}, {'uuid': False})
    #       # cursor = collection_batches.find({})

    #       for document in cursor:
    #         _date = datetime.strptime(document['Article Date'], "%Y-%m-%d %H:%M:%S")
    #         max_date = datetime.strptime(date[0], "%Y-%m-%d")
    #         min_date = datetime.strptime(date[1], "%Y-%m-%d")
    #         print('date:', _date, 'max_date:', max_date, 'min_date:', min_date)

    #         if (_date <= max_date) and (_date >= min_date):
    #           document['Article_Date'] = document.pop('Article Date')
    #           document['City_of_News_Paper'] = document.pop('City of News Paper')
    #           document['City_State_mentioned_under_the_news'] = document.pop('City/ State mentioned under the news')
    #           document['HDFC_Bank_Name_under_News_Article'] = document.pop('HDFC Bank Name under News / Article')
    #           document['Key_word_Used_foruuidentify_the_article'] = document.pop('Key word Used for identify the article')
    #           document['Organization_Name_mentioned_in_the_news'] = document.pop('Organization Name mentioned in the news')
    #           document['Person_Name_mentioned_in_the_news'] = document.pop('Person Name mentioned in the news')
    #           document['Source_Name'] = document.pop('Source Name')
    #           document['Source_of_Info'] = document.pop('Source of Info')
    #           document['Web_link_of_news'] = document.pop('Web link of news')
    #           document['uuid'] = f1.uuid4()

    #           search_results.append(document)
            
    #         else:
    #           print('skipping news past 1 days')

    #       return jsonify({"news_source_id": None, 
    #         "keywords_searched" : _request["keywords"], 
    #         "date_of_response": _request["date"],
    #         "mode_of_search": _request["mode"],
    #         "search_results": search_results})

    #     else:
    #       return jsonify({"news_source_id": None, 
    #         "keywords_searched" : _request["keywords"], 
    #         "date_of_response": _request["date"],
    #         "mode_of_search": _request["mode"],
    #         "search_results": search_results})

    # else:
    #   if mode == 'full':

    #     # fetch all the data relative to keywords
    #     search_results = search(_request["keywords"])
    #     _search_results = []

    #     for response in search_results:
    #       response['uuid'] = f1.uuid4()
    #       if news_source_id:
    #         if response['Source Name'] in news_source_id:
    #           print('it has found source name')
    #           _search_results.append(response)
    #           return jsonify({"news_source_id": news_source_id, 
    #             "keywords_searched" : _request["keywords"], 
    #             "date_of_response": None,
    #             "mode_of_search": _request["mode"],
    #             "search_results": _search_results})
    #         else:
    #           print('sourceid not present in request body')

    #       else:
    #         _search_results.append(response)

    #         return jsonify({"news_source_id": None, 
    #           "keywords_searched" : _request["keywords"], 
    #           "date_of_response": None,
    #           "mode_of_search": _request["mode"],
    #           "search_results": _search_results})


    #   elif mode == 'incremental':

    #     # fetch all the data relative to keywords
    #     search_results = search(_request["keywords"])
    #     _search_results = []

    #     for response in search_results:
    #       response['uuid'] = f1.uuid4()
    #       date = datetime.strptime(response['Article Date'], "%Y-%m-%d %H:%M:%S")
    #       past = datetime.now() - timedelta(days=1)
    #       if date > past:
    #         if news_source_id:
    #           if response['Source Name'] in news_source_id:
    #             _search_results.append(response)
    #             return jsonify({"news_source_id": news_source_id, 
    #               "keywords_searched" : _request["keywords"], 
    #               "date_of_response": None,
    #               "mode_of_search": _request["mode"],
    #               "search_results": _search_results})
    #           else:
    #             print('sourceid not present in request body')
    #         else:
    #           _search_results.append(response)

    #           return jsonify({"news_source_id": None, 
    #             "keywords_searched" : _request["keywords"], 
    #             "date_of_response": None,
    #             "mode_of_search": _request["mode"],
    #             "search_results": _search_results})

    #   elif mode == 'manual':
    #     # fetch all the data relative to keywords
    #     search_results = search(_request["keywords"])
    #     _search_results = []

    #     if _request["date"]:
    #       date = _request["date"]
    #       date = date.split(',')

    #       for response in search_results:
    #         _date = datetime.strptime(response['Article Date'], "%Y-%m-%d %H:%M:%S")
    #         max_date = datetime.strptime(date[0], "%Y-%m-%d")
    #         min_date = datetime.strptime(date[1], "%Y-%m-%d")
    #         print('date:', _date, 'max_date:', max_date, 'min_date:', min_date)

    #         if (_date <= max_date) and (_date >= min_date):
    #           response['uuid'] = f1.uuid4()
    #           if news_source_id:
    #             if response['Source Name'] in news_source_id:
    #               _search_results.append(response)
    #               return jsonify({"news_source_id": news_source_id, 
    #                 "keywords_searched" : _request["keywords"], 
    #                 "date_of_response": None,
    #                 "mode_of_search": _request["mode"],
    #                 "search_results": _search_results})
    #             else:
    #               print('sourceid not present in request body')
    #           else:
    #             _search_results.append(response)
    #         else:
    #           print('skipping news not in date range')

    #       return jsonify({"news_source_id": None, 
    #         "keywords_searched" : _request["keywords"], 
    #         "date_of_response": None,
    #         "mode_of_search": _request["mode"],
    #         "search_results": _search_results})

    #     else:
    #       return jsonify({"news_source_id": None, 
    #         "keywords_searched" : _request["keywords"], 
    #         "date_of_response": _request["date"],
    #         "mode_of_search": _request["mode"],
    #         "search_results": _search_results})


@app.route('/Adversecheck', methods=['GET', 'POST'])
def Adversecheck():
    responses = []

    client = MongoClient('localhost', 27017)
    db = client['adversedb']
    collection_batches = db['adversedb']
    # cursor = collection_batches.find({}, {'uuid': False})
    cursor = collection_batches.find({}, {'uuid': False})

    for document in cursor:
      responses.append(document)

    # return jsonify(responses) # "Wiki Refresh Api test slave databases"


    # message = ""
    # if request.method == 'POST' or request.method == 'GET':

        # pep_name = request.form['pep_name']
        # pep_name = ''.join([char if ord(char) < 128 else '' for char in pep_name])

        # responses = search(pep_name)
        # pep_response = []
        # print(responses)

        # if not responses:
        #     pass
        # else:
        #   for response in responses:
        #     if check_designation(response) and response['spouse']:
        #       pep_response.extend([response])
        #       if ast.literal_eval(response['spouse']):
        #         spouses = ast.literal_eval(response['spouse'])
        #         for spouse in spouses:
        #           pep_response.extend(search_spouse(spouse))
        #     elif check_designation(response):
        #       pep_response.extend([response])
        #     elif response['spouse']:
        #       if ast.literal_eval(response['spouse']):
        #         spouses = ast.literal_eval(response['spouse'])
        #         for spouse in spouses:
        #           responses_ = search_spouse(spouse)
        #           spouse_check = [response_ for response_ in responses_ if check_designation(response_)]
        #           pep_response.extend(spouse_check)
        #           if any(spouse_check):
        #             pep_response.extend([response])
                    # pep_response.extend(search_spouse2(response['full_name']))
                    # pep_response.extend(responses_)
                  # for response_ in responses_:
                    # if check_designation(response_):
                      # pep_response.extend([response])
                      # pep_response.extend(search_spouse2(spouse))
                      # pep_response.extend([response_])

                      # pep_response.extend(search_pep(response_['full_name']))
                      # pep_response.extend(search_pep(spouse))
                    # else:
                      # pass
            # else:
            #   pass

        # print(pep_response)



        
        # if not responses:
        #     pass
        #     # responses = responses1
        # else:
        #     spouses = [ast.literal_eval(x['spouse']) for x in responses if x['spouse']]
        #     if not spouses:
        #         pass
        #         # responses = responses
        #     else:
        #         spouses = [item for sublist in spouses for item in sublist]
        #         # print(spouses)
        #         spouses = list(set(spouses))
        #         for spouse in spouses:
        #             if pep_name != spouse:
        #                 responses.extend(search_spouse(spouse))
        #                 # responses2 = search(spouse)
        #                 # responses = [*responses1, *responses2]
        #             else:
        #                 pass
        #                 # responses = responses1

        # designations = [x['designation'] for x in responses if x['designation']]

        # designations = list(set(designations))

        # find_designation = []

        # filters = ['politician', 'businessman', 'officer', 'director', 'governor', 'officer', 'manager', 'adviser', 'chairman', 'md', 'ceo', 'fgm', 'cgm', 'board', 'pgm', 'secretary', 'cvo', 'minister', 'cs', 'president', 'cmo']

        # for designation in designations:
        #     for filter_ in filters:
        #         if filter_ in designation.lower():
        #             find_designation.append(filter_)
        #         else:
        #             pass

        # if not find_designation:
        #     responses = []

        # pep_responses = filter_responses(responses)



       #  # check if found persons are officers or not :-
       #  filters = ['politician', 'businessman', 'officer', 'director', 'governor', 'officer', 'manager', 'adviser', 'chairman', 'md', 'ceo', 'fgm', 'cgm', 'board', 'pgm', 'secretary', 'cvo', 'minister', 'cs', 'president', 'cmo']

       # if not responses:
       #      pass
       #  else:
       #      for reponse in responses:
       #          for filter_ in filters:
       #              if filter_ in reponse['designation'].lower():
       #                  pep_response.append(response)
       #              else:
       #                  if response['spouse']:
       #                      if ast.literal_eval(response['spouse']):
       #                          spouse = ast.literal_eval(response['spouse'])
       #                          spouse_ = search(spouse)






         
 


       #  if not responses:
       #      pass
       #  else:
       #      designations = [x['designation'] for x in responses if x['designation']]
       #      designations = list(set(designations))

       #      find_designation = []

       #      filters = ['politician', 'businessman', 'officer', 'director', 'governor', 'officer', 'manager', 'adviser', 'chairman', 'md', 'ceo', 'fgm', 'cgm', 'board', 'pgm', 'secretary', 'cvo', 'minister', 'cs', 'president', 'cmo']

       #      for designation in designations:
       #          for filter_ in filters:
       #              if filter_ in designation.lower():
       #                  find_designation.append(filter_)
       #              else:
       #                  pass

       #      if not find_designation:
       #          # check if found persons have relative officers or not :-
       #          # search for spouse
       #          spouses = [ast.literal_eval(x['spouse']) for x in responses if x['spouse']]
       #          if not spouses:
       #              pass
       #          else:
       #              spouses = [item for sublist in spouses for item in sublist]
       #              # print(spouses)
       #              spouses = list(set(spouses))
       #              for spouse in spouses:
       #                  if pep_name not in spouse:
       #                      # print(pep_name)
       #                      # print(spouse)
       #                      responses.extend(search(spouse))
       #                  else:
       #                      pass


       #      responses = []



       #  # name of all the members in the family
       #  fam_list = []
       #  pep_response = []

       #  # filter relatives name:
       #  if not responses:
       #      pass
       #  else:
       #      for i, response in enumerate(responses):
       #          if ast.literal_eval(response['aliases']):
       #              aliases = ast.literal_eval(response['aliases'])
       #              if aliases:
       #                  fam_list.extend(aliases)
       #                  # familiy_list += [aliase for aliase in aliases if aliases]
       #          if response['children']:
       #              if ast.literal_eval(response['children']):
       #                  children = ast.literal_eval(response['children'])
       #                  if children:
       #                      fam_list.extend(children)
       #          if response['relatives']:
       #              if ast.literal_eval(response['relatives']):
       #                  relatives = ast.literal_eval(response['relatives'])
       #                  if relatives:
       #                      fam_list.extend(relatives)                        
       #          if response['siblings']:
       #              if ast.literal_eval(response['siblings']):
       #                  siblings = ast.literal_eval(response['siblings'])
       #                  if siblings:
       #                      fam_list.extend(siblings)                        
       #          if response['spouse']:
       #              if ast.literal_eval(response['spouse']):
       #                  spouse = ast.literal_eval(response['spouse'])
       #                  if spouse:
       #                      fam_list.extend(spouse)                        

       #          # familiy_list += [aliase for aliase in aliases if aliases]
       #          # familiy_list.extend([aliase for aliase in aliases if aliases])
       #          fam_list += [response['birth_name']] if response['birth_name'] is not None else []
       #          # familiy_list += [response['birth_name'] if response['birth_name']
       #          # familiy_list.extend([response['birth_name'] if response['birth_name']])
       #          # familiy_list += [child for child in children if children]
       #          # familiy_list.extend([child for child in children if children])
       #          fam_list += [response['father']] if response['father'] is not None else []
       #          # familiy_list += [response['father'] if response['father']
       #          # familiy_list.extend([response['father'] if response['father']])
       #          fam_list += [response['first_name']] if response['first_name'] is not None else []
       #          # familiy_list += [response['first_name'] if response['first_name']
       #          # familiy_list.extend([response['first_name'] if response['first_name']])
       #          fam_list += [response['full_name']] if response['full_name'] is not None else []
       #          # familiy_list += [response['full_name'] if response['full_name']
       #          # familiy_list.extend([response['full_name'] if response['full_name']])
       #          fam_list += [response['last_name']] if response['last_name'] is not None else []
       #          # familiy_list += [response['last_name'] if response['last_name']
       #          # familiy_list.extend([response['last_name'] if response['last_name']])
       #          fam_list += [response['mother']] if response['mother'] is not None else []
       #          # familiy_list += [response['mother'] if response['mother']
       #          # familiy_list.extend([response['mother'] if response['mother']])
       #          fam_list += [response['native_name']] if response['native_name'] is not None else []
       #          # familiy_list += [response['native_name'] if response['native_name']
       #          # familiy_list.extend([response['native_name'] if response['native_name']])
       #          fam_list += [response['relatives']] if response['relatives'] is not None else []
       #          # familiy_list += [response['relatives'] if response['relatives']
       #          # familiy_list.extend([response['relatives'] if response['relatives']])
       #          # familiy_list += [sibling for sibling in siblings if siblings]
       #          # familiy_list.extend([sibling for sibling in siblings if siblings])
       #          # familiy_list += [sps for sps in spouse if spouse]
       #          # familiy_list.extend([sps for sps in spouse if spouse])

       #          if pep_name in fam_list:
       #              print(i)
       #              pep_response.append(response)

        # search for spouse
        # if not pep_response:
        #     pass
        # else:
        #     spouses = [ast.literal_eval(x['spouse']) for x in pep_response if x['spouse']]
        #     if not spouses:
        #         pass
        #     else:
        #         spouses = [item for sublist in spouses for item in sublist]
        #         # print(spouses)
        #         spouses = list(set(spouses))
        #         for spouse in spouses:
        #             if pep_name not in spouse:
        #                 print(pep_name)
        #                 print(spouse)
        #                 pep_response.extend(search(spouse))
        #             else:
        #                 pass

        # pep_responses = list({v['full_name']:v for v in pep_response}.values())

        # pep_names = [response['full_name'] for response in pep_response]
        # pep_names = list(set(pep_names))

        # for response in pep_response:
        #   if response['full_name'] not in pep_names:
        #     pep_responses.append(response)
        #   # if response['full_name'] not in pep_names:
          #   pep_responses.append(response)



        # pep_response = [dict(y) for y in set(tuple(x.items()) for x in pep_response)]
        # pep_response = [response for response in pep_response if pep_response['full_name'] in pep_names]

        # pep_response = [qcode2val(response) for response in pep_response]
        # if pep_response:
          # for response in pep_response:
            # response['summary'] = response['full_name'] + ' is a ' + response['designation']
          # pep_response = [response['summary']: ]
    results = {'results': responses}

    results = dumps(results, sort_keys=False, indent=4, ensure_ascii=False)
    message = 'Searched PEP information'
    return render_template('check.html', response=results, msg=message)        

@app.route('/Adversecheck2', methods=['GET', 'POST'])
def Adversecheck2():
    responses = []

    client = MongoClient('localhost', 27017)
    db = client['adversedb']
    collection_batches = db['adversedb']
    # cursor = collection_batches.find({}, {'uuid': False})
    cursor = collection_batches.find({})

    for document in cursor:

      document['City_of_News_Paper'] = document.pop('City of News Paper')
      document['City_State_mentioned_under_the_news'] = document.pop('City/ State mentioned under the news')
      document['HDFC_Bank_Name_under_News_Article'] = document.pop('HDFC Bank Name under News / Article')
      document['Key_word_Used_foruuidentify_the_article'] = document.pop('Key word Used for identify the article')
      document['Organization_Name_mentioned_in_the_news'] = document.pop('Organization Name mentioned in the news')
      document['Person_Name_mentioned_in_the_news'] = document.pop('Person Name mentioned in the news')
      document['Source_Name'] = document.pop('Source Name')
      document['Source_of_Info'] = document.pop('Source of Info')
      document['Web_link_of_news'] = document.pop('Web link of news')

      document['uuid'] = str(document['uuid'])

      responses.append(document)

    results = {'results': responses}

    return jsonify(results)

    # results = dumps(results, sort_keys=False, indent=4, ensure_ascii=False)
    # message = 'Searched PEP information'
    # return render_template('check.html', response=results, msg=message)        

@app.route('/check_name/<name>')
def check_name(name):

    name = ''.join([char if ord(char) < 128 else '' for char in name])

    responses = search(name)
    # pep_response = []

    # if not responses:
      # pass
    # else:
      # for response in responses:
        # if check_designation(response) and response['spouse']:
        #   pep_response.extend([response])
        #   if ast.literal_eval(response['spouse']):
        #     spouses = ast.literal_eval(response['spouse'])
        #     for spouse in spouses:
        #       pep_response.extend(search_spouse(spouse))
        # elif check_designation(response):
        #   pep_response.extend([response])
        # elif response['spouse']:
        #   if ast.literal_eval(response['spouse']):
        #     spouses = ast.literal_eval(response['spouse'])
        #     for spouse in spouses:
        #       responses_ = search_spouse(spouse)
        #       spouse_check = [response_ for response_ in responses_ if check_designation(response_)]
        #       pep_response.extend(spouse_check)
        #       if any(spouse_check):
        #         pep_response.extend([response])
        # else:
        #   pass

    # responses = search(name)
    results = {'results':responses}
    return results # jsonify(response) # response


@app.route('/check2', methods=['GET', 'POST'])
def check2():
   if request.method == 'POST':
      user = request.form['pep_name']
      return redirect(url_for('check_name',name = user))
   else:
      user = request.args.get('pep_name')
      return redirect(url_for('check_name',name = user))

@app.route('/Adversecheck3', methods=['GET', 'POST'])
def Adversecheck3():
    responses = [{
            "uuid": "603681a19b19655dab57cff8",
            "Person Name mentioned in the news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
            "Organization Name mentioned in the news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
            "City/ State mentioned under the news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
            "Key word Used for identify the article": "money laundering",
            "Web link of news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
            "HDFC Bank Name under News / Article": "No",
            "Article Date": '2021-02-25',
            "Source of Info": "News Paper",
            "Source Name": "Economic Times",
            "City of News Paper": None
        },
        {
            "uuid": "f1.uuid4()",
            "Person Name mentioned in the news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
            "Organization Name mentioned in the news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
            "City/ State mentioned under the news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
            "Key word Used for identify the article": "money laundering",
            "Web link of news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
            "HDFC Bank Name under News / Article": "No",
            "Article Date": '2021-02-25',
            "Source of Info": "News Paper",
            "Source Name": "Economic Times",
            "City of News Paper": None
        },
        {
            "uuid": "f1.uuid4()",
            "Person Name mentioned in the news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
            "Organization Name mentioned in the news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
            "City/ State mentioned under the news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
            "Key word Used for identify the article": "money laundering",
            "Web link of news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
            "HDFC Bank Name under News / Article": "No",
            "Article Date": '2021-02-25',
            "Source of Info": "News Paper",
            "Source Name": "Economic Times",
            "City of News Paper": None
        }]

    results = {'results': responses}

    results = dumps(results, sort_keys=False, indent=4, ensure_ascii=False)
    message = 'Searched PEP information'
    return render_template('check.html', response=results, msg=message)        

# @app.route('/adverseapi', methods=['GET', 'POST'])
# def adverseapi():

    # a = request.data
    # b = a.decode("utf-8")
    # c = ast.literal_eval(b)
    # print(c)
    # print(c["api"])

    # api = request.args.get('api')
    # mode = request.args.get('mode')
    # keywords = request.args.get('keywords')
    # sourceid = request.args.get('sourceid')
    # date = request.args.get('date')

    # try:
    #   keywords = keywords.split(',')
    # except Exception as e:
    #   print(e)
    #   pass

    # if api != '35622ca4d6fc49c6b811df1e9fc10de4':
    #   return jsonify({"status": "error",
    #     "code": "apiKeyInvalid",
    #     "message": "Your API key is invalid or incorrect. Check your key, or contact administrator."
    #     })

    # if api == '35622ca4d6fc49c6b811df1e9fc10de4':
    #   if mode == 'full':
    #     if 'default' in keywords:
    #       responses = [
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
    #       "uuid": "603681a19b19655dab57cff8"
    #       },
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
    #       "uuid": "f1.uuid4()"
    #       },
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
    #       "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
    #       "uuid": "f1.uuid4()"
    #       }
    #       ]

    #       return jsonify({'results': responses})

    #     elif 'money laundering' in keywords or 'money launder' in keywords:
    #       responses = [
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money launder",
    #       "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
    #       "uuid": "603681a19b19655dab57cff8"
    #       },
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
    #       "uuid": "f1.uuid4()"
    #       },
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
    #       "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
    #       "uuid": "f1.uuid4()"
    #       }
    #       ]

    #       return jsonify({'results': responses})

    #   elif mode == 'incremental':
    #     if 'default' in keywords:
    #       responses = [
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
    #       "uuid": "603681a19b19655dab57cff8"
    #       },
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
    #       "uuid": "f1.uuid4()"
    #       }
    #       ]

    #       return jsonify({'results': responses})

    #     elif 'money laundering' in keywords or 'money launder' in keywords:
    #       responses = [
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
    #       "uuid": "603681a19b19655dab57cff8"
    #       },
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
    #       "uuid": "f1.uuid4()"
    #       }
    #       ]

    #       return jsonify({'results': responses})


    #   elif mode == 'realtime':
    #     if 'default' in keywords:
    #       responses = [
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
    #       "uuid": "603681a19b19655dab57cff8"
    #       },
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
    #       "uuid": "f1.uuid4()"
    #       }
    #       ]
    #       return jsonify({'results': responses})

    #     elif 'money laundering' in keywords or 'money launder' in keywords:
    #       responses = [
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
    #       "uuid": "603681a19b19655dab57cff8"
    #       },
    #       {
    #       "Article Date": '2021-02-25',
    #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
    #       "City_of_News_Paper": None,
    #       "HDFC_Bank_Name_under_News_Article": "No",
    #       "Key_word_Used_foruuidentify_the_article": "money laundering",
    #       "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #       "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #       "Source_Name": "Economic Times",
    #       "Source_of_Info": "News Paper",
    #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
    #       "uuid": "f1.uuid4()"
    #       }
    #       ]
    #       return jsonify({'results': responses})

    #   elif mode == 'manual':
    #     if date == '20210226':
    #       if 'default' in keywords:
    #         responses = [
    #         {
    #         "Article Date": '20210226',
    #         "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #         "City_of_News_Paper": None,
    #         "HDFC_Bank_Name_under_News_Article": "No",
    #         "Key_word_Used_foruuidentify_the_article": "money laundering",
    #         "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #         "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #         "Source_Name": "Economic Times",
    #         "Source_of_Info": "News Paper",
    #         "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
    #         "uuid": "603681a19b19655dab57cff8"
    #         }
    #         ]
    #         return jsonify({'results': responses})

    #       elif 'money laundering' in keywords or 'money launder' in keywords:
    #         responses = [
    #         {
    #         "Article Date": '20210226',
    #         "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #         "City_of_News_Paper": None,
    #         "HDFC_Bank_Name_under_News_Article": "No",
    #         "Key_word_Used_foruuidentify_the_article": "money laundering",
    #         "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #         "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #         "Source_Name": "Economic Times",
    #         "Source_of_Info": "News Paper",
    #         "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
    #         "uuid": "603681a19b19655dab57cff8"
    #         },
    #         {
    #         "Article Date": '20210226',
    #         "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
    #         "City_of_News_Paper": None,
    #         "HDFC_Bank_Name_under_News_Article": "No",
    #         "Key_word_Used_foruuidentify_the_article": "money laundering",
    #         "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #         "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #         "Source_Name": "Economic Times",
    #         "Source_of_Info": "News Paper",
    #         "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
    #         "uuid": "f1.uuid4()"
    #         }
    #         ]
    #         return jsonify({'results': responses})

    # else:
    #   return jsonify({"status": "error",
    #     "code": "apiKeyInvalid",
    #     "message": "Your API key is invalid or incorrect. Check your key, or contact administrator."
    #     })


    # if api == '35622ca4d6fc49c6b811df1e9fc10de4' and mode == 'full', and keywords=='default' and :
    #   responses = [
    #   {
    #   "Article Date": '2021-02-25',
    #   "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #   "City_of_News_Paper": None,
    #   "HDFC_Bank_Name_under_News_Article": "No",
    #   "Key_word_Used_foruuidentify_the_article": "money laundering",
    #   "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #   "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #   "Source_Name": "Economic Times",
    #   "Source_of_Info": "News Paper",
    #   "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
    #   "uuid": "603681a19b19655dab57cff8"
    #   },
    #   {
    #   "Article Date": '2021-02-25',
    #   "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
    #   "City_of_News_Paper": None,
    #   "HDFC_Bank_Name_under_News_Article": "No",
    #   "Key_word_Used_foruuidentify_the_article": "money laundering",
    #   "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
    #   "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #   "Source_Name": "Economic Times",
    #   "Source_of_Info": "News Paper",
    #   "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
    #   "uuid": "f1.uuid4()"
    #   },
    #   {
    #   "Article Date": '2021-02-25',
    #   "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
    #   "City_of_News_Paper": None,
    #   "HDFC_Bank_Name_under_News_Article": "No",
    #   "Key_word_Used_foruuidentify_the_article": "money laundering",
    #   "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
    #   "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
    #   "Source_Name": "Economic Times",
    #   "Source_of_Info": "News Paper",
    #   "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
    #   "uuid": "f1.uuid4()"
    #   }
    #   ]
    #   results = {'results': responses}
    #   return jsonify(results)

@app.route('/adverseapi2', methods=['GET', 'POST'])
def adverseapi2():

    f1 = Faker()

    _request = request.data
    _request = _request.decode("utf-8")
    _request = ast.literal_eval(_request)

    print(_request)

    if _request["api"]:
      api = _request["api"]
    else:
      return jsonify({"status": "error",
        "code": "apiKeyInvalid",
        "message": "Your API key is invalid or incorrect. Check your key, or contact administrator."
        })

    if api != '35622ca4d6fc49c6b811df1e9fc10de4':
      return jsonify({"status": "error",
        "code": "apiKeyInvalid",
        "message": "Your API key is invalid or incorrect. Check your key, or contact administrator."
        })

    if _request["mode"]:
      # if _request['keywords']
      mode = _request["mode"]
    else:
      mode = "full"


    if api == '35622ca4d6fc49c6b811df1e9fc10de4':
      if mode == 'full':
              search_results = [
              {
              "Article Date": '2021-02-25 00:00:00',
              "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
              "City_of_News_Paper": None,
              "HDFC_Bank_Name_under_News_Article": "No",
              "Key_word_Used_foruuidentify_the_article": "money laundering",
              "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
              "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
              "Source_Name": "Economic Times",
              "Source_of_Info": "News Paper",
              "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
              "uuid": 'a299a2b8-5500-4dfd-ad05-a6ca5cf8e562'
              },
              {
              "Article Date": '2021-02-25 00:00:00',
              "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
              "City_of_News_Paper": None,
              "HDFC_Bank_Name_under_News_Article": "No",
              "Key_word_Used_foruuidentify_the_article": "money laundering",
              "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
              "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
              "Source_Name": "Economic Times",
              "Source_of_Info": "News Paper",
              "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
              "uuid": '4a668431-b0a6-4d32-a393-8a4b033ddb76'
              },
              {
              "Article Date": '2021-02-25 00:00:00',
              "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
              "City_of_News_Paper": None,
              "HDFC_Bank_Name_under_News_Article": "No",
              "Key_word_Used_foruuidentify_the_article": "money laundering",
              "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
              "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
              "Source_Name": "Economic Times",
              "Source_of_Info": "News Paper",
              "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
              "uuid": 'a6569a15-1b25-4f58-8e8f-4f7813ae60cf'
              }
              ]
              return jsonify({"news_source_id": None, 
                "last_updated_time": "2021-02-25 00:00:00",
                "keywords_searched" : None, 
                "date_of_response": None,
                "mode_of_search": mode,
                "search_results": search_results})

      elif mode == 'manual':
        _search_results = []
        if _request["date"]:
          date = _request["date"]
          date = datetime.strptime(_request["date"], "%Y-%m-%d %H:%M:%S")
          search_results = [
                  {
                  "Article Date": '2021-02-27 21:02:45',
                  "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
                  "City_of_News_Paper": None,
                  "HDFC_Bank_Name_under_News_Article": "No",
                  "Key_word_Used_foruuidentify_the_article": "money laundering",
                  "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
                  "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
                  "Source_Name": "Economic Times",
                  "Source_of_Info": "News Paper",
                  "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
                  "uuid": f1.uuid4()
                  },
                  {
                  "Article Date": '2021-02-27 21:02:45',
                  "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
                  "City_of_News_Paper": None,
                  "HDFC_Bank_Name_under_News_Article": "No",
                  "Key_word_Used_foruuidentify_the_article": "money laundering",
                  "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
                  "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
                  "Source_Name": "Economic Times",
                  "Source_of_Info": "News Paper",
                  "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
                  "uuid": f1.uuid4()
                  },
                  {
                  "Article Date": '2021-02-27 21:02:45',
                  "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
                  "City_of_News_Paper": None,
                  "HDFC_Bank_Name_under_News_Article": "No",
                  "Key_word_Used_foruuidentify_the_article": "money laundering",
                  "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
                  "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
                  "Source_Name": "Economic Times",
                  "Source_of_Info": "News Paper",
                  "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
                  "uuid": f1.uuid4()
                  }
                  ]
          for result in search_results:
              if datetime.strptime(result['Article Date'], "%Y-%m-%d %H:%M:%S") > date:
                _search_results.append(result)

          last_updated_time = datetime.strptime("2021-02-27 21:02:45", "%Y-%m-%d %H:%M:%S")
          last_updated_time = last_updated_time.replace(tzinfo=timezone.utc)

          return jsonify({"news_source_ids": None, 
                    "last_updated_time": last_updated_time,
                    "keywords_searched" : None, 
                    "date_of_response": _request["date"],
                    "mode_of_search": mode,
                    "search_results": _search_results})

      elif mode == 'update':
        # if _request['news_source_ids']:
        #     news_source_ids = _request['news_source_ids'].split(',')
        #     for source_id in news_source_ids:
        #       if source_id not in ['c1f4a45b-aa9c-4627-980b-f69509e5c862', 'a70e9599-4480-46d2-889f-652fdd58cc55', '3d4a70cb-fe3f-459e-8cb1-43bc04f759c6', '5966436a-2f26-4305-95a3-fcda913d621d', 
        #       'ad60ab7b-906b-467d-b29e-92f200eb88fe',
        #       '52d0de86-1525-417d-b8fd-2158f1256c38',
        #       '557e51e6-b04c-4be1-a4fa-aff4b7e1c37b',
        #       '4dfab6d8-8246-469b-9e19-7ddbb55d806d',
        #       'eeff09cb-6fdb-45f1-a206-32a55320d598',
        #       'e43b544e-577b-4ed0-adb0-4661bda4c487',
        #       'ca3c6507-8c4a-4269-a384-8de06f43bc4f',
        #       '73f6c89a-fe6b-4c20-ba77-fdf4740874b0',
        #       '5b32994e-2e6e-417f-ba44-77f508742349',
        #       '8cbc9eec-7255-43bf-bb72-2bce4f4764ea',
        #       '91272662-bb73-4649-a8c2-026d112c190e',
        #       'c55c0b9c-614e-4f1b-ba2c-d5e34e37800b',
        #       'ec2217c5-0320-491c-a351-78ff97d47885',
        #       'd33446c7-a37b-4c5b-ba7a-275cc9583c05',
        #       '65cb3dec-94a9-4274-b518-543c74e14a59',
        #       '6c676cc1-2338-4834-a0fb-9ae8a04a2bda',
        #       '890d11b8-05e7-416e-b777-7ba62f4a7045',
        #       '7eba470b-1edc-4f69-840d-99cfde3a5fcb',
        #       'a9ecac2e-a7da-4bbd-b326-103de3149ece',
        #       'bef37780-c007-4b96-89f4-5198b69f2c93',
        #       '2cdd8f28-01f5-4d18-b438-742f04fe3140',
        #       'e5a8f17c-58c6-4087-a5c0-2ab681446611',]:
        #           return jsonify({"news_source_ids": _request['news_source_ids'], 
        #             "last_updated_time": None,
        #             "keywords_searched" : None, 
        #             "date_of_response": None,
        #             "mode_of_search": mode,
        #             "search_results": ['Please provide news_source_id only from 28 newspaper']})
        
        if _request['keywords'] and _request['news_source_ids']:
          keywords = _request['keywords'].split(',')
          news_source_id = _request['news_source_ids'].split(',')

          return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": None,
                    "keywords_updated" : _request['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Updated successfully']})

        elif _request['news_source_ids']:
            news_source_ids = _request['news_source_ids'].split(',')
            for source_id in news_source_ids:
              if source_id not in ['c1f4a45b-aa9c-4627-980b-f69509e5c862', 'a70e9599-4480-46d2-889f-652fdd58cc55', '3d4a70cb-fe3f-459e-8cb1-43bc04f759c6', '5966436a-2f26-4305-95a3-fcda913d621d', 
              'ad60ab7b-906b-467d-b29e-92f200eb88fe',
              '52d0de86-1525-417d-b8fd-2158f1256c38',
              '557e51e6-b04c-4be1-a4fa-aff4b7e1c37b',
              '4dfab6d8-8246-469b-9e19-7ddbb55d806d',
              'eeff09cb-6fdb-45f1-a206-32a55320d598',
              'e43b544e-577b-4ed0-adb0-4661bda4c487',
              'ca3c6507-8c4a-4269-a384-8de06f43bc4f',
              '73f6c89a-fe6b-4c20-ba77-fdf4740874b0',
              '5b32994e-2e6e-417f-ba44-77f508742349',
              '8cbc9eec-7255-43bf-bb72-2bce4f4764ea',
              '91272662-bb73-4649-a8c2-026d112c190e',
              'c55c0b9c-614e-4f1b-ba2c-d5e34e37800b',
              'ec2217c5-0320-491c-a351-78ff97d47885',
              'd33446c7-a37b-4c5b-ba7a-275cc9583c05',
              '65cb3dec-94a9-4274-b518-543c74e14a59',
              '6c676cc1-2338-4834-a0fb-9ae8a04a2bda',
              '890d11b8-05e7-416e-b777-7ba62f4a7045',
              '7eba470b-1edc-4f69-840d-99cfde3a5fcb',
              'a9ecac2e-a7da-4bbd-b326-103de3149ece',
              'bef37780-c007-4b96-89f4-5198b69f2c93',
              '2cdd8f28-01f5-4d18-b438-742f04fe3140',
              'e5a8f17c-58c6-4087-a5c0-2ab681446611',]:
                  return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": None,
                    "keywords_searched" : None, 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Please provide news_source_id only from 28 newspaper']})


        elif not _request['news_source_ids']:
            return jsonify({"news_source_ids": None, 
                    "last_updated_time": None,
                    "keywords_searched" : None, 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Please provide atleast one news_source_ids']})
        else:
            return jsonify({"news_source_ids": None, 
                    "last_updated_time": None,
                    "keywords_searched" : None, 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": ['Please provide atleast one keyword']})

      elif mode == 'realtime':
        _search_results = []

        if _request['keywords'] and _request['news_source_ids']:
          keywords = _request['keywords'].split(',')
          news_source_id = _request['news_source_ids'].split(',')
          search_results = [
                  {
                  "Article Date": '2021-02-27 23:12:45',
                  "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
                  "City_of_News_Paper": None,
                  "HDFC_Bank_Name_under_News_Article": "No",
                  "Key_word_Used_foruuidentify_the_article": keywords[0],
                  "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
                  "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
                  "Source_Name": "Economic Times",
                  "Source_of_Info": "News Paper",
                  "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
                  "uuid": f1.uuid4()
                  },
                  {
                  "Article Date": '2021-02-27 22:42:45',
                  "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
                  "City_of_News_Paper": None,
                  "HDFC_Bank_Name_under_News_Article": "No",
                  "Key_word_Used_foruuidentify_the_article": keywords[0],
                  "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
                  "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
                  "Source_Name": "Economic Times",
                  "Source_of_Info": "News Paper",
                  "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
                  "uuid": f1.uuid4()
                  },
                  {
                  "Article Date": '2021-02-27 23:22:45',
                  "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
                  "City_of_News_Paper": None,
                  "HDFC_Bank_Name_under_News_Article": "No",
                  "Key_word_Used_foruuidentify_the_article": keywords[0],
                  "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
                  "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
                  "Source_Name": "Economic Times",
                  "Source_of_Info": "News Paper",
                  "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
                  "uuid": f1.uuid4()
                  }
                  ]

          return jsonify({"news_source_ids": _request['news_source_ids'], 
                    "last_updated_time": None,
                    "keywords_updated" : _request['keywords'], 
                    "date_of_response": None,
                    "mode_of_search": mode,
                    "search_results": search_results})


        # if _request["date"]:
        #   date = _request["date"]
        #   date = datetime.strptime(_request["date"], "%Y-%m-%d %H:%M:%S")
        #   search_results = [
        #           {
        #           "Article Date": '2021-02-27 21:02:45',
        #           "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
        #           "City_of_News_Paper": None,
        #           "HDFC_Bank_Name_under_News_Article": "No",
        #           "Key_word_Used_foruuidentify_the_article": "money laundering",
        #           "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
        #           "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
        #           "Source_Name": "Economic Times",
        #           "Source_of_Info": "News Paper",
        #           "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
        #           "uuid": f1.uuid4()
        #           },
        #           {
        #           "Article Date": '2021-02-27 21:02:45',
        #           "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
        #           "City_of_News_Paper": None,
        #           "HDFC_Bank_Name_under_News_Article": "No",
        #           "Key_word_Used_foruuidentify_the_article": "money laundering",
        #           "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
        #           "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
        #           "Source_Name": "Economic Times",
        #           "Source_of_Info": "News Paper",
        #           "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
        #           "uuid": f1.uuid4()
        #           },
        #           {
        #           "Article Date": '2021-02-27 21:02:45',
        #           "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
        #           "City_of_News_Paper": None,
        #           "HDFC_Bank_Name_under_News_Article": "No",
        #           "Key_word_Used_foruuidentify_the_article": "money laundering",
        #           "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
        #           "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
        #           "Source_Name": "Economic Times",
        #           "Source_of_Info": "News Paper",
        #           "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
        #           "uuid": f1.uuid4()
        #           }
        #           ]
        #   for result in search_results:
        #       if datetime.strptime(result['Article Date'], "%Y-%m-%d %H:%M:%S") > date:
        #         _search_results.append(result)

        #   last_updated_time = datetime.strptime("2021-02-27 21:02:45", "%Y-%m-%d %H:%M:%S")
        #   last_updated_time = last_updated_time.replace(tzinfo=timezone.utc)

        #   return jsonify({"news_source_ids": None, 

        # _search_results = []
        # if _request["date"]:
        #   date = _request["date"]
        #   date = datetime.strptime(_request["date"], "%Y-%m-%d %H:%M:%S")
        #   search_results = [
        #           {
        #           "Article Date": '2021-02-25 21:02:45',
        #           "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
        #           "City_of_News_Paper": None,
        #           "HDFC_Bank_Name_under_News_Article": "No",
        #           "Key_word_Used_foruuidentify_the_article": "money laundering",
        #           "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
        #           "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
        #           "Source_Name": "Economic Times",
        #           "Source_of_Info": "News Paper",
        #           "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
        #           "uuid": f1.uuid4()
        #           },
        #           {
        #           "Article Date": '2021-02-25 21:02:45',
        #           "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
        #           "City_of_News_Paper": None,
        #           "HDFC_Bank_Name_under_News_Article": "No",
        #           "Key_word_Used_foruuidentify_the_article": "money laundering",
        #           "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
        #           "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
        #           "Source_Name": "Economic Times",
        #           "Source_of_Info": "News Paper",
        #           "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
        #           "uuid": f1.uuid4()
        #           },
        #           {
        #           "Article Date": '2021-02-27 21:02:45',
        #           "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
        #           "City_of_News_Paper": None,
        #           "HDFC_Bank_Name_under_News_Article": "No",
        #           "Key_word_Used_foruuidentify_the_article": "money laundering",
        #           "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
        #           "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
        #           "Source_Name": "Economic Times",
        #           "Source_of_Info": "News Paper",
        #           "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
        #           "uuid": f1.uuid4()
        #           }
        #           ]
        #   for result in search_results:
        #       if datetime.strptime(result['Article Date'], "%Y-%m-%d %H:%M:%S") > date:
        #         _search_results.append(result)

        #   last_updated_time = datetime.strptime("2021-02-27 21:02:45", "%Y-%m-%d %H:%M:%S")
        #   last_updated_time = last_updated_time.replace(tzinfo=timezone.utc)

        #   return jsonify({"news_source_id": None, 
        #             "last_updated_time": last_updated_time,
        #             "keywords_searched" : None, 
        #             "date_of_response": _request["date"],
        #             "mode_of_search": mode,
        #             "search_results": _search_results})
          # past = datetime.now() - timedelta(days=1)

          # date = date.split(',')

          # if date == '2021-02-27' or date == '2021-02-26' or date == '2021-02-25': # and date[1] == '2021-02-25':
            # if 'default' in keywords:
            #   if _request["news_source_id"]:
            #     news_source_id = _request["news_source_id"]
            #     news_source_id = news_source_id.split(',')

            #     if 'ad60ab7b-906b-467d-b29e-92f200eb88fe' in news_source_id or 'ca3c6507-8c4a-4269-a384-8de06f43bc4f' in news_source_id:
                  # search_results = [
                  # {
                  # "Article Date": '2021-02-25',
                  # "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
                  # "City_of_News_Paper": None,
                  # "HDFC_Bank_Name_under_News_Article": "No",
                  # "Key_word_Used_foruuidentify_the_article": "money laundering",
                  # "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
                  # "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
                  # "Source_Name": "Economic Times",
                  # "Source_of_Info": "News Paper",
                  # "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
                  # "uuid": f1.uuid4()
                  # },
                  # {
                  # "Article Date": '2021-02-26',
                  # "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
                  # "City_of_News_Paper": None,
                  # "HDFC_Bank_Name_under_News_Article": "No",
                  # "Key_word_Used_foruuidentify_the_article": "money laundering",
                  # "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
                  # "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
                  # "Source_Name": "Economic Times",
                  # "Source_of_Info": "News Paper",
                  # "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
                  # "uuid": f1.uuid4()
                  # },
                  # {
                  # "Article Date": '2021-02-27',
                  # "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
                  # "City_of_News_Paper": None,
                  # "HDFC_Bank_Name_under_News_Article": "No",
                  # "Key_word_Used_foruuidentify_the_article": "money laundering",
                  # "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
                  # "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
                  # "Source_Name": "Economic Times",
                  # "Source_of_Info": "News Paper",
                  # "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
                  # "uuid": f1.uuid4()
                  # }
                  # ]
                  # return jsonify({"news_source_id": None, 
                  #   "last_updated_time": "2021-02-27",
                  #   "keywords_searched" : None, 
                  #   "date_of_response": _request["date"],
                  #   "mode_of_search": mode,
                  #   "search_results": search_results})

            # elif 'money laundering' in keywords or 'money launder' in keywords:
            #   if _request["news_source_id"]:
            #     news_source_id = _request["news_source_id"]
            #     news_source_id = news_source_id.split(',')

            #     # if 'ad60ab7b-906b-467d-b29e-92f200eb88fe' in news_source_id or 'ca3c6507-8c4a-4269-a384-8de06f43bc4f' in news_source_id:
            #       search_results = [
            #       {
            #       "Article Date": '2021-02-25',
            #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
            #       "City_of_News_Paper": None,
            #       "HDFC_Bank_Name_under_News_Article": "No",
            #       "Key_word_Used_foruuidentify_the_article": "money laundering",
            #       "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
            #       "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
            #       "Source_Name": "Economic Times",
            #       "Source_of_Info": "News Paper",
            #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
            #       "uuid": f1.uuid4()
            #       },
            #       {
            #       "Article Date": '2021-02-26',
            #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
            #       "City_of_News_Paper": None,
            #       "HDFC_Bank_Name_under_News_Article": "No",
            #       "Key_word_Used_foruuidentify_the_article": "money laundering",
            #       "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
            #       "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
            #       "Source_Name": "Economic Times",
            #       "Source_of_Info": "News Paper",
            #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
            #       "uuid": f1.uuid4()
            #       },
            #       {
            #       "Article Date": '2021-02-27',
            #       "last_updated_time": "2021-02-27",
            #       "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
            #       "City_of_News_Paper": None,
            #       "HDFC_Bank_Name_under_News_Article": "No",
            #       "Key_word_Used_foruuidentify_the_article": "money laundering",
            #       "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
            #       "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
            #       "Source_Name": "Economic Times",
            #       "Source_of_Info": "News Paper",
            #       "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
            #       "uuid": f1.uuid4()
            #       }
            #       ]
            #       return jsonify({"news_source_id": news_source_id, 
            #         "last_updated_time": "2021-02-27",
            #         "keywords_searched" : keywords, 
            #         "date_of_response": _request["date"],
            #         "mode_of_search": mode,
            #         "search_results": search_results})


    # if _request["mode"]:
      # if _request['keywords']
      # mode = _request["mode"]
    # else:
    #   mode = "full"

    # if _request["keywords"]:
    #   keywords = _request["keywords"]
    #   keywords = keywords.split(',')
    #   print('keywords is:', keywords)
    #   for keyword in keywords:
    #     if 'money laundering' not in keywords:
    #       if 'money launder' not in keywords:
    #         search_results = []
    #         return jsonify({"news_source_id": None, 
    #           "last_updated_time": "2021-02-27",
    #           "keywords_searched" : _request["keywords"], 
    #           "date_of_response": None,
    #           "mode_of_search": _request["mode"],
    #           "search_results": search_results})
    # else:
    #   keywords = ["default"]


    # if _request["news_source_id"]:
    #   news_source_id = _request["news_source_id"]

    # if _request["date"]:
    #   date = _request["date"]



    # a = request.data
    # b = a.decode("utf-8")
    # c = ast.literal_eval(b)
    # print(c)
    # print(c["api"])

    # api = request.args.get('api')
    # mode = request.args.get('mode')
    # keywords = request.args.get('keywords')
    # sourceid = request.args.get('sourceid')
    # date = request.args.get('date')

    # try:
    #   keywords = keywords.split(',')
    # except Exception as e:
    #   print(e)
    #   pass

    if api != '35622ca4d6fc49c6b811df1e9fc10de4':
      return jsonify({"status": "error",
        "code": "apiKeyInvalid",
        "message": "Your API key is invalid or incorrect. Check your key, or contact administrator."
        })

    # if api == '35622ca4d6fc49c6b811df1e9fc10de4':
      # if mode == 'full':
      #   keywords = None
      #         search_results = [
      #         {
      #         "Article Date": '2021-02-25',
      #         "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
      #         "City_of_News_Paper": None,
      #         "HDFC_Bank_Name_under_News_Article": "No",
      #         "Key_word_Used_foruuidentify_the_article": "money laundering",
      #         "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
      #         "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
      #         "Source_Name": "Economic Times",
      #         "Source_of_Info": "News Paper",
      #         "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
      #         "uuid": f1.uuid4()
      #         },
      #         {
      #         "Article Date": '2021-02-25',
      #         "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
      #         "City_of_News_Paper": None,
      #         "HDFC_Bank_Name_under_News_Article": "No",
      #         "Key_word_Used_foruuidentify_the_article": "money laundering",
      #         "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
      #         "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
      #         "Source_Name": "Economic Times",
      #         "Source_of_Info": "News Paper",
      #         "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
      #         "uuid": f1.uuid4()
      #         },
      #         {
      #         "Article Date": '2021-02-25',
      #         "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
      #         "City_of_News_Paper": None,
      #         "HDFC_Bank_Name_under_News_Article": "No",
      #         "Key_word_Used_foruuidentify_the_article": "money laundering",
      #         "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
      #         "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
      #         "Source_Name": "Economic Times",
      #         "Source_of_Info": "News Paper",
      #         "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
      #         "uuid": f1.uuid4()
      #         }
      #         ]
      #         return jsonify({"news_source_id": None, 
      #           "last_updated_time": "2021-02-27",
      #           "keywords_searched" : None, 
      #           "date_of_response": None,
      #           "mode_of_search": mode,
      #           "search_results": search_results})

      # elif mode == 'manual':
      #   if _request["date"]:
      #     date = _request["date"]
      #     date = date.split(',')

      #     if date[0] == '2021-02-27' and date[1] == '2021-02-25':
      #       if 'default' in keywords:
      #         if _request["news_source_id"]:
      #           news_source_id = _request["news_source_id"]
      #           news_source_id = news_source_id.split(',')

      #           if 'ad60ab7b-906b-467d-b29e-92f200eb88fe' in news_source_id or 'ca3c6507-8c4a-4269-a384-8de06f43bc4f' in news_source_id:
      #             search_results = [
      #             {
      #             "Article Date": '2021-02-25',
      #             "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
      #             "City_of_News_Paper": None,
      #             "HDFC_Bank_Name_under_News_Article": "No",
      #             "Key_word_Used_foruuidentify_the_article": "money laundering",
      #             "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
      #             "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
      #             "Source_Name": "Economic Times",
      #             "Source_of_Info": "News Paper",
      #             "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
      #             "uuid": f1.uuid4()
      #             },
      #             {
      #             "Article Date": '2021-02-26',
      #             "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
      #             "City_of_News_Paper": None,
      #             "HDFC_Bank_Name_under_News_Article": "No",
      #             "Key_word_Used_foruuidentify_the_article": "money laundering",
      #             "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
      #             "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
      #             "Source_Name": "Economic Times",
      #             "Source_of_Info": "News Paper",
      #             "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
      #             "uuid": f1.uuid4()
      #             },
      #             {
      #             "Article Date": '2021-02-27',
      #             "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
      #             "City_of_News_Paper": None,
      #             "HDFC_Bank_Name_under_News_Article": "No",
      #             "Key_word_Used_foruuidentify_the_article": "money laundering",
      #             "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
      #             "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
      #             "Source_Name": "Economic Times",
      #             "Source_of_Info": "News Paper",
      #             "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
      #             "uuid": f1.uuid4()
      #             }
      #             ]
      #             return jsonify({"news_source_id": news_source_id, 
      #               "last_updated_time": "2021-02-27",
      #               "keywords_searched" : keywords, 
      #               "date_of_response": _request["date"],
      #               "mode_of_search": mode,
      #               "search_results": search_results})

      #       elif 'money laundering' in keywords or 'money launder' in keywords:
      #         if _request["news_source_id"]:
      #           news_source_id = _request["news_source_id"]
      #           news_source_id = news_source_id.split(',')

      #           if 'ad60ab7b-906b-467d-b29e-92f200eb88fe' in news_source_id or 'ca3c6507-8c4a-4269-a384-8de06f43bc4f' in news_source_id:
      #             search_results = [
      #             {
      #             "Article Date": '2021-02-25',
      #             "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
      #             "City_of_News_Paper": None,
      #             "HDFC_Bank_Name_under_News_Article": "No",
      #             "Key_word_Used_foruuidentify_the_article": "money laundering",
      #             "Organization_Name_mentioned_in_the_news": "Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ED, Jharkhand Ispat Private Limited, JIPL, Enforcement Directorate, PMLA, CBI, CAG, State, SC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
      #             "Person_Name_mentioned_in_the_news": "Vittal Kamath, Dilip Ray, HC Gupta, Naveen Jindal, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
      #             "Source_Name": "Economic Times",
      #             "Source_of_Info": "News Paper",
      #             "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/ed-attaches-assets-worth-rs-1-2-crore-in-coal-scam-case/articleshow/81175445.cms",
      #             "uuid": f1.uuid4()
      #             },
      #             {
      #             "Article Date": '2021-02-26',
      #             "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, MUMBAI, BNM, Mumbai, Gujarat, Kerala, Bangalore, Colombia, New Delhi",
      #             "City_of_News_Paper": None,
      #             "HDFC_Bank_Name_under_News_Article": "No",
      #             "Key_word_Used_foruuidentify_the_article": "money laundering",
      #             "Organization_Name_mentioned_in_the_news": "Nippon India, SBI, Mirae Asset Emerging Bluechip Fund, Nokia, ET Markets, The Economic Times Digital Payments Forum, ET India Inc., Lok Sabha, ET TV, PMLA, ED, the JM Joshi Group, the Enforcement Directorate, Omkar Group, Slum Rehabilitation Authority, NPA, Covid, BMC, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Sensex Live, IRCTC, Infosys, Boeing, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service",
      #             "Person_Name_mentioned_in_the_news": "Sachin Joshi, Omkar, Narendra Modi, Mamata Banerjee, Ashok Gehlot, Mehbooba Mufti, Amit Shah, Nitish Kumar, Sonia Gandhi, Mukesh Ambani, Elon Musk, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
      #             "Source_Name": "Economic Times",
      #             "Source_of_Info": "News Paper",
      #             "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/pmla-case-bizman-actor-sachin-joshi-remanded-in-ed-custody/articleshow/80926650.cms",
      #             "uuid": f1.uuid4()
      #             },
      #             {
      #             "Article Date": '2021-02-27',
      #             "last_updated_time": "2021-02-27",
      #             "City_State_mentioned_under_the_news": "India, UAE, Saudi Arabia, US, Bihar, Delhi, NEW DELHI, Kerala, Mumbai, Bangalore, Colombia, New Delhi",
      #             "City_of_News_Paper": None,
      #             "HDFC_Bank_Name_under_News_Article": "No",
      #             "Key_word_Used_foruuidentify_the_article": "money laundering",
      #             "Organization_Name_mentioned_in_the_news": "Coal India Ltd, Mirae Asset Emerging Bluechip Fund, ICICI, SBI, Axis, Nokia, ET Markets, ET India Inc., The Economic Times Digital Payments Forum, Lok Sabha, ET TV, ET Bureau, ED, Enforcement Directorate, NGO Advantage India, the Central Bureau of Investigation, Airbus, Isolux Corsan, Air India, Airbus/Isolux Corsan, Foreign Investment Promotion Board, FIPB, Govt, Ministry of Finance, Indian Air Force, Indian Armed Forces News, Ministry of Coal, NRC, CAA, Nureca, Covid, Sensex Live, IRCTC, Infosys, Ministry of Agriculture, Ministry of External Affairs, Health News, IT News, IT Security News, AdAge India, Times of India, Bombay Times, ET Prime, Times Internet Limited, Bennett, Coleman & Co. Ltd., Times Syndication Service, DocuBay, TimesPrime",
      #             "Person_Name_mentioned_in_the_news": "Deepak Talwar, Raghav Ohri, Nitesh Rana, Tanveer Ahmed Mir, Aditya Talwar, Manoranjan Dutta, Chidambaram, Praful Patel, Sridhar Reddy, Babus, Devidas, Deepak Talwar’s, Narendra Modi, Mamata Banerjee, Rajnath Singh, Amit Shah, Sonia Gandhi, Elon Musk, Anil Deshmukh, Nirmala Sitharaman, Raghuram Rajan, Sundar Pichai, Eisamay, Kyra, Deepak Ajwani",
      #             "Source_Name": "Economic Times",
      #             "Source_of_Info": "News Paper",
      #             "Web_link_of_news": "https://economictimes.indiatimes.com/news/politics-and-nation/laundering-of-csr-funds-ed-adjudicating-authority-confirms-attachment-of-properties-of-deepak-talwar-worth-rs-70-crore/articleshow/80826322.cms",
      #             "uuid": f1.uuid4()
      #             }
      #             ]
      #             return jsonify({"news_source_id": news_source_id, 
      #               "last_updated_time": "2021-02-27",
      #               "keywords_searched" : keywords, 
      #               "date_of_response": _request["date"],
      #               "mode_of_search": mode,
      #               "search_results": search_results})
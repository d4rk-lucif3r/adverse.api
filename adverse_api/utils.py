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


def update_ids_dbs(keywords, news_source_ids):
    '''
    function to update sources ids and keywords into database
    '''
    dbs = {}
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['news_ids']
    dbs['keywords'] = keywords
    dbs['news_source_ids'] = news_source_ids
    collection_batches.insert(dbs)
    # print("Batch Run ingesting into DB")
    collection_batches.create_index([("news_ids", pymongo.ASCENDING)])
    # print("BatchId is created")
    return "Successfully Updated keywords and news source ids"

def current_ids_dbs(keywords, news_source_ids):
    '''
    function to update sources ids and keywords into database
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['news_ids']
    cursor = collection_batches.find({}, {'_id': False})
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

    current_databases = current_dbs()
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

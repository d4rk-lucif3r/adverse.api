import pymongo
from pymongo import MongoClient
from flask import Flask, request, render_template, jsonify, url_for, redirect
from app import app
from bson.json_util import dumps, loads
from flask import escape
import html
import bleach

# from utils import *
import ast
import httplib2
import json


@app.route("/")
@app.route("/index")
def home():
    # current status?
    docs = []
    client = MongoClient("localhost", 27017)
    db = client["BatchRunStatus"]
    collection_batches = db["DetailStatus"]
    cursor = collection_batches.find({}, {"_id": False})
    # status = [document['BatchRunStatus'] for document in cursor]
    # print(cursor)
    for document in cursor:
        # Sanitize all string values in the document to prevent XSS
        sanitized_doc = sanitize_document(document)
        docs.append(sanitized_doc)
        # print(document)

    results = {"results": docs}
    print(results)

    return jsonify(results)  # "Wiki Refresh Api test slave databases"
    # return render_template('home.html')

def sanitize_document(document):
    """
    Recursively sanitize all string values in a document to prevent XSS attacks.
    """
    if isinstance(document, dict):
        return {k: sanitize_document(v) for k, v in document.items()}
    elif isinstance(document, list):
        return [sanitize_document(item) for item in document]
    elif isinstance(document, str):
        # Use bleach to clean any HTML and prevent XSS
        return bleach.clean(document, strip=True)
    else:
        # Return non-string values unchanged
        return document


@app.route("/status")
def status():
    # current status?
    docs = []
    client = MongoClient("localhost", 27017)
    try:
        db = client["BatchRunStatus"]
        collection_batches = db["OverallStatus"]
        cursor = collection_batches.find({}, {"_id": False})
        # Sanitize the status value
        status = [sanitize_document(document["OverallStatus"]) for document in cursor]
        # print(cursor)
        # for document in cursor:
        # docs.append(document)
        # print(document)
        results = {"status": status[-1]}
    except Exception as e:
        print(e)
        results = {"status": None}

    # print(results)

    return jsonify(results)  # "Wiki Refresh Api test slave databases"
    # return render_template('home.html')


# @app.route('/check', methods=['GET', 'POST'])
# def check():
#     slave_mcs = ["44.229.34.80", "52.43.95.114"]
#     ip1 = "44.229.34.80"
#     ip2 = "52.43.95.114"

#     for mc in slave_mcs:
# check if machine is working or not


# message = ""
# if request.method == 'POST' or request.method == 'GET':

#     pep_name = request.form['pep_name']
#     pep_name = ''.join([char if ord(char) < 128 else '' for char in pep_name])

#     resp, content = httplib2.Http().request("http://44.229.34.80:5001/check_name/%s" % pep_name)

#     print(content)

#     content = content.decode("utf-8")

#     content = content.strip()

#     content = json.loads(content)


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
# results = {'results': pep_response}

#         results = dumps(content, sort_keys=False, indent=4, ensure_ascii=False)
#         message = 'Searched PEP information'
#         return render_template('check.html', response=results, msg=message)

# @app.route('/check_name/<name>')
# def check_name(name):

#     pep_name = ''.join([char if ord(char) < 128 else '' for char in pep_name])

#     resp, content = httplib2.Http().request("http://44.229.34.80:5001/check_name/%s" % pep_name)

#     content = content.decode("utf-8")

#     content = content.strip()

#     content = json.loads(content)

#     # responses = search(name)
#     # results = {'results':responses}
#     return content # jsonify(response) # response


# @app.route('/check2', methods=['GET', 'POST'])
# def check2():
#    if request.method == 'POST':
#       user = request.form['pep_name']
#       return redirect(url_for('check_name',name = user))
#    else:
#       user = request.args.get('pep_name')
#       return redirect(url_for('check_name',name = user))

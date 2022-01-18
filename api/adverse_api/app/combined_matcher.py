import itertools
import os
import re

import locationtagger
# stanza.download('en')
import pandas as pd
import spacy
import stanza
from black import traceback
from dateutil.parser import parse
from flair.data import Sentence
from flair.models import SequenceTagger
from fuzzywuzzy import fuzz
from transformers import (AutoModelForTokenClassification, AutoTokenizer,
                          pipeline)

tokenizer = AutoTokenizer.from_pretrained("dslim/bert-large-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-large-NER")

# tokenizer_xml = AutoTokenizer.from_pretrained(
#     "vesteinn/XLMR-ENIS-finetuned-ner")
# model_xml = AutoModelForTokenClassification.from_pretrained(
#     "vesteinn/XLMR-ENIS-finetuned-ner")
# ner_xml = pipeline("ner", model=model_xml, tokenizer=tokenizer_xml)
ner_bert = pipeline("ner", model=model, tokenizer=tokenizer)
ner_stanza = stanza.Pipeline(lang="en")
ner_flair = SequenceTagger.load("flair/ner-english-large")
# ner_flair = SequenceTagger.load("flair/ner-multi")
ner_spacy = spacy.load("en_core_web_trf")
ner_spacy_2 = spacy.load("en_core_web_lg")
# stanza.download('en', package = 'partut')
ner_stanza = stanza.Pipeline('en', package = 'partut') 
# org_fp = ["Latest", "Thanks", "Omicron", "Unionmic", "OTP",
#           "FIR", "'s", "http", '@', 'SHO', 'Court of Judicial Ma', 'pan India', 'P) Ltd Tags', 
#           'Bench', 'conscious', 'S://Images.Indianexpress.Com/2020/08/1X1.Png Top News',
#           'OBCikaner Gwa', 'Top News', 'Right Now', 'non-Yadav', 'ARTICLE', 'Black Cat', 'NDATR',
#           'TSTR', 'Regis General of',
#           ]
org_fp = ['SHO', 'FIR', 'IPS', 'OTP', 'Omicron', 'pan India',
          'ARTICLE', 'TSTR', 'NDATR', 'VET', 'cryptocurrencies', '’', 'ATM', 'SSP', 'CHB', 'Newsguard ']
# loc_fp = ["Wli Houseman ' s Wharf House House House", 'Batala', 'Hussainiwala']
loc_fp = ['BNB']
name_fp = [
    "maggi",
    "rooh afza",
    "prayagraj",
    "Owner",
    "thanks",
    ";td.",
    "CO.",
    "Omicron",
    "'s",
    "http",
    "@",
]


def is_date(string, fuzzy=False):
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

def combined_matcher(data):
    try:
        if type(data) is not str:
            if type(data) is list:
                data = ' '.join(data)
            else:
                print('[ERROR] Combined Matcher', data)
                raise TypeError('Data must be a str only')
        names = []
        org = []
        locations = []
        flair_test = {}
        flair_test2 = {}
        numeric_data = []
        final_numerical_data = []
        misc_data = []
        print('[INFO] Filtering Started\n')
        spacy_results = ner_spacy(data)
        for ent in spacy_results.ents:
            if ent.label_ == 'PERSON':
                names.append(ent.text)
        for i in range(len(names)):
            if names[i] in str(data):
                data = data.replace(names[i], '').replace(',', ' , ')
        locations.append(locationtagger.find_locations(text=data).regions)
        dat = data.split('\n')
        for i in range(len(dat)):
            stream = os.popen("echo "+data[i].strip()+" | finner extr")
            output = stream.read()
            if output != '':
                numeric_data.append(output.split('\t'))

            
        
        
        locations = list(itertools.chain(*locations))
        numeric_data = list(filter(None, numeric_data))
        for i in range(0, len(numeric_data)):
            for j in range(0, len(numeric_data[i])):
                if 'date' in numeric_data[i][j].lower() or 'time' in numeric_data[i][j].lower() or 'year' in numeric_data[i][j].lower() or 'amt' in numeric_data[i][j].lower():
                    word = numeric_data[i][:j]
                    final_numerical_data.append(word)
        final_numerical_data = list(
            set(itertools.chain.from_iterable(final_numerical_data)))
        print('[INFO] Predicting Tokens\n')
        sentence = Sentence(data)
        ner_flair.predict(sentence, mini_batch_size=16)
        # sentence_2 = Sentence(data)
        # ner_flair_2.predict(sentence_2, mini_batch_size=16)
        # print('Predicting with Flair done 1\n')
        stanza_results = ner_stanza(data)
        spacy_results = ner_spacy(data)
        spacy_results_2 = ner_spacy_2(data)
        # print('Predicting with Stanza done 1\n')
        # bert_results = ner_bert(data)
        for ent in stanza_results.entities:
            if ent.type == 'ORG':
                org.append(ent.text)
            if ent.type == 'LOC':
                locations.append(ent.text)
            if ent.type == 'LAW':
                misc_data.append(ent.text)
            if ent.type == 'GPE':
                locations.append(ent.text)
        raw_locations = []
        # locations = []

        for entity in sentence.get_spans('ner'):
            flair_test[entity.text] = entity.tag
        for i, j in flair_test.items():
            if j == 'LOC':
                locations.append(i)
            if j == 'GPE':
                locations.append(i)
            if j == 'MISC':
                misc_data.append(i)
            # if j == 'FAC':
            #     locations.append(i)
            # if j == 'ORG':
            #     org.append(i)
        # for entity in sentence_2.get_spans('ner'):
        #     flair_test2[entity.text] = entity.tag
        # for i, j in flair_test2.items():
        #     if j == 'LOC':
        #         locations.append(i)
        #     if j == 'GPE':
        #         locations.append(i)
        #     if j == 'FAC':
        #         locations.append(i)
        #     if j == 'ORG':
        #         org.append(i)
        for ent in spacy_results.ents:
            if ent.label_ == 'GPE':
                locations.append(ent.text)
            if ent.label_ == 'ORG':
                org.append(ent.text)
            # if ent.label_ == 'FAC':
            #     locations.append(ent.text)
            if ent.label_ == 'PERSON':
                names.append(ent.text)
            if ent.label_ == 'DATE':
                numeric_data.append(ent.text)
            if ent.label_ == 'TIME':
                numeric_data.append(ent.text)
            if ent.label_ == 'MONEY':
                numeric_data.append(ent.text)
            if ent.label_ == 'NUMBER':
                numeric_data.append(ent.text)
            if ent.label_ == 'LOC':
                locations.append(ent.text)
            if ent.label_ == 'LAW':
                misc_data.append(ent.text)
            if ent.label_ == 'CARDINAL':
                numeric_data.append(ent.text)
        for ent in spacy_results_2.ents:
            if ent.label_ == 'GPE':
                locations.append(ent.text)
            if ent.label_ == 'ORG':
                org.append(ent.text)
            # if ent.label_ == 'FAC':
            #     locations.append(ent.text)
            if ent.label_ == 'PERSON':
                names.append(ent.text)
            if ent.label_ == 'DATE':
                numeric_data.append(ent.text)
            if ent.label_ == 'TIME':
                numeric_data.append(ent.text)
            if ent.label_ == 'CARDINAL':
                numeric_data.append(ent.text)
            if ent.label_ == 'MONEY':
                numeric_data.append(ent.text)
            if ent.label_ == 'NUMBER':
                numeric_data.append(ent.text)
            if ent.label_ == 'LOC':
                locations.append(ent.text)
        filter_words = locations + final_numerical_data + org + numeric_data + misc_data
        # for i in range(len(filter_words)):
        #     if filter_words[i] in str(data):
        #         data = data.replace(filter_words[i], '').replace(',', ' , ')
        org = list(set(org)-set(misc_data))
        sentence = Sentence(data)
        ner_flair.predict(sentence, mini_batch_size=16)
        # print('Predicting with Flair done 2\n')
        stanza_results = ner_stanza(data)
        # print('Predicting with Stanza done 2\n')
        # xml_results = ner_xml(data)
        spacy_results = ner_spacy(data)
        spacy_results_2 = ner_spacy_2(data)
        # print('Predicting with BERT done 1\n')
        for ent in stanza_results.entities:
            if ent.type == 'PER':
                names.append(ent.text)
            if ent.type == 'GPE':
                locations.append(ent.text)
        for entity in sentence.get_spans('ner'):
            flair_test[entity.text] = entity.tag
        for i, j in flair_test.items():
            if j == 'PER':
                names.append(i)
        for ent in spacy_results.ents:
            if ent.label_ == 'PER':
                names.append(ent.text)
        for ent in spacy_results_2.ents:
            if ent.label_ == 'PER':
                names.append(ent.text)
        # for entity in sentence_2.get_spans('ner'):
        #     flair_test2[entity.text] = entity.tag
        # for i, j in flair_test2.items():
        #     if j == 'PER':
        #         names.append(i)
        # this_location = []
        # all_locations_list_tmp = []
        # for ner_dict in xml_results:
        #     if ner_dict['entity'] == 'B-LOC':
        #         if len(this_location) == 0:
        #             this_location.append(ner_dict['word'])
        #         else:
        #             all_locations_list_tmp.append([this_location])
        #             this_location = []
        #             this_location.append(ner_dict['word'])
        #     elif ner_dict['entity'] == 'I-LOC':
        #         this_location.append(ner_dict['word'])

        # all_locations_list_tmp.append([this_location])
        # final_location_list = []

        # for location_list in all_locations_list_tmp:
        #     full_location = ' '.join(location_list[0]).replace(
        #         ' ##', '').replace(' .', '.')
        #     final_location_list.append([full_location])

        # for i in range(len(final_location_list)):
        #     final_location_list[i] = final_location_list[i][0]
        # locations = locations + final_location_list
        # this_org = []
        # all_orgs_list_tmp = []
        # for ner_dict in xml_results:
        #     if ner_dict['entity'] == 'B-ORG':
        #         if len(this_org) == 0:
        #             this_org.append(ner_dict['word'])
        #         else:
        #             all_orgs_list_tmp.append([this_org])
        #             this_org = []
        #             this_org.append(ner_dict['word'])
        #     elif ner_dict['entity'] == 'I-ORG':
        #         this_org.append(ner_dict['word'])
        # all_orgs_list_tmp.append([this_org])
        # final_org_list = []
        # for org_list in all_orgs_list_tmp:
        #     full_org = ' '.join(org_list[0]).replace(
        #         ' ##', '').replace(' .', '.')
        #     final_org_list.append([full_org])

        # for i in range(len(final_org_list)):
        #     final_org_list[i] = final_org_list[i][0]
        # org = org + final_org_list
        
        filter_words = locations + final_numerical_data + org
        for i in range(len(filter_words)):
            if filter_words[i] in str(data):
                data = data.replace(filter_words[i], '')
        print('[INFO] Filtering Done\n')
        print('[INFO] Name Prediction Started\n')
        bert_results = ner_bert(data)
        this_name = []
        all_names_list_tmp = []
        for ner_dict in bert_results:
            if ner_dict['entity'] == 'B-PER':
                if len(this_name) == 0:
                    this_name.append(ner_dict['word'])
                else:
                    all_names_list_tmp.append([this_name])
                    this_name = []
                    this_name.append(ner_dict['word'])
            elif ner_dict['entity'] == 'I-PER':
                this_name.append(ner_dict['word'])

        all_names_list_tmp.append([this_name])
        final_name_list = []
        for name_list in all_names_list_tmp:
            full_name = ' '.join(name_list[0]).replace(
                ' ##', '').replace(' .', '.')
            final_name_list.append([full_name])

        for i in range(len(final_name_list)):
            final_name_list[i] = final_name_list[i][0]
        names = names + final_name_list

        print('Post-Processing the Predictions\n')
        
        if len(org) > 0:
            for i in range(len(org)):
                org[i] = org[i].strip().replace("'s", '').replace(
                    "'", '').replace('the', '').replace('The', '').replace('@', '')
                if org[i] in locations:
                    org[i] = ''
                if org[i] in names:
                    org[i] = ''
                if '##' in org[i]:
                    org[i] = ''
                if len(org[i]) < 3:
                    org[i] = ''
                if any(emt in org[i] for emt in org_fp):
                    rem = [emt for emt in org_fp if(emt in str(org[i]))][0]
                    print('org removed: ', rem)
                    org[i] = org[i].lower().replace(
                        rem.lower(), '').strip().title()
                if is_date(org[i]):
                    org[i] = ''
            for (i, element) in enumerate(org):
                for (j, choice) in enumerate(org[i+1:]):
                    if fuzz.ratio(element, choice) >= 90:
                        if element in org:
                            org.remove(element)
                            print('FUZZ org removed: ', element)
                # if len(org[i].split()) == 1:
                #     for j in range(len(org)):
                #         if org[i] in org[j]:
                #             org[i] = ''
        if len(names) > 0:
            for i in range(len(names)):
                names[i] = names[i].strip().replace("'s", '').replace("'",'').replace('@', '')
                if names[i] in org:
                    names[i] = ''
                if names[i] in locations:
                    names[i] = ''
                if '##' in names[i]:
                    names[i] = ''
                if len(names[i]) < 4:
                    names[i] = ''
                if any(emt in names[i] for emt in name_fp):
                    rem = [emt for emt in name_fp if(emt in str(names[i]))][0]
                    print('name removed: ', rem)
                    names[i] = names[i].lower().replace(
                        rem.lower(), '').strip().title()
                if names[i].isnumeric():
                    names[i] = ''
                if is_date(names[i]):
                    names[i] = ''
            for (i, element) in enumerate(names):
                for (j, choice) in enumerate(names[i+1:]):
                    if fuzz.ratio(names, choice) >= 90:
                        if element in names:

                            names.remove(element)
                            print('FUZZ name removed: ', element)
                
                # if len(names[i].split()) == 1:
                #     for j in range(len(names)):
                #         if names[i] in names[j]:
                #             names[i] = ''
        if len(locations) > 0:
            for i in range(len(locations)):
                locations[i] = locations[i].strip().replace("'s", '').replace(
                    "'", '').replace('@', '')
                if locations[i] in org:
                    locations[i] = ''
                if locations[i] in names:
                    locations[i] = ''
                if '##' in locations[i]:
                    locations[i] = ''
                if len(locations[i]) < 3:
                    locations[i] = ''
                if any(emt in locations[i] for emt in loc_fp):
                    rem = [emt for emt in loc_fp if(
                        emt in str(locations[i]))][0]
                    print('loc removed: ', rem)
                    locations[i] = locations[i].lower().replace(
                        rem.lower(), '').strip().title()
                if is_date(locations[i]):
                    locations[i] = ''
            # for (i, element) in enumerate(locations):
            #     for (j, choice) in enumerate(locations[i+1:]):
            #         if fuzz.ratio(element, choice) >= 90:
            #             locations.remove(element)
            #             print('FUZZ loc removed: ', element)
                # if len(locations[i].split()) == 1:
                #     for j in range(len(locations)):
                #         if locations[i] in locations[j]:
                #             locations[i] = ''

        org = list(set(filter(None, org)))
        names = list(set(filter(None, names)))
        locations = list(set(filter(None, locations)))
        # print('Post-Processing the Predictions Completed\n')
        return names, org, locations
    except Exception as e:
        print(data)
        traceback.print_exc()
        print('[ERROR] Combined Matcher :', e)

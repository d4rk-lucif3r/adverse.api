import keras
import os
import spacy
# import stanza
from pathlib import Path
import time
import warnings
import pandas as pd
from googletrans import Translator
from unidecode import unidecode

# stanza.download('en')

nlp_Name = spacy.load("en_core_web_trf") # spacy.load(OUTPUT1)
# nlp_Org = spacy.load("en_core_web_lg") # spacy.load(OUTPUT1)
# nlp_Org = stanza.Pipeline('en')

# OUTPUT1='NER Models/Name/content/Model'
# OUTPUT2='NER Models/Prefix/content/Model'
# OUTPUT3='NER Models/Position Held/content/Model'
# OUTPUT4='NER Models/Intelligence/Model'

# nlp_Name = spacy.load(OUTPUT1)
# nlp_Pref = spacy.load(OUTPUT2)
# nlp_Min = spacy.load(OUTPUT3)
# nlpIntel = spacy.load(OUTPUT4)

#trans=Translator()          ###Only create instance once while loading in program else it automatically blocks IP if frequently used

def translator(text):
    try:
        t=trans.translate(text)
        print(t.text)
    except:
        return text
    #print(t.src)
    #print(t.dest)
    #print(t.text)
    if t.src == 'en':
        return text
    return t.text

def pred(tag):
    return 1
    # rtrn = 0
    # redirect = [
                # 'black money'
                # 'money laundering', 
                # 'money launder', 
                # 'lauder the money', 
                # 'money-mule', 
                # 'money mule', 
                # 'Hawala', 
                # 'drug-trafficking', 
                # 'drug trafficking', 
                # 'terror', 
                # 'terror financing'
                # ]
    
    # print(tag)

    # tag = tag.strip().lower()
    # tag = unidecode(tag)
    # tag = translator(tag)
    # stop_words = ['contact','citizenship','jobs','immigration','service','travel','security','apply','military','data','news','pension','travel','social','terms','media','twitter','where','mobile','treaties','covid','e-mail','search','healthy','quit','download','forum','veteran','information','detail','scheme','art','help','external website','register','communication','policy','policies','bill','form','affair','visit','grievance','access','publication','holiday','sitemap','mission','plan','pan','constitution','community','life','speech','service','gallery','rule','law']
    # hot_words = ['department','government','member','parties','party','federal','mp', 'lords','ministry','minister','cabinet','senat'] # Tuning the model
    # for hw in hot_words:
        # if hw in tag:
            # return 1
    # for sw in stop_words:
        # if sw in tag:
            # return 0
    # if(tag.isnumeric()):
        # return 1
        
    # doc = nlp_Name(tag)     #NLP model object

    # for ent in doc.ents:
      # if ent.label_ == 'PERSON':
        # print('-------------------', tag, ':', ent.label_, '-----------------')
        # rtrn = 1
      # else:
        # pass
    
    # for _tag in redirect:
    #   if _tag in tag:
    #     print('----------------- tag in redirect:', tag, '------------')
    #     rtrn = 1
            
    # if tag in redirect:
      # print('------------------- tag in redirect:', tag, '------------')
      # rtrn = 1
    # elif tag.isdigit():
      # print('------------------- tag is digit:', tag, '---------------')
      # rtrn = 1
    # else:
      # rtrn = 0
    
    # return 1

    # doc = nlpIntel(tag)     #NLP model object

    # for ent in doc.ents:
        # if ent.text!=0:
            # print(tag)
            # return 1
    # return 0

# def main():
#     tag = ''
#     print(pred(tag))

# if __name__=='__main__':
#     main()
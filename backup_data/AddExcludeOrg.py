import ast

import requests
from fake_useragent import UserAgent
import pandas as pd
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import LanguageTranslatorV3
from googletrans import Translator
from google_trans_new import google_translator as google_translator2
import newspaper
from newspaper import Article
from newspaper.utils import BeautifulSoup
from newspaper import Config
import os
import re
from datetime import datetime
import time

import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta
from dateutil.parser import parse
import spacy

nlp_Name = spacy.load("en_core_web_trf")
translator2 = google_translator2()
translator = Translator()
ua = UserAgent()
client = MongoClient("localhost", 27017)
db = client["adverse_db"]
collection_batches = db["adverse_db"]
cursor = collection_batches.find({})


def detect_lang(text):
    if text.strip():
        KEY = "IE8hVfhy0XCdw2gFGKQous7etnspEN66OTWsnB_bEhe2"
        SERVICE_URL = "https://api.eu-gb.language-translator.watson.cloud.ibm.com/instances/1c656c34-6170-4a20-be18-57f030abacf0"

        authenticator = IAMAuthenticator(KEY)
        language_translator = LanguageTranslatorV3(
            version="2018-05-01", authenticator=authenticator
        )

        language_translator.set_service_url(SERVICE_URL)
        lang = language_translator.identify(text).get_result()

        return lang["languages"][0]["language"]


def soup_text(soup, sourcename):
    """
    Function to use beautifulsoup tag
    and classes to fetch article data.
    """

    text_ = []

    dictionary = {
        # 'www.hindustantimes.com': {'h1': ['hdg1', 'hdg3'], 'div': ['sortDec', 'detail', 'storyDetails']},
        # 'www.dnaindia.com': {'div': ['container']},
        # 'www.business-standard.com': {'h1': ['headline'], 'h2': ['alternativeHeadline'], 'span': ['p-content']},
        "www.esakal.com": {
            "Headlines": {"h1": ["news-title"]},
            "Text": {"div": ["news-description selectionShareable"]},
        },
        "maharashtratimes.com": {
            "Headlines": {"h1": {"itemprop": ["headline"]}},
            "Synopsis": {
                "h2": ["caption text_ellipsis more"],
                "div": ["undefined top-article tophighlight"],
            },
            "Text": {"article": ["story-content"]},
        },
        "www.greaterkashmir.com": {
            "Headlines": {
                "h1": [
                    "story-headline-m__headline__1LzaJ story-headline-m__dark__1wPld"
                ]
            },
            "Text": {"div": ["arr--story-page-card-wrapper"]},
        },
        "www.nytimes.com": {
            "Headlines": {"h1": ["css-19rw7kf e1h9rw200"]},
            "Synopsis": {"p": ["css-w6ymp8 e1wiw3jv0"]},
            "Text": {"div": ["css-53u6y8"]},
        },
        "www.business-standard.com": {
            "Headlines": {"h1": ["headline"]},
            "Synopsis": {"h2": ["alternativeHeadline"]},
            "Text": {"span": ["p-content"]},
        },
        "www.ndtv.com": {
            "Headlines": {"h1": ["sp-ttl"]},
            "Synopsis": {"h2": ["sp-descp"]},
            "Text": {"div": ["sp-cn ins_storybody", ".*sp-cn.*"]},
        },
        # 'indianexpress.com': {'h1': ['native_story_title'], 'h2' : ['synopsis'], 'div' : ['full-details', 'pcl-full-content']},
        "www.bbc.com": {
            "Headlines": {
                "h1": [
                    "ssrcss-1pl2zfy-StyledHeading e1fj1fc10",
                    "ssrcss-1pl2zfy-StyledHeading",
                ]
            },
            "Synopsis": {
                "b": [
                    "ssrcss-14iz86j-BoldText e5tfeyi0",
                    "ssrcss-hmf8ql-BoldText e5tfeyi3",
                ]
            },
            "Text": {
                "div": [
                    "ssrcss-uf6wea-RichTextComponentWrapper e1xue1i83",
                    "ssrcss-18snukc-RichTextContainer e5tfeyi1",
                    "ssrcss-5h7eao-ArticleWrapper",
                    "ssrcss-5h7eao-ArticleWrapper e1nh2i2l6",
                    "ssrcss-14iz86j-BoldText",
                ]
            },
        },
        "www.bbc.co.uk": {
            "Headlines": {
                "h1": [
                    "ssrcss-1pl2zfy-StyledHeading e1fj1fc10",
                    "ssrcss-1pl2zfy-StyledHeading",
                ]
            },
            "Synopsis": {
                "b": [
                    "ssrcss-14iz86j-BoldText e5tfeyi0",
                    "ssrcss-hmf8ql-BoldText e5tfeyi3",
                ]
            },
            "Text": {
                "div": [
                    "ssrcss-uf6wea-RichTextComponentWrapper e1xue1i83",
                    "ssrcss-18snukc-RichTextContainer e5tfeyi1",
                    "ssrcss-5h7eao-ArticleWrapper",
                    "ssrcss-5h7eao-ArticleWrapper e1nh2i2l6",
                    "ssrcss-14iz86j-BoldText",
                ]
            },
        },
        "economictimes.indiatimes.com": {
            "Headlines": {"h1": ["artTitle font_faus"]},
            "Synopsis": {"h2": ["summary", "artSyn tac font_mon"]},
            "Text": {
                "div": [
                    ".*artText.*",
                    "pageContent flt",
                    ".*content1.*",
                    "primeContent col s_col font_faus artText paywall",
                ]
            },
        },
        # 'www.thehindu.com': {'div': ['title', 'paywall']},
        "timesofindia.indiatimes.com": {
            "Headlines": {"h1": ["_23498", ".*_1Y-96.*"], "div": ["pu1zi"]},
            "Synopsis": {"h2": ["Normal media-summary"]},
            "Text": {"div": ["ga-headlines", ".*Normal.*", ".*_3YYSt.*", "_2ndvO"]},
        },
        "bangaloremirror.indiatimes.com": {
            "Headlines": {"div": ["heading2"]},
            "Text": {"div": [".*Normal.*", "ga-headlines"]},
        },
        "edition.cnn.com": {
            "Headlines": {"h1": ["pg-headline"]},
            "Text": {"div": ["pg-headline", "l-container", "zn-body__paragraph"]},
        },
        "www.deccanchronicle.com": {
            "Headlines": {"h1": ["headline"]},
            "Synopsis": {"div": ["strap"]},
            "Text": {"div": ["story-body"]},
        },
        "www.deccanherald.com": {
            "Headlines": {"h1": ["f-left sanspro-b"]},
            "Synopsis": {"h3": ["sanspro-reg strap-heading"]},
            "Text": {"div": ["field-items"]},
        },
        "www.tribuneindia.com": {
            "Headlines": {"div": ["glb-heading"]},
            "Text": {"div": ["story-desc"]},
        },
        "www.dailypioneer.com": {
            "Headlines": {"div": ["col-12"]},
            "Text": {
                "div": [
                    "col-22 mt-4",
                    "col-12 col-md order-md-2 order-1",
                    "newsDetailedContent",
                    "row no-gutters bodyContentSection",
                    "storyDetailBox",
                ]
            },
        },
        "www.telegraphindia.com": {
            "Headlines": {
                "h1": ["fs-45 uk-text-1D noto-bold mb-2", "sub_head  haedlinesstory1"]
            },
            "Synopsis": {
                "div": ["fs-20 uk-text-69 noto-regular", "fontStyle", "col-12"]
            },
            "Text": {"div": ["fs-17 pt-2 noto-regular"], "p": ["p_txt_kj"]},
        },
        "epaper.telegraphindia.com": {
            "Headlines": {
                "h1": ["fs-45 uk-text-1D noto-bold mb-2", "sub_head  haedlinesstory1"]
            },
            "Synopsis": {
                "div": ["fs-20 uk-text-69 noto-regular", "fontStyle", "col-12"]
            },
            "Text": {
                "div": ["fs-17 pt-2 noto-regular", "website_story_inside", "col-12"],
                "p": ["p_txt_kj"],
            },
        },
        "www.wsj.com": {
            "Headlines": {"h1": ["wsj-article-headline"]},
            "Synopsis": {
                "h2": ["sub-head"],
                "figcaption": [".*article__inset__video__caption.*"],
            },
            "Text": {
                "div": [
                    "column at8-col8 at12-col7 at16-col9 at16-offset1",
                    "wsj-snippet-body",
                ],
                "p": ["p_txt_kj"],
            },
        },
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
        for (
            tag,
            _class,
        ) in tag_class.items():  # i = 0, headline, i = 1, synopysis, i =2 text
            for __tag, __class in _class.items():
                for ___class in __class:
                    if (
                        (tag == "Headlines" and not Headlines)
                        or (tag == "Synopsis" and not Synopsis)
                        or (tag == "Text" and not Text)
                    ):
                        regex = re.compile(___class)
                        for block in soup.find_all(__tag, {"class": regex}):
                            for strings in block.stripped_strings:
                                if tag == "Headlines":
                                    Headlines.append(strings)
                                elif tag == "Synopsis":
                                    Synopsis.append(strings)
                                elif tag == "Text":
                                    Text.append(strings)
                                else:
                                    continue

        Text = " ".join(Text)
        Text = [Text]

        text_ = Headlines + ["\n"] + Synopsis + ["\n"] + Text
        # text_.append(strings)
        # text = [tag.get_text() for tag in soup.find_all("div", {"class" : regex})]
        # text_ += [tag.get_text() for tag in soup.find_all(tag, {"class" : regex})]
    except Exception as e:
        print("soup_text: ", e)
        return None

    if text_:
        # print(text_)
        # return '\n'.join(text_)
        # return ' '.join(text_)
        return "".join(text_)
    else:
        print("text not found")
        return None


def current_ids():
    """
    function to retrieve current ids from mongodb
    """
    client = MongoClient("localhost", 27017)
    db = client["news_ids"]
    collection_batches = db["news_ids"]
    cursor = collection_batches.find({}, {"_id": False})
    dbs = [database for database in cursor]
    return dbs[-1]


def StripUnique(_list):

    """
    function to strip leading and trailing spaces
    and return sorted unique elements
    """
    _list = [__list.strip() for __list in _list if __list.strip()]
    _list = list(set(_list))
    _list.sort()
    return _list


# function to split strip and unique
def SplitStripUnique(_string, delimiter=","):

    """
    function to split(,) strip leading and trailing spaces
    and return sorted unique elements
    """
    _list = _string.split(delimiter)
    _list = [__list.strip() for __list in _list if __list.strip()]
    _list = list(set(_list))
    _list.sort()
    return _list


# function to get text of article:
def GetText(url):
    """
    function to fetch the text of
    the article from its url
    """
    USER_AGENT = ua.random
    HEADERS = {
        "user-agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

    config = Config()
    config.headers = HEADERS
    config.request_timeout = 40

    try:
        article = Article(url, config=config)
        article.download()
        article.parse()

        soup = BeautifulSoup(article.html, "html.parser")
        text = soup_text(soup, url.split("/")[2])

        if not text:
            text = article.title + os.linesep + article.text

        # check the language of text
        lang = detect_lang(text)
        print("lang:", lang)

        if lang == "mr":
            translation = translator.translate(text, dest="en")
            # print('translating:', translation.text)
            text = translation.text

            lang = detect_lang(text)
            print("language after translation:", lang)

            if lang == "mr":
                translate_text2 = translator2.translate(text, lang_tgt="en")
                print("again translating:", translate_text2)
                text = translate_text2

    except Exception as e:
        print("couldn't fetch text: ", print(e))
        text = ""

    return text


dbs = current_ids()
excludeorg = SplitStripUnique(dbs["excludeorg"])

print("looking through documents..............")
for document in cursor:

    # check article date
    week = datetime.now() - timedelta(days=8)
    week = week.strftime("%Y-%m-%d %H:%M:%S")
    date = parse(document["created_date"].split("+")[0])
    date = date.strftime("%Y-%m-%d %H:%M:%S")

    if date >= week and document["Key word Used for identify the article"]:
        print("found document:", date)
        # text = GetText(document["Web link of news"])

        # if not text:
        # print('text not found: ', document["Web link of news"])
        # continue

        document["Person Name mentioned in the news"] = SplitStripUnique(
            document["Person Name mentioned in the news"], delimiter="|"
        )
        document["Organization Name mentioned in the news"] = SplitStripUnique(
            document["Organization Name mentioned in the news"], delimiter="|"
        )

        # check if org in excludeorg
        _exc_org = []
        for ent in (
            document["Person Name mentioned in the news"]
            + document["Organization Name mentioned in the news"]
        ):
            for _org in excludeorg:

                if ent.lower() == _org.lower():
                    _exc_org.append(ent)

                if len(ent.split("’")) > 1:
                    for _ent in ent.lower().split("’"):
                        __org = _org.lower().split(" ")
                        __org = StripUnique(__org)
                        _ent_text = _ent.lower().split(" ")
                        _ent_text = StripUnique(_ent_text)

                        if set(__org) <= set(_ent_text) or set(_ent_text) <= set(__org):
                            _exc_org.append(ent)

                __org = _org.lower().split(" ")
                __org = StripUnique(__org)
                _ent_text = ent.lower().split(" ")
                _ent_text = StripUnique(_ent_text)

                if set(__org) <= set(_ent_text) or set(_ent_text) <= set(__org):
                    _exc_org.append(ent)

        document["Person Name mentioned in the news"] = [
            x
            for x in document["Person Name mentioned in the news"]
            if x not in _exc_org
        ]
        document["Organization Name mentioned in the news"] = [
            x
            for x in document["Organization Name mentioned in the news"]
            if x not in _exc_org
        ]

        document["Person Name mentioned in the news"] = " | ".join(
            document["Person Name mentioned in the news"]
        )
        document["Organization Name mentioned in the news"] = " | ".join(
            document["Organization Name mentioned in the news"]
        )

        collection_batches.save(document)

from datetime import datetime, timedelta
import spacy
from dateutil.parser import parse
import newspaper
from newspaper import Article
import pytz
import csv

csv_file = "month_1.csv"
csv_columns = [
    "name",
    "org",
    "loc",
    "keyword",
    "hdfcpresent",
    "date",
    "sourcename",
    "weblink",
]

news_link = [
    "https://www.thehindu.com/news/international/pak-court-sentences-lakhvi-to-5-years-in-terror-financing-case/article33529260.ece"
]

nlp_Name = spacy.load("en_core_web_trf")  # spacy.load(OUTPUT1)

utc = pytz.UTC

keywords = [
    "black money" "money laundering",
    "money launder",
    "lauder the money",
    "money-mule",
    "money mule",
    "Hawala",
    "drug-trafficking",
    "drug trafficking",
    "terror",
    "terror financing",
]


with open(csv_file, "w") as csvfile:
    _writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    _writer.writeheader()
    # for link in news_link:
    profile = {
        "name": "",
        "org": "",
        "loc": "",
        "keyword": "",
        "hdfcpresent": "No",
        "date": "",
        "sourcename": "",
        "weblink": "",
    }
    article = Article(news_link[0])
    article.download()
    article.parse()
    text = article.text.lower()
    if article.publish_date:
        # print(article.publish_date)
        # if parse(article.publish_date) > date:
        # print('Date is greater:', article.publish_date)

        profile["date"] = article.publish_date

    for keyword in keywords:
        if keyword in text.lower():
            if keyword not in profile["keyword"]:
                profile["keyword"] += keyword + ", "
        else:
            continue

    if "hdfc" in text.lower():
        profile["hdfcpresent"] = "YES"

    doc = nlp_Name(article.text)
    # iterate through each entity present
    for count, ent in enumerate(doc.ents):
        # save data in profile
        # find persons in text
        if ent.label_ == "PERSON":
            # remove name if present in false positives
            if ent.text not in profile["name"]:
                # print(str(string))
                profile["name"] += ent.text + ", "

        # find persons in text
        elif ent.label_ == "ORG":

            # remove name if present in false positives
            if ent.text not in profile["org"]:
                profile["org"] += ent.text + ", "

            else:
                # print('Persons entity:', ent.text, ':', ent.label_)
                pass

        # find persons in text
        elif ent.label_ == "GPE":

            # remove name if present in false positives
            if ent.text not in profile["loc"]:
                profile["loc"] += ent.text + ", "

        profile["sourcename"] = news_link[0]
        profile["weblink"] = article.url

    print(profile)

    if profile["keyword"]:
        _writer.writerow(profile)
        print(profile)

        # for rss in rss_list:
        #   NewsFeed = feedparser.parse(rss)
        #   for news in NewsFeed.entries:
        #     data = {"URL": news['link'], "Publised_Date": 'India'}
        #     _writer.writerow(data)
        #     # print(news['link'], news['published'])

        #   print(ent.text, ":", ent.label_)

        #   # find persons in text
        #   if ent.label_ == 'PERSON':

        # if article.publish_date:
        #   print(article.publish_date)
        #   if article.publish_date > date:
        #     print('Date is greater:', article.publish_date)

from bs4 import BeautifulSoup
import requests
from functions import *
import pandas as pd
from csv import writer
import datetime
from unidecode import unidecode
import feedparser
import csv

def rss2url():
    csv_file = "rss.csv"
    csv_columns = ['URL', 'Publised_Date']
    rss_list = ['https://www.thehindu.com/news/national/feeder/default.rss',
                'https://indianexpress.com/section/india/feed/',
                'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml',
                'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
                'http://www.allindianewspapers.com/Feeds/nation.xml',
                'https://www.dnaindia.com/feeds/india.xml',
                'https://www.deccanchronicle.com/rss_feed/',
                'https://www.asianage.com/rss_feed/',
                'https://timesofindia.indiatimes.com/rssfeeds/1221656.cms',
                'https://www.business-standard.com/rss/home_page_top_stories.rss',
                'http://feeds.feedburner.com/ndtvnews-top-stories?format=xml',
                'https://www.livemint.com/rss/news',
                'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
                'https://asia.nikkei.com/rss/feed/nar',
                'https://www.ft.com/?format=rss',
                'https://www.economist.com/international/rss.xml',
                'http://www.abc.net.au/news/feed/2942460/rss.xml',
                'http://feeds.bbci.co.uk/news/world/rss.xml',
                'https://www.theguardian.com/world/rss',
                'https://prod-qt-images.s3.amazonaws.com/production/bloombergquint/feed.xml',
                'http://rss.cnn.com/rss/edition.rss']
    
    # NewsFeed = feedparser.parse("https://economictimes.indiatimes.com/rssfeedstopstories.cms")
    
    with open(csv_file, 'w') as csvfile:
      _writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
      _writer.writeheader()

      for rss in rss_list:
        NewsFeed = feedparser.parse(rss)
        for news in NewsFeed.entries:
          data = {"URL": news['link'], "Publised_Date": 'India'}
          _writer.writerow(data)
          # print(news['link'], news['published'])

def returner(string):
  
    text = string['text']
    name = string['name']
    org = string['org']
    loc = string['loc']
    facebook_url = string['facebook_link']
    twitter_url = string['twitter_link']
    other_weblinks = string['other_weblinks']
    image_link = string['image_link']
    keywords = string['keyword']
    sources = string['sources']
    hdfc_present = string['hdfcpresent']

    # prefix = ''
    # name = string['name']
    # ministry = string['org']
    # image_url = string['image_link']
    # facebook_url = string['facebook_link']
    # instagram_url = ''
    # twitter_url = string['twitter_link']
    # other_urls = string['other_weblinks']

    # name=''
    # doc = nlp_Name(string)
    # for count,ent in enumerate(doc.ents):
    #     name+=ent.text+' '
    #     if count==0:
    #         break
    
    # doc =nlp_Min(string)
    # ministry=''
    # for ent in doc.ents:
    #     ministry+=ent.text+' '
    
    # doc =nlp_Pref(string)
    # prefix=''
    # for ent in doc.ents:
    #     prefix+=ent.text+' '

    # prefix = ' '.join(prefix.split(' ')[:2])
    # name = ' '.join(name.split(' ')[:10])
    # name = ''.join(e for e in name if e.isalpha() or e == ' ')   #removing special chars, numbers and punctuations
    # ministry = ''.join(e for e in ministry if e.isalpha() or e == ' ')
    return name, org, loc, keywords, sources, hdfc_present

def has_name(text):  #  name finder
    doc = nlp_Name(text)
    names = ''
    for ent in doc.ents:
        names += ent.text+' '
    names = names.strip()
    if names=='' or names.isnumeric():
        return 0
    return 1

def scraper(url, domain, soup):
    
    result = []

    # print('it is now inside scraper function')
    
    # false positives list
    fp_name = [
               
    ]
    
    fp_org = [
              
    ]
      
    # list of positions
    fp_loc = [
                 
    ]
    
    keywords = [
                'black money'
                'money laundering', 
                'money launder', 
                'lauder the money', 
                'money-mule', 
                'money mule', 
                'Hawala', 
                'drug-trafficking', 
                'drug trafficking', 
                'terror', 
                'terror financing'
                ]

    # extract body from it
    tag = soup.body # scrape.parse_sou
    
    # save data in profile
    profile = {'text': '', 'name': '', 'org': '', 'loc': '', 'facebook_link': '', 'twitter_link': '', 'other_weblinks': '', 'image_link': '', 'keyword': '', 'sources': '', 'hdfcpresent': 'No'}
    
    # iterate through each string
    for string in tag.stripped_strings:
      
      for keyword in keywords:
        if keyword in str(string).lower():
          if keyword not in profile['keyword']:
            profile['keyword'] += keyword + ', '
        else:
          continue
      
      if 'hdfc' in str(string).lower():
        profile['hdfcpresent'] = 'YES'

      if len(string) > 540:
        continue
      
      # name extration through spacy model
      doc = nlp_Name(str(string))
      
      # iterate through each entity present
      for count,ent in enumerate(doc.ents):
        
        # find persons in text
        if ent.label_ == 'PERSON':
          
          # remove name if present in false positives
          if str(string) not in fp_name and (ent.text not in profile['name']):
            # print(str(string))
            profile['text'] = str(string)
            profile['name'] += ent.text + ', '
        
        # find persons in text
        elif ent.label_ == 'ORG':
          
          # remove name if present in false positives
          if str(string) not in fp_org and (ent.text not in profile['org']):
            profile['org'] += ent.text + ', '
          
          else:
            # print('Persons entity:', ent.text, ':', ent.label_)
            pass
        
        # find persons in text
        elif ent.label_ == 'GPE':
          
          # remove name if present in false positives
          if str(string) not in fp_loc and (ent.text not in profile['loc']):
            profile['loc'] += ent.text + ', '
    
    print(profile)

    if profile['keyword']:
      result.append(profile)
      print(profile)
    
    return result

def link_parser(links):
    img_formats = ['.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi', '.png', 'webp', '.bmp', '.jp2', '.jpx', '.jpm', '.j2k']
    image_url, facebook_url, instagram_url, twitter_url, other_urls = '','','','',''
    for link in links:
        if 'javascript' in link:
            continue
        for imf in img_formats:
            if imf in link.lower():
                image_url+=link+' '
                break
        else:
            if 'facebook' in link.lower():
                facebook_url+=link+' '
            elif 'instagram' in link.lower():
                instagram_url+=link+' '
            elif 'twitter' in link.lower():
                twitter_url+=link+' '
            else:
                other_urls+=link+' '
    if len(other_urls.split(' '))>5:        #Removing excessive websites 
        other_urls = ' '.join(other_urls.split(' ')[:4])
    return image_url, facebook_url, instagram_url, twitter_url, other_urls


def parse_soup(domain, nation, url, soup):

    # print('it is now inside parse soup')

    if soup is None:
        return

    content =  scraper(url, domain, soup)

    # if not content:
        # return 
    #return content                         #debug statement

    write_obj = open("result_database/database.csv", 'a+', newline='',encoding='utf-8')
    csv_writer = writer(write_obj)
    for items in content:
        # print(' items :', items)
        name, org, loc, keywords, sources, hdfc_present = returner(items)        
        l1 = [name.strip(),org.strip(),loc.strip()]
        # if l1[0] == '' and l1[1] == '':     #no name no salutation //cleaner step
            # continue
        # if l1[1] in l1[2]:                  #name found in ministry //cleaner step
            # continue
        # if nation != 0:                     #0 if nation could not be retrieved from url
            # l1.append(nation)
        # else:
            # l1.append('')
        l1.append(datetime.datetime.now())  #timestamp
        # l1.append('PEP')                    #catagory
        # image_url, facebook_url, instagram_url, twitter_url, other_urls = link_parser(items[1])
        l1.extend((keywords, hdfc_present, url)) #urls
        print(l1)
        csv_writer.writerow(l1)
        row_count = sum(1 for line in open(filename))
    print('writing csv file')
    write_obj.close()



# #for debugging:
# def main():
#     urls = ["https://www.india.gov.in/my-government/whos-who/council-ministers", "https://www.gov.za/about-government/leaders", "https://uaecabinet.ae/en/cabinet-members", "https://www.india.gov.in/my-government/whos-who/chiefs-armed-forces", "https://www.india.gov.in/my-government/indian-parliament/lok-sabha"]
#     url2 = "https://www.india.gov.in/my-government/whos-who/council-ministers"
#     site = requests.get(url2).content
#     soup = BeautifulSoup(site,"html.parser")
#     return(parse_soup('in','sw',url2, soup.body))
    

# if __name__=="__main__":
#     res = main()
#     print(res)

    


import pymongo
from pymongo import MongoClient
from datetime import datetime

def add_default_ids():
    '''
    function to default news_id databases in mongodb
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['news_ids']

    keywords = ['black money',
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

    keywords = ', '.join(keywords)

    source_news_ids = ['c1f4a45b-aa9c-4627-980b-f69509e5c862',
 'a70e9599-4480-46d2-889f-652fdd58cc55',
 '3d4a70cb-fe3f-459e-8cb1-43bc04f759c6',
 'ad60ab7b-906b-467d-b29e-92f200eb88fe',
 '52d0de86-1525-417d-b8fd-2158f1256c38',
 '4dfab6d8-8246-469b-9e19-7ddbb55d806d',
 'eeff09cb-6fdb-45f1-a206-32a55320d598',
 'e43b544e-577b-4ed0-adb0-4661bda4c487',
 'ca3c6507-8c4a-4269-a384-8de06f43bc4f',
 '5b32994e-2e6e-417f-ba44-77f508742349',
 '8cbc9eec-7255-43bf-bb72-2bce4f4764ea',
 '91272662-bb73-4649-a8c2-026d112c190e',
 'd33446c7-a37b-4c5b-ba7a-275cc9583c05',
 '65cb3dec-94a9-4274-b518-543c74e14a59',
 '6c676cc1-2338-4834-a0fb-9ae8a04a2bda',
 '890d11b8-05e7-416e-b777-7ba62f4a7045',
 '7eba470b-1edc-4f69-840d-99cfde3a5fcb',
 'a9ecac2e-a7da-4bbd-b326-103de3149ece',
 'bef37780-c007-4b96-89f4-5198b69f2c93',
 '2cdd8f28-01f5-4d18-b438-742f04fe3140',
 'e5a8f17c-58c6-4087-a5c0-2ab681446611']

    source_news_ids = ','.join(source_news_ids)

    last_updated_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    x = {}
    x['keywords'] = keywords
    x['news_source_id'] = source_news_ids
    x['last_updated_time'] = last_updated_time

    collection_batches.insert_one(x)
    print('Successfully inserted default keywords and news sources')

    return 'Successfully inserted default keywords and news sources'

def newsids2rss():
    '''
    function to save news_id databases in mongodb
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['rss']

    dictionary = {'2cdd8f28-01f5-4d18-b438-742f04fe3140': 'https://prod-qt-images.s3.amazonaws.com/production/bloombergquint/feed.xml',
 '3d4a70cb-fe3f-459e-8cb1-43bc04f759c6': 'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml',
 '4dfab6d8-8246-469b-9e19-7ddbb55d806d': 'https://www.dnaindia.com/feeds/india.xml',
 '52d0de86-1525-417d-b8fd-2158f1256c38': 'http://www.allindianewspapers.com/Feeds/nation.xml',
 '5b32994e-2e6e-417f-ba44-77f508742349': 'https://www.business-standard.com/rss/home_page_top_stories.rss',
 '65cb3dec-94a9-4274-b518-543c74e14a59': 'https://asia.nikkei.com/rss/feed/nar',
 '6c676cc1-2338-4834-a0fb-9ae8a04a2bda': 'https://www.ft.com/?format=rss',
 '7eba470b-1edc-4f69-840d-99cfde3a5fcb': 'http://www.abc.net.au/news/feed/2942460/rss.xml',
 '890d11b8-05e7-416e-b777-7ba62f4a7045': 'https://www.economist.com/international/rss.xml',
 '8cbc9eec-7255-43bf-bb72-2bce4f4764ea': 'https://feeds.feedburner.com/ndtvnews-cities-news?format=xml',
 '91272662-bb73-4649-a8c2-026d112c190e': 'https://www.livemint.com/rss/news',
 'a70e9599-4480-46d2-889f-652fdd58cc55': 'https://indianexpress.com/section/india/feed/',
 'a9ecac2e-a7da-4bbd-b326-103de3149ece': 'http://feeds.bbci.co.uk/news/world/rss.xml',
 'ad60ab7b-906b-467d-b29e-92f200eb88fe': 'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
 'bef37780-c007-4b96-89f4-5198b69f2c93': 'https://www.theguardian.com/world/rss',
 'c1f4a45b-aa9c-4627-980b-f69509e5c862': 'https://www.thehindu.com/news/national/feeder/default.rss',
 'ca3c6507-8c4a-4269-a384-8de06f43bc4f': 'https://timesofindia.indiatimes.com/rssfeeds/1221656.cms',
 'd33446c7-a37b-4c5b-ba7a-275cc9583c05': 'https://feeds.a.dj.com/rss/RSSWorldNews.xml',
 'e43b544e-577b-4ed0-adb0-4661bda4c487': 'https://www.asianage.com/rss_feed/',
 'e5a8f17c-58c6-4087-a5c0-2ab681446611': 'http://rss.cnn.com/rss/edition.rss',
 'eeff09cb-6fdb-45f1-a206-32a55320d598': 'https://www.deccanchronicle.com/rss_feed/'}
    for key, value in dictionary.items():
        x = {}
        x['source_news_ids'] = key
        x['rss_values'] = value
        collection_batches.insert_one(x)

    print('Successfully inserted all news source_ids')

    return 'Successfully inserted all 28 news sources'



def newsids2db():
    '''
    function to save news_id databases in mongodb
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['source_ids']
    dictionary = {'2cdd8f28-01f5-4d18-b438-742f04fe3140': 'Bloomberg', 
    '3d4a70cb-fe3f-459e-8cb1-43bc04f759c6': 'Hindustan Times', 
    '4dfab6d8-8246-469b-9e19-7ddbb55d806d': 'DNA',
    '52d0de86-1525-417d-b8fd-2158f1256c38': 'The Telegraph',
    '557e51e6-b04c-4be1-a4fa-aff4b7e1c37b': 'The pioneer',
    '5966436a-2f26-4305-95a3-fcda913d621d': 'The Statesman',
    '5b32994e-2e6e-417f-ba44-77f508742349': 'Business Standard',
    '65cb3dec-94a9-4274-b518-543c74e14a59': 'Nikkei',
    '6c676cc1-2338-4834-a0fb-9ae8a04a2bda': '\nFinancial Times',
    '73f6c89a-fe6b-4c20-ba77-fdf4740874b0': 'Deccan Herald',
    '7eba470b-1edc-4f69-840d-99cfde3a5fcb': 'Australian Financial review',
    '890d11b8-05e7-416e-b777-7ba62f4a7045': 'The Economist',
    '8cbc9eec-7255-43bf-bb72-2bce4f4764ea': 'NDTV',
    '91272662-bb73-4649-a8c2-026d112c190e': 'LiveMint',
    'a70e9599-4480-46d2-889f-652fdd58cc55': 'The Indian Express',
    'a9ecac2e-a7da-4bbd-b326-103de3149ece': 'BBC',
    'ad60ab7b-906b-467d-b29e-92f200eb88fe': 'The Economic Times',
    'bef37780-c007-4b96-89f4-5198b69f2c93': 'The Guardian',
    'c1f4a45b-aa9c-4627-980b-f69509e5c862': 'The Hindu',
    'c55c0b9c-614e-4f1b-ba2c-d5e34e37800b': 'Dawn',
    'ca3c6507-8c4a-4269-a384-8de06f43bc4f': 'The Times Of India',
    'd33446c7-a37b-4c5b-ba7a-275cc9583c05': 'The Wall Street Journal',
    'e43b544e-577b-4ed0-adb0-4661bda4c487': 'Asian Age',
    'e5a8f17c-58c6-4087-a5c0-2ab681446611': 'CNN',
    'ec2217c5-0320-491c-a351-78ff97d47885': 'USA Today',
    'eeff09cb-6fdb-45f1-a206-32a55320d598': 'Deccan Chronicle'}
    for key, value in dictionary.items():
        x = {}
        x['uuid'] = key
        x['source_name'] = value
        collection_batches.insert_one(x)

    return 'Successfully inserted all 28 news sources'

def keywords2db():
    '''
    function to save keywords into mongodb
    '''
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['keyword_ids']
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
    for key, value in enumerate(keywords):
        x = {}
        x['id'] = key
        x['keyword'] = value
        collection_batches.insert_one(x)

    return 'Successfully inserted all keywords'

def update_dbs(primary, secondary):
    '''
    function to update current slave machines into mongodb
    '''
    dbs = {}
    client = MongoClient('localhost', 27017)
    db = client['CurrentDatabase']
    collection_dbs = db['Databases']
    dbs['Primary'] = primary
    dbs['Secondary'] = secondary
    collection_dbs.insert(dbs)
    # print("Batch Run ingesting into DB")
    collection_dbs.create_index([("Databases", pymongo.ASCENDING)])
    # print("BatchId is created")


if __name__ == '__main__':
    add_default_ids()
    newsids2rss()

import pymongo
from pymongo import MongoClient
import bson

if __name__ == '__main__':
    batch = {}
    client = MongoClient('localhost', 27017)
    db = client['news_ids']
    collection_batches = db['fp_list']
    post = collection_batches.find_one({'_id': bson.objectid.ObjectId("60799419ba4eda7932fc2ec2")})
    if post:
        post.pop('excludeorg')
        post.pop('exclude')
        collection_batches.save(post)
    	# post['exclude'] = None
    	# post['excludeorg'] = None

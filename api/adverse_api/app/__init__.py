from flask import Flask
from elasticsearch import Elasticsearch
# from config import Config


app = Flask(__name__)
# app.config.from_object(Config)
# app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
		# if app.config['ELASTICSEARCH_URL'] else None
from app import routes
# app.run(debug=True, host="0.0.0.0")

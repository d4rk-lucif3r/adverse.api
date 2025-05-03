from flask import Flask
from elasticsearch import Elasticsearch
from flask_talisman import Talisman

# from config import Config


app = Flask(__name__)
# Configure HTTP Strict Transport Security
Talisman(app, 
         force_https=True, 
         strict_transport_security=True, 
         strict_transport_security_max_age=31536000,  # 1 year in seconds
         strict_transport_security_include_subdomains=True,
         strict_transport_security_preload=True)

# app.config.from_object(Config)
# app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
# if app.config['ELASTICSEARCH_URL'] else None
from app import routes

# app.run(debug=True, host="0.0.0.0")

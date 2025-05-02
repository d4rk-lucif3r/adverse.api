from flask import Flask
from elasticsearch import Elasticsearch
from config import Config
from flask_talisman import Talisman


app = Flask(__name__)
app.config.from_object(Config)
app.elasticsearch = (
    Elasticsearch([app.config["ELASTICSEARCH_URL"]])
    if app.config["ELASTICSEARCH_URL"]
    else None
)

# Add HSTS protection with Talisman
talisman = Talisman(
    app,
    force_https=True,
    strict_transport_security=True,
    strict_transport_security_max_age=31536000,  # 1 year in seconds
    strict_transport_security_include_subdomains=True,
    strict_transport_security_preload=True
)

from app import routes

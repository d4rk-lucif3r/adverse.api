from flask import Flask
from flask_talisman import Talisman
from elasticsearch import Elasticsearch
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.elasticsearch = (
    Elasticsearch([app.config["ELASTICSEARCH_URL"]])
    if app.config["ELASTICSEARCH_URL"]
    else None
)

# Apply Flask-Talisman to enforce security headers, including HSTS
Talisman(app, force_https=True)

from app import routes
AdverseMedia.API
====
This document all the details to run adverse media api, modes and to reproduce software

Structure:
---
The API consist of Master/Slave Configuration each added in it own branch

### Master Configuration
Master runs on adverse_master and send http request to confirm batch run is complete. 

Master runs API to communicate with Slave and its uses Decision Maker to check if batch table is run successfully on Slave machine.

### Slave Configuration
Slave runs on adverse_slave and sends data to Master. It uses two apis `adverseapi` and `adverse_check_api`. 

#### adverseapi
It sends news results in json data format in full, manual and incremental mode

When run incremental mode, it will save all the keywords and news_source_ids to `news_id` mongo database.

#### adverse_check_api
It sends the `DetailStatus` and `OverallStatus` to confirm the batch run is complete

#### Manual Mode
Manual mode uses scheduler to schedule every day calls and update data in `adverse_db`. Using `news_ids` present in mongo database manaul mode will run on that ids present in keywords and news sources.

## Backups

Fews rows has been extracted from different news paper to test the scraper

hindu.json: contains few rows of news articles run on the hindu news paper
indian_express.json: contains few rows of news articles run on the hindu news paper
ndtv.json: contains few rows of news articles run on the ndtv news paper
toi.json: contains few rows of news articles run on the times of india news paper
economic.json: contains few rows of news articles run on the economic times news paper

full_mode.json: contains data concatenated from 1 year (13 news source) run and 1 month (26 news source run), it has been added to mongo db in pep_wiki vm.

database2.csv: contains data collected by running scraper on 1 month (26 news sources)

database.csv: contains data collected by running scraper on 1 year (13 news sources)

### Notebooks
It contains jupyter notebook to experiment, getting started and run different models for named entity recognition. 

adverse_{news_paper}.ipynb: explore possibility of different site structure scraping through ner models
adverse_trails.ipynb: contain end-2-end pipeline on running scrapper on different sources
adverse_media.ipynb: contains ners models exploration through different methods.
news_scraping.ipynb: it gives use newsapi.org for scraping
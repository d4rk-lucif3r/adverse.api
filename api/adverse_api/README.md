## Adverse API

Our master branch is for deployment and other branches are used for development of our upcoming release.

## Table of contents

- [Quick start](#quick-start)


## Quick start

Several quick start options are available:

- Clone the repo
- Go inside repo folder
- Create a virtual environment : `python3 -m venv venv # python3`
- Activate virtual environment : `source venv/bin/activate python 3`
- Install all dependencies : `pip3 install -r requirements.txt`
- To start api under gunicorn you can use the following command:
	* on your own pc: `gunicorn -b localhost:8000 -w 4 pep_check_api5003:app`
	* on server: `gunicorn -b 0.0.0.0:5000 -w 4 pep_check_api5003:app`


#TODO: error handling, design docs, tests, etc

#TODO: store NHL API data on first request or schedule a daily fetch

#TODO: set up gitlabs on local server - use github private repo as source
# backup

#TODO: set up server to run API via WSGI on apache or something with CORS
# enabled

#POC: this is a proof of concept v2 using NHL public API instead of table
#scaraping hockeyreference.com
from flask import Flask
from dotenv import load_dotenv
load_dotenv('.env')
from routes import api

app = Flask(__name__)
api.init_app( app )

app.run( host="0.0.0.0")
#TODO: error handling, design, tests, etc
from flask import Flask
from routes import api

app = Flask(__name__)
api.init_app( app )

app.run()
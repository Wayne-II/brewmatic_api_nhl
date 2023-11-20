from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import os
from models.schedule import Schedule
from models.teams import Team
from models.skaters import Skater
from models.roster import Roster
from models.base import Base
from models.engine import engine
from models.injury import Injury

#FOR USE WITH DEVELOPMENT ONLY!!!
#USE deploy.py FOR PRODUCTION DEPLOYMENT
if not database_exists( engine.url ):
    create_database( engine.url )
    print( 'Database created')
Base.metadata.create_all( engine )
print( 'Tables created or updated' )





#TODO design database schema
#TODO create database initialization script/API setup script.  Setup
#   script will set up schema, API keys, as well as fetch initial data.
#TODO requests for historical data will be blocked from non-"admin" API
#   clients.  App will only be able to fetch data for the given day.
#   This is intended to prevent API abuse.
#Tables:
#games/schedule
#teams
#skaters
#suggestions - requires feedback from app which will require permissions
#   these permissions will be handled by API keys.  Public access will
#   not have write access to the suggestion table, but the "admin" API
#   enabled app will.  "admin" API app will not be available to install
#   from any stores or website.  Key will not be stored in source code.
#   Manual installtion of "admin" API app will be required to manually
#   
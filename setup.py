from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import os
from schema.schedule import Schedule
from schema.teams import Team
from schema.skaters import Skater
from schema.base import Base
from schema.engine import engine


if not database_exists( engine.url ):
    create_database( engine.url )
    Base.metadata.create_all( engine )
    print( 'database and tables created' )
else:
    print( 'database already exists' )





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
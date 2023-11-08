from sqlalchemy import Column, Integer, String, Date, ForeignKey, BLANK_SCHEMA
from uuid import uuid4
from .base import Base

class Schedule( Base ):
    __tablename__ = 'schedule'
    id = Column( Integer, primary_key=True, autoincrement=True )
    home_id = Column( Integer, ForeignKey( 'teams.id' ) )
    away_id = Column( Integer, ForeignKey( 'teams.id' ) )
    game_date = Column( Date )

#TODO: new schedule API https://api-web.nhle.com/v1/scoreboard/
#this endpoint provides team records
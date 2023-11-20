from sqlalchemy import Column, Integer, String, Date, ForeignKey, BLANK_SCHEMA
from uuid import uuid4
from .base import Base

#TODO: make home_id, away_id, and game_date the primary key so duplicates 
# aren't entered into the API database
class Schedule( Base ):
    __tablename__ = 'schedule'
    __table_args__ = {'extend_existing':True}
    id = Column( Integer, primary_key=True, autoincrement=True )
    home_id = Column( Integer, ForeignKey( 'teams.team_id' ) )
    away_id = Column( Integer, ForeignKey( 'teams.team_id' ) )
    game_date = Column( Date )
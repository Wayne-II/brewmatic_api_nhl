from sqlalchemy import Column, Integer, String, Date, ForeignKey, BLANK_SCHEMA
from .base import Base

class Schedule( Base ):
    __tablename__ = 'schedule'
    id = Column( Integer, primary_key=True )
    home_id = Column( Integer, ForeignKey( 'teams.id' ) )
    away_id = Column( Integer, ForeignKey( 'teams.id' ) )
    game_date = Column( Date, primary_key=True )


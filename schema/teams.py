from sqlalchemy import Column, Integer, String
from .base import Base

class Team( Base ):
    __tablename__ = 'teams'
    id = Column( Integer, primary_key=True )
    name = Column( String )
    abbreviation = Column( String )
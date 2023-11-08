from sqlalchemy import Column, Integer, String
from .base import Base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert

class Team( Base ):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing':True}
    id = Column( Integer, primary_key=True )
    name = Column( String )
    abbreviation = Column( String )
    #TODO: last updated field to keep track if teams was updated
    # will use roster for now

    def __repr__(self):
        return f'Team(id: {self.id}, name: \'{self.name}\', abbreviation: \'{self.abbreviation}\')'
    
    #TODO: team standings https://api-web.nhle.com/v1/standings/2023-11-05
    #

    
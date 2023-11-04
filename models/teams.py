from sqlalchemy import Column, Integer, String
from .base import Base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert

class Team( Base ):
    __tablename__ = 'teams'
    id = Column( Integer, primary_key=True )
    name = Column( String )
    abbreviation = Column( String )
    #TODO: last updated field to keep track if teams was updated
    # will use roster for now

# @compiles( Insert, 'sqlite')
# def generate_insert( insert, compiler, **kwargs ):
#     stmt = compiler.visit_insert( insert, **kwargs )
#     if insert.dialect_kwargs.get( 'sqlite_on_conflict_do_nothing' ):
#         stmt += ' ON CONFLICT DO NOTHING'
#     return stmt
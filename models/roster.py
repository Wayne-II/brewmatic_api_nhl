from sqlalchemy import Column, Integer, Date, ForeignKey
from .base import Base

class Roster( Base ):
    __tablename__ = 'roster'
    id = Column( Integer, primary_key=True )
    skater_id = Column( Integer, ForeignKey( 'skaters.id' ), nullable=False, unique=True )
    team_id = Column( Integer, ForeignKey( 'teams.id' ), nullable=False )
    updated = Column( Date )
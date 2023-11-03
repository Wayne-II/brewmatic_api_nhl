from sqlalchemy import Column, Integer, String, Date, ForeignKey
from .base import Base

class Skater( Base ):
    __tablename__ = 'skaters'
    id = Column( Integer, primary_key=True )
    join_date = Column( Date, primary_key=True )
    lase_name = Column( String )
    skater_full_name = Column( String )
    goals = Column( Integer )
    team_id = Column( Integer, ForeignKey( 'teams.id' ), nullable=False )
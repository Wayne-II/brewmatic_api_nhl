from sqlalchemy import Column, Integer, String, Date, ForeignKey
from .base import Base

class Skater( Base ):
    __tablename__ = 'skaters'
    __table_args__ = {'extend_existing':True}
    #id provided by NHL and is used in roster to link skaters to teams
    #nullable=False required with autoincrement=False otherwise a syntax error 
    #happens for the "ON CONFLICT" can't reproduce in simple example.  happens
    #in writers/skaters.py.
    #TODO: figure out why nullable=False resolved this error trying to run data_scraper.py:
    #sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) near "ON": syntax error
    # [SQL: INSERT INTO skaters DEFAULT VALUES ON CONFLICT (id) DO UPDATE SET updated = excluded.updated, goals = excluded.goals, team_abbrevs = excluded.team_abbrevs]
    id = Column( Integer, primary_key=True, autoincrement=False, nullable=False )
    updated = Column( Date )
    #last_name is pointless unless we want to display <Initial>. <Last Name>
    #this is a likely scenario to save display space
    last_name = Column( String )
    skater_full_name = Column( String )
    goals = Column( Integer )
    team_abbrevs = Column( String )

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from .base import Base

class Skater( Base ):
    __tablename__ = 'skaters'
    __table_args__ = {'extend_existing':True}
    #id provided by NHL and is used in roster to link skaters to teams
    id = Column( Integer, primary_key=True, autoincrement=False )
    updated = Column( Date )
    #last_name is pointless unless we want to display <Initial>. <Last Name>
    #this is a likely scenario to save display space
    last_name = Column( String )
    skater_full_name = Column( String )
    goals = Column( Integer )
    team_abbrevs = Column( String )
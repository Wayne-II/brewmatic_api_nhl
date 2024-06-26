from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from .base import Base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert
import json
from dataclasses import dataclass

@dataclass
class Injury( Base ):
    __tablename__ = 'injuries'
    __table_args__ = {'extend_existing':True}
    id = Column( Integer, primary_key=True )
    skater_id = Column( Integer, ForeignKey( 'skaters.id' ), unique=True )
    #TODO: status can be (D)day-to-day, (S)scratched, (I)injured, or (IR)injured reserve for now it's just whatever the source information provides
    status = Column( String ) # (I)njured or (S)cratched
    updated = Column( DateTime(timezone=True) )
    injury_type = Column( String )# upper body, Achillies, undisclosed, blood clot, etc.
    #TODO: last updated field to keep track if teams was updated
    # will use roster for now

    def __repr__(self):
        return f'Injury(skater_id: {self.skater_id}, status: \'{self.status}\')'
    
    def jsonify( self ):
        return {
            'id':self.id,
            'skater_id':self.skater_id,
            'status':self.status,
            'updated':self.updated,
            'injury_type':self.injury_type
        }
    
    def __str__( self ):
        return f'Injury(skater_id: {self.skater_id}, status: \'{self.status}\')'
    

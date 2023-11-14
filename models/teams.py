from sqlalchemy import Column, Integer, String, Date
from .base import Base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import Insert

class Team( Base ):
    __tablename__ = 'teams'
    __table_args__ = {'extend_existing':True}
    team_id = Column( Integer, primary_key=True )
    # name = Column( String )
    # abbreviation = Column( String )
    losses = Column( Integer )
    ot_losses = Column( Integer )
    team_full_name = Column( String )
    ties = Column( Integer )
    wins = Column( Integer )
    wins_in_regulation = Column( Integer )
    tri_code = Column( String )
    updated = Column( Date )
    #TODO: last updated field to keep track if teams was updated
    # will use roster for now

    def __repr__(self):
        return f'Team("Kickin ass, TBD, Third thing here")'
    
    #TODO: team standings https://api-web.nhle.com/v1/standings/2023-11-05
    #

    # overloading team_id so it can be used as team_id, id, or teamId
    # reasoning.  3rd party API provides in lower camel case.  database stores
    # fields as snake case.  3rd party api sometimes calls it id, depending on
    # the endpoint eg /schedule uses id and /team uses teamId.  reason for
    # snake case in the database is databases aren't case sensitive unless you
    # surround fields by double quotes.  Models are for database translation, 
    # and overloading the attributes allows use of API JSON dict/object keys
    # to get the field without knowledge of the underlying models in the API
    # response handling code.  Having setters should allow for setting up
    # models using defaul JSON encoders and decoders without defining multiple
    # encoders and decoders for each individual class to compensate for the
    # intricacies of each level of the data layers
    ################### team_id overloads
    @property
    def id( self ):
        return self.team_id
    @property
    def teamId( self ):
        return self.team_id
    
    ################### ot_losses overloads
    @property
    def otLosses( self ):
        return self.ot_losses
    ################### team_full_name overloads
    @property
    def teamFullName( self ):
        return self.team_full_name
    ################### wins_in_regulation overloads
    @property
    def winsInRegulation( self ):
        return self.wins_in_regulation
    


#teams IDs: 1,17,6,52,28,5,14,4,9,10,7,19,12,53,20,8,15,26,23,21,18,24,54,2,55,25,30,16,3,29,13,22
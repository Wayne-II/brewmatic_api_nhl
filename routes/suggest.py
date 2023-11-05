from flask_restx import Namespace, Resource, fields
from difflib import get_close_matches
from sqlalchemy.orm import sessionmaker
import models
from common import GetDate

def GetTodaysSkaters():
    #TODO: get list of skaters from list of skaters going to play today
    #This is a list of skaters paying today october 25th 2023 ( WSH v NJD)
    #testing Google ML Kit detecting Nicklas Backsrtom as Nicklas Backstronm.
    #Some arbitrary 'N' got added between 'O' and 'M'
    Session = sessionmaker( models.engine )
    ret = []
    today = GetDate()

    with Session() as session:
        #get today's roster
        rosterQuery = session.query(
            models.Roster
        ).filter(
            models.Roster.updated == today
        )
        rosterResults = session.scalars( rosterQuery ).all()
        skaterIds = [ roster.skater_id for roster in rosterResults ]
        #using roster IDs get skater full names
        skatersQuery = session.query( 
            models.Skater
        ).filter(
            models.Skater.id.in_( skaterIds )
        )
        skatersResults = session.scalars( skatersQuery ).all()
        ret = [ skater.skater_full_name for skater in skatersResults ]
    return ret

def SuggestSkater( suggestFromName ):
    #TODO: prevent abuse.  difflib is notoriously computationally intensive
    #   and could be leveraged to DoS from a single system.
    skaters = GetTodaysSkaters()
    ret = {}
    #this is not perfect as someone with a longer name match have a higher
    #percentage match.  This will have to be something that is checked.
    #adding a last name match in the results will help this.  The most
    #common mistmatches are diacritics(umlaut), short names(mitch vs
    #mitchell), and punctuated names(AJ. vs A.J.)
    for misspelledName in suggestFromName:
        ret[ misspelledName ] = get_close_matches( misspelledName, skaters, 1)
    return ret

#TODO add to skaters namespace as /skaters/suggest
api = Namespace( "suggest" )

name_parser = api.parser()
name_parser.add_argument('name', type=str, action='split')

@api.route("/")
@api.doc(params={"name": "Skater name that doesn't seem to have a match with existing data."})
class Suggest( Resource ):
    def get( self ):
        args = name_parser.parse_args()
        return SuggestSkater( args[ 'name' ] )
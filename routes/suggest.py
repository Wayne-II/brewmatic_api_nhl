from flask_restx import Namespace, Resource, fields
from difflib import get_close_matches
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_
import models
from common import GetDate

def GetTodaysSkaters():
    Session = sessionmaker( models.engine )
    ret = []
    today = GetDate()

    with Session() as session:
        #get skaters from the roster where the team they are currently on is a
        #team that is playing today
        rosterQuery = session.query(
            models.Roster
        ).join(
            models.Team,
            and_( models.Roster.team_id == models.Team.team_id )
        ).join(
            models.Schedule,
            or_( models.Schedule.away_id == models.Team.team_id, models.Schedule.home_id == models.Team.team_id )
        ).filter(
            models.Schedule.game_date == today
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
    #TODO: this is not perfect as someone with a longer name match have a higher
    #percentage match.  This will have to be something that is checked.  adding 
    #a last name match in the results will help this.  The most common 
    #mistmatches are diacritics(umlaut), short names(mitch vs mitchell), and 
    #punctuated names(AJ. vs A.J.)
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
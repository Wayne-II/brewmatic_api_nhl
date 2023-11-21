# https://statsapi.web.nhl.com/api/v1/teams
# https://statsapi.web.nhl.com/api/v1/teams/ID
# https://statsapi.web.nhl.com/api/v1/teams/ID?expand=team.roster
# https://statsapi.web.nhl.com/api/v1/teams?teamId=<id,list,comma,separated>&expand=team.roster

# this endpoint is only required to get the translation between team name and 3
# character code EG TOR for Toronto Maple Leafs

#Tim Horton's puts point awards to accounts before 6AM Eastern.  6AM Eastern
#is probably the best time to automate the check for NHL data as the app will
#likely have the updated information by this time.

import requests
import datetime

from sqlalchemy.orm import sessionmaker
import models

from flask_restx import Namespace, Resource, fields
from common import FetchJson, GetDate, GetDateString, GetInsert
from os import getenv

def GetAllTeamIds():
    #TODO: this shouldn't happen - flag suspicious request
    Session = sessionmaker( models.engine )
    ret = []
    with Session() as session:
        selectQuery = session.query( models.Team.team_id )
        results = session.scalars( selectQuery ).all()
        #TODO: exception handling
        ret = results if results else []
    return ret

#TODO: update to new api
def RetrieveData( teamIds ):
    Session = sessionmaker( models.engine )
    ret = []
    with Session() as session:
        teamQuery = session.query( 
            models.Team 
        ).filter(
            models.Team.team_id.in_( teamIds ) 
        )
        
        rosterQuery = session.query( 
            models.Roster
        ).filter(
            models.Roster.team_id.in_( teamIds ) 
        )
        
        teamResults = session.scalars( teamQuery ).all()
        rosterResults = session.scalars( rosterQuery ).all()
        for team in teamResults:
            roster = [ roster.skater_id for roster in rosterResults if roster.team_id == team.id ]
            ret.append( {
                "team_id" : team.teamId,
                "losses" : team.losses,
                "ot_losses" : team.otLosses,
                "team_full_name" : team.teamFullName,
                "ties" : team.ties,
                "wins" : team.wins,
                "wins_in_regulation" : team.winsInRegulation,
                "tri_code" : team.triCode,
                'roster': roster
            } )
    return ret

api = Namespace( "teams" )

team_id_parser = api.parser()
team_id_parser.add_argument('teamId', type=int, action='split')

@api.route("/")
@api.doc(params={"teamId": "Optional comma separated list of Team IDs"})
class Teams( Resource ):
    def get( self ):
        ret = []
        args = team_id_parser.parse_args()
        #TODO: exception handling
        teamIds = args[ 'teamId' ] if 'teamId' in args.keys() and args[ 'teamId' ] else GetAllTeamIds()
        #until everything is fixed we're just going to fetch all teams
        #TODO: eventually the fetching 3rd party data and storing it in the database will be gone
        ret = RetrieveData( teamIds )
        return ret
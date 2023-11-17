import datetime
from flask_restx import Namespace, Resource, fields
from common import FetchJson, GetDate, GetDateString
import os
import models
from sqlalchemy.orm import sessionmaker


# ~~~~~ SCHEDULE ~~~~~
# https://api-web.nhle.com/v1/schedule/2023-11-07 # includes teams and odds

#TODO: separate games, from teams, from schedule and fetch data from local
#database.  Done this way because the source data is fetched at each request
#instead of regularly fetching the data and applying it to a local database
#and then having the app API use the local database, implement models, etc.
#This is not required for the initial version and would be a refactoring of the
#existing code when these features are required.  The next iteration of this
#API would only store the raw NHL results in a database and not make NHL API
#requests on every request.  However the userbase is not large enough to
#warrant this dev time.

SCHEDULE_BASE_URL = os.getenv( 'SCHEDULE_BASE_URL' )

def FilterGames( games ):
    filteredGames = []
    for game in games:
        filteredGames.append( FilterGame( game ) )
    return filteredGames

#TODO: take the filter pattern and genericize the function

def FilterGame( game ):
    gameKeys = [ 'homeTeam', 'awayTeam' ]
    return { key: FilterTeam( game[ key ] ) for key in gameKeys }

# filter a team so only the ID and name come back also flatten out object as
# team is the only key that we keep
def FilterTeam( team ):
    teamKeys = [ "id", "abbrev" ]
    return { key: team[ key ] for key in teamKeys }

# fetch and filter raw NHL data
def FetchSchedule():
    today = GetDateString()
    scheduleJson = FetchJson( f'{SCHEDULE_BASE_URL}/{today}' )
    filteredGames = []
    for todaysGames in scheduleJson['gameWeek']:
        if todaysGames['date'] == today:
            filteredGames = FilterGames( todaysGames[ 'games' ] )
    return filteredGames

# dev debug, usually FetchScheudle would be use by the route code which is the
# publicly availabel API flask 
# FetchSchedule()

#TODO: update to new api
def CheckIfDataExists():
    Session = sessionmaker( models.engine )
    today = GetDateString()
    with Session() as session:
        exists = session.query( models.Schedule ).filter_by( game_date=today ).first() is not None
    return exists

def GetTeamName( teamId, teamsData ):
    for team in teamsData:
        if team.id == teamId:
            return team.name
    #should be impossible - potential if new team is created/renamed
    #this potentian should be resolved once the team data is fetched.
    #the team save will have to check each team individually whereas
    #schedule data SHOULD be able to assume that if some schedule data
    #exists, it all exists - terrible assumption but we'll got with it
    #for now
    return 'Team Name Not Found'
#TODO: update to new api/schema
def RetrieveData():
    today = GetDate()
    Session = sessionmaker( models.engine )
    data = []
    with Session() as session:
        scheduleQuery = session.query( models.Schedule ).filter_by( game_date=today )
        scheduleResult = session.execute( scheduleQuery )
        for datum in scheduleResult.scalars():
            teamIds = ( datum.away_id, datum.home_id )
            teamQuery = session.query( models.Team ).filter(models.Team.id.in_( teamIds ) )
            teamResult = session.execute( teamQuery )
            teamResultData = teamResult.scalars()
            awayName = GetTeamName( datum.away_id, teamResultData )
            homeName = GetTeamName( datum.home_id, teamResultData )
            data.append(
                {
                    'teams':{
                        'away':{
                            'id':datum.away_id,
                            'name':awayName
                        },
                        'home': {
                            'id':datum.home_id,
                            'name':homeName
                        }
                    }
                }
            )
    return data

api = Namespace( "schedule" )
#TODO: clean up NHL API fetching and database writing functions - once data scraper is schedule
@api.route("/")
class Schedule( Resource ):
    def get( self ):
        ret = []
        ret = FetchSchedule()
        #TODO: reimplement
        return ret
from dotenv import load_dotenv
load_dotenv('.env')

from common import GetDateString, FetchJson
import os

SCHEDULE_BASE_URL = os.getenv( 'SCHEDULE_BASE_URL' )

# fetch and filter raw NHL data
def FetchSchedule():
    today = GetDateString()
    scheduleJson = FetchJson( f'{SCHEDULE_BASE_URL}/{today}' )
    filteredGames = []
    for todaysGames in scheduleJson['gameWeek']:
        if todaysGames['date'] == today:
            filteredGames = FilterGames( todaysGames[ 'games' ] )
    return filteredGames

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

#TODO: separate games, from teams, from schedule and fetch data from local
#database.  Done this way because the source data is fetched at each request
#instead of regularly fetching the data and applying it to a local database
#and then having the app API use the local database, implement models, etc.
#This is not required for the initial version and would be a refactoring of the
#existing code when these features are required.  The next iteration of this
#API would only store the raw NHL results in a database and not make NHL API
#requests on every request.  However the userbase is not large enough to
#warrant this dev time.

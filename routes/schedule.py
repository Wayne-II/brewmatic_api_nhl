import datetime
from flask_restx import Namespace, Resource, fields
from common import FetchJson

#TODO: separate games, from teams, from schedule and fetch data from local
#database.  Done this way because the source data is fetched at each request
#instead of regularly fetching the data and applying it to a local database
#and then having the app API use the local database, implement models, etc.
#This is not required for the initial version and would be a refactoring of the
#existing code when these features are required.  The next iteration of this
#API would only store the raw NHL results in a database and not make NHL API
#requests on every request.  However the userbase is not large enough to
#warrant this dev time.

baseUrl = "https://statsapi.web.nhl.com/api/v1/schedule"

def GetDate():
    return datetime.date.today().strftime("%Y-%m-%d")

def FilterGames( games ):
    filteredGames = []
    for game in games:
        filteredGames.append( FilterGame( game ) )
    return filteredGames

#TODO: take the filter pattern and genericize the function

def FilterGame( game ):
    gameKeys = [ 'teams' ]
    return { key: FilterTeams( game[ key ] ) for key in gameKeys } 

# filter a games teatms so only home and away are returned as the meta data is
# not required
def FilterTeams( teams ):
    teamsKeys = [ 'away', 'home' ]
    return { key: FilterTeam( teams[ key ] ) for key in teamsKeys }

# filter a team so only the ID and name come back also flatten out object as
# team is the only key that we keep
def FilterTeam( team ):
    teamKeys = [ "id", "name" ]
    return { key: team[ 'team' ][ key ] for key in teamKeys }

# fetch and filter raw NHL data
def FetchSchedule():
    today = GetDate()
    scheduleJson = FetchJson( baseUrl + "?date=" + today )
    filteredGames = []
    for gameDate in scheduleJson['dates']:
        if gameDate['date'] == today:
            filteredGames = FilterGames( gameDate[ 'games' ] )
    return filteredGames

# dev debug, usually FetchScheudle would be use by the route code which is the
# publicly availabel API flask 
# FetchSchedule()

api = Namespace( "schedule" )

@api.route("/")
class Schedule( Resource ):
    def get( self ):
        return FetchSchedule()

##################################
# NHL API INFO FOR THIS ENDPOINT #
##################################
# Filtered output example
# {
#     "games" : [ {
#       "teams" : {
#         "away" : {
#             "id" : 5,
#             "name" : "Pittsburgh Penguins"
#         },
#         "home" : {
#             "id" : 9,
#             "name" : "Ottawa Senators"
#         }
#       }
#     }, ... ]
# }

# https://statsapi.web.nhl.com/api/v1/schedule
# ?date=YYYY-MM-DD
# RAW RESPONSE EXAMPLE
# {
#   "copyright" : "NHL and the NHL Shield are registered trademarks of the National Hockey League. NHL and NHL team marks are the property of the NHL and its teams. © NHL 2023. All Rights Reserved.",
#   "totalItems" : 5,
#   "totalEvents" : 0,
#   "totalGames" : 5,
#   "totalMatches" : 0,
#   "metaData" : {
#     "timeStamp" : "20230118_205351"
#   },
#   "wait" : 10,
#   "dates" : [ {
#     "date" : "2023-01-18",
#     "totalItems" : 5,
#     "totalEvents" : 0,
#     "totalGames" : 5,
#     "totalMatches" : 0,
#     "games" : [ {
#       "gamePk" : 2022020712,
#       "link" : "/api/v1/game/2022020712/feed/live",
#       "gameType" : "R",
#       "season" : "20222023",
#       "gameDate" : "2023-01-19T00:00:00Z",
#       "status" : {
#         "abstractGameState" : "Preview",
#         "codedGameState" : "1",
#         "detailedState" : "Scheduled",
#         "statusCode" : "1",
#         "startTimeTBD" : false
#       },
#       "teams" : {
#         "away" : {
#           "leagueRecord" : {
#             "wins" : 22,
#             "losses" : 15,
#             "ot" : 6,
#             "type" : "league"
#           },
#           "score" : 0,
#           "team" : {
#             "id" : 5,
#             "name" : "Pittsburgh Penguins",
#             "link" : "/api/v1/teams/5"
#           }
#         },
#         "home" : {
#           "leagueRecord" : {
#             "wins" : 19,
#             "losses" : 21,
#             "ot" : 3,
#             "type" : "league"
#           },
#           "score" : 0,
#           "team" : {
#             "id" : 9,
#             "name" : "Ottawa Senators",
#             "link" : "/api/v1/teams/9"
#           }
#         }
#       },
#       "venue" : {
#         "id" : 5031,
#         "name" : "Canadian Tire Centre",
#         "link" : "/api/v1/venues/5031"
#       },
#       "content" : {
#         "link" : "/api/v1/game/2022020712/content"
#       }
#     }, ... ],
#     "events" : [ ],
#     "matches" : [ ]
#   } ]
# }

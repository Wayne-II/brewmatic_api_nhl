import requests
import json
import datetime

baseUrl = "https://statsapi.web.nhl.com/api/v1/schedule"

def GetDate():
    return datetime.date.today().strftime("%Y-%m-%d")

def FilterGames( games ):
    filteredGames = []
    for game in games:
        filteredGames.append( FilterGame( game ) )
    return filteredGames

def FilterGame( game ):
    gameKeys = [ 'teams' ]
    return { key: FilterTeams( game[ key ] ) for key in gameKeys } 

def FilterTeams( teams ):
    teamsKeys = [ 'away', 'home' ]
    return { key: FilterTeam( teams[ key ] ) for key in teamsKeys }

def FilterTeam( team ):
    teamKeys = [ "id", "name" ]
    return { key: team[ 'team' ][ key ] for key in teamKeys }

def FetchJson( url ):
    response = requests.get( url )
    return response.json()

def FetchSchedule():
    today = GetDate()
    scheduleJson = FetchJson( baseUrl + "?date=" + today )
    filteredGames = []
    for gameDate in scheduleJson['dates']:
        if gameDate['date'] == today:
            filteredGames = FilterGames( gameDate[ 'games' ] )
    print( filteredGames )
            
                

# dev debug, usually FetchScheudle would be use by the route code which is the
# publicly availabel API flask 
FetchSchedule()

##################################
# NHL API INFO FOR THIS ENDPOINT #
##################################
# Filtered output example
# {
#     "games" : [ {
#       "teams" : {
#         "away" : {
#           "team" : {
#             "id" : 5,
#             "name" : "Pittsburgh Penguins"
#           }
#         },
#         "home" : {
#           "team" : {
#             "id" : 9,
#             "name" : "Ottawa Senators"
#           }
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

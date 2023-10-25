# https://statsapi.web.nhl.com/api/v1/teams
# https://statsapi.web.nhl.com/api/v1/teams/ID
# https://statsapi.web.nhl.com/api/v1/teams/ID?expand=team.roster
# https://statsapi.web.nhl.com/api/v1/teams?teamId=<id,list,comma,separated>&expand=team.roster

# this endpoint is only required to get the translation between team name and 3
# character code EG TOR for Toronto Maple Leafs

import requests
import datetime

from flask_restx import Namespace, Resource, fields
from common import FetchJson
from os import getenv

TEAMS_BASE_URL = getenv( 'TEAMS_BASE_URL' )

# filter the team roster to only include IDs as we need to fetch them using the
# people API in order to get injury status as well as other detailed stats
def FilterTeamRoster( roster ):
    filteredRoster = []
    for person in roster:
        filteredRoster.append( person[ 'person' ][ 'id' ] )
    return filteredRoster   

# filter a team to only include the require information.  The datum fileds
# being id, name, abbreviation, and a roster of IDs to fetch detailed info
def FilterTeam( team ):
    teamKeys = [ 'id', 'name', 'abbreviation' ]
    roster = FilterTeamRoster( team[ 'roster' ][ 'roster' ] )
    filteredTeam = { key: team[ key ] for key in teamKeys }
    filteredTeam[ 'roster' ] = roster
    return filteredTeam

#filter the raw teams data so that only required information is required
def FilterTeams( teams ):  
    filteredTeams = []
    for team in teams:
        filteredTeams.append( FilterTeam( team ) )
    return filteredTeams

# fetch the raw data and filter
def FetchTeams( teamIds ):
    teamIdsStringList = [ str( id ) for id in teamIds ]
    requestUrl = '%s?teamId=%s&expand=team.roster' % ( TEAMS_BASE_URL, ','.join( teamIdsStringList ) )
    teamsJson = FetchJson( requestUrl )
    return FilterTeams( teamsJson[ 'teams' ] )

api = Namespace( "teams" )

id_parser = api.parser()
id_parser.add_argument('id', type=int, action='split')

@api.route("/")
@api.doc( params={ 'id':'Team IDs' } )
class Teams( Resource ):
    def get( self ):
        args = id_parser.parse_args()
        return FetchTeams( args[ 'id' ] )

##################################
# NHL API INFO FOR THIS ENDPOINT #
##################################
# Filtered output example
##################################
# {
#   "teams" : [ {
#     "id" : 9,
#     "name" : "Ottawa Senators",
#     "abbreviation" : "OTT",
#     "teamName" : "Senators",
#     "roster" : [ 8477353,...]
#   } ]
# }

##################################
# RAW NHL API OUTPUT             #
# https://statsapi.web.nhl.com/api/v1/teams/<id>?expand=team.roster
##################################
# {
#   "copyright" : "NHL and the NHL Shield are registered trademarks of the National Hockey League. NHL and NHL team marks are the property of the NHL and its teams. © NHL 2023. All Rights Reserved.",
#   "teams" : [ {
#     "id" : 9,
#     "name" : "Ottawa Senators",
#     "link" : "/api/v1/teams/9",
#     "venue" : {
#       "id" : 5031,
#       "name" : "Canadian Tire Centre",
#       "link" : "/api/v1/venues/5031",
#       "city" : "Ottawa",
#       "timeZone" : {
#         "id" : "America/New_York",
#         "offset" : -5,
#         "tz" : "EST"
#       }
#     },
#     "abbreviation" : "OTT",
#     "teamName" : "Senators",
#     "locationName" : "Ottawa",
#     "firstYearOfPlay" : "1990",
#     "division" : {
#       "id" : 17,
#       "name" : "Atlantic",
#       "nameShort" : "ATL",
#       "link" : "/api/v1/divisions/17",
#       "abbreviation" : "A"
#     },
#     "conference" : {
#       "id" : 6,
#       "name" : "Eastern",
#       "link" : "/api/v1/conferences/6"
#     },
#     "franchise" : {
#       "franchiseId" : 30,
#       "teamName" : "Senators",
#       "link" : "/api/v1/franchises/30"
#     },
#     "roster" : {
#       "roster" : [ {
#         "person" : {
#           "id" : 8477353,
#           "fullName" : "Tyler Motte",
#           "link" : "/api/v1/people/8477353"
#         },
#         "jerseyNumber" : "14",
#         "position" : {
#           "code" : "L",
#           "name" : "Left Wing",
#           "type" : "Forward",
#           "abbreviation" : "LW"
#         }
#       }, {
#         "person" : {
#           "id" : 8478078,
#           "fullName" : "Rourke Chartier",
#           "link" : "/api/v1/people/8478078"
#         },
#         "jerseyNumber" : "67",
#         "position" : {
#           "code" : "C",
#           "name" : "Center",
#           "type" : "Forward",
#           "abbreviation" : "C"
#         }
#       }, {
#         "person" : {
#           "id" : 8479458,
#           "fullName" : "Nikita Zaitsev",
#           "link" : "/api/v1/people/8479458"
#         },
#         "jerseyNumber" : "22",
#         "position" : {
#           "code" : "D",
#           "name" : "Defenseman",
#           "type" : "Defenseman",
#           "abbreviation" : "D"
#         }
#       }, {
#         "person" : {
#           "id" : 8482245,
#           "fullName" : "Artem Zub",
#           "link" : "/api/v1/people/8482245"
#         },
#         "jerseyNumber" : "2",
#         "position" : {
#           "code" : "D",
#           "name" : "Defenseman",
#           "type" : "Defenseman",
#           "abbreviation" : "D"
#         }
#       }, {
#         "person" : {
#           "id" : 8473512,
#           "fullName" : "Claude Giroux",
#           "link" : "/api/v1/people/8473512"
#         },
#         "jerseyNumber" : "28",
#         "position" : {
#           "code" : "R",
#           "name" : "Right Wing",
#           "type" : "Forward",
#           "abbreviation" : "RW"
#         }
#       }, {
#         "person" : {
#           "id" : 8473544,
#           "fullName" : "Derick Brassard",
#           "link" : "/api/v1/people/8473544"
#         },
#         "jerseyNumber" : "61",
#         "position" : {
#           "code" : "C",
#           "name" : "Center",
#           "type" : "Forward",
#           "abbreviation" : "C"
#         }
#       }, {
#         "person" : {
#           "id" : 8474207,
#           "fullName" : "Nick Holden",
#           "link" : "/api/v1/people/8474207"
#         },
#         "jerseyNumber" : "5",
#         "position" : {
#           "code" : "D",
#           "name" : "Defenseman",
#           "type" : "Defenseman",
#           "abbreviation" : "D"
#         }
#       }, {
#         "person" : {
#           "id" : 8474612,
#           "fullName" : "Travis Hamonic",
#           "link" : "/api/v1/people/8474612"
#         },
#         "jerseyNumber" : "23",
#         "position" : {
#           "code" : "D",
#           "name" : "Defenseman",
#           "type" : "Defenseman",
#           "abbreviation" : "D"
#         }
#       }, {
#         "person" : {
#           "id" : 8475660,
#           "fullName" : "Cam Talbot",
#           "link" : "/api/v1/people/8475660"
#         },
#         "jerseyNumber" : "33",
#         "position" : {
#           "code" : "G",
#           "name" : "Goalie",
#           "type" : "Goalie",
#           "abbreviation" : "G"
#         }
#       }, {
#         "person" : {
#           "id" : 8475766,
#           "fullName" : "Austin Watson",
#           "link" : "/api/v1/people/8475766"
#         },
#         "jerseyNumber" : "16",
#         "position" : {
#           "code" : "L",
#           "name" : "Left Wing",
#           "type" : "Forward",
#           "abbreviation" : "LW"
#         }
#       }, {
#         "person" : {
#           "id" : 8476341,
#           "fullName" : "Anton Forsberg",
#           "link" : "/api/v1/people/8476341"
#         },
#         "jerseyNumber" : "31",
#         "position" : {
#           "code" : "G",
#           "name" : "Goalie",
#           "type" : "Goalie",
#           "abbreviation" : "G"
#         }
#       }, {
#         "person" : {
#           "id" : 8478469,
#           "fullName" : "Thomas Chabot",
#           "link" : "/api/v1/people/8478469"
#         },
#         "jerseyNumber" : "72",
#         "position" : {
#           "code" : "D",
#           "name" : "Defenseman",
#           "type" : "Defenseman",
#           "abbreviation" : "D"
#         }
#       }, {
#         "person" : {
#           "id" : 8478472,
#           "fullName" : "Mathieu Joseph",
#           "link" : "/api/v1/people/8478472"
#         },
#         "jerseyNumber" : "21",
#         "position" : {
#           "code" : "R",
#           "name" : "Right Wing",
#           "type" : "Forward",
#           "abbreviation" : "RW"
#         }
#       }, {
#         "person" : {
#           "id" : 8479337,
#           "fullName" : "Alex DeBrincat",
#           "link" : "/api/v1/people/8479337"
#         },
#         "jerseyNumber" : "12",
#         "position" : {
#           "code" : "R",
#           "name" : "Right Wing",
#           "type" : "Forward",
#           "abbreviation" : "RW"
#         }
#       }, {
#         "person" : {
#           "id" : 8479580,
#           "fullName" : "Dylan Gambrell",
#           "link" : "/api/v1/people/8479580"
#         },
#         "jerseyNumber" : "27",
#         "position" : {
#           "code" : "C",
#           "name" : "Center",
#           "type" : "Forward",
#           "abbreviation" : "C"
#         }
#       }, {
#         "person" : {
#           "id" : 8480064,
#           "fullName" : "Josh Norris",
#           "link" : "/api/v1/people/8480064"
#         },
#         "jerseyNumber" : "9",
#         "position" : {
#           "code" : "C",
#           "name" : "Center",
#           "type" : "Forward",
#           "abbreviation" : "C"
#         }
#       }, {
#         "person" : {
#           "id" : 8480073,
#           "fullName" : "Erik Brannstrom",
#           "link" : "/api/v1/people/8480073"
#         },
#         "jerseyNumber" : "26",
#         "position" : {
#           "code" : "D",
#           "name" : "Defenseman",
#           "type" : "Defenseman",
#           "abbreviation" : "D"
#         }
#       }, {
#         "person" : {
#           "id" : 8480208,
#           "fullName" : "Drake Batherson",
#           "link" : "/api/v1/people/8480208"
#         },
#         "jerseyNumber" : "19",
#         "position" : {
#           "code" : "R",
#           "name" : "Right Wing",
#           "type" : "Forward",
#           "abbreviation" : "RW"
#         }
#       }, {
#         "person" : {
#           "id" : 8480355,
#           "fullName" : "Mark Kastelic",
#           "link" : "/api/v1/people/8480355"
#         },
#         "jerseyNumber" : "47",
#         "position" : {
#           "code" : "C",
#           "name" : "Center",
#           "type" : "Forward",
#           "abbreviation" : "C"
#         }
#       }, {
#         "person" : {
#           "id" : 8480448,
#           "fullName" : "Parker Kelly",
#           "link" : "/api/v1/people/8480448"
#         },
#         "jerseyNumber" : "45",
#         "position" : {
#           "code" : "L",
#           "name" : "Left Wing",
#           "type" : "Forward",
#           "abbreviation" : "LW"
#         }
#       }, {
#         "person" : {
#           "id" : 8480801,
#           "fullName" : "Brady Tkachuk",
#           "link" : "/api/v1/people/8480801"
#         },
#         "jerseyNumber" : "7",
#         "position" : {
#           "code" : "L",
#           "name" : "Left Wing",
#           "type" : "Forward",
#           "abbreviation" : "LW"
#         }
#       }, {
#         "person" : {
#           "id" : 8480879,
#           "fullName" : "Jacob Bernard-Docker",
#           "link" : "/api/v1/people/8480879"
#         },
#         "jerseyNumber" : "24",
#         "position" : {
#           "code" : "D",
#           "name" : "Defenseman",
#           "type" : "Defenseman",
#           "abbreviation" : "D"
#         }
#       }, {
#         "person" : {
#           "id" : 8481596,
#           "fullName" : "Shane Pinto",
#           "link" : "/api/v1/people/8481596"
#         },
#         "jerseyNumber" : "57",
#         "position" : {
#           "code" : "C",
#           "name" : "Center",
#           "type" : "Forward",
#           "abbreviation" : "C"
#         }
#       }, {
#         "person" : {
#           "id" : 8482105,
#           "fullName" : "Jake Sanderson",
#           "link" : "/api/v1/people/8482105"
#         },
#         "jerseyNumber" : "85",
#         "position" : {
#           "code" : "D",
#           "name" : "Defenseman",
#           "type" : "Defenseman",
#           "abbreviation" : "D"
#         }
#       }, {
#         "person" : {
#           "id" : 8482116,
#           "fullName" : "Tim Stützle",
#           "link" : "/api/v1/people/8482116"
#         },
#         "jerseyNumber" : "18",
#         "position" : {
#           "code" : "L",
#           "name" : "Left Wing",
#           "type" : "Forward",
#           "abbreviation" : "LW"
#         }
#       } ],
#       "link" : "/api/v1/teams/9/roster"
#     },
#     "shortName" : "Ottawa",
#     "officialSiteUrl" : "http://www.ottawasenators.com/",
#     "franchiseId" : 30,
#     "active" : true
#   } ]
# }
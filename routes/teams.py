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

TEAMS_BASE_URL = getenv( 'TEAMS_BASE_URL' )

# filter the team roster to only include IDs as we need to fetch them using the
# people API in order to get injury status as well as other detailed stats

#TODO: Filter Roster and Filter Team are being hacked to leverage the new 
#discoveries of the old API that will allow for fetching all data by 
#combining expands.  expanding roster person to see roster status.
#will have to keep track of the skaters without a skaters entry but have a
#roster entry.  will have to save roster status.  keeping list of IDs so it
#continues to work wi=hile I implement it completely.
def FilterTeamRoster( roster ):
    filteredRoster = ([],[])
    rosterKeys = [ 'id', 'rosterStatus' ]
    for person in roster:

        filteredRoster[0].append( person[ 'person' ][ 'id' ] )
        filteredRoster[1].append( { key: person['person'][ key ] for key in rosterKeys } )
    return filteredRoster   

# filter a team to only include the require information.  The datum fileds
# being id, name, abbreviation, and a roster of IDs to fetch detailed info
def FilterTeam( team ):
    teamKeys = [ 'id', 'name', 'abbreviation' ]
    roster = FilterTeamRoster( team[ 'roster' ][ 'roster' ] )
    filteredTeam = { key: team[ key ] for key in teamKeys }
    filteredTeam[ 'rosterStatus' ] = roster[1]
    filteredTeam[ 'roster' ] = roster[0]
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
    #TODO: check if data exists for today locally, if not, fetch it and save
    #it to the database

    requestUrl = f'{TEAMS_BASE_URL}?teamId={",".join( teamIdsStringList )}&expand=team.roster,roster.person'
    teamsJson = FetchJson( requestUrl )
    filteredTeams = FilterTeams( teamsJson[ 'teams' ] )
    return filteredTeams

def StoreRoster( skaterIds, teamId, session ):
    insertData = []
    today = GetDate()
    for skaterId in skaterIds:
        insertData.append( {
            'skater_id': skaterId,
            'team_id': teamId,
            'updated': today
        } )
    insert = GetInsert( session )
    
    insertConflictQuery = insert( 
        models.Roster 
    ).values( 
        insertData 
    ).on_conflict_do_update(
        index_elements=[ 'skater_id' ],
        set_ = {
            'team_id': teamId,
            'updated': today
        }
    )
    return insertConflictQuery

def StoreTeams( teams, session ):
    insertData = []
    for team in teams:
        insertData.append( {
            'id':team[ 'id' ],
            'name':team[ 'name' ],
            'abbreviation':team[ 'abbreviation' ]
        } )
    insert = GetInsert( session )
    insertConflictQuery = insert( 
        models.Team 
    ).values( 
        insertData 
    ).on_conflict_do_nothing(
        index_elements=[ 'id' ]
    )

    return insertConflictQuery

#this is broken
def CheckIfDataExists( teamIds ):
    Session = sessionmaker( models.engine )
    today = GetDateString()
    with Session() as session:
        exists = session.query( models.Roster ).filter_by( updated=today ).first() is not None
    return exists

def StoreData( teamData ):
    #old format
    #"roster" : {
    #   "roster" : [ {
    #     "person" : {
    #       "id" : 8479323,
    #       "fullName" : "Adam Fox",
    #       "link" : "/api/v1/people/8479323"
    #     },
    #     "jerseyNumber" : "23",
    #     "position" : {
    #       "code" : "D",
    #       "name" : "Defenseman",
    #       "type" : "Defenseman",
    #       "abbreviation" : "D"
    #     }
    #   }
    # ]
    #}

    #adding roster.person to expands format RAW
    # "roster" : {
    #   "roster" : [ {
    #     "person" : {
    #       "id" : 8479323,
    #       "fullName" : "Adam Fox",
    #       "link" : "/api/v1/people/8479323",
    #       "firstName" : "Adam",
    #       "lastName" : "Fox",
    #       "primaryNumber" : "23",
    #       "birthDate" : "1998-02-17",
    #       "currentAge" : 25,
    #       "birthCity" : "Jericho",
    #       "birthStateProvince" : "NY",
    #       "birthCountry" : "USA",
    #       "nationality" : "USA",
    #       "height" : "5' 11\"",
    #       "weight" : 185,
    #       "active" : true,
    #       "alternateCaptain" : true,
    #       "captain" : false,
    #       "rookie" : false,
    #       "shootsCatches" : "R",
    #       "rosterStatus" : "I",
    #       "currentTeam" : {
    #         "id" : 3,
    #         "name" : "New York Rangers",
    #         "link" : "/api/v1/teams/3"
    #       },
    #       "primaryPosition" : {
    #         "code" : "D",
    #         "name" : "Defenseman",
    #         "type" : "Defenseman",
    #         "abbreviation" : "D"
    #       }
    #     },
    #     "jerseyNumber" : "23",
    #     "position" : {
    #       "code" : "D",
    #       "name" : "Defenseman",
    #       "type" : "Defenseman",
    #       "abbreviation" : "D"
    #     }
    #   },
    Session = sessionmaker( models.engine )
    with Session() as session:
        teamsInsert = StoreTeams( teamData, session )
        session.execute( teamsInsert )
        for team in teamData:
            rosterInsert = StoreRoster( 
                skaterIds = team[ 'roster' ], 
                teamId = team[ 'id' ],
                session = session
            )
            session.execute( rosterInsert )
        session.commit()

def RetrieveData( teamIds ):
    Session = sessionmaker( models.engine )
    ret = []
    with Session() as session:
        teamQuery = session.query( 
            models.Team 
        ).filter(
            models.Team.id.in_( teamIds ) 
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
                'id': team.id,
                'name': team.name,
                'abbreviation': team.abbreviation,
                'roster': roster
            } )
    return ret

api = Namespace( "teams" )

id_parser = api.parser()
id_parser.add_argument('id', type=int, action='split')

@api.route("/")
@api.doc( params={ 'id':'Team IDs' } )
class Teams( Resource ):
    def get( self ):
        args = id_parser.parse_args()
        ret = []
        teamIds = args[ 'id' ]
        #if not database data, fetch from NHL and store in DB otherwise DB
        if not CheckIfDataExists( teamIds ):
            ret = FetchTeams( teamIds )
            StoreData( ret )
        else:
            ret = RetrieveData( teamIds )
        return ret

##################################
# NHL API INFO FOR THIS ENDPOINT #
##################################
# Filtered output example
##################################
# [ {
#     "id" : 9,
#     "name" : "Ottawa Senators",
#     "abbreviation" : "OTT",
#     "roster" : [ 8477353,...]
#   } ]

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
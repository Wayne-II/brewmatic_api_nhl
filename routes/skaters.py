from flask_restx import Namespace, Resource, fields
from common import FetchJson, GetInsert, GetDate, GetDateString
import math
from os import getenv
from sqlalchemy.orm import sessionmaker
import models

#TODO: There appears to be an issue with players which don't have stats not
#showing up in the new API as the new api only returs the person if they have
#active stats for the requested season.  Eg.  Toronto Jake Muzzins, is still
#listed in the roster for 20232024 season but has retired and is a pro-scout.
#Similaarly, Conor Timmins, also on Toronto, has been out with an upper body
#injury which is is still recovering from the following season.

#TODO: update NHL API for skaters to use new API as multiple people can be
# fetched all at once up to 100 at a time.  One request per game scheduled 
# should result in minimal server requests and quicker loading time.  Once data
# is fetched, it should be stored locally and checked against the database 
# before a request is sent to NHL - to avoid being banned 
# the following url fetches the stats for 2 players with this part being the part that needs to be modified "playerId%20in%20%288478402,8478403%29"
# which translates to SQL query where clause part "playerId in (8478402,8478403)"
# https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22goals%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22%7D,%7B%22property%22:%22playerId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=334&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId%3E=2%20and%20playerId%20in%20%288478402,8478403%29%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023

#TODO: revert to old API as there's a way to get the entire schedule, teams,
#roster, skaters, and stats in a single request using the old api.
newBase = "https://api.nhle.com/stats/rest/en/skater/summary"
params = {
    'isAggregate':'false',
    'isGame':'false',
    'sort': [
        {
            "property":"goals"
            ,"direction":"DESC"
        },{
            "property":"points",
            "direction":"DESC"
        },{
            "property":"gamesPlayed",
            "direction":"ASC"
        },{
            "property":"playerId"
            ,"direction":"ASC"
        }
    ],
    'start':0,
    'limit':334,
    'factCayenneExp':'gamesPlayed>=1',
    'cayenneExp':'gameTypeId>=2 and playerId in (%PLAYERIDS%) and seasonId<=%SEASON% and seasonId>=%SEASON%'
}
# URI Encodings
# %3C = <
# %3E = >
# %5B = [
# %5D = ]
# %7B = {
# %7D = }
# %22 = "
# %28 = (
# %29 = )
#OLD v1 API - limits one player stats per request - new API allows up to 100
#baseUrl = "https://statsapi.web.nhl.com/api/v1/people"

seasonEndYear = 2024#TODO move to env
SKATER_BASE_URL = getenv( 'SKATER_BASE_URL' )
#baseUrl = 'https://api.nhle.com/stats/rest/en/skater/summary?gameTypeId=2 and playerId in (%s) and seasonId<=%s and seasonId>=%s'
#TODO: move season end year to request or configuration - maybe computed based
# on month/year 


# filter skater to only the required information
def FilterSkater( skater ):
    #old api stats will be used once names scanned as there's no roster status
    # which is used in order to tell if they're playing, playing limited ( scrateched )
    # or out due to injury/other  Because only one player's stats can be fetched at a time
    # the old API will not be used for all the players for the games for the given day
    #skaterKeys = [ 'id', 'firstName', 'lastName', 'fullName', 'rosterStatus' ]
    skaterKeys = [ 'playerId', 'lastName', 'skaterFullName' ]
    return { key: skater[ key ] for key in skaterKeys }

# filter stats so that only goals are returned
def FilterStats( stats ):
    statsKeys=[ 'goals' ]
    return { key: stats[ key ] if key in stats else 0 for key in statsKeys }

def buildRequestCount( skaterCount, queryLimitMultiplier ):
    return math.ceil( skaterCount / queryLimitMultiplier)

def buildSeasonYears():
    return [ str(seasonEndYear - 1), str(seasonEndYear) ]

def buildSeasonId():
    seasonYears = buildSeasonYears()
    return ''.join(seasonYears)

def GenerateSkaterQueryUrls( skaterIds ):
    queryLimitMultiplier = 100
    skaterCount = len(skaterIds )
    requestCount = buildRequestCount( skaterCount, queryLimitMultiplier )
    queries = []#TODO: queries = buildQueries()
    seasonId = buildSeasonId()

    for i in range( requestCount ):#337 skaters would be range(4) 0, 1, 2, 3 for 0-100, 101-200, 201-300, 301-337
        querySkaterIdsStart = i * queryLimitMultiplier
        querySkaterIdsEnd = ( i + 1 ) * queryLimitMultiplier
        if querySkaterIdsEnd >= skaterCount:
            querySkaterIdsEnd = skaterCount
        querySkaterIds = ','.join( [ str(id) for id in skaterIds[ querySkaterIdsStart : querySkaterIdsEnd ] ] )
        query = f'{SKATER_BASE_URL}?start={querySkaterIdsStart}&limit={queryLimitMultiplier}&cayenneExp=gamesPlayed>=0 and gameTypeId>=2 and playerId in ({querySkaterIds}) and seasonId={seasonId}'

        # t='https://api.nhle.com/stats/rest/en/skater/summary?start=0&limit=100&cayenneExp=gamesPlayed>=0 and gameTypeId>=2 and playerId in (8479982) and seasonId=20232024 and rosterStatus in ( "Y", "I" )' % (querySkaterIdsStart, queryLimitMultiplier, querySkaterIds , seasonId )

        queries.append( query )
    return queries

# fetch the raw data and filter
def FetchSkaters( skaterIds ):
    skaters = []
    seasonString = str( seasonEndYear - 1 ) + str( seasonEndYear )


    queries = GenerateSkaterQueryUrls( skaterIds )
    for requestUrl in queries:
        statsJson = FetchJson( requestUrl )
        #TODO: it appears some players do not have stats yet - seems to be a rookie thing, maybe goalies
        skaters = skaters + statsJson[ 'data' ]
    return skaters

def CheckIfDataExists( skaterIds ):
    Session = sessionmaker( models.engine )
    today = GetDate()
    exists = False
    with Session() as session:
        skaterIdsQuery = session.query( 
            models.Skater
        ).filter(
            models.Skater.id.in_( skaterIds ),
            models.Skater.updated == today
        )

        skaterIdsResults = session.scalars( skaterIdsQuery ).all()
        exists = len( skaterIdsResults ) > 0
    return exists

def StoreSkatersQuery( skaters, session ):
    insertData = []
    today = GetDate()

    for skater in skaters:
        insertData.append( {
            'id':skater[ 'playerId' ],
            'skater_full_name':skater[ 'skaterFullName' ],
            'goals':skater[ 'goals' ],
            'last_name': skater[ 'lastName' ],
            'updated': today,
            'team_abbrevs': skater[ 'teamAbbrevs' ]
        } )

    insert = GetInsert( session )

    insertQuery = insert( 
        models.Skater 
    ).values( 
        insertData 
    )
    
    insertConflictQuery = insertQuery.on_conflict_do_update(
        index_elements=[ 'id' ],
        set_ = {
            'goals': insertQuery.excluded.goals,
            'updated': today,
            #TODO: used for now as UI depends on it.  will fix UI
            'team_abbrevs':insertQuery.excluded.team_abbrevs
        }
    )
    
    return insertConflictQuery

def StoreData( skaterData ):
    Session = sessionmaker( models.engine )
    with Session() as session:
        skatersInsert = StoreSkatersQuery( skaterData, session )
        session.execute( skatersInsert )
        session.commit()

def RetrieveData( skaterIds ):
    Session = sessionmaker( models.engine )
    ret = []
    with Session() as session:
        skatersQuery = session.query( 
            models.Skater
        ).filter(
            models.Skater.id.in_( skaterIds ) 
        )
        
        skatersResults = session.scalars( skatersQuery ).all()
        
        for skater in skatersResults:
            ret.append( {
                'playerId': skater.id,
                'skaterFullName': skater.skater_full_name,
                'goals': skater.goals,
                'lastName': skater.last_name,
                'teamAbbrevs':skater.team_abbrevs
            } )
    return ret

api = Namespace( "skaters" )

id_parser = api.parser()
id_parser.add_argument('id', type=int, action='split')

@api.route("/")
@api.doc(params={"id": "Skater IDs - comma delimited list"})
class Skaters( Resource ):
    def get( self ):
        args = id_parser.parse_args()
        return FetchSkaters( args[ 'id' ] )
    
    def get( self ):
        args = id_parser.parse_args()
        ret = []
        skaterIds = args[ 'id' ]
        #if not database data, fetch from NHL and store in DB otherwise DB
        if not CheckIfDataExists( skaterIds ):
            ret = FetchSkaters( skaterIds )
            StoreData( ret )
        else:
            ret = RetrieveData( skaterIds )
        return ret

##################################
# NHL API INFO FOR THIS ENDPOINT #
##################################
# Filtered output example
##################################


##################################
# RAW NHL API OUTPUT             #

##################################
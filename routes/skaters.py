from flask_restx import Namespace, Resource, fields
from common import FetchJson
import math

#TODO: update NHL API for skaters to use new API as multiple people can be
# fetched all at once up to 100 at a time.  One request per game scheduled 
# should result in minimal server requests and quicker loading time.  Once data
# is fetched, it should be stored locally and checked against the database 
# before a request is sent to NHL - to avoid being banned 
# the following url fetches the stats for 2 players with this part being the part that needs to be modified "playerId%20in%20%288478402,8478403%29"
# which translates to SQL query where clause part "playerId in (8478402,8478403)"
# https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22goals%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22%7D,%7B%22property%22:%22playerId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=334&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId%3E=2%20and%20playerId%20in%20%288478402,8478403%29%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023

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


#baseUrl = "https://statsapi.web.nhl.com/api/v1/people"

seasonEndYear = 2024


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
        query = 'https://api.nhle.com/stats/rest/en/skater/summary?start=%s&limit=%s&cayenneExp=gamesPlayed>=0 and gameTypeId>=2 and playerId in (%s) and seasonId=%s' % ( querySkaterIdsStart, queryLimitMultiplier, querySkaterIds , seasonId )
        queries.append( query )
    return queries

# fetch the raw data and filter
def FetchSkaters( teamIds ):
    skaters = []
    seasonString = str( seasonEndYear - 1 ) + str( seasonEndYear )


    queries = GenerateSkaterQueryUrls( teamIds)
    for requestUrl in queries:
        
        # requestUrl = baseUrl + '/' + str( skaterId )
        # skaterJson =  FetchJson( requestUrl )
        # filteredSkater = FilterSkater( skaterJson[ 'people' ][ 0 ] )
        # requestUrl = baseUrl + '/' + str( skaterId ) + '/stats?stats=statsSingleSeason&season=' + seasonString
        
        
        statsJson = FetchJson( requestUrl )
        #TODO: it appears some players do not have stats yet - seems to be a rookie thing, maybe goalies
        #FIXME: disbaled the sorting of the data as the data response structure 
        # has changed from apiV1 vs new api
        # try: 
        #     filteredStats = FilterStats( statsJson[ 'stats' ][ 0 ][ 'splits' ][ 0 ][ 'stat' ] )
        #     filteredSkater[ 'goals' ] = filteredStats[ 'goals' ]
        # except:
        #     filteredSkater[ 'goals' ] = 0
        # skaters.append( filteredSkater )
        skaters = skaters + statsJson[ 'data' ]
    return skaters

api = Namespace( "skaters" )

id_parser = api.parser()
id_parser.add_argument('id', type=int, action='split')

@api.route("/")
@api.doc(params={"id": "Skater IDs - comma delimited list"})
class Skaters( Resource ):
    def get( self ):
        args = id_parser.parse_args()
        print( str(args))
        return FetchSkaters( args[ 'id' ] )

##################################
# NHL API INFO FOR THIS ENDPOINT #
##################################
# Filtered output example
##################################


##################################
# RAW NHL API OUTPUT             #

##################################

from flask_restx import Namespace, Resource, fields
from common import FetchJson

#TODO: update NHL API for skaters to use new API as multiple people can be
# fetched all at once up to 100 at a time.  One request per game scheduled 
# should result in minimal server requests and quicker loading time.  Once data
# is fetched, it should be stored locally and checked against the database 
# before a request is sent to NHL - to avoid being banned 
# the following url fetches the stats for 2 players with this part being the part that needs to be modified "playerId%20in%20%288478402,8478403%29"
# which translates to SQL query where clause part "playerId in (8478402,8478403)"
# https://api.nhle.com/stats/rest/en/skater/summary?isAggregate=false&isGame=false&sort=%5B%7B%22property%22:%22goals%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22points%22,%22direction%22:%22DESC%22%7D,%7B%22property%22:%22gamesPlayed%22,%22direction%22:%22ASC%22%7D,%7B%22property%22:%22playerId%22,%22direction%22:%22ASC%22%7D%5D&start=0&limit=334&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId%3E=2%20and%20playerId%20in%20%288478402,8478403%29%20and%20seasonId%3C=20222023%20and%20seasonId%3E=20222023
baseUrl = "https://statsapi.web.nhl.com/api/v1/people"
#TODO: move season end year to request or configuration - maybe computed based
# on month/year 
seasonEndYear = 2024

# filter skater to only the required information
def FilterSkater( skater ):
    skaterKeys = [ 'id', 'firstName', 'lastName', 'fullName', 'rosterStatus' ]
    return { key: skater[ key ] for key in skaterKeys }

# filter stats so that only goals are returned
def FilterStats( stats ):
    statsKeys=[ 'goals' ]
    return { key: stats[ key ] if key in stats else 0 for key in statsKeys }

# fetch the raw data and filter
def FetchSkaters( teamIds ):
    skaters = []
    seasonString = str( seasonEndYear - 1 ) + str( seasonEndYear )
    for skaterId in teamIds:
        requestUrl = baseUrl + '/' + str( skaterId )
        skaterJson =  FetchJson( requestUrl )
        filteredSkater = FilterSkater( skaterJson[ 'people' ][ 0 ] )
        requestUrl = baseUrl + '/' + str( skaterId ) + '/stats?stats=statsSingleSeason&season=' + seasonString
        statsJson = FetchJson( requestUrl )
        #TODO: it ppears some players do not have stats yet - seems to be a rookie thing, maybe goalies
        try: 
            filteredStats = FilterStats( statsJson[ 'stats' ][ 0 ][ 'splits' ][ 0 ][ 'stat' ] )
            filteredSkater[ 'goals' ] = filteredStats[ 'goals' ]
        except:
            filteredSkater[ 'goals' ] = 0
        skaters.append( filteredSkater )
    return skaters

api = Namespace( "skaters" )

id_parser = api.parser()
id_parser.add_argument('id', type=int, action='split')

@api.route("/")
@api.doc(params={"id": "Skater IDs - comma delimited list"})
class Skaters( Resource ):
    def get( self ):
        args = id_parser.parse_args()
        return FetchSkaters( args[ 'id' ] )

##################################
# NHL API INFO FOR THIS ENDPOINT #
##################################
# Filtered output example
##################################


##################################
# RAW NHL API OUTPUT             #

##################################

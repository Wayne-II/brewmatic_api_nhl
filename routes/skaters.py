from flask_restx import Namespace, Resource, fields
from common import FetchJson

baseUrl = "https://statsapi.web.nhl.com/api/v1/people"
#TODO: move season end year to request or configuration - maybe computed based
# on month/year 
seasonEndYear = 2023

# filter skater to only the required information
def FilterSkater( skater ):
    skaterKeys = [ 'id', 'firstName', 'lastName', 'fullName', 'rosterStatus' ]
    print( skater )
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

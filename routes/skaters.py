from flask_restx import Namespace, Resource, fields
from common import FetchJson

baseUrl = "https://statsapi.web.nhl.com/api/v1/people"

# filter skater to only the required information
def FilterSkater( skater ):
    skaterKeys = [ 'id', 'firstName', 'lastName', 'fullName', 'rosterStatus' ]
    print( skater )
    return { key: skater[ key ] for key in skaterKeys }

# fetch the raw data and filter
def FetchSkaters( teamIds ):
    skaters = []
    for skaterId in teamIds:
        requestUrl = baseUrl + '/' + str( skaterId )
        skaterJson =  FetchJson( requestUrl )
        filteredSkater = FilterSkater( skaterJson[ 'people' ][ 0 ] )
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

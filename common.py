import requests
from urllib.parse import urlparse
from urllib.parse import parse_qs

def ExtractParamsFromUrl( url ):
    parsedUrl = urlparse( url )
    return parse_qs( parsedUrl.query )

def GetDataFromDatabase( url ):
    
    params = ExtractParamsFromUrl( url )
    return []

def CheckIfDataExists( url ):
    params = ExtractParamsFromUrl( url )
    table = DetermineTable( url )
    return False

def DetermineRoute( url ):
    parsedUrl = urlparse( url )
    print('check if data exists')
    print( parsedUrl.path )
    match parsedUrl.path:
        case '/api/v1/schedule':
            return 'schedule'
        case '/api/v1/teams':
            return 'teams'
        case '/stats/rest/en/skater/summary':
            return 'skaters'
    return 'TODO: convert route to table name'

def DetermineTable( url ):
    route = DetermineRoute( url )
    pass

def SaveRemoteDataToDatabase( response ):
    DetermineTable( response.url )
    pass

# simplification of requests for the NHL api
def FetchJson( url ):
    #TODO: this is probably the wront place to do this, maybe not.
    #TODO: check database.  if database data is older than today
    #fetch new data and update database
    #Setting up call stack as no-op
    if( CheckIfDataExists( url ) ):
        response = GetDataFromDatabase( url )
        return response
    else:
        response = requests.get( url )
        SaveRemoteDataToDatabase( response )
        return response.json()
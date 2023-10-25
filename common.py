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
        case '_':
            return None#TSK TSK - throw
    return 'TODO: exceptions'#TODO: exceptions

def DetermineTable( url ):
    route = DetermineRoute( url )
    #conveniently routes and tables are named identically.  However, routes
    #will return data from multiple tables due to it's design mimicking
    #the NHL API data structure which would have relations in a database
    #for refrential integrity 
    pass

def SaveSkaters( response ):
    #update skaters data and any related data received from NHL API response
    pass

def SaveTeams( response ):
    #update teams data and any related data received from NHL API response
    pass

def SaveSchedule( response ):
    #update schedule data and any related data received from NHL API response
    pass

def SaveRemoteDataToDatabase( response ):
    table = DetermineTable( response.url )
    match table:
        case 'teams':
            SaveTeams( response )
        case 'schedule':
            SaveSchedule( response )
        case 'skaters':
            SaveSkaters( response )
        case None:
            pass
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
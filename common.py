import requests
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pgsql_insert

def GetInsert( session ):
    return sqlite_insert if session.bind.dialect.name == 'sqlite' else  pgsql_insert

# simplification of requests for the NHL api
def FetchJson( url ):
    return requests.get( url ).json()

#eastern is either -4(EDT)  or -5(EST)
#Eastern because NHL games are mostly based on Eastern.
def GetDateString():
    d = GetDate()
    ret = d.strftime( '%Y-%m-%d' )
    return ret

#offsetHours = -5
offsetName = 'America/New_York'  
def GetDate():
    zone = ZoneInfo( offsetName )
    offsetHours = datetime.datetime.now( zone ).utcoffset()
    td = timedelta( hours = offsetHours )
    dt = datetime.now()
    tz = timezone(td)
    easternDt = dt.astimezone( tz=tz )
    ret = date( easternDt.year, easternDt.month, easternDt.day )
    print( f'Returning {ret}')
    return ret
import requests
import datetime
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pgsql_insert

def GetInsert( session ):
    return sqlite_insert if session.bind.dialect.name == 'sqlite' else  pgsql_insert

# simplification of requests for the NHL api
def FetchJson( url ):
    return requests.get( url ).json()

def GetDateString():
    return datetime.date.today().strftime("%Y-%m-%d")

def GetDate():
    return datetime.date.today()
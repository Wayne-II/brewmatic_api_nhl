import requests
import datetime



# simplification of requests for the NHL api
def FetchJson( url ):
    return requests.get( url ).json()

def GetDateString():
    return datetime.date.today().strftime("%Y-%m-%d")

def GetDate():
    return datetime.date.today()
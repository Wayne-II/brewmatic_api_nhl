import requests



# simplification of requests for the NHL api
def FetchJson( url ):
    return requests.get( url ).json()
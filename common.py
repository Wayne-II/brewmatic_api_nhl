import requests

# simplification of requests for the NHL api
def FetchJson( url ):
    response = requests.get( url )
    return response.json()
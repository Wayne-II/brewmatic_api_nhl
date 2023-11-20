from common import FetchJson
from os import getenv

TEAMS_BASE_URL = getenv( 'TEAMS_BASE_URL' )
TRICODE_BASE_URL = getenv( 'TRICODE_BASE_URL' )
ROSTER_BASE_URL = getenv( 'ROSTER_BASE_URL' )
SEASON_ID = 20232024

# fetch the raw data and filter
def FetchTeams():
    requestUrl = f'{TEAMS_BASE_URL}?cayenneExp=seasonId={SEASON_ID}'
    teamsJson = FetchJson( requestUrl )
    filteredTeams = FilterTeams( teamsJson[ 'data' ] )
    filteredTeams = AddTeamTriCodes( filteredTeams )
    filteredTeams = AddTeamRoster( filteredTeams )
    return filteredTeams

#filter the raw teams data so that only required information is required
def FilterTeams( teams ):  
    filteredTeams = []
    for team in teams:
        filteredTeams.append( FilterTeam( team ) )
    return filteredTeams

# being id, name, abbreviation, and a roster of IDs to fetch detailed info
def FilterTeam( team ):
    teamKeys = [ 'losses', 'otLosses', 'teamFullName', 'teamId', 'ties', 'wins', "winsInRegulation" ]
    filteredTeam = { key: team[ key ] for key in teamKeys }
    return filteredTeam

def AddTeamTriCodes( filteredTeams ):
    teamIds = [ team[ 'teamId' ] for team in filteredTeams ]    
    teamIdsString = ",".join( map( str, teamIds ) )
    requestUrl = f'{TRICODE_BASE_URL}?cayenneExp=id in ( { teamIdsString } )'
    tricodeJson = FetchJson( requestUrl )
    return UpdateFilteredTeamsWithTriCodes( filteredTeams, tricodeJson[ 'data' ] )

def UpdateFilteredTeamsWithTriCodes( filteredTeams, tricodeJson ):
    ret = []
    for team in filteredTeams:
        team[ 'triCode' ] = GetTricodeByTeamId( team[ 'teamId' ], tricodeJson )
        ret.append( team )
    return ret

def GetTricodeByTeamId( teamId, tricodeJson ):
    for team in tricodeJson:
        if team[ 'id' ] == teamId:
            return team[ 'triCode' ]
    return 'NHL'#shouldn't happen TODO exception handling

def AddTeamRoster( filteredTeams ):
    ret = []
    for team in filteredTeams:
        triCode = team[ "triCode" ]
        requestUrl = f'{ROSTER_BASE_URL}/{triCode}/{SEASON_ID}'
        rosterJson = FetchJson( requestUrl )
        team[ 'roster' ] = FilterRoster( rosterJson )
        ret.append( team )
    return ret

def FilterRoster( roster ):  
    filteredRoster = []
    mergedRoster = roster[ 'forwards' ] + roster[ 'defensemen' ] + roster[ 'goalies' ] 
    for skater in mergedRoster:
        filteredRoster.append( skater[ 'id' ] )
    return filteredRoster 
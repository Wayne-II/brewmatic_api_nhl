# https://statsapi.web.nhl.com/api/v1/teams
# https://statsapi.web.nhl.com/api/v1/teams/ID
# https://statsapi.web.nhl.com/api/v1/teams/ID?expand=team.roster
# https://statsapi.web.nhl.com/api/v1/teams?teamId=<id,list,comma,separated>&expand=team.roster

# this endpoint is only required to get the translation between team name and 3
# character code EG TOR for Toronto Maple Leafs

#Tim Horton's puts point awards to accounts before 6AM Eastern.  6AM Eastern
#is probably the best time to automate the check for NHL data as the app will
#likely have the updated information by this time.

import requests
import datetime

from sqlalchemy.orm import sessionmaker
import models

from flask_restx import Namespace, Resource, fields
from common import FetchJson, GetDate, GetDateString, GetInsert
from os import getenv

TEAMS_BASE_URL = getenv( 'TEAMS_BASE_URL' )
SEASON_ID = 20232024#todo add to env

# filter the team roster to only include IDs as we need to fetch them using the
# people API in order to get injury status as well as other detailed stats

#TODO: Filter Roster and Filter Team are being hacked to leverage the new 
#discoveries of the old API that will allow for fetching all data by 
#combining expands.  expanding roster person to see roster status.
#will have to keep track of the skaters without a skaters entry but have a
#roster entry.  will have to save roster status.  keeping list of IDs so it
#continues to work wi=hile I implement it completely.

#TODO: keeping this to get new endpoint that will be required to fetch rosters
def FilterTeamRoster( roster ):
    filteredRoster = ([],[])
    rosterKeys = [ 'id', 'rosterStatus' ]
    for person in roster:

        filteredRoster[0].append( person[ 'person' ][ 'id' ] )
        filteredRoster[1].append( { key: person['person'][ key ] for key in rosterKeys } )
    return filteredRoster   

# filter a team to only include the require information.  The datum fileds
# being id, name, abbreviation, and a roster of IDs to fetch detailed info
def FilterTeam( team ):
    teamKeys = [ 'losses', 'otLosses', 'teamFullName', 'teamId', 'ties', 'wins', "winsInRegulation" ]
    filteredTeam = { key: team[ key ] for key in teamKeys }
    return filteredTeam

#filter the raw teams data so that only required information is required
def FilterTeams( teams ):  
    filteredTeams = []
    for team in teams:
        filteredTeams.append( FilterTeam( team ) )
    return filteredTeams

# fetch the raw data and filter
def FetchTeams(  ):
    requestUrl = f'{TEAMS_BASE_URL}?cayenneExp=seasonId={SEASON_ID}'
    teamsJson = FetchJson( requestUrl )
    filteredTeams = FilterTeams( teamsJson[ 'data' ] )
    return filteredTeams
#TODO update to new api
def StoreRoster( skaterIds, teamId, session ):
    insertData = []
    today = GetDate()
    for skaterId in skaterIds:
        insertData.append( {
            'skater_id': skaterId,
            'team_id': teamId,
            'updated': today
        } )
    insert = GetInsert( session )
    
    insertConflictQuery = insert( 
        models.Roster 
    ).values( 
        insertData 
    ).on_conflict_do_update(
        index_elements=[ 'skater_id' ],
        set_ = {
            'team_id': teamId,
            'updated': today
        }
    )
    return insertConflictQuery
#TODO: update to new api
def StoreTeams( teams, session ):
    insertData = []
    for team in teams:
        insertData.append( {
            'id':team[ 'id' ],
            'name':team[ 'name' ],
            'abbreviation':team[ 'abbreviation' ]
        } )
    insert = GetInsert( session )
    insertConflictQuery = insert( 
        models.Team 
    ).values( 
        insertData 
    ).on_conflict_do_nothing(
        index_elements=[ 'id' ]
    )

    return insertConflictQuery

#TODO: update to new api
def CheckIfDataExists(  ):
    Session = sessionmaker( models.engine )
    today = GetDateString()
    with Session() as session:
        exists = session.query( models.Roster ).filter_by( updated=today ).first() is not None
    return exists
#TODO: update to new api
def StoreData( teamData ):
    Session = sessionmaker( models.engine )
    with Session() as session:
        teamsInsert = StoreTeams( teamData, session )
        session.execute( teamsInsert )
        # for team in teamData:
        #     rosterInsert = StoreRoster( 
        #         skaterIds = team[ 'roster' ], 
        #         teamId = team[ 'id' ],
        #         session = session
        #     )
        #     session.execute( rosterInsert )
        session.commit()
#TODO: update to new api
def RetrieveData(  ):
    Session = sessionmaker( models.engine )
    ret = []
    with Session() as session:
        teamQuery = session.query( 
            models.Team 
        ).filter(
            models.Team.id.in_( teamIds ) 
        )
        
        rosterQuery = session.query( 
            models.Roster
        ).filter(
            models.Roster.team_id.in_( teamIds ) 
        )
        
        teamResults = session.scalars( teamQuery ).all()
        rosterResults = session.scalars( rosterQuery ).all()
        
        for team in teamResults:
            roster = [ roster.skater_id for roster in rosterResults if roster.team_id == team.id ]
            ret.append( {
                'id': team.id,
                'name': team.name,
                'abbreviation': team.abbreviation,
                'roster': roster
            } )
    return ret

api = Namespace( "teams" )

@api.route("/")
class Teams( Resource ):
    def get( self ):
        ret = []
        #until everything is fixed we're just going to fetch all teams
        if not CheckIfDataExists():
            ret = FetchTeams()
            #StoreData( ret )
        else:
            ret = RetrieveData()
        return ret

sample = {
   "data":[
      {
         "faceoffWinPct":0.530935,
         "gamesPlayed":12,
         "goalsAgainst":44,
         "goalsAgainstPerGame":3.66666,
         "goalsFor":46,
         "goalsForPerGame":3.83333,
         "losses":4,
         "otLosses":1,
         "teamFullName":"New Jersey Devils",
         "teamId":1,
         "ties":None,
         "wins":7,
         "winsInRegulation":6,
         "penaltyKillNetPct":0.790697,
         "penaltyKillPct":0.767442,
         "pointPct":0.62500,
         "points":15,
         "powerPlayNetPct":0.395833,
         "powerPlayPct":0.416666,
         "regulationAndOtWins":7,
         "seasonId":20232024,
         "shotsAgainstPerGame":30.91666,
         "shotsForPerGame":33.08333,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.528213,
         "gamesPlayed":11,
         "goalsAgainst":31,
         "goalsAgainstPerGame":2.81818,
         "goalsFor":29,
         "goalsForPerGame":2.63636,
         "losses":3,
         "otLosses":3,
         "penaltyKillNetPct":0.846153,
         "penaltyKillPct":0.794872,
         "pointPct":0.59090,
         "points":13,
         "powerPlayNetPct":0.151515,
         "powerPlayPct":0.151515,
         "regulationAndOtWins":5,
         "seasonId":20232024,
         "shotsAgainstPerGame":35.18181,
         "shotsForPerGame":30.81818,
         "teamFullName":"New York Islanders",
         "teamId":2,
         "ties":None,
         "wins":5,
         "winsInRegulation":5,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.548780,
         "gamesPlayed":12,
         "goalsAgainst":26,
         "goalsAgainstPerGame":2.16666,
         "goalsFor":39,
         "goalsForPerGame":3.25000,
         "losses":2,
         "otLosses":1,
         "penaltyKillNetPct":0.883720,
         "penaltyKillPct":0.860466,
         "pointPct":0.79166,
         "points":19,
         "powerPlayNetPct":0.317073,
         "powerPlayPct":0.341463,
         "regulationAndOtWins":9,
         "seasonId":20232024,
         "shotsAgainstPerGame":27.50000,
         "shotsForPerGame":27.50000,
         "teamFullName":"New York Rangers",
         "teamId":3,
         "ties":None,
         "wins":9,
         "winsInRegulation":7,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.456403,
         "gamesPlayed":13,
         "goalsAgainst":41,
         "goalsAgainstPerGame":3.15384,
         "goalsFor":38,
         "goalsForPerGame":2.92307,
         "losses":7,
         "otLosses":1,
         "penaltyKillNetPct":0.897435,
         "penaltyKillPct":0.794872,
         "pointPct":0.42307,
         "points":11,
         "powerPlayNetPct":0.066666,
         "powerPlayPct":0.088888,
         "regulationAndOtWins":5,
         "seasonId":20232024,
         "shotsAgainstPerGame":26.00000,
         "shotsForPerGame":31.92307,
         "teamFullName":"Philadelphia Flyers",
         "teamId":4,
         "ties":None,
         "wins":5,
         "winsInRegulation":5,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.564102,
         "gamesPlayed":11,
         "goalsAgainst":31,
         "goalsAgainstPerGame":2.81818,
         "goalsFor":38,
         "goalsForPerGame":3.45454,
         "losses":6,
         "otLosses":0,
         "penaltyKillNetPct":0.810810,
         "penaltyKillPct":0.810811,
         "pointPct":0.45454,
         "points":10,
         "powerPlayNetPct":0.151515,
         "powerPlayPct":0.181818,
         "regulationAndOtWins":5,
         "seasonId":20232024,
         "shotsAgainstPerGame":28.72727,
         "shotsForPerGame":35.90909,
         "teamFullName":"Pittsburgh Penguins",
         "teamId":5,
         "ties":None,
         "wins":5,
         "winsInRegulation":5,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.513966,
         "gamesPlayed":12,
         "goalsAgainst":23,
         "goalsAgainstPerGame":1.91666,
         "goalsFor":38,
         "goalsForPerGame":3.16666,
         "losses":1,
         "otLosses":1,
         "penaltyKillNetPct":0.940000,
         "penaltyKillPct":0.940000,
         "pointPct":0.87500,
         "points":21,
         "powerPlayNetPct":0.175000,
         "powerPlayPct":0.175000,
         "regulationAndOtWins":9,
         "seasonId":20232024,
         "shotsAgainstPerGame":31.41666,
         "shotsForPerGame":31.58333,
         "teamFullName":"Boston Bruins",
         "teamId":6,
         "ties":None,
         "wins":10,
         "winsInRegulation":8,
         "winsInShootout":1
      },
      {
         "faceoffWinPct":0.448509,
         "gamesPlayed":13,
         "goalsAgainst":41,
         "goalsAgainstPerGame":3.15384,
         "goalsFor":41,
         "goalsForPerGame":3.15384,
         "losses":6,
         "otLosses":1,
         "penaltyKillNetPct":0.920000,
         "penaltyKillPct":0.880000,
         "pointPct":0.50000,
         "points":13,
         "powerPlayNetPct":0.076923,
         "powerPlayPct":0.128205,
         "regulationAndOtWins":6,
         "seasonId":20232024,
         "shotsAgainstPerGame":29.76923,
         "shotsForPerGame":28.38461,
         "teamFullName":"Buffalo Sabres",
         "teamId":7,
         "ties":None,
         "wins":6,
         "winsInRegulation":5,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.532258,
         "gamesPlayed":12,
         "goalsAgainst":42,
         "goalsAgainstPerGame":3.50000,
         "goalsFor":35,
         "goalsForPerGame":2.91666,
         "losses":5,
         "otLosses":2,
         "penaltyKillNetPct":0.773584,
         "penaltyKillPct":0.735850,
         "pointPct":0.50000,
         "points":12,
         "powerPlayNetPct":0.140000,
         "powerPlayPct":0.200000,
         "regulationAndOtWins":4,
         "seasonId":20232024,
         "shotsAgainstPerGame":34.91666,
         "shotsForPerGame":29.83333,
         "teamFullName":"Montréal Canadiens",
         "teamId":8,
         "ties":None,
         "wins":5,
         "winsInRegulation":2,
         "winsInShootout":1
      },
      {
         "faceoffWinPct":0.532786,
         "gamesPlayed":10,
         "goalsAgainst":35,
         "goalsAgainstPerGame":3.50000,
         "goalsFor":38,
         "goalsForPerGame":3.80000,
         "losses":6,
         "otLosses":0,
         "penaltyKillNetPct":0.777777,
         "penaltyKillPct":0.750000,
         "pointPct":0.40000,
         "points":8,
         "powerPlayNetPct":0.177777,
         "powerPlayPct":0.222222,
         "regulationAndOtWins":4,
         "seasonId":20232024,
         "shotsAgainstPerGame":31.50000,
         "shotsForPerGame":33.00000,
         "teamFullName":"Ottawa Senators",
         "teamId":9,
         "ties":None,
         "wins":4,
         "winsInRegulation":4,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.511461,
         "gamesPlayed":12,
         "goalsAgainst":41,
         "goalsAgainstPerGame":3.41666,
         "goalsFor":41,
         "goalsForPerGame":3.41666,
         "losses":4,
         "otLosses":2,
         "penaltyKillNetPct":0.717948,
         "penaltyKillPct":0.717949,
         "pointPct":0.58333,
         "points":14,
         "powerPlayNetPct":0.195121,
         "powerPlayPct":0.268292,
         "regulationAndOtWins":5,
         "seasonId":20232024,
         "shotsAgainstPerGame":31.25000,
         "shotsForPerGame":33.00000,
         "teamFullName":"Toronto Maple Leafs",
         "teamId":10,
         "ties":None,
         "wins":6,
         "winsInRegulation":3,
         "winsInShootout":1
      },
      {
         "faceoffWinPct":0.517241,
         "gamesPlayed":13,
         "goalsAgainst":44,
         "goalsAgainstPerGame":3.38461,
         "goalsFor":44,
         "goalsForPerGame":3.38461,
         "losses":5,
         "otLosses":0,
         "penaltyKillNetPct":0.840000,
         "penaltyKillPct":0.760000,
         "pointPct":0.61538,
         "points":16,
         "powerPlayNetPct":0.183673,
         "powerPlayPct":0.265306,
         "regulationAndOtWins":7,
         "seasonId":20232024,
         "shotsAgainstPerGame":25.61538,
         "shotsForPerGame":34.61538,
         "teamFullName":"Carolina Hurricanes",
         "teamId":12,
         "ties":None,
         "wins":8,
         "winsInRegulation":4,
         "winsInShootout":1
      },
      {
         "faceoffWinPct":0.524031,
         "gamesPlayed":11,
         "goalsAgainst":32,
         "goalsAgainstPerGame":2.90909,
         "goalsFor":31,
         "goalsForPerGame":2.81818,
         "losses":4,
         "otLosses":1,
         "penaltyKillNetPct":0.736842,
         "penaltyKillPct":0.710527,
         "pointPct":0.59090,
         "points":13,
         "powerPlayNetPct":0.108108,
         "powerPlayPct":0.135135,
         "regulationAndOtWins":6,
         "seasonId":20232024,
         "shotsAgainstPerGame":28.00000,
         "shotsForPerGame":35.18181,
         "teamFullName":"Florida Panthers",
         "teamId":13,
         "ties":None,
         "wins":6,
         "winsInRegulation":5,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.527443,
         "gamesPlayed":13,
         "goalsAgainst":45,
         "goalsAgainstPerGame":3.46153,
         "goalsFor":50,
         "goalsForPerGame":3.84615,
         "losses":3,
         "otLosses":4,
         "penaltyKillNetPct":0.871794,
         "penaltyKillPct":0.871795,
         "pointPct":0.61538,
         "points":16,
         "powerPlayNetPct":0.340909,
         "powerPlayPct":0.340909,
         "regulationAndOtWins":6,
         "seasonId":20232024,
         "shotsAgainstPerGame":33.61538,
         "shotsForPerGame":30.46153,
         "teamFullName":"Tampa Bay Lightning",
         "teamId":14,
         "ties":None,
         "wins":6,
         "winsInRegulation":6,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.459016,
         "gamesPlayed":10,
         "goalsAgainst":30,
         "goalsAgainstPerGame":3.00000,
         "goalsFor":19,
         "goalsForPerGame":1.90000,
         "losses":4,
         "otLosses":1,
         "penaltyKillNetPct":0.823529,
         "penaltyKillPct":0.794118,
         "pointPct":0.55000,
         "points":11,
         "powerPlayNetPct":0.096774,
         "powerPlayPct":0.096774,
         "regulationAndOtWins":3,
         "seasonId":20232024,
         "shotsAgainstPerGame":29.90000,
         "shotsForPerGame":29.60000,
         "teamFullName":"Washington Capitals",
         "teamId":15,
         "ties":None,
         "wins":5,
         "winsInRegulation":3,
         "winsInShootout":2
      },
      {
         "faceoffWinPct":0.425837,
         "gamesPlayed":11,
         "goalsAgainst":38,
         "goalsAgainstPerGame":3.45454,
         "goalsFor":26,
         "goalsForPerGame":2.36363,
         "losses":7,
         "otLosses":0,
         "penaltyKillNetPct":0.861111,
         "penaltyKillPct":0.833334,
         "pointPct":0.36363,
         "points":8,
         "powerPlayNetPct":0.052631,
         "powerPlayPct":0.105263,
         "regulationAndOtWins":4,
         "seasonId":20232024,
         "shotsAgainstPerGame":35.36363,
         "shotsForPerGame":26.90909,
         "teamFullName":"Chicago Blackhawks",
         "teamId":16,
         "ties":None,
         "wins":4,
         "winsInRegulation":3,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.488435,
         "gamesPlayed":13,
         "goalsAgainst":42,
         "goalsAgainstPerGame":3.23076,
         "goalsFor":48,
         "goalsForPerGame":3.69230,
         "losses":5,
         "otLosses":1,
         "penaltyKillNetPct":0.795918,
         "penaltyKillPct":0.795919,
         "pointPct":0.57692,
         "points":15,
         "powerPlayNetPct":0.232142,
         "powerPlayPct":0.250000,
         "regulationAndOtWins":7,
         "seasonId":20232024,
         "shotsAgainstPerGame":31.00000,
         "shotsForPerGame":30.76923,
         "teamFullName":"Detroit Red Wings",
         "teamId":17,
         "ties":None,
         "wins":7,
         "winsInRegulation":6,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.505934,
         "gamesPlayed":12,
         "goalsAgainst":36,
         "goalsAgainstPerGame":3.00000,
         "goalsFor":34,
         "goalsForPerGame":2.83333,
         "losses":7,
         "otLosses":0,
         "penaltyKillNetPct":0.717948,
         "penaltyKillPct":0.692308,
         "pointPct":0.41666,
         "points":10,
         "powerPlayNetPct":0.224489,
         "powerPlayPct":0.224489,
         "regulationAndOtWins":5,
         "seasonId":20232024,
         "shotsAgainstPerGame":30.33333,
         "shotsForPerGame":30.33333,
         "teamFullName":"Nashville Predators",
         "teamId":18,
         "ties":None,
         "wins":5,
         "winsInRegulation":4,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.477093,
         "gamesPlayed":11,
         "goalsAgainst":32,
         "goalsAgainstPerGame":2.90909,
         "goalsFor":26,
         "goalsForPerGame":2.36363,
         "losses":5,
         "otLosses":1,
         "penaltyKillNetPct":0.806451,
         "penaltyKillPct":0.741936,
         "pointPct":0.50000,
         "points":11,
         "powerPlayNetPct":0.000000,
         "powerPlayPct":0.035714,
         "regulationAndOtWins":4,
         "seasonId":20232024,
         "shotsAgainstPerGame":33.09090,
         "shotsForPerGame":26.63636,
         "teamFullName":"St. Louis Blues",
         "teamId":19,
         "ties":None,
         "wins":5,
         "winsInRegulation":4,
         "winsInShootout":1
      },
      {
         "faceoffWinPct":0.526027,
         "gamesPlayed":12,
         "goalsAgainst":42,
         "goalsAgainstPerGame":3.50000,
         "goalsFor":32,
         "goalsForPerGame":2.66666,
         "losses":7,
         "otLosses":1,
         "penaltyKillNetPct":0.950000,
         "penaltyKillPct":0.900000,
         "pointPct":0.37500,
         "points":9,
         "powerPlayNetPct":0.119047,
         "powerPlayPct":0.166666,
         "regulationAndOtWins":4,
         "seasonId":20232024,
         "shotsAgainstPerGame":27.58333,
         "shotsForPerGame":33.16666,
         "teamFullName":"Calgary Flames",
         "teamId":20,
         "ties":None,
         "wins":4,
         "winsInRegulation":4,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.459420,
         "gamesPlayed":11,
         "goalsAgainst":31,
         "goalsAgainstPerGame":2.81818,
         "goalsFor":37,
         "goalsForPerGame":3.36363,
         "losses":3,
         "otLosses":0,
         "penaltyKillNetPct":0.978260,
         "penaltyKillPct":0.891305,
         "pointPct":0.72727,
         "points":16,
         "powerPlayNetPct":0.139534,
         "powerPlayPct":0.186046,
         "regulationAndOtWins":7,
         "seasonId":20232024,
         "shotsAgainstPerGame":28.63636,
         "shotsForPerGame":34.36363,
         "teamFullName":"Colorado Avalanche",
         "teamId":21,
         "ties":None,
         "wins":8,
         "winsInRegulation":7,
         "winsInShootout":1
      },
      {
         "faceoffWinPct":0.509298,
         "gamesPlayed":11,
         "goalsAgainst":47,
         "goalsAgainstPerGame":4.27272,
         "goalsFor":29,
         "goalsForPerGame":2.63636,
         "losses":8,
         "otLosses":1,
         "penaltyKillNetPct":0.688888,
         "penaltyKillPct":0.688889,
         "pointPct":0.22727,
         "points":5,
         "powerPlayNetPct":0.205128,
         "powerPlayPct":0.256410,
         "regulationAndOtWins":2,
         "seasonId":20232024,
         "shotsAgainstPerGame":30.72727,
         "shotsForPerGame":34.27272,
         "teamFullName":"Edmonton Oilers",
         "teamId":22,
         "ties":None,
         "wins":2,
         "winsInRegulation":2,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.500000,
         "gamesPlayed":12,
         "goalsAgainst":24,
         "goalsAgainstPerGame":2.00000,
         "goalsFor":54,
         "goalsForPerGame":4.50000,
         "losses":2,
         "otLosses":1,
         "penaltyKillNetPct":0.818181,
         "penaltyKillPct":0.772728,
         "pointPct":0.79166,
         "points":19,
         "powerPlayNetPct":0.326086,
         "powerPlayPct":0.326086,
         "regulationAndOtWins":9,
         "seasonId":20232024,
         "shotsAgainstPerGame":31.25000,
         "shotsForPerGame":29.16666,
         "teamFullName":"Vancouver Canucks",
         "teamId":23,
         "ties":None,
         "wins":9,
         "winsInRegulation":9,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.452380,
         "gamesPlayed":12,
         "goalsAgainst":34,
         "goalsAgainstPerGame":2.83333,
         "goalsFor":37,
         "goalsForPerGame":3.08333,
         "losses":5,
         "otLosses":0,
         "penaltyKillNetPct":0.827586,
         "penaltyKillPct":0.793104,
         "pointPct":0.58333,
         "points":14,
         "powerPlayNetPct":0.184210,
         "powerPlayPct":0.184210,
         "regulationAndOtWins":7,
         "seasonId":20232024,
         "shotsAgainstPerGame":32.66666,
         "shotsForPerGame":27.91666,
         "teamFullName":"Anaheim Ducks",
         "teamId":24,
         "ties":None,
         "wins":7,
         "winsInRegulation":4,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.491253,
         "gamesPlayed":11,
         "goalsAgainst":28,
         "goalsAgainstPerGame":2.54545,
         "goalsFor":31,
         "goalsForPerGame":2.81818,
         "losses":3,
         "otLosses":1,
         "penaltyKillNetPct":0.950000,
         "penaltyKillPct":0.925000,
         "pointPct":0.68181,
         "points":15,
         "powerPlayNetPct":0.000000,
         "powerPlayPct":0.096774,
         "regulationAndOtWins":6,
         "seasonId":20232024,
         "shotsAgainstPerGame":33.45454,
         "shotsForPerGame":29.90909,
         "teamFullName":"Dallas Stars",
         "teamId":25,
         "ties":None,
         "wins":7,
         "winsInRegulation":5,
         "winsInShootout":1
      },
      {
         "faceoffWinPct":0.497084,
         "gamesPlayed":11,
         "goalsAgainst":31,
         "goalsAgainstPerGame":2.81818,
         "goalsFor":47,
         "goalsForPerGame":4.27272,
         "losses":2,
         "otLosses":2,
         "penaltyKillNetPct":0.871794,
         "penaltyKillPct":0.846154,
         "pointPct":0.72727,
         "points":16,
         "powerPlayNetPct":0.142857,
         "powerPlayPct":0.183673,
         "regulationAndOtWins":7,
         "seasonId":20232024,
         "shotsAgainstPerGame":27.36363,
         "shotsForPerGame":32.72727,
         "teamFullName":"Los Angeles Kings",
         "teamId":26,
         "ties":None,
         "wins":7,
         "winsInRegulation":7,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.549019,
         "gamesPlayed":12,
         "goalsAgainst":55,
         "goalsAgainstPerGame":4.58333,
         "goalsFor":14,
         "goalsForPerGame":1.16666,
         "losses":10,
         "otLosses":1,
         "penaltyKillNetPct":0.702127,
         "penaltyKillPct":0.702128,
         "pointPct":0.12500,
         "points":3,
         "powerPlayNetPct":0.157894,
         "powerPlayPct":0.184210,
         "regulationAndOtWins":1,
         "seasonId":20232024,
         "shotsAgainstPerGame":37.66666,
         "shotsForPerGame":24.75000,
         "teamFullName":"San Jose Sharks",
         "teamId":28,
         "ties":None,
         "wins":1,
         "winsInRegulation":1,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.478851,
         "gamesPlayed":12,
         "goalsAgainst":39,
         "goalsAgainstPerGame":3.25000,
         "goalsFor":32,
         "goalsForPerGame":2.66666,
         "losses":5,
         "otLosses":3,
         "penaltyKillNetPct":0.868421,
         "penaltyKillPct":0.868422,
         "pointPct":0.45833,
         "points":11,
         "powerPlayNetPct":0.121951,
         "powerPlayPct":0.146341,
         "regulationAndOtWins":4,
         "seasonId":20232024,
         "shotsAgainstPerGame":33.08333,
         "shotsForPerGame":31.50000,
         "teamFullName":"Columbus Blue Jackets",
         "teamId":29,
         "ties":None,
         "wins":4,
         "winsInRegulation":3,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.455474,
         "gamesPlayed":12,
         "goalsAgainst":48,
         "goalsAgainstPerGame":4.00000,
         "goalsFor":43,
         "goalsForPerGame":3.58333,
         "losses":5,
         "otLosses":2,
         "penaltyKillNetPct":0.717948,
         "penaltyKillPct":0.666667,
         "pointPct":0.50000,
         "points":12,
         "powerPlayNetPct":0.108695,
         "powerPlayPct":0.152173,
         "regulationAndOtWins":4,
         "seasonId":20232024,
         "shotsAgainstPerGame":32.83333,
         "shotsForPerGame":31.50000,
         "teamFullName":"Minnesota Wild",
         "teamId":30,
         "ties":None,
         "wins":5,
         "winsInRegulation":4,
         "winsInShootout":1
      },
      {
         "faceoffWinPct":0.484104,
         "gamesPlayed":12,
         "goalsAgainst":40,
         "goalsAgainstPerGame":3.33333,
         "goalsFor":41,
         "goalsForPerGame":3.41666,
         "losses":4,
         "otLosses":2,
         "penaltyKillNetPct":0.750000,
         "penaltyKillPct":0.700000,
         "pointPct":0.58333,
         "points":14,
         "powerPlayNetPct":0.155555,
         "powerPlayPct":0.177777,
         "regulationAndOtWins":6,
         "seasonId":20232024,
         "shotsAgainstPerGame":27.91666,
         "shotsForPerGame":32.75000,
         "teamFullName":"Winnipeg Jets",
         "teamId":52,
         "ties":None,
         "wins":6,
         "winsInRegulation":5,
         "winsInShootout":0
      },
      {
         "faceoffWinPct":0.487323,
         "gamesPlayed":12,
         "goalsAgainst":35,
         "goalsAgainstPerGame":2.91666,
         "goalsFor":39,
         "goalsForPerGame":3.25000,
         "losses":5,
         "otLosses":1,
         "penaltyKillNetPct":0.714285,
         "penaltyKillPct":0.714286,
         "pointPct":0.54166,
         "points":13,
         "powerPlayNetPct":0.265306,
         "powerPlayPct":0.265306,
         "regulationAndOtWins":4,
         "seasonId":20232024,
         "shotsAgainstPerGame":31.66666,
         "shotsForPerGame":29.08333,
         "teamFullName":"Arizona Coyotes",
         "teamId":53,
         "ties":None,
         "wins":6,
         "winsInRegulation":4,
         "winsInShootout":2
      },
      {
         "faceoffWinPct":0.512683,
         "gamesPlayed":13,
         "goalsAgainst":28,
         "goalsAgainstPerGame":2.15384,
         "goalsFor":49,
         "goalsForPerGame":3.76923,
         "losses":1,
         "otLosses":1,
         "penaltyKillNetPct":0.923076,
         "penaltyKillPct":0.871795,
         "pointPct":0.88461,
         "points":23,
         "powerPlayNetPct":0.212765,
         "powerPlayPct":0.234042,
         "regulationAndOtWins":8,
         "seasonId":20232024,
         "shotsAgainstPerGame":30.30769,
         "shotsForPerGame":29.23076,
         "teamFullName":"Vegas Golden Knights",
         "teamId":54,
         "ties":None,
         "wins":11,
         "winsInRegulation":8,
         "winsInShootout":3
      },
      {
         "faceoffWinPct":0.495263,
         "gamesPlayed":13,
         "goalsAgainst":44,
         "goalsAgainstPerGame":3.38461,
         "goalsFor":34,
         "goalsForPerGame":2.61538,
         "losses":6,
         "otLosses":3,
         "penaltyKillNetPct":0.729729,
         "penaltyKillPct":0.702703,
         "pointPct":0.42307,
         "points":11,
         "powerPlayNetPct":0.210526,
         "powerPlayPct":0.263157,
         "regulationAndOtWins":4,
         "seasonId":20232024,
         "shotsAgainstPerGame":32.07692,
         "shotsForPerGame":31.46153,
         "teamFullName":"Seattle Kraken",
         "teamId":55,
         "ties":None,
         "wins":4,
         "winsInRegulation":2,
         "winsInShootout":0
      }
   ],
   "total":32
}
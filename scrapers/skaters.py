from common import FetchJson, GetDateString
import math
from os import getenv
import models
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, or_

#TODO move to env
seasonEndYear = 2024
SKATER_BASE_URL = getenv( 'SKATER_BASE_URL' )

# fetch the raw data and filter
def FetchSkaters():
    skaterIds = FetchSkaterIds()
    skaters = []
    queries = GenerateSkaterQueryUrls( skaterIds )
    for requestUrl in queries:
        statsJson = FetchJson( requestUrl )
        #TODO: it appears some players do not have stats yet - seems to be a rookie thing, maybe goalies
        skaters = skaters + statsJson[ 'data' ]
    return skaters

def FetchSkaterIds():
    Session = sessionmaker( models.engine )
    skaterIds = []
    with Session() as session:
        skaterIdsQuery = select(
            models.Skater.id
        ).join(
            models.Roster,
            and_( models.Skater.id == models.Roster.skater_id )
        ).join(
            models.Team,
            and_( models.Roster.team_id == models.Team.team_id )
        ).join(
            models.Schedule,
            or_( models.Schedule.away_id == models.Team.team_id, models.Schedule.home_id == models.Team.team_id )
        ).filter(
            models.Schedule.game_date == GetDateString()
        )

        skaterIdsResults = session.execute( skaterIdsQuery )
        skaterIds = skaterIdsResults.scalars().all()
    return skaterIds

def GenerateSkaterQueryUrls( skaterIds ):
    queryLimitMultiplier = 100
    skaterCount = len(skaterIds )
    requestCount = buildRequestCount( skaterCount, queryLimitMultiplier )
    queries = []#TODO: queries = buildQueries()
    seasonId = buildSeasonId()

    for i in range( requestCount ):#337 skaters would be range(4) 0, 1, 2, 3 for 0-100, 101-200, 201-300, 301-337
        querySkaterIdsStart = i * queryLimitMultiplier
        querySkaterIdsEnd = ( i + 1 ) * queryLimitMultiplier
        if querySkaterIdsEnd >= skaterCount:
            querySkaterIdsEnd = skaterCount
        
        test = [ id for id in skaterIds[ querySkaterIdsStart : querySkaterIdsEnd ] ]
        querySkaterIds = ','.join( [ str(id) for id in skaterIds[ querySkaterIdsStart : querySkaterIdsEnd ] ] )
        
        query = f'{SKATER_BASE_URL}?start=0&limit={queryLimitMultiplier}&cayenneExp=gamesPlayed>=0 and gameTypeId>=2 and playerId in ({querySkaterIds}) and seasonId={seasonId}'
        # t='https://api.nhle.com/stats/rest/en/skater/summary?start=0&limit=100&cayenneExp=gamesPlayed>=0 and gameTypeId>=2 and playerId in (8479982) and seasonId=20232024 and rosterStatus in ( "Y", "I" )' % (querySkaterIdsStart, queryLimitMultiplier, querySkaterIds , seasonId )

        queries.append( query )
    return queries

def buildRequestCount( skaterCount, queryLimitMultiplier ):
    return math.ceil( skaterCount / queryLimitMultiplier)

def buildSeasonId():
    seasonYears = buildSeasonYears()
    return ''.join(seasonYears)

def buildSeasonYears():
    return [ str(seasonEndYear - 1), str(seasonEndYear) ]
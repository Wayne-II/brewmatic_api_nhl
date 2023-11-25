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
    #skaterIds = FetchSkaterIds()
    skaters = []
    seasonId = buildSeasonId()
    #TODO: skip first 100 and process this data
    query = f'{SKATER_BASE_URL}?start=0&limit=100&cayenneExp=gamesPlayed>=0 and gameTypeId>=2 and seasonId={seasonId}'
    statsJson = FetchJson( query )
    skaters = skaters + statsJson[ 'data' ]
    skaterCount = int( statsJson[ 'total' ]  )
    if skaterCount > 100:
        queries = GenerateSkaterQueryUrls( skaterCount )
        print( queries )
        for requestUrl in queries:
            statsJson = FetchJson( requestUrl )
            #TODO: it appears some players do not have stats yet - seems to be a rookie thing, maybe goalies
            skaters = skaters + statsJson[ 'data' ]
    return skaters


def GenerateSkaterQueryUrls( skaterCount ):
    queryLimitMultiplier = 100
    queries = []#TODO: queries = buildQueries()
    seasonId = buildSeasonId()

    #skip the first 100 as the data has already been fetched in order to get skaterCount
    for i in range( 100, skaterCount, queryLimitMultiplier ):#337 skaters would be range(4) 0, 1, 2, 3 for 0-100, 101-200, 201-300, 301-337
        
        query = f'{SKATER_BASE_URL}?start={i}&limit={queryLimitMultiplier}&cayenneExp=gamesPlayed>=0 and gameTypeId>=2 and seasonId={seasonId}'
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
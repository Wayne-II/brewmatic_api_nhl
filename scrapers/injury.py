from dotenv import load_dotenv
load_dotenv('.env')

from common import FetchJson, GetDateString
import os
import models
from sqlalchemy.orm import sessionmaker

INJURY_ALTERNATE_BASE_URL = os.getenv( 'INJURY_ALTERNATE_BASE_URL' )
################################################################################
########################### FUNCTIONS COMMON TO ALL ############################
################################################################################
# fetch and filter raw NHL data
#TODO: determine which data I want to keep if there's a conflict
def FetchInjuries():
    injuriesTSN = FetchTSNData()
    injuriesNHL = FetchNHLData()
    injuries = injuriesTSN
    for team in injuriesNHL:
        injuries.extend( injuriesNHL[ team ] )
    
    return injuries

#TODO: if the first atempt at skater_full_name doesn't get a match for the
#provided skaterName, try to use the suggestions to try getting an alternative
#spelling for the name that returned 0 user ID
def GetSkaterIdByName( skaterName, session=sessionmaker( models.engine )() ):
    ret = 0
    skatersQuery = session.query( 
        models.Skater
    ).filter(
        models.Skater.skater_full_name == skaterName
    )
    skaterResults = session.scalars( skatersQuery ).all()
    if len( skaterResults ) > 0:
        ret = skaterResults[ 0 ].id
    return ret

################################################################################
################## FUNCTIONS TO EXTRACT TSN/BELLMEDIA DATA #####################
################################################################################
def FetchTSNData():
    injuries = FetchJson( f'{INJURY_ALTERNATE_BASE_URL}' )
    injuredPlayers = []
    for team in injuries:
        injuredPlayers.extend( ProcessTeamInjuries( team ) )
    return injuredPlayers

def ProcessTeamInjuries( teamJson ):
    injuredPlayers = []
    for player in teamJson[ 'playerInjuries' ]:
        injuredPlayers.append( ProcessPlayerInjury( player ) )
    return injuredPlayers

def FilterPlayer( playerJson ):
    playerName = playerJson[ 'displayName' ]
    return { 
        'name' : playerName,
        'player_status': playerJson[ 'playerStatus' ],
        'skater_id': GetSkaterIdByName( playerName )
        }

def FilterInjuryData( injuryData ):
    today = GetDateString()
    injuryKeys = [ 'date', 'status' ]
    filteredInjury = { k:injuryData[k] for k in injuryKeys }
    filteredInjury.update( 
        injury_type=injuryData[ 'description' ],
        updated=datetime.datetime.strptime( today + 'T00:00:00+0000', "%Y-%m-%dT%H:%M:%S%z")
    )
    return filteredInjury

def ProcessPlayerInjury( playerJson ):
    playerData = FilterPlayer( playerJson[ 'player' ] )
    playerData.update( FilterInjuryData( playerJson ) )
    return playerData

################################################################################
######################## FUNCTIONS TO EXTRACT NHL DATA #########################
################################################################################
import cloudscraper
from bs4 import BeautifulSoup
import datetime
import json
import re

INJURY_BASE_URL = os.getenv( 'INJURY_BASE_URL' )
#compile regex at runtime
teamRegex = re.compile( r'\*\*([A-Za-z\s]+) projected lineup\*\*', re.DOTALL | re.MULTILINE | re.IGNORECASE )
injuredLineRegex = re.compile( r'\*\*\*Injured:?\s?\*\*')
injuredRegex = re.compile( r'([a-zA-Z\s]+) \([a-zA-Z\s]+\)', re.DOTALL | re.IGNORECASE )
injuriesRegex = re.compile( r'[a-zA-Z\s]+ \(([a-zA-Z\s]+)\),?', re.DOTALL | re.IGNORECASE )
scratchedLineRegex = re.compile( r'\*\*\*Scratched:\*\*', re.IGNORECASE )
scratchedRegex = re.compile( r'(?:\s|\s\*)([a-zA-Z\s]+),?', re.DOTALL | re.IGNORECASE )

def FetchNHLData():
    scraper = cloudscraper.create_scraper(browser='chrome')
    url = INJURY_BASE_URL
    htmlText = scraper.get(url).text
    htmlSoup = BeautifulSoup( htmlText, 'html.parser' )
    #extract injury JSON embedded in HTML as script tag
    injuryJsonStringMatches = htmlSoup.find_all( 'script', { 'type': 'application/ld+json' } )
    #extract date and time information - it's updated around 5 UTC either 5:45 opr 4:45 can't remember atm
    injuryDateTime = htmlSoup.find( 'div', { 'class' : 'nhl-c-article__date' } ).find( 'time' ).get( 'datetime' )
    dt = datetime.datetime.strptime(injuryDateTime + '+0000', "%Y-%m-%dT%H:%M:%S%z")
    ret = {}
    #TODO process status report to process suspensions.  THis will require some AI to determine
    #if there's any raw english that suggests any suspensions
    #process raw data
    for match in injuryJsonStringMatches:
        matchJson = json.loads( match.contents[0] )
        #TODO: process injury article
        
        if matchJson[ '@type' ] == 'NewsArticle' and matchJson[ 'headline' ] == 'Projected lineups, starting goalies for today':
            extractedInjuryData = ExtractInjuryData( matchJson[ 'articleBody' ] )
    
    ret = UpdateExtractedInjuryData( extractedInjuryData, dt )

    return ret

def UpdateExtractedInjuryData( injuryData, updated ):
    updatedData = { k:[] for k in injuryData.keys() }
    for team in injuryData:
        for injured in injuryData[ team ]:
            injured.update( updated=updated )
            updatedData[ team ].append( injured )
    return updatedData


def ExtractInjuryData( article_body ):

    article_lines = article_body.split( '\n' )

    teamMatches = teamRegex.findall(article_body)
    teamIdx = 0
    currentTeam = None
    players_by_team = { team: [] for team in teamMatches }
    for article_line in article_lines:
        if injuredLineRegex.match( article_line ):
            injuredMatches = injuredRegex.findall( article_line )
            injuriesMatches = injuriesRegex.findall( article_line )
            players_by_team[ currentTeam ].extend( ProcessInjuryData( injuredMatches, injuriesMatches ) )
        elif scratchedLineRegex.match( article_line ):
            scratchedMatches = scratchedRegex.findall( article_line )
            injuriesData = [ 'scratched' for scratch in scratchedMatches ]
            players_by_team[ currentTeam ].extend( ProcessInjuryData( scratchedMatches, injuriesData ) )
        elif teamRegex.match( article_line ):
            currentTeam = teamMatches[ teamIdx ]
            teamIdx += 1

    return players_by_team

def ProcessInjuryData( playerData, injuryData ):
    player_statuses = []
    Session = sessionmaker( models.engine )
    with Session() as session:
        for playerIdx, player in enumerate( playerData ):
            player_name = player.strip()
            player_statuses.append( {
                'name': player_name,
                'skater_id': GetSkaterIdByName( player_name, session ),
                'status':'I' if injuryData[ playerIdx ] != 'scratched' else 'S',
                'injury_type':injuryData[ playerIdx ].strip()
            } )
    return player_statuses
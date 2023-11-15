import requests
import datetime

from sqlalchemy.orm import sessionmaker
import models

from flask_restx import Namespace, Resource, fields
from flask import jsonify
from common import FetchJson, GetDate, GetDateString, GetInsert
from os import getenv

import re
import cloudscraper
from bs4 import BeautifulSoup
import json

from .suggest import SuggestSkater

INJURY_BASE_URL = getenv( 'INJURY_BASE_URL' )

#this is broken
def CheckIfDataExists():
    return False

def GetSkaterIdByName( skaterName, session ):
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

def StoreData( injuryData, session ):
    today = GetDate()
    injuryInsertData = []
    scratchInsertData = []
    insert = GetInsert( session )
    for teamId in injuryData:
        for injury in injuryData[ teamId ][ 'injury' ]:
            injured = injury[ 'name' ].strip()
            injuryType = injury[ 'injury' ]
            skaterId = GetSkaterIdByName( injured.strip(), session )
            if( skaterId == 0 ):#TODO: error logging, exception handling, etc
                #TODO: throw
                suggestions = SuggestSkater( [injured] )
                suggest = '<No Suggestion>'
                if injured in suggestions.keys() and len( suggestions[ injured ] ) > 0:
                    suggest = suggestions[ injured ][0]
                    skaterId = GetSkaterIdByName( suggest, session )
                if skaterId == 0:#TODO: bugs with data sanitization from upstreamp api
                    print( f'injured {injured} id: {skaterId} type: {injuryType} suggest: {suggest}' )
            status = 'I'
            injuryInsertData.append( {
                'skater_id': skaterId,
                'status': status,
                'injury_type':injuryType,
                'updated': today
            } )
        for scratched in injuryData[ teamId ][ 'scratch' ]:
            scratched = scratched.strip()
            skaterId = GetSkaterIdByName( scratched, session )
            if skaterId == 0:
                suggestions = SuggestSkater( [scratched] )
                suggest = '<No Suggestion>'
                if scratched in suggestions.keys() and len( suggestions[ scratched ] ) > 0:
                    suggest = suggestions[ scratched ][ 0 ]
                    skaterId = GetSkaterIdByName( suggest, session )
                if skaterId == 0:
                    print( f'scratched {scratched} id: {skaterId} suggest: {suggest}' )
            status = 'S'
            scratchInsertData.append( {
                'skater_id': skaterId,
                'status': status,
                'updated': today,
                'injury_type': 'scratch'
            } )
    insertData = injuryInsertData + scratchInsertData
    insertQuery = insert( 
        models.Injury 
    ).values( 
        injuryInsertData 
    )
    
    conflictQuery = insertQuery.on_conflict_do_update(
        index_elements=[ 'skater_id' ],
        set_ = {
            'status' : insertQuery.excluded.status,
            'updated' : insertQuery.excluded.updated,
            'injury_type':insertQuery.excluded.injury_type
        }
    )
    
    scratchInsertQuery = insert( 
        models.Injury 
    ).values( 
        scratchInsertData
    )
    scratchConflictQuery = scratchInsertQuery.on_conflict_do_update(
        index_elements=[ 'skater_id' ],
        set_ = {
            'status' : insertQuery.excluded.status,
            'updated' : insertQuery.excluded.updated,
            'injury_type':insertQuery.excluded.injury_type
        }
    )
    session.execute( scratchConflictQuery )
    session.execute( conflictQuery )
    session.commit()

def RetrieveData( session ):
    
    ret = []
    today = GetDate()
    injuryQuery = session.query( 
        models.Injury,
        models.Skater
    ).join(
        models.Skater
    ).filter(
        models.Injury.updated == today
    )
    
    injuryResults = session.scalars( injuryQuery ).all()
    for injuryResult in injuryResults:
        #the fact I have to baby this while jsonify doesn't work makes me think jsonify is a bit
        #useless. 
        ret.append( {
            'skater_id':injuryResult.skater_id,
            'status':injuryResult.status,
            'injury_type':injuryResult.injury_type
        } )

    return ret

ScInNameRegex = re.compile( r'([a-zA-Z ]+),?' )
injuryTypeRegex = re.compile( r'\(([a-zA-Z ]+)\)' )
noneRegex = re.compile( r'\*\* None\*')
def ProcessScInNames( data ):
    return ScInNameRegex.findall( data)

def ProcessScratched( data ):
    return ProcessScInNames( data )

def ProcessInjured( data ):
    injuryTypeMatches = injuryTypeRegex.findall( data )
    nameMatches = ProcessScInNames( injuryTypeRegex.sub( '', data ) )
    return { 'names': nameMatches, 'injuries': injuryTypeMatches }

def ProcessStatus( data ):
    return data


def FetchInjury():
    scraper = cloudscraper.create_scraper(browser='chrome')
    url = INJURY_BASE_URL
    htmlText = scraper.get(url).text
    htmlSoup = BeautifulSoup( htmlText, 'html.parser' )
    injuryJsonStringMatches = htmlSoup.find_all( 'script', { 'type': 'application/ld+json' } )

    teamsLineupRegex = re.compile( r'(\*\*([a-zA-Z ]+) projected lineup\*\*)' )
    scInStRegex = re.compile( r'\*?\*\*(Scratched|Injured|Status report|Status Report):?' )
    # injuryRegex = re.compile( r'\*\*\*Injured:' )
    # statusRegex = re.compile( r'\*\*Status report' )
    #{ 
    #   '<Common Name>':{ 
    #       'scratch':[ '<player name>' ],
    #       'injury':[
    #           {
    #               'name': '<player name'>,
    #               'injury': '<eg upper body>                
    #           }
    #       ],
    #       'suspend':[ '<player name>' ],
    #       'status':''
    #   }
    #}
    ret = {}
    #TODO: deconstruct into managable bits.  Each block of for could probably be a function
    #TODO process status report to process suspensions.  THis will require some AI to determine
    #if there's any raw english that suggests any suspensions
    #process raw data
    for match in injuryJsonStringMatches:
        matchJson = json.loads( match.contents[0] )
        #TODO: process injury article
        if matchJson[ '@type' ] == 'NewsArticle' and matchJson[ 'headline' ] == 'Projected lineups, starting goalies for today':
            articleSplit = matchJson[ 'articleBody' ].split( "\\-\\-\\-" )
            injuriesDataRaw = articleSplit[ 1 ]
            lineupDataRaw = teamsLineupRegex.split( injuriesDataRaw )
            #process lineup section of article
            #TODO process injuries and scratched
            for rawIdx, rawDatum in enumerate( lineupDataRaw ):
                if teamsLineupRegex.fullmatch( rawDatum ):
                    teamCommonName = lineupDataRaw[ rawIdx + 1 ]
                    teamLineupData = scInStRegex.split( lineupDataRaw[ rawIdx + 2 ] )
                    ret[ teamCommonName ] = {'scratch':[], 'injury':[], 'suspend':[], 'status':''}
                    #process team data
                    for lineIdx, lineDatum in enumerate( teamLineupData ):
                        if lineDatum == 'Scratched':
                            scratches = ProcessScratched( teamLineupData[ lineIdx + 1 ] )
                            for scratched in scratches:
                                if scratched.strip() != '':
                                    ret[ teamCommonName ][ 'scratch' ].append( scratched )
                        elif lineDatum == 'Injured' and not noneRegex.match( teamLineupData[ lineIdx + 1 ] ):
                            injuries = ProcessInjured( teamLineupData[ lineIdx + 1 ] )
                            for injuryIdx, injured in enumerate( injuries[ 'names' ] ):
                                ret[ teamCommonName ][ 'injury' ].append(
                                    { 'name' : injured, 'injury': injuries[ 'injuries' ][ injuryIdx ] }
                                )
                        elif lineDatum == 'Status report':
                            ret[ teamCommonName ][ 'status' ] = ProcessStatus( teamLineupData[ lineIdx + 1 ] )
    return ret                   

api = Namespace( "injury" )

@api.route("/")
class Injury( Resource ):
    def get( self ):
        ret = {}
        #if not database data, fetch from NHL and store in DB otherwise DB
        Session = sessionmaker( models.engine )
        with Session() as session:
            if not CheckIfDataExists(  ):
                raw = FetchInjury(  )
                StoreData( raw, session )
            ret = RetrieveData( session )
        return ret

# ~~~~~ INJURY ~~~~~
# https://www.nhl.com/news/nhl-projected-lineup-projections
#       Will have to scrape data from HTML.  Sample format:
#       <script type="application/ld&#x2B;json">
#       {"@type":"NewsArticle","headline":"Projected lineups, starting goalies for today","image":["https://media.d3.nhle.com/image/private/t_ratio16_9-size20/v1695749003/prd/eizseephgncsxye9bfwt","https://media.d3.nhle.com/image/private/t_ratio4_3-size20/v1695749003/prd/eizseephgncsxye9bfwt","https://media.d3.nhle.com/image/private/t_ratio1_1-size20/v1695749003/prd/eizseephgncsxye9bfwt"],"articleBody":"## [How to stream NHL games](https://www.nhl.com/info/how-to-watch-and-stream-nhl-games)\n\n*Below are projected lineups compiled by NHL.com staff writers and independent correspondents.*\n\n### **MORE COVERAGE**:\n\n[Daily fantasy picks](https://www.nhl.com/news/nhl-dfs-expert-picks-fantasy-hockey) | [Rankings](https://www.nhl.com/news/topic/fantasy/nhl-fantasy-hockey-top-250-200-rankings-drafts-players-big-board-281505474)\n\nListen: [NHL Fantasy on Ice podcast](https://audioboom.com/channel/nhl-fantasy-on-ice)\n\n\\-\\-\\-\n\n## **SABRES (6-6-0) at HURRICANES (7-5-0)**\n\n**7 p.m. ET; BSSO, MSG-B**\n\n**Sabres projected lineup**\n\nJeff Skinner -- Tage Thompson -- Alex Tuch\n\nJordan Greenway -- Casey Mittelstadt -- JJ Peterka\n\nVictor Olofsson -- Peyton Krebs -- Lukas Rousek\n\nZemgus Girgensons -- Tyson Jost -- Kyle Okposo\n\nRyan Johnson – Rasmus Dahlin\n\nOwen Power -- Henri Jokiharju\n\nConner Clifton -- Erik Johnson\n\nUkko-Pekka Luukkonen\n\nDevon Levi\n\n***Scratched:**** Matt Savoie, Jacob Bryson*\n\n***Injured:**** Dylan Cozens (upper body), Brandon Biro (upper body), Mattias Samuelsson (lower body), Zach Benson (lower body), Eric Comrie (lower body), Jack Quinn (Achilles)*\n\n**Hurricanes projected lineup**\n\nStefan Noesen -- Sebastian Aho -- Seth Jarvis\n\nAndrei Svechnikov -- Jesper Kotkaniemi -- Teuvo Teravainen\n\nJordan Martinook -- Jordan Staal -- Jesper Fast\n\nMichael Bunting -- Jack Drury -- Martin Necas\n\nJaccob Slavin -- Brent Burns\n\nBrady Skjei -- Dmitry Orlov\n\nTony DeAngelo -- Jalen Chatfield\n\nAntti Raanta\n\nPyotr Kochetkov\n\n***Scratched:**** Brendan Lemieux*\n\n***Injured:**** Frederik Andersen (blood clot), Brett Pesce (lower body)*\n\n**Status report**\n\nSavoie was recalled from Rochester of the American Hockey League on Monday but the forward is unlikely to play. … Andersen, a goalie, was placed on injured reserve Monday because of a blood clot issue. Kochetkov was recalled from Syracuse of the AHL on Monday, and goalie Jaroslav Halak joined Carolina on a professional tryout contract. … Pesce participated in Carolina’s morning skate without a no-contact jersey, but the defenseman will miss his eighth straight game.\n\n## **LIGHTNING (5-3-4) at CANADIENS (5-4-2)**\n\n**7 p.m. ET; RDS, TSN2, BSSUN**\n\n**Lightning projected lineup**\n\nBrandon Hagel – Brayden Point -- Nikita Kucherov\n\nSteven Stamkos -- Nick Paul -- Conor Sheary\n\nTyler Motte -- Anthony Cirelli -- Alex Barre-Boulet\n\nTanner Jeannot -- Luke Glendening -- Austin Watson\n\nVictor Hedman -- Erik Cernak\n\nMikhail Sergachev -- Darren Raddysh\n\nCalvin de Haan -- Nick Perbix\n\nMatt Tomkins\n\nJonas Johansson\n\n***Scratched:** Zach Bogosian, Michael Eyssimont*\n\n***Injured:** Andrei Vasilevskiy (back)*\n\n**Canadiens projected lineup**\n\nJuraj Slafkovsky -- Nick Suzuki -- Cole Caufield\n\nAlex Newhook -- Christian Dvorak -- Josh Anderson\n\nTanner Pearson -- Sean Monahan -- Brendan Gallagher\n\nMichael Pezzetta -- Jake Evans -- Joel Armia\n\nMike Matheson -- Jordan Harris\n\nKaiden Guhle -- Justin Barron\n\nArber Xhekaj -- Johnathan Kovacevic\n\nJake Allen\n\nSam Montembeault\n\n***Scratched:** Jesse Ylonen, Cayden Primeau*\n\n***Injured:** Raphael Harvey-Pinard (lower body), David Savard (hand)*\n\n**Status report**\n\nThe Lightning did not hold a morning skate following a 6-5 overtime loss at the Toronto Maple Leafs on Monday. ... Harvey-Pinard took part in the optional morning skate but the forward will miss his second straight game.\n\n## **RED WINGS (7-4-1) at RANGERS (8-2-1)**\n\n**7:30 p.m. ET; MAX, TNT, SNP, SNO, SNE, SN1**\n\n**Red Wings projected lineup**\n\nAlex DeBrincat -- Dylan Larkin -- Lucas Raymond\n\nDavid Perron -- J.T. Compher -- Andrew Copp\n\nRobby Fabbri -- Joe Veleno -- Daniel Sprong\n\nKlim Kostin -- Michael Rasmussen -- Christian Fischer\n\nJake Walman -- Moritz Seider\n\nBen Chiarot -- Justin Holl\n\nOlli Maatta -- Shayne Gostisbehere\n\nVille Husso\n\nJames Reimer\n\n***Scratched**: Alex Lyon, Jeff Petry, Austin Czarnik*\n\n***Injured**: None*\n\n**Rangers projected lineup**\n\nChris Kreider -- Mika Zibanejad -- Blake Wheeler\n\nArtemi Panarin -- Vincent Trocheck -- Alexis Lafreniere\n\nWill Cuylle -- Nick Bonino -- Kaapo Kakko\n\nJimmy Vesey -- Barclay Goodrow -- Tyler Pitlick\n\nK'Andre Miller -- Jacob Trouba\n\nRyan Lindgren -- Erik Gustafsson\n\nZac Jones -- Braden Schneider\n\nJonathan Quick\n\nLouis Domingue\n\n***Scratched**: Jonny Brodzinski, Connor Mackey*\n\n***Injured**: Adam Fox (lower body), Filip Chytil (upper body), Igor Shesterkin (soreness)*\n\n**Status report**\n\nLarkin is a game-time decision because of \"bumps and bruises,\" Red Wings coach Derek Lalonde said. Larkin skated Tuesday morning after missing practice Monday. If he can't play, Detroit could use 11 forwards and seven defensemen. … Fabbri will return after missing 11 games because of a lower-body injury he sustained during the season-opener Oct. 12. … Fischer is expected to play after missing the Red Wings' 5-4 win against the Boston Bruins on Saturday because of an upper-body injury. … Shesterkin will not dress for a second straight game. The goalie skated Tuesday morning and is day to day.\n\n## **WILD (4-5-2) at ISLANDERS (5-2-3)**\n\n**7:30 PM, MSGSN, BSWI, BSN**\n\n**Minnesota Wild projected lineup**\n\nKirill Kaprizov -- Marco Rossi -- Matt Boldy\n\nMarcus Johansson -- Ryan Hartman -- Mats Zuccarello\n\nMarcus Foligno -- Joel Eriksson Ek -- Pat Maroon\n\nBrandon Duhaime -- Connor Dewar -- Vinni Lettieri\n\nJonas Brodin -- Brock Faber\n\nJake Middleton -- Dakota Mermis\n\nDaemon Hunt -- Calen Addison\n\nMarc-Andre Fleury\n\nFilip Gustavsson\n\n***Scratched:** Nic Petan, John Merrill*\n\n***Injured:** Jared Spurgeon (upper body), Alex Goligoski (lower body), Frederik Gaudreau (upper body)*\n\n**Islanders projected lineup**\n\nAnders Lee -- Mathew Barzal -- Oliver Wahlstrom\n\nPierre Engvall -- Brock Nelson -- Kyle Palmieri\n\nSimon Holmstrom -- Jean-Gabriel Pageau -- Hudson Fasching\n\nMatt Martin -- Casey Cizikas -- Cal Clutterbuck\n\nAdam Pelech -- Noah Dobson\n\nAlexander Romanov -- Ryan Pulock\n\nSebastian Aho -- Scott Mayfield\n\nSemyon Varlamov\n\nIlya Sorokin\n\n***Scratched:** Julien Gauthier, Samuel Bolduc*\n\n***Injured:** Adam Pelech (lower body), Bo Horvat (lower body) *\n\n**Status report**\n\nPetan was recalled from Iowa of the American Hockey League on Sunday but the forward will not play. … Varlamov is expected to start after Sorokin made 42 saves in a 4-3 overtime loss to the Carolina Hurricanes on Saturday. … Pelech, a defenseman, and Horvat, a forward, are each day to day but were not ruled out for the game. … Mayfield missed practice Monday (maintenance) but is expected to play.\n\n## **JETS (5-4-2) at BLUES (5-4-1)**\n\n**8 p.m. ET; BSMW, TSN3**\n\n**Jets projected lineup**\n\nKyle Connor -- Mark Scheifele -- Alex Iafallo\n\nCole Perfetti -- Vladislav Namestnikov -- Nikolaj Ehlers\n\nNino Niederreiter -- Adam Lowry -- Mason Appleton\n\nMorgan Barron -- Rasmus Kupari -- David Gustafsson\n\nJosh Morrissey -- Dylan DeMelo\n\nBrenden Dillon -- Neal Pionk\n\nDylan Samberg -- Nate Schmidt\n\nConnor Hellebuyck\n\nLaurent Brossoit\n\n***Scratched: ****Dominic Toninato, Declan Chisholm, Logan Stanley*\n\n***Injured:**** Ville Heinola (ankle), Gabriel Vilardi (knee)*\n\n**Blues projected lineup**\n\nPavel Buchnevich -- Robert Thomas -- Kasperi Kapanen\n\nBrandon Saad -- Brayden Schenn -- Jordan Kyrou\n\nAlexey Toropchenko -- Kevin Hayes -- Jakub Vrana\n\nSammy Blais -- Oskar Sundqvist -- Jake Neighbours\n\nNick Leddy -- Colton Parayko\n\nTorey Krug -- Justin Faulk\n\nTyler Tucker -- Marco Scandella\n\nJordan Binnington\n\nJoel Hofer\n\n***Scratched:**** Robert Bortuzzo, Scott Perunovich, Nikita Alexandrov*\n\n***Injured: ****None*\n\n**Status report**\n\nHellebuyck will start for the 10th time in 12 games. ... Binnington will start for the eighth time in 11 games.\n\n## **KRAKEN (4-6-2) at COYOTES (5-5-1)**\n\n**9 p.m. ET; SCRIPPS, ROOT-NW**\n\n**Kraken projected lineup**\n\nJared McCann -- Matty Beniers -- Kailer Yamamoto\n\nJaden Schwartz -- Alex Wennberg -- Jordan Eberle\n\nEeli Tolvanen -- Yanni Gourde -- Oliver Bjorkstrand\n\nDevin Shore -- Pierre-Edouard Bellemare -- Tye Kartye\n\nVince Dunn -- Adam Larsson\n\nJamie Oleksiak -- Will Borgen\n\nBrian Dumoulin -- Justin Schultz\n\nJoey Daccord\n\nPhilipp Grubauer\n\n***Scratched:** Jaycob Megna*\n\n***Injured:** Brandon Tanev (lower body), Andre Burakovsky (upper body)*\n\n**Coyotes projected lineup**\n\nClayton Keller -- Barrett Hayton -- Nick Schmaltz\n\nMatias Maccelli -- Nick Bjugstad -- Lawson Crouse\n\nMichael Carcone -- Logan Cooley -- Travis Boyd\n\nLiam O'Brien -- Jack McBain -- Alex Kerfoot\n\nJ.J. Moser -- Sean Durzi\n\nTravis Dermott -- Matt Dumba\n\nJuuso Valimaki -- Troy Stecher\n\nConnor Ingram\n\nKarel Vejmelka\n\n***Scratched:** Josh Brown, Zach Sanford*\n\n***Injured:** Jason Zucker (lower body)*\n\n**Status report**\n\nKraken coach Dave Hakstol switched several lines, promoting Yamamoto from the fourth line to the top line with Beniers and McCann, and moving Kartye off the top line. ... Tanev took part in the morning skate but is not yet ready to return. The forward hasn't played since the season opener Oct. 10,. ... Daccord, a former Arizona State goalie, will make his first start since Oct. 28. Grubauer started the previous three games. ... Zucker is practicing and the forward could return against the Nashville Predators on Saturday. He will miss his seventh game since Oct. 21.\n\n## **PREDATORS (5-6-0) at FLAMES (3-7-1)**\n\n**9 p.m. ET; SNW, BSSO**\n\n**Predators projected lineup**\n\nFilip Forsberg -- Ryan O'Reilly -- Gustav Nyquist\n\nKiefer Sherwood -- Tommy Novak -- Luke Evangelista\n\nYakov Trenin -- Colton Sissons -- Cole Smith\n\nLiam Foudy -- Jusso Parssinen -- Michael McCarron\n\nRoman Josi -- Dante Fabbro\n\nJeremy Lauzon -- Alexandre Carrier\n\nMarc Del Gaizo -- Tyson Barrie\n\nJuuse Saros\n\nKevin Lankinen\n\n***Scratched:** Samuel Fagemo, Philip Tomasino*\n\n***Injured:** Ryan McDonagh (lower body), Luke Schenn (lower body), Cody Glass (lower body)*\n\n**Flames projected lineup**\n\nJonathan Huberdeau -- Elias Lindholm -- Dillon Dube\n\nConnor Zary -- Nazem Kadri -- Yegor Sharangovich\n\nMartin Pospisil -- Mikael Backlund -- Blake Coleman\n\nA.J. Greer -- Adam Ruzicka -- Walker Duehr\n\nMacKenzie Weegar -- Rasmus Andersson\n\nNoah Hanifin -- Chris Tanev\n\nNikita Zadorov -- Nick DeSimone\n\nJacob Markstrom\n\nDan Vladar\n\n***Scratched:** Dryden Hunt, Dennis Gilbert*\n\n***Injured:** Jakob Pelletier (shoulder), Kevin Rooney (upper body), Oliver Kylington (undisclosed)*\n\n***Suspended:** Andrew Mangiapane*\n\n**Status report**\n\nSaros is expected to start for the 10th time in 12 games this season. ... McCarron, a healthy scratch the past four games, could play in place of Tomasino, a forward. ... Ruzicka will return after missing four games because of a shoulder injury sustained during a 3-1 loss to the New York Rangers on Oct. 24. ... Mangiapane will serve a one-game suspension from the NHL Department of Player Safety. The forward cross-checked Seattle Kraken forward Jared McCann in the first period of a 6-3 win Saturday. ... Markstrom will make his fifth start in six games.\n\n## **PENGUINS (4-6-0) at DUCKS (7-4-0)**\n\n**10 p.m. ET; SN-PIT, BSSD, BSSC, TVAS**\n\n**Penguins projected lineup**\n\nJake Guentzel -- Sidney Crosby -- Bryan Rust\n\nReilly Smith -- Evgeni Malkin -- Rikard Rakell\n\nDrew O'Connor -- Lars Eller -- Radim Zohorna\n\nMatt Nieto -- Noel Acciari -- Vinnie Hinostroza\n\nRyan Graves -- Kris Letang\n\nMarcus Pettersson -- Erik Karlsson\n\nRyan Shea -- Chad Ruhwedel\n\nTristan Jarry\n\nMagnus Hellberg\n\n***Scratched**: Jeff Carter*\n\n***Injured**: John Ludvig (concussion), Alex Nedeljkovic (lower body)*\n\n**Ducks projected lineup**\n\nTrevor Zegras -- Leo Carlsson -- Troy Terry\n\nFrank Vatrano -- Mason McTavish -- Ryan Strome\n\nAlex Killorn -- Adam Henrique -- Jakob Silfverberg\n\nRoss Johnston -- Sam Carrick -- Brett Leason\n\nCam Fowler -- Jackson LaCombe\n\nPavel Mintyukov -- Ilya Lyubushkin\n\nUrho Vaakanainen -- Radko Gudas\n\nJohn Gibson\n\nLukas Dostal\n\n***Scratched**: Benoit-Olivier Groulx, Max Jones*\n\n***Injured**: Jamie Drysdale (lower body), Brock McGinn (lower body), Isac Lundestrom (Achilles), Chase De Leo (knee)*\n\n**Status report**\n\nThe Penguins did not hold a morning skate. ... Carter, a forward, will be a healthy scratch for the second straight game and second time in the NHL. Hinostroza again will take his spot on the fourth line. ... Ludvig has been skating in Pittsburgh. The defenseman was injured during his first game of the season, a 4-1 loss to the Dallas Stars on Oct. 24. ... Nedeljkovic also has been skating in Pittsburgh. The goalie was placed on long-term injured reserve Oct. 25, one day after he was injured against the Stars. The earliest Nedeljkovic could return is Nov. 19 against the Vegas Golden Knights ... The Ducks will stick with the same lineup they used in a 4-2 win against the visiting Vegas Golden Knights on Sunday.\n\n## **DEVILS (7-3-1) at AVALANCHE (7-3-0)**\n\n**10 p.m. ET; MAX, TNT, SNP, SNO, SNE, SN1**\n\n**Devils projected lineup**\n\nTyler Toffoli -- Michael McLeod -- Jesper Bratt\n\nOndrej Palat -- Dawson Mercer -- Timo Meier\n\nMax Willman -- Erik Haula -- Curtis Lazar\n\nAlexander Holtz -- Chris Tierney -- Nathan Bastian\n\nJonas Siegenthaler -- Dougie Hamilton\n\nKevin Bahl -- John Marino\n\nBrendan Smith -- Luke Hughes\n\nVitek Vanecek\n\nAkira Schmid\n\n***Scratched:*** *Cal Foote*\n\n***Injured:*** *Jack Hughes (shoulder), Nico Hischier (upper body), Tomas Nosek (lower body), Colin Miller (lower body)*\n\n**Avalanche projected lineup**\n\nJonathan Drouin -- Nathan MacKinnon -- Mikko Rantanen\n\nArtturi Lehkonen -- Ryan Johansen -- Valeri Nichushkin\n\nMiles Wood -- Ross Colton -- Logan O'Connor\n\nAndrew Cogliano -- Ondrej Pavel -- Tomas Tatar\n\nDevon Toews -- Cale Makar\n\nBowen Byram -- Samuel Girard\n\nJack Johnson -- Josh Manson\n\nAlexandar Georgiev\n\nIvan Prosvetov\n\n***Scratched:*** *Kurtis MacDermid*\n\n***Injured:*** *Fredrik Olofsson (upper body)*\n\n**Status report**\n\nAvalanche coach Jared Bednar missed practice Monday and the morning skate Tuesday because of an illness but is expected to coach the game, according to assistant Nolan Pratt. ... Pavel, who was recalled from Colorado of the American Hockey League on Monday, is expected to make his NHL debut. … Olofsson, a forward, is day to day.\n\n## **FLYERS (5-6-1) at SHARKS (0-10-1)**\n\n**10:30 p.m. ET; NBCSP, NBCSCA**\n\n**Flyers projected lineup**\n\nOwen Tippett -- Sean Couturier -- Tyson Foerster\n\nTravis Konecny -- Noah Cates --  Cam Atkinson\n\nJoel Farabee -- Scott Laughton -- Bobby Brink\n\nNicolas Deslauriers -- Ryan Poehling -- Garnet Hathaway\n\nCam York -- Travis Sanheim\n\nNick Seeler -- Sean Walker\n\nEgor Zamula -- Louie Belpedio\n\nSamuel Ersson\n\nCal Petersen\n\n***Scratched: ****Morgan Frost, Victor Mete*\n\n***Injured: ****Carter Hart (mid-body), Rasmus Ristolainen (undisclosed), Marc Staal (upper body), Felix Sandstrom (upper body)*\n\n**Sharks projected lineup**\n\nWilliam Eklund -- Tomas Hertl -- Fabian Zetterlund\n\nAnthony Duclair -- Mikael Granlund -- Luke Kunin\n\nJacob MacDonald -- Nico Sturm -- Kevin Labanc\n\nGivani Smith -- Ryan Carpenter -- Filip Zadina\n\nMario Ferraro -- Kyle Burroughs\n\nNikolai Knyzhov -- Jan Rutta\n\nMarc-Edouard Vlasic -- Nikita Okhotiuk\n\nMackenzie Blackwood\n\nKaapo Kahkonen\n\n***Scratched: ****Ty Emberson, Mike Hoffman*\n\n***Injured:**** Logan Couture (lower body), Alexander Barabanov (broken finger), Matt Benning (undisclosed)*\n\n**Status report**\n\nThe Flyers held an optional morning skate. ... Couturier will play after missing two games because of a lower-body injury. ... Ersson will start after Peterson made 25 saves in a 5-0 loss to the Los Angeles Kings on Saturday. ... Mete was recalled from Lehigh Valley of the American Hockey League on Monday but the defenseman will not play. ... Blackwood will start after giving up six goals on 18 shots in a 10-2 loss to the Pittsburgh Penguins on Saturday.","datePublished":"2023-11-07T19:38:00Z","dateModified":"2023-11-07T20:30:47.944Z","author":{"@type":"Person","name":"NHL.com @NHLdotcom","url":""},"@context":"https://schema.org"}

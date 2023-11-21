#TODO: extract all 3rd party API requests from API
#TODO: extract all database storage functionality from API
import sys, getopt

#TODO: (sqlite3.OperationalError) near "ON": syntax error is usually the error
#provided when there's no games today, which means there's no data to insert.

import scrapers
import writers

def handleError( error ):
    try:
        if type( error ).__name__ == 'OperationalError':
            print( 'Operational Errors are usually due to trying to execute an INSERT without data.')
        print( f'There was an error: {type(error).__name__}: {str(error)}')
    except Exception as e:
        print( f'The was an error in the error handler. {str(e)}')

def main( argv ):
    doSchedule = True
    doInjury = True
    doTeams = True
    doSkaters = True
    opts, args = getopt.getopt(argv[1:],"hs:i:t:p:",["schedule=","injuries=","teams=","players="])
    for opt, arg in opts:
        if opt == '-h':
            print ('data_scraper.py [-s <Y|N>] [-i <Y|N] [-t <Y|N] [-p <Y|N]')
            print( 'Y or N are not case sensitive.  They indicate if the data should be fetched')
            print( 'and stored.  Anything other than "Y" is considered "don\'t fetch"')
            sys.exit()
        
        elif opt in ("-s", "--schedule"):
            doSchedule = True if arg.upper() == 'Y' else False
        elif opt in ("-i", "--injuries"):
            doInjury = True if arg.upper() == 'Y' else False
        elif opt in ("-t", "--teams"):
            doTeams = True if arg.upper() == 'Y' else False
        elif opt in ("-p", "--players"):
            doSkaters = True if arg.upper() == 'Y' else False
        
    ##################### SCHEDULE
    if doSchedule:
        try:
            print( 'Fetching schedule.' )
            scheduleData = scrapers.schedule_scraper()
            print( 'Writing schedule.' )
            writers.schedule_writer( scheduleData )
        except Exception as e:
            print( 'There is an issue with schedules.  Skipping.')
            handleError( e )

    ##################### INJURY
    #TODO: determin which INJURY report to take if there are duplicates - which 
    # there should be.  bell media/TSN data seems to be more accurate - NHL has 
    # scratches and some players that are not on the Bell/TSN list, but the same
    # can be said regarding vice-versa
    if doInjury:
        try:    
            print( 'Fetching injuries.' )
            injuryData = scrapers.injury_scraper()
            print( 'Writing injuries' )
            writers.injury_writer( injuryData )
        except Exception as e:
            print( 'There is an issue with injuries.  Skipping.')
            handleError( e )

    ##################### TEAMS
    if doTeams:
        try:
            print( 'Fetching teams.' )
            teamsData = scrapers.teams_scraper()
            print( 'Writing teams.' )
            writers.teams_writer( teamsData )
        except Exception as e:
            print( 'There is an issue with teams.  Skipping.')
            handleError( e )

    ##################### SKATERS
    if doSkaters:
        try:
            print( 'Fetching skaters.' )
            skatersData = scrapers.skaters_scraper()
            print( 'Writing skaters.' )
            writers.skaters_writer( skatersData )
        except Exception as e:
            print( 'There is an issue with skaters.  Skipping.')
            handleError( e )

if __name__ == '__main__':
    try:
        main( sys.argv)
    except Exception as e:
        handleError( e )
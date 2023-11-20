#TODO: extract all 3rd party API requests from API
#TODO: extract all database storage functionality from API

import scrapers
import writers


##################### SCHEDULE
doSchedule = False
if doSchedule:
    print( 'Fetching schedule.' )
    scheduleData = scrapers.schedule_scraper()
    print( 'Writing schedule.' )
    writers.schedule_writer( scheduleData )

##################### INJURY
#TODO: determin which INJURY report to take if there are duplicates - which 
# there should be.  bell media/TSN data seems to be more accurate - NHL has 
# scratches and some players that are not on the Bell/TSN list, but the same
# can be said regarding vice-versa
doInjury = False
if doInjury:
    print( 'Fetching injuries.' )
    injuryData = scrapers.injury_scraper()
    print( 'Writing injuries' )
    writers.injury_writer( injuryData )

##################### TEAMS
doTeams = False
if doTeams:
    print( 'Fetching teams.' )
    teamsData = scrapers.teams_scraper()
    print( 'Writing teams.' )
    writers.teams_writer( teamsData )

##################### SKATERS
doSkaters = True
if doSkaters:
    print( 'Fetching skaters.' )
    skatersData = scrapers.skaters_scraper()
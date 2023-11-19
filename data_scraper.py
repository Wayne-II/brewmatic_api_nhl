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
#TODO: merge NHL injury report data as it becomes available to the bell media data 
doInjury = False
if doInjury:
    print( 'Fetching injuries.' )
    injuryData = scrapers.injury_scraper()
    print( 'Writing injuries' )
    writers.injury_writer( injuryData )

##################### TEAMS
doTeams = True
if doTeams:
    print( 'Fetching teams.' )
    teamsData = scrapers.teams_scraper()
    print( 'Writing teams.' )
    writers.teams_writer( teamsData )

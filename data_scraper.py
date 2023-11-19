#TODO: extract all 3rd party API requests from API
#TODO: extract all database storage functionality from API

import scrapers
import writers


##################### SCHEDULE
doSchedule = True
if doSchedule:
    scheduleData = scrapers.schedule_scraper()
    writers.schedule_writer( scheduleData )

##################### INJURY
#TODO: merge NHL injury report data as it becomes available to the bell media data 
doInjury = True
if doInjury:
    injuryData = scrapers.injury_scraper()
    writers.injury_writer( injuryData )

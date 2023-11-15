#TODO: extract all 3rd party API requests from API
#TODO: extract all database storage functionality from API

import scrapers
import writers

scheduleData = scrapers.schedule_scraper()
writers.schedule_writer( scheduleData )

print( scheduleData )
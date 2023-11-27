# TODO: NHL took down statsapi.web.nhl.com today.  Have to figure out solutions
# using the newer api-web.nhle.com website.  
# potential solutions:
# ~~~~~ TEAMS ~~~~~
# https://api-web.nhle.com/v1/schedule-calendar/2023-11-07

#TODO: error handling, design docs, tests, etc

#TODO: set up gitlabs on local server - use github private repo as source
# backup

#TODO: set up server to run API via WSGI on apache or something with CORS
# enabled

#POC: this is a proof of concept v2 using NHL public API instead of table
#scaraping hockeyreference.com

#investigate https://statsapi.web.nhl.com/api/v1/configurations
#figured out more to the NHL stats API able to get all player stats for a give shcedule with a single request.
#https://statsapi.web.nhl.com/api/v1/teams/?teamId=3,4,5&stats=statsSingleSeason&season=20232024&expand=team.roster,roster.person,person.stats
#descriptions below
#?teamId=3,4,5 - identifies which teams to get stats for - comma separated
#&stats=statsSingleSeason - identifies which stats to get - list at https://statsapi.web.nhl.com/api/v1/statTypes
#&season=20232024 - used for statsSingleSeason above to identify season ( <season year start><season year end> )
#
#this is the magic bit - expands can be chained with commas
#
#&expand=team.roster,roster.person,person.stats
#
# By fetching data for teams identified by teamId I can expand the roster
# with teams.roster.  
#
# By having the roster expanded, I can expand the people with roster.person
# as the second expand chain.
#
# Since the people in the roster are expanded, I can fetch all stats for
# each person by adding person.stats as the last to the chain.
#
# Due to the nature of stats, the stats parameter must be set as well as
# any other requirements for the give statType
#
#Upon further investigation, a single request can be sent for the schedule, 
#the teams playing, the roster for teams, the people details, and people 
#stats.  The only problem is that the browser runs out of memory in the
#browser if you don't include a date for the schedule ;)  Otherwise 15 games
#including each game's teams, each team's stats, each team's roster, and each 
#roster's person and each person's stats will take about 2.34MB.  There's
#only 32 teams in the NHL
#
#"https://statsapi.web.nhl.com/api/v1/schedule/
#?expand=
#   schedule.teams,
#   team.roster,
#   team.stats,
#   roster.person,
#   person.stats
#&stats=statsSingleSeason
#&season=20232024
#&date=YYYY-MM-DD

from dotenv import load_dotenv
load_dotenv('.env')

from flask import Flask
from routes import api

app = Flask(__name__)
api.init_app( app )


if __name__ == '__main__':
    app.run( host='0.0.0.0')
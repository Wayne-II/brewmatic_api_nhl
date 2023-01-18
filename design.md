the api will prefix all endpoints with /nhl/<int:year>

The NHL API is documented here: https://gitlab.com/dword4/nhlapi/-/blob/master/

the API needs to provide consistent responses whether or not the data has already been fetched from the NHL official API.  When data is fetched from the NHL API, it should be stored in the database unless it already exists.

subsequent endpoints will be:
/teams
/skaters
/suggest
/schedule

/teams will have the following endpoints
/teams will return all teams for the prefix year
/teams/<int:id> will provide a list of information about the team based on the NHL API Team ID
/teams/<int:id>/roster will return all skaters for the given year and team ID ( teams/1?expand=team.roster )("rosterStatus" : "I" is injured)
The following is a raw snippet response from the NHL API endpoint: https://statsapi.web.nhl.com/api/v1/teams.  Providing an ID after teams endpoint will provide this information for the identified team object within the "teams" list snipped below
"teams" : [ {
    "id" : 1,
    "name" : "New Jersey Devils",
    "link" : "/api/v1/teams/1",
    "venue" : {
      "name" : "Prudential Center",
      "link" : "/api/v1/venues/null",
      "city" : "Newark",
      "timeZone" : {
        "id" : "America/New_York",
        "offset" : -5,
        "tz" : "EST"
      }
    },
    "abbreviation" : "NJD",
    "teamName" : "Devils",
    "locationName" : "New Jersey",
    "firstYearOfPlay" : "1982",
    "division" : {
      "id" : 18,
      "name" : "Metropolitan",
      "nameShort" : "Metro",
      "link" : "/api/v1/divisions/18",
      "abbreviation" : "M"
    },
    "conference" : {
      "id" : 6,
      "name" : "Eastern",
      "link" : "/api/v1/conferences/6"
    },
    "franchise" : {
      "franchiseId" : 23,
      "teamName" : "Devils",
      "link" : "/api/v1/franchises/23"
    },
    "shortName" : "New Jersey",
    "officialSiteUrl" : "http://www.newjerseydevils.com/",
    "franchiseId" : 23,
    "active" : true
  }, ... ]

/skaters will have the following endpoints
/skaters will return all the skaters for the given year
/skaters/<int:skater_id> will get all data for a given skater

/suggest will provide access to the NHL API suggestion API.
/suggest/<string:name>/<int:count> will fetch up to <count> suggestions for <name> portion of a name
Example: /suggest/ilya/100 will return a subset of this raw NHL data:
{"suggestions":[
    "8482792|Fedotov|Ilya|1|1|6\u0027 0\"|176|Saratov||RUS|2003-03-19|ARI|L||ilya-fedotov-8482792",
    "8480950|Lyubushkin|Ilya|1|0|6\u0027 2\"|200|Moscow||RUS|1994-04-06|BUF|D|46|ilya-lyubushkin-8480950",
    "8481624|Mikheyev|Ilya|1|0|6\u0027 2\"|192|Omsk||RUS|1994-10-10|VAN|R|65|ilya-mikheyev-8481624",
    "8481590|Nikolaev|Ilya|1|1|6\u0027 0\"|190|Yaroslavl||RUS|2001-06-26|CGY|C|77|ilya-nikolaev-8481590",
    "8468511|Nikulin|Ilya|1|0|6\u0027 1\"|210|Moscow||RUS|1982-03-12|WPG|D||ilya-nikulin-8468511",
    "8482915|Safonov|Ilya|1|1|6\u0027 4\"|205|Moscow||RUS|2001-05-30|CHI|C||ilya-safonov-8482915",
    "8478492|Samsonov|Ilya|1|0|6\u0027 3\"|214|Magnitogorsk||RUS|1997-02-22|TOR|G|35|ilya-samsonov-8478492",
    "8482470|Solovyov|Ilya|1|1|6\u0027 3\"|208|Mogilev||BLR|2000-07-20|CGY|D|98|ilya-solovyov-8482470",
    "8478009|Sorokin|Ilya|1|0|6\u0027 3\"|195|Mezhdurechensk||RUS|1995-08-04|NYI|G|30|ilya-sorokin-8478009",
    "8483408|Usau|Ilya|1|1|6\u0027 1\"|183|Minsk||BLR|2001-08-03|TBL|C||ilya-usau-8483408"
]}
The above snippet is a result of the following NHL API request URL: https://suggest.svc.nhl.com/svc/suggest/v1/minactiveplayers/ilya/100

/schedule will provide a list of games for the day with data. There is an endpoint provided by NHL API for this data and it can be filtered for the given day ?date=YYYY-MM-DD
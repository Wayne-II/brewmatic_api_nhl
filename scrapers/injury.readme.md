NHL Projected Lineup data is also in JSON but it's contained within a <script>
tag.  So beautiful soup is required to process the fetched HTML.  The JSON is
not in an easily readable format and has "formatting" characters similar to
markdown eg `***` makes something bold. and `**`makes it italic.  This is
processed using RegEx - which is not ultra reliable as the data frequently has
errors in the formatting, spaces in unusual spaces, etc.  The benefit to the NHL
projected lineups injury data is they have a "scratched" list as well.
Scratched players may or may not play.  However, it appears it's inconsistent as
some players that are out due to illness are marked as scratched, but not all
players that are out due to illness are marked as scratched.  Some are marked
as injured.  There are some players that are on one list but not the other, so
the datasets will have to be merged.  Using player IDs should help with this.


Bellmedia/TSN data is retreived from an API that returns JSON.

https://stats.sports.bellmedia.ca/sports/hockey/leagues/nhl/playerInjuries?brand=tsn&type=json
```JSON
sample = [
   {
      "id":"NHL:2023:181",
      "season":2023,
      "competitor":{
         "id":"NHL:181",
         "competitorId":181,
         "name":"Anaheim Ducks",
         "clubFR":"Ducks",
         "shortName":"ANA",
         "shortNameFR":"ANA",
         "points":18,
         "club":"Ducks",
         "recordOverall":"9-8-0",
         "streak":"L2",
         "ranking":"4th Pacific",
         "rankingFr":"4e Pacifique",
         "seoIdentifier":"anaheim-ducks",
         "seoIdentifierFr":"ducks-anaheim",
         "place":4,
         "seed":8,
         "location":"Anaheim",
         "locationFR":"Anaheim",
         "primaryColor":"F47A38"
      },
      "playerInjuries":[
         {
            "competitorId":181,
            "player":{
               "id":"NHL:376477",
               "playerId":376477,
               "sportId":2,
               "competitorId":181,
               "displayName":"Trevor Zegras",
               "firstName":"Trevor",
               "lastName":"Zegras",
               "seoIdentifier":"trevor-zegras-376477",
               "number":11,
               "position":"Left Wing",
               "positionFr":"Ailier gauche",
               "positionShort":"LW",
               "positionShortFr":"AG",
               "country":"United States",
               "playerStatus":"false",
               "teamSeoIdentifier":"anaheim-ducks",
               "age":22
            },
            "date":"2023-11-10",
            "status":"IR",
            "statusFr":"Liste des blessés",
            "description":"Lower-body injury",
            "descriptionFr":"Blessure au bas du corps"
         },
      ]
   }
]```
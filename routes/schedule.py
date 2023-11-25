from flask_restx import Namespace, Resource
from common import GetDateString
import models
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_

#fetch data from the database
def RetrieveData():
    today = GetDateString()
    Session = sessionmaker( models.engine )
    data = []
    with Session() as session:
        #Get all the schedules - each game will come back with 2 rows.  This
        #isn't ideal, however, subqueries would be required to get the home
        #tri_code and the away tri_code in a single row.  This would
        #probably be faster in SQL, as it's optimized for such operations.
        scheduleQuery = session.query(
            models.Schedule.id, 
            models.Schedule.away_id,
            models.Schedule.home_id,
            models.Schedule.game_date,
            models.Team.team_id,
            models.Team.tri_code
        ).filter_by( 
            game_date = today
        ).join(
            models.Team,
            or_( models.Schedule.away_id == models.Team.team_id, models.Schedule.home_id == models.Team.team_id )
        ).order_by(
            models.Schedule.id.desc()
        )
        scheduleResult = session.execute( scheduleQuery ).all()
        #this is the tricky park.  WIll have to do a 2 pass processing 
        currentGameId = None
        SCHID = 0
        AID = 1
        HID = 2
        GD = 3
        TID = 4
        TRI = 5
        game = {}
        print( scheduleResult)
        for datum in scheduleResult:
            awayId = datum[AID]
            homeId = datum[HID]
            teamId = datum[TID]
            gameId = datum[SCHID]
            triCode = datum[TRI]
            #reset if new game detected
            if gameId != currentGameId:
                #add game if this isn't the first game
                if currentGameId is not None:
                    data.append( game )
                game = {}
                currentGameId = gameId
            #set current game away or home data
            if teamId == awayId:
                game[ 'awayTeam' ] = {
                    'id': awayId,
                    'abbrev':triCode
                }
            elif teamId == homeId:
                game[ 'homeTeam' ] = {
                    'id': homeId,
                    'abbrev': triCode
                }
            else:
                #TODO: throw it has to be one or the other
                pass
        #add the last game we built to the result data
        data.append( game )
    return data

api = Namespace( "schedule" )
@api.route("/")
class Schedule( Resource ):
    def get( self ):
        ret = []
        ret = RetrieveData()
        return ret
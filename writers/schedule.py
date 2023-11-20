import models
#TODO separate Database common functions from "other" functions
from common import GetDate
from sqlalchemy.orm import sessionmaker

def StoreData( scheduleData ):
    today = GetDate()
    Session = sessionmaker( models.engine )
    with Session() as session:
        scheduledGames = []
        for game in scheduleData:
            scheduledGames.append( { 
                'home_id': game[ 'homeTeam' ][ 'id' ],
                'away_id': game[ 'awayTeam' ][ 'id' ],
                'game_date': today
            } )
        insert = models.GetInsert( session )
        scheduleInsert = insert(
            models.Schedule
        ).values(
            scheduledGames
        )

        scheduleInsertConflict = scheduleInsert.on_conflict_do_nothing(
            index_elements=['home_id','away_id']
        )

        session.execute( scheduleInsertConflict )
        session.commit()

from sqlalchemy.orm import sessionmaker
import models
from common import GetDate, GetInsert, GetDateString

def StoreData( skaterData ):
    Session = sessionmaker( models.engine )
    with Session() as session:
        skatersInsert = StoreSkatersQuery( skaterData, session )
        session.execute( skatersInsert )
        session.commit()

def StoreSkatersQuery( skaters, session ):
    insertData = []
    today = GetDate()

    skaterIds = []
    for skater in skaters:
        #make sure 3rd party API doesn't produce duplicates for the same player
        #as the result would be a postgres integrity check with the on conflict
        #clause resulting in a failed insert.
        if skater[ 'playerId' ] not in skaterIds:
            insertData.append( {
                'id':skater[ 'playerId' ],
                'skater_full_name':skater[ 'skaterFullName' ],
                'goals':skater[ 'goals' ],
                'last_name': skater[ 'lastName' ],
                'updated': today,
                'team_abbrevs': skater[ 'teamAbbrevs' ]
            } )
            skaterIds.append( skater[ 'playerId' ] )
    insert = GetInsert( session )

    insertQuery = insert( 
        models.Skater 
    ).values( 
        insertData 
    )
    
    insertConflictQuery = insertQuery.on_conflict_do_update(
        index_elements=[ 'id' ],
        set_ = {
            'goals': insertQuery.excluded.goals,
            'updated': insertQuery.excluded.updated,
            #TODO: used for now as UI depends on it.  will fix UI as it used old API data structures
            'team_abbrevs':insertQuery.excluded.team_abbrevs
        }
    )
    
    return insertConflictQuery
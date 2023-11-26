import models
#TODO separate Database common functions from "other" functions
from common import GetDate
from sqlalchemy.orm import sessionmaker

def StoreData( injuryData ):
    today = GetDate()
    Session = sessionmaker( models.engine )
    with Session() as session:
        injuries = []
        skaterIds = []
        for injury in injuryData:
            #due to the nature of multiple 3rd party sources from completeness
            #of the injury data, there will be several duplicates which will
            #result in the integrity check failing for postgres as postgres
            #can't guarantee in which order multiple updates will occur - even
            #though it doesn't matter in this case.  There may be an issue where
            #one data source has them marked as injured whereas the other data
            #source has them marked as scratched - I've seen this with illness
            #as the reason.  It might be worth tracking which data source the
            #duplicate is from and replacing the lesser source with the more
            #confidence instilling source.  For now - just skip.  It compiles!
            #Ship!
            if injury[ 'skater_id' ] not in skaterIds and int( injury[ 'skater_id' ] ) != 0:
                injuries.append( {
                'skater_id': injury[ 'skater_id' ],
                'status': injury[ 'status' ],
                'updated': today,
                'injury_type': injury[ 'injury_type' ],
                } )
                skaterIds.append( injury[ 'skater_id' ] )
            if int( injury[ 'skater_id' ] ) == 0 and 'player_status' in injury.keys() and injury[ 'player_status' ] != 'false':
                #TODO: figure out issues with not having goalies in the skaters
                #list as well as players that haven't played yet this season.
                #Otherwise it seems the only reason their ID is 0 in the local 
                #database is their player_status is 'false' - their in a junior
                #league or long term injury.
                pass
        insert = models.GetInsert( session )
        injuryInsert = insert(
            models.Injury
        ).values(
            injuries
        )

        injuryInsertConflict = injuryInsert.on_conflict_do_update(
            index_elements=[ 'skater_id' ],
            set_= {
                'status': injuryInsert.excluded.status,
                'updated': injuryInsert.excluded.updated,
                'injury_type': injuryInsert.excluded.injury_type
            }
        )

        session.execute( injuryInsertConflict )
        session.commit()

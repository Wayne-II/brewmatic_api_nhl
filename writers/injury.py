import models
#TODO separate Database common functions from "other" functions
from common import GetDate
from sqlalchemy.orm import sessionmaker

def StoreData( injuryData ):
    
    Session = sessionmaker( models.engine )
    with Session() as session:
        injuries = []

        for injury in injuryData:
            injuries.append( {
            'skater_id': injury[ 'skater_id' ],
            'status': injury[ 'status' ],
            'updated': injury[ 'updated' ],
            'injury_type': injury[ 'injury_type' ],
            } )
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

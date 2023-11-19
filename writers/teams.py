from sqlalchemy.orm import sessionmaker
import models
from common import GetDate, GetInsert


def StoreData( teamData ):
    Session = sessionmaker( models.engine )
    with Session() as session:
        teamsInsert = GenerateTeamsQuery( teamData, session )
        session.execute( teamsInsert )
        for team in teamData:
            rosterInsert = GenerateRosterQuery( 
                skaterIds = team[ 'roster' ], 
                teamId = team[ 'teamId' ],
                session = session
            )
            session.execute( rosterInsert )
        session.commit()

#Store team data, including tri code
def GenerateTeamsQuery( teams, session ):
    today = GetDate()
    insertData = []
    for team in teams:
        insertData.append( {
            "team_id" : team[ 'teamId' ],
            "losses" : team[ 'losses' ] or 0,
            "ot_losses" : team[ 'otLosses' ] or 0,
            "team_full_name" : team[ 'teamFullName' ],
            "ties" : team[ 'ties' ] or 0,
            "wins" : team[ 'wins' ] or 0,
            "wins_in_regulation" : team[ 'winsInRegulation' ] or 0,
            "tri_code" : team[ 'triCode' ],
            "updated" : today
        } )

    insert = GetInsert( session )
    
    insertQuery = insert( 
        models.Team 
    ).values( 
        insertData 
    )

    insertConflictQuery = insertQuery.on_conflict_do_update(
        index_elements=[ 'team_id' ],
        set_ = {
            "losses" : insertQuery.excluded.losses,
            "ot_losses" : insertQuery.excluded.ot_losses,
            "ties" : insertQuery.excluded.ties,
            "wins" : insertQuery.excluded.wins,
            "wins_in_regulation" : insertQuery.excluded.wins_in_regulation,
            "updated" : today
        }
    )

    return insertConflictQuery

#generate UPSERT query for roster
def GenerateRosterQuery( skaterIds, teamId, session ):
    insertData = []
    today = GetDate()
    for skaterId in skaterIds:
        insertData.append( {
            'skater_id': skaterId,
            'team_id': teamId,
            'updated': today
        } )
    insert = GetInsert( session )
    
    insertQuery = insert( 
        models.Roster 
    ).values( 
        insertData 
    )

    insertConflictQuery = insertQuery.on_conflict_do_update(
        index_elements=[ 'skater_id' ],
        set_ = {
            'team_id': insertQuery.excluded.team_id,#excluded not required, team ID doesn't change within scope
            'updated': today
        }
    )
    return insertConflictQuery
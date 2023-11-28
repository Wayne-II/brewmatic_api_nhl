import cgi
from datetime import date
import models
from sqlalchemy.orm import sessionmaker
import sqlalchemy

print( 'Content-type: text/html' )

def GetTable( tableName ):
    if tableName == 'schedule':
        return models.Schedule
    elif tableName == 'injuries':
        return models.Injury
    if tableName == 'teams':
        return models.Team
    if tableName == 'skaters':
        return models.Skater
    if tableName == 'roster':
        return models.Roster

def GetColumn( table ):
    if isinstance( table, models.Schedule ):
        return table.game_date
    if isinstance( table, models.Injury ):
        return table.updated
    if isinstance( table, models.Team ):
        return table.updated
    if isinstance( table, models.Skater ):
        return table.updated
    if isinstance( table, models.Roster ):
        return table.updated
    

def main():

    form = cgi.FieldStorage()
    password = "super_date_osbourne_can_haz_chezburger"
    tableName = form.getvalue( 'table' )
    if isinstance( tableName, list ):
        tableName = tableName[ 0 ]

    updated = form.getvalue( 'updated' )
    if isinstance( updated, list ):
        updated = updated[ 0 ]
    updated = str( updated ).split( '-' )

    if len( updated ) != 3:
        print( 'Updated my be in the format: YYYY-MM-DD' )
        exit()
    updatedDate = date( updated[ 0 ], updated[ 1 ], updated[ 2 ] )

    formPassword = form.getvalue( 'password' )
    if isinstance( formPassword, list ):
        formPassword = formPassword[ 0 ]
    formPassword = str( formPassword )

    if formPassword == password:
        Session = sessionmaker( models.engine )
        table = GetTable( tableName )
        column = GetColumn( table )
        with Session() as session:
            delete = session.delete( 
                table
            ).where(
                column == updatedDate
            )
        print( f'Built query using: table name: {tableName} column: {updated}')
        print( f'Query: {str( delete )}')
        session.execute( delete )

    
main()


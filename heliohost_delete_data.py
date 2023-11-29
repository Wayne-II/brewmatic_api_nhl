#!/usr/bin/python3.10
print( "Content-type: text/html\n\n" )

import cgi
from datetime import date
import models
from sqlalchemy.orm import sessionmaker
import sqlalchemy

def GetTable( tableName ):
    try:
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
    except Exception as e:
        print( f'There was an issue determining the table: {str(e)}' )

def GetColumn( table ):
    try:
        if type( table) == type( models.Schedule ):
            return table.game_date
        if type( table ) == type( models.Injury ):
            return table.updated
        if type( table ) == type( models.Team ):
            return table.updated
        if type( table ) == type( models.Skater ):
            return table.updated
        if type( table ) == type( models.Roster ):
            return table.updated
    except Exception as e:
        print( f'There was an issue determining the column: {str(e)}' )

def main():
    password = "super_dave_osbourne_can_haz_chezburger"
    tableName = ''
    updated = ''

    get = cgi.parse()
    print( f'parameters sent: {get}')
    try:
        getTable = get[ 'table' ]
        getUpdated = get[ 'updated' ] 
        getPassword = get[ 'password' ]
    except Exception as e:
        print( f'There was an issue with a required parameter: {str(e)}' )

    try:
        if isinstance( getTable, list ):
            tableName = getTable[ 0 ]

        if isinstance( getUpdated, list ):
            updated = getUpdated[ 0 ]

        updatedParts = str( updated ).split( '-' )

        if len( updatedParts ) != 3:
            print( f'Updated my be in the format: YYYY-MM-DD {updatedParts}' )
            exit()
        updatedDate = date( int( updatedParts[ 0 ] ), int( updatedParts[ 1 ] ), int( updatedParts[ 2 ] ) )

        if isinstance( getPassword, list ):
            formPassword = getPassword[ 0 ]
        formPassword = str( formPassword )
    except Exception as e:
        print( f'There was an issue processing the required parameters: {str(e)}' )
    
    try:
        if formPassword == password:
            tableName = 'schedule'
            Session = sessionmaker( models.engine )
            
            with Session() as session:
                table = GetTable( tableName )
                column = GetColumn( table )
                query = session.query( table ).filter( column == updated)
                print( f'Query for deletion: {str(query)}')
                query.delete()
                session.commit()
    except Exception as e:
        print( f'There was an issue with the database {str(e)}')

try:    
    main()
    print( 'All Done' )
except Exception as e:
    print( f'uncaught exception: {str(e)}')
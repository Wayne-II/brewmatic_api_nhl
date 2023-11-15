from sqlalchemy import create_engine
import os
#TODO read environment variable for production.  production deployment will
#set the production environment variable.
production = False if True else True
devDbRelativePath = 'brewmatic.db'
devEnginePath = 'sqlite:///' + os.path.abspath( devDbRelativePath )
prodEnginePath = ''#TODO postgres database engine path

enginePath = devEnginePath if not production else prodEnginePath
engine = create_engine( enginePath )


from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.dialects.postgresql import insert as pgsql_insert
#TODO: remove from API routes and common functions
#TODO: maybe move it to models common
def GetInsert( session ):
    return sqlite_insert if session.bind.dialect.name == 'sqlite' else  pgsql_insert


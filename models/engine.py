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

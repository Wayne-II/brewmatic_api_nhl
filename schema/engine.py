from sqlalchemy import create_engine
import os

production = False
devDbRelativePath = 'brewmatic.db'
devEnginePath = 'sqlite:///' + os.path.abspath( devDbRelativePath )
prodEnginePath = ''#TODO postgres database engine path

enginePath = devEnginePath if not production else prodEnginePath
engine = create_engine( enginePath )

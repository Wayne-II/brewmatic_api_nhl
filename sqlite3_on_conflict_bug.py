from sqlalchemy import Column, Integer, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database
import os
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from datetime import datetime

Base = declarative_base()

class MyTable( Base ):
    __tablename__ = 'my_table'
    __table_args__ = {'extend_existing':True}
    #provided by 3rd-party API
    # adding nullable=False resolves the issue but the error doesn't say 
    # anything about it, however there is a warning that a PK generally
    # isn't a nullable field.
    id = Column( Integer, primary_key=True, autoincrement=False )
    col2 = Column( String )
    col3 = Column( Date )

devDbRelativePath = 'database.db'
devEnginePath = 'sqlite:///' + os.path.abspath( devDbRelativePath )
engine = create_engine( devEnginePath )

if not database_exists( engine.url ):
    create_database( engine.url )
    print( 'Database created')
    Base.metadata.create_all( engine )

today = datetime.today()
data = [
    {'id':1, 'col2':"entry", 'col3':today},
    {'id':2, 'col2':"another entry", 'col3':today},
    {'id':1, 'col2':"updated string", 'col3':today}
]

Session = sessionmaker( engine )
with Session() as session:

    insertQuery = sqlite_insert( 
            MyTable 
        ).values( 
            data
        )
    
    conflictUpdate = insertQuery.on_conflict_do_update(
        index_elements=[ 'id' ],
        set_={
            'col2':insertQuery.excluded.col2,
            'col3':insertQuery.excluded.col3
        }
    )
    session.execute( conflictUpdate )
    session.commit()
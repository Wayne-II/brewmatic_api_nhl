from sqlalchemy import Column, Integer, String, Date, ForeignKey, BLANK_SCHEMA
from uuid import uuid4
from .base import Base


#TODO: automatic serialization like @JsonSerializable() / json_annotation in Dart
class Schedule( Base ):
    __tablename__ = 'schedule'
    __table_args__ = {'extend_existing':True}
    id = Column( Integer, primary_key=True, autoincrement=True )
    home_id = Column( Integer, ForeignKey( 'teams.team_id' ) )
    away_id = Column( Integer, ForeignKey( 'teams.team_id' ) )
    game_date = Column( Date )

#TODO: new schedule API https://api-web.nhle.com/v1/scoreboard/
#this endpoint provides team records
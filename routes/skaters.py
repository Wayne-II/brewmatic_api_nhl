from flask_restx import Namespace, Resource
from sqlalchemy.orm import sessionmaker
import models

def RetrieveData( skaterIds ):
    Session = sessionmaker( models.engine )
    ret = []
    with Session() as session:
        skatersQuery = session.query( 
            models.Skater
        ).filter(
            models.Skater.id.in_( skaterIds ) 
        )
        
        skatersResults = session.scalars( skatersQuery ).all()
        
        for skater in skatersResults:
            ret.append( {
                'playerId': skater.id,
                'skaterFullName': skater.skater_full_name,
                'goals': skater.goals,
                'lastName': skater.last_name,
                'teamAbbrevs':skater.team_abbrevs
            } )
    return ret

api = Namespace( "skaters" )

id_parser = api.parser()
id_parser.add_argument('id', type=int, action='split')

@api.route("/")
@api.doc(params={"id": "Skater IDs - comma delimited list"})
class Skaters( Resource ):
    def get( self ):
        args = id_parser.parse_args()
        ret = []
        skaterIds = args[ 'id' ]
        ret = RetrieveData( skaterIds )
        return ret

##################################
# NHL API INFO FOR THIS ENDPOINT #
##################################
# Filtered output example
##################################


##################################
# RAW NHL API OUTPUT             #

##################################
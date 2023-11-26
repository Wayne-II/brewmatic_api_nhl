from sqlalchemy.orm import sessionmaker
import models
from flask_restx import Namespace, Resource
from common import GetDate

def RetrieveData( session ):
    
    ret = []
    today = GetDate()
    injuryQuery = session.query( 
        models.Injury.skater_id,
        models.Injury.status,
        models.Injury.injury_type,
        models.Skater.skater_full_name
    ).filter_by(
        updated = today
    ).join(
        models.Skater
    )
    #for some reason session.scalars( query ).all() returns only the first
    #column for each row.  This is not my understanding of how it should work.
    #Will have to find something more human readable instead of numeric tuple
    #indicies
    injuryResults = session.execute( injuryQuery ).all()
    SID = 0
    ST = 1
    IT = 2
    SFN = 3
    print( injuryResults )
    for injuryResult in injuryResults:
        #the fact I have to baby this while jsonify doesn't work makes me think jsonify is a bit
        #useless.
        skaterId = injuryResult[ SID ]
        if skaterId > 0:
            ret.append( {
                'skater_id':skaterId,
                'status':injuryResult[ ST ],
                'injury_type':injuryResult[ IT ],
                'name': injuryResult[ SFN ]
            } )

    return ret

api = Namespace( "injury" )

@api.route("/")
class Injury( Resource ):
    def get( self ):
        ret = []
        #fetch data from "local" database
        Session = sessionmaker( models.engine )
        with Session() as session:
            ret = RetrieveData( session )
        return ret
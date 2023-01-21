from flask_restx import Api

from .schedule import api as schedule_api
from .teams import api as teams_api

api = Api(
    title="NHL API"
)

api.add_namespace( schedule_api )
api.add_namespace( teams_api )
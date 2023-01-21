from flask_restx import Api

from .schedule import api as schedule_api

api = Api(
    title="NHL API"
)

api.add_namespace( schedule_api )
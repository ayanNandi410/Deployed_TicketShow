from flask_restful import Resource, fields, marshal_with, reqparse
from models.admin import City
from main.db import db
from main.validation import NotFoundError, BusinessValidationError

# get all cities where venues exist

city_output_fields = {
    "city": fields.String
}

class GetAllCitiesApi(Resource):

    @marshal_with(city_output_fields)
    def get(self):
        cities = db.session.query(City.name)

        if cities:
            return list(cities)
        else:
            raise NotFoundError(error_message='No City found',status_code=404,error_code="CN001")
        
    def post(self):
        pass

def DictToList(d):
    L = []
    for x in d:
        if x not in L:
            L.append(x)
    return L

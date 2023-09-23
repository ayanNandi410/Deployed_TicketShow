from flask_restful import Resource, fields, marshal_with, reqparse
from flask import request
from models.admin import Venue, Allocation, Show, City
from main.db import db
from main.validation import NotFoundError, BusinessValidationError
from sqlalchemy import desc, exc

# Output JSON format
venue_output_fields = {
    "id" : fields.Integer,
    "name" : fields.String,
    "location" : fields.String,
    "city" : fields.String,
    "capacity" : fields.Integer,
    "description" : fields.String,
    "timestamp" : fields.DateTime(dt_format='rfc822')

}

# for POST and PUT request
create_venue_parser = reqparse.RequestParser()
create_venue_parser.add_argument('id',type=int)
create_venue_parser.add_argument('name')
create_venue_parser.add_argument('location')
create_venue_parser.add_argument('city')
create_venue_parser.add_argument('capacity',type=int, help='Capacity cannot be converted')
create_venue_parser.add_argument('description')

class VenueAPI(Resource):

    # get Venue by Name
    @marshal_with(venue_output_fields)
    def get(self,id):
        venue = db.session.query(Venue).filter(Venue.id == id).first()

        if venue:
            return venue
        else:
            raise NotFoundError(error_message='Venue not found',status_code=404,error_code="VN001")

    # Create new Venue
    def post(self):
        vn_args = create_venue_parser.parse_args()
        name = vn_args.get('name',None)
        location = vn_args.get('location',None)
        city = vn_args.get('city',None)
        capacity = vn_args.get('capacity',None)
        desc = vn_args.get('description',None)

        if name is None or name == '':
            raise BusinessValidationError(status_code=400,error_code="VN002",error_message="Name is required")
    
        if location is None or location == '':
            raise BusinessValidationError(status_code=400,error_code="VN003",error_message="Location is required")

        if city is None or city == '':
            raise BusinessValidationError(status_code=400,error_code="VN004",error_message="City is required")

        if capacity == None or type(capacity) is not int:
            raise BusinessValidationError(status_code=400,error_code="VN005",error_message="Invalid capacity of venue")
        
        if int(capacity) < 40:
            raise BusinessValidationError(status_code=400,error_code="VN006",error_message="Capacity must be atleast 40")
        
        if desc is None or desc == '':
            raise BusinessValidationError(status_code=400,error_code="VN007",error_message="Description is required")


        venue = db.session.query(Venue).filter(Venue.name == name, Venue.location == location,Venue.city == city).first()

        if venue:
            raise BusinessValidationError(status_code=400,error_code="VN008",error_message="Venue already exists in the same city")

        from datetime import datetime
        timestamp = datetime.now()

        
        try:
            new_venue = Venue(name=name,location=location,city=city,capacity=int(capacity),description=desc,timestamp=timestamp)
            db.session.add(new_venue)
            new_city = City(city=city)
            db.session.add(new_city)
            db.session.commit()
            return "Success", 201
        except exc.SQLAlchemyError as e:    # Some Database Error occured
            db.session.rollback()
            raise BusinessValidationError(status_code=500,error_code="VN011",error_message=" Add Transaction failed. Try again")


    # Update existing venue
    def put(self):
        vn_args = create_venue_parser.parse_args()
        id = vn_args.get('id',None)
        name = vn_args.get('name',None)
        location = vn_args.get('location',None)
        city = vn_args.get('city',None)
        capacity = vn_args.get('capacity',None)
        desc = vn_args.get('description',None)
         

        if name is None or name == '':
            raise BusinessValidationError(status_code=400,error_code="VN002",error_message="Name is required")
    
        if location is None or location == '':
            raise BusinessValidationError(status_code=400,error_code="VN003",error_message="Location is required")

        if city is None or city == '':
            raise BusinessValidationError(status_code=400,error_code="VN004",error_message="City is required")

        if capacity == None or type(capacity) is not int:
            raise BusinessValidationError(status_code=400,error_code="VN005",error_message="Invalid capacity of venue")
        
        if int(capacity) < 40:
            raise BusinessValidationError(status_code=400,error_code="VN006",error_message="Capacity must be atleast 40")
        
        if desc is None or desc == '':
            raise BusinessValidationError(status_code=400,error_code="VN007",error_message="Description is required")

        venue = db.session.query(Venue).filter(Venue.id == int(id)).first()

        from datetime import datetime
        timestamp = datetime.now()

        try:
            venue.name = name
            venue.location = location
            venue.city = city
            venue.capacity = capacity
            venue.description = desc
            venue.timestamp = timestamp
            
            db.session.add(venue)
            db.session.commit()
            return "Success", 201
        except exc.SQLAlchemyError as e:    # Some Database Error occured
            db.session.rollback()
            raise BusinessValidationError(status_code=500,error_code="VN012",error_message="Update Transaction failed. Try again")

    
    # Delete existing venue
    def delete(self,id):
        venue = db.session.query(Venue).filter(Venue.id == id).first()

        if not venue:
            raise BusinessValidationError(status_code=400,error_code="VN001",error_message="Venue not found with such name")
        
        # check for dependency
        showForVenue = db.session.query(Allocation).filter(Allocation.venue_id == venue.id).first()

        if showForVenue:
            raise BusinessValidationError(status_code=400,error_code="VN008",error_message="Venue has shows allocated to it")

        try:
            db.session.delete(venue)
            db.session.commit()
            return "Success", 200
        except exc.SQLAlchemyError as e:    # Some Database Error occured
            db.session.rollback()
            raise BusinessValidationError(status_code=500,error_code="VN013",error_message="Delete Transaction failed. Try again")


# Get Venue List for a city
class VenueListByCityApi(Resource):

    @marshal_with(venue_output_fields)
    def get(self,city):
        venues = db.session.query(Venue).filter(Venue.city == city).order_by(desc(Venue.timestamp)).all()

        if venues:
            return venues
        else:
            raise NotFoundError(error_message='No Venues found for this city',status_code=404,error_code="VN009")
        
    def post(self):
        raise BusinessValidationError(status_code=405,error_code="VN050",error_message="Method not allowed")

# Get Venue List by Venue Name
class VenueListByNameApi(Resource):

    @marshal_with(venue_output_fields)
    def get(self,name):
        venues = db.session.query(Venue).filter(Venue.name.ilike(f'%{name}%')).order_by(desc(Venue.timestamp)).all()

        if venues:
            return venues
        else:
            raise NotFoundError(error_message='No Venues found for this name',status_code=404,error_code="VN010")
        

# Get Venue List by Show Name
class VenueListByShowApi(Resource):

    @marshal_with(venue_output_fields)
    def get(self,sname):
        city = request.args.get('city',None)
           
        show = db.session.query(Show).filter(Show.name == sname).first()
        venues = show.venues


        if city is not None: 
            venueList = []
            for venue in venues:
                if venue.city == city:
                    venueList.append(venue)
            if venueList != []:
                return venueList
            else:
                raise NotFoundError(error_message='No Venues found for show with city name',status_code=404,error_code="VN012")
        
        if venues:
            return venues
        else:
            raise NotFoundError(error_message='No Venues found for show',status_code=404,error_code="VN011")
        

# Get Venue List by Venue Name
class GetVenueByNameApi(Resource):

    @marshal_with(venue_output_fields)
    def get(self,name):
        venue = db.session.query(Venue).filter(Venue.name == name).first()

        if venue:
            return venue
        else:
            raise NotFoundError(error_message='No Venue found for this name',status_code=404,error_code="VN010")
        
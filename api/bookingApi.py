from flask_restful import Resource, fields, marshal_with, reqparse, inputs
from flask import request, jsonify
from flask_login import current_user
from datetime import datetime as dt
from models.admin import BookTicket, Show, Venue, Allocation
from main.db import db
from main.validation import NotFoundError, BusinessValidationError
from sqlalchemy import desc, exc

# Api for handling user booking

class MyDate(fields.Raw):
    def format(self, value):
        return value.strftime('%Y-%m-%d')
    
class MyTime(fields.Raw):
    def format(self, value):
        return value.strftime('%H-%M-%S')

venue_output_fields = {
    "name" : fields.String
}

show_output_fields = {
    "id" : fields.Integer,
    "name" : fields.String
}

alloc_output_fields = {
    "timeslot" : fields.String,
    "price" : fields.String
}

booking_output_fields = {
    "venue" : fields.Nested(venue_output_fields),
    "show" : fields.Nested(show_output_fields),
    "allocation": fields.Nested(alloc_output_fields),
    "totPrice" : fields.String,
    "allocSeats" : fields.Integer,
    "timestamp" : fields.DateTime(dt_format='rfc822')
}

create_booking_parser = reqparse.RequestParser()
create_booking_parser.add_argument('venue_name')
create_booking_parser.add_argument('show_name')
create_booking_parser.add_argument('date')
create_booking_parser.add_argument('time')
create_booking_parser.add_argument('user_email')
create_booking_parser.add_argument('allocSeats',type=int, help="Seats must be an integer")
create_booking_parser.add_argument('totPrice', type=float, help="Not a valid number or price")

class BookTicketAPI(Resource):

    # get booking details for a given user
    @marshal_with(booking_output_fields)
    def get(self,email):

        bookings = db.session.query(BookTicket).filter(BookTicket.user_email == email).order_by(BookTicket.timestamp).limit(20).all()

        if not bookings:
            raise NotFoundError(error_message='No Booking found',status_code=404,error_code="BK001")
        else:
            return bookings, 200

    # create a new booking
    def post(self):
        bk_args = create_booking_parser.parse_args()
        venueName = bk_args.get('venue_name',None)
        showName = bk_args.get('show_name',None)
        fDate = bk_args.get('date',None)
        fTime = bk_args.get('time',None)
        email = bk_args.get('user_email',None)
        allcSeats = bk_args.get('allocSeats',None)
        ticketPrice = bk_args.get('totPrice',None)

        if venueName is None or venueName == '':
            raise BusinessValidationError(status_code=400,error_code="AL001",error_message="Venue Name is required")
    
        if showName is None or showName == '':
            raise BusinessValidationError(status_code=400,error_code="AL002",error_message="Show Name is required")

        if email is None or email == '':
            raise BusinessValidationError(status_code=400,error_code="AL0017",error_message="Email is required")

        if float(ticketPrice) < 0.0:
            raise BusinessValidationError(status_code=400,error_code="AL003",error_message="Invalid value for Ticket Price")

        try:
            rDate = dt.strptime(fDate, "%Y-%m-%d").date()
        except(ValueError):
            raise BusinessValidationError(status_code=400,error_code="AL004",error_message="Invalid Date or date format")

        try:
            rTime = dt.strptime(fTime, "%H:%M").time()
        except(ValueError):
            raise BusinessValidationError(status_code=400,error_code="AL005",error_message="Invalid Time or time format")

        if allcSeats is None:
            raise BusinessValidationError(status_code=400,error_code="AL006",error_message="Allocated seat count is required")

        if int(allcSeats) <= 0:
            raise BusinessValidationError(status_code=400,error_code="AL007",error_message="Invalid seat count")

        
        show = db.session.query(Show).filter(Show.name == showName).first()

        if not show:
            raise BusinessValidationError(status_code=400,error_code="AL008",error_message="Show does not exist")

        venue = db.session.query(Venue).filter(Venue.name == venueName).first()

        if not venue:
            raise BusinessValidationError(status_code=400,error_code="AL009",error_message="Venue does not exist")

        timestamp = dt.now()
        timeslot = dt.combine(rDate,rTime)
    
        allocation = db.session.query(Allocation).filter(Allocation.show == show, Allocation.venue == venue, Allocation.timeslot == timeslot).first()
        if not allocation:
            raise BusinessValidationError(status_code=400,error_code="AL0019",error_message="Allocation not found")

        if int(allcSeats) > int(allocation.avSeats):
            message = "Only " + str(allocation.avSeats) + " seats available"
            raise BusinessValidationError(status_code=400,error_code="AL0016",error_message=message)

        # allows multiple bookings
        try:
            new_booking = BookTicket(user_email=email,allocation=allocation,showAllocId=allocation.id,allocSeats=allcSeats,totPrice=ticketPrice)
            allocation.avSeats = int(allocation.avSeats) - int(allcSeats)
            db.session.add(allocation) # update available seats
            db.session.add(new_booking)

            db.session.commit()
            return "Success", 201
        except exc.SQLAlchemyError as e:    # Some Database Error occured
            db.session.rollback()
            raise BusinessValidationError(status_code=500,error_code="AL020",error_message="Add Transaction failed. Try again")


    def put(self,name):
        pass
    
    def delete(self,name):
        pass
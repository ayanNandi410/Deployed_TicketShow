from flask_restful import Resource, fields, marshal_with, reqparse, inputs
import json
from models.admin import Show, Venue, Allocation
from datetime import date, timedelta
from flask import request
from sqlalchemy import desc, exc
from main.db import db
from main.validation import NotFoundError, BusinessValidationError
from datetime import datetime as dt

# Api for working with show-venue allocations alongwith timing details

allocation_output_fields = {
    "id" : fields.Integer,
    "venue_id" : fields.Integer,
    "date" : fields.String,
    "time" : fields.String,
    "avSeats" : fields.Integer,
    "totSeats" : fields.Integer,
    "price" : fields.Float,
    "show" : fields.String,
    "venue" : fields.String
}

# details visible to user
userallocation_output_fields = {
    "id" : fields.Integer,
    "venue_id" : fields.Integer,
    "date" : fields.String,
    "time" : fields.String,
    "avSeats" : fields.Integer,
    "totSeats" : fields.Integer,
    "price" : fields.Float
}

# Parser details for post and put request
create_allocation_parser = reqparse.RequestParser()
create_allocation_parser.add_argument('venue_id',type=int)
create_allocation_parser.add_argument('show_name')
create_allocation_parser.add_argument('releaseDate')
create_allocation_parser.add_argument('releaseTime')
create_allocation_parser.add_argument('allocSeats',type=int, help="Seats must be an integer")
create_allocation_parser.add_argument('price', type=float, help="Not a valid number or price")



class AllocationAPI(Resource):

    # get an allocation by its id
    @marshal_with(allocation_output_fields)
    def get(self,aid):

        timeslot = db.session.query(Allocation).filter(Allocation.id == aid).first()

        if not timeslot:
            raise NotFoundError(error_message='No timeslot found',status_code=404,error_code="AL011")
        else:
            slot = { "id":timeslot.id, "venue_id" : timeslot.venue_id, "date" : timeslot.timeslot.strftime("%Y-%m-%d"), "time" : timeslot.timeslot.strftime("%H:%M:%S"), 
                            "avSeats" : timeslot.avSeats, "totSeats" : timeslot.totSeats, "price" : timeslot.price,
                            "show" : timeslot.show.name, "venue" : timeslot.venue.name }
            return slot, 200

    # create a new allocation
    def post(self):
        vn_args = create_allocation_parser.parse_args()
        venueId = vn_args.get('venue_id',None)
        showName = vn_args.get('show_name',None)
        rlDate = vn_args.get('releaseDate',None)
        rlTime = vn_args.get('releaseTime',None)
        allcSeats = vn_args.get('allocSeats',None)
        ticketPrice = vn_args.get('price',None)

        if venueId is None or venueId == '':
            raise BusinessValidationError(status_code=400,error_code="AL001",error_message="Venue Id is required")
    
        if showName is None or showName == '':
            raise BusinessValidationError(status_code=400,error_code="AL002",error_message="Show Name is required")

        if float(ticketPrice) < 0.0:
            raise BusinessValidationError(status_code=400,error_code="AL003",error_message="Invalid value for Ticket Price")

        try:
            rDate = dt.strptime(rlDate, "%Y-%m-%d").date()
        except(ValueError):
            raise BusinessValidationError(status_code=400,error_code="AL004",error_message="Invalid Date or date format")

        try:
            rTime = dt.strptime(rlTime, "%H:%M").time()
        except(ValueError):
            raise BusinessValidationError(status_code=400,error_code="AL005",error_message="Invalid Time or time format")

        if allcSeats is None:
            raise BusinessValidationError(status_code=400,error_code="AL006",error_message="Allocated seat count is required")

        if int(allcSeats) <= 0:
            raise BusinessValidationError(status_code=400,error_code="AL007",error_message="Invalid seat count")

        
        show = db.session.query(Show).filter(Show.name == showName).first()

        if not show:
            raise BusinessValidationError(status_code=400,error_code="AL008",error_message="Show does not exist")

        venue = db.session.query(Venue).filter(Venue.id == venueId).first()

        if not venue:
            raise BusinessValidationError(status_code=400,error_code="AL009",error_message="Venue does not exist")

        if int(allcSeats) > int(venue.capacity):
            raise BusinessValidationError(status_code=400,error_code="AL0016",error_message="Seats exceeds capacity of Venue")


        from datetime import datetime
        timestamp = datetime.now()

        timeslot = datetime.combine(rDate,rTime)

        prevAlloc = db.session.query(Allocation).filter(Allocation.venue == venue, Allocation.show == show, Allocation.timeslot == timeslot).first()

        if prevAlloc:
            raise BusinessValidationError(status_code=400,error_code="AL0015",error_message="Timeslot already allocated")


        show_id = db.session.query(Show.id).filter(Show.name == showName).first()

        new_allocation = Allocation(show_id=show_id.id,venue_id=venueId,timeslot=timeslot,totSeats=allcSeats,avSeats=allcSeats,price=ticketPrice)
        
        db.session.add(new_allocation)

        db.session.commit()
        return "Success", 201

    # update existing allocation
    def put(self,aid):
        vn_args = create_allocation_parser.parse_args()
        venueId = vn_args.get('venue_id',None)
        showName = vn_args.get('show_name',None)
        rlDate = vn_args.get('releaseDate',None)
        rlTime = vn_args.get('releaseTime',None)
        allcSeats = vn_args.get('allocSeats',None)
        ticketPrice = vn_args.get('price',None)

        if venueId is None or venueId == '':
            raise BusinessValidationError(status_code=400,error_code="AL001",error_message="Venue Id is required")
    
        if showName is None or showName == '':
            raise BusinessValidationError(status_code=400,error_code="AL002",error_message="Show Name is required")

        if float(ticketPrice) < 0.0:
            raise BusinessValidationError(status_code=400,error_code="AL003",error_message="Invalid value for Ticket Price")

        try:
            rDate = dt.strptime(rlDate, "%Y-%m-%d").date()
        except(ValueError):
            raise BusinessValidationError(status_code=400,error_code="AL004",error_message="Invalid Date or date format")

        try:
            rTime = dt.strptime(rlTime, "%H:%M").time()
        except(ValueError):
            raise BusinessValidationError(status_code=400,error_code="AL005",error_message="Invalid Time or time format")

        if allcSeats is None:
            raise BusinessValidationError(status_code=400,error_code="AL006",error_message="Allocated seat count is required")

        if int(allcSeats) <= 0:
            raise BusinessValidationError(status_code=400,error_code="AL007",error_message="Invalid seat count")

        
        show = db.session.query(Show).filter(Show.name == showName).first()

        if not show:
            raise BusinessValidationError(status_code=400,error_code="AL008",error_message="Show does not exist")

        venue = db.session.query(Venue).filter(Venue.id == int(venueId)).first()

        if not venue:
            raise BusinessValidationError(status_code=400,error_code="AL009",error_message="Venue does not exist")

        if int(allcSeats) > int(venue.capacity):
            raise BusinessValidationError(status_code=400,error_code="AL0016",error_message="Seats exceeds capacity of Venue")


        from datetime import datetime
        timestamp = datetime.now()

        timeslot = datetime.combine(rDate,rTime)

        showItem = db.session.query(Show.id).filter(Show.name == showName).first()
        show_id = showItem.id

        curAllocation = db.session.query(Allocation).filter(Allocation.id == aid).first()
        curAllocation.venue_id = venueId
        curAllocation.show_id = show_id
        curAllocation.timeslot = timeslot
        curAllocation.totSeats = allcSeats
        curAllocation.avSeats = allcSeats
        curAllocation.price = ticketPrice

        db.session.add(curAllocation)

        db.session.commit()
        return "Success", 201
    
    # delete existing allocation
    def delete(self,aid):

        try:
            delAlloc = db.session.query(Allocation).filter(Allocation.id == aid).first()
            db.session.delete(delAlloc)
            db.session.commit()

            return 'Success', 200
        except exc.SQLAlchemyError as e:    # Some Database Error occured
            db.session.rollback()
            raise BusinessValidationError(status_code=500,error_code="AL017",error_message="Delete Transaction failed. Try again")


# get allocations for a range of dates
class AllocationBetweenDatesAPI(Resource):

    @marshal_with(userallocation_output_fields)
    def get(self):
        sDate = request.args.get('startDate')
        eDate = request.args.get('endDate')

        showName = request.args.get('show')
        vId = request.args.get('vid')

        show = db.session.query(Show).filter(Show.name == showName).first()
        venue =db.session.query(Venue).filter(Venue.id == vId).first()

        timeslotList = db.session.query(Allocation.id,Allocation.venue_id,Allocation.timeslot,Allocation.avSeats,Allocation.totSeats,Allocation.price).filter(Allocation.venue == venue,Allocation.show == show,Allocation.timeslot.between(sDate,eDate)).order_by(Allocation.timeslot).limit(50).all()

        if not timeslotList:
            raise NotFoundError(error_message='No timeslots found',status_code=404,error_code="AL011")
        else:
            slotlist = []
            for row in timeslotList:
                slotDict = { "id": row.id, "venue_id": row.venue_id, "date" : row.timeslot.strftime("%Y-%m-%d"), "time" : row.timeslot.strftime("%H:%M:%S"), 
                            "avSeats" : row.avSeats, "totSeats" : row.totSeats, "price" : row.price }
                slotlist.append(slotDict)
            print(slotDict)
            return slotlist, 200
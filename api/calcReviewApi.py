from flask_restful import Resource, fields, marshal_with, reqparse, inputs
from flask import request, jsonify
from flask_login import current_user
from datetime import datetime as dt
from models.admin import  Show, MovieReview, CalcReview
from main.db import db
from main.validation import NotFoundError, BusinessValidationError
from sqlalchemy import desc, exc

# Api to update show rating 

calcreview_output_fields = {
    "show_id": fields.Integer,
    "avRating" : fields.String,
    "timestamp" : fields.DateTime(dt_format='rfc822')
}

create_calcreview_parser = reqparse.RequestParser()
create_calcreview_parser.add_argument('show_id')
create_calcreview_parser.add_argument('rating',type=int, help="Rating must be an integer")

class CalcReviewAPI(Resource):
    # get rating for a particular show
    @marshal_with(calcreview_output_fields)
    def get(self,sid):

        rating = db.session.query(CalcReview).filter(CalcReview.show_id == sid).first()

        if not rating:
           raise NotFoundError(error_message='Rating entry not found',status_code=404,error_code="CR001") 
        else:
            return rating, 200

    # update rating for a particular show
    def post(self):
        bk_args = create_calcreview_parser.parse_args()
        showId = bk_args.get('show_id',None)
        rating = bk_args.get('rating',None)
    
        if showId is None or showId == '':
            raise BusinessValidationError(status_code=400,error_code="CR004",error_message="Show ID is required")

        if rating is None:
            raise BusinessValidationError(status_code=400,error_code="CR005",error_message="Rating is required")

        if int(rating)<0 or int(rating)>10:
            raise BusinessValidationError(status_code=400,error_code="CR006",error_message="Invalid value for rating")

        try:
            rowR = db.session.query(CalcReview).filter(CalcReview.show_id == showId).first()

            timestamp = dt.now()

            if not rowR:
                rowR = CalcReview(show_id=showId,oneStarRatings=0,twoStarRatings=0,threeStarRatings=0,fourStarRatings=0,fiveStarRatings=0,totalRatings=0,avRating="0")
            
            rt = round(rating/2)

            if rt <= 1:
                rowR.oneStarRatings += 1
                add = 1
            elif rt == 2:
                rowR.twoStarRatings += 1
                add = 2
            elif rt == 3:
                rowR.threeStarRatings += 1
                add = 3
            elif rt == 4:
                rowR.fourStarRatings += 1
                add = 4
            else:
                rowR.fiveStarRatings += 1
                add = 5

            newAvgRating = round(((float(rowR.avRating)*rowR.totalRatings) + add)/(rowR.totalRatings+1),2)
            rowR.totalRatings += 1

            rowR.avRating = str(newAvgRating)
            
            db.session.add(rowR)

            # update show rating
            show = db.session.query(Show).filter(Show.id == showId).first()
            show.rating = round(int(newAvgRating)*2)

            db.session.add(show)

            db.session.commit()
            return "Success", 200
        except exc.SQLAlchemyError as e:    # Some Database Error occured
            db.session.rollback()
            raise BusinessValidationError(status_code=500,error_code="RW020",error_message="Update Rating Transaction failed. Try again")

    # other requests
    def put(self,name):
        raise BusinessValidationError(status_code=405,error_code="CR010",error_message="Method not allowed")
    
    def delete(self,name):
        raise BusinessValidationError(status_code=405,error_code="CR011",error_message="Method not allowed")
# Api initialization
from flask_restful import Resource, Api
from api.venueApi import VenueAPI, VenueListByCityApi, VenueListByNameApi, VenueListByShowApi, GetVenueByNameApi
from api.showApi import ShowAPI, ListShowByNameApi, ListShowByVenueApi, PopularShowsApi, FilterShowsApi
from api.cityApi import  GetAllCitiesApi
from api.allocationApi import AllocationAPI, AllocationBetweenDatesAPI
from api.bookingApi import BookTicketAPI
from api.reviewApi import MovieReviewAPI
from api.calcReviewApi import CalcReviewAPI
    
def getConfiguredApi(app):
    apiV = Api(app)

    apiV.add_resource(VenueAPI,"/api/venue","/api/venue/<string:id>",endpoint="/venue")
    apiV.add_resource(GetVenueByNameApi,"/api/getVenue/<string:name>",endpoint="/getVenue")
    apiV.add_resource(VenueListByCityApi,"/api/venues/byCity/<string:city>",endpoint="/venues/byCity/<city>")
    apiV.add_resource(VenueListByNameApi,"/api/venues/byName/<string:name>",endpoint="/venues/byName/<name>")
    apiV.add_resource(VenueListByShowApi,"/api/venues/byShow/<string:sname>")
    
    apiV.add_resource(GetAllCitiesApi,"/api/city/all",endpoint="/city")

    apiV.add_resource(ShowAPI,"/api/show","/api/show/<string:name>",endpoint="/show")
    apiV.add_resource(ListShowByVenueApi,"/api/shows/byVenue/<string:vid>",endpoint="/shows/byVenue/<vid>")
    apiV.add_resource(ListShowByNameApi,"/api/shows/byName/<string:name>",endpoint="/shows/byName/<name>")
    apiV.add_resource(PopularShowsApi,"/api/popShows/<string:email>",endpoint="/popShows")
    apiV.add_resource(FilterShowsApi,"/api/filterShows",endpoint="/filterShows")

    apiV.add_resource(AllocationAPI,"/api/allocation","/api/allocation/<string:aid>",endpoint="/allocation")
    apiV.add_resource(AllocationBetweenDatesAPI,"/api/allocations/dateRange",endpoint="/dateRange")

    apiV.add_resource(BookTicketAPI,"/api/booking","/api/booking/<string:email>",endpoint="/booking")
    
    apiV.add_resource(MovieReviewAPI,"/api/review","/api/review/<string:sname>",endpoint="/review")

    apiV.add_resource(CalcReviewAPI,"/api/updateReview","/api/updateReview/<string:sid>",endpoint="/updateReview")

    return apiV
from flask import Blueprint, request, flash, redirect, url_for
import requests
from datetime import datetime, timedelta, date
from flask import render_template
from flask_login import login_required, current_user
from models.admin import Venue, Show
from main.constants import BASE_URL

user = Blueprint('user', __name__,url_prefix='/user')

@user.route('/')
@login_required
def index():
    pass

@user.route('/userHome')
@login_required
def userHome():
    
    cityCall = requests.get(BASE_URL+'/api/city/all')
    cities = cityCall.json()

    return render_template("userHome.html",cities=cities, user=current_user)

@user.route('/userProfile')
@login_required
def userProfile():
    return render_template("userProfile.html", user=current_user)

# ignore
@user.route('/venues')
@login_required
def userVenues():
    page = request.args.get('page', 1, type=int)
    pagedVenues = Venue.query.order_by(Venue.name).paginate(page=page, per_page=20)

    if pagedVenues.pages == 0:
        return render_template('userVenues.html',venuesPage=pagedVenues,noVenue=True, user=current_user)
    else:
        return render_template('userVenues.html',venues=pagedVenues, user=current_user)

@user.route('/venuesByCity/<city>')
@login_required
def userVenuesByCity(city):
    venueCall = requests.get(BASE_URL+'/api/venues/byCity/'+city)
    venues = venueCall.json()

    if venueCall.status_code != 200:
        return render_template('userVenues.html',venues=venues,city=city,noVenue=True, user=current_user)
    else:
        return render_template('userVenues.html',venues=venues,city=city, user=current_user)

@user.route('/searchVenueByName',methods=['POST'])
@login_required
def userVenuesByName():
    if request.method == 'POST':
        name = request.form.get('searchVenueName')
        venueCall = requests.get(BASE_URL+'/api/venues/byName/'+name)
        venues = venueCall.json()
        return render_template('userVenues.html',venues=venues,name=name, user=current_user)
    else:
        return render_template('NotFound.html', user=current_user)

@user.route('/venueHome', methods=['GET','POST'])
@login_required
def userVenueHome():

    venue_id = request.form.get('vid')
    venueCall = requests.get(BASE_URL+'/api/venue/'+str(venue_id))
    venue = venueCall.json()

    showsByVenueCall = requests.get(BASE_URL+'/api/shows/byVenue/'+str(venue_id))
    shows = showsByVenueCall.json()

    if showsByVenueCall.status_code == 404:
        return render_template('userVenueHome.html',venue=venue,showListEmpty=True, user=current_user)
    else:
        return render_template('userVenueHome.html',venue=venue,shows=shows, user=current_user)
    
# --------------------- Shows -----------------------------

@user.route('/popularShows/', methods=['GET','POST'])
@login_required
def popShows():
    if request.method == 'GET':
        pshowsCall = requests.get(BASE_URL+'/api/popShows/'+current_user.email)
        pshows= pshowsCall.json()

        cityCall = requests.get(BASE_URL+'/api/city/all')
        cities = cityCall.json()

        if pshowsCall.status_code == 404:
            return render_template('userShows.html',shows=pshows,heading="Latest Added Shows",showListEmpty=True, user=current_user)
        else:
            return render_template('userShows.html',shows=pshows,heading="Latest Added Shows", cities=cities, user=current_user)
  

@user.route('/showsByName', methods=['GET','POST'])
@login_required
def showsByName():
    if request.method == 'POST':
        name = request.form.get('sname')

        if name == '':
            return redirect(url_for('user.popShows'))

        showsByNameCall = requests.get(BASE_URL+'/api/shows/byName/'+name)
        shows = showsByNameCall.json()

        cityCall = requests.get(BASE_URL+'/api/city/all')
        cities = cityCall.json()

        if showsByNameCall.status_code == 404:
            return render_template('userShows.html',heading="Shows with name : "+name,showListEmpty=True, user=current_user)
        else:
            return render_template('userShows.html',shows=shows,heading="Shows with name : "+name, cities=cities, user=current_user)

# ------------------- Timeslot ---------------------------

@user.route('/bookTimeslot/')
@login_required
def bookTimeslot():
    show = request.args.get('show')
    venueId = request.args.get('vid')

    from datetime import date
    sDate = date.today()
    eDate = date.today()+ timedelta(days=7)

    query = {'show': show, 'vid' : venueId, 'startDate' : sDate, 'endDate' : eDate}
    timeslotsCall = requests.get(BASE_URL+'/api/allocations/dateRange',params=query)
    timeslots = timeslotsCall.json()
    print(timeslots)
    slots = {}

    vnCall = requests.get(BASE_URL+'/api/venue/'+venueId)
    vn = vnCall.json()
    venue = vn['name']

    if  timeslotsCall.status_code == 404 and timeslots['error_code'] == "AL011":
        return render_template("bookTimeslot.html",show=show,venue=venue,emptySlotList=True)
    else:
        for item in timeslots:
            if item['date'] in slots.keys() :
                if item['avSeats'] == 0:
                    slots[item['date']].append((item['time'],item['avSeats'],item['price']))
                else:
                    slots[item['date']].append((item['time'],item['avSeats'],item['price']))
            else:
                slots[item['date']] = []
                if item['avSeats'] == 0:
                    slots[item['date']].append((item['time'],item['avSeats'],item['price']))
                else:
                    slots[item['date']].append((item['time'],item['avSeats'],item['price']))

        dateList, dayList = [],[]

        curdate = date.today()
        for i in range(7): 
            dateList.append(curdate)
            dayList.append(curdate.strftime("%A"))
            curdate += timedelta(days=1)

        for date in dateList:
            if str(date) not in slots.keys():
                slots[str(date)] = []

        return render_template("bookTimeslot.html", dayList=dayList,show=show,venue=venue,slotsDict=slots, user=current_user)

# ---------------- Ticket Booking ----------------------

@user.route('/bookTicket/', methods=['GET','POST'])
@login_required
def bookTicket():
    show = request.args.get('show')
    venue = request.args.get('venue') 
    date = request.args.get('date')
    time = request.args.get('time')
    price = request.args.get('price')

    details = { "show": show, "venue": venue, "date": date, "time": time,"price": price, "email": current_user.email}

    if request.method == 'GET':
        
        return render_template('bookTicket.html',details=details,user=current_user)
    else:
        show = request.form.get('showName')
        venue = request.form.get('venueName') 
        date = request.form.get('date')
        time = request.form.get('time') 
        seats = request.form.get('allocSeats')
        price = request.form.get('totPrice')

        ticketDetails = { "user_email" : current_user.email,"show_name" : show, "venue_name" : venue, "date" : date, "time" : time, "allocSeats" : int(seats), "totPrice" : price  }

        bookingCall = requests.post(BASE_URL+'/api/booking',json=ticketDetails)
        response = bookingCall.json()

        if bookingCall.status_code != 201:
            if 'error_message' in response.keys():
                flash(response['error_message'],'error')
            else:
                flash('Some error occured. Try Again...','error')
        else:
            flash('Succesfully booked tickets','success') 

        return redirect( url_for('user.userHome') )

@user.route('/bookings/')
@login_required
def showBookings():
    bookingsCall = requests.get(BASE_URL+'/api/booking/'+current_user.email)
    bookings = bookingsCall.json()

    if bookingsCall.status_code != 200:
        return render_template('userBookings.html',bookingsEmpty=True,user=current_user)
    else:
        return render_template('userBookings.html',bookings=bookings,user=current_user)

# --------------- Movie Review ---------------------------

@user.route('/review/add', methods=["POST"])
@login_required
def addReview():
    show = request.form.get('showName')
    showId =  request.form.get('showId')
    email = current_user.email
    gRating = request.form.get('userRating')
    comment = request.form.get('userComment')

    reviewJson = { 'show_name' : show, 'user_email' : email, 'rating' : gRating, 'comment' : comment}

    reviewsPostCall = requests.post(BASE_URL+'/api/review',json=reviewJson)
    response = reviewsPostCall.json()

    updateReviewJson = { 'show_id' : showId, 'rating' : gRating }
    print(updateReviewJson)

    statusCode = 404
    i = 0
    while statusCode != 200 and i<10:
        i+=1
        reviewUpdatePostCall = requests.post(BASE_URL+'/api/updateReview',json=updateReviewJson)
        statusCode = reviewUpdatePostCall.status_code

    if i==10:
        flash('Could not process review','error')
    else:
        if reviewsPostCall.status_code != 200:
            if 'error_message' in response.keys():
                flash(response['error_message'],'error')
            else:
                flash('Some error occured. Try Again...','error')
        else:
            flash('Succesfully added your review','success') 

    return redirect(url_for('user.showBookings'))

@user.route('/reviews/<sname>')
@login_required
def getReviews(sname):

    reviewsCall = requests.get(BASE_URL+'/api/review/'+sname)
    reviews = reviewsCall.json()


@user.route('/filterShows', methods=["POST"])
@login_required
def filterShows():
    tags = request.form.getlist('tags')
    langs = request.form.getlist('languages')
    rating = request.form.get('userRating')
    runningShows = request.form.get('runShows')

    filterData = { 'tags' : tags, 'languages' : langs, 'rating' : rating, 'runningShows' : runningShows}

    filterCall = requests.post(BASE_URL+'/api/filterShows',json=filterData)
    shows = filterCall.json()

    cityCall = requests.get(BASE_URL+'/api/city/all')
    cities = cityCall.json()

    if filterCall.status_code == 404:
        return render_template('userShows.html',heading="Shows with filters : ",showListEmpty=True, user=current_user)
    else:
        return render_template('userShows.html',shows=shows,heading="Shows with filters : ",cities=cities, user=current_user)



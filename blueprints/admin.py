from flask import Blueprint, render_template,request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from sqlalchemy import desc
from datetime import datetime, date
from models.admin import Venue, Show
from models.users import User
#from ..models.Image import Image
from functools import wraps
from werkzeug.utils import secure_filename
from main.db import db
import requests
from main.constants import BASE_URL, PER_PAGE_SIZE


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

admin = Blueprint('admin', __name__,url_prefix='/admin')


def admin_login_required(view):
    @login_required
    @wraps(view)
    def wrap(*args, **kwargs):
        if current_user is not None:
            if current_user.is_admin():
                return view(*args,**kwargs)
            else:
                flash('Not a Admin User...')
                redirect(url_for('authn.userLogin'))
        else:
            flash('You need to login first.')
            return redirect(url_for('authn.adminLogin'))
    return wrap

# Admin Home
@admin.route('/')
@admin_login_required
def index():
    return render_template('adminHome.html',user=current_user)


# Admin Profile
@admin.route('/profile')
@admin_login_required
def profile():
    return render_template('profile.html',name=current_user.name)


# List All Venues
@admin.route('/showVenues')
@admin_login_required
def showVenues():
    page = request.args.get('page', 1, type=int)
    paginationVenue = db.session.query(Venue).order_by(desc(Venue.timestamp),Venue.name).paginate(page=page, per_page=PER_PAGE_SIZE)
    
    return render_template('venuesHome.html',pagination=paginationVenue, user=current_user)

@admin.route('/showVenues/<city>')
@admin_login_required
def showVenuesByCity(city):
    venues = requests.get(BASE_URL+'/api/venues/'+city)
    return render_template('venuesHome.html',venues = venues,city=city, user=current_user)

@admin.route('/deleteVenue/<id>', methods=['GET'])
@admin_login_required
def deleteVenue(id):
    delVenueCall = requests.delete(BASE_URL+'/api/venue/'+id)
    response = delVenueCall.json()

    if delVenueCall.status_code != 200:
        if 'error_message' in response.keys():
            flash(response['error_message'],'error')
        else:
             flash('Some error occured. Try Aagain...','error')
    else:
        flash('Succesfully Deleted','success')
    return redirect(url_for('admin.showVenues'))

@admin.route('/venue/add',methods=['GET','POST'])
@admin_login_required
def addVenue():
    if request.method == 'POST':
        name = request.form.get('venueName','')
        location = request.form.get('venueLocation','')
        city = request.form.get('venueCity','')
        description = request.form.get('venueDescription','')
        capacity = request.form.get('venueCapacity','')
        venue = { 'name' : name, 'location' : location, 'city' : city, 'description' : description, 
        'capacity' : capacity }

        resV = requests.post(BASE_URL+'/api/venue', json=venue)
        response = resV.json()

        if resV.status_code != 201:
            if 'error_message' in response.keys():
                flash(response['error_message'],'error')
            else:
                flash('Some error occured. Try Again...','error')
        else:
            flash('Succesfully Added','success') 

        return render_template('addVenue.html', user=current_user)
    else:
        return render_template('addVenue.html', user=current_user)
    
@admin.route('/venue/update',methods=['GET','POST'])
@admin_login_required
def updateVenue():
    if request.method == 'POST':
        id = request.form.get('venueId','')
        name = request.form.get('venueName','')
        location = request.form.get('venueLocation','')
        city = request.form.get('venueCity','')
        description = request.form.get('venueDescription','')
        capacity = request.form.get('venueCapacity','')
        venue = { 'id' : id,'name' : name, 'location' : location, 'city' : city, 'description' : description, 
        'capacity' : capacity }

        resV = requests.put(BASE_URL+'/api/venue', json=venue)
        response = resV.json()

        if resV.status_code != 201:
            if 'error_message' in response.keys():
                flash(response['error_message'],'error')
            else:
                flash('Some error occured. Try Again...','error')
        else:
            flash('Succesfully Updated','success') 

        return render_template('updateVenue.html',venue=venue, user=current_user)
    else:
        id = request.args.get('id')

        resV = requests.get(BASE_URL+'/api/venue/'+id)
        response = resV.json()

        return render_template('updateVenue.html',venue=response, user=current_user)

# -------------------- Shows ---------------------

@admin.route('/showShows')
@admin_login_required
def showShows():
    page = request.args.get('page', 1, type=int)
    paginationShow = db.session.query(Show).order_by(desc(Show.timestamp)).paginate(page=page, per_page=PER_PAGE_SIZE)
    return render_template('showsHome.html',pagination=paginationShow, user=current_user)

@admin.route('/show/add',methods=['GET','POST'])
@admin_login_required
def addShow():
    if request.method == 'POST':
        name = request.form.get('showName')
        tags = request.form.getlist('tags')
        languages = request.form.getlist('languages')
        rating = request.form.get('showRating')
        duration = request.form.get('showDuration')

        show = { 'name' : name, 'tags' : list(tags), 'languages' : list(languages),
                 'rating' : int(rating), 'duration' : duration }

        resS = requests.post(BASE_URL+'/api/show', json=show)
        response=resS.json()

        if resS.status_code != 201:
            if 'error_message' in response.keys():
                flash(response['error_message'],'error')
            else:
                flash('Some error occured. Try Again...','error')
        else:
            flash('Succesfully added','success') 

        return render_template('addShow.html',response=response,user=current_user), 201
    else:

        return render_template('addShow.html',user=current_user)
    
@admin.route('/deleteShow/<name>',methods=['GET'])
@admin_login_required
def deleteShow(name):
    delShowCall = requests.delete(BASE_URL+'/api/show/'+name)
    response = delShowCall.json()

    if delShowCall.status_code != 200:
        if 'error_message' in response.keys():
            flash(response['error_message'],'error')
        else:
             flash('Some error occured. Try Aagain...','error')
    else:
        flash('Succesfully Deleted','success')
    return redirect(url_for('admin.showShows'))

@admin.route('/show/update',methods=['GET','POST'])
@admin_login_required
def updateShow():
    if request.method == 'POST':
        name = request.form.get('showName')
        tags = request.form.getlist('tags')
        languages = request.form.getlist('languages')
        rating = request.form.get('showRating')
        duration = request.form.get('showDuration')

        show = { 'name' : name, 'tags' : list(tags), 'languages' : list(languages),
                 'rating' : int(rating), 'duration' : duration }
        print(show)

        resS = requests.put(BASE_URL+'/api/show', json=show)
        response = resS.json()
        
        if resS.status_code != 201:
            if 'error_message' in response.keys():
                flash(response['error_message'],'error')
            else:
                flash('Some error occured. Try Again...','error')
        else:
            flash('Succesfully Updated','success') 
        
        return render_template('updateShow.html',sname=name,response=resS.json(),user=current_user), 201
    else:
        name = request.args.get('name')
        return render_template('updateShow.html',sname=name, user=current_user)


# not used
@admin.route('/showFor/<vname>/add',methods=['GET','POST'])
@admin_login_required
def addShowForVenue(vname):
    if request.method == 'POST':
        name = request.form.get('showName')
        venue = request.form.get('venueName')
        tags = request.form.getlist('tags')
        languages = request.form.getlist('languages')
        rating = request.form.get('showRating')
        rlDate = request.form.get('showReleaseDate')
        rlTime = request.form.get('showReleaseTime')
        duration = request.form.get('showDuration')
        ticketPrice = request.form.get('showTicketPrice',type=float)

        showWithAllocation = { 'name' : name, 'vname' : venue, 'tags' : tags, 'languages' : languages,
                 'rating' : int(rating), 'releaseDate' : rlDate, 'releaseTime' : rlTime, 'duration' : duration,
                  'price' : ticketPrice }
        print(showWithAllocation)

        resS = requests.post(BASE_URL+'/api/show', json=showWithAllocation)
        
        return render_template('addShow.html',venue_name=vname,response=resS.json(),user=current_user), 201
    else:

        return render_template('addShow.html',venue_name=vname,user=current_user)
    

#  ------------------- Allocation -------------------

@admin.route('/allocation/add', methods=['GET','POST'])
@admin_login_required
def allocateShow():
    vname = request.args.get('venue')
    vid = request.args.get('vid')
    if request.method == "GET":
        dateToday = date.today()
        return render_template('allocateShow.html',vname=vname,vid=str(vid),curDate=dateToday, user=current_user)
    else:
        vid = request.form.get('venue_id')
        sname = request.form.get('showName')
        rlDate = request.form.get('showReleaseDate')
        rlTime = request.form.get('showReleaseTime')
        allcSeats = request.form.get('allocSeats')
        ticketPrice = request.form.get('showTicketPrice',type=float)

        showWithAllocation = { 'show_name' : sname, 'venue_id' : vid, 'releaseDate' : rlDate, 
                              'releaseTime' : rlTime, 'allocSeats' : int(allcSeats), 'price' : float(ticketPrice) }
        print(showWithAllocation)

        resA = requests.post(BASE_URL+'/api/allocation', json=showWithAllocation)
        response=resA.json()

        if resA.status_code != 201:
            if 'error_message' in response.keys():
                flash(response['error_message'],'error')
            else:
                flash('Some error occured. Try Again...','error')
        else:
            flash('Succesfully Added','success') 
        
        return render_template('allocateShow.html',vname=vname,response=response,user=current_user), 201


@admin.route('/getAllocations', methods=['GET','POST'])
@admin_login_required
def getAllocations():
    show = request.args.get('show')
    venue = request.args.get('venue')
    vid = request.args.get('vid')
    if request.method == 'GET':
        return render_template('adminTimings.html',show=show,venue=venue,vid=vid,user=current_user), 200
    else:
        sDate = request.form.get('startDate')
        eDate = request.form.get('endDate')
        resA = requests.get(BASE_URL+'/api/allocations/dateRange?show='+show+'&vid='+str(vid)+'&startDate='+sDate+'&endDate='+eDate)
        response=resA.json()

    if resA.status_code != 200:
        return render_template('adminTimings.html',show=show,venue=venue,vid=vid,emptyAlloc=True,user=current_user), 200
    else:
        return render_template('adminTimings.html',show=show,venue=venue,vid=vid,sDate=sDate,eDate=eDate,allocations=response,user=current_user), 200


@admin.route('/allocation/delete', methods=['GET'])
@admin_login_required
def deleteAllocation():
    
    id = request.args.get('aid')
    vid = request.args.get('vid')

    resA = requests.delete(BASE_URL+'/api/allocation/'+str(id))
    response=resA.json()

    if resA.status_code != 200:
        if 'error_message' in response.keys():
            flash(response['error_message'],'error')
        else:
             flash('Some error occured. Try Aagain...','error')
    else:
        flash('Succesfully Deleted','success')

    show = request.args.get('show')
    venue = request.args.get('venue')
    sDate = request.args.get('sDate')
    eDate = request.args.get('eDate')

    return render_template('adminTimings.html',show=show,vid=vid,venue=venue,sDate=sDate,eDate=eDate,emptyAlloc=True,user=current_user), 200


@admin.route('/allocation/update', methods=['GET','POST'])
@admin_login_required
def updateAllocation():
    id = request.args.get('aid')
    vid = request.args.get('vid')
    print(vid)
    if request.method == 'GET':
        resA = requests.get(BASE_URL+'/api/allocation/'+str(id))
        response=resA.json()

        return render_template('updateAllocation.html',vid=response['venue_id'],alloc=response,user=current_user)

    else:
        sname = request.form.get('showName')
        venueName = request.form.get('venueName')
        vid = request.form.get('venue_id')
        rlDate = request.form.get('showReleaseDate')
        rlTime = request.form.get('showReleaseTime')
        allcSeats = request.form.get('allocSeats')
        ticketPrice = request.form.get('showTicketPrice',type=float)

        showWithAllocation = { 'show_name' : sname, 'venue_id' : int(vid), 'releaseDate' : rlDate, 
                              'releaseTime' : rlTime, 'allocSeats' : int(allcSeats), 'price' : float(ticketPrice) }
        print(showWithAllocation)

        resA = requests.put(BASE_URL+'/api/allocation/'+str(id), json=showWithAllocation)
        response=resA.json()

        if resA.status_code != 201:
            if 'error_message' in response.keys():
                flash(response['error_message'],'error')
            else:
                flash('Some error occured. Try Again...','error')
        else:
            flash('Succesfully Updated','success') 
        
        return render_template('adminTimings.html',show=sname,vid=vid,venue=venueName,response=response,user=current_user), 201

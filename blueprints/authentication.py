from flask import Blueprint
from flask import render_template, request, redirect, url_for, flash
from flask_login import logout_user, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models.users import User
from main.db import db

authn = Blueprint('authn', __name__)

@authn.route('/')
def index():
    return render_template("index.html")


@authn.route('/userSignup', methods=['GET','POST'])
def userSignup():
    if request.method == 'GET':
        return render_template('signup.html')

    email = request.form.get('signup_email')
    first_name = request.form.get('signup_firstname')
    last_name = request.form.get('signup_lastname')
    password = request.form.get('signup_passwd')
    name = first_name+" "+last_name

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('User already exists!','SignUp')
        return redirect(url_for('authn.userSignup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), access=0)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    flash('Successfully signed up','success')
    return redirect(url_for('authn.userLogin'))




@authn.route('/userLogin', methods=['GET','POST'])
def userLogin():
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form.get('login_email')
    password = request.form.get('login_passwd')
    remember = True if request.form.get('login_remember') else False

    user = User.query.filter_by(email=email).first()

    if not user:
        flash('Register first!','error')
        return redirect(url_for('authn.userSignup'))
    elif user and user.is_admin():
        flash('You should login as Admin User','error')
        return redirect(url_for('authn.adminLogin'))

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user:
        flash('Please check your login details and try again.','error')
        return redirect(url_for('authn.userLogin'))
    elif not check_password_hash(user.password, password):
        flash('Invalid password','error')
        return redirect(url_for('authn.userLogin')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('user.userHome'))


@authn.route('/adminLogin', methods=['GET','POST'])
def adminLogin():
    if request.method == 'GET':
        return render_template('adminLogin.html')
    
    email = request.form.get('login_email')
    password = request.form.get('login_passwd')
    remember = True if request.form.get('login_remember') else False

    user = User.query.filter_by(email=email).first()

    if user and user.is_user():
        return redirect(url_for('authn.userLogin'))

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user:
        flash('Please check your login details and try again.','error')
        return redirect(url_for('authn.adminLogin'))
    elif not check_password_hash(user.password, password):
        flash('Invalid password','error')
        return redirect(url_for('authn.adminLogin')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('admin.showVenues'))

@authn.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out')
    return redirect(url_for('authn.userLogin'))
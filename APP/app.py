from flask import (
                Flask,
                flash, 
                render_template,
                redirect,
                url_for
                )
import requests
import json
from passlib.hash import pbkdf2_sha256
from forms import *
import emails as email
import os.path
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)

urlDatabase = "http://127.0.0.1:5000"
urlWebsite = "http://127.0.0.1:5001"

# CLIENT SALT
CLIENT_SALT = os.environ['CLIENT_SALT']

# set the secret key for forms
app.config['SECRET_KEY'] = 'caed12f0f9063bf94fef30f10eaf5cbe'


## I literally do not know wtf this is lol
#this is the serializer for links
s = URLSafeTimedSerializer("dontworryboutb")

# login routes
@app.route("/", methods=['POST', 'GET'])
@app.route("/login", methods=['POST', 'GET'])
def login():
    
    form = LoginForm()

    # main validation (entered data into fields, correct email, etc.)
    if form.validate_on_submit():

        user_id = requests.get(urlDatabase + "/getuseridfromemail/" + str(form.email.data))

        # if email in database
        if (user_id.status_code == 200): 
            
            ## Uses ObjectID of that user to get their datqa
            user_data = requests.get(urlDatabase + "/getuserdata/" + str(user_id.json().get('id_employee')))
            
            inputted_password = form.password.data
            password_stored = user_data.json().get('employee_data').get('Password')

            # Now check password - does form password equal database password?
            if (pbkdf2_sha256.verify(inputted_password, password_stored)):

                flash(f"Successfully logged in!", "success")
                return redirect(url_for('home'))
            else:
                flash(f"Wrong Password!", "danger")

        else:
            flash(f"Email isn't in the database!", "danger")

    return render_template('login.html', title='login', form=form)

# register route
@app.route("/createuser", methods=['POST', 'GET'])
def create_user():
    
    form = RegistrationForm()

    # main validation (entered data into fields, correct email, etc.)
    if form.validate_on_submit():
        
        # make sure account doesn't already exist
        user_from_email_request = requests.get(urlDatabase + '/getuseridfromemail/' + form.email.data)

        if (user_from_email_request.status_code == 404): # no user in database
            
            # create user
            create_request = requests.post(
                urlDatabase + '/createnewuser/' +
                str(form.first_name.data) + '/' +
                str(form.last_name.data) + '/' +
                str(form.email.data)
            )
            
            # Email confirmation link to complete the user creation process.
            flash("User successfully created", "success")
            
            # Creates email to send to new user's logged email to complete user creation
            token = s.dumps(form.email.data, salt = CLIENT_SALT)
            link = urlWebsite + "/completeusercreation/" + token

            # Sends email out to designated user, returns
            email.create_user_email(form.email.data, link)
            
            return redirect(url_for('home'))

        else:
            flash("Account already exists with that email!", "danger")
    
    return render_template('create_user.html', title='login', form=form)

# Link from email to complete account creation process
@app.route('/completeusercreation/<token>', methods=['GET', 'POST'])
def complete_user_creation(token):

    # Create Form
    form = CompleteUserCreationForm()

    #get email from token
    email = s.loads(token, salt=CLIENT_SALT, max_age=86400)

    if form.validate_on_submit():

        # Grabs userID of email found within database
        userID = requests.get(urlDatabase + "/getuseridfromemail/" + email)

        ## If successful,
        if userID.status_code == 200:

            ## How to go about editing the data with the information provided in the form(?)
            # Updates user information in database to complete user creation process. Searches database with userID
            update_request = requests.post(

                urlDatabase + '/updateuserinfo/' +
                str(userID.json().get("id_employee")) + '/' +
                str(form.phonenumber.data) + '/' +
                str(form.street.data) + '/' +
                str(form.city.data) + '/' +
                str(form.state.data) + '/' +
                str(form.zipcode.data) + '/' +
                str(form.password.data)
            )

            if update_request.status_code == 200:
                return redirect(url_for('login'))
    
    return render_template('new_user.html', form = form)

# home route
@app.route("/home")
def home():
    return render_template('home.html', title='home')


# can run the application via command 'python3 app.py'
if __name__ == '__main__':
    app.run(port=5001, debug=True)
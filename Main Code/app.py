from flask import Flask, render_template, redirect, url_for, request, flash, session, logging, jsonify, make_response, abort
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField, SelectField, RadioField, validators
from wtforms.fields.html5 import EmailField
from wtforms import ValidationError
from datetime import timezone
import datetime
import emails as email
from markupsafe import escape
import calendar
import datetime as dt
import time
import hashlib
import requests
import json
#import emails
import texts
import phonenumbers
import random
import string
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import logging
import warnings
import os.path
import csv
import pandas
import pymongo


app = Flask(__name__)

urlDatabase = "http://127.0.0.1:5000"
urlWebsite = "http://127.0.0.1:5001"

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

CLIENT_SALT = os.environ['CLIENT_SALT']
# CLIENT_SALT = str(datetime.datetime.now())

## I literally do not know wtf this is lol
#this is the serializer for links
s = URLSafeTimedSerializer("dontworryboutb")

ACCESS = {
    "guest": 0,
    "unverified": 1,
    "user": 2,
    "admin": 3
}


## A LOT TO DO lol ##

class User():
    def __init__(self, employee_id, position, first_name, last_name, part_time_ind, email, phone, access=ACCESS["guest"]):
        self.id_employee = employee_id
        self.access = access
        self.position = position
        self.first_name = first_name
        self.last_name = last_name
        self.part_time_ind = part_time_ind
        self.email = email
        self.phone = phone
        self.session_key = None

    def set_session_key(self, session_key):
        self.session_key = session_key

def getUser():

    username = ""
    user = ""

    user = User("", "", "", "", "", "", "", "")

    return user


## Handles logging into the program
@app.route('/login', methods = ['GET', 'POST'])
def login():

    ## Grabs the login class to make shit in the html functional(?)
    form = Login(request.form)

    # Handles the user requirement in the return
    user = getUser()

    # Waits for the submit button to be pushed
    if request.method == "POST":

        # Grabs userID        
        userID = requests.get(urlDatabase + "/getuseridfromemail/" + str(form.email.data))

        print("\n\n\n", userID.json().get('id_employee'), "\n\n\n")
        # print("\n\n\n", form.password.data, "\n\n\n")

        # Checks if successful and proceeds to the password check
        if userID.status_code == 200:

            password_check = requests.get(
                urlDatabase + "/passwordcheck/" + str(userID.json().get('id_employee')), 
                headers = dict({"Password": str(form.password.data)}))

            # If successful,
            if password_check.status_code == 200:

                session_key = password_check.json().get('session_key')

                print("\n\n\n", session_key, "\n\n\n")

                session['username'] = str(userID.text.rstrip())
                session['session_key'] = session_key

                # get user data
                user_data = requests.get(
                    urlDatabase + "/getuserdata/" + str(userID.json().get('id_employee')),
                    headers=dict({'Authorization': 'Bearer ' + session['session_key']}))

                print("\n\n\n", user_data.json().get("employee_data"), "\n\n\n")

                return redirect(url_for("home"))

            else:

                # TO DO
                pass

        else:

            # Notifies of invalid email
            flash('Invalid login credentials. Please try again.')
        
    return render_template('login.html', form = form, user = user)

@app.route('/createuser', methods = ['GET', 'POST'])
def createUser():

    # Handles the user requirement in the return
    user = getUser()

    form = CreateUser(request.form)

    if request.method == "POST":

        # print("\n\n\n", form.firstName.data, "\n\n\n")
        # print("\n\n\n", form.lastName.data, "\n\n\n")
        # print("\n\n\n", form.email.data, "\n\n\n")

        ## Generates a spot in the database for the new user's info and fills what it can, returns generated employee id for possible later use.
        user_entry = requests.post(urlDatabase + "/createnewuser/" + str(form.firstName.data) + "/" + str(form.lastName.data) + "/" + str(form.email.data))

        ## If successful,
        if user_entry.status_code == 200:
            
            # Creates email to send to new user's logged email to complete user creation
            token = s.dumps(form.email.data, salt = CLIENT_SALT)
            link = urlWebsite + "/completeusercreation/" + token

            # Sends email out to designated user, returns
            email.create_user_email(form.email.data, link)

            message = "User successfully created, and an email has been sent to their email address. Please use the button below to go back to the homepage." 
            return render_template('success.html', form=form, user=user, message=message, buttonText="Home", link="/")
    
    return render_template('createUser.html', form = form, user = user)

@app.route('/completeusercreation/<token>', methods=['GET', 'POST'])
def completeUserCreation(token):

    #get user
    user = getUser()

    # Create Form
    form = NewUser(request.form)

    #get email from token
    email = s.loads(token, salt=CLIENT_SALT, max_age=86400)

    # Grabs userID of email found within database
    userID = requests.get(urlDatabase + "/getuseridfromemail/" + email)

    ## If successful,
    if userID.status_code == 200:

        print("\n\n\n", userID.json().get("id_employee"), "\n\n\n")

        # Grabs all data of user with that id in the database
        user_data = requests.get(urlDatabase + "/getuserdata/" + str(userID.json().get("id_employee")))

        print("\n\n\n", user_data.status_code, "\n\n\n")

    return render_template('newuser.html', form = form, user = user)

@app.route('/')
def home():

    ## TO DO 

    return render_template('home.html')

@app.route('/home', methods = ['GET', 'POST'])
def homepage():
    return render_template('home.html')

@app.route('/account', methods = ['GET', 'POST'])
def account():
    return render_template('account.html')

@app.route('/calendar', methods = ['GET', 'POST'])
def calendarpage():
    return render_template('calendar.html')

@app.route('/filter', methods = ['GET', 'POST'])
def filter():
    return render_template('filter.html')


###### Form Shite ######

class Login(Form):
    email = EmailField('Email', [validators.InputRequired()])
    password = PasswordField('Password', [validators.Length(
        min=8, max=40), validators.InputRequired()])


class CreateUser(Form):
    firstName = StringField('First Name',[
        validators.InputRequired()
    ])
    lastName = StringField('Last Name', [
        validators.InputRequired()
    ])

    email = EmailField('Email Address', [
    validators.InputRequired()])
    
    ## For whatever reason these two variables need to stay in for the form to run. I don't know why.
    # Error when left out: 
    # jinja2.exceptions.UndefinedError: '__main__.CreateUser object' has no attribute 'employeeCode'

    employeeCode = StringField('Employee Code (Paycore)', [

        validators.InputRequired()
        ])
    roleName = SelectField('Roll Name', coerce=int)

    # Commented Out for Right Now
    # partTime = RadioField('Part Time?', choices = [('Y', 'User is a Part-time employee'), ('N', 'User is a Full-time employee')])
    # userType = RadioField('User Type', choices = [('2', 'Employee with have normal access'), ('3', 'Employee will have admin level access')])

class NewUser(Form):
    
    # noneditable fields
    firstName = StringField('First Name')
    lastName = StringField('Last Name')

    #editable fields
    phonenumber = StringField('PhoneNumber', [
        validators.InputRequired(),
        validators.Length(min=10, max=12, message="Not a valid phone number") 
    ])

    email = StringField('Email')

    streetAddress = StringField('Street Address', [
        validators.InputRequired()
    ])


    city = StringField("City", [
        validators.InputRequired()
    ])

    stateCode = StringField("State Code",[
        validators.InputRequired(), 
        validators.Length(min=2,max=2, message="State Code is not valid")
    ])

    zipCode = StringField("Zip Code", [
        validators.InputRequired(), 
        validators.Length(min=5,max=5, message="Zip code is not valid")
    ])

    password = PasswordField("Password", [
        validators.Length(min=8, max=40), 
        validators.InputRequired()
    ])

    confirmPassword = PasswordField("Confirm Password", [
        validators.EqualTo('password', message="Passwords do not match"), 
        validators.InputRequired()
    ])

    ## Variables edited out in the HTML so it's currently not used, but needed for the code to run for whatever reason
    partTime = StringField('Part Time')
    roleName = StringField('Role Name')
    mobile = RadioField('Phone number is a mobile number', choices = [('Y', 'Yes'), ('N', 'No')])
    aptNumber = StringField('Street Address 2')



if __name__ == '__main__':
    app.run(debug=True, port=5001)
from flask import Flask, render_template, redirect, url_for, request, flash, session, logging, jsonify, make_response, abort
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, IntegerField, SelectField, RadioField, validators, EmailField
##from wtforms.fields.html5 import EmailField
from wtforms import ValidationError
from datetime import timezone
import datetime
from markupsafe import escape
import calendar
import datetime as dt
import time
import hashlib
import requests
import json
import emails
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
        userID = requests.get(urlDatabase + "/getuserfromemail/" + str(form.email.data))

        # print("\n\n\n", userID.json().get('id_employee'), "\n\n\n")
        # print("\n\n\n", form.password.data, "\n\n\n")

        # Checks if successful and proceeds to the password check
        if userID.status_code == 200:

            password_check = requests.get(urlDatabase + "/passwordcheck/" + str(userID.json().get('id_employee')), headers = dict({"Password": str(form.password.data)}))

            # If successful,
            if password_check.status_code == 200:

                return redirect(url_for("home"))

            else:

                # TO DO
                pass
        
    return render_template('login.html', form = form, user = user)


@app.route('/')
def home():

    ## TO DO 

    return render_template('home.html')


class Login(Form):
    email = EmailField('Email', [validators.InputRequired()])
    password = PasswordField('Password', [validators.Length(
        min=8, max=40), validators.InputRequired()])

if __name__ == '__main__':
    app.run(debug=True, port=5001)
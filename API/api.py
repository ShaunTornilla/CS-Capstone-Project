from flask import Flask, request, g, make_response, session, Response
from flask_restful import Resource, Api
from flask_cors import CORS
from datetime import datetime, timedelta
import time
import pyodbc
import requests
import json
import hashlib
from itsdangerous import URLSafeTimedSerializer, TimestampSigner, SignatureExpired, BadSignature, BadData
import os
import logging
import base64
import jwt
import pymongo


app = Flask(__name__)
api = Api(app)

urlDatabase = "http://127.0.0.1:5000"
urlWebsite = "http://127.0.0.1:5001"

client = pymongo.MongoClient("mongodb+srv://ShaunTornilla:cJgxXnBgwLDYKpPy@bradleycapstoneproject.c4bea.mongodb.net/test")
#client = pymongo.MongoClient("mongodb+srv://bob:bob@bradleyschedulerapplica.s3n3e.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = client.employee

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

CLIENT_SALT = os.environ['CLIENT_SALT']
# CLIENT_SALT = str(datetime.datetime.now())


## A LOT TO DO lol ##

class PasswordCheck(Resource):

    def get(self, id_employee):

        # print("\n\n\n", id_employee, "\n\n\n")
        # print("\n\n\n", request.headers.get("Password"), "\n\n\n")

        # Hashes the password grabbed from user input
        inputted_password = request.headers.get("Password")
        hashed_password = hashlib.sha256((CLIENT_SALT + inputted_password).encode('utf-8')).hexdigest()
        
        # print("\n\n\n", hashed_password, "\n\n\n")

        # Creates query to extract data from
        query = db["employee_password"].find({"id_employee": id_employee})

        # Grabs the password stored with that employee id
        for data in query:
            password_stored = data["password_string"]
        
        # print("\n\n\n", password_stored, "\n\n\n")

        #Runs a check to see if password inputted matches what's stored in the database
        if hashed_password == password_stored:
            
            # Password Successful
            response = make_response("Password Matched", 200)

        else:
            
            # Handles invalid passwords
            return response_error("400", "Bad Request", "Invalid Password"), 400

        return(response)



## Searches employee database using email as input; Returns employee ID if successful
class GetUserFromEmail(Resource):

    def get(self, email_address):

        #print("\n\n\n", email_address, "\n\n\n")

        query = db["employee_info"].find({"email_address": email_address})

        for data in query:
            result = data["id_employee"]

        response = make_response({'id_employee' : result}, 200)

        return(response)


##########

def response_error(status_code='404', error='No error message', message='No message available'):
    return {
        'status': status_code,
        'error': error,
        'message': message
    }




api.add_resource(GetUserFromEmail, '/getuserfromemail/<string:email_address>')
api.add_resource(PasswordCheck, '/passwordcheck/<string:id_employee>')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
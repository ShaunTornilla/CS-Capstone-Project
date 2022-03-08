from flask import Flask, request, g, make_response, session, Response
from flask_restful import Resource, Api
from flask_cors import CORS
from datetime import datetime, timedelta
from bson import json_util
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

#client = pymongo.MongoClient("mongodb+srv://ShaunTornilla:cJgxXnBgwLDYKpPy@bradleycapstoneproject.c4bea.mongodb.net/test")
client = pymongo.MongoClient("mongodb+srv://bob:bob@bradleyschedulerapplica.s3n3e.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

db = client.application_database

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
CLIENT_SALT = os.environ['CLIENT_SALT']
# CLIENT_SALT = str(datetime.datetime.now())

## A LOT TO DO lol ##

class PasswordCheck(Resource):

    def get(self, user_id):

        # print("\n\n\n", id_employee, "\n\n\n")
        # print("\n\n\n", request.headers.get("Password"), "\n\n\n")

        # Hashes the password grabbed from user input
        inputted_password = request.headers.get("Password")
        hashed_password = hashlib.sha256((CLIENT_SALT + inputted_password).encode('utf-8')).hexdigest()
        
        # print("\n\n\n", hashed_password, "\n\n\n")

        # Creates query to extract data from
        query = db["passwords"].find({"_id": id_employee})

        # Grabs the password stored with that employee id

        for data in query:
            password_stored = data["Hashed Password"]
            print("\n\n\n", password_stored, "\n\n\n")
        
        # Runs a check to see if password inputted matches what's stored in the database
        if hashed_password == password_stored:

            time_session_created = datetime.utcnow()
            time_session_expire = datetime.utcnow() + timedelta(days=1, seconds=0)

            # set up payload for json web token
            payload = {
                'exp': time_session_expire,
                'iat': time_session_created,
                'sub': id_employee
            }

            # generate jwt session key to return as response
            session_key = jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )

            # Password Successful
            response = make_response({"session_key": session_key}, 200)

        else:

            # Handles invalid passwords
            return response_error("400", "Bad Request", "Invalid Password"), 400

        return(response)
        # return(200)


## Searches employee database using email as input; Returns employee ID if successful
class GetUserIDFromEmail(Resource):

    def get(self, email_address):

        # print("\n\n\n", email_address, "\n\n\n")

        # Searches through database with given parameters and returns all data found with that parameter (email_address)
        # Ideally it should just be one element found or we gonna have problems lol
        query = db["employees"].find({"Email": email_address})


        # Grabs employee id for the return
        for data in query:
            
            result = parse_json(data)
            

        print("\n\n\n", result, "\n\n\n")

        response = make_response({'id_employee' : result}, 200)

        return(response)

class GetUserData(Resource):

    def get(self, user_id):

        #print("\n\n\n", user_id, "\n\n\n")

        # Creates query to extract data from
        query = db["employee_info"].find({user_id})

        for data in query:

            # parse_json handles issues regarding the objectID
            result = data["_id"]["$oid"]

        print("\n\n\n", result, "\n\n\n")
            
        response = make_response({'employee_data' : result}, 200)

        return(response)

class CreateNewUser(Resource):

    def post(self, first_name, last_name, email):

        ## Creates a new entry into the employee database (all other info will be included after email confirmation...hopefully lol)

        user_entry = db["employees"].insert_one({
            "First Name": first_name, 
            "Last Name": last_name, 
            "Phone Number": "N/A",  
            "Email": email,
            "Street": "N/A",
            "City": "N/A",
            "State": "N/A",
            "Zip Code": "N/A"})
        
        # parse_json handles issues regarding the objectID
        # Error given without parse_json: ObjectId is not JSON serializable

        response = make_response({'employee_id' : parse_json(user_entry.inserted_id)}, 200)
        
        return(response)

class CreateShiftData(Resource):
    # Add a shift
    def add_shift(self, start_time, end_time, employee_count, req_training):
        shift_entry = db["shfits"].insert_one(
            {
                "start_time": start_time,
                "end_time": end_time,
                "employee_count": employee_count,
                "req_training": req_training,
                "assigned_employees": [],
            }
        )

        response = make_response({'shift_id' : parse_json(shift_entry.inserted_id)}, 200)

        return response



class GetShiftData(Resource):
    # Find a shift with given parameters. If one is left blank or set to None, it is ignored
    def view_shift(self, start_time=None, end_time=None, employee_count = None, req_training = None, assigned_employees = None):
        shifts = db["shifts"]
        query = {}
        if start_time is not None:
            query["start_time"] = str(start_time)
        
        if end_time is not None:
            query["end_time"] = str(end_time)

        if employee_count is not None:
            query["employee_count"] = employee_count
        
        if req_training is not None:
            query["req_training"] = req_training
        
        if assigned_employees is not None:
            query["assigned_employees"] = assigned_employees

        doc = shifts.find(query)
        
        response = make_response(doc, 200)

        return response

class GetShiftDataComplex(Resource):
    def view_shift_complex(self, query):
        shifts = db["shifts"]
        
        doc = shifts.find(query)

        response = make_response(doc, 200)

        return response

##########

def response_error(status_code='404', error='No error message', message='No message available'):
    return {
        'status': status_code,
        'error': error,
        'message': message
    }

def parse_json(data):
    return json.loads(json_util.dumps(data))


api.add_resource(GetUserIDFromEmail, '/getuseridfromemail/<string:email_address>')
api.add_resource(PasswordCheck, '/passwordcheck/<string:user_id>')
api.add_resource(GetUserData, '/getuserdata/<string:user_id>')
api.add_resource(CreateNewUser, '/createnewuser/<string:first_name>/<string:last_name>/<string:email>')
api.add_resource(GetShiftData, '/getshiftdata/<string:start_time>/<string:end_time>/<int:employee_count>/<string:req_training>/<string:assigned_employees>')
api.add_resource(CreateShiftData, '/createshiftdata/<string:start_time>/<string:end_time>/<int:employee_count>/<string:req_training>')
# api.add_resource(CompleteUserCreation, '/completeusercreation/<string:token>')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
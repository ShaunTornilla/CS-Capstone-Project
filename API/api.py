from flask import Flask, request, g, make_response, session, Response
from flask_restful import Resource, Api
from flask_cors import CORS
from datetime import datetime, timedelta
from bson import json_util
import time
import pyodbc
import requests
import json
from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer, TimestampSigner, SignatureExpired, BadSignature, BadData
import os
import logging
import base64
import jwt
import pymongo
from bson.objectid import ObjectId


app = Flask(__name__)
api = Api(app)

urlDatabase = "http://127.0.0.1:5000"
urlWebsite = "http://127.0.0.1:5001"

#client = pymongo.MongoClient("mongodb+srv://ShaunTornilla:cJgxXnBgwLDYKpPy@bradleycapstoneproject.c4bea.mongodb.net/test")
client = pymongo.MongoClient("mongodb+srv://bob:bob@bradleyschedulerapplica.s3n3e.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

application_db = client.application_database

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
CLIENT_SALT = os.environ['CLIENT_SALT']
# CLIENT_SALT = str(datetime.datetime.now())

## A LOT TO DO lol ##

## Searches employee database using email as input; Returns employee ID if successful
class GetUserIDFromEmail(Resource):

    def get(self, email_address):

        # print("\n\n\n", email_address, "\n\n\n")

        # Searches through database with given parameters and returns all data found with that parameter (email_address)
        # Ideally it should just be one element found or we gonna have problems lol
        query = application_db["employees"].find({"Email": email_address})

        # If nothing exists in the database,
        if query.count() == 0:
            return response_error("400", "No account found."), 404

        else:
            # Grabs employee id for the return
            for data in query:           
                result = str(data["_id"])

            return make_response({'id_employee' : result}, 200)

class GetUserData(Resource):

    def get(self, user_id):

        print("\n\n\n", user_id, "\n\n\n")

        # Creates query to extract data from
        query = application_db["employees"].find({"_id": ObjectId(user_id)})

        for data in query:
            
            # parse_json handles issues regarding the objectID
            # Error given without parse_json: ObjectId is not JSON serializable
            result = parse_json(data)

        response = make_response({'employee_data' : result}, 200)

        return(response)

##### 

class CreateNewUser(Resource):

    def post(self, first_name, last_name, email):

        ## Creates a new entry into the employee database (all other info will be included after email confirmation...hopefully lol)

        user_entry = application_db.employees.insert_one({
            "First Name": first_name, 
            "Last Name": last_name, 
            "Phone Number": "N/A",  
            "Email": email,
            "Street": "N/A",
            "City": "N/A",
            "State": "N/A",
            "Zip Code": "N/A",
            "Password": "N/A"})

        response = make_response({'employee_id' : parse_json(user_entry.inserted_id)}, 200)
        
        return(response)

class UpdateUserInfo(Resource):

    def post(self, userid, phonenumber, street, city, state, zipcode, password):

        ## Searches the database by ObjectID to update the information of that user with the rest of the required info.
        updated_info = application_db["employees"].update_one({"_id": ObjectId(userid)},

            # $set will update the entries you put in the body (preferably elements already set by the createuser early on in the process)
            {"$set":

                ## The variables being updated
                {
                    "Phone Number": phonenumber,
                    "Street": street,
                    "City": city,
                    "State": state,
                    "Zip Code": zipcode,
                    "Password": pbkdf2_sha256.using(rounds = 8000, salt_size = 10).hash(password)
                }
            }
        )

        response = make_response({'message' : 'User Creation Successful'}, 200)

        return(response)

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
api.add_resource(GetUserData, '/getuserdata/<string:user_id>')
api.add_resource(CreateNewUser, '/createnewuser/<string:first_name>/<string:last_name>/<string:email>')
api.add_resource(UpdateUserInfo, '/updateuserinfo/<string:userid>/<string:phonenumber>/<string:street>/<string:city>/<string:state>/<string:zipcode>/<string:password>')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
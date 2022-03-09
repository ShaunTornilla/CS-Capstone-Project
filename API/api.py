from collections import UserDict
from flask import Flask, make_response
from flask_restful import Resource, Api
from pymongo import MongoClient
import certifi
import json
from bson import json_util

app = Flask(__name__)
api = Api(app)

urlDatabase = "http://127.0.0.1:5000"
urlWebsite = "http://127.0.0.1:5001"

# connect to MongoDB
ca = certifi.where()
connection = MongoClient("mongodb+srv://bob:bob@bradleyschedulerapplica.s3n3e.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",tlsCAFile=ca)
application_db = connection.application_database
employee_db = application_db.employees


## Searches employee database using email as input; Returns employee if successful
class GetUserFromEmail(Resource):

    def get(self, email_address):
        # find employee with given email address
        query = application_db.employees.find_one( {"Email": email_address} )
        if query != None:
            response = parse_json(query)
            status_code = 200
        else:
            response = {"user_error_404": "There are no users for this email"}
            status_code = 404
        return make_response(response, status_code)

# creates a new user and adds it to database
class CreateNewUser(Resource):
    
    def post(self, firstname, lastname, email_address):
        # insert document into employee database
        query = employee_db.insert_one({
            "First Name": firstname,
            "Last Name": lastname,
            "Email": email_address
        })
        print(query)

        return 200

api.add_resource(GetUserFromEmail, '/getuserfromemail/<string:email_address>')
api.add_resource(CreateNewUser, '/createnewuser/<string:firstname>/<string:lastname>/<string:email_address>')


def parse_json(data):
    return json.loads(json_util.dumps(data))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
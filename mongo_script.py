from pymongo import MongoClient
import certifi
from passlib.hash import pbkdf2_sha256
import uuid

ca = certifi.where()
connection = MongoClient("mongodb+srv://bob:bob@bradleyschedulerapplica.s3n3e.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",tlsCAFile=ca)
employee_db = connection.application_database.employees

new_id = uuid.uuid4().hex

# method to add hashed password for each employee
def add_password():
    all_docs = employee_db.find()
    for doc in all_docs:
        password = pbkdf2_sha256.hash("password123")
        employee_db.update_one({"_id": doc["_id"]}, {"$set": {"password": password}})

# method to add unique id for each employee
def add_new_id():
    all_docs = employee_db.find()
    for doc in all_docs:
        new_id = uuid.uuid4().hex
        employee_db.update_one({"_id": doc["_id"]}, {"$set": {"new_id": new_id} })


query = employee_db.find_one( {"Email": "erikbendt33@gmail.com"} )
print(query)

employee_db.insert_one({
    "First Name": "erik",
    "Last Name": "bendt",
    "Email": "erikbendt33@gmail.com"
    })
query = employee_db.find_one( {"Email": "erikbendt33@gmail.com"} )
print(query)

from pymongo import MongoClient
from faker import Faker
import random

# Connect to the database
def connect():
    client = MongoClient("mongodb+srv://bob:bob@bradleyschedulerapplica.s3n3e.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    if client:
        print("successful connection")
        db = client["application_database"]
        return db
    else:
        print("connection failed")

# Add a shift
def add_shift(db, start_time, end_time, employee_count, req_training):
        shift_entry = db["shfits"].insert_one(
            {
                "start_time": start_time,
                "end_time": end_time,
                "employee_count": employee_count,
                "req_training": req_training,
                "assigned_employees": [],
            }
        )

        return shift_entry

# Find a shift with given parameters. If one is left blank or set to None, it is ignored
def view_shift(db, date=None, employee_count = None, req_training = None, assigned_employees = None):
    shifts = db["shifts"]
    query = {}
    if date is not None:
        query["time"] = str(date)
    
    if employee_count is not None:
        query["employee_count"] = employee_count
    
    if req_training is not None:
        query["req_training"] = req_training
    
    if assigned_employees is not None:
        query["assigned_employees"] = assigned_employees

    doc = shifts.find(query)
    
    print("Query complete!")
    return doc

# Find a given query. Alows for complex queries to be run
def view_shift_complex(db, query):
    shifts = db["shifts"]
    
    doc = shifts.find(query)

    return doc

# Populate the database with (count) dummy shifts
def populate_shifts(db, count):
    for i in range(0, count):
        add_shift(db, fake.date_time(), fake.date_time(), random.randrange(0, 4), random.choice(["forklift", "ladder", "machine", "welding", "security", "chemical"]))

if __name__ == "__main__":
    fake = Faker()
    db = connect()

    populate_shifts(db, 20)


from pymongo import MongoClient
from faker import Faker
import random
import certifi
import datetime

# Connect to the database
def connect():
    ca = certifi.where()
    client = MongoClient("mongodb+srv://bob:bob@bradleyschedulerapplica.s3n3e.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",tlsCAFile=ca)
    if client:
        print("successful connection")
        db = client["application_database"]
        return db
    else:
        print("connection failed")

# Add a shift
def add_shift(db, start_time, end_time, employee_count, req_training):
        shift_entry = db["shifts"].insert_one(
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
def view_shift(db, start_time=None, end_time=None, employee_count = None, req_training = None, assigned_employees = None):
    shifts = db["shifts"]
    query = {}
    if start_time is not None:
        query["start_time"] = start_time
    
    if end_time is not None:
        query["end_time"] = end_time

    if employee_count is not None:
        query["employee_count"] = employee_count
    
    if req_training is not None:
        query["req_training"] = req_training
    
    if assigned_employees is not None:
        query["assigned_employees"] = assigned_employees

    doc = shifts.find(query)

    x = []

    for i in doc:
        x.append(i)

    print("Query complete!")
    return doc

# Find a given query. Alows for complex queries to be run
def view_shift_complex(db, query):
    shifts = db["shifts"]
    
    doc = shifts.find(query)

    return doc

def assign_shift(db, shift, employeee_fname, employee_lname):
    shifts = db["shifts"]
    employees = db["employees"]
    query = {}

    # TODO: Swap to a universal unique lookup (or recieve ID directly)
    query["First Name"] = employeee_fname
    query["Last Name"] = employee_lname

    doc = employees.find(query)

    # Return the first employee found
    employee = doc[0]

    print(employee)

    shifts.update_one(
        {"start_time": shift["start_time"],
         "end_time": shift["end_time"],
         "req_training": shift["req_training"]},
        {"assigned_employees": {employee["new_id"]}},
    )


# Populate the database with (count) dummy shifts
def populate_shifts(db, count):
    for i in range(0, count):
        add_shift(db, fake.date_time(), fake.date_time(), random.randrange(0, 4), random.choice(["forklift", "ladder", "machine", "welding", "security", "chemical"]))

if __name__ == "__main__":
    fake = Faker()
    db = connect()
    x = 0
    #populate_shifts(db, 20)
    #shift = view_shift(db, start_time=datetime("1974-07-13T00:25:08.000+00:00"), end_time=datetime("2017-10-30T01:04:40.000+00:00"), employee_count=1, req_training="security")
    #for i in x:
    #    print(i)

    #print(x)
    
    #y = view_shift(db)
    #for i in y:
        #print(i)


    assign_shift(db, shift=x, employeee_fname="Kyle", employee_lname="Lane")


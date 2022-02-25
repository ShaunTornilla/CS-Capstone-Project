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

client = pymongo.MongoClient("mongodb+srv://ShaunTornilla:cJgxXnBgwLDYKpPy@bradleycapstoneproject.c4bea.mongodb.net/test")
urlDatabase = client.test_database

print("\n\n\n", urlDatabase, "\n\n\n")

#urlDatabase = "http://127.0.0.1:5000"
urlWebsite = "http://127.0.0.1:5001"

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

CLIENT_SALT = os.environ['CLIENT_SALT']
# CLIENT_SALT = str(datetime.datetime.now())


## A LOT TO DO lol ##


@app.route('/templatepage')
def test():

    return("Hello Dicks")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
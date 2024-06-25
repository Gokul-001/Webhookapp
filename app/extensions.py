from flask_pymongo import PyMongo
from pymongo import MongoClient

conn="mongodb://localhost:27017/"

client = MongoClient(conn)
db = client.get_database("data") 
logs = db.get_collection("webhook")

def server_connect():
    try:
        des=client.server_info()
    except Exception:
        des="Unable to connect to the server"
    return des
from app.logcontrol import logger
from flask_pymongo import PyMongo
from pymongo import MongoClient

conn="mongodb://localhost:27017/"

client = MongoClient(conn)
db = client.get_database("data") 
logs_db = db.get_collection("webhook")
logger("Database").info("Database created")

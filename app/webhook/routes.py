from email import message
import re
from datetime import datetime as dt
import datetime
from flask import Blueprint, json, render_template, request,jsonify
from app.logcontrol import logger
from app.extensions import logs_db

# Creating a Blueprint for the webhook endpoint
webhook = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook.route('/')
def welcome():
    logger('webhook').info("Welcome message")
    return jsonify(message="Welcome",status=200),200

@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.headers['Content-Type'] == "application/json":
        data = request.json
        try:
            #pull request [open, close, merge, Synchronize]
            if data.get('action') in ['opened','closed','synchronize']:
                action = data.get('action',"No data")
                request_id = data.get("pull_request",{}).get("id","No data")
                author = data.get("pull_request",{}).get("user",{}).get("login","No data")
                from_branch = data.get('pull_request',{}).get('head',{}).get('ref',"No data")
                to_branch = data.get('pull_request',{}).get('base',{}).get('ref',"No data")

                if action=="closed":
                    if data.get("pull_request",{}).get("merged",False):
                        action="merged"
                    else:
                        action="closed without merge"
                
                elif action =="synchronize":
                    action='synchronize'
                logger('webhook/receiver').info(action)
            #push 
            elif "head_commit" in data and "pusher" in data:
                request_id = data.get('head_commit',{}).get('id',"No data")
                action = "pushed"
                author = data.get("pusher",{}).get('name',"No data")
                to_branch = data.get("ref","None").split("/")[-1]
                from_branch = data.get('base_ref',"None")
                logger('webhook/receiver').info(action)
            #default
            else:
                action = "unknown"
                request_id = "No data"
                author = "No data"
                from_branch = "No data"
                to_branch = "No data"
                logger('webhook/receiver').info(action)

        except Exception as e:
            logger('webhook/receiver').error("Invalid data %s",e)
            return jsonify(message=f"Invalid data : {e}",status=400), 400
            
        timestamp=dt.utcnow()
        # Creating a document to store in MongoDB
        doc = {
            "request_id": request_id,
            "author": author,
            "action": action,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }
        try:
            logs_db.insert_one(doc)
            logger('Database').info("Data received and stored in MongoDB ")
            return jsonify(message="Data received and stored in MongoDB",status=200),200
        except Exception as e:
            logger("Database").info("Data couldnt be stored in DB : ",e) 
            return jsonify(message=f"Data couldnt be stored in DB : {e}",status=500),500
    else:
        logger('webhook/receiver').critical("Unsupported data")
        return jsonify(message="Unsupported data",status= 415),415
    
@webhook.route('/ui', methods=["GET"])
def webhook_home1():
    return render_template("index.html", Title="Recent Repo Events")

@webhook.route('/ui/data', methods=["GET"])
def webhook_home():
    tasks = []
    def suffix(day):
        suffix = "th"
        if day % 10 == 1 and day != 11:
            suffix = "st"
        elif day % 10 == 2 and day != 12:
            suffix = "nd"
        elif day % 10 == 3 and day != 13:
            suffix = "rd"
        return suffix
    
    # Loop through tasks retrieved from MongoDB and format them
    time_now_15 = dt.utcnow()-datetime.timedelta(seconds=15)
    for task in logs_db.find({'timestamp' : { '$gte': time_now_15} }):
    #for task in logs_db.find().sort("timestamp", -1):
        task.update({
        'author': str(task.get('author', '')),
        'request_id': str(task.get('request_id', '')),
        'from_branch': str(task.get('from_branch', '')),
        'to_branch': str(task.get('to_branch', '').split("/")[-1]),
        'action': str(task.get('action', '')),
        'timestamp': task['timestamp'].strftime(f"%d{suffix(task['timestamp'].day)} %B %Y - %I:%M %p UTC"),
        '_id': str(task.get('_id', ''))
    })
        tasks.append(task)
    logger("ui/data").info("Retrieving info from DB")
    return jsonify(tasks),200

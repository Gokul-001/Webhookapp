import re
from flask import Blueprint, json, render_template, request,jsonify
from app.extensions import logs,server_connect
import datetime

# Creating a Blueprint for the webhook endpoint
webhook = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook.route('/')
def welcome():
    print("Welcome")
    return "Welcome"

@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.headers['Content-Type'] == "application/json":
        info = json.dumps(request.json)
        print(info)

        data = request.json

        try:
            request_id = data["pull_request"]['id']
            author = data['pull_request']['user']['login']
            action = data['action']
            from_branch = data['pull_request']['head']['ref']
            to_branch = data['pull_request']['base']['ref']
            timestamp = datetime.datetime.now()
        except KeyError:
            request_id = data['head_commit']['id']
            action = "pushed"
            author = data["pusher"]['name']
            from_branch = data['base_ref']
            to_branch = data['ref']
            timestamp = datetime.datetime.now()
        except Exception as e:
            print("Invalid data")
            return f"Invalid data : {e}", 400
            
        print(request_id, author, from_branch, to_branch)

        # Creating a document to store in MongoDB
        doc = {
            "request_id": request_id,
            "author": author,
            "action": action,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp
        }

        logs.insert_one(doc)
        
        return "Data received and stored in MongoDB", 200
    else:
        return "Unsupported data", 415

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
    for task in logs.find().sort("timestamp", -1):
        task['author'] = str(task['author'])
        task['request_id'] = str(task['request_id'])
        task['from_branch'] = str(task['from_branch'])
        task['to_branch'] = str(task['to_branch'])
        task['action'] = str(task['action'])
        task['timestamp'] = task['timestamp'].strftime("%d{} %B %Y - %I %M:%p UTC".format(suffix(task['timestamp'].day)))
        task['_id'] = str(task['_id'])
        tasks.append(task)

    return jsonify(tasks)

import re
from flask import Blueprint, json, render_template, request
from app.extensions import logs,server_connect
import datetime


webhook = Blueprint('webhook', __name__, url_prefix='/webhook')


@webhook.route('/')
def welcome():
    print("Welcone")
    return "Wlcme"


@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.headers['Content-Type']=="application/json":
        info=json.dumps(request.json)
        print(info)

        data=request.json

        try:
            request_id=data["pull_request"]['id']
            author=data['pull_request']['user']['login']
            action=data['action']
            from_branch=data['pull_request']['head']['ref']
            to_branch=data['pull_request']['base']['ref']
            timestamp=datetime.datetime.now()
        except KeyError:
            request_id=data['head_commit']['id']
            action = "pushed"
            author=data["pusher"]['name']
            from_branch=data['base_ref']
            to_branch=data['ref']
            timestamp=datetime.datetime.now()
        except Exception as e:
            print("Invalid data")
            return f"Invalid data : {e}",400
            
        print(request_id,author,from_branch,to_branch)
        print(server_connect())

        doc={
        "request_id":request_id,
        "author":author,
        "action":action,
        "from_branch":from_branch,
        "to_branch":to_branch,
        "timestamp":timestamp}

        logs.insert_one(doc)
        return "Data recieved and stored in MongDb",200
    else:
        return "Unsupported data",415
        

@webhook.route('/ui',methods=["GET"])
def webhook_home():
  tasks=[]
  def suffix(day):
        suffix = "th"
        if day % 10 == 1 and day != 11:
            suffix = "st"
        elif day % 10 == 2 and day != 12:
            suffix = "nd"
        elif day % 10 == 3 and day != 13:
            suffix = "rd"
        return suffix
  #getting data from webhook collection
  for task in logs.find().sort("timestamp",-1):
    task['author']=str(task['author'])
    task['request_id']  = str(task['request_id']) 
    task['from_branch'] = str(task['from_branch'])
    task['to_branch'] = str(task['to_branch'])
    task['action'] = str(task['action'])
    time = task['timestamp'] = task['timestamp'].strftime("%d{} %B %Y - %I %M:%p %z UTC".format(suffix(task['timestamp'].day)))
    tasks.append(task)
    
  return render_template("index.html",Title="Recent Repo Events",tasks=tasks)
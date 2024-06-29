import os
from dotenv import load_dotenv
from app import create_app
from app.logcontrol import logger

app = create_app()
logger("app").info("App created")


if __name__ == '__main__': 
    load_dotenv()
    logger("app").info("App running...")
    from waitress import serve
    serve(app, host=os.getenv("host"), port=os.getenv('port'))
    #app.run(debug=True,port=os.getenv('port'))
    

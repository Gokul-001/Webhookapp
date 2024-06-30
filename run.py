import os
from dotenv import load_dotenv
from app import create_app
from app.logcontrol import logger

load_dotenv()
app = create_app()
host = os.getenv('host', '127.0.0.1')
port = os.getenv('port', 8000)

if __name__ == '__main__': 
    logger("app").info("App running...")
    from waitress import serve
    serve(app, host=host, port=int(port))
    
    

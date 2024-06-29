import os,logging
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.WARNING)
def logger(name):
    logging.basicConfig(filename=os.getenv('logs_path'),
                            filemode='a',
                            level=logging.INFO,
                            format="%(asctime)s - %(name)s -- %(message)s ",
                            datefmt='%Y-%m-%d | %H:%M:%S'
                            )
    log=logging.getLogger(name)
    return log


from flaskServer import app
import threading
class flaskServerThread(threading.Thread):
        def __init__(self):
                super(flaskServerThread,self).__init__()
        def run(self):
                #Run the flask server
                app.run(host = '0.0.0.0')

from flaskServer import app
from flask import Flask, request, redirect, url_for, abort, flash, render_template
import time, thread, os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
#app.debug = True
import upstream    
import downstream
@app.route("/imu")
def getIMU():
        upstream.lock.acquire(True)
        returnString = str(upstream.imu.pitch)
        returnString+=" "+ str(upstream.imu.roll)
        returnString+=" "+(str(upstream.imu.yaw))
        app.logger.debug(returnString)
        upstream.lock.release()
        return returnString

@app.route('/')
def mainPage():
        app.logger.debug('A value for debugging')
        return render_template('index.html', )

@app.route('/buttons/<button>',methods=['GET','POST'])
def atButtonPress(button):
        app.logger.debug('Button %s pressed' % button)
        upstream.lock.acquire()
        upstream.yaw=button
        upstream.lock.release()
        
        downstream.lock.acquire()
        downstream.state = button
        downstream.lock.release()
        return redirect (url_for('mainPage'))

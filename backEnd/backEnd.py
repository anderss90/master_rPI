import math
import threading, time
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from serial import SerialException 

from imu import imu
from sonarSys import sonarSys
import upstream
import downstream
from posController import fControl
from position import position
from uartHandler import uartHandler
serialPort = "/dev/ttyUSB0"
serialPort2 = "/dev/ttyUSB1"
serialPort3 = "/dev/ttyUSB2"
baudRate = 115200

debugprinting = False 
loopInterval = 0.08 # 10 Hz = 100ms (Adjusted down to keep up with arduino)
enableLogging = True
nSeconds = 15
nLoops = nSeconds * 10

class backEndThread(threading.Thread):
        def __init__(self,threadID):
                print "backEndThread init"
                super(backEndThread,self).__init__()
                self.ss = sonarSys()
                self.fc = fControl()
                self.imu = imu(0,0,0,0,0,0)
                self.sonarValues = {0,0,0,0,0,0}
                self.pos = position(0,0,0,False,False,False)
                self.error = {"uart":"ok","fc":"ok","ss":"ok"}
                self.state = "landed"
                if enableLogging:
                        timeString = time.strftime("%d.%m-%H.%M")
                        pathString = "/home/pi/master/logs/"+timeString+"/"
                        debugname = "logTesting"
                        debugPath = "/home/pi/master/logs/"+debugname+"/"
                        pathString = debugPath
                        self.ssLogs = {}
                        if not os.path.exists(pathString):
                                os.makedirs(pathString)

                        #sonar system logs
                        for key,sonar in self.ss.sonars.iteritems():
                                keystr = str(key)
                                self.ssLogs[keystr] = open(pathString+key+".dat",'w')
                                self.ssLogs[keystr].write("#Time(ms)\t Value \t Validity \t avgValue \t Diff \t Outliers \t invalidReason\t SD \n")

                        self.ssLogs["pairs"] = open(pathString+"pairs.dat",'w') 
                        self.ssLogs["pairs"].write("#Time(ms)\t xPos \t yPos \t zPos \t xValid \t yValid \t zValid \t validreasons x-y-z \n")

                        #flight controller logs
                        self.fcLog = open(pathString+"fcLog.dat",'w')
                        self.fcLog.write("#Time(ms)\t  xPos \t yPos \t zPos \t xVal \t yVal \t zVal \t State \t oRoll \t oPitch \t oYaw \t oThrottle \t spX \t spY \t spZ \n")

                        #IMU logging
                        self.imuLog = open(pathString+"imuLog.dat",'w')
                        self.imuLog.write("#Time(ms)\t Roll \t Pitch \t Yaw \t gX \t Gy \t gZ \n")



                        #self.error["log"]="error"
                try:
                        self.uart = uartHandler(serialPort,baudRate)
                except SerialException:
                        print "Error opening serial port " + serialPort 
                        try:
                                self.uart = uartHandler(serialPort2,baudRate)
                        except SerialException:
                                print "Error opening serial port " + serialPort2
                                try:
                                        self.uart = uartHandler(serialPort3,baudRate)
                                except SerialException:
                                        print "Error opening serial port " + serialPort3
                                        self.error["uart"]="fail"

        def run(self):
                counter = 0
                print "backEndThread run()"
                #Check if all is good in the hood
                for key,value in self.error.iteritems():
                        if value != "ok":
                                print "Shutting down backEnd because of %s error"%key
                                return
                nextExecTime = time.time()+loopInterval
                while True: 
                        #sleep until next
                        if time.time() < nextExecTime:
                                sleepTime = nextExecTime-time.time()
                                if sleepTime > 0:
                                        time.sleep(sleepTime)
                        nextExecTime = time.time()+loopInterval

                        #Read sensor data from uart
                        if debugprinting: print "reading Uart"
                        self.uart.readLine()
                        self.uart.parseInput()
                        self.sonarValues = self.uart.sonarValues
                        self.imu = self.uart.imuValues

                        #Estimate position using the sonar system
                        if debugprinting: print "updating ss"
                        self.ss.update(self.imu,self.sonarValues)
                        self.pos = self.ss.pos

                        #Send data to frontend
                        if debugprinting: print "acquiring upstream"
                        upstream.lock.acquire()
                        upstream.sonars = self.sonarValues
                        upstream.imu = self.imu
                        upstream.pos = self.pos
                        if debugprinting: print "releasing upstream"
                        upstream.lock.release()

                        #Update position regulator
                        downstream.lock.acquire()
                        if self.state != "hover" and downstream.state == "hover":
                                self.fc.startHover(self.pos)
                        self.state = downstream.state
                        downstream.lock.release()
                        self.fc.update(self.state,self.pos)

                        #Send setpoints to FC via MCU
                        self.uart.addSetpoints(self.fc.output)
                        self.uart.sendBuffer()
                        
                        #debug print
                        counter+=1
                        if True:
                                self.debugPrint()
                                #counter = 0
                        #logs
                        if counter > 1:
                                self.logger(counter*100)
                        #Exit loop
                        if counter > nLoops:
                                self.closeDown()
                                break

        def closeDown(self):
                for key,log in self.ssLogs.iteritems():
                        log.close()
                self.fcLog.close()
                self.imuLog.close()

        def logger(self,timeMs):
                #log sonar values
                for key in self.ss.sonars:
                        if key == "pairs":
                                break
                        cur = self.ss.sonars[key]
                        #self.ssLogs[key].write("KLOLOOLOL \n")
                        self.ssLogs[key].write("%i\t %.2f \t%i \t%.2f \t%.2f \t%i \t%s\t %.2f\t %.2f \n"%(timeMs,cur.value,cur.validity,cur.avgValue,math.fabs(cur.value-cur.avgValue),cur.nOutliers,cur.invalidReason,cur.sd,cur.lowpassed))
                        
                #logs sonar pair values
                x = self.ss.sonarPairs["x"]
                y = self.ss.sonarPairs["y"]
                z = self.ss.sonarPairs["z"]
                imu = self.imu
                self.ssLogs["pairs"].write("%i\t %.2f\t %.2f\t %.2f\t %i\t %i\t %i\t %s\t %s\t %s\n"%(timeMs,x.pos,y.pos,z.pos,x.validity,y.validity,z.validity,x.invalidReason,y.invalidReason,z.invalidReason))

                #log flight control values
                fc = self.fc
                pos = self.pos
                # DEBUG
                fc.state = 0
                self.fcLog.write("%i\t %.2f\t %.2f\t %.2f\t %i\t %i\t %i\t %s\t %i\t %i\t %i\t %i\t %.2f\t %.2f\t %.2f\n"%(timeMs,pos.x,pos.y,pos.z,pos.xValid,pos.yValid,pos.zValid,fc.state,fc.output["roll"],fc.output["pitch"],fc.output["yaw"],fc.output["throttle"],fc.setPoints["x"],fc.setPoints["y"],fc.setPoints["z"]))

                #imulogging
                self.imuLog.write("%i\t %.2f\t %.2f\t %.2f\t %.2f\t %.2f\t %.2f\n"%(timeMs,imu.roll,imu.pitch,imu.yaw,imu.gx,imu.gy,imu.gz))

        def debugPrint(self):
                sys.stderr.write("\x1b[2J\x1b[H")
                print "X: %.2f Y: %.2f Z: %.2f"%(self.pos.x,self.pos.y,self.pos.z)
                print str(self.imu.roll)+" "+str(self.imu.pitch)+" "+str(self.imu.yaw)
                print self.sonarValues
                print "   Right: %s   Back: %s   Up: %s   Down: %s   Front: %s   Left: %s "%(self.ss.sonars["right"].validity,self.ss.sonars["back"].validity,self.ss.sonars["up"].validity,self.ss.sonars["down"].validity,self.ss.sonars["front"].validity,self.ss.sonars["left"].validity)
                 
                print "Right: %.2f Back: %.2f Up: %.2f Down: %.2f Front: %.2f Left: %.2f "%(self.ss.sonars["right"].avgValue,self.ss.sonars["back"].avgValue,self.ss.sonars["up"].avgValue,self.ss.sonars["down"].avgValue,self.ss.sonars["front"].avgValue,self.ss.sonars["left"].avgValue)
if __name__ == "__main__":
        thread1 = backEndThread(1)
        thread1.start()


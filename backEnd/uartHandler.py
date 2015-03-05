import time
from serial import SerialException
import serial
from imu import imu
serialPort = "/dev/ttyUSB2"
baudRate = 115200
debugPrint= False
debugLevel = 0
outputBufferSize = 64
class uartHandler:
        def __init__(self,port,baudRate):
                self.baudrate = baudRate
                self.port = port
                self.sonarValues = {}
                self.infoValues = {}
                self.imuValues = imu(0,0,0,0,0,0)
                self.lastReceiveTime = 0
                self.inputString = ""
                self.outputString = ""
                self.ser = serial.Serial(port,baudRate) # raises SerialException, ValueError 
                
        def addSetpoints(self,sp):
                roll = sp["roll"]
                pitch = sp["pitch"]
                yaw = sp["yaw"]
                throttle = sp["throttle"]
                self.outputString += "r:"+str(roll)+";p:"+str(pitch)+";y:"+str(yaw)+";t:"+str(throttle)+";"
                if debugPrint: print self.outputString
                
        def addCommand(self,command):
                if len(self.outputString) >= outputBufferSize: 
                        sendBuffer()
                        if debugPrint: print "Output buffer full, sending it out before adding cmd"
                self.outputString += "c:"+command+";"
                if debugPrint: print self.outputString

        def sendBuffer(self):
               bytesSent = self.ser.write(self.outputString) 
               if bytesSent < len(self.outputString):
                        print "Error. Did not send all bytes. Tried to send %i , sent %i" %(len(self.outputString),bytesSent)
               else:
                       if debugLevel >= 1: print "Sent %i bytes : %s" %(bytesSent,self.outputString)
               self.outputString = ""
        def readLine(self):
                self.inputString = self.ser.readline()
                if debugLevel >= 1: print "Received " + self.inputString
                # Clearing input buffer to avoid getting old data
                self.ser.flushInput()
        def parseInput(self):
                if debugPrint: print self.inputString
                data = self.inputString.split(';')
                for block in data:
                        if debugPrint: print block
                        info = block.split(':')
                        if len(info)<2:
                                break
                        type= info[0]
                        value = num(info[1])
                        if value == "error":
                                break
                        #Sonar
                        if type == "sf":
                                self.sonarValues["front"]=value
                        if type == "sb":
                                self.sonarValues["back"]=value
                        if type == "sr":
                                self.sonarValues["right"]=value
                        if type == "sl":
                                self.sonarValues["left"]=value
                        if type == "sd":
                                self.sonarValues["down"]=value
                        if type == "su":
                                self.sonarValues["up"]=value
                        #IMU
                        if type == "p":
                                self.imuValues.pitch = value
                        if type == "r":
                                self.imuValues.roll = value
                        if type == "y":
                                self.imuValues.yaw = value
                        if type == "gx":
                                self.imuValues.gx = value
                        if type == "gy":
                                self.imuValues.gy = value
                        if type == "gz":
                                self.imuValues.gz = value
                self.inputString = ""
                            
def num(s):
        try:
            return int(s)
        except ValueError:
                try:
                        return float(s)
                except ValueError:
                        print "ValueError %s"%s
                        return "error"
def testFunction():
        try:
                uart = uartHandler(serialPort,baudRate)
        except SerialException:
                print "Hey! This aint no serial port"
                return
        except ValueError:
                print "Invalid input parameters"
                return
        uart.inputString = "sf:1;sb:2;sr:3;sl:4;sd:5;su:6;p:8;r:10;y:11;gy:12;gx:13;gz:14;"
        print uart.inputString
        uart.parseInput()
        uart.readLine()
        uart.parseInput()
        uart.addSetpoints(4,5,6)
        uart.addSetpoints(7,8,9)
        uart.sendBuffer()
        uart.readLine()
        uart.parseInput()
def testRead():
        try:
                uart= uartHandler(serialPort,baudRate)
        except SerialException:
                print "FAIL"
                return
        except ValueError:
                print "valueError"
                return
        while True:
                uart.readLine()
                #print uart.inputString
                time.sleep(0.1)
if __name__ == "__main__":
        #testFunction()
        testRead()

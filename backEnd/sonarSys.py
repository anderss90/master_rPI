import math
#from imu import imu
from sonar import sonar
from position import position
maxPairDiff = 2

class sonarPair:
        def __init__(self,sonarA,sonarB,axis):
                self.a = sonarA
                self.b = sonarB
                self.axis = axis
                self.pos = 0
                self.validity = False
                self.invalidReason = "none"
        
        def evaluate(self):
                aPos = -1*self.a.avgValue-self.a.offset
                bPos = self.b.avgValue-self.b.offset

                if self.a.validity or self.b.validity:
                        self.invalidReason = "none"
                        self.validity = True
                        if self.a.validity and self.b.validity:
                                difference = math.fabs(aPos-bPos)
                                if difference  < maxPairDiff:
                                        self.pos = (aPos+bPos)/2
                                else:
                                        self.validity = False
                                        self.invalidReason = "%.2f"%difference
                        else:
                                if self.a.validity:
                                        self.pos = aPos
                                elif self.b.validity:
                                        self.pos = bPos
                else:
                        self.validity = False
                        self.invalidReason = "novalid"
                
class sonarSys:
        def __init__(self):
                self.pos = position(0,0,0,False,False,False)
                self.sonars = {}
                self.sonarPairs = {}
                self.sonars["front"]=sonar("front")
                self.sonars["back"]=sonar("back")
                self.sonars["right"]=sonar("right")
                self.sonars["left"]=sonar("left")
                self.sonars["down"]=sonar("down")
                self.sonars["up"]=sonar("up")
                self.sonarPairs["x"] = sonarPair(self.sonars["front"],self.sonars["back"],"x")
                self.sonarPairs["y"] = sonarPair(self.sonars["right"],self.sonars["left"],"y")
                self.sonarPairs["z"] = sonarPair(self.sonars["down"],self.sonars["up"],"z")

        def update(self,imu,sonarValues):
                i = 0
                for key,value in sonarValues.iteritems():
                        self.sonars[key].update(float(value))
                        self.sonars[key].evaluate(imu,self.pos)
                        i=i+1
                for axis,sonarPair in self.sonarPairs.iteritems():
                        sonarPair.evaluate()
                
                #store position estimate
                self.pos.x = self.sonarPairs["x"].pos
                self.pos.xValid = self.sonarPairs["x"].validity

                self.pos.y = self.sonarPairs["y"].pos
                self.pos.yValid = self.sonarPairs["y"].validity
                
                self.pos.z = self.sonarPairs["z"].pos
                self.pos.zValid = self.sonarPairs["z"].validity
                


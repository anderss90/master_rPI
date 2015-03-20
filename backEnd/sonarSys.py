import math
#from imu import imu
from sonar import sonar
from position import position
maxPairDiff = 5

class sonarPair:
        def __init__(self,sonarA,sonarB,axis):
                self.a = sonarA
                self.b = sonarB
                self.axis = axis
                self.pos = 0
                self.validity = False
                self.invalidReason = -3
        
        def evaluate(self):
                aPos = -1*self.a.value-self.a.offset
                bPos = self.b.value-self.b.offset

                totalSd = self.a.sd + self.b.sd
                if totalSd == 0: totalSd = 1
                aCoeff = self.b.sd/totalSd
                bCoeff = self.a.sd/totalSd

                if self.a.validity or self.b.validity:
                        self.invalidReason = -3
                        self.validity = True
                        if self.a.validity and self.b.validity:
                                difference = math.fabs(aPos-bPos)
                                if difference  < maxPairDiff:
                                        self.pos = aCoeff*aPos+bCoeff*bPos

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
                        self.invalidReason = -2
                
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
                


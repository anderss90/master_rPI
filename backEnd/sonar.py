import position, math
avgAlpha = 0.5
sdAlpha = 0.1
lowpassAlpha = 0.7
maxDeviation =  3
maxValueCm = 450
minValueCm = 0
maxAttitudeDeg = 15
maxAngleVelocityDeg = 500
outlierLimit = 20
maxOutlierNumber = 1
enableAttitudeFilter = False
enableLowpass = True 

deviationAlpha = 0.3
deviationConstant = 0

front = "front"
back = "back"
right = "right"
left = "left"
down = "down"
up = "up"

class sonar:
        def __init__(self,direction):
                self.dir=direction
                self.value=0
                self.prevValue=0
                self.avgValue=0
                self.validity=False
                self.offset=0
                self.nOutliers = 0
                self.invalidReason = 0
                self.sd = 0
                self.lowpassed = 0

        def update(self,value):
                #dynamic outlierlimit
                outlierLimit = self.avgValue*0.4
                self.prevValue = self.value
                if value < 0:
                        self.value = -1
                        return
                if value > maxValueCm:
                        self.value = maxValueCm+1
                        return
                diff = math.fabs(value-self.value)
                if  diff > outlierLimit: #is outlier
                        if  self.nOutliers < maxOutlierNumber:
                                # ignore, keep last value
                                self.nOutliers += 1
                                #print "OUTLIER %i" %self.nOutliers 
                                return
                else: #is not outlier
                        self.nOutliers = 0
                self.value=value
                self.avgValue = self.avgValue + avgAlpha*(value-self.avgValue)
                self.lowpassed = self.lowpassed + lowpassAlpha*(value-self.lowpassed)
                #update standard deviation
                self.sd = self.sd + sdAlpha*(diff-self.sd)

        def resetOffset(self,pos):
                if enableLowpass:
                        currentValue = self.lowpassed
                else:
                        currentValue = self.value


                if self.dir == front:
                        self.offset = -1*(currentValue)-pos.x
                elif self.dir == back:
                        self.offset = currentValue-pos.x
                elif self.dir == right:
                        self.offset = -1*currentValue-pos.y
                elif self.dir == left:
                        self.offset = currentValue-pos.z
                elif self.dir == down:
                        self.offset = -1*currentValue-pos.z
                elif self.dir == up:
                        self.offset = currentValue-pos.z
                else:
                        print "ERROR: No valid sonar direction value"

        def evaluate(self,imu,pos):
                tempValidity = True
                self.invalidReason = -3
                diff = math.fabs(self.value-self.avgValue)
                #update maxDeviation based on avgValue
                maxDeviation = self.lowpassed*deviationAlpha + deviationConstant
                #check if withing accepted values
                if self.value < minValueCm or self.value > maxValueCm:
                        tempValidity = False
                        self.invalidReason = 0
                 
                #check if close enough to avg
                elif  diff > maxDeviation:
                        tempValidity = False
                        self.invalidReason = "%.2f"%diff
                
                #check if attitude is within maximum
                elif enableAttitudeFilter and (math.fabs(imu.roll) > maxAttitudeDeg or math.fabs(imu.pitch) > maxAttitudeDeg):
                        tempValidity = False
                        self.invalidReason = -1

                #check angle velocities
                elif enableAttitudeFilter and gmath.fabs(imu.gx)+math.fabs(imu.gy)+math.fabs(imu.gz) > 3*maxAngleVelocityDeg:
                        tempValidity = False
                        self.invalidReason = -2
                
                #detect transition from invalid to valid
                if self.validity == False:
                        if tempValidity == True:
                                self.resetOffset(pos)
                self.validity = tempValidity



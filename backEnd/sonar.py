import position, math
avgAlpha = 0.3
maxDeviation =  3
maxValueCm = 450
minValueCm = 0
maxAttitudeDeg = 10
maxAngleVelocityDeg = 10
maxPairDiff = 5
outlierLimit = 20
maxOutlierNumber = 5

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
                self.invalidReason = ""
        def update(self,value):
                self.prevValue = self.value
                if value < 0:
                        self.value = -1
                        return
                if math.fabs(value-self.value) > outlierLimit: #is outlier
                        if  self.nOutliers < maxOutlierNumber:
                                # ignore, keep last value
                                self.nOutliers += 1
                                #print "OUTLIER %i" %self.nOutliers 
                                return
                else: #is not outlier
                        self.nOutliers = 0
                self.value=value
                self.avgValue = self.avgValue + avgAlpha*(value-self.avgValue)

        def resetOffset(self,pos):
                if self.dir == front:
                        self.offset = -1*(self.value)-pos.x
                elif self.dir == back:
                        self.offset = self.value-pos.x
                elif self.dir == right:
                        self.offset = -1*self.value-pos.y
                elif self.dir == left:
                        self.offset = self.value-pos.z
                elif self.dir == down:
                        self.offset = -1*self.value-pos.z
                elif self.dir == up:
                        self.offset = self.value-pos.z
                else:
                        print "ERROR: No valid sonar direction value"

        def evaluate(self,imu,pos):
                tempValidity = True
                self.invalidReason = "none"
                #check if withing accepted values
                if self.value < minValueCm or self.value > maxValueCm:
                        tempValidity = False
                        self.invalidReason = "range"
                 
                #check if close enough to avg
                diff = math.fabs(self.value-self.avgValue)
                if  diff > maxDeviation:
                        tempValidity = False
                        self.invalidReason = "%.2f"%diff
                
                #check if attitude is within maximum
                if math.fabs(imu.roll) > maxAttitudeDeg or math.fabs(imu.pitch) > maxAttitudeDeg:
                        tempValidity = False
                        self.invalidReason = "attitude"

                #check angle velocities
                if math.fabs(imu.gx)+math.fabs(imu.gy)+math.fabs(imu.gz) > 3*maxAngleVelocityDeg:
                        tempValidity = False
                        self.invalidReason = "anglevel"
                
                #detect transition from invalid to valid
                if self.validity == False:
                        if tempValidity == True:
                                self.resetOffset(pos)
                self.validity = tempValidity



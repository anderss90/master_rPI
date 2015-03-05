from pid import Pid
from position import position
defSpeed = 50
defState = "landed"
midOutput = 1500 #1500 ms pwm output is analog stick center
maxOutput = 2000
minOutput = 1000

pidDefKp = 1
pidDefKi = 0
pidDefKd = 0
pidZKd = 1
pidMaxOut = 500
pidMinOut = -500
pidDt = 0.1
throttleIncrement = 10
class fControl:
        def __init__(self):
                self.state = defState
                self.pos = position(0,0,0,False,False,False)
                self.output = {"roll":midOutput,"pitch":midOutput,"yaw":midOutput,"throttle":minOutput}
                self.speeds = {"roll":defSpeed,"pitch":defSpeed,"yaw":defSpeed,"throttle":defSpeed}
                self.xPid = Pid(pidDefKp,pidDefKi,pidDefKd,0,pidMinOut,pidMaxOut)
                self.yPid = Pid(pidDefKp,pidDefKi,pidDefKd,0,pidMinOut,pidMaxOut)
                self.zPid = Pid(pidDefKp,pidDefKi,pidZKd,0,pidMinOut,pidMaxOut)
                self.setPoints = {"x":0,"y":0,"z":0}

        def tune(self,controller,P,I,D):
                if controller == "x":
                        self.xPid.tune(P,I,D)
                elif controller == "y":
                        self.yPid.tune(P,I,D)
                elif controller == "z":
                        self.zPid.tune(P,I,D)

        def setSpeed(self,direction,value):
                self.speeds[direction]=value

        def startHover(self,pos):
                self.setPoints["x"] = pos.x
                self.setPoints["y"] = pos.y
                self.setPoints["z"] = pos.z
                self.state = "hover"

        def update(self,state,pos):
                self.state = state
                self.pos = pos
                if self.state == "landed":
                        return 
                
                # Put setpoints over/under current to move in z direction
                if self.state == "moveUP":
                        self.setPoints["z"] = pos.z - self.speeds["throttle"]
                elif self.state == "moveDown":
                        self.setPoints["z"] = pos.z + self.speeds["throttle"]

                #Feed forward control if position info is invalid
                if pos.zValid == False:
                        if state == "moveUp":
                                self.output["throttle"]+=throttleIncrement
                        elif state == "moveDown":
                                self.output["throttle"]-=throttleIncrement

                #run altitude controller
                elif pos.zValid == True:
                        self.zPid.set(self.setPoints["z"])
                        self.zPid.step(pidDt,pos.z)
                        self.output["throttle"] -=  self.zPid.get() #negative because of NED

                # Run X/Y-controllers in hover mode
                if self.state == "hover":
                        if pos.xValid:
                                self.xPid.set(self.setPoints["x"])
                                self.xPid.step(pidDt,pos.x)
                                self.output["pitch"] = midOutput + self.xPid.get()
                        else:
                                self.output["pitch"] = midOutput

                        if pos.yValid: 
                                self.yPid.set(self.setPoints["y"])
                                self.yPid.step(pidDt,pos.y)
                                self.output["roll"] = midOutput + self.yPid.get()
                        else:
                                self.output["roll"] = midOutput
                        return
                
                # Moving states. Feed forward attitude setpoints to FC
                if self.state == "turnLeft":
                        self.output["yaw"] = midOutput + self.speeds["yaw"]
                elif self.state == "turnRight":
                        self.output["yaw"] = midOutput - self.speeds["yaw"]
                elif self.state == "moveRight":
                        self.output["roll"] = midOutput + self.speeds["roll"]
                elif self.state == "moveLeft":
                        self.output["roll"] = midOutput - self.speeds["roll"]
                elif self.state == "moveForward":
                        self.output["pitch"] = midOutput + self.speeds["pitch"]
                elif self.state == "moveBackward":
                        self.output["pitch"] = midOutput - self.speeds["pitch"]

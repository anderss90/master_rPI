import threading
from position import position
from imu import imu

lock = threading.Lock()
var1= "var1"
var2 = "var2"

pitch = "pitch value"
roll = "roll value"
yaw = "yaw value"

sonarFront = 0
sonarBack = 0
sonarRight = 0
sonarLeft = 0
sonarDown = 0
sonarUp = 0

posX = 0
posY = 0
posZ = 0

sonars = {}
imu = imu(0,0,0,0,0,0)
pos = position(0,0,0,False,False,False)


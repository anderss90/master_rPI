class imu:
        def __init__(self,roll,pitch,yaw,gx,gy,gz):
                self.roll = roll
                self.pitch = pitch
                self.yaw = yaw
                self.gx = gx
                self.gy = gy
                self.gz = gz
        def update(self,roll,pitch,yaw,gx,gy,gz):
                self.roll = roll
                self.pitch = pitch
                self.yaw = yaw
                self.gx = gx
                self.gy = gy
                self.gz = gz

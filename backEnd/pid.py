import time
class Pid (object):

    '''A discrete PID (Proportional-Integral-Derivative) controller.'''

    def __init__(self, P=1.0, I=1.0, D=1.0, point=0.0, below=-1.0, above=1.0):
        '''Sets up basic operational parameters for the controller.
        Three constants for the "tuning" of the controller can be given.
          * P (proportional gain) scales acceleration to new setpoints
          * I (integral gain) scales correction of error buildup
          * D (derivative gain) scales bounded rate of output change
        The initial desired ouput value or "point" can be given.
        The overall output range ("below" and "above") can be given.
        '''
        self.tune(P, I, D)
        self.range(below, above)
        self.output = below
        self.set(point)
        self.input = self.measure()

    def reset(self):
        self._integral = 0.0
        self._previous = 0.0

    def step(self, dt=1.0, input=None):
        '''Update the controller with a new input, to get new output.
        The time step "dt" can be given, or is assumed as an arbitrary 1.0.
        If a new "input" value a callable object, it is called for a value.
        If a new "input" value is not given here, measure() is called.
        '''
        if input is None:
            self.input = self.measure()
        elif callable(input):
            self.input = input()
        else:
            self.input = input
        err = self.setpoint - self.input
        self._integral += err * dt
        I = self._integral
        D = (err - self._previous) / dt
        output = self.Kp*err + self.Ki*I + self.Kd*D
        self._previous = err
        self.output = self.bound(output)

    def bound(self, output):
        '''Ensure the output falls within the current output range.
        May be overridden with a new method if overshoot is allowed.
        '''
        return max(min(output, self.maxout), self.minout)

    def range(self, below, above):
        '''Set the overall output range.
        Outputs are bounded to remain within this range with the bound()
        overridable method.
        '''
        if below > above:
            (above, below) = (below, above)
        self.minout = below
        self.maxout = above
        self.reset()

    def tune(self, P, I, D):
        '''Sets the three constant tuning parameters, P, I, and D.'''
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.reset()

    def set(self, point):
        '''Sets the desired output value to which the controller seeks.'''
        self.setpoint = point

    def get(self):
        '''Returns the current output value at any time.'''
        return self.output

    def measure(self):
        '''May be overridden to calculate a new input value.'''
        return 0.0

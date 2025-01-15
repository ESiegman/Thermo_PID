import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

class PID:
    """ This class implements a PID controller.
    """

    def __init__(self, Kp, Ki, Kd, Kaw, T_C, T, max, min, max_rate):
        self.Kp = Kp  # Proportional gain
        self.Ki = Ki  # Integral gain
        self.Kd = Kd  # Derivative gain
        self.Kaw = Kaw  # Anti-windup gain
        self.T_C = T_C  # Time constant for derivative filtering
        self.T = T  # Time step
        self.max = max  # Maximum command
        self.min = min  # Minimum command
        self.max_rate = max_rate  # Maximum rate of change of the command
        self.integral = 0  # Integral term
        self.err_prev = 0  # Previous error
        self.deriv_prev = 0  # Previous derivative
        self.command_sat_prev = 0  # Previous saturated command
        self.command_prev = 0  # Previous command
        self.command_sat = 0  # Current saturated command

    def Step(self, measurement, setpoint):
        """ Execute a step of the PID controller.

        Inputs:
            measurement: current measurement of the process variable
            setpoint: desired value of the process variable
        """

        # Calculate error
        err = setpoint - measurement

        # Update integral term with anti-windup
        self.integral += self.Ki * err * self.T + self.Kaw * (self.command_sat_prev - self.command_prev) * self.T

        # Calculate filtered derivative
        deriv_filt = (err - self.err_prev + self.T_C * self.deriv_prev) / (self.T + self.T_C)
        self.err_prev = err
        self.deriv_prev = deriv_filt

        # Calculate command using PID equation
        command = self.Kp * err + self.integral + self.Kd * deriv_filt

        # Store previous command
        self.command_prev = command

        # Saturate command
        if command > self.max:
            self.command_sat = self.max
        elif command < self.min:
            self.command_sat = self.min
        else:
            self.command_sat = command

        # Apply rate limiter
        if self.command_sat > self.command_sat_prev + self.max_rate * self.T:
            self.command_sat = self.command_sat_prev + self.max_rate * self.T
        elif self.command_sat < self.command_sat_prev - self.max_rate * self.T:
            self.command_sat = self.command_sat_prev - self.max_rate * self.T

        # Store previous saturated command
        self.command_sat_prev = self.command_sat
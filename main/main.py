import logging
import csv
import os
from time import time, sleep
import numpy as np
from scipy.optimize import minimize
from daq.sensors import Sensors
from power_supply.power_supply_device import PowerSupply
from pid_tuner import PID

# ----- Initialization -----
log = logging.getLogger("RealTimePIDTuner")
log.setLevel(logging.INFO)

sensors = Sensors()
power = PowerSupply()

# Channels for heating and cooling
cool_ch = "ch1"
heat_ch = "ch2"

# Target setpoints and time interval
target_temp = 50.0  # Desired temperature setpoint (°C)
tuning_interval = 0.5  # Time period for PID updates (seconds)
data_dir = r"C:\Users\12392\Desktop\Research\PID_Code\data"

# Data recording file setup
os.makedirs(data_dir, exist_ok=True)
file_path = os.path.join(data_dir, f"real_time_pid_tuning_{int(time())}.csv")

# ----- PID Controller Initialization -----
pid = PID(
    Kp=0.5, Ki=0.1, Kd=0.01, Kaw=0.01, T_C=1, T=0.1, max=10, min=0, max_rate=0.5
)

# Performance metric accumulator and history
error_history = []


# ----- Real-Time Optimization -----
def optimize_pid(coefficients_initial, temperature_history, setpoint):
    """
    Uses scipy's optimization framework to adjust PID coefficients dynamically.
    :param coefficients_initial: Initial PID coefficients [Kp, Ki, Kd].
    :param temperature_history: Recorded temperature values (real-time feedback).
    :param setpoint: Desired temperature setpoint.
    :return: Optimized coefficients [Kp, Ki, Kd].
    """

    def pid_cost(coefficients):
        """
        Cost function for PID optimization.
        Minimizes cumulative error (sum of squared errors).
        """
        Kp, Ki, Kd = coefficients
        pid.Kp = Kp
        pid.Ki = Ki
        pid.Kd = Kd

        total_error = 0.0
        for temp in temperature_history:
            error = setpoint - temp
            total_error += error ** 2  # Sum of squared errors over history

        return total_error

    # Run the optimizer
    result = minimize(
        pid_cost,
        coefficients_initial,
        bounds=[(0, 10), (0, 10), (0, 10)],  # Define bounds for Kp, Ki, Kd
        method="L-BFGS-B"
    )
    log.info(f"Optimization successful: {result.x}")
    return result.x  # Return updated PID coefficients


def real_time_pid_tuning(start_time):
    """
    Real-time PID tuning loop using live system feedback and optimization.
    Logs results to CSV and dynamically adjusts PID coefficients based on `pid_tuner.py` optimizer logic.
    """
    global error_history

    # Prepare CSV for logging
    with open(file_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ["Time (s)", "Temperature (°C)", "Setpoint (°C)", "PID Command", "Output Voltage (V)", "Kp", "Ki", "Kd",
             "Error"])
        log.info("Real-Time PID Tuning started.")

        # Initial PID coefficients
        coefficients = [pid.Kp, pid.Ki, pid.Kd]

        # Main tuning loop
        while True:
            try:
                elapsed_time = time() - start_time
                sensors.update()  # Update sensor data

                # Get current temperature feedback
                sensor_data = sensors.get_sensor_data("temperature")
                current_temp = sensor_data["temperature"]
                error = target_temp - current_temp

                # Compute PID output
                pid_command = pid.Step(current_temp, target_temp)

                # Map PID command to power supply voltage control
                output_voltage = pid_command
                power.set_output(heat_ch if output_voltage > 0 else cool_ch, abs(output_voltage), 2)

                # Log data
                writer.writerow(
                    [
                        elapsed_time,
                        current_temp,
                        target_temp,
                        pid_command,
                        output_voltage,
                        pid.Kp,
                        pid.Ki,
                        pid.Kd,
                        error,
                    ]
                )
                log.info(
                    f"Time: {elapsed_time:.2f}s, Temp: {current_temp:.2f}°C, Setpoint: {target_temp}°C, "
                    f"Command: {pid_command:.2f}, Voltage: {output_voltage:.2f}V, "
                    f"Kp={pid.Kp:.2f}, Ki={pid.Ki:.2f}, Kd={pid.Kd:.2f}, Error={error:.2f}"
                )

                # Append error and temperature to history
                error_history.append(error)
                if len(error_history) > 50:  # Limit history for optimization (e.g., 50 data points)
                    error_history.pop(0)

                # Optimize PID coefficients periodically
                if len(error_history) > 10 and elapsed_time % 5 < tuning_interval:  # Every 5 seconds
                    temperature_history = [target_temp - e for e in error_history]  # Reconstruct history
                    coefficients = optimize_pid(coefficients, temperature_history, target_temp)
                    pid.Kp, pid.Ki, pid.Kd = coefficients

                sleep(tuning_interval)  # Wait before next PID computation

            except KeyboardInterrupt:
                log.info("PID tuning interrupted by user.")
                break
            except Exception as e:
                log.error(f"Error during PID tuning: {e}")
                raise


if __name__ == "__main__":
    start_time = time()

    try:
        # Run the real-time PID tuning
        real_time_pid_tuning(start_time)

    except Exception as e:
        log.error(f"An error occurred: {e}")
        raise
    finally:
        # Clean up resources
        try:
            power.end()
            log.info("Power supply safely turned off.")
        except Exception as cleanup_err:
            log.error(f"Cleanup error: {cleanup_err}")

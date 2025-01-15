import logging
from time import time, sleep
import csv
import os  # Added for proper path handling
from daq.sensors import Sensors
from power_supply.power_supply_device import PowerSupply
from power_supply.ps_config import heat_volt, heat_curr, cool_volt, cool_curr
from utils.logging_util import LoggerUtility

# Initialize logger, sensors, and power supply
log = LoggerUtility(logger_name="OscillatingPowerTest", level=logging.DEBUG).logger
sensors = Sensors()
power = PowerSupply()

# Power supply channels
cool_ch = "ch1"
heat_ch = "ch2"

# Data storage configuration
data_dir = r'C:\Users\12392\Desktop\Research\PID_Code\data'
num_oscillations = 10
cycle_time = 5  # Duration of each cooling or heating cycle in seconds


def oscillate(time_start, writer):
    """
    Perform a complete oscillation cycle between cooling and heating.

    :param time_start: Start time of the full test.
    :param writer: CSV writer to log sensor data.
    """
    for i in range(num_oscillations):
        log.info(f"Starting oscillation {i + 1}/{num_oscillations}, Test Time Elapsed: {time() - time_start:.2f}s")
        cycle(time_start, writer, task=0)  # Cooling cycle
        cycle(time_start, writer, task=1)  # Heating cycle


def cycle(time_start, writer, task: int):
    """
    Perform a single cooling or heating cycle.

    :param time_start: Start time of the full test.
    :param writer: CSV writer to log sensor data.
    :param task: Task type (0 for cooling, 1 for heating).
    """
    if task == 0:
        log.info("Cooling cycle initiated.")
        power.set_output(cool_ch, cool_volt, cool_curr)
    elif task == 1:
        log.info("Heating cycle initiated.")
        power.set_output(heat_ch, heat_volt, heat_curr)
    else:
        raise ValueError(f"Invalid task type: {task}")

    cycle_start = time()

    # Collect data for the cycle duration
    while time() - cycle_start < cycle_time:
        try:
            sensors.update()  # Update the sensor values
            for ch, sensor in sensors.sensors.items():
                data = sensors.get_sensor_data(ch)
                writer.writerow([
                    time() - time_start,  # Elapsed time
                    data["output_voltage"],  # Power supply's output voltage
                    data["current"],  # Power supply's output current
                    data["sensor_voltage"],  # Sensor voltage
                    data["temperature"]  # Sensor temperature
                ])
        except Exception as e:
            log.error(f"Failed to update sensor data: {e}")
            raise

        sleep(0.05)  # Slight delay to limit sensor polling frequency


if __name__ == "__main__":
    start_time = time()
    try:
        # Ensure the data directory exists
        os.makedirs(data_dir, exist_ok=True)  # Safely create directory if it doesn't exist

        # Create a unique CSV file to log data
        file_name = f"oscillating_power_test_{int(start_time)}.csv"
        file_path = os.path.join(data_dir, file_name)

        with open(file_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            # Write the header
            writer.writerow(["Time (s)", "Output Voltage (V)", "Current (A)", "Sensor Voltage (V)", "Temperature (°C)"])
            log.info(f"Started oscillating power test: Logging data to {file_path}")

            # Perform oscillation cycles
            oscillate(start_time, writer)

        log.info("Oscillating power test completed successfully.")

    except Exception as e:
        log.error(f"An error occurred during the oscillating power test: {e}")
        raise
    finally:
        # Clean up power supply
        try:
            power.end()
            log.info("Power supply turned off and safely disconnected.")
        except Exception as cleanup_err:
            log.error(f"Error during power supply cleanup: {cleanup_err}")

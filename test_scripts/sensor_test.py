import time
from power_supply.power_supply_device import PowerSupply
from daq.sensors import Sensors
from power_supply.ps_config import sens_volt, sens_curr

def sensor_test(test_duration=10, interval=1):
    """
    Perform a sensor test by collecting readings over a specified duration.

    :param test_duration: Duration of the test in seconds (default 10 seconds).
    :param interval: Time interval between each reading in seconds (default 1 second).
    """
    # Initialize the logger for this script
    from utils.logging_util import LoggerUtility
    log = LoggerUtility(logger_name="SensorTest", level="DEBUG").logger

    # Initialize power supply (specific to channel 3)
    power_supply = PowerSupply()
    log.info("Power supply initialized")

    try:
        # Set the output for channel 3 (sensors)
        power_supply.set_output(ch="ch3", volt=sens_volt, curr=sens_curr)
        log.info("Power supply output on channel 3 set for sensor test")

        # Initialize sensors on specific channels
        sensor_channels = [0]  # Add more sensor channels if needed
        sensors = Sensors(channels=sensor_channels)
        log.info(f"Sensors initialized on channels: {sensor_channels}")

        start_time = time.time()
        log.info("Starting the sensor test...")

        # Perform the test over the specified duration
        while (time.time() - start_time) < test_duration:
            log.info("Reading data from sensors...")
            for ch, sensor in sensors.sensors.items():  # Access each sensor by channel
                sensor.update_values()  # Fetch new data from the sensor
                raw, volt, res, tempC, tempF = sensor.return_values()
                log.info(
                    f"Channel {ch}: Raw={raw}, Voltage={volt}V, Resistance={res}Ω, "
                    f"TempC={tempC}°C, TempF={tempF}°F"
                )
            time.sleep(interval)  # Wait for the specified interval before the next reading

        log.info("Sensor test complete.")

    except Exception as e:
        log.error(f"An error occurred during the sensor test: {e}")
    finally:
        # Cleanup resources
        log.info("Turning off power supply and cleaning up resources...")
        power_supply.end()


if __name__ == "__main__":
    # Run the sensor test with default settings
    sensor_test(test_duration=10, interval=1)

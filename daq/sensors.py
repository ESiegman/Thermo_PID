from dataclasses import dataclass, field
from mcculw import ul
from math import sqrt
import logging
from sens_config import A, B, res_c, res_0, vin, board_num, ul_range
from utils.logging_util import LoggerUtility

@dataclass
class Sensor:
    """
    Represents a sensor connected to a specific channel and provides methods to
    fetch and compute raw data, voltage, resistance, and temperature values
    from the sensor's readings.

    This class is designed for use with a specific board configuration and uses
    the log object for handling errors and informational messages. It provides
    the ability to read sensor data, process it into meaningful measurements, and
    return those values.

    :ivar channel: The sensor channel being used.
    :type channel: int
    :ivar raw: The raw sensor reading (default is 0.0).
    :type raw: float
    :ivar volt: The converted voltage from the raw sensor reading in volts
        (default is 0.0).
    :type volt: float
    :ivar res_t: The calculated resistance value in Ohms (default is 0.0).
    :type res_t: float
    :ivar tempC: The calculated temperature in degrees Celsius (default is 0.0).
    :type tempC: float
    :ivar tempF: The calculated temperature in degrees Fahrenheit (default is 0.0).
    :type tempF: float
    """
    channel: int
    raw: float = 0.0
    volt: float = 0.0
    res_t: float = 0.0
    tempC: float = 0.0
    tempF: float = 0.0

    def __init(self, channel: int, log):
        self.log = log
        self.channel = channel

    def update_values(self):
        try:
            self.raw = ul.a_in(board_num, self.channel, ul_range)
        except Exception as e:
            self.log.error(e, f"Failed to read sensor {self.channel}")
            exit()
        try:
            self.volt = ul.to_eng_units(board_num, self.raw, ul_range)
        except Exception as e:
            self.log.error(e, f"Failed to convert raw value to voltage from sensor {self.channel}")
            exit()
        try:
            self.res_t = (vin / self.volt - 1) * res_c
            self.tempC = (sqrt(A**2 + 4 * B * (self.res_t / res_0 - 1)) + (-1 * A)) / (2 * B)
            self.tempF = (self.tempC * 9 / 5) + 32
        except Exception as e:
            self.log.error(e, f"Failed to calculate temperature from sensor {self.channel}")
            exit()
        self.log.info(f"Recorded sensor data for channel {self.channel}: {self.raw}, {self.volt} V, {self.res_t} Ohms, {self.tempC} C, {self.tempF} F")

    def return_values(self):
        return self.raw, self.volt, self.res_t, self.tempC, self.tempF


class Sensors:
    """
    Represents a collection of sensors and provides functionality to create
    and manage them based on channel inputs. Each instance initializes a logger
    for debugging and logging purposes and creates Sensor instances for the
    provided channels.

    :ivar log: Logger instance used for logging messages.
    :type log: logging.Logger
    :ivar sensors: A dictionary mapping channel numbers to their respective
        Sensor instances.
    :type sensors: dict[int, Sensor]
    """
    def __init__(self, channels: list[int] | None = None):
        self.log = LoggerUtility(logger_name="Sensors", level=logging.DEBUG).logger
        if channels is None:
            channels = []
        self.sensors = {channel: Sensor(channel) for channel in channels}
        self.log.info(f"Sensors initialized with channels: {channels}")

    def update(self):
        for sensor in self.sensors.values():
            sensor.update_values()

    def get_sensor_data(self, channel: int):
        """
        Retrieves the raw, voltage, resistance, and temperature data for the specified sensor.

        :param channel: The sensor channel number.
        :type channel: int
        :return: A tuple containing raw, voltage, resistance, tempC, tempF values or None if the channel is invalid.
        :rtype: tuple or None
        """
        sensor = self.sensors.get(channel)
        if sensor:
            return sensor.return_values()
        else:
            self.log.error(f"Sensor data requested for invalid channel: {channel}")
            exit()

    
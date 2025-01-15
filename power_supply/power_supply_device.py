import pyvisa
import logging
from utils.logging_util import LoggerUtility
from ps_config import ps_address, sens_volt, sens_curr, PowerSupplyChannel as Channel

class PowerSupply:

    def __init__(self):
        """
        Initializes the Power Supply interface and sets up its channels and logger.

        The `__init__` method configures the logging utility and initializes the
        communication with the power supply hardware using a VISA resource manager.
        It also creates three power supply channels and sets their initial statuses
        to disabled.

        :Attributes:
            log (logging.Logger): Logger instance configured for logging actions
                related to the power supply.
            ps: Resource instance representing the connection with the power supply.
            ch1 (Channel): Configuration and control for Channel 1 of
                the power supply.
            ch2 (Channel): Configuration and control for Channel 2 of
                the power supply.
            ch3 (Channel): Configuration and control for Channel 3 of
                the power supply.
            ch_status (List[int]): List representing the status of the channels
                (1 for enabled, 0 for disabled).
        """
        self.log = LoggerUtility(logger_name="PowerSupply", level=logging.DEBUG).logger
        rm = pyvisa.ResourceManager()
        self.ps = rm.open_resource(ps_address)
        self.ch1 = Channel(*Channel.CH1)
        self.ch2 = Channel(*Channel.CH2)
        self.ch3 = Channel(*Channel.CH3)
        self.ch_status = [0,0,0]
        self.log.info("Power Supply Initialized")

    def turn_off_all(self):
        try:
            self.ps.write(self.ch1.off)
            self.ps.write(self.ch2.off)
            self.ps.write(self.ch3.off)
            self.log.info("Turned off all channels")
        except Exception as e:
            self.log.error(e, "An error occurred while turning off all channels")
            exit()

    def set_output(self, ch=str, volt=float, curr=float):
        """
        Sets the output of the specified channel to the given voltage and current.

        This method configures a particular channel of a power supply based on the
        provided parameters. It performs necessary checks to shut down conflicting
        channels if they are on and applies the new settings to the selected channel.
        Proper channel handling is conducted to maintain device integrity. Logs any
        encountered errors or invalid inputs.

        :param ch: The channel to configure. Supported values are "ch1", "ch2", and "ch3".
        :param volt: The voltage level to set for the specified channel.
        :param curr: The current level to set for the specified channel.
        :return: None
        """
        try:
            if ch == "ch1":
                if self.ch_status[1] == 1:
                    self.ps.write(self.ch2.off)
                    self.ch_status[1] = 0
                self.ps.write(f':APPL CH1,{volt},{curr}')
                if self.ch_status[0] == 0:
                    self.ps.write(self.ch1.on)
                    self.ch_status[0] = 1
            elif ch == "ch2":
                if self.ch_status[2] == 1:
                    self.ps.write(self.ch3.off)
                    self.ch_status[2] = 0
                self.ps.write(f':APPL CH2,{volt},{curr}')
                if self.ch_status[1] == 0:
                    self.ps.write(self.ch2.on)
                    self.ch_status[1] = 1
            elif ch == "ch3":
                self.ps.write(f':APPL CH3,{sens_volt},{sens_curr}')
            else:
                self.log.error(f"Invalid channel name: {ch}")
        except Exception as e:
            self.log.error(e, f"An error occurred while setting output for {ch}")
            exit()

    def end(self):
        """
        Closes the power supply connection and performs any necessary cleanup.

        This method ensures that all connected components are properly turned off
        and the connection to the power supply is securely closed. It logs the
        status of the operation, and in the case of an exception, it logs the error
        appropriately for debugging purposes.

        :return: None
        """
        try:
            self.turn_off_all()
            self.ps.close()
            self.log.info("Power supply connection closed.")
        except Exception as e:
            self.log.error(e, f"Failed to properly close the power supply connection: {e}")
            exit()
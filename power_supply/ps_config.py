ps_address = 'USB0::0x1AB1::0xA4A8::DP2A243700427::INSTR'
sens_volt = 3.3
sens_curr = .02
heat_volt = 0
heat_curr = 0
cool_volt = 0
cool_curr = 0

class PowerSupplyChannel:
    """
    Represents a channel of a power supply.

    This class is used to manage a specific channel of a power supply device.
    It provides the essential commands to turn the channel on or off, query its
    state, and check its status.

    :ivar label: The label or identifier of the channel.
    :type label: str
    :ivar off_command: The command to turn the channel off.
    :type off_command: str
    :ivar on_command: The command to turn the channel on.
    :type on_command: str
    :ivar status_command: The command to check the channel's status.
    :type status_command: str
    :ivar query_command: The command to query the channel's state.
    :type query_command: str
    """
    CH1 = ("CH1", ":OUTP CH1,OFF", ":OUTP CH1,ON", ":APPL? CH1", ":OUTP? CH1")
    CH2 = ("CH2", ":OUTP CH2,OFF", ":OUTP CH2,ON", ":APPL? CH2", ":OUTP? CH2")
    CH3 = ("CH3", ":OUTP CH3,OFF", ":OUTP CH3,ON", ":APPL? CH3", ":OUTP? CH3")

    def __init__(self, label: str, off: str, on: str, status: str, query: str):
        self.label = label
        self.off_command = off
        self.on_command = on
        self.status_command = status
        self.query_command = query

    @property
    def off(self):
        return self.off_command

    @property
    def on(self):
        return self.on_command

    @property
    def status(self):
        return self.status_command

    @property
    def query(self):
        return self.query_command

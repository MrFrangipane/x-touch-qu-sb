from abc import ABC, abstractmethod
from typing import Callable


from xtouchqusb.entities.channel_state import ChannelState
from xtouchqusb.contracts.base_configuration import BaseConfiguration


class AbstractDevice(ABC):

    def __init__(self, configuration: BaseConfiguration, channel_state_update_callback: Callable):
        self._configuration = configuration
        self._callback = channel_state_update_callback

    @abstractmethod
    def connect(self):
        """Connects to device"""
        pass

    @abstractmethod
    def close(self):
        """Closes connection to device"""
        pass

    @abstractmethod
    def poll(self):
        """Called in a loop to handle messages and callbacks"""
        pass

    @abstractmethod
    def set_channel_state(self, channel_state: ChannelState):
        pass

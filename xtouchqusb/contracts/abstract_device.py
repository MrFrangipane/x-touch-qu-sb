from abc import ABC, abstractmethod
from typing import Callable


from xtouchqusb.entities.channel_state import ChannelState


class AbstractDevice(ABC):

    def __init__(self, configuration: dict, channel_state_update_callback: Callable):
        self._configuration = configuration
        self._enabled = configuration['enabled']
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

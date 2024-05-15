import logging
from typing import Callable
from threading import Thread

from pythonosc.osc_server import ThreadingOSCUDPServer, Dispatcher
from pythonosc.udp_client import SimpleUDPClient

from xtouchqusb.contracts.abstract_device import AbstractDevice
from xtouchqusb.entities.channel_parameters_enum import ChannelParametersEnum
from xtouchqusb.entities.channel_state import ChannelState


_logger = logging.getLogger(__name__)


class OscClient(AbstractDevice):

    def __init__(self, configuration: dict, channel_state_callback: Callable):
        super().__init__(configuration, channel_state_callback)
        self._client: SimpleUDPClient = None
        self._server: ThreadingOSCUDPServer = None

    def connect(self):
        self._client = SimpleUDPClient(
            address=self._configuration['server-host'],
            port=self._configuration['server-port']
        )

    def close(self):
        pass

    def poll(self):
        pass

    def set_channel_state(self, channel_state: ChannelState):
        if self._client is None:
            return

        if channel_state.parameter == ChannelParametersEnum.FADER:
            channel_number = channel_state.channel - 32
            self._client.send_message(f'/fader{channel_number + 1}', float(channel_state.value) / 127.0)

import copy
import logging
from typing import Callable
from threading import Thread
from queue import Queue

from pythonosc.osc_server import ThreadingOSCUDPServer, Dispatcher
from pythonosc.udp_client import SimpleUDPClient

from xtouchqusb.contracts.abstract_device import AbstractDevice
from xtouchqusb.entities.channel_parameters_enum import ChannelParametersEnum
from xtouchqusb.entities.channel_state import ChannelState


_logger = logging.getLogger(__name__)


class Osc(AbstractDevice):

    def __init__(self, configuration: dict, channel_state_callback: Callable):
        super().__init__(configuration, channel_state_callback)
        self._server: ThreadingOSCUDPServer = None
        self._client: SimpleUDPClient = None
        self._server_thread: Thread = None
        self._queue= Queue()
        self._u = None

    def connect(self):
        dispatcher = Dispatcher()
        dispatcher.set_default_handler(self._parse_osc, needs_reply_address=True)
        address = self._configuration['server-host'], self._configuration['server-port']
        self._server = ThreadingOSCUDPServer(
            server_address=address,
            dispatcher=dispatcher
        )

        self._server_thread = Thread(target=self._server.serve_forever, daemon=True)
        self._server_thread.start()

        address = self._configuration['client-host'], self._configuration['client-port']
        self._client = SimpleUDPClient(*address)

    def close(self):
        pass

    def poll(self):
        while not self._queue.empty():
            cs = self._queue.get()
            print('cb', cs)
            self._callback(cs)

    def set_channel_state(self, channel_state: ChannelState):
        print('ss', channel_state)
        if channel_state.parameter == ChannelParametersEnum.FADER:
            channel_number = channel_state.channel - 32
            self._client.send_message(f'/fader{channel_number + 1}', float(channel_state.value) / 127.0)

    def _parse_osc(self, reply_address, osc_address, osc_value):
        channel_number = int(osc_address[-1]) - 1
        cs = ChannelState(
            channel=32 + channel_number,
            parameter=ChannelParametersEnum.FADER,
            value=int(osc_value * 127)
        )
        self._queue.put(cs)

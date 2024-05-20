import os.path
from queue import Queue, Empty
from threading import Thread
from typing import Callable

import yaml

from xtouchqusb.components.qu_sb.service import QuSb, QuSbConfiguration
from xtouchqusb.components.osc import Osc
from xtouchqusb.components.x_touch import XTouch

from xtouchqusb.contracts.abstract_device import AbstractDevice

from xtouchqusb.entities.channel_state import ChannelState


class Application:
    def __init__(self):
        self._component_a: AbstractDevice = None
        self._component_b: AbstractDevice = None

        self._queue_a_to_b: Queue[ChannelState] = None
        self._queue_b_to_a: Queue[ChannelState] = None

        self._queue_thread_a: Thread = Thread(target=self.queue_loop_a, daemon=True)
        self._queue_thread_b: Thread = Thread(target=self.queue_loop_b, daemon=True)

        self._is_running: bool = False

    def load_configuration(self, filepath: str):
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Given configuration filepath does not exists '{filepath}'")

        with open(filepath, 'r') as yaml_file:
            configuration = yaml.safe_load(yaml_file)

        self._component_a = self._configure_component(configuration['component_a'], self._put_to_b)
        self._component_b = self._configure_component(configuration['component_b'], self._put_to_a)

    @staticmethod
    def _configure_component(configuration: dict, callback: Callable) -> AbstractDevice:
        if configuration['type'] == 'osc':
            return Osc(configuration, callback)

        elif configuration['type'] == 'x-touch':
            return XTouch(configuration, callback)

        elif configuration['type'] == 'qu-sb':
            qu_sb_configuration = QuSbConfiguration(
                tcp_host=configuration['host'],
                tcp_port=configuration['port'],
                port_name_pattern=configuration['midi_port_name_pattern']
            )
            return QuSb(qu_sb_configuration, callback)

    def _put_to_a(self, channel_state):
        self._queue_b_to_a.put(channel_state, block=False)

    def _put_to_b(self, channel_state):
        self._queue_a_to_b.put(channel_state, block=False)

    def exec(self):
        self._queue_a_to_b = Queue()
        self._queue_b_to_a = Queue()

        self._is_running = True
        self._queue_thread_a.start()
        self._queue_thread_b.start()

        try:
            self._component_a.connect()
            self._component_b.connect()

            while True:
                self._component_a.poll()
                self._component_b.poll()

        except KeyboardInterrupt:
            self._is_running = False
            self._component_a.close()
            self._component_b.close()

    def queue_loop_a(self):
        while self._is_running:
            self._component_a.set_channel_state(self._queue_b_to_a.get())

    def queue_loop_b(self):
        while self._is_running:
            self._component_b.set_channel_state(self._queue_a_to_b.get())

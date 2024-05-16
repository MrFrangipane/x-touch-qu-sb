import os.path
from threading import Thread
from typing import Callable

import yaml

from xtouchqusb.components.qu_sb import QuSb
from xtouchqusb.components.osc import Osc
from xtouchqusb.components.x_touch import XTouch
from xtouchqusb.contracts.abstract_device import AbstractDevice


class Application:
    def __init__(self):
        self._component_a: AbstractDevice = None
        self._component_b: AbstractDevice = None
        self._is_running: bool = False

    def load_configuration(self, filepath: str):
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Given configuration filepath does not exists '{filepath}'")

        with open(filepath, 'r') as yaml_file:
            configuration = yaml.safe_load(yaml_file)

        self._component_a = self._configure_component(configuration['component_a'], self._callback_b)
        self._component_b = self._configure_component(configuration['component_b'], self._callback_a)

    @staticmethod
    def _configure_component(configuration: dict, callback: Callable) -> AbstractDevice:
        return {
            'osc': Osc,
            'x-touch': XTouch,
            'qu-sb': QuSb
        }[configuration['type']](configuration, callback)

    def _callback_a(self, channel_state):
        self._component_a.set_channel_state(channel_state)

    def _callback_b(self, channel_state):
        self._component_b.set_channel_state(channel_state)

    def exec_a(self):
        self._component_a.connect()
        while self._is_running:
            self._component_a.poll()
        self._component_b.close()

    def exec_b(self):
        self._component_b.connect()
        while self._is_running:
            self._component_b.poll()
        self._component_b.close()

    def exec(self):
        try:
            self._is_running = True

            a_thread = Thread(target=self.exec_a, daemon=True)
            a_thread.start()

            b_thread = Thread(target=self.exec_b, daemon=True)
            b_thread.start()

            while True:
                pass

        except KeyboardInterrupt:
            self._is_running = False

import os.path
from typing import Callable

import yaml

from xtouchqusb.components.qu_sb import QuSb
from xtouchqusb.components.osc_client import OscClient
from xtouchqusb.components.osc_server import OscServer
from xtouchqusb.components.x_touch import XTouch
from xtouchqusb.contracts.abstract_device import AbstractDevice


class Application:
    def __init__(self):
        self._component_a: AbstractDevice = None
        self._component_b: AbstractDevice = None

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
            'osc-client': OscClient,
            'osc_server': OscServer,
            'x-touch': XTouch,
            'qu-sb': QuSb
        }[configuration['type']](configuration, callback)

    def _callback_a(self, channel_state):
        self._component_a.set_channel_state(channel_state)

    def _callback_b(self, channel_state):
        self._component_b.set_channel_state(channel_state)

    def exec(self):
        try:
            self._component_a.connect()
            self._component_b.connect()

            while True:
                self._component_a.poll()
                self._component_b.poll()

        except KeyboardInterrupt:
            self._component_a.close()
            self._component_b.close()

import os.path
from typing import Callable

import yaml

from xtouchqusb.components.qu_sb.service import QuSb, QuSbConfiguration
from xtouchqusb.components.osc import Osc
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

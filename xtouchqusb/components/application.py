import json
import os.path

from xtouchqusb.components.qu_sb import QuSb
from xtouchqusb.components.x_touch import XTouch


class Application:
    FRAMERATE = 60

    def __init__(self, configuration_filepath: str):
        if not os.path.isfile(configuration_filepath):
            raise FileNotFoundError(f'Configuration file not found {configuration_filepath}')

        with open(configuration_filepath, 'r') as configuration_file:
            configuration = json.load(configuration_file)

        self.x_touch = XTouch(
            in_port_name=configuration['x-touch']['midi_in'],
            out_port_name=configuration['x-touch']['midi_out'],
            channel_state_update_callback=self.callback_qu_sb
        )
        self.qu_sb = QuSb(
            host=configuration['qu-sb']['host'],
            tcp_only=configuration['qu-sb']['tcp_only'],
            midi_in=configuration['qu-sb']['midi_in'],
            midi_out=configuration['qu-sb']['midi_out'],
            channel_state_callback=self.callback_x_touch
        )

        self._last_x_touch_message_timestamp = 0
        self._last_qu_sb_message_timestamp = 0

    def callback_x_touch(self, channel_state):
        self.x_touch.set_channel_state(channel_state)

    def callback_qu_sb(self, channel_state):
        self.qu_sb.set_channel_state(channel_state)

    def main(self):
        try:
            self.x_touch.connect()

            self.qu_sb.connect()
            self.qu_sb.request_state()

            while True:
                self.x_touch.poll()
                self.qu_sb.poll()

        except KeyboardInterrupt:
            self.qu_sb.close()
            self.x_touch.close()

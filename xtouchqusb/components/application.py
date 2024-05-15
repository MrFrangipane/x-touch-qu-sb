from xtouchqusb.components.qu_sb import QuSb
from xtouchqusb.components.osc import OSC
from xtouchqusb.components.x_touch import XTouch


class Application:
    FRAMERATE = 60

    def __init__(self, configuration: dict):
        self.osc = OSC(
            configuration=configuration['osc'],
            channel_state_callback=self.callback_qu_sb
        )
        self.qu_sb = QuSb(
            configuration=configuration['qu-sb'],
            channel_state_callback=self.callback_osc
        )

    def callback_osc(self, channel_state):
        self.osc.set_channel_state(channel_state)

    def callback_qu_sb(self, channel_state):
        self.qu_sb.set_channel_state(channel_state)

    def callback_x_touch(self, channel_state):
        self.x_touch.set_channel_state(channel_state)


    def main(self):
        try:
            self.osc.connect()

            self.qu_sb.connect()
            self.qu_sb.request_state()

            while True:
                self.osc.poll()
                self.qu_sb.poll()

        except KeyboardInterrupt:
            self.qu_sb.close()
            self.osc.close()

import logging
from typing import Callable

from mido.messages import Message
from mido.ports import BaseInput, BaseOutput

from xtouchqusb.contracts.abstract_device import AbstractDevice
from xtouchqusb.entities.channel_parameters_enum import ChannelParametersEnum
from xtouchqusb.entities.channel_state import ChannelState
from xtouchqusb.python_extensions.mido_extensions import open_input_from_pattern, open_output_from_pattern


_logger = logging.getLogger(__name__)


class XTouch(AbstractDevice):

    CHANNEL_OFFSET = 32

    def __init__(self, configuration: dict, channel_state_update_callback: Callable):
        super().__init__(configuration, channel_state_update_callback)

        self._in: BaseInput = None
        self._out: BaseOutput = None

        self._previous_state: ChannelState = ChannelState(-1, ChannelParametersEnum.UNKNOWN, -1)

    def connect(self):
        pattern = self._configuration['midi_port_name_pattern']
        self._in = open_input_from_pattern(pattern)
        self._out = open_output_from_pattern(pattern)

    def close(self):
        self._in.close()
        self._out.close()

    def poll(self):
        message = self._in.receive(block=False)
        if message is not None:
            channel_state = None
            if message.type == 'pitchwheel':
                value = int(float(message.pitch + 8192) / 16380.0 * 127)
                channel_state = ChannelState(
                    channel=message.channel + self.CHANNEL_OFFSET,  # todo: paginate
                    parameter=ChannelParametersEnum.FADER,
                    value=value
                )

            elif message.type == 'note_on' and message.note == 24:
                channel_state = ChannelState(
                    channel=message.channel + self.CHANNEL_OFFSET,  # todo: paginate
                    parameter=ChannelParametersEnum.COMPRESSOR_ON,
                    value=int(message.velocity / 127)
                )

            else:
                _logger.info(message)

            if channel_state is not None:
                if channel_state != self._previous_state:
                    self._previous_state = channel_state
                    self._callback(channel_state)

            self._out.send(message)

    def set_channel_state(self, channel_state: ChannelState):
        """Usually called as a callback by the other component"""
        channel = channel_state.channel - self.CHANNEL_OFFSET  # todo: paginate
        if channel > 15 or channel < 0:
            return

        # _logger.info(channel_state)

        if channel_state.parameter == ChannelParametersEnum.FADER:
            value = int((channel_state.value * 128) - 8192)

            self._out.send(Message(
                type='pitchwheel',
                channel=channel,
                pitch=value
            ))

        elif channel_state.parameter == ChannelParametersEnum.COMPRESSOR_ON:
            value = int(channel_state.value * 127)
            self._out.send(Message(
                type='note_on',
                channel=channel,
                note=24,
                velocity=value
            ))

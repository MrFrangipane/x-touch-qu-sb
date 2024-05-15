import logging
from typing import Callable

import mido
from mido.messages import Message
from mido.ports import BaseInput, BaseOutput

from xtouchqusb.contracts.abstract_device import AbstractDevice
from xtouchqusb.entities.channel_parameters_enum import ChannelParametersEnum
from xtouchqusb.entities.channel_state import ChannelState


_logger = logging.getLogger(__name__)


class XTouch(AbstractDevice):

    CHANNEL_OFFSET = 32

    def __init__(self, in_port_name: str, out_port_name: str, channel_state_update_callback: Callable):
        super().__init__(channel_state_update_callback)
        self._in_port_name = in_port_name
        self._out_port_name = out_port_name

        self._in_port: BaseInput = None
        self._out_port: BaseOutput = None

    def connect(self):
        self._in_port = mido.open_input(self._in_port_name)
        self._out_port = mido.open_output(self._out_port_name)

    def close(self):
        self._in_port.close()
        self._out_port.close()

    def poll(self):
        message = self._in_port.receive(block=False)
        if message is not None:
            _logger.info(message)
            if message.type == 'pitchwheel':
                value = int(float(message.pitch + 8192) / 16380.0 * 127)
                self._callback(ChannelState(
                    channel=message.channel + self.CHANNEL_OFFSET,  # todo: paginate
                    parameter=ChannelParametersEnum.FADER,
                    value=value
                ))

            elif message.type == 'note_on' and message.note == 24:
                channel_state = ChannelState(
                    channel=message.channel + self.CHANNEL_OFFSET,  # todo: paginate
                    parameter=ChannelParametersEnum.COMPRESSOR_ON,
                    value=int(message.velocity / 127)
                )
                self._callback(channel_state)

            else:
                print('Xt >', message)

            self._out_port.send(message)

    def set_channel_state(self, channel_state: ChannelState):
        channel = channel_state.channel - self.CHANNEL_OFFSET  # todo: paginate
        if channel > 15 or channel < 0:
            return

        _logger.info(channel_state)

        if channel_state.parameter == ChannelParametersEnum.FADER:
            value = int((channel_state.value * 128) - 8192)

            self._out_port.send(Message(
                type='pitchwheel',
                channel=channel,
                pitch=value
            ))

        elif channel_state.parameter == ChannelParametersEnum.COMPRESSOR_ON:
            value = int(channel_state.value * 127)
            self._out_port.send(Message(
                type='note_on',
                channel=channel,
                note=24,
                velocity=value
            ))

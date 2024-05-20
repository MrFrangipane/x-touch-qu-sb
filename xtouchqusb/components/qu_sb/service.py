import logging
from typing import Callable

from mido.messages import Message

from xtouchqusb.components.qu_sb.configuration import QuSbConfiguration
from xtouchqusb.components.qu_sb.constants import QuSbConstants
from xtouchqusb.components.qu_sb.midi import QuSbMidi

from xtouchqusb.contracts.abstract_device import AbstractDevice

from xtouchqusb.entities.channel_parameters_enum import ChannelParametersEnum
from xtouchqusb.entities.channel_state import ChannelState


_logger = logging.getLogger(__name__)


class QuSb(AbstractDevice):
    def __init__(self, configuration: QuSbConfiguration, channel_state_callback: Callable):
        super().__init__(configuration, channel_state_callback)

        self._midi = QuSbMidi(configuration)

        self._message_channel: int = None
        self._message_parameter: ChannelParametersEnum = None
        self._message_value: int = None

        self._last_state: ChannelState = ChannelState(-1, ChannelParametersEnum.UNKNOWN, -1)

    def connect(self):
        for state_message in self._midi.request_state():
            self._process_message(state_message)
        
        self._midi.connect()

    def close(self):
        self._midi.close()

    def poll(self):
        self._process_message(self._midi.receive(block=False))

    def set_channel_state(self, channel_state: ChannelState):
        """Usually called as a callback by the other component"""
        if channel_state.parameter == ChannelParametersEnum.UNKNOWN:
            return

        if channel_state != self._last_state:
            self._last_state = channel_state
        else:
            return

        self._midi.send(Message(
            type='control_change',
            control=QuSbConstants.NRPN_CHANNEL,
            value=channel_state.channel
        ))
        self._midi.send(Message(
            type='control_change',
            control=QuSbConstants.NRPN_PARAMETER,
            value=QuSbConstants.CHANNEL_ENUM_PARAMETER_CODE[channel_state.parameter],
        ))
        self._midi.send(Message(
            type='control_change',
            control=QuSbConstants.NRPN_VALUE,
            value=channel_state.value,
        ))
        self._midi.send(Message(
            type='control_change',
            control=QuSbConstants.NRPN_DATA_ENTRY_FINE,
            value=0,  # fixme: not always 0 ?
        ))

    def _process_message(self, message: Message):
        if message is None or message.type == 'active_sensing':
            return

        if message.type == 'sysex':
            # TODO: do something ?
            pass

        elif message.type == 'control_change':
            if message.control == QuSbConstants.NRPN_CHANNEL:
                self._message_channel = message.value

            elif message.control == QuSbConstants.NRPN_PARAMETER:
                self._message_parameter = QuSbConstants.CHANNEL_PARAMETER_CODE_TO_ENUM.get(
                    message.value,
                    ChannelParametersEnum.UNKNOWN
                )

            elif message.control == QuSbConstants.NRPN_VALUE:
                self._message_value = message.value

            elif message.control == QuSbConstants.NRPN_DATA_ENTRY_FINE:
                channel_state = ChannelState(
                    self._message_channel,
                    self._message_parameter,
                    self._message_value
                )
                self._callback(channel_state)

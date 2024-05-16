import logging
import time
from typing import Callable

from mido.messages import Message
from mido.sockets import connect, SocketPort
from mido.ports import BaseInput, BaseOutput

from xtouchqusb.contracts.abstract_device import AbstractDevice
from xtouchqusb.entities.channel_parameters_enum import ChannelParametersEnum
from xtouchqusb.entities.channel_state import ChannelState
from xtouchqusb.python_extensions.mido_extensions import open_input_from_pattern, open_output_from_pattern


_logger = logging.getLogger(__name__)


class QuSb(AbstractDevice):
    TCP_PORT = 51325

    POLL_SLEEP = 0.01

    SYSEX_HEADER = b'\x00\x00\x1A\x50\x11\x01\x00'
    SYSEX_ALL_CALL = b'\x7F'
    SYSEX_GET_SYSTEM_STATE = b'\x10'
    SYSEX_SYSTEM_STATE_END = b'\x14'

    # todo: hex notation ?
    NRPN_CHANNEL = 99
    NRPN_PARAMETER = 98
    NRPN_VALUE = 6
    NRPN_DATA_ENTRY_FINE = 38

    CHANNEL_PARAMETER_CODE_TO_ENUM = {
        23: ChannelParametersEnum.FADER,
        25: ChannelParametersEnum.INPUT_GAIN,
        104: ChannelParametersEnum.COMPRESSOR_ON
    }
    CHANNEL_ENUM_PARAMETER_CODE = {
        ChannelParametersEnum.FADER: 23,
        ChannelParametersEnum.INPUT_GAIN: 25,
        ChannelParametersEnum.COMPRESSOR_ON: 104
    }

    def __init__(self, configuration: dict, channel_state_callback: Callable):
        super().__init__(configuration, channel_state_callback)

        self._in: BaseInput = None
        self._out: BaseOutput = None

        self._message_channel: int = None
        self._message_parameter: ChannelParametersEnum = None
        self._message_value: int = None

    def connect(self):
        self.request_state()

        pattern = self._configuration['midi_port_name_pattern']
        self._in = open_input_from_pattern(pattern)
        self._out = open_output_from_pattern(pattern)

    def close(self):
        self._in.close()
        self._out.close()

    def poll(self):
        message = self._in.receive(block=False)
        self._process_message(message)

        time.sleep(self.POLL_SLEEP)

    def _process_message(self, message: Message):
        if message is not None and message.type != 'active_sensing':
            if message.type == 'sysex':
                # TODO: do something ?
                pass

            elif message.type == 'control_change':
                if message.control == self.NRPN_CHANNEL:
                    self._message_channel = message.value

                elif message.control == self.NRPN_PARAMETER:
                    self._message_parameter = self.CHANNEL_PARAMETER_CODE_TO_ENUM.get(
                        message.value,
                        ChannelParametersEnum.UNKNOWN
                    )

                elif message.control == self.NRPN_VALUE:
                    self._message_value = message.value

                elif message.control == self.NRPN_DATA_ENTRY_FINE:
                    channel_state = ChannelState(
                        self._message_channel,
                        self._message_parameter,
                        self._message_value
                    )
                    self._callback(channel_state)

    def set_channel_state(self, channel_state: ChannelState):
        if channel_state.parameter == ChannelParametersEnum.UNKNOWN:
            return

        self._out.send(Message(
            type='control_change',
            control=self.NRPN_CHANNEL,
            value=channel_state.channel
        ))
        self._out.send(Message(
            type='control_change',
            control=self.NRPN_PARAMETER,
            value=self.CHANNEL_ENUM_PARAMETER_CODE[channel_state.parameter],
        ))
        self._out.send(Message(
            type='control_change',
            control=self.NRPN_VALUE,
            value=channel_state.value,
        ))
        self._out.send(Message(
            type='control_change',
            control=self.NRPN_DATA_ENTRY_FINE,
            value=0,  # fixme: not always 0 ?
        ))

    def request_state(self):
        message = Message(
            type='sysex',
            data=self.SYSEX_HEADER + self.SYSEX_ALL_CALL + self.SYSEX_GET_SYSTEM_STATE + b'\x00'  # we are not an iPad
        )
        with connect(host=self._configuration['host'], portno=self.TCP_PORT) as tcp_socket:
            tcp_socket.send(message)
            for message in tcp_socket:
                if bytearray(message.bytes()[1:-1]) == self.SYSEX_HEADER + b'\x00' + self.SYSEX_SYSTEM_STATE_END:
                    tcp_socket.close()
                    break
                self._process_message(message)

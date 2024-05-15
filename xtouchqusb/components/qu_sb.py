import logging
import time
from typing import Callable

import mido
from mido.messages import Message
from mido.sockets import connect, SocketPort
from mido.ports import BaseInput, BaseOutput

from xtouchqusb.contracts.abstract_device import AbstractDevice
from xtouchqusb.entities.channel_parameters_enum import ChannelParametersEnum
from xtouchqusb.entities.channel_state import ChannelState


_logger = logging.getLogger(__name__)


class QuSb(AbstractDevice):
    TCP_PORT = 51325

    SYSEX_HEADER = b'\x00\x00\x1A\x50\x11\x01\x00'
    SYSEX_ALL_CALL = b'\x7F'
    SYSEX_GET_SYSTEM_STATE = b'\x10'

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

        self._tcp_socket: SocketPort = None

        self._message_channel: int = None
        self._message_parameter: ChannelParametersEnum = None
        self._message_value: int = None

        self._in: BaseInput = None
        self._out: BaseOutput = None

        self._poll_sleep = 0

    def connect(self):
        if not self._enabled:
            return

        in_type = self._configuration['midi_in']['type']
        out_type = self._configuration['midi_out']['type']

        if 'tcp' in [in_type, out_type]:
            self._tcp_socket = connect(host=self._configuration['host'], portno=self.TCP_PORT)
        else:
            self._poll_sleep = 0.001

        if in_type == 'midi':
            self._in = mido.open_input(self._configuration['midi_in']['port_name'])
        else:
            self._in = self._tcp_socket

        if out_type == 'midi':
            self._out = mido.open_output(self._configuration['midi_out']['port_name'])
        else:
            self._out = self._tcp_socket

    def close(self):
        if not self._enabled:
            return

        self._in.close()
        self._out.close()

    def poll(self):
        if not self._enabled:
            return

        message = self._in.receive(block=False)

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

        time.sleep(self._poll_sleep)

    def set_channel_state(self, channel_state: ChannelState):
        if not self._enabled:
            return

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
        if self._tcp_socket is not None:
            self._tcp_socket.send(message)
        else:
            _logger.warning("no MIDI TCP Socket available, unable to request device state")

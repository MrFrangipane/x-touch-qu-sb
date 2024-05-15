from typing import Callable

import mido
from mido.messages import Message
from mido.sockets import connect, SocketPort
from mido.ports import BaseInput, BaseOutput

from xtouchqusb.contracts.abstract_device import AbstractDevice
from xtouchqusb.entities.channel_parameters_enum import ChannelParametersEnum
from xtouchqusb.entities.channel_state import ChannelState


# fixme: remove all ifs for tcp_only and use reference variable
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

    def __init__(self, host: str, tcp_only: bool, channel_state_callback: Callable, midi_in:str = "", midi_out: str = ""):
        super().__init__(channel_state_callback)

        self._tcp_only = tcp_only

        self._tcp_host = host
        self._tcp_socket: SocketPort = None

        self._midi_in_name = midi_in
        self._midi_out_name = midi_out
        self._midi_in: BaseInput = None
        self._midi_out: BaseOutput = None

        self._message_channel: int = None
        self._message_parameter: ChannelParametersEnum = None
        self._message_value: int = None

    def connect(self):
        if self._tcp_only:
            self._tcp_socket = connect(host=self._tcp_host, portno=self.TCP_PORT)
        else:
            self._midi_in = mido.open_input(self._midi_in_name)
            self._midi_out = mido.open_output(self._midi_out_name)

    def close(self):
        if self._tcp_only:
            self._tcp_socket.close()
        else:
            self._midi_in.close()
            self._midi_out.close()

    def poll(self):
        if self._tcp_only:
            message = self._tcp_socket.receive(block=False)
        else:
            message = self._midi_in.receive(block=False)

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
        if self._tcp_only:
            out = self._tcp_socket
        else:
            out = self._midi_out

        if channel_state.parameter == ChannelParametersEnum.UNKNOWN:
            return

        out.send(Message(
            type='control_change',
            control=self.NRPN_CHANNEL,
            value=channel_state.channel
        ))
        out.send(Message(
            type='control_change',
            control=self.NRPN_PARAMETER,
            value=self.CHANNEL_ENUM_PARAMETER_CODE[channel_state.parameter],
        ))
        out.send(Message(
            type='control_change',
            control=self.NRPN_VALUE,
            value=channel_state.value,
        ))
        out.send(Message(
            type='control_change',
            control=self.NRPN_DATA_ENTRY_FINE,
            value=0,  # fixme: not always 0 ?
        ))

    def request_state(self):
        message = Message(
            type='sysex',
            data=self.SYSEX_HEADER + self.SYSEX_ALL_CALL + self.SYSEX_GET_SYSTEM_STATE + b'\x00'  # we are not an iPad
        )
        if self._tcp_only:
            self._tcp_socket.send(message)
        else:
            self._midi_out.send(message)

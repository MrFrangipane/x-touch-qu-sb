import time

from mido.messages import Message
from mido.sockets import connect, SocketPort
from mido.ports import BaseInput, BaseOutput

import logging
import json
import os.path
import sys

from multiprocessing import Process
from rtmidi.midiutil import open_midiinput
from xtouchqusb.python_extensions.mido_extensions import open_input_from_pattern, open_output_from_pattern

_logger = logging.getLogger(__name__)


class QuSbConstants:
    HEADER = b'\x00\x00\x1A\x50\x11\x01\x00'
    ALL_CALL = b'\x7F'
    GET_SYSTEM_STATE = b'\x10'
    SYSTEM_STATE_END = b'\x14'


class QuSbMidi:

    def __init__(self, tcp_host: str, tcp_port: int, port_name_pattern: str):
        self._tcp_host = tcp_host
        self._tcp_port = tcp_port
        self._port_name_pattern = port_name_pattern
        
        self.midi_in: BaseInput = None
        self.midi_out: BaseOutput = None

    def close(self):
        _logger.info(f"Disconnecting USB MIDI ports")

        if self.midi_in is not None:
            self.midi_in.close()
            self.midi_in = None
        
        if self.midi_out is not None:
            self.midi_out.close()
            self.midi_out = None

    def connect(self):
        _logger.info(f"Connecting USB MIDI ports")

        if self.midi_in is None:
            self.midi_in = open_input_from_pattern(self._port_name_pattern)

        if self.midi_out is None:
            self.midi_out = open_output_from_pattern(self._port_name_pattern)

    def receive(self, block=True) -> Message:
        return self.midi_in.receive(block)

    def send(self, message: Message) -> None:
        self.midi_out.send(message)

    def request_state(self) -> list[Message]:
        _logger.info(f"Requesting Qu-SB state ({self._tcp_host}:{self._tcp_port})...")
        begin = time.time()

        was_connected = self.midi_in is not None
        self.close()
    
        request_message = Message(
            type='sysex',
            data=(
                QuSbConstants.HEADER +
                QuSbConstants.ALL_CALL +
                QuSbConstants.GET_SYSTEM_STATE +
                b'\x00'  # we are not an iPad
            )
        )
        messages: list[Message] = list()
        with connect(self._tcp_host, self._tcp_port) as midi_tcp:
            midi_tcp.send(request_message)
    
            while True:
                message = midi_tcp.receive()
                if bytearray(message.bytes()[1:-1]) == QuSbConstants.HEADER + b'\x00' + QuSbConstants.SYSTEM_STATE_END:
                    break
                messages.append(message)
    
            midi_tcp.close()

        if was_connected:
            self.connect()

        _logger.info(f"Received {len(messages)} state messages in {time.time() - begin:.3f}s")

        return messages


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    qu_sb_midi = QuSbMidi(
        tcp_host='192.168.20.4',
        tcp_port=51325,
        port_name_pattern='QU-SB'
    )

    try:
        all_state_messages = qu_sb_midi.request_state()
        qu_sb_midi.connect()

        while True:
            message_ = qu_sb_midi.receive()
            if message_ is not None:
                if message_.type == 'sysex':
                    print('sysex', message_.hex())
                else:
                    print(message_)

    except KeyboardInterrupt:
        pass

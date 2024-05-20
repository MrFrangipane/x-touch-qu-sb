import logging
import time

from mido.messages import Message
from mido.ports import BaseInput, BaseOutput
from mido.sockets import connect

from xtouchqusb.python_extensions.mido_extensions import open_input_from_pattern, open_output_from_pattern
from xtouchqusb.components.qu_sb.constants import QuSbConstants
from xtouchqusb.components.qu_sb.configuration import QuSbConfiguration


_logger = logging.getLogger(__name__)


class QuSbMidi:

    def __init__(self, configuration: QuSbConfiguration):
        self._tcp_host = configuration.tcp_host
        self._tcp_port = configuration.tcp_port
        self._port_name_pattern = configuration.port_name_pattern

        self.midi_in: BaseInput = None
        self.midi_out: BaseOutput = None

    def close(self):
        if self.midi_in is not None:
            _logger.info(f"Disconnecting USB MIDI input")
            self.midi_in.close()
            self.midi_in = None

        if self.midi_out is not None:
            _logger.info(f"Disconnecting USB MIDI output")
            self.midi_out.close()
            self.midi_out = None

    def connect(self):
        if self.midi_in is None:
            _logger.info(f"Connecting USB MIDI input")
            self.midi_in = open_input_from_pattern(self._port_name_pattern)

        if self.midi_out is None:
            _logger.info(f"Connecting USB MIDI output")
            self.midi_out = open_output_from_pattern(self._port_name_pattern)

    def receive_pending(self, block=True) -> Message:
        return self.midi_in.iter_pending()

    def send(self, message: Message) -> None:
        self.midi_out.send(message)

    def request_state(self) -> list[Message]:
        _logger.info(f"Requesting Qu-SB state ({self._tcp_host}:{self._tcp_port})...")
        begin = time.time()

        was_connected = self.midi_in is not None
        self.close()

        request_message = Message(
            type='sysex',
            data=QuSbConstants.SYSEX_REQUEST_STATE
        )
        messages: list[Message] = list()
        with connect(self._tcp_host, self._tcp_port) as midi_tcp:
            midi_tcp.send(request_message)

            while True:
                message = midi_tcp.receive()
                if bytearray(message.bytes()[1:-1]) == QuSbConstants.SYSEX_REQUEST_STATE_END:
                    break
                messages.append(message)

            midi_tcp.close()

        if was_connected:
            self.connect()

        _logger.info(f"Received {len(messages)} state messages in {time.time() - begin:.3f}s")

        return messages

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
from xtouchqusb.python_extensions.mido_extensions import get_input_port_name_from_pattern
from xtouchqusb.components.qu_sb import QuSb

_logger = logging.getLogger(__name__)


def request_state() -> list[Message]:
    _logger.info(f"Requesting Qu-SB state...")
    _begin = time.time()
    messages: list[Message] = list()

    request_message = Message(
        type='sysex',
        data=QuSb.SYSEX_HEADER + QuSb.SYSEX_ALL_CALL + QuSb.SYSEX_GET_SYSTEM_STATE + b'\x00'  # we are not an iPad
    )
    with connect('192.168.20.4', 51325) as midi_tcp:
        midi_tcp.send(request_message)

        while True:
            message = midi_tcp.receive()
            if bytearray(message.bytes()[1:-1]) == QuSb.SYSEX_HEADER + b'\x00' + QuSb.SYSEX_SYSTEM_STATE_END:
                break
            messages.append(message)

        midi_tcp.close()

    _logger.info(f"Done in {time() - begin:.3f}s")

    return messages


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    begin = time.time()
    p = Process(target=request_state)
    p.start()

    try:
        state_messages = request_state()

        port_name = get_input_port_name_from_pattern('QU-SB')
        midi_in, port_name = open_midiinput(port_name)

        while True:
            message = midi_in.get_message()
            print(message)

    except KeyboardInterrupt:
        pass

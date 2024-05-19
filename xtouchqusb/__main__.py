import time

from mido.messages import Message
from mido.sockets import connect, SocketPort
from mido.ports import BaseInput, BaseOutput

import logging
import json
import os.path
import sys

from xtouchqusb.python_extensions.mido_extensions import open_input_from_pattern, open_output_from_pattern
from xtouchqusb.components.qu_sb import QuSb

_logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    midi_tcp = connect('192.168.20.4', 51325)
    midi_in = open_input_from_pattern('QU-SB')
    midi_out = open_output_from_pattern('QU-SB')

    try:
        messages = list()
        request_message = Message(
            type='sysex',
            data=QuSb.SYSEX_HEADER + QuSb.SYSEX_ALL_CALL + QuSb.SYSEX_GET_SYSTEM_STATE + b'\x00'  # we are not an iPad
        )
        begin = time.time()
        midi_tcp.send(request_message)
        for message in midi_tcp:
            if bytearray(message.bytes()[1:-1]) == QuSb.SYSEX_HEADER + b'\x00' + QuSb.SYSEX_SYSTEM_STATE_END:
                midi_tcp.close()
                break
            messages.append((time.time(), message))

        print(f'Elapsed: {messages[-1][0] - begin}')
        print(f'Number of messages: {len(messages)}')

    except KeyboardInterrupt:
        pass

    finally:
        midi_tcp.close()
        midi_in.close()
        midi_out.close()

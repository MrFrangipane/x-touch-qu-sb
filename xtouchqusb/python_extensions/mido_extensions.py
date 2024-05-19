import mido
from mido.ports import BaseInput, BaseOutput

from xtouchqusb.python_extensions import logger


_logger = logger.make_logger(__name__)


def open_input_from_pattern(pattern) -> BaseInput:
    for port_name in mido.get_input_names():
        if pattern in port_name:
            _logger.info(f"Opening MIDI input '{port_name}'")
            return mido.open_input(port_name)

    raise ConnectionError(f"No MIDI in port matching '{pattern}' was found")


def open_output_from_pattern(pattern) -> BaseOutput:
    for port_name in mido.get_output_names():
        if pattern in port_name:
            _logger.info(f"Opening MIDI output '{port_name}'")
            return mido.open_output(port_name)

    raise ConnectionError(f"No MIDI out port matching '{pattern}' was found")


def get_input_port_name_from_pattern(pattern):
    for port_name in mido.get_input_names():
        if pattern in port_name:
            return port_name

    raise ConnectionError(f"No MIDI in port matching '{pattern}' was found")

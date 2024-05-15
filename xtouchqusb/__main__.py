import logging
import json
import os.path
import sys

import mido

from xtouchqusb.components.application import Application


_logger = logging.getLogger(__name__)


def load_configuration(configuration_filepath):
    if not os.path.isfile(configuration_filepath):
        raise FileNotFoundError(f'Configuration file not found {configuration_filepath}')

    with open(configuration_filepath, 'r') as configuration_file:
        configuration = json.load(configuration_file)

    midi_inputs: list[str] = mido.get_input_names()
    midi_outputs: list[str] = mido.get_output_names()

    _logger.info(f"MIDI in ports: {', '.join(midi_inputs)}")
    _logger.info(f"MIDI out ports: {', '.join(midi_outputs)}")

    in_detected = 0
    for midi_input in midi_inputs:
        if configuration['x-touch']['midi_in']['detection_pattern'] in midi_input:
            configuration['x-touch']['midi_in']['port_name'] = midi_input
            in_detected += 1
            _logger.info(f"Auto detected MIDI input port for X Touch '{midi_input}'")

        elif configuration['qu-sb']['midi_in']['detection_pattern'] in midi_input:
            configuration['qu-sb']['midi_in']['port_name'] = midi_input
            in_detected += 1
            _logger.info(f"Auto detected MIDI input port QuSB '{midi_input}'")

    if not in_detected:
        _logger.warning("No MIDI in port detected")

    out_detected = 0
    for midi_output in midi_outputs:
        if configuration['x-touch']['midi_out']['detection_pattern'] in midi_output:
            configuration['x-touch']['midi_out']['port_name'] = midi_output
            out_detected += 1
            _logger.info(f"Auto detected MIDI output port for X Touch '{midi_output}'")

        elif configuration['qu-sb']['midi_out']['detection_pattern'] in midi_output:
            configuration['qu-sb']['midi_out']['port_name'] = midi_output
            out_detected += 1
            _logger.info(f"Auto detected MIDI output port QuSB '{midi_output}'")

    if not out_detected:
        _logger.warning("No MIDI out port detected")

    return configuration


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) == 2:
        configuration_filepath = os.path.join(os.path.dirname(__file__), 'resources', sys.argv[1])
        application = Application()
        application.load_configuration(configuration_filepath)
        application.exec()
    else:
        raise AttributeError('No configuration filepath provided')

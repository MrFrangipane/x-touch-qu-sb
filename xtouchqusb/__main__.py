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

    for midi_input in midi_inputs:
        if 'X-Touch-Ext' in midi_input:
            configuration['x-touch']['midi_in'] = midi_input
            _logger.info(f"Auto detected MIDI input port for X Touch '{midi_input}'")
        elif 'QU-SB MIDI' in midi_input:
            configuration['qu-sb']['midi_in'] = midi_input
            _logger.info(f"Auto detected MIDI input port QuSB '{midi_input}'")

    for midi_output in midi_outputs:
        if 'X-Touch-Ext' in midi_output:
            configuration['x-touch']['midi_out'] = midi_output
            _logger.info(f"Auto detected MIDI output port for X Touch '{midi_output}'")
        elif 'QU-SB MIDI' in midi_output:
            configuration['qu-sb']['midi_out'] = midi_output
            _logger.info(f"Auto detected MIDI output port QuSB '{midi_output}'")

    return configuration


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) == 2:
        configuration_filepath = os.path.join(os.path.dirname(__file__), 'resources', sys.argv[1])
        configuration = load_configuration(configuration_filepath)
        application = Application(configuration)
        application.main()
    else:
        raise AttributeError('No configuration filepath provided')

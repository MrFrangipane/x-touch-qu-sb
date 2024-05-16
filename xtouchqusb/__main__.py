import logging
import json
import os.path
import sys

import mido

from xtouchqusb.components.application import Application


_logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) == 2:
        configuration_filepath = os.path.join(os.path.dirname(__file__), 'resources', sys.argv[1])
        application = Application()
        application.load_configuration(configuration_filepath)
        application.exec()
    else:
        raise AttributeError('No configuration filepath provided')

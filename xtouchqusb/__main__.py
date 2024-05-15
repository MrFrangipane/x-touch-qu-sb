import os.path
import sys

from xtouchqusb.components.application import Application


if __name__ == '__main__':
    import mido
    print('input', mido.get_input_names())
    print('output', mido.get_output_names())

    if len(sys.argv) == 2:
        configuration_filepath = os.path.join(os.path.dirname(__file__), 'resources', sys.argv[1])
        application = Application(configuration_filepath)
        application.main()
    else:
        raise AttributeError('No configuration filepath provided')

from multiprocessing import Process, Queue

from mido import Message

from aa.python_extensions.mido_extensions import open_input_from_pattern, open_output_from_pattern
from aa.entities.channel_state import ChannelState
from aa.entities.channel_parameters_enum import ChannelParametersEnum
from aa.components.qu_sb.constants import QuSbConstants


CHANNEL_OFFSET = 32


class QuSB:
    _message_channel = None
    _message_parameter = None
    _message_value = None

    @staticmethod
    def process(message, queue_to_xtouch):
        #
        # Read
        channel_state = None
        if message is None or message.type == 'active_sensing':
            return

        if message.type == 'sysex':
            # TODO: do something ?
            pass

        elif message.type == 'control_change':
            if message.control == QuSbConstants.NRPN_CHANNEL:
                QuSB._message_channel = message.value

            elif message.control == QuSbConstants.NRPN_PARAMETER:
                QuSB._message_parameter = QuSbConstants.CHANNEL_PARAMETER_CODE_TO_ENUM.get(
                    message.value,
                    ChannelParametersEnum.UNKNOWN
                )

            elif message.control == QuSbConstants.NRPN_VALUE:
                QuSB._message_value = message.value

            elif message.control == QuSbConstants.NRPN_DATA_ENTRY_FINE:
                channel_state = ChannelState(
                    QuSB._message_channel,
                    QuSB._message_parameter,
                    QuSB._message_value
                )

        #
        # Write
        if channel_state is not None:
            channel = channel_state.channel - CHANNEL_OFFSET  # todo: paginate
            if channel > 15 or channel < 0:
                return

            if channel_state.parameter == ChannelParametersEnum.FADER:
                value = int((channel_state.value * 128) - 8192)

                queue_to_xtouch.put(Message(
                    type='pitchwheel',
                    channel=channel,
                    pitch=value
                ))

            elif channel_state.parameter == ChannelParametersEnum.COMPRESSOR_ON:
                value = int(channel_state.value * 127)
                queue_to_xtouch.put(Message(
                    type='note_on',
                    channel=channel,
                    note=24,
                    velocity=value
                ))


def process_xtouch(message, queue_to_qusb):
    #
    # Read
    channel_state = None
    if message.type == 'pitchwheel':
        value = int(float(message.pitch + 8192) / 16380.0 * 127)
        channel_state = ChannelState(
            channel=message.channel + CHANNEL_OFFSET,  # todo: paginate
            parameter=ChannelParametersEnum.FADER,
            value=value
        )

    elif message.type == 'note_on' and message.note == 24:
        channel_state = ChannelState(
            channel=message.channel + CHANNEL_OFFSET,  # todo: paginate
            parameter=ChannelParametersEnum.COMPRESSOR_ON,
            value=int(message.velocity / 127)
        )

    #
    # Write
    if channel_state is not None:
        queue_to_qusb.put(Message(
            type='control_change',
            control=QuSbConstants.NRPN_CHANNEL,
            value=channel_state.channel
        ))
        queue_to_qusb.put(Message(
            type='control_change',
            control=QuSbConstants.NRPN_PARAMETER,
            value=QuSbConstants.CHANNEL_ENUM_PARAMETER_CODE[channel_state.parameter],
        ))
        queue_to_qusb.put(Message(
            type='control_change',
            control=QuSbConstants.NRPN_VALUE,
            value=channel_state.value,
        ))
        queue_to_qusb.put(Message(
            type='control_change',
            control=QuSbConstants.NRPN_DATA_ENTRY_FINE,
            value=0,  # fixme: not always 0 ?
        ))


def qusb_recv(queue):
    midi_in = open_input_from_pattern("MIDI Control")
    try:
        while True:
            message = midi_in.receive()
            QuSB.process(message, queue)
    except KeyboardInterrupt:
        pass


def qusb_send(queue):
    midi_in = open_output_from_pattern("MIDI Control")
    try:
        while True:
            message = queue.get()
            midi_in.send(message)
    except KeyboardInterrupt:
        pass


def xtouch_recv(queue_to_xtouch, queue_to_qusb):
    midi_in = open_input_from_pattern("Frangitronik")
    try:
        while True:
            message = midi_in.receive()
            queue_to_xtouch.put(message)  # loopback
            process_xtouch(message, queue_to_qusb)
    except KeyboardInterrupt:
        pass


def xtouch_send(queue):
    midi_in = open_output_from_pattern("Frangitronik")
    try:
        while True:
            message = queue.get()
            midi_in.send(message)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    queue_to_xtouch = Queue()
    queue_to_qusb = Queue()

    p_qusb_in = Process(target=qusb_recv, args=(queue_to_xtouch,))
    p_qusb_out = Process(target=qusb_send, args=(queue_to_qusb,))

    p_xtouch_in = Process(target=xtouch_recv, args=(queue_to_xtouch, queue_to_qusb))
    p_xtouch_out = Process(target=xtouch_send, args=(queue_to_xtouch,))

    p_xtouch_in.start()
    p_xtouch_out.start()

    p_qusb_in.start()
    p_qusb_out.start()

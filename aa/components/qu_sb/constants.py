from aa.entities.channel_parameters_enum import ChannelParametersEnum


class QuSbConstants:
    SYSEX_HEADER = b'\x00\x00\x1A\x50\x11\x01\x00'
    SYSEX_ALL_CALL = b'\x7F'
    SYSEX_GET_SYSTEM_STATE = b'\x10'

    SYSEX_REQUEST_STATE = SYSEX_HEADER + SYSEX_ALL_CALL + SYSEX_GET_SYSTEM_STATE + b'\x00'  # we are not an iPad
    SYSEX_REQUEST_STATE_END = SYSEX_HEADER + b'\x00' + b'\x14'

    # todo: hex notation ?
    NRPN_CHANNEL = 99
    NRPN_PARAMETER = 98
    NRPN_VALUE = 6
    NRPN_DATA_ENTRY_FINE = 38

    CHANNEL_PARAMETER_CODE_TO_ENUM = {
        23: ChannelParametersEnum.FADER,
        25: ChannelParametersEnum.INPUT_GAIN,
        104: ChannelParametersEnum.COMPRESSOR_ON
    }
    CHANNEL_ENUM_PARAMETER_CODE = {
        ChannelParametersEnum.FADER: 23,
        ChannelParametersEnum.INPUT_GAIN: 25,
        ChannelParametersEnum.COMPRESSOR_ON: 104
    }

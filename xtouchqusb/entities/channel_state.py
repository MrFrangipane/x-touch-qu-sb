from dataclasses import dataclass

from xtouchqusb.entities.channel_parameters_enum import ChannelParametersEnum


@dataclass
class ChannelState:
    channel: int
    parameter: ChannelParametersEnum
    value: int

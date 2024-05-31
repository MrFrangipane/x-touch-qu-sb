from dataclasses import dataclass

from aa.entities.channel_parameters_enum import ChannelParametersEnum


@dataclass
class ChannelState:
    channel: int
    parameter: ChannelParametersEnum
    value: int

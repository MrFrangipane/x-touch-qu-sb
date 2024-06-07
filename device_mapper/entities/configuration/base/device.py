from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from device_mapper.entities.configuration.base.control import BaseControlConfiguration
from device_mapper.entities.configuration.control_bank import ControlBankConfiguration


@dataclass_json
@dataclass
class BaseDeviceConfiguration:
    name: str
    controls: list[BaseControlConfiguration] = field(default_factory=list)
    banks: list[ControlBankConfiguration] = field(default_factory=list)

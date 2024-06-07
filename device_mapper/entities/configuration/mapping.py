from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from device_mapper.entities.configuration.base.device import BaseDeviceConfiguration


@dataclass_json
@dataclass
class MappingConfiguration:
    devices: list[BaseDeviceConfiguration] = field(default_factory=list)

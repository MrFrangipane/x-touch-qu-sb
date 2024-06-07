from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from device_mapper.entities.configuration.bank_control_group import BankControlGroupConfiguration


@dataclass_json
@dataclass
class ControlBankConfiguration:
    page_count: int
    page_up: str
    page_down: str
    control_groups: list[BankControlGroupConfiguration]

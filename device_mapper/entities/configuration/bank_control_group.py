from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class BankControlGroupConfiguration:
    rename_pattern: str
    controls: list[str] = field(default_factory=list)

# Read -> https://lidatong.github.io/dataclasses-json/#overriding-extending

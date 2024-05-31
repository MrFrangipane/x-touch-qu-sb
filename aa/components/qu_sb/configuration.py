from dataclasses import dataclass

from xtouchqusb.contracts.base_configuration import BaseConfiguration


@dataclass
class QuSbConfiguration(BaseConfiguration):
    tcp_host: str
    tcp_port: int
    port_name_pattern: str

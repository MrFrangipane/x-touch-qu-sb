from dataclasses import dataclass

from xtouchqusb.core.configuration import Configuration
from xtouchqusb.python_extensions.singleton_metaclass import SingletonMetaclass


@dataclass
class Components(metaclass=SingletonMetaclass):
    configuration = Configuration()

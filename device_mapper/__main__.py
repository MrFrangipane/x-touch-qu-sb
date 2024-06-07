import sys
from pprint import pprint

from device_mapper.loader.loader import DeviceMappingConfigurationLoader


loader = DeviceMappingConfigurationLoader()
mapping = loader.load_from_yaml(sys.argv[1])


pprint(mapping)

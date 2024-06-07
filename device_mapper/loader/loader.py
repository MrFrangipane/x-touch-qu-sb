from yaml import safe_load

from device_mapper.entities.configuration.mapping import MappingConfiguration
from device_mapper.loader.yaml.loader_v1 import YAMLDeviceMappingConfigurationLoader1


class DeviceMappingConfigurationLoader:
    _YAML_LOADERS = {
        1: YAMLDeviceMappingConfigurationLoader1
    }

    def load_from_yaml(self, filepath: str) -> MappingConfiguration:
        with open(filepath, 'r') as yaml_file:
            configuration_data = safe_load(yaml_file)

        return self._YAML_LOADERS[configuration_data['schema_version']](configuration_data).load()

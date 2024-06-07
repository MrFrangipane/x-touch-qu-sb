from device_mapper.entities.device_type_enum import DeviceType
from device_mapper.entities.configuration.mapping import MappingConfiguration
from device_mapper.entities.configuration.midi_device import MIDIDeviceConfiguration
from device_mapper.entities.configuration.osc_device import OSCDeviceConfiguration
from device_mapper.entities.configuration.meta_device import MetaDeviceConfiguration


class YAMLDeviceMappingConfigurationLoader1:
    def __init__(self, configuration_data: dict):
        self.configuration_data = configuration_data

    def load(self) -> MappingConfiguration:
        data = self.configuration_data
        mapping_configuration = MappingConfiguration()

        for device_data in data['devices']:
            device_configuration_types = {
                DeviceType.MIDI: MIDIDeviceConfiguration,
                DeviceType.OSC: OSCDeviceConfiguration,
                DeviceType.META: MetaDeviceConfiguration
            }
            new_device_type = device_configuration_types.get(device_data['type'], None)
            if new_device_type is None:
                raise ValueError(f"Unknown device type '{device_data['type']}'")

            mapping_configuration.devices.append(new_device_type.from_dict(device_data))

        return mapping_configuration

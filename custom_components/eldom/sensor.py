"""Sensor platform for Eldom integration."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_TYPE_FLAT_BOILER_ELDOM,
    DEVICE_TYPE_FLAT_BOILER_IOT_ELDOM,
    DEVICE_TYPE_NATURELA_BOILER_ELDOM,
    DEVICE_TYPE_SMART_BOILER_ELDOM,
    DOMAIN,
)
from .coordinator import EldomCoordinator
from .eldom_boiler import EldomBoiler, FlatIoTEldomBoiler
from .models import EldomData

HEATER_STATE_ON = "On"
HEATER_STATE_OFF = "Off"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eldom sensor platform."""

    eldom_data: EldomData = hass.data[DOMAIN][config_entry.entry_id]

    await eldom_data.coordinator.async_config_entry_first_refresh()

    entities_to_add = []

    for flat_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_FLAT_BOILER_ELDOM
    ).values():
        entities_to_add.append(
            EldomBoilerDayEnergyConsumptionSensor(flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerNightEnergyConsumptionSensor(flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerSavedEnergySensor(flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerHeaterSensor(flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerEnergyUsageResetDateSensor(flat_boiler, eldom_data.coordinator)
        )

    for smart_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_SMART_BOILER_ELDOM
    ).values():
        entities_to_add.append(
            EldomBoilerDayEnergyConsumptionSensor(smart_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerNightEnergyConsumptionSensor(
                smart_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomBoilerSavedEnergySensor(smart_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerHeaterSensor(smart_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerEnergyUsageResetDateSensor(smart_boiler, eldom_data.coordinator)
        )

    for naturela_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_NATURELA_BOILER_ELDOM
    ).values():
        entities_to_add.append(
            EldomBoilerDayEnergyConsumptionSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomBoilerNightEnergyConsumptionSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomBoilerHeaterSensor(naturela_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomBoilerEnergyUsageResetDateSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomNaturelaSolarTemperatureSensor(naturela_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomNaturelaBoilerTemperatureSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomNaturelaTopTemperatureSensor(naturela_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            EldomNaturelaMiddleTemperatureSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomNaturelaBottomTemperatureSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            EldomNaturelaHeaterOnTemperatureSensor(
                naturela_boiler, eldom_data.coordinator
            )
        )

    for iot_flat_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_FLAT_BOILER_IOT_ELDOM
    ).values():
        entities_to_add.append(
            IoTFlatBoilerHeaterSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerCurrentTemperatureSensor(
                iot_flat_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            IoTFlatBoilerChamber1TemperatureSensor(
                iot_flat_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            IoTFlatBoilerChamber2TemperatureSensor(
                iot_flat_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            IoTFlatBoilerTargetTemperatureSensor(
                iot_flat_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            IoTFlatBoilerPowerfulTargetTemperatureSensor(
                iot_flat_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            IoTFlatBoilerEcoTargetTemperatureChamber1Sensor(
                iot_flat_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            IoTFlatBoilerEcoTargetTemperatureChamber2Sensor(
                iot_flat_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            IoTFlatBoilerExtraSaveRateSensor(
                iot_flat_boiler, eldom_data.coordinator
            )
        )
        entities_to_add.append(
            IoTFlatBoilerReadyTimeSensor(iot_flat_boiler, eldom_data.coordinator)
        )
        entities_to_add.append(
            IoTFlatBoilerRemainingTimeSensor(
                iot_flat_boiler, eldom_data.coordinator
            )
        )

    async_add_entities(entities_to_add)


class EldomBoilerDayEnergyConsumptionSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler day energy consumption sensor."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom energy consumption sensor."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-day-energy-consumption-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Day Energy Consumption"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:lightning-bolt"

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return int(self._eldom_boiler.day_energy_consumption)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


class EldomBoilerNightEnergyConsumptionSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler night energy consumption sensor."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom energy consumption sensor."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-night-energy-consumption-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Night Energy Consumption"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:lightning-bolt"

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return int(self._eldom_boiler.night_energy_consumption)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


class EldomBoilerSavedEnergySensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler energy saved sensor."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom energy saved sensor."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-energy-saved-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Saved Energy"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:lightning-bolt"

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.ENERGY

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfEnergy.KILO_WATT_HOUR

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return int(self._eldom_boiler.saved_energy / 100)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


class EldomBoilerHeaterSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler's heater."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize a sensor for an Eldom boiler's heater."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-heater-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Heater"

    @property
    def icon(self) -> str:
        """Return the icon of the heater sensor."""
        return "mdi:heat-wave"

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.ENUM

    @property
    def options(self) -> list[str]:
        """Return a set of possible options."""
        return [HEATER_STATE_ON, HEATER_STATE_OFF]

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return (
            HEATER_STATE_ON if self._eldom_boiler.heater_enabled else HEATER_STATE_OFF
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


class EldomBoilerEnergyUsageResetDateSensor(SensorEntity, CoordinatorEntity):
    """Representation of an Eldom boiler's energy usage reset date."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize a sensor for an Eldom boiler's heater."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-energy-usage-reset-date-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Energy Usage Reset Date"

    @property
    def icon(self) -> str:
        """Return the icon of the heater sensor."""
        return "mdi:calendar-range"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        if self._eldom_boiler.energy_usage_reset_date == "0001-01-01T00:00:00Z":
            return "Never"

        return self._eldom_boiler.energy_usage_reset_date

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()


class EldomNaturelaTemperatureSensor(SensorEntity, CoordinatorEntity):
    """Base class for Naturela boiler temperature sensors."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize a Naturela temperature sensor."""
        super().__init__(coordinator)
        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )
        self.async_write_ha_state()


class EldomNaturelaSolarTemperatureSensor(EldomNaturelaTemperatureSensor):
    """Sensor for the Naturela boiler's solar collector temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-solar-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Solar Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:solar-panel"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._eldom_boiler.solar_temperature


class EldomNaturelaBoilerTemperatureSensor(EldomNaturelaTemperatureSensor):
    """Sensor for the Naturela boiler's intake temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-boiler-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Boiler Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer-water"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._eldom_boiler.boiler_temperature


class EldomNaturelaTopTemperatureSensor(EldomNaturelaTemperatureSensor):
    """Sensor for the Naturela boiler's top tank zone temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-top-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Tank Top Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer-chevron-up"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._eldom_boiler.top_temperature


class EldomNaturelaMiddleTemperatureSensor(EldomNaturelaTemperatureSensor):
    """Sensor for the Naturela boiler's middle tank zone temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-middle-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Tank Middle Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._eldom_boiler.middle_temperature


class EldomNaturelaBottomTemperatureSensor(EldomNaturelaTemperatureSensor):
    """Sensor for the Naturela boiler's bottom tank zone temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-bottom-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Tank Bottom Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer-chevron-down"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._eldom_boiler.bottom_temperature


class EldomNaturelaHeaterOnTemperatureSensor(EldomNaturelaTemperatureSensor):
    """Sensor for the Naturela boiler's electric heater activation temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-heater-on-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s Heater Activation Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer-alert"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._eldom_boiler.heater_on_temperature


class IoTFlatBoilerTemperatureSensor(SensorEntity, CoordinatorEntity):
    """Base class for IoT flat boiler temperature sensors."""

    def __init__(
        self, boiler: FlatIoTEldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize the IoT flat boiler temperature sensor."""
        super().__init__(coordinator)
        self._boiler = boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(identifiers={(DOMAIN, self._boiler.device_id)})

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._boiler = self.coordinator.data.get(self._boiler.type).get(
            self._boiler.id
        )
        self.async_write_ha_state()


class IoTFlatBoilerCurrentTemperatureSensor(IoTFlatBoilerTemperatureSensor):
    """Sensor for the IoT flat boiler's current temperature (chamber average)."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-current-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Current Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self._boiler.current_temperature


class IoTFlatBoilerChamber1TemperatureSensor(IoTFlatBoilerTemperatureSensor):
    """Sensor for the IoT flat boiler's first chamber temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-chamber1-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Chamber 1 Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self._boiler.chamber1_temperature


class IoTFlatBoilerChamber2TemperatureSensor(IoTFlatBoilerTemperatureSensor):
    """Sensor for the IoT flat boiler's second chamber temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-chamber2-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Chamber 2 Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self._boiler.chamber2_temperature


class IoTFlatBoilerTargetTemperatureSensor(IoTFlatBoilerTemperatureSensor):
    """Sensor for the IoT flat boiler's current target temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-target-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Target Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer-check"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self._boiler.target_temperature


class IoTFlatBoilerPowerfulTargetTemperatureSensor(IoTFlatBoilerTemperatureSensor):
    """Sensor for the IoT flat boiler's Powerful mode target temperature."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-powerful-target-temperature-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Powerful Target Temperature"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer-high"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self._boiler.powerful_target_temp


class IoTFlatBoilerEcoTargetTemperatureChamber1Sensor(IoTFlatBoilerTemperatureSensor):
    """Sensor for the IoT flat boiler's Eco target temp for chamber 1."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-eco-target-temperature-chamber1-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Eco Target Temperature Chamber 1"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self._boiler.eco_target_temp_chamber1


class IoTFlatBoilerEcoTargetTemperatureChamber2Sensor(IoTFlatBoilerTemperatureSensor):
    """Sensor for the IoT flat boiler's Eco target temp for chamber 2."""

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-eco-target-temperature-chamber2-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Eco Target Temperature Chamber 2"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:thermometer"

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        return self._boiler.eco_target_temp_chamber2


class IoTFlatBoilerHeaterSensor(SensorEntity, CoordinatorEntity):
    """Sensor for the IoT flat boiler's heater on/off state."""

    def __init__(
        self, boiler: FlatIoTEldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize the IoT flat boiler heater sensor."""
        super().__init__(coordinator)
        self._boiler = boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(identifiers={(DOMAIN, self._boiler.device_id)})

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-heater-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Heater"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:heat-wave"

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.ENUM

    @property
    def options(self) -> list[str]:
        """Return a set of possible options."""
        return [HEATER_STATE_ON, HEATER_STATE_OFF]

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return HEATER_STATE_ON if self._boiler.heater_enabled else HEATER_STATE_OFF

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._boiler = self.coordinator.data.get(self._boiler.type).get(
            self._boiler.id
        )
        self.async_write_ha_state()


class IoTFlatBoilerExtraSaveRateSensor(SensorEntity, CoordinatorEntity):
    """Sensor for the IoT flat boiler's ExtraSave tariff zone count."""

    def __init__(
        self, boiler: FlatIoTEldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._boiler = boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(identifiers={(DOMAIN, self._boiler.device_id)})

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-extra-save-rate-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Extra Save Rate"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:calendar-clock"

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self._boiler.extra_save_rate

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._boiler = self.coordinator.data.get(self._boiler.type).get(
            self._boiler.id
        )
        self.async_write_ha_state()


class IoTFlatBoilerReadyTimeSensor(SensorEntity, CoordinatorEntity):
    """Sensor for the IoT flat boiler's ready time."""

    def __init__(
        self, boiler: FlatIoTEldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._boiler = boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(identifiers={(DOMAIN, self._boiler.device_id)})

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-ready-time-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Ready Time"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:clock-check"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self._boiler.ready_time or None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._boiler = self.coordinator.data.get(self._boiler.type).get(
            self._boiler.id
        )
        self.async_write_ha_state()


class IoTFlatBoilerRemainingTimeSensor(SensorEntity, CoordinatorEntity):
    """Sensor for the IoT flat boiler's remaining time for the current mode."""

    def __init__(
        self, boiler: FlatIoTEldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._boiler = boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(identifiers={(DOMAIN, self._boiler.device_id)})

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._boiler.device_id}-remaining-time-sensor"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._boiler.name}'s Remaining Time"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:timer-outline"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self._boiler.remain_time or None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._boiler = self.coordinator.data.get(self._boiler.type).get(
            self._boiler.id
        )
        self.async_write_ha_state()

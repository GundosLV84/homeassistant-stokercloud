"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


from GundosStokercloud.controller_data import PowerState, Unit, Value
from GundosStokercloud.client import Client as StokerCloudClient


import datetime
from homeassistant.const import CONF_USERNAME, UnitOfPower, UnitOfTemperature, UnitOfMass, PERCENTAGE, UnitOfVolumeFlowRate, UnitOfPressure
from .const import DOMAIN
from .mixins import StokerCloudControllerMixin

import logging

logger = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(minutes=1)

async def async_setup_entry(hass, config, async_add_entities):
    """Set up the sensor platform."""
    client = hass.data[DOMAIN][config.entry_id]
    serial = config.data[CONF_USERNAME]
    logger.debug(client.BASE_URL)
    logger.debug(client.query_url)
    async_add_entities([
        StokerCloudControllerBinarySensor(client, serial, 'Running', 'running', 'power'),
        StokerCloudControllerBinarySensor(client, serial, 'Alarm', 'alarm', 'problem'),
        StokerCloudControllerSensor(client, serial, 'Boiler Temperature', 'boiler_temperature_current', SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Boiler Temperature Requested', 'boiler_temperature_requested', SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Boiler Power', 'boiler_kwh', SensorDeviceClass.POWER),
        StokerCloudControllerSensor(client, serial, 'Total Consumption', 'consumption_total', state_class=SensorStateClass.TOTAL_INCREASING), # state class STATE_CLASS_TOTAL_INCREASING
        StokerCloudControllerSensor(client, serial, 'State', 'state'),
        StokerCloudControllerSensor(client, serial, 'Boiler Power %', 'boiler_powerPrc', SensorDeviceClass.POWER_FACTOR),
        StokerCloudControllerSensor(client, serial, 'Boiler smoke temperature', 'boiler_returntemp', SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Boiler actual O2%', 'boiler_actualo2', SensorDeviceClass.MOISTURE),
        StokerCloudControllerSensor(client, serial, 'Hopper content', 'hopper_content', SensorDeviceClass.WEIGHT),
        StokerCloudControllerSensor(client, serial, 'Boiler wanted O2%', 'wanted_o2', SensorDeviceClass.MOISTURE),
        StokerCloudControllerSensor(client, serial, 'Boiler wanted air flow', 'wanted_air', SensorDeviceClass.VOLUME_FLOW_RATE), 
        StokerCloudControllerSensor(client, serial, 'Buffer tank temp', 'hotwater_temperature_current', SensorDeviceClass.TEMPERATURE), 
        StokerCloudControllerSensor(client, serial, 'Back pressure Pa', 'backpressure', SensorDeviceClass.PRESSURE), 
        StokerCloudControllerSensor(client, serial, 'Exhaust fan %', 'exhaust_fan' ), 
        StokerCloudControllerSensor(client, serial, 'Photosensor', 'photosensor', SensorDeviceClass.HUMIDITY), 
        StokerCloudControllerSensor(client, serial, 'Dropshaft temperature', 'dropshaft_temp', SensorDeviceClass.TEMPERATURE),
        StokerCloudControllerSensor(client, serial, 'Pressure Pa', 'pressure', SensorDeviceClass.PRESSURE), 
        StokerCloudControllerSensor(client, serial, 'Fan speed %', 'fan_speed'),
        StokerCloudControllerSensor(client, serial, 'Boiler 17 return temperature', 'boiler_returntemp17', SensorDeviceClass.TEMPERATURE),
    ])





class StokerCloudControllerBinarySensor(StokerCloudControllerMixin, BinarySensorEntity):
    """Representation of a Sensor."""

    def __init__(self, client: StokerCloudClient, serial, name: str, client_key: str, device_class):
        """Initialize the sensor."""
        super(StokerCloudControllerBinarySensor, self).__init__(client, serial, name, client_key)
        self._device_class = device_class

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._state is PowerState.ON

    @property
    def device_class(self):
        return self._device_class


class StokerCloudControllerSensor(StokerCloudControllerMixin, SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, client: StokerCloudClient, serial, name: str, client_key: str, device_class=None, state_class=None):
        """Initialize the sensor."""
        super(StokerCloudControllerSensor, self).__init__(client, serial, name, client_key)
        self._device_class = device_class
        self._attr_state_class = state_class

    @property
    def device_class(self):
        return self._device_class

    @property
    def native_value(self):
        """Return the value reported by the sensor."""
        if self._state:
            if isinstance(self._state, Value):
                return self._state.value
            return self._state

    @property
    def native_unit_of_measurement(self):
        if self._state and isinstance(self._state, Value):
            return {
                Unit.KWH: UnitOfPower.KILO_WATT,
                Unit.DEGREE: UnitOfTemperature.CELSIUS,
                Unit.KILO_GRAM: UnitOfMass.KILOGRAMS,
                Unit.PERCENT: PERCENTAGE,
                Unit.M3HOUR: UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
                Unit.PASCAL: UnitOfPressure.PA,
            }.get(self._state.unit)
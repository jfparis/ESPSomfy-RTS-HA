"""Binary sensors related to ESPSomfy-RTS-HA"""
from __future__ import annotations


from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


from .entity import ESPSomfyEntity
from .controller import ESPSomfyController
from .const import DOMAIN, EVT_SHADESTATE


from homeassistant.components.binary_sensor import BinarySensorEntity

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up shades for the shade controller."""
    controller = hass.data[DOMAIN][config_entry.entry_id]
    new_entities = []
    for shade in controller.api.shades:
        try:
            if "shadeType" in shade:
                match(shade["shadeType"]):
                    case 3:
                        new_entities.append(ESPSomfySunSensor(controller, shade))
                        new_entities.append(ESPSomfyWindSensor(controller, shade))

        except KeyError:
            pass
    if new_entities:
        async_add_entities(new_entities)


class ESPSomfySunSensor(ESPSomfyEntity, BinarySensorEntity):
    """A sun flag sensor indicating whether there is sun"""

    def __init__(self, controller: ESPSomfyController, data):
        """Initialize a new SunSensor"""
        super().__init__(controller=controller, data=data)
        self._controller = controller
        self._shade_id = data["shadeId"]
        self._attr_unique_id = f"sun_{controller.unique_id}_{self._shade_id}"
        self._attr_name = data["name"]
        self._attr_has_entity_name = False
        if "flags" in data:
            self._attr_is_on = bool((int(data["flags"]) & 0x20) == 0x20)
        else:
            self._attr_is_on = False

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if "shadeId" in self._controller.data:
            if self._controller.data["shadeId"] == self._shade_id:
                if (
                    self._controller.data["event"] == EVT_SHADESTATE
                    and "flags" in self._controller.data
                ):
                    self._attr_is_on = bool((int(self._controller.data["flags"]) & 0x20) == 0x20)
                    self.async_write_ha_state()

    @property
    def icon(self) -> str:
        if self.is_on:
            return "mdi:weather-sunny"
        return "mdi:weather-sunny-off"

class ESPSomfyWindSensor(ESPSomfyEntity, BinarySensorEntity):
    """A sun flag sensor indicating whether there is sun"""

    def __init__(self, controller: ESPSomfyController, data):
        """Initialize a new SunSensor"""
        super().__init__(controller=controller, data=data)
        self._controller = controller
        self._shade_id = data["shadeId"]
        self._attr_unique_id = f"wind_{controller.unique_id}_{self._shade_id}"
        self._attr_name = data["name"]
        self._attr_has_entity_name = False
        if "flags" in data:
            self._attr_is_on = bool((int(data["flags"]) & 0x10) == 0x10)
        else:
            self._attr_is_on = False

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if "shadeId" in self._controller.data:
            if self._controller.data["shadeId"] == self._shade_id:
                if (
                    self._controller.data["event"] == EVT_SHADESTATE
                    and "flags" in self._controller.data
                ):
                    self._attr_is_on = bool((int(self._controller.data["flags"]) & 0x10) == 0x10)
                self.async_write_ha_state()

    @property
    def icon(self) -> str:
        if self.is_on:
            return "mdi:wind-power"
        return "mdi:wind-power-outline"

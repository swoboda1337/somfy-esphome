import esphome.codegen as cg
from esphome.components import binary_sensor
import esphome.config_validation as cv
from esphome.const import CONF_ADDRESS, CONF_ID, DEVICE_CLASS_LIGHT, DEVICE_CLASS_MOVING

from .. import SomfyComponent, somfy_ns

DEPENDENCIES = ["somfy"]

CONF_SOMFY_ID = "somfy_id"
CONF_SUNNY = "sunny"
CONF_WINDY = "windy"

SomfyBinarySensor = somfy_ns.class_("SomfyBinarySensor", cg.Component)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(SomfyBinarySensor),
        cv.GenerateID(CONF_SOMFY_ID): cv.use_id(SomfyComponent),
        cv.Required(CONF_ADDRESS): cv.hex_uint32_t,
        cv.Optional(CONF_SUNNY): binary_sensor.binary_sensor_schema(
            device_class=DEVICE_CLASS_LIGHT,
        ),
        cv.Optional(CONF_WINDY): binary_sensor.binary_sensor_schema(
            device_class=DEVICE_CLASS_MOVING,
        ),
    }
)

async def to_code(config):
    parent = await cg.get_variable(config[CONF_SOMFY_ID])
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    cg.add(var.set_address(config[CONF_ADDRESS]))
    if CONF_SUNNY in config:
        sens = await binary_sensor.new_binary_sensor(
            config[CONF_SUNNY]
        )
        cg.add(var.set_sunny_binary_sensor(sens))
    if CONF_WINDY in config:
        sens = await binary_sensor.new_binary_sensor(
            config[CONF_WINDY]
        )
        cg.add(var.set_windy_binary_sensor(sens))
    cg.add(parent.add_sensor(var))

from esphome import automation
import esphome.codegen as cg
from esphome.components import remote_transmitter
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_ADDRESS

CODEOWNERS = ["@swoboda1337"]
DEPENDENCIES = ["remote_transmitter"]
MULTI_CONF = True
CONF_TRANSMITTER_ID = "transmitter_id"
CONF_COMMAND = "command"
CONF_REPEAT = "repeat"

somfy_ns = cg.esphome_ns.namespace("somfy")
SomfyComponent = somfy_ns.class_("SomfyComponent", cg.Component)
SomfySendCommandAction = somfy_ns.class_("SomfySendCommandAction", automation.Action)

SomfyCommand = somfy_ns.enum("SomfyCommand")
SOMFY_COMMAND = {
    "SOMFY_MY": SomfyCommand.SOMFY_MY,
    "SOMFY_UP": SomfyCommand.SOMFY_UP,
    "SOMFY_MYUP": SomfyCommand.SOMFY_MYUP,
    "SOMFY_DOWN": SomfyCommand.SOMFY_DOWN,
    "SOMFY_MYDOWN": SomfyCommand.SOMFY_MYDOWN,
    "SOMFY_UPDOWN": SomfyCommand.SOMFY_UPDOWN,
    "SOMFY_PROG": SomfyCommand.SOMFY_PROG,
    "SOMFY_SUNFLAG": SomfyCommand.SOMFY_SUNFLAG,
    "SOMFY_FLAG": SomfyCommand.SOMFY_FLAG,
}

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(SomfyComponent),
        cv.GenerateID(CONF_TRANSMITTER_ID): cv.use_id(
            remote_transmitter.RemoteTransmitterComponent
        ),
        cv.Required(CONF_ADDRESS): cv.hex_uint32_t,
    }
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    transmitter = await cg.get_variable(config[CONF_TRANSMITTER_ID])
    cg.add(var.set_tx(transmitter))
    cg.add(var.set_address(config[CONF_ADDRESS]))


@automation.register_action(
    "somfy.send_command",
    SomfySendCommandAction,
    cv.Schema(
        {
            cv.Required(CONF_ID): cv.use_id(SomfyComponent),
            cv.Required(CONF_COMMAND): cv.templatable(cv.enum(SOMFY_COMMAND, upper=True)),
            cv.Required(CONF_REPEAT): cv.templatable(cv.int_range(min=0, max=5)),
        }
    ),
)
async def text_sensor_template_publish_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    command = await cg.templatable(config[CONF_COMMAND], args, SomfyCommand)
    repeat = await cg.templatable(config[CONF_REPEAT], args, cg.uint32)
    cg.add(var.set_command(command))
    cg.add(var.set_repeat(repeat))
    return var

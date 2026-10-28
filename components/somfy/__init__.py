from esphome import automation
import esphome.codegen as cg
from esphome.components import remote_base, remote_receiver, remote_transmitter
import esphome.config_validation as cv
from esphome.types import ConfigType
from esphome.const import CONF_ID, CONF_ADDRESS, CONF_TRIGGER_ID

CODEOWNERS = ["@swoboda1337"]
DEPENDENCIES = ["remote_transmitter", "remote_receiver"]
MULTI_CONF = True
CONF_TRANSMITTER_ID = "transmitter_id"
CONF_RECEIVER_ID = "receiver_id"
CONF_COMMAND = "command"
CONF_REPEAT = "repeat"
CONF_CODE = "code"
CONF_ON_COMMAND = "on_command"

somfy_ns = cg.esphome_ns.namespace("somfy")
SomfyComponent = somfy_ns.class_("SomfyComponent", cg.Component)
SomfySendCommandAction = somfy_ns.class_("SomfySendCommandAction", automation.Action)
SomfySetCodeAction = somfy_ns.class_("SomfySetCodeAction", automation.Action)
SomfyCommandTrigger = somfy_ns.class_(
    "SomfyCommandTrigger", automation.Trigger.template(cg.uint32, cg.uint8, cg.uint16)
)

SomfyCommand = somfy_ns.enum("SomfyCommand")
SOMFY_COMMAND = {
    "MY": SomfyCommand.SOMFY_MY,
    "UP": SomfyCommand.SOMFY_UP,
    "MYUP": SomfyCommand.SOMFY_MYUP,
    "DOWN": SomfyCommand.SOMFY_DOWN,
    "MYDOWN": SomfyCommand.SOMFY_MYDOWN,
    "UPDOWN": SomfyCommand.SOMFY_UPDOWN,
    "MYUPDOWN": SomfyCommand.SOMFY_MYUPDOWN,
    "PROG": SomfyCommand.SOMFY_PROG,
    "SUNFLAG": SomfyCommand.SOMFY_SUNFLAG,
    "FLAG": SomfyCommand.SOMFY_FLAG,
    "STEPDOWN": SomfyCommand.SOMFY_STEPDOWN,
    "TOGGLE": SomfyCommand.SOMFY_TOGGLE,
    "SENSOR": SomfyCommand.SOMFY_SENSOR,
}

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(SomfyComponent),
        cv.GenerateID(CONF_TRANSMITTER_ID): cv.use_id(
            remote_transmitter.RemoteTransmitterComponent
        ),
        cv.GenerateID(CONF_RECEIVER_ID): cv.use_id(
            remote_receiver.RemoteReceiverComponent
        ),
        cv.Required(CONF_ADDRESS): cv.hex_uint32_t,
        cv.Optional(CONF_ON_COMMAND): automation.validate_automation(
            {
                cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(SomfyCommandTrigger),
            }
        ),
    }
)

async def to_code(config: ConfigType) -> None:
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    transmitter = await cg.get_variable(config[CONF_TRANSMITTER_ID])
    cg.add(var.set_tx(transmitter))
    await remote_base.register_listener(var, config)
    cg.add(var.set_address(config[CONF_ADDRESS]))
    for conf in config.get(CONF_ON_COMMAND, []):
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(
            trigger,
            [(cg.uint32, "address"), (cg.uint8, "command"), (cg.uint16, "code")],
            conf,
        )


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
    synchronous=True,
)
async def somfy_send_command_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    command = await cg.templatable(config[CONF_COMMAND], args, SomfyCommand)
    repeat = await cg.templatable(config[CONF_REPEAT], args, cg.uint32)
    cg.add(var.set_command(command))
    cg.add(var.set_repeat(repeat))
    return var

@automation.register_action(
    "somfy.set_code",
    SomfySetCodeAction,
    cv.Schema(
        {
            cv.Required(CONF_ID): cv.use_id(SomfyComponent),
            cv.Required(CONF_CODE): cv.templatable(cv.uint16_t),
        }
    ),
    synchronous=True,
)
async def somfy_set_code_to_code(config, action_id, template_arg, args):
    paren = await cg.get_variable(config[CONF_ID])
    var = cg.new_Pvariable(action_id, template_arg, paren)
    code = await cg.templatable(config[CONF_CODE], args, cg.uint16)
    cg.add(var.set_code(code))
    return var

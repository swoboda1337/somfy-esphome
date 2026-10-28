ESPHome Somfy remote component based off of https://github.com/Legion2/Somfy_Remote_Lib/

Commands are: MY, UP, MYUP, DOWN, MYDOWN, UPDOWN, MYUPDOWN, PROG, SUNFLAG, FLAG, STEPDOWN, TOGGLE, SENSOR. Address should be a random 24 bit (or 6 hex digit) number. Can create any number of remotes, buttons or covers.

The RF board needs to use 433.42 MHz not 433.92 MHz. The [CC1101](https://esphome.io/components/cc1101/) and [SX127x](https://esphome.io/components/sx127x/) components built into ESPHome both work, see their docs for wiring and the other options.

Example yaml for CC1101 (update pins for your board):

    spi:
      clk_pin: GPIO18
      miso_pin: GPIO19
      mosi_pin: GPIO23

    cc1101:
      cs_pin: GPIO5
      frequency: 433.42MHz

    remote_receiver:
      pin: GPIO12
      filter: 200us
      idle: 6000us

    remote_transmitter:
      pin: GPIO13
      carrier_duty_percent: 100%
      on_transmit:
        then:
          - cc1101.begin_tx
      on_complete:
        then:
          - cc1101.begin_rx

Example yaml for SX127x (update pins for your board):

    spi:
      clk_pin: GPIO5
      mosi_pin: GPIO27
      miso_pin: GPIO19

    sx127x:
      cs_pin: GPIO18
      rst_pin: GPIO23
      bandwidth: 50_0kHz
      frequency: 433.42MHz
      modulation: OOK
      bitsync: false
      packet_mode: false
      rx_start: true
      rx_floor: -90
      pa_pin: BOOST
      pa_power: 17

    remote_receiver:
      pin:
        number: GPIO32
        mode:
          input: true
          output: true
          pullup: true
          open_drain: true
        allow_other_uses: true
      filter: 200us
      idle: 6000us

    remote_transmitter:
      pin:
        number: GPIO32
        mode:
          input: true
          output: true
          pullup: true
          open_drain: true
        allow_other_uses: true
      eot_level: false
      carrier_duty_percent: 100%
      on_transmit:
        then:
          - sx127x.set_mode_standby
          - remote_transmitter.digital_write: false
          - sx127x.set_mode_tx
      on_complete:
        then:
          - sx127x.set_mode_standby
          - remote_transmitter.digital_write: true
          - sx127x.set_mode_rx

Every `somfy:` entry decodes every frame on the band, not just its own address. Use `on_command` to react to frames from other remotes, for example to keep a cover in sync when a physical remote is used. The trigger gets `address` (24 bit), `command` (the 4 bit command, see the enum above) and `code` (the 16 bit rolling code). A single button press sends the same frame two or three times with the same rolling code, so compare `code` to the last one seen if you only want to act once per press:

    globals:
      - id: last_code
        type: uint16_t
        initial_value: '0'

    somfy:
      - address: 0x111111
        id: remote_1
        on_command:
          - if:
              condition:
                lambda: 'return address == 0xAABBCC && code != id(last_code);'
              then:
                - lambda: 'id(last_code) = code;'
                - if:
                    condition:
                      lambda: 'return command == 0x2;'
                    then:
                      - cover.open: my_cover
                - if:
                    condition:
                      lambda: 'return command == 0x4;'
                    then:
                      - cover.close: my_cover
                - if:
                    condition:
                      lambda: 'return command == 0x1;'
                    then:
                      - cover.stop: my_cover

Example yaml for Somfy:

    external_components:
    - source:
        type: git
        url: https://github.com/swoboda1337/somfy-esphome
        ref: main
      refresh: 5min

    somfy:
      - address: 0x111111
        id: remote_1

    binary_sensor:
      - platform: somfy
        address: 0x222222
        sunny:
          name: "Sunny"
        windy:
          name: "Windy"

    button:
      - platform: template
        name: "Somfy PROG"
        on_press:
          then:
            - somfy.send_command:
                id: remote_1
                command: PROG
                repeat: 1

    cover:
      - platform: template
        name: "Somfy Cover"
        open_action:
          - somfy.send_command:
              id: remote_1
              command: DOWN
              repeat: 1
        close_action:
          - somfy.send_command:
              id: remote_1
              command: UP
              repeat: 1
        optimistic: true

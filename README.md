ESPHome Somfy remote component based off of https://github.com/Legion2/Somfy_Remote_Lib/

Commands are: MY, UP, MYUP, DOWN, MYDOWN, UPDOWN, PROG, SUNFLAG, FLAG. Address should be a random 24 bit (or 6 hex digit) number. Can create any number of remotes, buttons or covers.

The RF board needs to use 433.42 MHz not 433.92 MHz. There are two RFs CC1101 https://github.com/esphome/esphome/pull/6300 and SX127x https://github.com/esphome/esphome/pull/7490 that will work. Both are currently being reviewed but are usable now, see the links for more info.

Example yaml for CC1101 (update pins for your board):

    external_components:
      - source: github://pr#6300
        components: [ cc1101 ]
        refresh: 5min

    spi:
      clk_pin: GPIO18
      miso_pin: GPIO19
      mosi_pin: GPIO23

    cc1101:
      id: cc1101_id
      cs_pin: GPIO5
      bandwidth: 200
      frequency: 433420

    remote_transmitter:
      pin: GPIO13
      carrier_duty_percent: 100%
      on_transmit:
        then:
          - cc1101.begin_tx: cc1101_id
      on_complete:
        then:
          - cc1101.end_tx: cc1101_id

Example yaml for SX127x (update pins for your board):

    external_components:
      - source: github://pr#7490
        components: [ sx127x ]
        refresh: 5min

    spi:
      clk_pin: GPIO5
      mosi_pin: GPIO27
      miso_pin: GPIO19

    sx127x:
      id: sx127x_id
      nss_pin: GPIO18
      rst_pin: GPIO23
      frequency: 433420000
      modulation: OOK
      rx_start: false
      pa_pin: BOOST
      pa_power: 17

    remote_transmitter:
      pin: GPIO32
      carrier_duty_percent: 100%
      on_transmit:
        then:
          - sx127x.set_mode_tx: sx127x_id
      on_complete:
        then:
          - sx127x.set_mode_rx: sx127x_id

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
      - address: 0x222222
        id: remote_2
      - address: 0x333333
        id: remote_3
      - address: 0x444444
        id: remote_4

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
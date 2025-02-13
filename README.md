ESPHome Somfy remote component based off of https://github.com/Legion2/Somfy_Remote_Lib/

Commands are: MY, UP, MYUP, DOWN, MYDOWN, UPDOWN, PROG, SUNFLAG, FLAG. Address should be a random 24 bit (or 6 hex digit) number. Can create any number of remotes, buttons or covers.

The RF board needs to use 433.42 MHz not 433.92 MHz. There are two RFs CC1101 https://github.com/esphome/esphome/pull/6300 and SX127x https://github.com/esphome/esphome/pull/7490 that will work. They are currently being reviewed, but are usable, see the links for more info.

Example yaml for CC1101 (update pins for your board):

    external_components:
      - source: github://pr#6300
        components: [ cc1101 ]

    spi:
      clk_pin: GPIO18
      miso_pin: GPIO19
      mosi_pin: GPIO23

    cc1101:
      id: cc1101_id
      cs_pin: GPIO5
      bandwidth: 200
      frequency: 433420

    remote_receiver:
      pin: GPIO12
      filter: 200us
      idle: 6000us

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
      - source: github://pr#7770
        components: [ remote_base, remote_receiver, remote_transmitter, esp32_rmt ]
      - source: github://pr#7490
        components: [ sx127x ]

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
      pa_pin: BOOST
      pa_power: 17

    remote_receiver:
      id: rx_id
      pin:
        number: GPIO32
        allow_other_uses: true
      filter: 200us
      idle: 6000us

    remote_transmitter:
      id: tx_id
      pin:
        number: GPIO32
        allow_other_uses: true
      one_wire: true
      eot_level: false
      carrier_duty_percent: 100%
      on_transmit:
        then:
          - sx127x.set_mode_standby
          - lambda: 'id(tx_id)->digital_write(false);'
          - sx127x.set_mode_tx
      on_complete:
        then:
          - sx127x.set_mode_standby
          - lambda: 'id(tx_id)->digital_write(true);'
          - sx127x.set_mode_rx

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
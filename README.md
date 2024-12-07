NOTE: This is a work in progress.

ESPHome Somfy Remote Component.

RF needs to use 433.42 MHz not 433.92 MHz.

Example yaml (valid commands are MY, UP, MYUP, DOWN, MYDOWN, UPDOWN, PROG, SUNFLAG, FLAG):

    external_components:
    - source:
        type: git
        url: https://github.com/swoboda1337/somfy-esphome
        ref: main
      refresh: 5min

    somfy:
      - address: 0x11111111
        id: remote_1
      - address: 0x22222222
        id: remote_2
      - address: 0x33333333
        id: remote_3
      - address: 0x44444444
        id: remote_4

    remote_transmitter:
      pin: GPIO20
      carrier_duty_percent: 100%

    button:
      - platform: template
        name: "Test Button 1"
        on_press:
          then:
            - somfy.set_code: 
                id: remote_1
                code: 1337
      - platform: template
        name: "Test Button 2"
        on_press:
          then:
            - somfy.send_command: 
                id: remote_1
                command: UP
                repeat: 1


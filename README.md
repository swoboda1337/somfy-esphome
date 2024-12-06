ESPHome Somfy Remote Component. 

Example yaml to use in esphome device config:

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
      pin:
        number: GPIO20
        allow_other_uses: true
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
                command: SOMFY_UP
                repeat: 1

Valid commands are:

    SOMFY_MY
    SOMFY_UP
    SOMFY_MYUP
    SOMFY_DOWN
    SOMFY_MYDOWN
    SOMFY_UPDOWN
    SOMFY_PROG
    SOMFY_SUNFLAG
    SOMFY_FLAG

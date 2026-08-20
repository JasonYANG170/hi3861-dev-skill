# Boards and BSP selection

## Default: PZ-Hi3861

The captured application `BUILD.gn` selects `//vendor/pzkj/pz_hi3861/demo:demo`. Its demo dispatcher contains 43 numbered examples and currently enables only `42_ps2`. Enable one intended application feature at a time unless their entry points and dependencies are deliberately composed.

PZ BSP evidence is in `vendor/pzkj/pz_hi3861/common/bsp/`. Notable captured mappings include:

- LED: GPIO2; PWM demo muxes GPIO2 to PWM2.
- Keys: GPIO11 and GPIO12; GPIO11 is also ADC channel 5.
- UART0: GPIO3 TX, GPIO4 RX.
- OLED/NFC I2C0: GPIO9 SCL, GPIO10 SDA.
- Beeper/relay/DC motor: GPIO14, so these functions conflict when used together.
- DS18B20/DHT11: GPIO7; stepper IN4 also uses GPIO7.
- Stepper: GPIO1, GPIO5, GPIO6, GPIO7.
- HC-SR04: GPIO13 trigger, GPIO14 echo.

These mappings are evidence from the included BSP, not universal Hi3861 pin assignments.

## Other bundled boards

- HiHope HiSpark Pegasus: `vendor/hihope/hispark_pegasus`.
- Huawei/HiSilicon HiSpark Pegasus SDK demos: `vendor/hisilicon/hispark_pegasus` and native `sdk_liteos/app/demo`.
- HiSpark M1: `vendor/hisilicon/hispark_M1`, including the practical SPI gyro/Flash example.
- BearPi-HM Nano: `vendor/bearpi/bearpi_hm_nano`.
- FS-Hi3861: `vendor/hqyj/fs_hi3861`.

When adapting across boards, retain the peripheral transaction logic but replace pin mux, pull/drive, board BSP, device address, electrical assumptions, GN dependencies, and any voltage conversion coefficients.

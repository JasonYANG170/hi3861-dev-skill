# Peripheral development

## Common workflow

Verify the pin can provide the requested mux in `hi_io.h`; configure pull/drive and mux before peripheral initialization; enable the matching `CONFIG_*` switch; check every return value; and copy transfer/address conventions from a Hi3861 example rather than a generic bus implementation.

## Evidence routes

- GPIO/IRQ: `hi_gpio.h`, `hi_io.h`, platform GPIO driver, PZ `08_led`, `11_key`, and `14_exti`.
- I2C/IIC: `hi_i2c.h`, platform I2C driver, native `app_demo_i2c.c`, PZ NFC/OLED BSP, Pegasus AHT20, and BearPi NFC. Check whether the API expects an 8-bit address containing R/W or a 7-bit address shifted by the example.
- SPI: `hi_spi.h`, platform SPI driver, native `app_demo_spi.c`, and HiSpark M1 `spi_gyro_demo`. The native demo covers host/slave, 8/16-bit, loopback, IRQ, and DMA. `CONFIG_SPI_SUPPORT` is disabled in the captured default configuration.
- PWM: `hi_pwm.h`, PZ `bsp_pwm.c`/`16_pwm`, BearPi `B3_basic_pwm_led`, and Pegasus PWM demos. Confirm the PWM channel matches the selected GPIO mux; the PZ LED uses GPIO2/PWM2.
- ADC: `hi_adc.h`, native `app_demo_adc.c`, PZ `bsp_adc.c`/`18_adc`, BearPi `B4_basic_adc`, and Pegasus `09_adc`. Preserve channel, averaging model, current-bias mode, reset count, and the board-specific voltage divider formula. PZ GPIO11 maps to ADC channel 5 in its BSP.
- UART: `hi_uart.h`, PZ `bsp_uart.c`/`17_uart`, and Pegasus/BearPi UART examples. PZ UART0 uses GPIO3 TX and GPIO4 RX.
- Timer/DMA/I2S/watchdog: use `hi_timer.h`, `hi_hrtimer.h`, `hi_dma.h`, `hi_i2s.h`, and `hi_watchdog.h`, then locate the native demo or closest board example through the index.
- Flash/NV: use `hi_flash.h`, `hi_flash_base.h`, `hi_nv.h`, and partition definitions; never infer writable ranges without the selected partition table.

## Configuration check

Inspect `sdk_liteos/build/config/usr_config.mk`. In the captured SDK, I2C and PWM are explicitly enabled, while SPI and SPI DMA are disabled. Do not assume the user's project retained these values.

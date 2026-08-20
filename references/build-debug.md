# Build, flash, and debugging

## Project wiring

1. Confirm `applications/sample/wifi-iot/app/BUILD.gn` selects the intended Vendor component.
2. Confirm the Vendor dispatcher selects the intended demo target.
3. Inspect that demo's `BUILD.gn` for sources, include paths, libraries, and BSP dependencies.
4. Enable required `CONFIG_*` options in the actual `sdk_liteos/build/config/usr_config.mk` used by the build.
5. Choose the build entry from evidence in the selected tree, then build from the SDK source root using the environment supplied with that SDK. Do not assume global `hb`, GN, Ninja, or RISC-V GCC is installed.

## Build-flow selection

- Use the OpenHarmony `hb` flow when the checkout exposes the standard product/component build and the selected product is configured through that flow. The SDK evidence is `build/lite/README_zh.md`: run `hb set` to select the source root/product, then `hb build` from the OpenHarmony source root.
- Use `python build.py wifiiot` only for the legacy HiSpark/HiHope Vendor examples whose bundled README explicitly gives that command and whose checkout still contains the matching top-level `build.py` flow.
- For PZ-Hi3861, first verify `applications/sample/wifi-iot/app/BUILD.gn`, `vendor/pzkj/pz_hi3861/demo/BUILD.gn`, and the selected numbered demo's `BUILD.gn`; then use the build flow actually present in the user's checkout.
- Do not translate one flow into the other from memory. If neither command and its supporting files exist in the user's project, report the build command as unverified and inspect the product configuration.

## Fault isolation

- Undefined `hi_i2c_*`, `hi_spi_*`, or PWM symbols usually require checking the corresponding support switch and linked driver before changing application code.
- Missing headers/libraries require tracing the active GN target and include/dependency path.
- No serial output requires checking the entry macro, enabled demo, UART selection/baud, reset/boot state, and whether multiple apps compete.
- Bus timeouts require checking mux, pull-ups, address convention, clock, device power, and the first return code.
- ADC/PWM anomalies require checking channel-to-pin mapping, divider/reference formula, PWM channel mux, period/duty units, and pin conflicts.
- Wi-Fi/MQTT failures should be separated into association, DHCP/IP, DNS/socket, TLS/time/certificate, and application-protocol stages.

Use the snapshot's prebuilt GN/Ninja only as part of the SDK's documented build flow. A successful static index does not prove the host has the required RISC-V toolchain or flashing utility.

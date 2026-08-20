---
name: hi3861-dev-skill
description: Develop, configure, build, debug, and review HiSilicon Hi3861V100 OpenHarmony/LiteOS-M firmware. Use for PZ-Hi3861, HiSpark Pegasus/M1, BearPi-HM Nano, and FS-Hi3861 projects involving peripherals, RTOS, Wi-Fi/networking, MQTT/IoTDA, storage, OTA, security, or low power. Routes work to a self-contained SDK snapshot, public APIs, build configuration, and verified examples.
metadata:
  short-description: Hi3861V100 OpenHarmony firmware development
---

# Hi3861 Development

Use this skill for Hi3861V100 firmware and SDK work. Its knowledge base contains only the bundled SDK snapshot and indexes derived from that SDK. Default to PZ-Hi3861 only when the user's board or project does not identify another target.

## Route and Verify

1. Inspect the user's project first: board/vendor path, `BUILD.gn`, selected feature, `usr_config.mk`, entry macro, existing BSP, and pin assignments.
2. Read [references/sdk-map.md](references/sdk-map.md) to choose the relevant SDK layer and board tree.
3. Resolve this skill's directory from this `SKILL.md`, then run `<python> <skill-root>/scripts/query_index.py --topic <topic> --board <board>` for evidence paths. Add `--symbol <name>` when checking an API. Do not assume the user's current directory is the skill directory.
4. Read the relevant topic guide, then inspect the returned header, driver, example, and build configuration in `references/source/sdk/`.
5. Verify every API, enum, pin function, configuration symbol, target, and include path against the snapshot. If evidence is absent, say it is unverified instead of inventing it.

## Evidence Order

1. User project and its selected board configuration.
2. SDK public headers, implementation, and build files.
3. Example for the same board.
4. SDK-native Hi3861 demo or an example for another board, explicitly adapted for pin/BSP differences.
5. SDK-bundled documentation.

Do not use U-Boot or unrelated third-party examples as evidence for the Hi3861 application API merely because a topic name matches.

## Required Development Output

When creating or changing firmware, include all affected application source, `BUILD.gn` wiring, required `CONFIG_*` changes, pin mux/pull/direction setup, initialization order, return-code handling, and a hardware/serial verification procedure. Preserve the user's existing board and build selection.

Use `APP_FEATURE_INIT`, `SYS_RUN`, or another entry mechanism only after verifying the selected example/build model. Avoid enabling multiple PZ demo features that define competing application entry points.

## Topic References

- GPIO, interrupts, I2C/IIC, SPI, PWM, ADC, UART, I2S, timer, DMA, Flash/NV, watchdog: [references/peripherals.md](references/peripherals.md)
- Tasks, queues, semaphores, mutexes, events, timers, memory, interrupts: [references/liteos-kernel.md](references/liteos-kernel.md)
- Wi-Fi, TCP/UDP, HTTP, MQTT, CoAP, IoTDA, TLS: [references/networking-cloud.md](references/networking-cloud.md)
- File systems, partitions, OTA/boot, security, low power, AT commands: [references/platform-services.md](references/platform-services.md)
- PZ-Hi3861 defaults and cross-board adaptation: [references/boards.md](references/boards.md)
- Build, flash, and fault isolation: [references/build-debug.md](references/build-debug.md)

## Snapshot Maintenance

The snapshot is read-only evidence. Edit the user's project, not `references/source/sdk/`. To replace the snapshot explicitly, run:

`<python> <skill-root>/scripts/sync_sources.py --sdk-root <Hi3861-SDK-src>`

The synchronization stages the new snapshot, rebuilds its indexes, validates it, and rolls back on failure. For a separate check, run `<python> <skill-root>/scripts/validate_hi3861_skill.py`; add `--full-checksums` for a complete file-hash audit.

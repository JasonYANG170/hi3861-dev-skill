# Platform services

- File systems: inspect `hi_fs.h`, mounted backend configuration, SDK file-system guide, and existing mount/use examples before choosing paths or limits.
- Flash/NV/partitions: verify address, alignment, erase granularity, reserved areas, and partition table before writes.
- OTA/upgrade/boot: route through `hi_upg_api.h`, `hi_upg_file.h`, boot/upgrade source, signing/layout configuration, and bundled upgrade/boot documentation. Never change partitions or signing assumptions without project evidence.
- Security: use `hi_cipher.h`, `hi_efuse.h`, TLS/DTLS sources, random/clock prerequisites, and security documentation. Treat keys, eFuse writes, and flash encryption as irreversible or sensitive operations.
- Low power: use `hi_lowpower.h`, clock/wakeup configuration, peripheral suspend behavior, and the bundled low-power guide. Confirm wake sources and reinitialize peripherals as required by examples.
- AT commands: use `hi_at.h`, command registration examples, parser constraints, and bundled AT documentation.
- Diagnostics: use `hi_errno.h`, `hi_diag.h`, crash/blackbox/dumper APIs, map files, and serial logs. Decode the first failing return code and trace it to its owning module.

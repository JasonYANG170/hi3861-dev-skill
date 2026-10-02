[简体中文](README.md) | [English](README_en.md)

# hi3861-dev-skill

HiSilicon Hi3861V100 / OpenHarmony / LiteOS-M firmware development skill with Codex support. The repository includes a complete SDK snapshot and search indexes generated from it, supporting peripheral development, RTOS, networking, cloud integration, storage, upgrades, security, low power, builds, and debugging.

## Support range

- Default board: Puzhong PZ-Hi3861
- Other boards: HiSpark Pegasus/M1, BearPi-HM Nano, FS-Hi3861
- Peripherals: GPIO/interrupt, I2C/IIC, SPI, PWM, ADC, UART, I2S, Timer, DMA, Flash/NV, Watchdog
- LiteOS: tasks, queues, semaphores, mutexes, events, software timers, memory and interrupts
- Network and Cloud: Wi-Fi AP/STA, TCP/UDP, HTTP, MQTT, CoAP, IoTDA, TLS/DTLS
- Platform capabilities: file system, partition, OTA/Boot, security, low power consumption, AT commands and fault diagnosis

The current index covers 25,806 SDK files, 2,486 unique API symbols, and 191 runnable routines, including 43 numbered routines for PZ-Hi3861. The latest statistics are based on [`references/indexes/metadata.json`](references/indexes/metadata.json).

## Content boundaries

The knowledge base only contains the SDK raw content and its derived indexes, not external blogs, external CHMs, or additional extracted PDF text. The original license, NOTICE, documentation and directory structure within the SDK are retained.

Use the following evidence priorities when answering and generating code:

1. User project and actual board configuration
2. SDK public header files, source code and build files
3. Examples for the same board
4. Native SDK examples or examples for other boards (clearly describe adaptation differences)
5. Documentation included with the SDK

APIs, pins, or configurations for which no evidence of the SDK can be found are marked as "unverified" and are not fabricated based on common embedded experience.

## Installation

Clone the repository into the Codex Skills directory:

```powershell
git clone https://github.com/JasonYANG170/hi3861-dev-skill.git "$env:USERPROFILE\.codex\skills\hi3861-dev-skill"
```

Linux/macOS：

```bash
git clone https://github.com/JasonYANG170/hi3861-dev-skill.git ~/.codex/skills/hi3861-dev-skill
```

After reopening the Codex task, you can explicitly call:

```text
使用 $hi3861-dev-skill 为 PZ-Hi3861 编写一个 I2C 传感器程序
```

This Skill also allows automatic triggering based on Hi3861 development requests.

## Index query

The script relies only on the Python 3.9+ standard library. Run in the root directory of the repository:

```bash
python scripts/query_index.py --topic iic --board pz
python scripts/query_index.py --topic spi --symbol hi_spi_init
python scripts/query_index.py --topic adc --board bearpi
python scripts/query_index.py --topic liteos --json
```

The default query preferentially returns Hi3861 public API, native routines and target board routines, and hides noise only from U-Boot/third-party directories. Add `--include-third-party` when full third-party results need to be checked.

## Development output

When using this Skill to create or modify firmware, you should also provide:

- Application source files and entry functions
- `BUILD.gn` wiring
- Required `CONFIG_*` switch
- Pin multiplexing, pull-up and pull-down and direction configuration
- Initialization sequence and return value processing
- Compilation, serial port and hardware verification methods

The build command must be based on the actual structure of the project: standard OpenHarmony products usually use `hb set` / `hb build`, and some old HiSpark/HiHope routines use `python build.py wifiiot`.

## Update SDK snapshot

Explicitly specify the new Hi3861 SDK `src` root directory:

```bash
python scripts/sync_sources.py --sdk-root <Hi3861-SDK-src>
```

The sync script excludes `out`, `build_tmp`, object files, and caches, replaces snapshots with staging directories, rebuilds indexes, and performs verification; automatically rolls back on failure.

## Validation

```bash
python scripts/validate_hi3861_skill.py
python scripts/validate_hi3861_skill.py --full-checksums
```

The validator checks the SDK snapshot, index paths, public APIs, configuration, drivers/native examples, 43 PZ examples, topic coverage, and file checksums. This does not replace a firmware build; compiling firmware requires the matching Hi3861 RISC-V toolchain and flashing environment.

## Directory structure

```text
hi3861-dev-skill/
├── SKILL.md
├── agents/openai.yaml
├── scripts/
│   ├── query_index.py
│   ├── build_indexes.py
│   ├── sync_sources.py
│   └── validate_hi3861_skill.py
└── references/
    ├── indexes/
    ├── source/sdk/
    └── *.md
```

## License

The code, documentation and third-party components in the SDK image continue to be subject to their respective original licenses and NOTICEs. This repository retains these files and does not relicense the SDK or third-party content; please check the license terms in the corresponding directory before use and distribution.

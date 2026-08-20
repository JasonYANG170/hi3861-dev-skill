# SDK map and search strategy

The self-contained snapshot is at `references/source/sdk/`. It mirrors the supplied SDK `src` tree while excluding generated `out`, `build_tmp`, object files, and caches.

## Choose the evidence layer

- Application selection: `applications/sample/wifi-iot/app/BUILD.gn`.
- Board examples and BSPs: `vendor/pzkj/pz_hi3861`, `vendor/hihope/hispark_pegasus`, `vendor/hisilicon/hispark_M1`, `vendor/bearpi/bearpi_hm_nano`, and `vendor/hqyj/fs_hi3861`.
- Hi3861 public API: `device/hisilicon/hispark_pegasus/sdk_liteos/include/hi_*.h`.
- OpenHarmony IoT facade: `base/iot_hardware/peripheral/interfaces/kits/` and board HAL implementations.
- Hi3861 driver implementation and native tests: `device/hisilicon/hispark_pegasus/sdk_liteos/platform/drivers/` and `.../app/demo/`.
- LiteOS-M kernel: `kernel/liteos_m/` plus `hi_task.h`, `hi_sem.h`, `hi_mux.h`, `hi_event.h`, `hi_msg.h`, `hi_timer.h`, and `hi_mem.h`.
- Build configuration: `device/hisilicon/hispark_pegasus/sdk_liteos/build/config/usr_config.mk`, SCons files, GN product definitions, and Vendor `BUILD.gn` files.

## Indexes

- `indexes/api-symbols.json`: public Hi3861/OpenHarmony symbols with declaration paths and line numbers.
- `indexes/examples.json`: Vendor and SDK-native demos with board, topics, entry points, pins, symbols, and targets.
- `indexes/configs.json`: `CONFIG_*` occurrences.
- `indexes/documents.json`: SDK-bundled Markdown, text, PDF, and HTML documents.
- `indexes/source-manifest.json`: every mirrored file with size and SHA-256.

Use `query_index.py` before broad source searches. Use `rg` inside `references/source/sdk` when a data flow, call chain, register operation, or error code needs deeper tracing.

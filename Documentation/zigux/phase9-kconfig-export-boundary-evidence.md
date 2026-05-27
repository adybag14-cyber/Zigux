# Phase 9 Kconfig And Export Boundary Evidence

This note records the current cross-phase boundary that the Phase 9 runtime-pilot lanes should treat as supporting evidence only.

- `scripts/zigux/kconfig/conf_bridge.zig` keeps the current mode and flag bridge for `syncconfig`, `defconfig`, and the bounded allconfig sentinel family.
- `scripts/zigux/kconfig/confdata_bridge.zig` keeps the current config-file parsing bridge for `CONFIG_` keys, unset markers, quoted strings, line-normalization edge cases, and bounded symbol-export projections for `auto.conf` plus `autoconf.h`.
- `zigux/kernel/export_shim.zig` keeps the current direct Phase 3 export-boundary surface through `ExportStatus`, boundary-header validation, and interop-policy validation.
- `rust/exports.c` does not materialize on the trusted current-`master` direct-read path, so keep it as historical export-boundary vocabulary until direct rereads return it.

Exact current-read evidence behind those bullets:

- `conf_bridge.zig` currently exposes `Mode`, maps `.syncconfig` to `--syncconfig`, maps `.defconfig` to `--defconfig`, and still carries the `modeUsesAllConfigSentinel()` branch for the allconfig-only modes.
- `confdata_bridge.zig` currently sets `config_prefix = "CONFIG_"`, truncates lines at the first NUL byte, trims a leading UTF-8 BOM and trailing carriage return, parses `# CONFIG_FOO is not set`, classifies values as tristate, string, or plain value, and now exposes `emitAutoConfExports()` plus `emitAutoconfHeaderExports()` for bounded symbol-export projection replay.
- `export_shim.zig` currently re-exports `ExportStatus`, relays `validateBoundaryHeader()`, and relays `validateInteropPolicy()` as the direct Phase 3 boundary hooks that remain readable on current `master`.
- `rust/exports.c` returned `404 Not Found` on the trusted current-`master` direct-read path used for this verification pass.

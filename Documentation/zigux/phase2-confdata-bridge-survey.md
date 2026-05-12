# Phase 2 Confdata Bridge Survey

This note records the current `master` readback for the roadmap-backed `scripts/zigux/kconfig/confdata_bridge.zig` scaffold so Phase 2 review stays grounded in the live packet instead of reopening this lane as if the bridge were still missing.

## Roadmap Target

- Phase 2 keeps `scripts/kconfig/confdata.c` inside the bounded parser-heavy tooling tranche.
- The roadmap's recommended Zigux destination is `scripts/zigux/kconfig/confdata_bridge.zig` beside `scripts/zigux/kconfig/conf_bridge.zig`.
- The commit ledger's original bounded Phase 2 kconfig bridge scaffold likewise names `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, and the `zigux/tests/fixtures/kconfig_bridge/` packet as the intended bridge-local surface.

## Current Master Readback

- `scripts/zigux/kconfig/confdata_bridge.zig` is present on `master` and already ships a bounded `runConfdataBridge()` entrypoint plus a CLI `main()` wrapper that reads one config path and emits a JSON summary.
- `zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries an `confdata_cases` packet with 11 fixture cases: `sample`, `escaped_strings`, `escaped_control_sequences`, `trailing_escaped_backslash`, `sample_crlf`, `explicit_n_tristate`, `final_trailing_carriage_return`, `final_unterminated_unset_comment`, `uppercase_tristate`, `non_config_lines`, and `empty_config_symbol_names`.
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 11-case packet, and names the current helper-local anchor list for the bridge tests.
- `scripts/zigux/check-kconfig-bridge.py` already treats `confdata_bridge.zig`, `confdata_manifest.json`, and the shared `cases.json` packet as dedicated review surfaces, including exact-field checks for the confdata manifest and source-anchor comparison for the bridge-local helper tests.

## Survey Result

- `P2-L19` does not have a remaining roadmap gap at the level of bridge scaffolding. The scaffolded Zigux destination, the fixture packet, the manifest, and the dedicated checker are all already present on live `master`.
- The honest remaining work for this file family is smaller: keep the bridge, checker, and manifest truthful when one of those surfaces changes, and prefer focused validation or survey-note updates over creating more wrapper or scaffold files.
- Future reopening in this lane should only happen for a concrete bridge-local drift such as missing fixture coverage, manifest-anchor mismatch, checker truthfulness drift, or a bounded parser behavior hole inside `confdata_bridge.zig` itself.

## Next Bounded Step

- When a writable checkout and Zig toolchain are available, run `python3 scripts/zigux/check-kconfig-bridge.py --self-test`, `python3 scripts/zigux/check-kconfig-bridge.py`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig` together so the already-landed scaffold stays replay-validated as one packet.
- Until that direct replay is available, keep this lane parked unless current `master` shows a new confdata-bridge-local truthfulness drift.

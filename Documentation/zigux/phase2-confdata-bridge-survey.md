# Phase 2 Confdata Bridge Survey

This note records the current `master` readback for the roadmap-backed `scripts/zigux/kconfig/confdata_bridge.zig` bridge so Phase 2 review stays grounded in the live packet instead of reviving the older missing-scaffold story.

## Roadmap Target

- Phase 2 keeps `scripts/kconfig/confdata.c` inside the bounded parser-heavy tooling tranche.
- The roadmap's recommended Zigux destination is `scripts/zigux/kconfig/confdata_bridge.zig` beside `scripts/zigux/kconfig/conf_bridge.zig`.
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-readme-alignment.py`, `scripts/zigux/validate-phase2.py`, and `scripts/zigux/validate-phase2-closure.py` now keep the already-landed confdata bridge packet reviewable through the shared Phase 2 reminder surface instead of reviving the older dedicated `check-kconfig-bridge.py` scaffold claim.

## Current Master Readback

- `scripts/zigux/kconfig/confdata_bridge.zig` is present on `master` and already ships a bounded `runConfdataBridge()` entrypoint plus a CLI `main()` wrapper that reads one config path and emits a JSON summary.
- `zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries a `confdata_cases` packet with 12 fixture cases: `sample`, `escaped_strings`, `escaped_control_sequences`, `trailing_escaped_backslash`, `sample_crlf`, `explicit_n_tristate`, `final_trailing_carriage_return`, `final_unterminated_unset_comment`, `uppercase_tristate`, `non_config_lines`, `empty_config_symbol_names`, and `last_state_transitions`.
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 12-case packet, and names the current helper-local anchor list for the bridge tests.
- `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already describe the same shared kconfig packet and keep the bridge reviewable without inventing a standalone checker or direct bridge-only replay.

## Survey Result

- `current master` does not have a remaining roadmap gap at the level of confdata bridge scaffolding. The bridge, fixture packet, manifest, and shared checker-backed reminder surface are already present.
- The honest remaining work for this file family is smaller: keep the bridge, checker, and manifest truthful when one of those surfaces changes, and prefer focused validation or survey-note updates over creating more wrapper or scaffold files.
- Future reopening in this lane should only happen for a concrete bridge-local drift such as missing fixture coverage, manifest-anchor mismatch, reminder-surface drift, or a bounded parser behavior hole inside `confdata_bridge.zig` itself.

## Next Bounded Step

- When a writable checkout and Zig toolchain are available, run `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `python3 scripts/zigux/check-phase2-kconfig-readme-alignment.py --self-test`, and `python3 scripts/zigux/validate-phase2-closure.py` together so the already-landed bridge packet stays replay-validated through the shared Phase 2 reminder surface.
- Until that direct reminder-surface replay happens, keep this lane parked unless current `master` shows a new confdata-bridge-local truthfulness drift.

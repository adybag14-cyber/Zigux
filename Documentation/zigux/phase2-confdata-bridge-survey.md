# Phase 2 Confdata Bridge Survey

This note records the current `master` readback for the roadmap-backed `scripts/zigux/kconfig/confdata_bridge.zig` bridge so Phase 2 review stays grounded in the live packet instead of reviving the older missing-scaffold story.

## Roadmap Target

- Phase 2 keeps `scripts/kconfig/confdata.c` inside the bounded parser-heavy tooling tranche.
- The roadmap's recommended Zigux destination is `scripts/zigux/kconfig/confdata_bridge.zig` beside `scripts/zigux/kconfig/conf_bridge.zig`.
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-readme-alignment.py`, `scripts/zigux/validate-phase2.py`, and `scripts/zigux/validate-phase2-closure.py` now keep the already-landed confdata bridge packet reviewable through the shared Phase 2 reminder surface instead of reviving the older dedicated `check-kconfig-bridge.py` scaffold claim.

## Current Master Readback

- `scripts/zigux/kconfig/confdata_bridge.zig` is present on `master` and already ships a bounded `runConfdataBridge()` entrypoint plus a CLI `main()` wrapper that reads one config path and emits a JSON summary.
- `zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries a `confdata_cases` packet with 12 fixture cases: `sample`, `escaped_strings`, `escaped_control_sequences`, `trailing_escaped_backslash`, `sample_crlf`, `explicit_n_tristate`, `final_trailing_carriage_return`, `final_unterminated_unset_comment`, `uppercase_tristate`, `non_config_lines`, `empty_config_symbol_names`, and `last_state_transitions`.
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 12-case packet, and now names the later duplicate-malformed-quote helper anchor together with the rest of the current bridge test list.
- `scripts/zigux/check-kconfig-bridge.py` still carries the confdata bridge reminder packet, but its `REQUIRED_CONFDATA_HELPER_ANCHORS` list currently stops one anchor short of the live source and manifest and does not yet require `confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed`.
- `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already describe the same shared kconfig packet and keep the bridge reviewable without inventing a standalone checker or direct bridge-only replay.

## Survey Result

- `current master` does not have a remaining roadmap gap at the level of confdata bridge scaffolding. The bridge, fixture packet, manifest, and shared reminder surfaces are already present.
- The honest remaining work for this file family is now narrower than scaffolding: the checker's helper-anchor packet still trails the live `confdata_bridge.zig` source and `confdata_manifest.json` by one duplicate-malformed-quote anchor, so the packet should not be described as fully parked yet.
- Future reopening in this lane should stay note-local unless current `master` lands that exact checker-versus-source-manifest truthfulness repair; broader parser behavior work, new scaffold files, or wider Phase 2 closure rewrites would be the wrong follow-through from this evidence.

## Next Bounded Step

- Update `scripts/zigux/check-kconfig-bridge.py` so `REQUIRED_CONFDATA_HELPER_ANCHORS` matches the live helper-anchor list already present in `scripts/zigux/kconfig/confdata_bridge.zig` and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, then rerun `python3 scripts/zigux/check-kconfig-bridge.py --self-test` plus the full checker.
- Until that substantive bridge-local truthfulness repair lands, keep this survey note explicit about the remaining checker-anchor drift instead of treating the confdata bridge packet as fully parked.

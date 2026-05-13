# Phase 2 Confdata Bridge Survey

This note records the current `master` readback for the roadmap-backed `scripts/zigux/kconfig/confdata_bridge.zig` bridge so Phase 2 review stays grounded in the live packet instead of reviving the older missing-scaffold story.

## Roadmap Target

- Phase 2 keeps `scripts/kconfig/confdata.c` inside the bounded parser-heavy tooling tranche.
- The roadmap's recommended Zigux destination is `scripts/zigux/kconfig/confdata_bridge.zig` beside `scripts/zigux/kconfig/conf_bridge.zig`.
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-readme-alignment.py`, `scripts/zigux/validate-phase2.py`, and `scripts/zigux/validate-phase2-closure.py` now keep the already-landed confdata bridge packet reviewable through the shared Phase 2 reminder surface instead of reviving the older dedicated bridge-scaffold claim.

## Current Master Readback

- `scripts/zigux/kconfig/confdata_bridge.zig` is present on `master` and already ships a bounded `runConfdataBridge()` entrypoint plus a CLI `main()` wrapper that reads one config path and emits a JSON summary, alongside `20` helper-local tests covering the current bridge-local edge cases.
- `zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries a `confdata_cases` packet with 13 fixture cases: `sample`, `escaped_strings`, `escaped_control_sequences`, `trailing_escaped_backslash`, `sample_crlf`, `explicit_n_tristate`, `final_trailing_carriage_return`, `final_unterminated_unset_comment`, `uppercase_tristate`, `non_config_lines`, `empty_config_symbol_names`, `last_state_transitions`, and `duplicate_malformed_quoted_assignment`.
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 13-case packet, and names the current helper-local anchor list for the bridge tests.
- `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already describe the same shared kconfig packet and keep the bridge reviewable without inventing a standalone checker or direct bridge-only replay.

## Verified Behavior

- An attached `0.17.0-dev.87+9b177a7d2` Zig toolchain replay on `2026-05-13` confirmed that the live `confdata_bridge.zig` source still passes its current `20` helper-local tests.
- The same replay confirmed that `CONFIG_ALPHA="stable"` followed by a malformed duplicate quoted reassignment keeps the prior stable value while later entries in the same config continue to parse, yielding `{\"counts\":{\"set\":2,\"unset\":1},\"entries\":[{\"name\":\"CONFIG_ALPHA\",\"kind\":\"string\",\"value\":\"stable\"},{\"name\":\"CONFIG_DEBUG\",\"kind\":\"unset\",\"value\":\"n\"},{\"name\":\"CONFIG_BETA\",\"kind\":\"tristate\",\"value\":\"y\"}]}` for the bounded duplicate-malformed probe.
- The current bridge replay still matches the live helper-local expectations for quoted trailing-suffix truncation, standalone malformed quoted scalar handling, and malformed unset comments with extra tokens, so this lane did not widen into a source rewrite.
- The external fixture packet now carries the same duplicate-malformed quoted reassignment behavior as a committed `13-case` replay under the shared checker and manifest instead of leaving that edge case only in survey prose.

## Survey Result

- `current master` does not have a remaining roadmap gap at the level of confdata bridge scaffolding. The bridge, fixture packet, manifest, and shared reminder surfaces are already present.
- The honest remaining work for this file family is now narrower than scaffolding: keep the shared reminder surfaces aligned with the already-landed bridge packet instead of reviving the older dedicated checker narrative.
- Future reopening in this lane should stay note-local unless current `master` changes the committed confdata bridge packet again; broader parser behavior work, new scaffold files, or wider Phase 2 closure rewrites would be the wrong follow-through from this evidence.

## Next Bounded Step

- When a writable checkout and Zig toolchain are available, rerun `python3 scripts/zigux/check-kconfig-bridge.py --self-test`, the full `python3 scripts/zigux/check-kconfig-bridge.py` gate, and the shared Phase 2 closure validators against the now `13-case` confdata packet.
- Until a fresh replay lands, keep this survey note explicit about the live 13-case confdata packet, the verified duplicate-malformed behavior above, and the shared reminder surfaces that govern it instead of treating the bridge as a missing scaffold.

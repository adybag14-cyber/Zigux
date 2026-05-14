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
- Current `master` still also carries the earlier standalone malformed-first-quote behavior directly in `scripts/zigux/kconfig/confdata_bridge.zig`: the helper-local anchor `confdata bridge leaves malformed quoted values as raw scalar values` is still present in the source, the shared checker and `confdata_manifest.json` still require that same anchor, and the bridge still treats `CONFIG_BROKEN="unterminated` as a raw scalar entry instead of skipping the malformed first-seen assignment.
- Because the duplicate-malformed fixture already proves the parser can ignore a later malformed quoted reassignment without derailing later entries, the smallest honest reopening is one bridge-local malformed-first-quote correction plus the directly coupled anchor wording refresh, not a broad reminder-surface rewrite.

## Survey Result

- `current master` does not have a remaining roadmap gap at the level of confdata bridge scaffolding. The bridge, fixture packet, manifest, and shared reminder surfaces are already present.
- The honest remaining work for this file family is narrower than scaffolding but no longer just a generic replay rerun: current `master` still preserves a first-seen malformed quoted assignment as a raw scalar value while the same bridge already ignores a later malformed duplicate quoted assignment.
- Future reopening in this lane should stay inside `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, and `scripts/zigux/check-kconfig-bridge.py` for that malformed-first-quote correction and the coupled anchor rename only; broader parser behavior work, new scaffold files, or wider Phase 2 closure rewrites would be the wrong follow-through from this evidence.

## Next Bounded Step

- When a writable checkout and Zig toolchain are available, change the bridge so a first-seen malformed quoted assignment is ignored instead of emitted as a raw scalar value, rename the directly coupled helper-local anchor wording to match that behavior, then rerun `python3 scripts/zigux/check-kconfig-bridge.py --self-test`, `python3 scripts/zigux/check-kconfig-bridge.py`, and `zig test scripts/zigux/kconfig/confdata_bridge.zig`.
- Until that bridge-local correction lands, keep this survey note explicit that the live `13-case` external packet is closed, but that the remaining confdata-local next safe step is the bounded malformed-first-quote behavior repair rather than a wider closure-note rewrite.

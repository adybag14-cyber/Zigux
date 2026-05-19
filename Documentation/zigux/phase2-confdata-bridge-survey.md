# Phase 2 Confdata Bridge Survey

This note records the current `master` readback for the roadmap-backed `scripts/zigux/kconfig/confdata_bridge.zig` bridge so Phase 2 review stays grounded in the live packet instead of reviving older missing-scaffold or already-fixed behavior claims.

## Roadmap Target
- Phase 2 keeps `scripts/kconfig/confdata.c` inside the bounded parser-heavy tooling tranche.
- The roadmap's recommended Zigux destination is `scripts/zigux/kconfig/confdata_bridge.zig` beside `scripts/zigux/kconfig/conf_bridge.zig`.
- The current shared Phase 2 checker and reminder surfaces now keep the already-landed confdata bridge packet reviewable without relying on an older dedicated helper-anchor checker route that current `master` no longer ships.

## Current Master Readback
- `scripts/zigux/kconfig/confdata_bridge.zig` is present on `master` and ships a bounded `runConfdataBridge()` entrypoint plus a CLI `main()` wrapper that reads one config path and emits a JSON summary, alongside `23` helper-local tests covering the current bridge-local edge cases.
- `zigux/tests/fixtures/kconfig_bridge/cases.json` currently carries a `confdata_cases` packet with 14 fixture cases: `sample`, `escaped_strings`, `escaped_control_sequences`, `trailing_escaped_backslash`, `sample_crlf`, `explicit_n_tristate`, `final_trailing_carriage_return`, `final_unterminated_unset_comment`, `uppercase_tristate`, `non_config_lines`, `empty_config_symbol_names`, `malformed_unset_comment_tokens`, `last_state_transitions`, and `duplicate_malformed_quoted_assignment`.
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` is present, marks the tool `closed`, records the same 14-case packet, and names the current helper-local anchor list for the bridge tests.
- `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, together with `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, keep the bounded confdata bridge packet reviewable on current `master`. Together these reminder surfaces keep the bridge reviewable without implying any current-`master` confdata scaffolding surface is missing.

## Verified Behavior
- Current `master` still carries the helper-local anchor `confdata bridge ignores malformed quoted values like upstream confdata`, and the live parser continues to short-circuit malformed leading quoted assignments before they can fall through to raw scalar handling.
- The bounded duplicate-malformed probe remains explicit in both the bridge-local test packet and the external fixture packet: `CONFIG_ALPHA="stable"` followed by a malformed duplicate quoted reassignment keeps the prior stable value while later entries continue to parse, yielding `{"counts":{"set":2,"unset":1},"entries":[{"name":"CONFIG_ALPHA","kind":"string","value":"stable"},{"name":"CONFIG_DEBUG","kind":"unset","value":"n"},{"name":"CONFIG_BETA","kind":"tristate","value":"y"}]}`.
- Together, the live helper-local malformed-quote behavior and malformed-unset-comment coverage now have a shared `14`-case external packet behind them, so this file family no longer has a remaining evidence gap framed as a pending malformed-first-quote or malformed-unset fixture correction.

## Survey Result
- `current master` does not have a remaining roadmap gap at the level of confdata bridge scaffolding or reminder-surface evidence.
- The bridge, external fixture packet, manifest, and shared reminder surfaces already agree on the bounded current packet.
- The real gap this run reopened was note-local truthfulness only: the older survey wording had drifted behind current repo reality by naming a no-longer-shipped dedicated helper-anchor checker route and by restating the older 20-anchor and 13-case packet. This note now reflects the live `23`-anchor and `14`-case confdata packet plus the current shared checker surfaces.
- Future reopening in this lane should stay evidence-first: only revisit this note if a later `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/*`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, or `Documentation/zigux/phase2-closure.md` change lands without matching review evidence.

## Next Bounded Step
- When a writable checkout and Zig toolchain are available, rerun `python3 scripts/zigux/check-kconfig-bridge.py --self-test`, `python3 scripts/zigux/check-kconfig-bridge.py`, `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`, `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, and the direct `zig test scripts/zigux/kconfig/confdata_bridge.zig` replay against the current `14-case` confdata packet.
- Leave this survey parked unless one of the live confdata bridge packet surfaces drifts again.
- If it reopens, first reread `scripts/zigux/kconfig/confdata_bridge.zig`, `zigux/tests/fixtures/kconfig_bridge/cases.json`, `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`, `scripts/zigux/check-kconfig-bridge.py`, and `scripts/zigux/check-phase2-kconfig-selftest-alignment.py` together, then update evidence only for genuinely new bridge-local drift.

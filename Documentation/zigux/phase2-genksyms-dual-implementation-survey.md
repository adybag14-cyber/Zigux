# Phase 2 genksyms dual-implementation survey

Lane: `P2-L07`

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.
- The bootstrap ledger still records a bounded genksyms wrapper lane around `scripts/zigux/genksyms.zig` together with a dedicated checker and fixture-backed expected-output packet, so this family remains real product infrastructure rather than wrapper churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/genksyms.zig`, so the core dual-implementation helper is still present on head.
- The live helper still exposes the bounded bridge shape rather than a deeper parser rollout: request and command structs, explicit parse-failure variants for option handling, a sixteen-file reference cap, long-option resolution for `help`, `version`, `debug`, `warnings`, `quiet`, `dump`, `reference`, `dump-types`, and `preserve`, and JSON bridge rendering through `renderGenksymsBridge()`.
- The live helper still carries embedded Zig unit tests for short and long option parsing, version or help side effects, getopt-style error rendering, passthrough handling, and the sixteen-reference-file cap, so helper-local replay evidence remains materialized.
- Current `master` directly serves the bounded checker and expanded expected-output packet again: `scripts/zigux/check-genksyms-bridge.py`, `zigux/tests/fixtures/genksyms_bridge/cases.json`, `zigux/tests/fixtures/genksyms_bridge/help_expected.json`, `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`, `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`, `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`, `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`, `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`, `zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`, `zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`, `zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`, `zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json`, `zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`, `zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`, `zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`, and `zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json` are all readable on head.
- Current shared Phase 2 reminder surfaces also keep the genksyms packet explicit: `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/fixtures/phase2_tool_manifest.json` all still name the checker, fixture roster, or `phase2-genksyms` replay route.
- `scripts/zigux/check-phase2-genksyms-survey-alignment.py` now fail-closes the survey note against the current helper, checker, and survey-local fixture inventory while also requiring the workflow, make-wrapper, and validator companion packet to stay present, without widening into parser behavior or closure-note churn.
- The narrower repo-reality gap is still governance-shaped rather than an implementation absence: the dedicated checker and broader shared Phase 2 reminder packet still do not fail-close on every restored process-output fixture, and there is still no dedicated `zigux/tests/fixtures/genksyms_bridge/manifest.json`.

## Survey result

- The roadmap-backed genksyms helper is not missing: `scripts/zigux/genksyms.zig` remains directly readable on current `master`.
- The older survey wording that treated the checker, fixture roster, and shared Phase 2 reminder packet as missing is no longer truthful on current head.
- The truthful current genksyms packet is the helper, its embedded Zig tests, `scripts/zigux/check-genksyms-bridge.py`, the bridge-invocation fixtures in `cases.json` plus `minimal_expected.json`, `debug_reference_types_expected.json`, `long_options_expected.json`, `quiet_overrides_warning_expected.json`, and `positional_passthrough_expected.json`, the help fixture, the restored process-output fixtures for version and parse-failure behavior, the dedicated survey-alignment checker, and the shared Phase 2 closure and make-wrapper packet that still replays `phase2-genksyms`.
- Relative to the roadmap and ledger, the remaining same-family gap is now narrow and governance-shaped rather than an implementation absence: the tool-local survey can stay truthful about the full packet today, and the survey note itself now has a direct fail-closed wording-and-presence checker, but the dedicated bridge checker and shared reminder surfaces still need one bounded follow-through so those restored process-output fixtures are fail-closed and cataloged without widening beyond the genksyms family.

## Next bounded same-family step

1. Leave this survey parked unless a future reread finds another genksyms-local wording or inventory drift.
2. If the genksyms family reopens for expected-output governance rather than implementation, either teach `scripts/zigux/check-genksyms-bridge.py` to validate the restored process-output fixtures too, or add a dedicated `zigux/tests/fixtures/genksyms_bridge/manifest.json` that catalogs the full current packet.
3. Do not widen this survey follow-through into fixdep, kconfig bridge, or broader shared Phase 2 reminder maintenance unless current `master` first develops a new genksyms-local mismatch that the existing closure packet does not already cover.

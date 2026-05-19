# Phase 2 genksyms dual-implementation survey

Lane: `P2-L07`

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.
- The bootstrap ledger still records a bounded genksyms wrapper lane around `scripts/zigux/genksyms.zig` together with a dedicated checker and fixture-backed expected-output packet, so this family remains real product infrastructure rather than wrapper churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/genksyms.zig`, so the core dual-implementation helper is still present on head.
- The live helper still exposes the bounded bridge shape rather than a deeper parser rollout: request and command structs, explicit parse-failure variants for option handling, a sixteen-file reference cap, long-option resolution for `help`, `version`, `debug`, `warnings`, `quiet`, `dump`, `reference`, `dump-types`, and `preserve`, and JSON bridge rendering through `renderGenksymsBridge()`.
- The live helper also still carries embedded Zig unit tests for short and long option parsing, version or help side effects, getopt-style error rendering, passthrough handling, and the sixteen-reference-file cap, so some helper-local replay evidence survives even without the older external checker.
- Current `master` still directly serves `zigux/tests/fixtures/genksyms_bridge/help_expected.json`, so one expected-output artifact remains attached to the helper-local packet.
- Repeated direct reads on current `master` now return missing for `scripts/zigux/check-genksyms-bridge.py`, `zigux/tests/fixtures/genksyms_bridge/cases.json`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`, `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`, `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`, and `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`.
- Current shared Phase 2 reminder surfaces also no longer carry the older genksyms packet: `scripts/zigux/validate-phase2.py`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `scripts/zigux/README.md`, and `.github/workflows/zigux-bootstrap.yml` do not currently list a dedicated genksyms checker, fixture roster, or direct replay step.

## Survey result

- The roadmap-backed genksyms helper is not missing: `scripts/zigux/genksyms.zig` is still directly readable on current `master`.
- The repo gap versus the original bounded Phase 2 packet is narrower and more specific: the helper, its embedded Zig tests, and the surviving help fixture remain materialized, but the dedicated checker, broader fixture roster, and workflow-backed review packet are not currently present on head.
- The truthful current genksyms packet is therefore the helper, its embedded unit-test surface, `zigux/tests/fixtures/genksyms_bridge/help_expected.json`, and this survey note, not the older broader checker-and-fixture packet described by previous lane history.

## Next bounded same-family step

1. Leave this survey parked unless a future reread finds another genksyms-local wording or inventory drift.
2. If the genksyms family reopens for implementation rather than governance, keep the follow-through on one smallest same-family artifact: either re-materialize `scripts/zigux/check-genksyms-bridge.py` or restore one coherent `zigux/tests/fixtures/genksyms_bridge/` expected-output packet beside it.
3. Do not widen this survey follow-through into fixdep, kconfig bridge, or broader shared Phase 2 reminder maintenance unless current `master` first returns direct genksyms checker or fixture surfaces that need shared packet accounting.

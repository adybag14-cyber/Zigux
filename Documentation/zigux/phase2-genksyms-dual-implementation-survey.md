# Phase 2 genksyms dual-implementation survey

Lane: `P2-L07`

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/genksyms/genksyms.c` inside the bounded toolchain and Kbuild enablement tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.
- The bootstrap ledger still records a bounded genksyms wrapper lane around `scripts/zigux/genksyms.zig` together with a dedicated checker and fixture-backed expected-output packet, so this family remains real product infrastructure rather than wrapper churn.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/genksyms.zig`, so the core dual-implementation helper is still present on head.
- The live helper still exposes the bounded bridge shape rather than a deeper parser rollout: request and command structs, explicit parse-failure variants for option handling, a sixteen-file reference cap, long-option resolution for `help`, `version`, `debug`, `warnings`, `quiet`, `dump`, `reference`, `dump-types`, and `preserve`, and JSON bridge rendering through `renderGenksymsBridge()`.
- The live helper still carries embedded Zig unit tests for short and long option parsing, version or help side effects, getopt-style error rendering, empty inline `--reference=` and abbreviated `--dump-t=` argument preservation, passthrough handling, and the sixteen-reference-file cap, so helper-local replay evidence remains materialized.
- Current `master` directly serves the bounded checker, invocation-fixture packet, dedicated manifest, help fixture, and restored process-output packet again: `scripts/zigux/check-genksyms-bridge.py`, `zigux/tests/fixtures/genksyms_bridge/cases.json`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, `zigux/tests/fixtures/genksyms_bridge/help_expected.json`, `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`, `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`, `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`, `zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`, `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`, `zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`, `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`, `zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`, `zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`, `zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`, `zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`, `zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`, `zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`, `zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`, `zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json`, and `zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json` are all readable on head.
- Current shared Phase 2 reminder surfaces also keep the genksyms packet explicit: `Documentation/zigux/phase2-closure.md`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/tests/fixtures/phase2_tool_manifest.json` all still name the checker, fixture roster, or `phase2-genksyms` replay route.
- The narrower repo-reality gap that once lived at the checker layer is now closed on current `master`: the dedicated checker directly validates the manifest-backed bridge packet, the restored process-output fixtures, the help fixture, and the standalone invalid-long-option version-side-effect proof, while `scripts/zigux/check-phase2-genksyms-selftest-alignment.py` keeps that checker-owned packet tied back to the workflow and Makefile hooks.

## Survey result

- The roadmap-backed genksyms helper is not missing: `scripts/zigux/genksyms.zig` remains directly readable on current `master`.
- The truthful current genksyms packet is the helper, its embedded Zig tests, `scripts/zigux/check-genksyms-bridge.py`, the bridge-invocation fixtures in `cases.json`, the dedicated `manifest.json` catalog, the help fixture, the restored process-output fixtures, the standalone invalid-long-option version-side-effect proof, the dedicated genksyms selftest-alignment checker, the validator pair in `scripts/zigux/validate-phase2.py` and `scripts/zigux/validate-phase2-closure.py`, and the shared Phase 2 closure and make-wrapper packet that still replays `phase2-genksyms`.
- Relative to the roadmap and ledger, the older inventory-shaped governance gap is no longer truthful on current `master`; the live work is a bounded wrapper-first dual-implementation packet whose expected-output governance is already checker-owned, so the remaining same-family posture is to keep this survey parked unless another directly coupled reminder surface drifts.

## Next bounded same-family step

1. Leave this survey parked unless a future reread finds another genksyms-local wording, inventory, or replay drift.
2. If the family reopens for governance rather than implementation, keep the next move to one directly coupled reminder-surface refresh in the survey note, closure note, tests README, or validator wording that mismatches the already checker-owned manifest and process-output packet.

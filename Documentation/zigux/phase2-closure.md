# Phase 2 Closure

This note keeps the shared Phase 2 closure packet parked while making the current `genksyms` evidence and shared repo-tooling reminder surfaces explicit and replayable from directly readable `master` surfaces.

## Status

- `PHASE2_STATUS=parked`
- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`
- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`
- shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`

## Current Genksyms Evidence

- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md` remains the same-family roadmap and ledger truthfulness anchor for the wrapper-first `genksyms` lane.
- `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, and `scripts/zigux/genksyms.zig` remain the live checker, closure-alignment guard, and Zig bridge helper on current `master`.
- `scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py` remains the dedicated survey guard that keeps the wrapper-first bridge evidence, restored CRC-side tool-plus-checker evidence, and current closure packet explicit.
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `scripts/zigux/genksyms_inline_short_option_argument_test.zig`, `scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig`, and `scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig` remain the standalone proof packet carried by the shipped bridge route.
- `zigux/tests/fixtures/genksyms_bridge/manifest.json` remains the live packet manifest, and `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json` is now part of the directly named process-output fixture set instead of sitting only in the helper-local manifest.
- The bridge expected-output packet now explicitly records the eleven committed replay cases, including the dash-prefixed long and short option argument-as-data cases, so the closure note does not fall back to the older minimal/debug/long-options-only fixture shape.
- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- `python3 scripts/zigux/check-genksyms-bridge.py`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test`
- `python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py`
- `zig test scripts/zigux/genksyms.zig`
- `make -C zigux phase2-genksyms`
- `PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=zigux/tests/fixtures/genksyms_bridge/minimal_expected.json,zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json,zigux/tests/fixtures/genksyms_bridge/inline_short_option_arguments_expected.json,zigux/tests/fixtures/genksyms_bridge/long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json,zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json,zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`
- `PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`

## Current Shared Repo-Tooling Evidence

- `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-bootstrap-workflow-routes.py`, and `scripts/zigux/check-phase2-artifact-tools-manifest.py` keep the shared manifest, workflow-route, and artifact-support packet explicit from current `master`.
- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-phase2-cross.py`, `Documentation/zigux/phase2-fixdep-dual-implementation-survey.md`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py` keep the helper-local kconfig, direct cross-route, and fixdep governance/parity packet directly replayable beside the closure note.
- `Documentation/zigux/phase2-conf-bridge-survey.md` remains the dedicated conf bridge survey note for the live `conf_bridge.zig`, checker, fixture roster, manifest, and closure-reminder packet.
- `PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=4`
- `scripts/zigux/kconfig/confdata_bridge.zig`, `scripts/zigux/check-kconfig-bridge.py`, and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` keep the bounded `confdata.c` bridge replay packet directly readable at 16 committed fixture cases and 36 helper-local anchors.
- `PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=16`
- `PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=36`
- `scripts/zigux/artifact_diff.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json` remain the current artifact-support reminder pair instead of falling back into repo-reality-gap wording.
- `python3 scripts/zigux/check-phase2-tool-manifest.py`
- `python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py`
- `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
- `python3 scripts/zigux/check-phase2-cross.py`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- `python3 scripts/zigux/check-fixdep-diff.py`
- `make -C zigux phase2-fixdep`
- `PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py`

## Shared Replay Routes

- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`
- `PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`

## Repo-Reality Gaps

- `PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`
- current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`, so the shipped kconfig bridge packet remains fixture-backed rather than same-tree differential
- the next same-family truthfulness pass should keep reminder surfaces aligned with the live split recorded in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`: request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`, `allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`, and the helper-local explicit-override roster remains broader by design

## Next Step

Keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again. If the kconfig bridge lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step that preserves the live split between request-plan overrides, the non-empty sentinel packet, and helper-local explicit-override coverage, then add a direct `conf.c` / `confdata.c` provenance anchor once those C sources are readable in-tree again on current `master`. If the `genksyms` lane resumes substantive implementation instead of closure upkeep, start with one smallest same-family step that preserves the restored CRC-side evidence and wrapper bridge packet before widening this shared note again.

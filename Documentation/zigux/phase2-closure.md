# Phase 2 Closure

This note keeps the current Phase 2 closure-side packet aligned to the directly readable toolchain, local-first archive, archive-verification, staged-archive helper, installer, cross-route, bootstrap-workflow-routes, kconfig-bridge, helper-local allconfig guard, genksyms bridge, fixdep, make-wrapper, manifest-guard, artifact-diff helper, and validator surfaces on current `master`.

## Status

- `PHASE2_STATUS=parked`
- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`
- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`
- current authority: this closure note, the committed Phase 2 tool manifest, the toolchain bootstrap note, the live toolchain, local-first archive, archive-verification, staged-archive helper, installer, cross-route, bootstrap workflow-route, reminder, pinning, manifest, artifact helper, fixdep guards, the helper-local kconfig allconfig guard, the returned closure-side validator pair, the shipped `zigux/Makefile` wrappers, and the current kconfig, genksyms, fixdep, artifact-support, plus cross-route fixture manifests remain the trustworthy current-master sources for the bounded Phase 2 tranche

The bounded Phase 2 tranche remains the directly readable toolchain, local-first archive, archive-verification, staged repo-local archive helper contract and selftest packet, installer, direct cross-route, bootstrap workflow-route guard, selected kconfig-bridge plus helper-local allconfig guard, bounded genksyms bridge, direct standalone genksyms invalid-long-option and ambiguous-long-option version-side-effect proofs, fixdep, required-make-route, validator-entrypoint, closure-validator, and fixture-backed artifact-support packet already present on current `master`.

## Current Closure Packet

The currently reviewable Phase 2 closure packet is:

- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-lane05-local-first-archive-workflow.py`
- `scripts/zigux/check-lane05-local-archive-readme.py`
- `scripts/zigux/check-lane05-install-zig-archive-verification.py`
- `scripts/zigux/stage-pinned-zig-archive.py`
- `scripts/zigux/check-lane05-stage-helper-contract.py`
- `scripts/zigux/check-lane05-stage-helper-selftest.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-kconfig-bridge.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-bootstrap-workflow-routes.py`
- `scripts/zigux/check-phase2-tool-manifest.py`
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `scripts/zigux/artifact_diff.py`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `scripts/zigux/check-phase2-fixdep-gate.py`
- `scripts/zigux/check-fixdep-diff.py`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/zig-toolchain-policy.json`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`
- `scripts/zigux/fixdep.zig`
- `third_party/README.md`
- `zigux/Makefile`
- `zigux/tests/README.md`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/fixdep/cases.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`

- `PHASE2_CURRENT_CLOSURE_PACKET=Documentation/zigux/phase2-closure.md,Documentation/zigux/phase2-genksyms-dual-implementation-survey.md,Documentation/zigux/phase2-toolchain-bootstrap-notes.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/install-zig.py,scripts/zigux/check-zig-toolchain.py,scripts/zigux/check-lane05-local-first-archive-workflow.py,scripts/zigux/check-lane05-local-archive-readme.py,scripts/zigux/check-lane05-install-zig-archive-verification.py,scripts/zigux/stage-pinned-zig-archive.py,scripts/zigux/check-lane05-stage-helper-contract.py,scripts/zigux/check-lane05-stage-helper-selftest.py,scripts/zigux/check-phase2-kbuild-routes.py,scripts/zigux/check-kconfig-bridge.py,scripts/zigux/check-phase2-kconfig-selftest-alignment.py,scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,scripts/zigux/check-phase2-tests-readme-alignment.py,scripts/zigux/check-phase2-cross.py,scripts/zigux/check-phase2-cross-selftest-alignment.py,scripts/zigux/check-phase2-toolchain-pinning.py,scripts/zigux/check-phase2-toolchain-pin-scope.py,scripts/zigux/check-phase2-required-make-routes.py,scripts/zigux/check-phase2-docs-shared-reminder.py,scripts/zigux/check-phase2-bootstrap-workflow-routes.py,scripts/zigux/check-phase2-tool-manifest.py,scripts/zigux/check-phase2-artifact-tools-manifest.py,scripts/zigux/artifact_diff.py,scripts/zigux/check-genksyms-bridge.py,scripts/zigux/check-phase2-genksyms-selftest-alignment.py,scripts/zigux/check-phase2-fixdep-gate.py,scripts/zigux/check-fixdep-diff.py,scripts/zigux/validate-phase2.py,scripts/zigux/validate-phase2-closure.py,scripts/zigux/zig-toolchain-policy.json,scripts/zigux/kconfig/conf_bridge.zig,scripts/zigux/kconfig/confdata_bridge.zig,scripts/zigux/genksyms.zig,scripts/zigux/genksyms_version_before_invalid_long_option_test.zig,scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig,scripts/zigux/fixdep.zig,third_party/README.md,zigux/Makefile,zigux/tests/README.md,zigux/tests/fixtures/phase2_tool_manifest.json,zigux/tests/fixtures/phase2_artifact_tools_manifest.json,zigux/tests/fixtures/phase2_cross_targets.json,zigux/tests/fixtures/fixdep/cases.json,zigux/tests/fixtures/kconfig_bridge/conf_manifest.json,zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json,zigux/tests/fixtures/kconfig_bridge/cases.json,zigux/tests/fixtures/genksyms_bridge/cases.json,zigux/tests/fixtures/genksyms_bridge/manifest.json,zigux/tests/fixtures/genksyms_bridge/help_expected.json,zigux/tests/fixtures/genksyms_bridge/minimal_expected.json,zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json,zigux/tests/fixtures/genksyms_bridge/long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json,zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json,zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`
- `PHASE2_KCONFIG_BRIDGE_CONF_HELPER_ANCHOR_COUNT=28`
- `PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=15`
- `PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=28`

## Current Repo-Reality Gaps

Within the bounded Phase 2 closure packet, current `master` no longer leaves the local-first archive pair, returned archive-verification and staged-archive helper packet, installer hook, direct cross-route packet, bootstrap workflow-route guard, returned closure-validator companions, primary artifact helper, fixdep checker packet, helper-local kconfig allconfig guard, or fixture-backed manifest guards in the repo-reality-gap bucket.

The current closure-side packet keeps the returned archive-verification and staged repo-local archive helper packet explicit through `scripts/zigux/check-lane05-install-zig-archive-verification.py`, `scripts/zigux/stage-pinned-zig-archive.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, `scripts/zigux/check-lane05-stage-helper-selftest.py`, `scripts/zigux/install-zig.py`, `third_party/README.md`, and `make -C zigux phase2-toolchain`, keeps the bootstrap workflow-route guard explicit through `scripts/zigux/check-phase2-bootstrap-workflow-routes.py`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `make -C zigux phase2`, keeps the helper-local kconfig allconfig guard explicit through `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/kconfig/conf_bridge.zig`, and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`, keeps the artifact-support helper packet explicit through `scripts/zigux/check-phase2-artifact-tools-manifest.py`, `scripts/zigux/artifact_diff.py`, `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`, `scripts/zigux/check-kconfig-bridge.py`, `scripts/zigux/check-fixdep-diff.py`, and `make -C zigux phase2-tools`, keeps the fixdep governance and parity checker pair explicit through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`, keeps the bounded genksyms closure evidence explicit through `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`, `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`, `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, the restored process-output fixture packet, the returned dash-prefixed long-option-arguments-as-data and dash-prefixed short-option-arguments-as-data expected-output fixtures, `zig test scripts/zigux/genksyms.zig`, and `make -C zigux phase2-genksyms`, and keeps same-lane follow-through tied to the toolchain, local-first archive, archive-verification, staged-archive helper, cross-route, bootstrap workflow-route, kconfig, manifest-guard, helper-local allconfig guard, artifact-support, genksyms, make-wrapper, fixdep, and validator packet that the repo still ships directly.

- `PHASE2_CURRENT_GAP_PACKET=`

The current closure-side packet now stays anchored to the materialized closure note, validator entrypoint, closure validator, toolchain policy, returned local-first archive pair, returned archive-verification checker, returned staged repo-local archive helper contract and selftest pair, returned installer helper, direct cross-route checker, bootstrap workflow-route guard, shared reminder guards, current manifest guards, the helper-local kconfig allconfig guard, selected kconfig bridge checker plus the direct `conf_bridge` and `confdata_bridge` Zig unit replays, the bounded genksyms bridge checker, the dedicated genksyms selftest-alignment checker, direct genksyms Zig unit replay, standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, restored process-output fixture packet, returned dash-prefixed long-option-arguments-as-data and dash-prefixed short-option-arguments-as-data expected-output fixtures, the primary artifact helper plus artifact-support manifest guard and fixture catalog, the fixdep checker pair and fixture roster, current manifests, and shipped make-wrapper routes that current `master` can honestly support.

## Closure Validation

The current closure packet is intentionally narrow and replayable, and it now names the policy-only, archive-integrity, local-first archive, returned archive-verification and staged repo-local archive helper companions, returned installer and cross-route companions, bootstrap workflow-route guard, current manifest guards, the helper-local kconfig allconfig guard, direct kconfig bridge checker plus direct `conf_bridge` and `confdata_bridge` Zig unit replays, bounded genksyms bridge checker, dedicated genksyms selftest-alignment checker, direct genksyms Zig unit replay, standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, returned dash-prefixed long-option-arguments-as-data and dash-prefixed short-option-arguments-as-data expected-output fixtures, the primary artifact helper plus artifact-support manifest guard, fixdep checker pair, required-make-route guard, docs-shared reminder, restored closure-side validator, and shipped wrapper routes that current `master` can actually replay:

- `python3 scripts/zigux/check-zig-toolchain.py --self-test`
- `python3 scripts/zigux/check-zig-toolchain.py --policy-only`
- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
- `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`
- `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`
- `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`
- `python3 scripts/zigux/check-lane05-local-archive-readme.py`
- `python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test`
- `python3 scripts/zigux/check-lane05-install-zig-archive-verification.py`
- `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`
- `python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test`
- `python3 scripts/zigux/check-lane05-stage-helper-contract.py`
- `python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test`
- `python3 scripts/zigux/check-lane05-stage-helper-selftest.py`
- `python3 scripts/zigux/install-zig.py --self-test`
- `python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test`
- `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- `python3 scripts/zigux/check-kconfig-bridge.py`
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test`
- `python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
- `zig test scripts/zigux/kconfig/conf_bridge.zig`
- `zig test scripts/zigux/kconfig/confdata_bridge.zig`
- `python3 scripts/zigux/check-phase2-cross.py --self-test`
- `python3 scripts/zigux/check-phase2-cross.py`
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test`
- `python3 scripts/zigux/check-phase2-docs-shared-reminder.py`
- `python3 scripts/zigux/check-phase2-required-make-routes.py --self-test`
- `python3 scripts/zigux/check-phase2-required-make-routes.py`
- `python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test`
- `python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py`
- `python3 scripts/zigux/check-phase2-tool-manifest.py --self-test`
- `python3 scripts/zigux/check-phase2-tool-manifest.py`
- `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`
- `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- `python3 scripts/zigux/check-genksyms-bridge.py`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `zig test scripts/zigux/genksyms.zig`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- `python3 scripts/zigux/check-fixdep-diff.py`
- `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-tests-readme-alignment.py`
- `python3 scripts/zigux/validate-phase2.py`
- `python3 scripts/zigux/validate-phase2-closure.py --self-test`
- `python3 scripts/zigux/validate-phase2-closure.py`
- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-tools`
- `make -C zigux phase2-kconfig`
- `make -C zigux phase2-cross`
- `make -C zigux phase2-genksyms`
- `make -C zigux phase2-fixdep`
- `make -C zigux phase2-validate`
- `make -C zigux phase2`

- `PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/check-zig-toolchain.py --self-test,python3 scripts/zigux/check-zig-toolchain.py --policy-only,python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing,python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test,python3 scripts/zigux/check-lane05-local-first-archive-workflow.py,python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test,python3 scripts/zigux/check-lane05-local-archive-readme.py,python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test,python3 scripts/zigux/check-lane05-install-zig-archive-verification.py,python3 scripts/zigux/stage-pinned-zig-archive.py --self-test,python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test,python3 scripts/zigux/check-lane05-stage-helper-contract.py,python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test,python3 scripts/zigux/check-lane05-stage-helper-selftest.py,python3 scripts/zigux/install-zig.py --self-test,python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test,python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test,python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test,python3 scripts/zigux/check-kconfig-bridge.py --self-test,python3 scripts/zigux/check-kconfig-bridge.py,python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test,python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,zig test scripts/zigux/kconfig/conf_bridge.zig,zig test scripts/zigux/kconfig/confdata_bridge.zig,python3 scripts/zigux/check-phase2-cross.py --self-test,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test,python3 scripts/zigux/check-phase2-cross-selftest-alignment.py,python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test,python3 scripts/zigux/check-phase2-docs-shared-reminder.py,python3 scripts/zigux/check-phase2-required-make-routes.py --self-test,python3 scripts/zigux/check-phase2-required-make-routes.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py --self-test,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-tool-manifest.py --self-test,python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-genksyms-bridge.py --self-test,python3 scripts/zigux/check-genksyms-bridge.py,python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test,python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py,zig test scripts/zigux/genksyms.zig,python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py --self-test,python3 scripts/zigux/check-fixdep-diff.py,python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test,python3 scripts/zigux/check-phase2-tests-readme-alignment.py,python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py --self-test,python3 scripts/zigux/validate-phase2-closure.py`
- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`

## Next Step

The next bounded same-lane follow-through is to keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again. If current `master` reopens the shared backlog first, start with one smallest truthfulness repair in `Documentation/zigux/README.md`, `zigux/tests/README.md`, or the directly coupled shared checker that proves the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes instead of sending this shared packet back through the already-covered toolchain-pinning-versus-`phase2-fixdep` comparison.

- `PHASE2_NEXT_SAFE_STEP=keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again; if the shared backlog reopens first, start with one smallest truthfulness repair in Documentation/zigux/README.md, zigux/tests/README.md, or the directly coupled shared checker that proves the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes`
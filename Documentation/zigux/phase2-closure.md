# Phase 2 Closure

This note keeps the current Phase 2 closure-side packet aligned to the directly readable toolchain, installer, cross-route, kconfig-bridge, genksyms bridge, fixdep, make-wrapper, manifest-guard, and validator surfaces on current `master`.

## Status

- `PHASE2_STATUS=parked`
- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`
- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`
- current authority: this closure note, the committed Phase 2 tool manifest, the toolchain bootstrap note, the live toolchain, installer, cross-route, reminder, pinning, manifest, and fixdep guards, the returned closure-side validator pair, the shipped `zigux/Makefile` wrappers, and the current kconfig, genksyms, fixdep, plus cross-route fixture manifests remain the trustworthy current-master sources for the bounded Phase 2 tranche

The bounded Phase 2 tranche remains the directly readable toolchain, installer, direct cross-route, selected kconfig-bridge, bounded genksyms bridge, fixdep, required-make-route, validator-entrypoint, closure-validator, and fixture-backed artifact-support packet already present on current `master`.

## Current Closure Packet

The currently reviewable Phase 2 closure packet is:

- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-kconfig-bridge.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-tool-manifest.py`
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-fixdep-gate.py`
- `scripts/zigux/check-fixdep-diff.py`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/zig-toolchain-policy.json`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/fixdep.zig`
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
- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`

- `PHASE2_CURRENT_CLOSURE_PACKET=Documentation/zigux/phase2-closure.md,Documentation/zigux/phase2-toolchain-bootstrap-notes.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/install-zig.py,scripts/zigux/check-zig-toolchain.py,scripts/zigux/check-phase2-kbuild-routes.py,scripts/zigux/check-kconfig-bridge.py,scripts/zigux/check-phase2-kconfig-selftest-alignment.py,scripts/zigux/check-phase2-tests-readme-alignment.py,scripts/zigux/check-phase2-cross.py,scripts/zigux/check-phase2-cross-selftest-alignment.py,scripts/zigux/check-phase2-toolchain-pinning.py,scripts/zigux/check-phase2-toolchain-pin-scope.py,scripts/zigux/check-phase2-required-make-routes.py,scripts/zigux/check-phase2-docs-shared-reminder.py,scripts/zigux/check-phase2-tool-manifest.py,scripts/zigux/check-phase2-artifact-tools-manifest.py,scripts/zigux/check-genksyms-bridge.py,scripts/zigux/check-phase2-fixdep-gate.py,scripts/zigux/check-fixdep-diff.py,scripts/zigux/validate-phase2.py,scripts/zigux/validate-phase2-closure.py,scripts/zigux/zig-toolchain-policy.json,scripts/zigux/kconfig/conf_bridge.zig,scripts/zigux/kconfig/confdata_bridge.zig,scripts/zigux/genksyms.zig,scripts/zigux/fixdep.zig,zigux/Makefile,zigux/tests/README.md,zigux/tests/fixtures/phase2_tool_manifest.json,zigux/tests/fixtures/phase2_artifact_tools_manifest.json,zigux/tests/fixtures/phase2_cross_targets.json,zigux/tests/fixtures/fixdep/cases.json,zigux/tests/fixtures/kconfig_bridge/conf_manifest.json,zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json,zigux/tests/fixtures/kconfig_bridge/cases.json,zigux/tests/fixtures/genksyms_bridge/cases.json,zigux/tests/fixtures/genksyms_bridge/help_expected.json,zigux/tests/fixtures/genksyms_bridge/minimal_expected.json,zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json,zigux/tests/fixtures/genksyms_bridge/long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json,zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`

## Current Repo-Reality Gaps

Within the bounded Phase 2 closure packet, current `master` no longer leaves the installer hook, direct cross-route packet, returned closure-validator companions, fixdep checker packet, or fixture-backed manifest guards in the repo-reality-gap bucket.

The current closure-side packet keeps the fixdep governance and parity checker pair explicit through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`, so same-lane follow-through should stay tied to the toolchain, cross-route, kconfig, manifest-guard, genksyms, make-wrapper, fixdep, and validator packet that the repo still ships directly.

- `PHASE2_CURRENT_GAP_PACKET=`

The current closure-side packet now stays anchored to the materialized closure note, validator entrypoint, closure validator, toolchain policy, returned installer helper, direct cross-route checker, shared reminder guards, current manifest guards, selected kconfig bridge checker and helpers, the bounded genksyms bridge checker and fixture roster, the fixdep checker pair and fixture roster, current manifests, and shipped make-wrapper routes that current `master` can honestly support.

## Closure Validation

The current closure packet is intentionally narrow and replayable, and it now names the policy-only, archive-integrity, returned installer and cross-route companions, current manifest guards, direct kconfig bridge checker, bounded genksyms bridge checker, fixdep checker pair, required-make-route guard, docs-shared reminder, restored closure-side validator, and shipped wrapper routes that current `master` can actually replay:

- `python3 scripts/zigux/check-zig-toolchain.py --self-test`
- `python3 scripts/zigux/check-zig-toolchain.py --policy-only`
- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
- `python3 scripts/zigux/install-zig.py --self-test`
- `python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test`
- `python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test`
- `python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test`
- `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- `python3 scripts/zigux/check-kconfig-bridge.py`
- `python3 scripts/zigux/check-phase2-cross.py --self-test`
- `python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test`
- `python3 scripts/zigux/check-phase2-required-make-routes.py --self-test`
- `python3 scripts/zigux/check-phase2-tool-manifest.py --self-test`
- `python3 scripts/zigux/check-phase2-tool-manifest.py`
- `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`
- `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- `python3 scripts/zigux/check-genksyms-bridge.py`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- `python3 scripts/zigux/check-fixdep-diff.py`
- `python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test`
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

- `PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/check-zig-toolchain.py --self-test,python3 scripts/zigux/check-zig-toolchain.py --policy-only,python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing,python3 scripts/zigux/install-zig.py --self-test,python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test,python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test,python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test,python3 scripts/zigux/check-kconfig-bridge.py --self-test,python3 scripts/zigux/check-kconfig-bridge.py,python3 scripts/zigux/check-phase2-cross.py --self-test,python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test,python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test,python3 scripts/zigux/check-phase2-required-make-routes.py --self-test,python3 scripts/zigux/check-phase2-tool-manifest.py --self-test,python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-genksyms-bridge.py --self-test,python3 scripts/zigux/check-genksyms-bridge.py,python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py --self-test,python3 scripts/zigux/check-fixdep-diff.py,python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test,python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py --self-test,python3 scripts/zigux/validate-phase2-closure.py`
- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`

## Next Step

The next bounded same-lane follow-through is to compare `scripts/zigux/check-phase2-toolchain-pinning.py` against the current Phase 2 tool manifest and shipped `phase2-fixdep` wrapper so the toolchain-pinning checker stays exact beside the now-restored closure-side fixdep packet, before widening Phase 2 follow-through beyond the parked closure packet.

- `PHASE2_NEXT_SAFE_STEP=compare scripts/zigux/check-phase2-toolchain-pinning.py against the current Phase 2 tool manifest and shipped phase2-fixdep wrapper so the checker stays exact beside the restored closure-side fixdep packet before widening Phase 2 follow-through beyond the parked closure packet`

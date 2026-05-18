# Phase 2 Scripts Surface Reconciliation

This note records the current Phase 2 scripts-root reconciliation gap that remains visible on `master`.

## Directly readable scripts-root anchors

- `scripts/zigux/README.md`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-docs-shared-reminder.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-required-make-routes.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/Makefile`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`

Treat those as the current directly readable Phase 2 scripts-root anchors on `master`.

## Remaining repo-reality gaps

- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`

Treat those paths as the remaining repo-reality gaps on current `master`, not as shipped Phase 2 scripts-root evidence.

## Current reminder drift

- `scripts/zigux/README.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, and `zigux/tests/fixtures/phase2_tool_manifest.json` still classify `scripts/zigux/validate-phase2-closure.py` as a missing validator-first companion even though current `master` now directly serves that file.
- `Documentation/zigux/phase2-closure.md` and `zigux/Makefile` already use `scripts/zigux/validate-phase2-closure.py` as a live closure-side validator entrypoint through `python3 scripts/zigux/validate-phase2-closure.py --self-test`, `python3 scripts/zigux/validate-phase2-closure.py`, and `make -C zigux phase2-validate`.
- Keep this scripts-surface sidecar focused on that reopened reminder drift until the scripts-root, bootstrap-note, and manifest-root surfaces catch up to the restored closure validator.
- Do not treat the remaining installer or direct cross-route companions as returned until current `master` materializes them.

## Lane 25 boundary

Lane 25 should use this note and its checker to keep the restored closure validator visible as current scripts-root evidence while the remaining reminder surfaces close the narrower truthfulness gap on their own review paths.

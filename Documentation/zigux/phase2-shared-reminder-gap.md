# Phase 2 Shared Reminder Gap

This note records the remaining shared-surface Phase 2 drift on current `master` after the scripts-root and tests-root reminder packet was reread.

## Remaining same-lane drift

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`

Those two shared reminder surfaces still overstate the older Phase 2 closure-side, validator-first, toolchain-replay, cross-route, and Linux-style make-wrapper packet.

## Current directly readable packet

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `zigux/tests/README.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase2-kbuild-routes.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pinning.py`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`

Treat that set as the current directly readable shared Phase 2 packet on `master`.

## Historical packet members

- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/Makefile`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-zig-toolchain.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-validate`
- `make -C zigux phase2-tools`
- `make -C zigux phase2-kconfig`
- `make -C zigux phase2-cross`
- `make -C zigux phase2`

Treat those closure-side, validator-first, toolchain-replay, cross-route, and make-wrapper names as historical packet members until a fresh reread proves they returned on current `master`.

## Guard

- `scripts/zigux/check-phase2-docs-shared-reminder.py`

That checker is the dedicated fail-closed guard for the eventual `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` replay.

## Close condition

Lane 25 closes when `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` all describe the same current directly readable packet and the same historical packet members, and `scripts/zigux/check-phase2-docs-shared-reminder.py` passes against the refreshed docs-root and checklist pair.

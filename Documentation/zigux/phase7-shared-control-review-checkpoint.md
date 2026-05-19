# Phase 7 Shared Control Review Checkpoint

This note keeps the current Phase 7 shared-control packet reviewable at the docs root without reviving the older shared build and make-wrapper routes that current `master` no longer materializes.

## Current Packet

- The current shared-control reminder packet is carried by `Documentation/zigux/phase7-helper-lane-sequencing.md`, `Documentation/zigux/phase7-shared-control-review-checkpoint.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/check-phase7-shared-control-gap.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `.github/workflows/zigux-bootstrap.yml`, and the readable non-owner `zigux/Makefile`.
- Keep the shared-control packet focused on reminder, checker, and workflow truthfulness only. The helper-local `argv_split`, `cmdline`, `rbtree`, and `string_helpers` packets remain separate owners for direct helper behavior and survey drift.

## Parked Reminders

- Keep `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/validate-phase7.py`, and `zigux/tests/phase7_build.zig` framed as parked reminder vocabulary until a fresh current-`master` reread proves those paths returned.
- Keep `phase7-validate`, `phase7-test`, and `phase7` framed as absent wrapper-route vocabulary while the readable `zigux/Makefile` still omits those routes on current `master`.

## Review Prompt

- Before treating a shared Phase 7 build, wrapper, workflow, docs-root, scripts-root, tests-root, or sample-root change as current proof, reread the shared-control packet together and confirm it still describes the current tree more truthfully than the older parked route names do.

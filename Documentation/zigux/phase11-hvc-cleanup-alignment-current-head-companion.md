# Phase 11 HVC Cleanup Alignment Current-Head Companion

This note records the bounded current-head readback for the Phase 11 HVC cleanup-alignment packet.

## Status

- `PHASE11_STATUS=current_head_companion_landed`
- `PHASE11_FAMILY=hvc-console-cleanup-alignment`
- `PHASE11_SURFACE=checker-truthfulness-readback`
- `PHASE11_PROVENANCE_MODE=dated_master_readback`
- surveyed against current `master` readback on `2026-05-16`
- scope: document the live checker drift inside `scripts/zigux/check-phase11-hvc-cleanup-alignment.py` while keeping notifier callback execution, khvcd execution, tty registration, sysrq execution, watchdog-core glue, and host-backed teardown out of scope
- role: current-head truthfulness companion for the bounded Phase 11 HVC teardown and failure-mode packet until the checker can be realigned in one coupled pass

## Why this companion exists

The Phase 11 roadmap still keeps simple-driver progress inside bounded teardown and failure-mode review surfaces before riskier integration work. Current `master` already carries a richer HVC archival packet than the cleanup-alignment checker now describes.

The smallest honest same-lane follow-up in this environment is therefore not to guess at a whole-file checker rewrite, but to publish one current-head companion that records the drift clearly and keeps the next safe fix scoped to the existing HVC packet.

## Current Repo Reality

Current `master` now shows the bounded HVC packet through these live surfaces:

- `drivers/tty/hvc/hvc_console.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `drivers/tty/hvc/hvc_console_sysrq.zig`
- `zigux/tests/phase11_hvc_console.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`

Those current-head surfaces already keep the direct sysrq helper, the direct verify and cleanup companions, the exported-helper signature proof, and the bounded teardown packet reviewable without claiming live tty-driver registration, notifier callbacks, khvcd execution, live sysrq execution, or host-backed teardown parity.

## Drift Kept Explicit

Current `master` readback shows `scripts/zigux/check-phase11-hvc-cleanup-alignment.py` still encodes an older HVC packet shape in three concrete ways:

- `REQUIRED_FILES["sysrq_helper"]` still points at `zigux/tests/phase11_hvc_console_sysrq_helper.zig`, while the live bounded helper in the current packet is `drivers/tty/hvc/hvc_console_sysrq.zig`.
- `SURVEY_MARKERS` and the built-in self-test fixture still require an older survey next-step sentence about a future notifier or khvcd handoff, while the live survey note now records the already-landed archival packet and separately names the paired survey gate's exported-helper signature proof.
- `MATRIX_MARKERS` still pin `PHASE11_HVC_CONSOLE_STATUS=cleanup_handoff_landed`, while the live validation matrix now publishes `PHASE11_HVC_CONSOLE_STATUS=hvc_notifier_handoff_landed`.

This means the checker is no longer the best current-head description of the HVC cleanup packet, even though the packet itself remains bounded and reviewable.

## Safe Reading

Use the current HVC survey note, validation matrix, teardown note, direct helper files, and `scripts/zigux/check-phase11-hvc-survey-packet.py` as the truthful readback for this lane on current `master`.

Read `scripts/zigux/check-phase11-hvc-cleanup-alignment.py` as a stale checker that still needs one coupled same-family repair, not as the source of truth for the present HVC packet layout.

## Boundary Kept Honest

This companion does not claim:

- a landed checker repair in `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`
- notifier callback execution
- khvcd worker execution
- tty-driver registration
- live sysrq dispatch
- host-backed teardown or transport parity

It only records the current-head mismatch between the checker and the already-landed bounded HVC packet.

## Next bounded step

Realign `scripts/zigux/check-phase11-hvc-cleanup-alignment.py` and its self-test in one coupled follow-up so the checker matches the live HVC packet again. The smallest honest repair is still the one-file checker sync around the sysrq helper path, the survey marker wording, and the validation-matrix status marker.
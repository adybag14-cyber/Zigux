# Phase 4 Validation Lane Sequencing

This note turns the current Phase 4 validation evidence into one bounded anti-overlap map for validation lanes only.

## Status
- lane: `P4-Y10`
- phase: `Phase 4`
- date: `2026-05-07`
- evidence mode: `github_connector_readback`
- scope: `validation_lane_sequencing_only`

## Why this note exists
- The roadmap says Phase 4 must keep future Zigux ports measurable and reversible through rollback ownership, lab and CI matrices, perf-threshold posture, and differential-validation gates.
- Current `master` already ships those validation surfaces across `scripts/zigux/validate-phase4.py`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, `zigux/tests/phase4_build.zig`, and the bounded packet files they route through.
- Nearby Phase 4 runs already closed real packet-local gaps for the bitmap rollback gate, the bitmap survey packet, and the artifact-diff contract checker, but there is still no single Phase 4 lane map explaining which surfaces are shared routing surfaces and which packet owns the next bounded fix.
- Without that map, nearby validation runs can reopen the same shared files for different reasons even when the real next step belongs in one narrower packet.

## Shared Validation Surfaces
- `scripts/zigux/validate-phase4.py`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, and `zigux/tests/phase4_build.zig` are shared routing surfaces for the current Phase 4 packet. They should reflect already-landed packet truth, not invent new packet scope on their own.
- `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` are shared replay-entry surfaces. They should only change when an already-bounded packet is being exposed or withdrawn from the shipped Phase 4 route.
- `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` are shared reviewability mirrors. They are not the owning surface for packet-local validation semantics.

## Current Owner Split

### `P4-L14`
- owning packet: host-side artifact-diff contract enforcement
- owner surfaces: `scripts/zigux/check-artifact-diff-contract.py` and `Documentation/zigux/artifact-diff.md`
- shared follow-through surfaces only when the packet changes: `scripts/zigux/validate-phase4.py`, the shared README files, and the Phase 4 matrix or gate-evidence notes if the shipped contract summary moves
- do not reopen this lane just to restate artifact-diff policy in the shared matrix when the contract packet itself has not changed

### `P4-Y04`
- owning packet: `zigux/tests/bitmap_diff.zig` rollback-gate truthfulness
- owner surfaces: `zigux/tests/bitmap_diff.zig` and the exact blob-pin lines in `Documentation/zigux/phase4-gate-evidence.md` that name that live gate
- shared follow-through surfaces only when the gate itself moves: `Documentation/zigux/phase4-validation-matrix.md` and `scripts/zigux/validate-phase4.py`
- do not widen this lane into bitmap survey governance, helper-backed replay wording, or perf-threshold approval

### `P4-Y09`
- owning packet: active bitmap survey governance for the shipped rollback packet
- owner surfaces: `zigux/tests/phase4_bitmap_diff_manifest.json` and `zigux/tests/phase4_bitmap_diff_survey.zig`
- shared follow-through surfaces only when the survey packet drifts: `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, and `scripts/zigux/validate-phase4.py`
- do not reopen this lane for helper semantics, direct `bitmap_diff.zig` behavior changes, or absent sample and perf packets

### `P4-Y08`
- owning packet: shared rollback-ownership and lab-matrix promotion work after a packet-local validation surface has already changed
- owner surfaces: `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, and `scripts/zigux/validate-phase4.py` only when one narrower Phase 4 packet needs promotion into the shared route
- current bounded trigger: only after the bitmap survey packet, or another already-shipped Phase 4 packet of the same kind, has drifted enough that the shared matrix, gate-evidence note, and validator need to be brought back into sync
- do not use this lane to start new sample packets, approve perf thresholds, or replace packet-local owners

## Validation-Lane Rules For Open Gaps
- `zigux/tests/phase4_runtime_atomic64_diff_manifest.json` and `zigux/tests/phase4_runtime_atomic64_diff_survey.zig` are already a shipped packet. Treat follow-ups there as packet-local survey work first; only mirror them into shared validation surfaces after the packet itself changes.
- `samples/zigux/kprobe_example.zig`, `samples/zigux/test_fsmount.zig`, and the Phase 4 perf-baseline packet remain matrix-only gaps on current `master`. Do not edit the shared validator, shared build route, or Linux-style wrappers to pretend those packets are shipped before one manifest-backed packet exists for each gap.
- When a future Phase 4 sample or perf packet lands, give that packet its own bounded owner surface first, then route the shared matrix, gate-evidence note, validator, Makefile, workflow, and README updates as follow-through rather than as the opening move.

## Next Safe Step
- Keep `P4-Y10` parked unless another Phase 4 validation run starts reopening `scripts/zigux/validate-phase4.py`, `Documentation/zigux/phase4-validation-matrix.md`, `Documentation/zigux/phase4-gate-evidence.md`, or `zigux/tests/phase4_build.zig` without first identifying the narrower owning packet.
- If that overlap returns, the next bounded fix should stay shared-surface-only: refresh this note or point one drifting shared summary back to the owning packet named here, without reopening packet-local validation semantics.

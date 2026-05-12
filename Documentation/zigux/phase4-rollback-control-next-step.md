# Phase 4 Rollback-Control Next Step

## Status
- `PHASE4_CONTROL_SURFACE_STATUS=shared_ownership_and_lab_matrix_landed`
- `PHASE4_CONTROL_SURFACE_SCOPE=rollback_ownership_and_lab_matrix_only`
- `PHASE4_CONTROL_SURFACE_MODE=current_master_readback`

## Current Repo Reality
- `Documentation/zigux/phase4-validation-matrix.md` already names the shipped rollback owners, rollback-owner fallbacks, bootstrap CI routes, and local replay routes for the current Phase 4 host-side checkers, the bounded atomic64 gate, the bounded bitmap gate, the helper-backed bitmap replay, and the dedicated local perf-baseline survey packet.
- `Documentation/zigux/phase4-gate-evidence.md` already exact-pins the shared rollback-ownership packet, including the dedicated exact-readback checker, the workflow-route checker, the manifest-backed runtime atomic64 survey pair, the bitmap survey pair, the helper-backed bitmap replay, the dedicated local-only perf-baseline packet, and the still-absent `samples/zigux/kprobe_example.zig` plus `samples/zigux/test_fsmount.zig` starters.
- `Documentation/zigux/review-checklist.md` and `scripts/zigux/validate-phase4.py` already keep the same shared packet reviewable without opening new ownership claims.

## Closure Decision
- The shared Phase 4 rollback-ownership and lab-matrix control surface is already closed enough on current `master`; the next safe move is not another ownership-map expansion or a wider lab-matrix rewrite.
- If this control lane reopens, keep it to one same-packet truthfulness correction only when the shared packet itself drifts from current repo evidence.

## Next Safe Step
- Leave the shared control packet parked while the dedicated per-surface lanes handle their own unfinished follow-through.
- The highest-value same-family follow-through remains a truthfulness repair inside the existing bitmap evidence packet so the shared rollback note stops lagging the live bounded bitmap inventory before any new Phase 4 control-surface wording is widened again.

## Anti-Overlap Guard
- Do not reopen the shared Phase 4 control packet for atomic64 harness wording, bitmap harness growth, perf-baseline policy widening, kprobe starter work, or `test_fsmount` starter work unless one of those changes first breaks the already-landed ownership or lab-matrix packet itself.

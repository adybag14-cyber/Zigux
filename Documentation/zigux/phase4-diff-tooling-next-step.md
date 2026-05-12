# Phase 4 Diff Tooling Next Step

## Scope
- Lane: `P4-Y06`
- Surface: `scripts/zigux` exact-readback tooling only
- Boundary: no bitmap, atomic64, perf-baseline, kprobe, or `test_fsmount` harness edits

## Current Repo Evidence
- `scripts/zigux/check-phase4-gate-evidence.py` currently validates a `BLOB_TARGETS` map with nineteen exact-readback blob pins.
- The same checker still hard-codes `EXPECTED_SHIPPED_TARGET_COUNT = 16`.
- `Documentation/zigux/phase4-gate-evidence.md` still publishes both `PHASE4_SHIPPED_GATE_BLOB_TARGET_COUNT=16` and `PHASE4_SHARED_VALIDATOR_EXPECTED_GATE_EVIDENCE_TARGET_COUNT=16`.
- `scripts/zigux/validate-phase4.py` only requires those status markers to exist, so the undercount can remain live even while the exact-readback packet has already widened.
- This is a tooling truthfulness gap, not direct evidence of a rollback replay regression in `zigux/tests/atomic64_diff.zig` or `zigux/tests/bitmap_diff.zig`.

## One Bounded Next Safe Step
- Refresh `scripts/zigux/check-phase4-gate-evidence.py` and `Documentation/zigux/phase4-gate-evidence.md` together so the published exact-readback target count matches the live `BLOB_TARGETS` list.
- Keep that follow-through count-only unless the lane intentionally decides to widen the exact-readback packet again.
- Leave `scripts/zigux/validate-phase4.py` unchanged unless the status schema itself changes beyond the literal target-count value.
- Re-run `python3 scripts/zigux/check-phase4-gate-evidence.py --self-test`, `python3 scripts/zigux/check-phase4-gate-evidence.py`, and `python3 scripts/zigux/validate-phase4.py --self-test` after the count refresh.

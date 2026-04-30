#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PHASE4_GATE_EXPECTATIONS = {
    'atomic64_diff.zig': {
        'owner': 'ABI and Runtime Team',
        'rollback_owner': 'ABI and Runtime Team',
        'fallback_path': 'keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses',
        'exact_check_markers': [
            '`addCounter()`',
            'onestwos growth',
            '`-1` decrement',
            '`or`',
            '`and`',
            '`xor`',
            '`andnot`',
            '`v0 -> v1`',
            '`v1 -> v2`',
            '`minInt(i64) -> -1`',
            '`cmpxchg`',
            'match-store',
            'mismatch-no-store',
            '`addUnlessCounter()`',
            'blocked and changed cases',
            '`incNotZeroCounter()`',
            'positive, zero, `-1`, and `minInt(i64)`',
            '`decIfPositiveCounter()`',
            'positive, zero, and negative return-path behavior',
            'ordered operation families',
            '`checked_returning_paths`',
            '`checked_guard_paths`',
            'post-exit invalid lifecycle errors',
            'post-selftest replay',
        ],
        'threshold_status': 'correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set',
        'threshold_posture': 'threshold_pending_until_runtime_atomic64_scope_widens',
        'gate_scope': 'add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay',
        'threshold_scope': 'add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set',
        'local_replay_markers': [
            'phase4-runtime-atomic64-diff-tests',
            'phase4-runtime-atomic64-diff-survey-tests',
        ],
        'reversible_delivery': '`lib/atomic64_test.c` stays the source of truth, and removing `atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move while `runtime_atomic64_diff.zig` remains the single replay body and the existing Phase 9 runtime atomic64 starter remains the forward path',
    },
    'bitmap_diff.zig': {
        'owner': 'Shared Subsystems Pod',
        'rollback_owner': 'Shared Subsystems Pod',
        'fallback_path': 'keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses',
        'rollback_evidence_gap': 'direct `bitmap_fill(..., 115)` still stops at bit 114 in the shipped Zig helper, so the Phase 4 packet keeps that mismatch survey-only instead of claiming parity with the `lib/test_bitmap.c` rounded two-word anchor',
        'exact_check_markers': [
            '`bitmap_fill(..., 35)`',
            '`bitmap_fill(..., 115)`',
            '`bitmap_zero(..., 35)`',
            '`bitmap_zero(..., 115)`',
            '`bitmap_set(..., 79, 19)`',
            '`bitmap_clear(..., 79, 19)`',
            '`bitmap_fill(..., 1024)`',
            '`bitmap_zero(..., 1024)`',
            '`1-3,7,10-11`',
            'truncated `1-3` rendering',
            '23-bit single-word window',
            'cleared-destination copies',
            'filled-destination copies',
            '109-bit partial-tail',
            '97-bit aligned-copy',
            '`bitmap.copyClearTail()` keeps the 109-bit cleared-tail contract',
            'full-width nth-7 and nth-8 outcomes',
            'bit 123 for nth 7',
            'cutoff width for nth 8',
        ],
        'threshold_status': 'correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, rounded-prefix, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior checkpoints',
        'threshold_posture': 'threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks',
        'gate_scope': 'bounded bitmap range, rounded-prefix, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior replay',
        'threshold_scope': 'range, rounded-prefix, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior checkpoints',
        'local_replay_markers': [
            'phase4-bitmap-diff-tests',
        ],
        'reversible_delivery': '`lib/test_bitmap.c` stays the source of truth, and removing `bitmap_diff.zig` from the shared `phase4_build.zig` entrypoint falls back to the existing broad bitmap parity checks',
    },
}

REQUIRED_FILES = [
    'scripts/zigux/artifact_diff.py',
    'scripts/zigux/check-artifact-diff-contract.py',
    'scripts/zigux/validate-phase4.py',
    'Documentation/zigux/artifact-diff.md',
    'Documentation/zigux/phase4-gate-evidence.md',
    'Documentation/zigux/phase4-validation-matrix.md',
    'samples/kprobes/Makefile',
    'samples/kprobes/kprobe_example.c',
    'samples/vfs/Makefile',
    'samples/vfs/test-fsmount.c',
    'zigux/Makefile',
    '.github/workflows/zigux-bootstrap.yml',
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/atomic64_diff.zig',
    'zigux/tests/phase4_runtime_atomic64_diff_survey.zig',
    'zigux/tests/phase4_runtime_atomic64_diff_manifest.json',
    'zigux/tests/phase4_test_fsmount_manifest.json',
    'zigux/tests/phase4_test_fsmount_survey.zig',
    'zigux/tests/phase4_perf_baseline_manifest.json',
    'zigux/tests/phase4_perf_baseline_survey.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
]

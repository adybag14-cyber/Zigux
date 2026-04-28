#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PHASE4_GATE_EXPECTATIONS = {
    'runtime_atomic64_diff.zig': {
        'owner': 'ABI and Runtime Team',
        'rollback_owner': 'ABI and Runtime Team',
        'fallback_path': 'keep the current C anchor plus the existing Phase 9 runtime atomic64 starter surface as the source of truth if the Zig replay gate regresses',
        'threshold_status': 'correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded add, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set',
        'threshold_posture': 'threshold_pending_until_runtime_atomic64_scope_widens',
        'gate_scope': 'add, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay',
        'threshold_scope': 'add, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set',
        'local_replay_markers': [
            'phase4-runtime-atomic64-diff-tests',
            'phase4-runtime-atomic64-diff-survey-tests',
        ],
        'reversible_delivery': '`lib/atomic64_test.c` stays the source of truth, and removing `runtime_atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move while the existing Phase 9 runtime atomic64 starter remains the forward path',
    },
    'bitmap_diff.zig': {
        'owner': 'Shared Subsystems Pod',
        'rollback_owner': 'Shared Subsystems Pod',
        'fallback_path': 'keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses',
        'exact_check_markers': [
            '`bitmap_fill(..., 35)`',
            '`bitmap_zero(..., 115)`',
            '`bitmap_set(..., 79, 19)`',
            '`bitmap_clear(..., 79, 19)`',
            '`bitmap_fill(..., 1024)`',
            '`bitmap_zero(..., 1024)`',
            '`1-3,7,10-11`',
            'truncated `1-3` rendering',
            '23-bit single-word window',
            'filled-destination copies',
            '109-bit partial-tail',
            '97-bit aligned-copy',
            '`bitmap.copyClearTail()` keeps the 109-bit cleared-tail contract',
            'full-width nth-7 and nth-8 outcomes',
            'bit 123 for nth 6',
            'cutoff width for nth 7',
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
    'Documentation/zigux/phase4-validation-matrix.md',
    'zigux/Makefile',
    '.github/workflows/zigux-bootstrap.yml',
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/phase4_runtime_atomic64_diff_survey.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
]

REQUIRED_MAKE_MARKERS = [
    'PHONY += phase4-validate phase4-test phase4',
    'phase4-validate:',
    'scripts/zigux/artifact_diff.py --self-test',
    'scripts/zigux/check-artifact-diff-contract.py',
    'scripts/zigux/validate-phase4.py',
    'scripts/zigux/validate-phase4.py --self-test',
    'phase4-test:',
    'zigux/tests/phase4_build.zig',
]

REQUIRED_WORKFLOW_MARKERS = [
    'Validate Phase 4 diff gates',
    'Run Phase 4 diff tests',
    'make -C zigux phase4-validate',
    'make -C zigux phase4-test',
]

REQUIRED_DOC_MARKERS = [
    'Current Phase 4 use',
    'python3 scripts/zigux/artifact_diff.py --self-test',
    'python3 scripts/zigux/check-artifact-diff-contract.py',
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
    'scripts/zigux/validate-phase4.py',
    'Documentation/zigux/artifact-diff.md',
    'Documentation/zigux/phase4-validation-matrix.md',
    'shared comparison layer that already backs the bounded host-side tools under `scripts/zigux/`',
    'keeps stale expected-output and catalog drift small, auditable, and easy to refresh',
    '`EXPECTED_JSON_ERROR=`',
    '`ACTUAL_JSON_ERROR=`',
]

REQUIRED_DOC_MARKER_GROUPS = [
    (
        'reversible_delivery_link',
        [
            'reversible-delivery evidence',
            'current C anchor',
            'shared Phase 4 entrypoint',
        ],
    ),
]

FORBIDDEN_DOC_MARKERS = [
    'future Phase 2 tooling work will reuse',
    'reuse the same artifact-diff pattern for Phase 2 dual-implementation and bridge outputs such as `fixdep`, `genksyms`, `genksyms_crc`, `kconfig_bridge`, and `mk_elfconfig`',
]

REQUIRED_TESTS_README_MARKERS = [
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
    'scripts/zigux/validate-phase4.py',
]

REQUIRED_SCRIPT_README_MARKERS = [
    'artifact_diff.py --self-test',
    'check-artifact-diff-contract.py',
    'make -C zigux phase4-validate',
    'validate-phase4.py',
    'Phase 4 flow',
    'phase4_build.zig',
    'phase4-validation-matrix.md',
    'phase4-runtime-atomic64-diff-survey-tests',
    'reversible-delivery evidence',
]

REQUIRED_DOC_README_MARKERS = [
    'Phase 4 notes',
    'make -C zigux phase4-validate',
    'python3 scripts/zigux/artifact_diff.py --self-test',
    'check-artifact-diff-contract.py',
    'validate-phase4.py',
    'phase4-validation-matrix.md',
    'Validate Phase 4 diff gates',
    'Run Phase 4 diff tests',
    'phase4-runtime-atomic64-diff-survey-tests',
    'reversible-delivery evidence',
]

REQUIRED_PHASE4_MATRIX_MARKERS = [
    'scripts/zigux/artifact_diff.py --self-test',
    'python3 scripts/zigux/check-artifact-diff-contract.py',
    'deterministic_preflight_required_for_host_side_diff_tools',
    'runtime_atomic64_diff.zig',
    'phase4_runtime_atomic64_diff_survey.zig',
    'bitmap_diff.zig',
    'rollback owner',
    'lab and CI matrix',
    'reversible delivery evidence',
    'perf threshold status',
    'Validate Phase 4 diff gates',
    'Run Phase 4 diff tests',
    'make -C zigux phase4-validate',
    'make -C zigux phase4-test',
    'phase4-runtime-atomic64-diff-tests',
    'phase4-runtime-atomic64-diff-survey-tests',
    'phase4-bitmap-diff-tests',
    'Remaining Measurability Gaps Vs Roadmap',
    'samples/zigux/kprobe_example.zig',
    'samples/zigux/test_fsmount.zig',
    'the current anchor remains `samples/vfs/test-fsmount.c` through `samples/vfs/Makefile` and `userprogs-always-y += test-fsmount`',
    'reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/vfs`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands',
    'benchmark command and acceptable limit are still unapproved for both landed gates',
]

ROADMAP_GAP_EXPECTATIONS = {
    'samples/zigux/kprobe_example.zig': {
        'current_repo_state': 'not present on `master`; the current anchor remains `samples/kprobes/kprobe_example.c` through `samples/kprobes/Makefile` and `CONFIG_SAMPLE_KPROBES`',
        'measurability_gap': 'reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands',
        'next_bounded_step': 'land one bounded survey manifest or starter gate under `samples/zigux/` that keeps the same owner, rollback owner, and replay command before claiming this anchor as active Phase 4 work',
    },
    'samples/zigux/test_fsmount.zig': {
        'current_repo_state': 'not present on `master`; the current anchor remains `samples/vfs/test-fsmount.c` through `samples/vfs/Makefile` and `userprogs-always-y += test-fsmount`',
        'measurability_gap': 'reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/vfs`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands',
        'next_bounded_step': 'land one bounded survey manifest or starter gate under `samples/zigux/` that keeps the same owner, rollback owner, and replay command before claiming this anchor as active Phase 4 work',
    },
    'perf baselines and thresholds for the two shipped rollback gates': {
        'current_repo_state': '`zigux/tests/runtime_atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still correctness-only gates today',
        'measurability_gap': 'benchmark command and acceptable limit are still unapproved for both landed gates',
        'next_bounded_step': 'land one bounded benchmark command and one acceptable limit per gate before Phase 4 claims perf coverage',
    },
}

REQUIRED_ARTIFACT_DIFF_MARKERS = [
    'def emit_result(matched: bool, details: dict[str, object]) -> int:',
    'def run_self_test() -> int:',
    "print('ARTIFACT_DIFF_SELF_TEST=pass')",
    "details['expected_sha256'] = expected_value",
    "print(f\"EXPECTED_SHA256={details['expected_sha256']}\")",
    "print(f\"ACTUAL_SHA256={details['actual_sha256']}\")",
    "details['expected_exists'] = expected.exists()",
    "print(f\"EXPECTED_JSON_ERROR={details['expected_json_error']}\")",
    "print(f\"ACTUAL_JSON_ERROR={details['actual_json_error']}\")",
]

REQUIRED_PHASE4_BUILD_MARKERS = [
    'runtime_atomic64_diff.zig',
    'phase4_runtime_atomic64_diff_survey.zig',
    'bitmap_diff.zig',
    'phase4-runtime-atomic64-diff-tests',
    'phase4-runtime-atomic64-diff-survey-tests',
    'phase4-bitmap-diff-tests',
]

REQUIRED_RUNTIME_ATOMIC64_MARKERS = [
    'addUn
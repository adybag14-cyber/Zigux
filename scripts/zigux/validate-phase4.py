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
    'scripts/zigux/check-phase4-gate-evidence.py',
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

REQUIRED_MAKE_MARKERS = [
    'PHONY += phase4-validate phase4-test phase4-runtime-atomic64-diff phase4-test-fsmount-survey phase4-perf-baseline-survey phase4-bitmap-diff phase4',
    'phase4-validate:',
    'scripts/zigux/artifact_diff.py --self-test',
    'scripts/zigux/check-artifact-diff-contract.py',
    'scripts/zigux/validate-phase4.py',
    'scripts/zigux/validate-phase4.py --self-test',
    'scripts/zigux/check-phase4-gate-evidence.py --self-test',
    'scripts/zigux/check-phase4-gate-evidence.py',
    'phase4-test:',
    'zigux/tests/phase4_build.zig',
    'phase4-perf-baseline-survey:',
    'phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig',
]

EXACT_REQUIRED_MAKE_LINES = [
    '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py --self-test',
    '\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py',
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
    'zigux/tests/atomic64_diff.zig',
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
            'reversible-delivery',
            'current C anchor',
        ],
    ),
]

FORBIDDEN_DOC_MARKERS = [
    'future Phase 2 tooling work will reuse',
    'reuse the same artifact-diff pattern for Phase 2 dual-implementation and bridge outputs such as `fixdep`, `genksyms`, `genksyms_crc`, `kconfig_bridge`, and `mk_elfconfig`',
]

REQUIRED_TESTS_README_MARKERS = [
    'zigux/tests/atomic64_diff.zig',
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/phase4_perf_baseline_manifest.json',
    'zigux/tests/phase4_perf_baseline_survey.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
    'scripts/zigux/validate-phase4.py',
    'make -C zigux phase4-perf-baseline-survey',
    'perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land',
]

REQUIRED_SCRIPT_README_MARKERS = [
    'artifact_diff.py --self-test',
    'check-artifact-diff-contract.py',
    'make -C zigux phase4-validate',
    'make -C zigux phase4-test-fsmount-survey',
    'make -C zigux phase4-perf-baseline-survey',
    'validate-phase4.py',
    'Phase 4 flow',
    'phase4_build.zig',
    'phase4-validation-matrix.md',
    'phase4-test-fsmount-survey',
    'phase4-runtime-atomic64-diff-survey-tests',
    'phase4_perf_baseline_manifest.json',
    'phase4-perf-baseline-survey-tests',
    'perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land',
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
    'phase4-test-fsmount-survey',
    'phase4-runtime-atomic64-diff-survey-tests',
    'phase4_perf_baseline_manifest.json',
    'phase4-perf-baseline-survey-tests',
    'make -C zigux phase4-perf-baseline-survey',
    'perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land',
    'reversible-delivery evidence',
]

REQUIRED_PHASE4_MATRIX_MARKERS = [
    'scripts/zigux/artifact_diff.py --self-test',
    'python3 scripts/zigux/check-artifact-diff-contract.py',
    'Documentation/zigux/phase4-gate-evidence.md',
    'deterministic_preflight_required_for_host_side_diff_tools',
    'roadmap names `zigux/tests/atomic64_diff.zig`',
    'canonical wrapper while the bounded atomic64 replay gate at `zigux/tests/runtime_atomic64_diff.zig` remains the single underlying replay body',
    'atomic64_diff.zig',
    'runtime_atomic64_diff.zig',
    'phase4_runtime_atomic64_diff_survey.zig',
    'phase4_perf_baseline_manifest.json',
    'phase4-perf-baseline-survey-tests',
    'make -C zigux phase4-perf-baseline-survey',
    'perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land',
    'threshold_pending_until_runtime_atomic64_scope_widens',
    'threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks',
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
    'phase4-test-fsmount-survey-tests',
    'phase4-perf-baseline-survey-tests',
    'phase4-bitmap-diff-tests',
    'make -C zigux phase4-test-fsmount-survey',
    'make -C zigux phase4-perf-baseline-survey',
    'c_anchor_only_until_test_fsmount_starter_lands',
    'Remaining Measurability Gaps Vs Roadmap',
    'samples/zigux/kprobe_example.zig',
    'samples/zigux/test_fsmount.zig',
    'the current anchor remains `samples/vfs/test-fsmount.c` through `samples/vfs/Makefile` and `userprogs-always-y += test-fsmount`',
    'reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/vfs`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands',
    'benchmark command and acceptable limit are still unapproved for both landed gates',
    'paired exact readback note',
    'inspected `master` head',
]

ROADMAP_GAP_EXPECTATIONS = {
    'samples/zigux/kprobe_example.zig': {
        'current_repo_state': 'not present on `master`; the current anchor remains `samples/kprobes/kprobe_example.c` through `samples/kprobes/Makefile` and `CONFIG_SAMPLE_KPROBES`, and the validator-backed absence check keeps that true today',
        'measurability_gap': 'reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands',
        'next_bounded_step': 'land one bounded survey manifest or starter gate under `samples/zigux/` that keeps the same owner, rollback owner, and replay command before claiming this anchor as active Phase 4 work',
    },
    'samples/zigux/test_fsmount.zig': {
        'current_repo_state': 'not present on `master`; the current anchor remains `samples/vfs/test-fsmount.c` through `samples/vfs/Makefile` and `userprogs-always-y += test-fsmount`, the validator-backed absence check keeps that true today, and the manifest-backed survey gate now lives in `zigux/tests/phase4_test_fsmount_manifest.json` plus `zigux/tests/phase4_test_fsmount_survey.zig` under the shared `phase4-test-fsmount-survey-tests` replay',
        'measurability_gap': 'reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/vfs`; the Zig lab matrix remains C-anchor-only and no hard timing threshold is approved before a bounded Zig sample lands',
        'next_bounded_step': 'land one bounded starter under `samples/zigux/test_fsmount.zig` that keeps the same owner, rollback owner, and `make M=samples/vfs` replay contract before claiming this anchor as active Phase 4 work',
    },
    'perf baselines and thresholds for the two shipped rollback gates': {
        'current_repo_state': '`zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` are still correctness-only gates today',
        'measurability_gap': 'benchmark command and acceptable limit are still unapproved for both landed gates',
        'next_bounded_step': 'land one bounded benchmark command and one acceptable limit per gate before Phase 4 claims perf coverage',
    },
}

PHASE4_SURVEY_MATRIX_EXPECTATIONS = {
    'zigux/tests/phase4_test_fsmount_survey.zig': {
        'owner': 'Validation and Perf Team',
        'rollback_owner': 'Validation and Perf Team',
        'bootstrap_ci_replay_markers': [
            'Validate Phase 4 diff gates',
            'Run Phase 4 diff tests',
            'phase4-test-fsmount-survey-tests',
        ],
        'local_lab_replay_markers': [
            'make -C zigux phase4-test-fsmount-survey',
            'zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig',
            'make M=samples/vfs',
        ],
        'reversible_delivery_markers': [
            '`samples/vfs/test-fsmount.c` stays the source of truth',
            'C-anchor-only until a bounded `samples/zigux/test_fsmount.zig` starter lands',
            'returns this roadmap row to matrix-only tracking without overstating a landed Zig sample',
        ],
        'threshold_posture': 'c_anchor_only_until_test_fsmount_starter_lands',
    },
    'zigux/tests/phase4_perf_baseline_survey.zig': {
        'owner': 'Validation and Perf Team',
        'rollback_owner': 'Validation and Perf Team',
        'bootstrap_ci_replay_markers': [
            'Validate Phase 4 diff gates',
            'Run Phase 4 diff tests',
            'phase4-perf-baseline-survey-tests',
        ],
        'local_lab_replay_markers': [
            'make -C zigux phase4-perf-baseline-survey',
            'zig build phase4-perf-baseline-survey --build-file zigux/tests/phase4_build.zig',
            'phase4-runtime-atomic64-diff-tests',
            'phase4-runtime-atomic64-diff-survey-tests',
            'phase4-bitmap-diff-tests',
        ],
        'reversible_delivery_markers': [
            '`zigux/tests/atomic64_diff.zig` and `zigux/tests/bitmap_diff.zig` remain the shipped rollback gates',
            'only machine-checked record that their benchmark command and acceptable limit are still unapproved',
            'instead of landed',
        ],
        'threshold_posture': 'perf_thresholds_unapproved_until_bounded_phase4_benchmarks_land',
    },
}

PHASE4_TEST_FSMOUNT_MANIFEST_EXPECTATIONS = {
    'lane_key': 'P4-L19',
    'phase': 'Phase 4',
    'owner': 'Validation and Perf Team',
    'rollback_owner': 'Validation and Perf Team',
    'anchor': 'samples/vfs/test-fsmount.c',
    'roadmap_destinations': ['samples/zigux/test_fsmount.zig'],
    'current_replay': 'make M=samples/vfs',
    'survey_summary': {
        'vfs_makefile_replay_present': True,
        'zig_sample_present': False,
        'phase4_build_present': True,
        'phase4_validator_present': True,
        'phase4_validation_matrix_present': True,
    },
}

PHASE4_PERF_BASELINE_MANIFEST_EXPECTATIONS = {
    'lane_key': 'P4-L20',
    'phase': 'Phase 4',
    'owner': 'Validation and Perf Team',
    'rollback_owner': 'Validation and Perf Team',
    'surveyed_gates': [
        {
            'surface': 'zigux/tests/atomic64_diff.zig',
            'gate_owner': 'ABI and Runtime Team',
            'gate_rollback_owner': 'ABI and Runtime Team',
            'threshold_posture': 'threshold_pending_until_runtime_atomic64_scope_widens',
        },
        {
            'surface': 'zigux/tests/bitmap_diff.zig',
            'gate_owner': 'Shared Subsystems Pod',
            'gate_rollback_owner': 'Shared Subsystems Pod',
            'threshold_posture': 'threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks',
        },
    ],
    'survey_summary': {
        'phase4_build_present': True,
        'phase4_validator_present': True,
        'phase4_validation_matrix_present': True,
        'benchmark_command_unapproved': True,
        'acceptable_limit_unapproved': True,
    },
}

PHASE4_RUNTIME_ATOMIC64_MANIFEST_EXPECTATIONS = {
    'lane_key': 'P4-L01',
    'phase': 'Phase 4',
    'anchor': 'lib/atomic64_test.c',
    'roadmap_destinations': ['zigux/tests/atomic64_diff.zig'],
    'survey_summary': {
        'roadmap_atomic64_diff_present': True,
        'phase4_validation_matrix_present': True,
        'phase4_build_present': True,
        'phase4_validator_runtime_atomic64_diff_present': True,
        'phase4_validator_atomic64_diff_present': True,
    },
    'threshold_plan': {
        'owner': 'ABI and Runtime Team',
        'rollback_owner': 'ABI and Runtime Team',
        'posture': 'threshold_pending_until_runtime_atomic64_scope_widens',
        'status': 'pending_scope_widening',
        'benchmark_command': 'unapproved_until_runtime_atomic64_scope_widens',
        'acceptable_limit': 'unapproved_until_runtime_atomic64_scope_widens',
    },
}

PHASE4_RUNTIME_ATOMIC64_MATRIX_NOTE_EXPECTATIONS = {
    'id': 'phase4-validation-matrix-note',
    'status': 'starter_landed',
    'kind': 'ownership_note',
    'zigux_destination': 'Documentation/zigux/phase4-validation-matrix.md',
    'why_now_fragments': [
        'rollback owner',
        'threshold posture',
        'threshold_pending_until_runtime_atomic64_scope_widens',
        'manifest-backed pending threshold plan',
        'reversible-delivery evidence',
        '`lib/atomic64_test.c` anchor',
        'shared `phase4_build.zig` entrypoint',
    ],
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
    'atomic64_diff.zig',
    'phase4_runtime_atomic64_diff_survey.zig',
    'phase4_test_fsmount_survey.zig',
    'phase4_perf_baseline_survey.zig',
    'bitmap_diff.zig',
    'phase4-runtime-atomic64-diff-tests',
    'phase4-runtime-atomic64-diff-survey-tests',
    'phase4-test-fsmount-survey-tests',
    'phase4-perf-baseline-survey-tests',
    'phase4-bitmap-diff-tests',
]

REQUIRED_RUNTIME_ATOMIC64_MARKERS = [
    'addUnlessCounter',
    'incNotZeroCounter',
    'decIfPositiveCounter',
    'add_unless, inc_not_zero, and dec_if_positive expectations',
    'checked_guard_paths',
    'error.InvalidLifecycleTransition, module.incNotZeroCounter()',
    'runtime atomic64 diff gate keeps post-selftest replay explicit',
]

REQUIRED_RUNTIME_ATOMIC64_SURVEY_MARKERS = [
    'roadmap_atomic64_diff_present',
    'phase4_validation_matrix_present',
    'phase4_build_present',
    'phase4-runtime-atomic64-diff-gate',
    'phase4-shared-build-entrypoint',
    'phase4-validation-matrix-note',
    'phase4-roadmap-path-alignment',
    'phase4-broader-atomic64-surface',
]

REQUIRED_BITMAP_DIFF_MARKERS = [
    'test "bitmap diff gate replays bounded lib/test_bitmap.c range expectations"',
    'The shipped Zig helper still keeps bitmap_fill(35) at the requested',
    'test "bitmap diff survey keeps the current rounded fill drifts explicit against lib/test_bitmap.c"',
    'the current Zig helper stops at bit 114',
    'test "bitmap diff gate records exact cross-boundary set and clear checks"',
    'test "bitmap diff gate records exact full-width fill and zero endpoints"',
    'test "bitmap diff gate records exact bounded copy checks"',
    'test_copy_clear_tail keeps the 109-bit cleared-tail contract explicit',
    'test "bitmap diff gate records exact bounded find_nth_bit checks"',
    'test_find_nth_bit full-width nth-7 and nth-8 outcomes',
    'test_find_nth_bit reduced-width replay still keeps bit 123 for nth 7',
    'test_find_nth_bit reduced-width replay returns the cutoff width for nth 8',
    'roundedPrefixLen',
    'fillPrefix',
    'zeroPrefix',
    'copyFrom',
    'findNthSet',
    'firstSet',
    'firstZero',
    'weight',
]

REQUIRED_GATE_EVIDENCE_MARKERS = [
    'PHASE4_EVIDENCE_MODE=github_connector_readback',
    'PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions',
    '## Exact Readback Evidence',
    '## Current Conclusion',
    'PHASE4_VALIDATION_MATRIX_BLOB_SHA=',
    'PHASE4_VALIDATOR_BLOB_SHA=',
    'PHASE4_BUILD_BLOB_SHA=',
    'PHASE4_MAKEFILE_BLOB_SHA=',
    'PHASE4_WORKFLOW_BLOB_SHA=',
    'PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA=',
    'PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA=',
    'PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA=',
]

PHASE4_GATE_EVIDENCE_BLOB_TARGETS = {
    'PHASE4_VALIDATION_MATRIX_BLOB_SHA': 'Documentation/zigux/phase4-validation-matrix.md',
    'PHASE4_VALIDATOR_BLOB_SHA': 'scripts/zigux/validate-phase4.py',
    'PHASE4_BUILD_BLOB_SHA': 'zigux/tests/phase4_build.zig',
    'PHASE4_MAKEFILE_BLOB_SHA': 'zigux/Makefile',
    'PHASE4_WORKFLOW_BLOB_SHA': '.github/workflows/zigux-bootstrap.yml',
    'PHASE4_TEST_FSMOUNT_MANIFEST_BLOB_SHA': 'zigux/tests/phase4_test_fsmount_manifest.json',
    'PHASE4_PERF_BASELINE_MANIFEST_BLOB_SHA': 'zigux/tests/phase4_perf_baseline_manifest.json',
    'PHASE4_RUNTIME_ATOMIC64_MANIFEST_BLOB_SHA': 'zigux/tests/phase4_runtime_atomic64_diff_manifest.json',
}


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding='utf-8')


def read_bytes(root: Path, relative_path: str) -> bytes:
    return (root / relative_path).read_bytes()


def read_json(root: Path, relative_path: str) -> object:
    return json.loads(read_text(root, relative_path))


def git_blob_sha1(payload: bytes) -> str:
    header = f'blob {len(payload)}\0'.encode('utf-8')
    return hashlib.sha1(header + payload).hexdigest()


def collect_missing_markers(text: str, prefix: str, markers: list[str]) -> list[str]:
    missing = []
    for marker in markers:
        if marker not in text:
            missing.append(f'{prefix}:{marker}')
    return missing


def count_exact_line(text: str, line: str) -> int:
    return sum(1 for candidate in text.splitlines() if candidate == line)


def collect_json_mismatches(
    expected: object, actual: object, prefix: str
) -> list[str]:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f'{prefix}:type']
        missing: list[str] = []
        for key, value in expected.items():
            if key not in actual:
                missing.append(f'{prefix}.{key}:missing')
                continue
            missing.extend(collect_json_mismatches(value, actual[key], f'{prefix}.{key}'))
        return missing
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return [f'{prefix}:type']
        if len(expected) != len(actual):
            return [f'{prefix}:len:{len(actual)}']
        missing: list[str] = []
        for index, value in enumerate(expected):
            missing.extend(
                collect_json_mismatches(value, actual[index], f'{prefix}[{index}]')
            )
        return missing
    if actual != expected:
        return [f'{prefix}:{actual!r}']
    return []


def check_row_field(row: str, surface: str, label: str, expected: str) -> list[str]:
    if expected not in row:
        return [f'phase4_matrix:{label}:{surface}:{expected}']
    return []


def check_gate_matrix_alignment(
    phase4_matrix: str,
    gate_name: str,
    expectation: dict[str, object],
) -> list[str]:
    row_prefix = f'| `zigux/tests/{gate_name}` |'
    row = next(
        (line for line in phase4_matrix.splitlines() if line.startswith(row_prefix)),
        '',
    )
    if not row:
        return [f'phase4_matrix:missing_gate_row:{gate_name}']

    missing: list[str] = []
    missing.extend(check_row_field(row, gate_name, 'owner', expectation['owner']))
    missing.extend(
        check_row_field(
            row,
            gate_name,
            'rollback_owner',
            expectation['rollback_owner'],
        )
    )
    missing.extend(
        check_row_field(
            row,
            gate_name,
            'threshold_posture',
            expectation['threshold_posture'],
        )
    )
    missing.extend(
        check_row_field(row, gate_name, 'reversible_delivery', expectation['reversible_delivery'])
    )
    for marker in expectation['exact_check_markers']:
        missing.extend(check_row_field(row, gate_name, 'exact_check', marker))
    rollback_evidence_gap = expectation.get('rollback_evidence_gap')
    if rollback_evidence_gap is not None:
        missing.extend(
            check_row_field(row, gate_name, 'rollback_evidence_gap', rollback_evidence_gap)
        )
    for marker in expectation['local_replay_markers']:
        missing.extend(check_row_field(row, gate_name, 'local_replay', marker))
    missing.extend(check_row_field(row, gate_name, 'purpose', expectation['gate_scope']))
    return missing


def check_survey_matrix_alignment(
    phase4_matrix: str,
    lane_surface: str,
    expectation: dict[str, object],
) -> list[str]:
    row_prefix = f'| `{lane_surface}` |'
    row = next(
        (line for line in phase4_matrix.splitlines() if line.startswith(row_prefix)),
        '',
    )
    if not row:
        return [f'phase4_matrix:missing_survey_row:{lane_surface}']

    missing: list[str] = []
    if expectation['owner'] not in row:
        missing.append(f"phase4_matrix:survey_owner:{lane_surface}:{expectation['owner']}")
    if expectation['rollback_owner'] not in row:
        missing.append(
            f"phase4_matrix:survey_rollback_owner:{lane_surface}:{expectation['rollback_owner']}"
        )
    for marker in expectation['bootstrap_ci_replay_markers']:
        if marker not in row:
            missing.append(
                f'phase4_matrix:survey_bootstrap_ci:{lane_surface}:{marker}'
            )
    for marker in expectation['local_lab_replay_markers']:
        if marker not in row:
            missing.append(f'phase4_matrix:survey_local_lab:{lane_surface}:{marker}')
    for marker in expectation['reversible_delivery_markers']:
        if marker not in row:
            missing.append(
                f'phase4_matrix:survey_reversible_delivery:{lane_surface}:{marker}'
            )
    if expectation['threshold_posture'] not in row:
        missing.append(
            f"phase4_matrix:survey_threshold_posture:{lane_surface}:{expectation['threshold_posture']}"
        )
    return missing


def check_roadmap_gap_alignment(
    phase4_matrix: str,
    item_name: str,
    expectation: dict[str, object],
) -> list[str]:
    row_prefix = f'| `{item_name}` |'
    row = next(
        (line for line in phase4_matrix.splitlines() if line.startswith(row_prefix)),
        '',
    )
    if not row:
        return [f'roadmap_gap:missing_row:{item_name}']

    missing: list[str] = []
    for key in ('current_repo_state', 'measurability_gap', 'next_bounded_step'):
        value = expectation[key]
        if value not in row:
            missing.append(f'roadmap_gap:{key}:{item_name}:{value}')
    return missing


def check_runtime_atomic64_manifest_alignment(manifest: object) -> list[str]:
    missing = collect_json_mismatches(
        PHASE4_RUNTIME_ATOMIC64_MANIFEST_EXPECTATIONS,
        manifest,
        'phase4_runtime_atomic64_manifest',
    )
    if not isinstance(manifest, dict):
        return missing

    gaps = manifest.get('gaps')
    if not isinstance(gaps, list):
        return missing + ['phase4_runtime_atomic64_manifest.gaps:type']

    matrix_note = next(
        (
            gap
            for gap in gaps
            if isinstance(gap, dict)
            and gap.get('id') == 'phase4-validation-matrix-note'
        ),
        None,
    )
    if matrix_note is None:
        return missing + [
            'phase4_runtime_atomic64_manifest.gaps:missing:phase4-validation-matrix-note'
        ]

    for key in ('status', 'kind', 'zigux_destination'):
        expected = PHASE4_RUNTIME_ATOMIC64_MATRIX_NOTE_EXPECTATIONS[key]
        actual = matrix_note.get(key)
        if actual != expected:
            missing.append(
                f'phase4_runtime_atomic64_manifest.gaps.phase4-validation-matrix-note.{key}:{actual!r}'
            )

    why_now = matrix_note.get('why_now')
    if not isinstance(why_now, str):
        missing.append(
            'phase4_runtime_atomic64_manifest.gaps.phase4-validation-matrix-note.why_now:type'
        )
        return missing

    for fragment in PHASE4_RUNTIME_ATOMIC64_MATRIX_NOTE_EXPECTATIONS[
        'why_now_fragments'
    ]:
        if fragment not in why_now:
            missing.append(
                'phase4_runtime_atomic64_manifest.gaps.phase4-validation-matrix-note.why_now:'
                + fragment
            )
    return missing


def check_gate_evidence_alignment(root: Path, gate_evidence: str) -> list[str]:
    missing = collect_missing_markers(
        gate_evidence, 'phase4_gate_evidence', REQUIRED_GATE_EVIDENCE_MARKERS
    )
    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        digest = git_blob_sha1(read_bytes(root, relative_path))
        evidence_line = f'`{marker}={digest}`'
        if evidence_line not in gate_evidence:
            missing.append(f'phase4_gate_evidence:{marker}:{digest}')
    return missing


def validate_root(root: Path) -> list[str]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return [f'file:{path}' for path in missing_files]

    makefile = read_text(root, 'zigux/Makefile')
    workflow = read_text(root, '.github/workflows/zigux-bootstrap.yml')
    artifact_diff = read_text(root, 'scripts/zigux/artifact_diff.py')
    artifact_doc = read_text(root, 'Documentation/zigux/artifact-diff.md')
    gate_evidence = read_text(root, 'Documentation/zigux/phase4-gate-evidence.md')
    tests_readme = read_text(root, 'zigux/tests/README.md')
    script_readme = read_text(root, 'scripts/zigux/README.md')
    doc_readme = read_text(root, 'Documentation/zigux/README.md')
    phase4_matrix = read_text(root, 'Documentation/zigux/phase4-validation-matrix.md')
    phase4_build = read_text(root, 'zigux/tests/phase4_build.zig')
    runtime_atomic64_diff = read_text(root, 'zigux/tests/runtime_atomic64_diff.zig')
    runtime_atomic64_diff_survey = read_text(
        root, 'zigux/tests/phase4_runtime_atomic64_diff_survey.zig'
    )
    runtime_atomic64_manifest = read_json(
        root, 'zigux/tests/phase4_runtime_atomic64_diff_manifest.json'
    )
    bitmap_diff = read_text(root, 'zigux/tests/bitmap_diff.zig')
    roadmap_atomic64_diff_present = (root / 'zigux/tests/atomic64_diff.zig').exists()

    missing_markers: list[str] = []
    missing_markers.extend(collect_missing_markers(makefile, 'make', REQUIRED_MAKE_MARKERS))
    for line in EXACT_REQUIRED_MAKE_LINES:
        if count_exact_line(makefile, line) != 1:
            missing_markers.append(f'make_exact:{line}')
    missing_markers.extend(
        collect_missing_markers(workflow, 'workflow', REQUIRED_WORKFLOW_MARKERS)
    )
    missing_markers.extend(collect_missing_markers(artifact_doc, 'doc', REQUIRED_DOC_MARKERS))
    missing_markers.extend(check_gate_evidence_alignment(root, gate_evidence))
    for group_name, markers in REQUIRED_DOC_MARKER_GROUPS:
        for marker in markers:
            if marker not in artifact_doc:
                missing_markers.append(f'doc_group:{group_name}:{marker}')
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in artifact_doc:
            missing_markers.append(f'doc_stale:{marker}')
    missing_markers.extend(
        collect_missing_markers(tests_readme, 'tests_readme', REQUIRED_TESTS_README_MARKERS)
    )
    missing_markers.extend(
        collect_missing_markers(script_readme, 'script_readme', REQUIRED_SCRIPT_README_MARKERS)
    )
    missing_markers.extend(
        collect_missing_markers(doc_readme, 'doc_readme', REQUIRED_DOC_README_MARKERS)
    )
    missing_markers.extend(
        collect_missing_markers(phase4_matrix, 'phase4_matrix', REQUIRED_PHASE4_MATRIX_MARKERS)
    )
    missing_markers.extend(
        collect_missing_markers(artifact_diff, 'artifact_diff', REQUIRED_ARTIFACT_DIFF_MARKERS)
    )
    missing_markers.extend(
        collect_missing_markers(phase4_build, 'phase4_build', REQUIRED_PHASE4_BUILD_MARKERS)
    )
    missing_markers.extend(
        collect_missing_markers(
            runtime_atomic64_diff,
            'runtime_atomic64_diff',
            REQUIRED_RUNTIME_ATOMIC64_MARKERS,
        )
    )
    missing_markers.extend(
        collect_missing_markers(
            runtime_atomic64_diff_survey,
            'runtime_atomic64_diff_survey',
            REQUIRED_RUNTIME_ATOMIC64_SURVEY_MARKERS,
        )
    )
    missing_markers.extend(
        collect_missing_markers(bitmap_diff, 'bitmap_diff', REQUIRED_BITMAP_DIFF_MARKERS)
    )
    if not roadmap_atomic64_diff_present:
        missing_markers.append('file:zigux/tests/atomic64_diff.zig')
    missing_markers.extend(check_runtime_atomic64_manifest_alignment(runtime_atomic64_manifest))

    test_fsmount_manifest = read_json(root, 'zigux/tests/phase4_test_fsmount_manifest.json')
    missing_markers.extend(
        collect_json_mismatches(
            PHASE4_TEST_FSMOUNT_MANIFEST_EXPECTATIONS,
            test_fsmount_manifest,
            'phase4_test_fsmount_manifest',
        )
    )
    perf_baseline_manifest = read_json(
        root, 'zigux/tests/phase4_perf_baseline_manifest.json'
    )
    missing_markers.extend(
        collect_json_mismatches(
            PHASE4_PERF_BASELINE_MANIFEST_EXPECTATIONS,
            perf_baseline_manifest,
            'phase4_perf_baseline_manifest',
        )
    )

    for gate_name, expectation in PHASE4_GATE_EXPECTATIONS.items():
        missing_markers.extend(
            check_gate_matrix_alignment(phase4_matrix, gate_name, expectation)
        )

    for survey_path, expectation in PHASE4_SURVEY_MATRIX_EXPECTATIONS.items():
        missing_markers.extend(
            check_survey_matrix_alignment(phase4_matrix, survey_path, expectation)
        )

    for item_name, expectation in ROADMAP_GAP_EXPECTATIONS.items():
        missing_markers.extend(check_roadmap_gap_alignment(phase4_matrix, item_name, expectation))
        if (root / item_name).exists():
            missing_markers.append(f'roadmap_gap:item_should_still_be_absent:{item_name}')

    return missing_markers


def build_phase4_matrix_fixture() -> str:
    lines = [
        '# Phase 4 Validation Matrix',
        '',
        'This document records the live Phase 4 differential-validation ownership and replay matrix.',
        '',
        '## Status',
        '',
        '- `PHASE4_STATUS=differential_validation_matrix_landed`',
    ]
    lines.extend(f'- {marker}' for marker in REQUIRED_PHASE4_MATRIX_MARKERS)
    lines.extend(
        [
            '',
            '## Gate Ownership',
            '',
            '### `scripts/zigux/artifact_diff.py --self-test`',
            '',
            '- owner: `Validation and Perf Team`',
            '- rollback owner: `Validation and Perf Team`',
            '- fallback path: keep the shared self-test wired into `make -C zigux phase4-validate` and fail closed before the rollback-readiness packet claims the host-side diff tooling is aligned',
            '- perf threshold status: deterministic correctness-only preflight today; no timing threshold is relevant until a future Phase 4 lane adds a benchmarked host-tool diff workload',
            '',
            '### `python3 scripts/zigux/check-artifact-diff-contract.py`',
            '',
            '- owner: `Validation and Perf Team`',
            '- rollback owner: `Validation and Perf Team`',
            '- fallback path: keep the external CLI-contract replay wired into `make -C zigux phase4-validate` so one stable pass case and one missing-file failure shape stay reviewable outside the helper-internal self-test',
            '- perf threshold status: deterministic correctness-only preflight today; no timing threshold is relevant until a future Phase 4 lane adds a benchmarked host-tool diff workload',
            '',
        ]
    )

    for gate_name, expectation in PHASE4_GATE_EXPECTATIONS.items():
        lines.extend(
            [
                f"### `zigux/tests/{gate_name}`",
                '',
                f"- owner: `{expectation['owner']}`",
                f"- rollback owner: `{expectation['rollback_owner']}`",
                f"- fallback path: {expectation['fallback_path']}",
                '- exact bounded checks: ' + ', '.join(expectation['exact_check_markers']),
            ]
        )
        rollback_evidence_gap = expectation.get('rollback_evidence_gap')
        if rollback_evidence_gap is not None:
            lines.append(f'- current rollback evidence gap: {rollback_evidence_gap}')
        lines.extend(
            [
                f"- perf threshold status: {expectation['threshold_status']}",
                f"- threshold scope: {expectation['threshold_scope']}",
                '',
            ]
        )

    lines.extend(
        [
            '## Lab And CI Matrix',
            '',
            '| lane surface | purpose | owner | rollback owner | bootstrap CI replay | local lab replay | reversible delivery evidence | threshold posture |',
            '| --- | --- | --- | --- | --- | --- | --- | --- |',
        ]
    )
    for gate_name, expectation in PHASE4_GATE_EXPECTATIONS.items():
        purpose = expectation['gate_scope'] + '; exact checks: ' + ', '.join(
            expectation['exact_check_markers']
        )
        reversible_delivery = expectation['reversible_delivery']
        rollback_evidence_gap = expectation.get('rollback_evidence_gap')
        if rollback_evidence_gap is not None:
            reversible_delivery += '; ' + rollback_evidence_gap
        lines.append(
            '| `zigux/tests/{gate}` | {purpose} | `{owner}` | `{rollback_owner}` | `Validate Phase 4 diff gates` and `Run Phase 4 diff tests` | {local_replay} | {reversible_delivery} | `{threshold_posture}` |'.format(
                gate=gate_name,
                purpose=purpose,
                owner=expectation['owner'],
                rollback_owner=expectation['rollback_owner'],
                local_replay=' and '.join(expectation['local_replay_markers']),
                reversible_delivery=reversible_delivery,
                threshold_posture=expectation['threshold_posture'],
            )
        )
    for survey_path, expectation in PHASE4_SURVEY_MATRIX_EXPECTATIONS.items():
        lines.append(
            '| `{survey}` | survey gate | `{owner}` | `{rollback_owner}` | {bootstrap} | {local_replay} | {reversible_delivery} | `{threshold_posture}` |'.format(
                survey=survey_path,
                owner=expectation['owner'],
                rollback_owner=expectation['rollback_owner'],
                bootstrap=' and '.join(expectation['bootstrap_ci_replay_markers']),
                local_replay=' and '.join(expectation['local_lab_replay_markers']),
                reversible_delivery=' and '.join(
                    expectation['reversible_delivery_markers']
                ),
                threshold_posture=expectation['threshold_posture'],
            )
        )

    lines.extend(
        [
            '',
            '## Remaining Measurability Gaps Vs Roadmap',
            '',
            '| roadmap item | current repo state | measurability gap | next bounded step |',
            '| --- | --- | --- | --- |',
        ]
    )
    for item_name, expectation in ROADMAP_GAP_EXPECTATIONS.items():
        lines.append(
            f"| `{item_name}` | {expectation['current_repo_state']} | {expectation['measurability_gap']} | {expectation['next_bounded_step']} |"
        )

    return '\n'.join(lines) + '\n'


def write_fixture_tree(root: Path) -> None:
    file_contents = {
        'scripts/zigux/artifact_diff.py': '\n'.join(REQUIRED_ARTIFACT_DIFF_MARKERS) + '\n',
        'scripts/zigux/check-artifact-diff-contract.py': '# synthetic contract replay target\n',
        'scripts/zigux/check-phase4-gate-evidence.py': '# synthetic gate evidence checker\n',
        'scripts/zigux/validate-phase4.py': '# synthetic self-test target\n',
        'Documentation/zigux/artifact-diff.md': '\n'.join(
            REQUIRED_DOC_MARKERS
            + [marker for _, markers in REQUIRED_DOC_MARKER_GROUPS for marker in markers]
        )
        + '\n',
        'Documentation/zigux/phase4-validation-matrix.md': build_phase4_matrix_fixture(),
        'Documentation/zigux/README.md': '\n'.join(REQUIRED_DOC_README_MARKERS) + '\n',
        'scripts/zigux/README.md': '\n'.join(REQUIRED_SCRIPT_README_MARKERS) + '\n',
        'zigux/tests/README.md': '\n'.join(REQUIRED_TESTS_README_MARKERS) + '\n',
        'zigux/Makefile': '\n'.join(REQUIRED_MAKE_MARKERS + EXACT_REQUIRED_MAKE_LINES)
        + '\n',
        '.github/workflows/zigux-bootstrap.yml': '\n'.join(REQUIRED_WORKFLOW_MARKERS) + '\n',
        'samples/kprobes/Makefile': 'obj-$(CONFIG_SAMPLE_KPROBES) += kprobe_example.o\n',
        'samples/kprobes/kprobe_example.c': 'CONFIG_SAMPLE_KPROBES\n',
        'samples/vfs/Makefile': 'userprogs-always-y += test-fsmount\n',
        'samples/vfs/test-fsmount.c': 'make M=samples/vfs\n',
        'zigux/tests/runtime_atomic64_diff.zig': '\n'.join(REQUIRED_RUNTIME_ATOMIC64_MARKERS)
        + '\n',
        'zigux/tests/atomic64_diff.zig': 'const runtime_atomic64_diff = @import("runtime_atomic64_diff.zig");\n\ncomptime {\n    _ = runtime_atomic64_diff;\n}\n',
        'zigux/tests/phase4_runtime_atomic64_diff_survey.zig': '\n'.join(
            REQUIRED_RUNTIME_ATOMIC64_SURVEY_MARKERS
        )
        + '\nroadmap_atomic64_diff_present = true\n',
        'zigux/tests/phase4_runtime_atomic64_diff_manifest.json': json.dumps(
            {
                **PHASE4_RUNTIME_ATOMIC64_MANIFEST_EXPECTATIONS,
                'surveyed_commit': '0' * 40,
                'survey_summary': {
                    **PHASE4_RUNTIME_ATOMIC64_MANIFEST_EXPECTATIONS['survey_summary'],
                    'atomic64_test_c_lines': 277,
                    'runtime_atomic64_diff_lines': 561,
                    'roadmap_atomic64_wrapper_targets_runtime_diff': True,
                    'runtime_atomic64_diff_present': True,
                    'post_selftest_replay_present': True,
                    'phase4_build_uses_atomic64_wrapper': True,
                    'phase9_build_present': True,
                    'phase9_build_uses_runtime_atomic64_diff': True,
                    'runtime_atomic64_sample_present': True,
                    'tests_readme_runtime_atomic64_diff_present': True,
                },
                'threshold_plan': {
                    **PHASE4_RUNTIME_ATOMIC64_MANIFEST_EXPECTATIONS['threshold_plan'],
                    'scope': 'add, sub, bitwise, exchange, cmpxchg, add_unless, inc_not_zero, dec_if_positive, and selftest-family plus post-selftest replay set',
                    'why_not_approved_yet': 'The live gate is still a bounded rollback-readiness slice, so Phase 4 keeps correctness-only coverage until a broader atomic64 benchmark entrypoint is explicitly added and reviewed.',
                },
                'gaps': [
                    {
                        'id': 'phase4-runtime-atomic64-diff-gate',
                        'status': 'starter_landed',
                        'kind': 'bounded_gate',
                        'zigux_destination': 'zigux/tests/runtime_atomic64_diff.zig',
                        'why_now': 'bounded replay is live',
                    },
                    {
                        'id': 'phase4-validation-matrix-note',
                        'status': 'starter_landed',
                        'kind': 'ownership_note',
                        'zigux_destination': 'Documentation/zigux/phase4-validation-matrix.md',
                        'why_now': 'The validation matrix already names the rollback owner, the exact `threshold_pending_until_runtime_atomic64_scope_widens` threshold posture, the manifest-backed pending threshold plan in this survey packet, and the reversible-delivery evidence that keeps the current `lib/atomic64_test.c` anchor plus the shared `phase4_build.zig` entrypoint explicit for the live runtime atomic64 gate.',
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + '\n',
        'zigux/tests/phase4_test_fsmount_survey.zig': 'phase4-test-fsmount-survey-tests\n',
        'zigux/tests/phase4_test_fsmount_manifest.json': json.dumps(
            PHASE4_TEST_FSMOUNT_MANIFEST_EXPECTATIONS, indent=2, sort_keys=True
        )
        + '\n',
        'zigux/tests/phase4_perf_baseline_survey.zig': 'phase4-perf-baseline-survey-tests\n',
        'zigux/tests/phase4_perf_baseline_manifest.json': json.dumps(
            PHASE4_PERF_BASELINE_MANIFEST_EXPECTATIONS, indent=2, sort_keys=True
        )
        + '\n',
        'zigux/tests/bitmap_diff.zig': '\n'.join(REQUIRED_BITMAP_DIFF_MARKERS) + '\n',
        'zigux/tests/phase4_build.zig': '\n'.join(REQUIRED_PHASE4_BUILD_MARKERS) + '\n',
    }

    for relative_path, content in file_contents.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    gate_evidence_lines = [
        '# Phase 4 Gate Evidence',
        '',
        '## Status',
        '',
        '- `PHASE4_EVIDENCE_DATE=2026-04-30`',
        '- `PHASE4_EVIDENCE_MODE=github_connector_readback`',
        '- `PHASE4_EVIDENCE_SCOPE=rollback_ownership_and_lab_matrix_current_gate_definitions`',
    ]
    for marker, relative_path in PHASE4_GATE_EVIDENCE_BLOB_TARGETS.items():
        digest = git_blob_sha1(read_bytes(root, relative_path))
        gate_evidence_lines.append(f'- `{marker}={digest}`')
    gate_evidence_lines.extend(
        [
            '',
            '## Exact Readback Evidence',
            '',
            '- synthetic fixture keeps the current Phase 4 rollback packet hashes explicit',
            '',
            '## Current Conclusion',
            '',
            'The synthetic Phase 4 rollback-ownership and lab-matrix packet is aligned.',
            '',
        ]
    )
    (root / 'Documentation/zigux/phase4-gate-evidence.md').write_text(
        '\n'.join(gate_evidence_lines),
        encoding='utf-8',
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_validate_phase4_') as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        write_fixture_tree(tmp_root)

        missing = validate_root(tmp_root)
        assert not missing, missing

        makefile = tmp_root / 'zigux/Makefile'
        makefile.write_text(
            makefile.read_text(encoding='utf-8').replace(
                'scripts/zigux/validate-phase4.py --self-test\n',
                '',
            ),
            encoding='utf-8',
        )
        missing = validate_root(tmp_root)
        assert 'make:scripts/zigux/validate-phase4.py --self-test' in missing, missing

        write_fixture_tree(tmp_root)
        makefile = tmp_root / 'zigux/Makefile'
        makefile.write_text(
            makefile.read_text(encoding='utf-8').replace(
                'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py --self-test\n',
                '',
            ),
            encoding='utf-8',
        )
        missing = validate_root(tmp_root)
        assert (
            'make_exact:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py --self-test'
            in missing
        ), missing

        write_fixture_tree(tmp_root)
        makefile = tmp_root / 'zigux/Makefile'
        makefile.write_text(
            makefile.read_text(encoding='utf-8').replace(
                'cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py\n',
                '',
            ),
            encoding='utf-8',
        )
        missing = validate_root(tmp_root)
        assert (
            'make_exact:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-gate-evidence.py'
            in missing
        ), missing

        write_fixture_tree(tmp_root)
        checker = tmp_root / 'scripts/zigux/check-phase4-gate-evidence.py'
        checker.unlink()
        missing = validate_root(tmp_root)
        assert 'file:scripts/zigux/check-phase4-gate-evidence.py' in missing, missing

        write_fixture_tree(tmp_root)
        perf_baseline_manifest = tmp_root / 'zigux/tests/phase4_perf_baseline_manifest.json'
        perf_baseline_data = json.loads(perf_baseline_manifest.read_text(encoding='utf-8'))
        perf_baseline_data['survey_summary']['benchmark_command_unapproved'] = False
        perf_baseline_manifest.write_text(
            json.dumps(perf_baseline_data, indent=2, sort_keys=True) + '\n',
            encoding='utf-8',
        )
        missing = validate_root(tmp_root)
        assert (
            'phase4_perf_baseline_manifest.survey_summary.benchmark_command_unapproved:False'
            in missing
        ), missing

        write_fixture_tree(tmp_root)
        phase4_matrix = tmp_root / 'Documentation/zigux/phase4-validation-matrix.md'
        phase4_matrix.write_text(
            phase4_matrix.read_text(encoding='utf-8').replace(
                '| `zigux/tests/phase4_test_fsmount_survey.zig` | survey gate |',
                '| `zigux/tests/phase4_test_fsmount_survey_missing.zig` | survey gate |',
                1,
            ),
            encoding='utf-8',
        )
        missing = validate_root(tmp_root)
        assert (
            'phase4_matrix:missing_survey_row:zigux/tests/phase4_test_fsmount_survey.zig'
            in missing
        ), missing

        write_fixture_tree(tmp_root)
        gate_evidence = tmp_root / 'Documentation/zigux/phase4-gate-evidence.md'
        gate_evidence.write_text(
            gate_evidence.read_text(encoding='utf-8').replace(
                'PHASE4_BUILD_BLOB_SHA=',
                'PHASE4_BUILD_BLOB_SHA=broken',
                1,
            ),
            encoding='utf-8',
        )
        missing = validate_root(tmp_root)
        assert any(
            marker.startswith('phase4_gate_evidence:PHASE4_BUILD_BLOB_SHA:')
            for marker in missing
        ), missing

        write_fixture_tree(tmp_root)
        landed_fsmount = tmp_root / 'samples/zigux/test_fsmount.zig'
        landed_fsmount.parent.mkdir(parents=True, exist_ok=True)
        landed_fsmount.write_text('// synthetic landed sample\n', encoding='utf-8')
        missing = validate_root(tmp_root)
        assert (
            'roadmap_gap:item_should_still_be_absent:samples/zigux/test_fsmount.zig'
            in missing
        ), missing

    print('PHASE4_VALIDATOR_SELF_TEST=pass')
    return 0


def required_marker_count() -> int:
    return (
        len(REQUIRED_MAKE_MARKERS)
        + len(EXACT_REQUIRED_MAKE_LINES)
        + len(REQUIRED_WORKFLOW_MARKERS)
        + len(REQUIRED_DOC_MARKERS)
        + sum(len(markers) for _, markers in REQUIRED_DOC_MARKER_GROUPS)
        + len(FORBIDDEN_DOC_MARKERS)
        + len(REQUIRED_TESTS_README_MARKERS)
        + len(REQUIRED_SCRIPT_README_MARKERS)
        + len(REQUIRED_DOC_README_MARKERS)
        + len(REQUIRED_PHASE4_MATRIX_MARKERS)
        + len(REQUIRED_ARTIFACT_DIFF_MARKERS)
        + len(REQUIRED_PHASE4_BUILD_MARKERS)
        + len(REQUIRED_RUNTIME_ATOMIC64_MARKERS)
        + len(REQUIRED_RUNTIME_ATOMIC64_SURVEY_MARKERS)
        + len(REQUIRED_BITMAP_DIFF_MARKERS)
        + len(REQUIRED_GATE_EVIDENCE_MARKERS)
        + len(PHASE4_GATE_EVIDENCE_BLOB_TARGETS)
        + sum(
            len(expectation.get('exact_check_markers', []))
            + (1 if expectation.get('rollback_evidence_gap') is not None else 0)
            + len(expectation.get('local_replay_markers', []))
            for expectation in PHASE4_GATE_EXPECTATIONS.values()
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate the Phase 4 diff bundle.')
    parser.add_argument(
        '--self-test',
        action='store_true',
        help='Run the built-in synthetic marker-contract check.',
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_markers = validate_root(ROOT)
    if missing_markers:
        print('PHASE4_VALIDATION=fail')
        print('MISSING_PHASE4_MARKERS_START')
        for marker in missing_markers:
            print(marker)
        print('MISSING_PHASE4_MARKERS_END')
        return 1

    print('PHASE4_VALIDATION=pass')
    print(f'PHASE4_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}')
    print(f'PHASE4_REQUIRED_MARKER_COUNT={required_marker_count()}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

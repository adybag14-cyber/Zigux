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
        'local_replay_test': 'phase4-runtime-atomic64-diff-tests',
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
        'threshold_status': 'correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior checkpoints',
        'threshold_posture': 'threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks',
        'gate_scope': 'bounded bitmap range, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior replay',
        'threshold_scope': 'range, cross-boundary set-clear, summary, exact nth-lookup, and copy-behavior checkpoints',
        'local_replay_test': 'phase4-bitmap-diff-tests',
        'reversible_delivery': '`lib/test_bitmap.c` stays the source of truth, and removing `bitmap_diff.zig` from the shared `phase4_build.zig` entrypoint falls back to the existing broad bitmap parity checks',
    },
}

REQUIRED_FILES = [
    'scripts/zigux/artifact_diff.py',
    'scripts/zigux/validate-phase4.py',
    'Documentation/zigux/artifact-diff.md',
    'Documentation/zigux/phase4-validation-matrix.md',
    'zigux/Makefile',
    '.github/workflows/zigux-bootstrap.yml',
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
]

REQUIRED_MAKE_MARKERS = [
    'PHONY += phase4-validate phase4-test phase4',
    'phase4-validate:',
    'scripts/zigux/artifact_diff.py --self-test',
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
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
    'scripts/zigux/validate-phase4.py',
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
    'make -C zigux phase4-validate',
    'validate-phase4.py',
    'Phase 4 flow',
    'phase4_build.zig',
    'phase4-validation-matrix.md',
    'reversible-delivery evidence',
]

REQUIRED_DOC_README_MARKERS = [
    'Phase 4 notes',
    'make -C zigux phase4-validate',
    'python3 scripts/zigux/artifact_diff.py --self-test',
    'validate-phase4.py',
    'phase4-validation-matrix.md',
    'Validate Phase 4 diff gates',
    'Run Phase 4 diff tests',
    'reversible-delivery evidence',
]

REQUIRED_PHASE4_MATRIX_MARKERS = [
    'scripts/zigux/artifact_diff.py --self-test',
    'deterministic_preflight_required_for_host_side_diff_tools',
    'runtime_atomic64_diff.zig',
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
        'measurability_gap': 'reserve `Validation and Perf Team` as both survey owner and rollback owner while the current replay stays on the C anchor via `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`; no hard timing threshold is approved before a bounded Zig sample lands',
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
    'bitmap_diff.zig',
    'phase4-runtime-atomic64-diff-tests',
    'phase4-bitmap-diff-tests',
]

REQUIRED_RUNTIME_ATOMIC64_MARKERS = [
    'addUnlessCounter',
    'incNotZeroCounter',
    'decIfPositiveCounter',
    'add_unless, and inc_not_zero expectations',
    'checked_guard_paths',
    'error.InvalidLifecycleTransition, module.incNotZeroCounter()',
    'runtime atomic64 diff gate keeps post-selftest replay explicit',
]

REQUIRED_BITMAP_DIFF_MARKERS = [
    'test "bitmap diff gate replays bounded lib/test_bitmap.c range expectations"',
    'test_fill_set bitmap_fill rounds 35 bits to one full word',
    'test_zero_clear bitmap_zero rounds 115 bits to two full words',
    'test "bitmap diff gate records exact cross-boundary set and clear checks"',
    'test_fill_set bitmap_set crosses the 79..97 window without disturbing the gap',
    'test_zero_clear bitmap_clear crosses the 79..97 window without disturbing the prefix',
    'test "bitmap diff gate records exact full-width fill and zero endpoints"',
    'test_find_nth_bit starter population',
    'test "bitmap diff gate records exact bounded copy checks"',
    'test_copy partial-word tail clearing at 109 bits',
    'test_copy aligned-on-word-length at 97 bits keeps the stale tail word visible',
    'test_copy_clear_tail keeps the 109-bit cleared-tail contract explicit',
    'test "bitmap diff gate records exact bounded find_nth_bit checks"',
    'test_find_nth_bit full-width nth 7',
    'test_find_nth_bit truncated-width nth 8 returns nbits',
    'roundedPrefixLen',
    'fillPrefix',
    'zeroPrefix',
    'copyFrom',
    'findNthSet',
    'firstSet',
    'firstZero',
    'weight',
]


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding='utf-8')


def collect_missing_markers(text: str, prefix: str, markers: list[str]) -> list[str]:
    missing = []
    for marker in markers:
        if marker not in text:
            missing.append(f'{prefix}:{marker}')
    return missing


def check_gate_matrix_alignment(phase4_matrix: str, gate_name: str, expectation: dict[str, object]) -> list[str]:
    gate_heading = f"### `zigux/tests/{gate_name}`"
    gate_heading_index = phase4_matrix.find(gate_heading)
    if gate_heading_index == -1:
        return [f'phase4_matrix:missing_gate_heading:{gate_name}']

    next_heading_index = phase4_matrix.find('\n### `zigux/tests/', gate_heading_index + len(gate_heading))
    matrix_heading_index = phase4_matrix.find('\n## Lab And CI Matrix', gate_heading_index + len(gate_heading))
    gate_block_end = matrix_heading_index
    if next_heading_index != -1 and next_heading_index < matrix_heading_index:
        gate_block_end = next_heading_index
    gate_block = phase4_matrix[gate_heading_index:gate_block_end]

    row_prefix = f"| `zigux/tests/{gate_name}` |"
    row = next(
        (line for line in phase4_matrix.splitlines() if line.startswith(row_prefix)),
        '',
    )

    missing = []
    if f"- owner: `{expectation['owner']}`" not in gate_block:
        missing.append(f"phase4_matrix:owner:{gate_name}:{expectation['owner']}")
    if f"- rollback owner: `{expectation['rollback_owner']}`" not in gate_block:
        missing.append(
            f"phase4_matrix:rollback_owner:{gate_name}:{expectation['rollback_owner']}"
        )
    if f"- fallback path: {expectation['fallback_path']}" not in gate_block:
        missing.append(
            f"phase4_matrix:fallback_path:{gate_name}:{expectation['fallback_path']}"
        )
    exact_check_markers = expectation.get('exact_check_markers')
    if exact_check_markers is not None:
        if '- exact bounded checks:' not in gate_block:
            missing.append(f'phase4_matrix:missing_exact_checks_heading:{gate_name}')
        for marker in exact_check_markers:
            if marker not in gate_block:
                missing.append(f'phase4_matrix:exact_check_marker:{gate_name}:{marker}')
    if f"- perf threshold status: {expectation['threshold_status']}" not in gate_block:
        missing.append(
            f"phase4_matrix:threshold_status:{gate_name}:{expectation['threshold_status']}"
        )
    if expectation['threshold_scope'] not in gate_block:
        missing.append(
            f"phase4_matrix:threshold_scope:{gate_name}:{expectation['threshold_scope']}"
        )
    if expectation['gate_scope'] not in row:
        missing.append(f"phase4_matrix:gate_scope:{gate_name}:{expectation['gate_scope']}")
    if expectation['threshold_posture'] not in row:
        missing.append(
            f"phase4_matrix:threshold_posture:{gate_name}:{expectation['threshold_posture']}"
        )
    if expectation['owner'] not in row:
        missing.append(f"phase4_matrix:matrix_owner:{gate_name}:{expectation['owner']}")
    if expectation['rollback_owner'] not in row:
        missing.append(
            f"phase4_matrix:matrix_rollback_owner:{gate_name}:{expectation['rollback_owner']}"
        )
    if expectation['local_replay_test'] not in row:
        missing.append(
            f"phase4_matrix:local_replay_test:{gate_name}:{expectation['local_replay_test']}"
        )
    if expectation['reversible_delivery'] not in row:
        missing.append(
            f"phase4_matrix:reversible_delivery:{gate_name}:{expectation['reversible_delivery']}"
        )
    return missing


def check_roadmap_gap_alignment(phase4_matrix: str, item_name: str, expectation: dict[str, str]) -> list[str]:
    row_prefixes = [
        f'| `{item_name}`',
        f'| {item_name} |',
    ]
    row = next(
        (
            line
            for line in phase4_matrix.splitlines()
            if any(line.startswith(prefix) for prefix in row_prefixes)
        ),
        '',
    )
    if not row:
        return [f'phase4_matrix:missing_gap_row:{item_name}']

    missing = []
    for key, fragment in expectation.items():
        if fragment not in row:
            missing.append(f'phase4_matrix:gap_{key}:{item_name}:{fragment}')
    return missing


def validate_root(root: Path) -> list[str]:
    missing_files = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing_files:
        return [f'file:{path}' for path in missing_files]

    makefile = read_text(root, 'zigux/Makefile')
    workflow = read_text(root, '.github/workflows/zigux-bootstrap.yml')
    artifact_diff = read_text(root, 'scripts/zigux/artifact_diff.py')
    artifact_doc = read_text(root, 'Documentation/zigux/artifact-diff.md')
    tests_readme = read_text(root, 'zigux/tests/README.md')
    script_readme = read_text(root, 'scripts/zigux/README.md')
    doc_readme = read_text(root, 'Documentation/zigux/README.md')
    phase4_matrix = read_text(root, 'Documentation/zigux/phase4-validation-matrix.md')
    phase4_build = read_text(root, 'zigux/tests/phase4_build.zig')
    runtime_atomic64_diff = read_text(root, 'zigux/tests/runtime_atomic64_diff.zig')
    bitmap_diff = read_text(root, 'zigux/tests/bitmap_diff.zig')

    missing_markers: list[str] = []
    missing_markers.extend(collect_missing_markers(makefile, 'make', REQUIRED_MAKE_MARKERS))
    missing_markers.extend(collect_missing_markers(workflow, 'workflow', REQUIRED_WORKFLOW_MARKERS))
    missing_markers.extend(collect_missing_markers(artifact_doc, 'doc', REQUIRED_DOC_MARKERS))
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
        collect_missing_markers(bitmap_diff, 'bitmap_diff', REQUIRED_BITMAP_DIFF_MARKERS)
    )

    for gate_name, expectation in PHASE4_GATE_EXPECTATIONS.items():
        missing_markers.extend(check_gate_matrix_alignment(phase4_matrix, gate_name, expectation))

    for item_name, expectation in ROADMAP_GAP_EXPECTATIONS.items():
        missing_markers.extend(check_roadmap_gap_alignment(phase4_matrix, item_name, expectation))

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
        '- current repo reality:',
        '  - `scripts/zigux/artifact_diff.py`',
        '  - `zigux/tests/runtime_atomic64_diff.zig`',
        '  - `zigux/tests/bitmap_diff.zig`',
        '  - `zigux/tests/phase4_build.zig`',
        '  - `scripts/zigux/validate-phase4.py`',
        '  - `.github/workflows/zigux-bootstrap.yml`',
        '- rollback owner',
        '- lab and CI matrix',
        '- reversible delivery evidence',
        '- perf threshold status',
        '- Validate Phase 4 diff gates',
        '- Run Phase 4 diff tests',
        '- make -C zigux phase4-validate',
        '- make -C zigux phase4-test',
        '- scripts/zigux/artifact_diff.py --self-test',
        '- deterministic_preflight_required_for_host_side_diff_tools',
        '- phase4-runtime-atomic64-diff-tests',
        '- phase4-bitmap-diff-tests',
        '',
        '## Why this exists',
        '',
        '- the bounded rollback owner for each live Phase 4 gate',
        '- the current perf threshold status for those gates',
        '- the lab and CI matrix that replays the gates today',
        '- the reversible-delivery evidence that ties each shipped Zig gate back to its current C anchor if the shared entrypoint has to drop that gate',
        '- the shared artifact comparator self-test that now runs before the Phase 4 validator claims the rollback-readiness bundle is still aligned',
        '- one isolated runtime atomic64 replay command that can be run without depending on the bitmap lane staying green on the same head',
        '',
        '## Gate Ownership',
        '',
        '### `scripts/zigux/artifact_diff.py --self-test`',
        '',
        '- anchor: `scripts/zigux/` host-side diff and layout tooling',
        '- phase bucket: `Phase 4 deterministic artifact-diff preflight for host-side tools`',
        '- owner: `Validation and Perf Team`',
        '- rollback owner: `Validation and Perf Team`',
        '- fallback path: keep the shared self-test wired into `make -C zigux phase4-validate` and fail closed before the rollback-readiness packet claims the host-side diff tooling is aligned',
        '- perf threshold status: deterministic correctness-only preflight today; no timing threshold is relevant until a future Phase 4 lane adds a benchmarked host-tool diff workload',
        '',
    ]

    for gate_name, expectation in PHASE4_GATE_EXPECTATIONS.items():
        lines.extend(
            [
                f"### `zigux/tests/{gate_name}`",
                '',
                f"- owner: `{expectation['owner']}`",
                f"- rollback owner: `{expectation['rollback_owner']}`",
                f"- fallback path: {expectation['fallback_path']}",
            ]
        )
        exact_check_markers = expectation.get('exact_check_markers')
        if exact_check_markers is not None:
            exact_checks = ', '.join(exact_check_markers)
            lines.append(f'- exact bounded checks: {exact_checks}')
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
            '| `scripts/zigux/artifact_diff.py --self-test` | deterministic text, JSON, SHA-256, and missing-file comparison self-test for the shared host-side diff tooling | `Validation and Perf Team` | `Validation and Perf Team` | workflow step `Validate Phase 4 diff gates`, which calls `make -C zigux phase4-validate` and therefore reruns the shared self-test before the shipped rollback gates | `make -C zigux phase4-validate` or direct `python3 scripts/zigux/artifact_diff.py --self-test` replay when the helper changes | `scripts/zigux/artifact_diff.py` stays the shared comparator for the bounded Phase 4 host-side tooling packet, and removing its self-test from `phase4-validate` would drop the roadmap-backed deterministic preflight that now guards the rollback-readiness docs and diff checks | `deterministic_preflight_required_for_host_side_diff_tools` |',
        ]
    )

    for gate_name, expectation in PHASE4_GATE_EXPECTATIONS.items():
        lines.append(
            '| `zigux/tests/{gate}` | {purpose} | `{owner}` | `{rollback_owner}` | workflow steps `Validate Phase 4 diff gates` and `Run Phase 4 diff tests` | `make -C zigux phase4-validate`, `make -C zigux phase4-test`, and `{local_replay}` | {reversible_delivery} | `{threshold_posture}` |'.format(
                gate=gate_name,
                purpose=expectation['gate_scope'],
                owner=expectation['owner'],
                rollback_owner=expectation['rollback_owner'],
                local_replay=expectation['local_replay_test'],
                reversible_delivery=expectation['reversible_delivery'],
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
        'zigux/Makefile': '\n'.join(REQUIRED_MAKE_MARKERS) + '\n',
        '.github/workflows/zigux-bootstrap.yml': '\n'.join(REQUIRED_WORKFLOW_MARKERS) + '\n',
        'zigux/tests/runtime_atomic64_diff.zig': '\n'.join(REQUIRED_RUNTIME_ATOMIC64_MARKERS) + '\n',
        'zigux/tests/bitmap_diff.zig': '\n'.join(REQUIRED_BITMAP_DIFF_MARKERS) + '\n',
        'zigux/tests/phase4_build.zig': '\n'.join(REQUIRED_PHASE4_BUILD_MARKERS) + '\n',
    }

    for relative_path, content in file_contents.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')


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

    print('PHASE4_VALIDATOR_SELF_TEST=pass')
    return 0


def required_marker_count() -> int:
    return (
        len(REQUIRED_MAKE_MARKERS)
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
        + len(REQUIRED_BITMAP_DIFF_MARKERS)
        + sum(
            len(expectation.get('exact_check_markers', []))
            + (1 if expectation.get('exact_check_markers') is not None else 0)
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
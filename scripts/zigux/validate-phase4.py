#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / 'scripts' / 'zigux' / 'artifact_diff.py',
    ROOT / 'scripts' / 'zigux' / 'validate-phase4.py',
    ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md',
    ROOT / 'Documentation' / 'zigux' / 'phase4-validation-matrix.md',
    ROOT / 'zigux' / 'Makefile',
    ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml',
    ROOT / 'zigux' / 'tests' / 'runtime_atomic64_diff.zig',
    ROOT / 'zigux' / 'tests' / 'bitmap_diff.zig',
    ROOT / 'zigux' / 'tests' / 'phase4_build.zig',
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print('PHASE4_VALIDATION=fail')
    print('MISSING_PHASE4_FILES_START')
    for item in missing:
        print(item)
    print('MISSING_PHASE4_FILES_END')
    sys.exit(1)

makefile = (ROOT / 'zigux' / 'Makefile').read_text(encoding='utf-8')
workflow = (ROOT / '.github' / 'workflows' / 'zigux-bootstrap.yml').read_text(encoding='utf-8')
artifact_diff = (ROOT / 'scripts' / 'zigux' / 'artifact_diff.py').read_text(encoding='utf-8')
artifact_doc = (ROOT / 'Documentation' / 'zigux' / 'artifact-diff.md').read_text(encoding='utf-8')
tests_readme = (ROOT / 'zigux' / 'tests' / 'README.md').read_text(encoding='utf-8')
script_readme = (ROOT / 'scripts' / 'zigux' / 'README.md').read_text(encoding='utf-8')
doc_readme = (ROOT / 'Documentation' / 'zigux' / 'README.md').read_text(encoding='utf-8')
phase4_matrix = (ROOT / 'Documentation' / 'zigux' / 'phase4-validation-matrix.md').read_text(encoding='utf-8')
phase4_build = (ROOT / 'zigux' / 'tests' / 'phase4_build.zig').read_text(encoding='utf-8')
runtime_atomic64_diff = (ROOT / 'zigux' / 'tests' / 'runtime_atomic64_diff.zig').read_text(encoding='utf-8')
bitmap_diff = (ROOT / 'zigux' / 'tests' / 'bitmap_diff.zig').read_text(encoding='utf-8')

phase4_gate_expectations = {
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

required_make_markers = [
    'PHONY += phase4-validate phase4-test phase4',
    'phase4-validate:',
    'scripts/zigux/artifact_diff.py --self-test',
    'scripts/zigux/validate-phase4.py',
    'phase4-test:',
    'zigux/tests/phase4_build.zig',
]
required_workflow_markers = [
    'Validate Phase 4 diff gates',
    'Run Phase 4 diff tests',
    'make -C zigux phase4-validate',
    'make -C zigux phase4-test',
]
required_doc_markers = [
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
required_doc_marker_groups = [
    (
        'reversible_delivery_link',
        [
            'reversible-delivery evidence',
            'current C anchor',
            'shared Phase 4 entrypoint',
        ],
    ),
]
forbidden_doc_markers = [
    'future Phase 2 tooling work will reuse',
    'reuse the same artifact-diff pattern for Phase 2 dual-implementation and bridge outputs such as `fixdep`, `genksyms`, `genksyms_crc`, `kconfig_bridge`, and `mk_elfconfig`',
]
required_tests_readme_markers = [
    'zigux/tests/runtime_atomic64_diff.zig',
    'zigux/tests/bitmap_diff.zig',
    'zigux/tests/phase4_build.zig',
    'scripts/zigux/validate-phase4.py',
]
required_script_readme_markers = [
    'artifact_diff.py --self-test',
    'make -C zigux phase4-validate',
    'validate-phase4.py',
    'Phase 4 flow',
    'phase4_build.zig',
    'phase4-validation-matrix.md',
    'reversible-delivery evidence',
]
required_doc_readme_markers = [
    'Phase 4 notes',
    'make -C zigux phase4-validate',
    'python3 scripts/zigux/artifact_diff.py --self-test',
    'validate-phase4.py',
    'phase4-validation-matrix.md',
    'Validate Phase 4 diff gates',
    'Run Phase 4 diff tests',
    'reversible-delivery evidence',
]
required_phase4_matrix_markers = [
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
roadmap_gap_expectations = {
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
required_artifact_diff_markers = [
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
required_phase4_build_markers = [
    'runtime_atomic64_diff.zig',
    'bitmap_diff.zig',
    'phase4-runtime-atomic64-diff-tests',
    'phase4-bitmap-diff-tests',
]
required_runtime_atomic64_markers = [
    'addUnlessCounter',
    'incNotZeroCounter',
    'decIfPositiveCounter',
    'add_unless, and inc_not_zero expectations',
    'checked_guard_paths',
    'error.InvalidLifecycleTransition, module.incNotZeroCounter()',
    'runtime atomic64 diff gate keeps post-selftest replay explicit',
]
required_bitmap_diff_markers = [
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

missing_markers = []
for marker in required_make_markers:
    if marker not in makefile:
        missing_markers.append(f'make:{marker}')
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f'workflow:{marker}')
for marker in required_doc_markers:
    if marker not in artifact_doc:
        missing_markers.append(f'doc:{marker}')
for group_name, markers in required_doc_marker_groups:
    for marker in markers:
        if marker not in artifact_doc:
            missing_markers.append(f'doc_group:{group_name}:{marker}')
for marker in forbidden_doc_markers:
    if marker in artifact_doc:
        missing_markers.append(f'doc_stale:{marker}')
for marker in required_tests_readme_markers:
    if marker not in tests_readme:
        missing_markers.append(f'tests_readme:{marker}')
for marker in required_script_readme_markers:
    if marker not in script_readme:
        missing_markers.append(f'script_readme:{marker}')
for marker in required_doc_readme_markers:
    if marker not in doc_readme:
        missing_markers.append(f'doc_readme:{marker}')
for marker in required_phase4_matrix_markers:
    if marker not in phase4_matrix:
        missing_markers.append(f'phase4_matrix:{marker}')
for marker in required_artifact_diff_markers:
    if marker not in artifact_diff:
        missing_markers.append(f'artifact_diff:{marker}')
for marker in required_phase4_build_markers:
    if marker not in phase4_build:
        missing_markers.append(f'phase4_build:{marker}')
for marker in required_runtime_atomic64_markers:
    if marker not in runtime_atomic64_diff:
        missing_markers.append(f'runtime_atomic64_diff:{marker}')
for marker in required_bitmap_diff_markers:
    if marker not in bitmap_diff:
        missing_markers.append(f'bitmap_diff:{marker}')


def check_gate_matrix_alignment(gate_name: str, expectation: dict[str, str]) -> list[str]:
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


for gate_name, expectation in phase4_gate_expectations.items():
    missing_markers.extend(check_gate_matrix_alignment(gate_name, expectation))


def check_roadmap_gap_alignment(item_name: str, expectation: dict[str, str]) -> list[str]:
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


for item_name, expectation in roadmap_gap_expectations.items():
    missing_markers.extend(check_roadmap_gap_alignment(item_name, expectation))

if missing_markers:
    print('PHASE4_VALIDATION=fail')
    print('MISSING_PHASE4_MARKERS_START')
    for marker in missing_markers:
        print(marker)
    print('MISSING_PHASE4_MARKERS_END')
    sys.exit(1)

print('PHASE4_VALIDATION=pass')
print(f'PHASE4_REQUIRED_FILE_COUNT={len(required_files)}')
print(
    'PHASE4_REQUIRED_MARKER_COUNT='
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_doc_markers) + sum(len(markers) for _, markers in required_doc_marker_groups) + len(forbidden_doc_markers) + len(required_tests_readme_markers) + len(required_script_readme_markers) + len(required_doc_readme_markers) + len(required_phase4_matrix_markers) + len(required_artifact_diff_markers) + len(required_phase4_build_markers) + len(required_runtime_atomic64_markers) + len(required_bitmap_diff_markers) + sum(len(expectation.get('exact_check_markers', [])) + (1 if expectation.get('exact_check_markers') is not None else 0) for expectation in phase4_gate_expectations.values())}"
)

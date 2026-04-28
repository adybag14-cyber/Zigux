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
        'threshold_status': 'correctness-only gate today; no hard timing threshold is approved until the lane widens beyond the current bounded exchange, cmpxchg, add_unless, inc_not_zero, and selftest-family replay set',
        'threshold_posture': 'threshold_pending_until_runtime_atomic64_scope_widens',
        'gate_scope': 'exchange, cmpxchg, add_unless, inc_not_zero, and selftest-family replay',
        'threshold_scope': 'exchange, cmpxchg, add_unless, inc_not_zero, and selftest-family replay set',
        'local_replay_test': 'phase4-runtime-atomic64-diff-tests',
        'reversible_delivery': '`lib/atomic64_test.c` stays the source of truth, and removing `runtime_atomic64_diff.zig` from the shared `phase4_build.zig` entrypoint is the documented rollback move while the existing Phase 9 runtime atomic64 starter remains the forward path',
    },
    'bitmap_diff.zig': {
        'owner': 'Shared Subsystems Pod',
        'rollback_owner': 'Shared Subsystems Pod',
        'fallback_path': 'keep the current C anchor as the source of truth and drop back to the existing broad bitmap parity checks if the Zig replay gate regresses',
        'threshold_status': 'correctness-only gate today; no hard timing threshold is approved until the lane grows past the current bounded range, rounded-prefix, summary, exact nth-lookup, and copy-behavior checkpoints',
        'threshold_posture': 'threshold_pending_until_bitmap_gate_grows_beyond_bounded_correctness_checks',
        'gate_scope': 'bounded bitmap range, rounded-prefix, summary, exact nth-lookup, and copy-behavior replay',
        'threshold_scope': 'range, rounded-prefix, summary, exact nth-lookup, and copy-behavior checkpoints',
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
    'survey owner, rollback owner, and Zig lab matrix stay unassigned while the current replay stays on the C anchor via `make M=samples/vfs`; no hard timing threshold is approved before a bounded Zig sample lands',
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
        'measurability_gap': 'survey owner, rollback owner, and Zig lab matrix stay unassigned while the current replay stays on the C anchor via `make M=samples/vfs`; no hard timing threshold is approved before a bounded Zig sample lands',
        'next_bounded_step': 'add a survey or starter gate that names one survey owner, one rollback owner, and one replay command before claiming this anchor as active Phase 4 work',
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
    "details['expected_exists'] = expected.exists()",
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
    'add_unless, and inc_not_zero expectations',
    'checked_guard_paths',
    'error.InvalidLifecycleTransition, module.incNotZeroCounter()',
]
required_bitmap_diff_markers = [
    'test "bitmap diff gate records exact partial fill and zero checks"',
    'bitmap.fill(map[0..bitmap.bitsToWords(35)], 35);',
    'bitmap.weight(&map, bitmap_nbits)',
    'find_bit.findFirstBit(&map, bitmap_nbits)',
    'find_bit.findFirstZeroBit(&map, bitmap_nbits)',
    'test "bitmap diff gate records exact copy and copyClearTail checks"',
    'bitmap.copy(&dst, &src, nbits);',
    'bitmap.copyClearTail(&dst, &src, nbits);',
    'bitmap.lastWordMask(nbits)',
    'test "bitmap diff gate records exact scnprintf and masked xor checks"',
    'bitmap.scnprintf(&map, 32, &buffer)',
    'bitmap.scnprintf(&map, 8, &trunc_buffer)',
    'bitmap.xorBits(&dst, &lhs, &rhs, 4);',
    'find_bit.findFirstZeroBit(&dst, 4)',
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
    for marker in markers"
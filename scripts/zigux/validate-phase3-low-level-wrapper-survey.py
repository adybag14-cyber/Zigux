#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
BUILD_REL = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
TEST_REL = Path("zigux/tests/phase3_low_level_wrappers.zig")
ATOMIC_REL = Path("zigux/helpers/atomic.zig")
BARRIER_REL = Path("zigux/helpers/barrier.zig")
MMIO_REL = Path("zigux/helpers/mmio.zig")
ALLOCATOR_POLICY_REL = Path("zigux/helpers/allocator_policy.zig")
PANIC_POLICY_REL = Path("zigux/helpers/panic_policy.zig")
NARROW_REL = Path("zigux/unsafe/narrow.zig")
ABI_SLICE_REL = Path("Documentation/zigux/phase3-abi-slice.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig",
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetchadd-fetchsub-fetchand-fetchor-fetchxor-fetchnand-fetchmin-fetchmax-compareexchange-compareexchangeweak",
    "PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig",
    "PHASE3_BARRIER_SCOPE=acquire-release-full-acquirerelease",
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_MMIO_SCOPE=range-read-write-8-16-32-64-plus-interop-policy-and-policy-byte-entrypoints",
    "PHASE3_ALLOCATOR_POLICY_PATH=zigux/helpers/allocator_policy.zig",
    "PHASE3_ALLOCATOR_POLICY_SCOPE=interop-policy-mode-decoding-caller-provided-gating-and-global-fallback-gating",
    "PHASE3_PANIC_POLICY_PATH=zigux/helpers/panic_policy.zig",
    "PHASE3_PANIC_POLICY_SCOPE=interop-policy-mode-decoding-action-selection-and-returnability-gating",
    "PHASE3_NARROW_UNSAFE_PATH=zigux/unsafe/narrow.zig",
    "PHASE3_LOW_LEVEL_BUILD_PATH=zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig",
    "PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
)

REQUIRED_SURVEY_SNIPPETS = (
    "64-bit MMIO coverage in the focused test route",
    "interop-policy and policy-byte MMIO entrypoints in the focused test route",
    "raw-pointer bridge scope gates in `zigux/unsafe/narrow.zig` and the focused test route",
    "non-`seq_cst` ordering coverage and signed atomic edges in the focused test route",
    "barrier-locality and handoff replays",
    "allocator policy mode decoding, caller-provided gating, and fallback gating in the focused test route",
    "panic policy mode decoding, action selection, and returnability gating in the focused test route",
)

REQUIRED_BUILD_SNIPPETS = (
    '.root_source_file = b.path("../bindings/abi.zig")',
    '.root_source_file = b.path("../unsafe/narrow.zig")',
    '.root_source_file = b.path("../helpers/atomic.zig")',
    '.root_source_file = b.path("../helpers/barrier.zig")',
    '.root_source_file = b.path("../helpers/mmio.zig")',
    '.root_source_file = b.path("../helpers/allocator_policy.zig")',
    '.root_source_file = b.path("../helpers/panic_policy.zig")',
    '.root_source_file = b.path("phase3_low_level_wrappers.zig")',
    'root_module.addImport("abi_bindings", abi_bindings_module);',
    'root_module.addImport("atomic_helpers", atomic_helpers_module);',
    'root_module.addImport("barrier_helpers", barrier_helpers_module);',
    'root_module.addImport("mmio_helpers", mmio_helpers_module);',
    'root_module.addImport("narrow_unsafe", narrow_unsafe_module);',
    'root_module.addImport("allocator_policy_helpers", allocator_policy_helpers_module);',
    'root_module.addImport("panic_policy_helpers", panic_policy_helpers_module);',
    '"phase3-low-level-wrappers-test"',
)

REQUIRED_TEST_SNIPPETS = (
    'test "phase3 low-level wrappers keep mmio interop policy gates reviewable"',
    'test "phase3 low-level wrappers keep raw pointer bridge policy gates reviewable"',
    'test "phase3 low-level wrappers keep non-seq-cst orderings and signed atomic edges reviewable"',
    'test "phase3 low-level wrappers keep barrier locality reviewable"',
    'test "phase3 low-level wrappers keep barrier handoff reviewable"',
    'test "phase3 low-level wrappers keep allocator and panic policy helpers reviewable"',
    'mmio.write64(base, @sizeOf(u64), 0x0123_4567_89ab_cdef);',
    'mmio.write64InteropPolicyByte(base, 8, 0xfedc_ba98_7654_3210, @intFromEnum(abi.UnsafeScope.volatile_mmio));',
    'const scoped_const_ptr = try narrow.constPointerAtInteropPolicyBytes(u32, third_addr, 2, 0);',
    'try narrow.writeValueAtInteropPolicyBytes(u32, third_addr, 66, 2, 0);',
    'atomic.fetchNand(u32, &value, 10, .seq_cst)',
    'atomic.fetchMin(i32, &ordered_fetch_value, -7, .acquire)',
    'atomic.compareExchangeWeak(u32, &weak_release_value, 13, 19, .release, .monotonic)',
    'allocator_policy.modeFromInteropPolicy(caller_abort_policy)',
    'allocator_policy.permitsGlobalFallbackInteropPolicy(arena_warn_policy)',
    'panic_policy.actionForInteropPolicy(heap_bug_policy)',
    'panic_policy.canReturnInteropPolicy(arena_warn_policy)',
)

REQUIRED_ATOMIC_SNIPPETS = (
    'pub fn fetchNand(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {',
    'pub fn fetchMin(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {',
    'pub fn fetchMax(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {',
    'pub fn compareExchangeWeak(',
    'test "phase3 atomic wrappers keep non-seq-cst orderings reviewable"',
)

REQUIRED_BARRIER_SNIPPETS = (
    'pub fn acquireRelease() void {',
    'test "phase3 barrier wrappers keep barrier locality reviewable"',
    'test "phase3 barrier wrappers keep barrier handoff reviewable"',
)

REQUIRED_ALLOCATOR_POLICY_SNIPPETS = (
    'pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.AllocatorMode {',
    'pub fn recognizesInteropPolicyBytes(mode: u8, reserved: u8) bool {',
    'pub fn requiresExplicitCallerInteropPolicy(policy: abi.InteropPolicy) bool {',
    'pub fn permitsGlobalFallbackInteropPolicy(policy: abi.InteropPolicy) bool {',
)

REQUIRED_PANIC_POLICY_SNIPPETS = (
    'pub const Action = enum {',
    'pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.PanicMode {',
    'pub fn actionForInteropPolicy(policy: abi.InteropPolicy) ?Action {',
    'pub fn canReturnInteropPolicy(policy: abi.InteropPolicy) bool {',
)

REQUIRED_NARROW_SNIPPETS = (
    'pub const UnsafeScopeTag = enum(u8) {',
    'volatile_mmio = 1,',
    'raw_pointer_bridge = 2,',
    'pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {',
    'pub fn requireRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {',
    'pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {',
    'pub fn requireRawPointerBridgeByte(unsafe_scope: u8) UnsafeScopeError!void {',
    'pub fn pointerAtInteropPolicyBytes(',
    'pub fn pointerAtInteropPolicy(',
    'pub fn pointerAtByte(',
    'pub fn constSliceAtInteropPolicyBytes(',
    'pub fn constSliceAtInteropPolicy(',
    'pub fn constSliceAtByte(',
    'pub fn constPointerAtInteropPolicyBytes(',
    'pub fn constPointerAtInteropPolicy(',
    'pub fn constPointerAtByte(',
    'pub fn writeValueAtInteropPolicyBytes(',
    'pub fn writeValueAtInteropPolicy(',
    'pub fn writeValueAtByte(',
)

REFERENCE_MARKERS = (
    (ABI_SLICE_REL, 'Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md'),
    (ABI_SLICE_REL, 'scripts/zigux/validate-phase3-low-level-wrapper-survey.py'),
    (DOCS_ROOT_REL, 'Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md'),
    (DOCS_ROOT_REL, 'scripts/zigux/validate-phase3-low-level-wrapper-survey.py'),
    (SCRIPTS_README_REL, 'validate-phase3-low-level-wrapper-survey.py'),
    (TESTS_README_REL, 'validate-phase3-low-level-wrapper-survey.py'),
    (MAKEFILE_REL, 'scripts/zigux/validate-phase3-low-level-wrapper-survey.py'),
    (MAKEFILE_REL, 'phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig'),
)


def _read(root: Path, rel: Path, issues: list[str]) -> str:
    path = root / rel
    if not path.is_file():
        issues.append(f"missing_file:{rel.as_posix()}")
        return ""
    return path.read_text(encoding="utf-8")


def _require(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    survey = _read(root, SURVEY_REL, issues)
    build = _read(root, BUILD_REL, issues)
    test = _read(root, TEST_REL, issues)
    atomic = _read(root, ATOMIC_REL, issues)
    barrier = _read(root, BARRIER_REL, issues)
    _read(root, MMIO_REL, issues)
    allocator_policy = _read(root, ALLOCATOR_POLICY_REL, issues)
    panic_policy = _read(root, PANIC_POLICY_REL, issues)
    narrow = _read(root, NARROW_REL, issues)

    if survey:
        _require(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        _require(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)
    if build:
        _require(build, REQUIRED_BUILD_SNIPPETS, "missing_build_snippet", issues)
    if test:
        _require(test, REQUIRED_TEST_SNIPPETS, "missing_test_snippet", issues)
    if atomic:
        _require(atomic, REQUIRED_ATOMIC_SNIPPETS, "missing_atomic_snippet", issues)
    if barrier:
        _require(barrier, REQUIRED_BARRIER_SNIPPETS, "missing_barrier_snippet", issues)
    if allocator_policy:
        _require(
            allocator_policy,
            REQUIRED_ALLOCATOR_POLICY_SNIPPETS,
            "missing_allocator_policy_snippet",
            issues,
        )
    if panic_policy:
        _require(
            panic_policy,
            REQUIRED_PANIC_POLICY_SNIPPETS,
            "missing_panic_policy_snippet",
            issues,
        )
    if narrow:
        _require(narrow, REQUIRED_NARROW_SNIPPETS, "missing_narrow_snippet", issues)

    for rel, marker in REFERENCE_MARKERS:
        text = _read(root, rel, issues)
        if text and marker not in text:
            issues.append(f"missing_reference:{rel.as_posix()}:{marker}")

    return issues


def _write(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_survey_") as tmp_dir:
        root = Path(tmp_dir)

        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS + REQUIRED_SURVEY_SNIPPETS) + "\n")
        _write(root, BUILD_REL, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
        _write(root, TEST_REL, "\n".join(REQUIRED_TEST_SNIPPETS) + "\n")
        _write(root, ATOMIC_REL, "\n".join(REQUIRED_ATOMIC_SNIPPETS) + "\n")
        _write(root, BARRIER_REL, "\n".join(REQUIRED_BARRIER_SNIPPETS) + "\n")
        _write(root, MMIO_REL, "mmio\n")
        _write(root, ALLOCATOR_POLICY_REL, "\n".join(REQUIRED_ALLOCATOR_POLICY_SNIPPETS) + "\n")
        _write(root, PANIC_POLICY_REL, "\n".join(REQUIRED_PANIC_POLICY_SNIPPETS) + "\n")
        _write(root, NARROW_REL, "\n".join(REQUIRED_NARROW_SNIPPETS) + "\n")
        grouped_markers: dict[Path, list[str]] = {}
        for rel, marker in REFERENCE_MARKERS:
            grouped_markers.setdefault(rel, []).append(marker)
        for rel, markers in grouped_markers.items():
            _write(root, rel, "\n".join(markers) + "\n")

        issues = validate(root)
        if issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            for issue in issues:
                print(issue)
            return 1

        (root / SURVEY_REL).write_text("broken\n", encoding="utf-8")
        issues = validate(root)
        if not any(issue.startswith("missing_survey_marker:") for issue in issues):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing survey marker failure")
            return 1

        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS + REQUIRED_SURVEY_SNIPPETS) + "\n")
        _write(root, TEST_REL, "missing helper checks\n")
        issues = validate(root)
        if not any(
            issue == 'missing_test_snippet:test "phase3 low-level wrappers keep allocator and panic policy helpers reviewable"'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing allocator/panic helper replay failure")
            return 1

        _write(root, TEST_REL, "\n".join(REQUIRED_TEST_SNIPPETS) + "\n")
        _write(
            root,
            TEST_REL,
            (root / TEST_REL).read_text(encoding="utf-8").replace(
                'test "phase3 low-level wrappers keep raw pointer bridge policy gates reviewable"',
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == 'missing_test_snippet:test "phase3 low-level wrappers keep raw pointer bridge policy gates reviewable"'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing raw-pointer bridge replay failure")
            return 1

        _write(root, TEST_REL, "\n".join(REQUIRED_TEST_SNIPPETS) + "\n")
        _write(
            root,
            NARROW_REL,
            (root / NARROW_REL).read_text(encoding="utf-8").replace(
                "pub fn pointerAtInteropPolicyBytes(",
                "pub fn removedPointerAtInteropPolicyBytes(",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == "missing_narrow_snippet:pub fn pointerAtInteropPolicyBytes("
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing raw-pointer bridge helper failure")
            return 1

        _write(root, NARROW_REL, "\n".join(REQUIRED_NARROW_SNIPPETS) + "\n")
        _write(
            root,
            SURVEY_REL,
            (root / SURVEY_REL).read_text(encoding="utf-8").replace(
                "PHASE3_MMIO_SCOPE=range-read-write-8-16-32-64-plus-interop-policy-and-policy-byte-entrypoints",
                "PHASE3_MMIO_SCOPE=range-read-write-8-16-32-64-plus-interop-policy-entrypoints",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue
            == "missing_survey_marker:PHASE3_MMIO_SCOPE=range-read-write-8-16-32-64-plus-interop-policy-and-policy-byte-entrypoints"
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing mmio scope marker failure")
            return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Phase 3 low-level wrapper boundary survey packet.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.repo_root)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
TEST_REL = Path("zigux/tests/phase3_low_level_wrappers.zig")
ATOMIC_REL = Path("zigux/helpers/atomic.zig")
BARRIER_REL = Path("zigux/helpers/barrier.zig")
MMIO_REL = Path("zigux/helpers/mmio.zig")
NARROW_REL = Path("zigux/unsafe/narrow.zig")
ABI_SLICE_REL = Path("Documentation/zigux/phase3-abi-slice.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_LOW_LEVEL_PACKET=approved atomic, barrier, MMIO, and narrow-unsafe wrappers remain the bounded low-level helper packet for the Phase 3 ABI substrate",
    "PHASE3_CURRENT_LOW_LEVEL_GAP=no same-lane helper gap is currently visible on direct current-master readback",
    "PHASE3_CURRENT_LOW_LEVEL_GAP_DETAIL=zigux/tests/phase3_low_level_wrappers.zig now already replays generic and byte-decoded volatile-MMIO policy gates",
    "PHASE3_NEXT_SAFE_STEP=keep future low-level wrapper follow-through bounded to one helper-local or note-local alignment step at a time",
    "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
)

REQUIRED_SURVEY_SNIPPETS = (
    "64-bit MMIO coverage in the focused test route",
    "interop-policy and policy-byte MMIO entrypoints in the focused test route",
    "raw-pointer bridge scope gates in `zigux/unsafe/narrow.zig` and the focused test route",
    "non-`seq_cst` ordering coverage and signed atomic edges in the focused test route",
    "barrier-locality and handoff replays",
)

REQUIRED_TEST_SNIPPETS = (
    'test "phase3 low-level wrappers keep mmio interop policy gates reviewable"',
    'test "phase3 low-level wrappers keep raw pointer bridge policy gates reviewable"',
    'test "phase3 low-level wrappers keep non-seq-cst orderings and signed atomic edges reviewable"',
    'test "phase3 low-level wrappers keep barrier locality reviewable"',
    'test "phase3 low-level wrappers keep barrier handoff reviewable"',
    'mmio.write64(base, @sizeOf(u64), 0x0123_4567_89ab_cdef);',
    'mmio.write64InteropPolicyByte(base, 8, 0xfedc_ba98_7654_3210, @intFromEnum(abi.UnsafeScope.volatile_mmio));',
    'atomic.fetchNand(u32, &value, 10, .seq_cst)',
    'atomic.fetchMin(i32, &ordered_fetch_value, -7, .acquire)',
    'atomic.compareExchangeWeak(u32, &weak_release_value, 13, 19, .release, .monotonic)',
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

REQUIRED_NARROW_SNIPPETS = (
    'pub const UnsafeScopeTag = enum(u8) {',
    'volatile_mmio = 1,',
    'raw_pointer_bridge = 2,',
    'pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {',
    'pub fn pointerAtInteropPolicy(',
    'pub fn writeValueAtInteropPolicyBytes(',
)

REFERENCE_MARKERS = (
    (ABI_SLICE_REL, 'Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md'),
    (ABI_SLICE_REL, 'scripts/zigux/validate-phase3-low-level-wrapper-survey.py'),
    (DOCS_ROOT_REL, 'Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md'),
    (DOCS_ROOT_REL, 'scripts/zigux/validate-phase3-low-level-wrapper-survey.py'),
    (SCRIPTS_README_REL, 'validate-phase3-low-level-wrapper-survey.py'),
    (TESTS_README_REL, 'validate-phase3-low-level-wrapper-survey.py'),
    (MAKEFILE_REL, 'scripts/zigux/validate-phase3-low-level-wrapper-survey.py'),
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
    test = _read(root, TEST_REL, issues)
    atomic = _read(root, ATOMIC_REL, issues)
    barrier = _read(root, BARRIER_REL, issues)
    _read(root, MMIO_REL, issues)
    narrow = _read(root, NARROW_REL, issues)

    if survey:
        _require(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        _require(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)
    if test:
        _require(test, REQUIRED_TEST_SNIPPETS, "missing_test_snippet", issues)
    if atomic:
        _require(atomic, REQUIRED_ATOMIC_SNIPPETS, "missing_atomic_snippet", issues)
    if barrier:
        _require(barrier, REQUIRED_BARRIER_SNIPPETS, "missing_barrier_snippet", issues)
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
        _write(root, TEST_REL, "\n".join(REQUIRED_TEST_SNIPPETS) + "\n")
        _write(root, ATOMIC_REL, "\n".join(REQUIRED_ATOMIC_SNIPPETS) + "\n")
        _write(root, BARRIER_REL, "\n".join(REQUIRED_BARRIER_SNIPPETS) + "\n")
        _write(root, MMIO_REL, "mmio\n")
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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
SURVEY_REL = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
BUILD_REL = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
TEST_REL = Path("zigux/tests/phase3_low_level_wrappers.zig")
ATOMIC_REL = Path("zigux/helpers/atomic.zig")
BARRIER_REL = Path("zigux/helpers/barrier.zig")
MMIO_REL = Path("zigux/helpers/mmio.zig")
ABI_SLICE_REL = Path("Documentation/zigux/phase3-abi-slice.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
MAKEFILE_REL = Path("zigux/Makefile")

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig",
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetchadd-fetchsub-fetchand-fetchor-fetchxor-fetchnand-fetchmin-fetchmax-bittest-bitset-bitreset-bittoggle-compareexchange-compareexchangeweak",
    "PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig",
    "PHASE3_BARRIER_SCOPE=acquire-release-full-acquirerelease",
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_MMIO_SCOPE=direct-range-read-write-8-16-32-64-width-alignment-and-odd-offset-replay",
    "PHASE3_LOW_LEVEL_BUILD_PATH=zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig",
    "PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_BOUNDARY_GAP=no-new-kernel-style-low-level-family-landed-beyond-current-atomic-barrier-and-direct-mmio-packet",
    "PHASE3_NEXT_BOUNDED_STEP=keep-this-lane-limited-to-packet-local-survey-validator-or-build-surface-repairs-for-atomic-barrier-and-direct-mmio-ownership-only",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`zigux/helpers/atomic.zig` keeps the approved atomic surface explicit through `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchNand`, `fetchMin`, `fetchMax`, `bitTest`, `bitSet`, `bitReset`, `bitToggle`, `compareExchange`, and `compareExchangeWeak`, including helper-local non-`seq_cst` ordering, signed min/max, and bit-wrapper replays.",
    "`zigux/helpers/mmio.zig` keeps the approved direct MMIO packet explicit through `range()`, direct 8-, 16-, 32-, and 64-bit reads and writes, width coverage, alignment handling, and odd-offset replay behavior in the focused test route.",
    "`zigux/tests/phase3_low_level_wrappers.zig` remains the current focused replay for the shared direct wrapper packet, including the direct MMIO width, alignment, odd-offset, and byte-scoped interop-policy checks plus the non-`seq_cst` atomic, barrier locality or handoff, and shared allocator-or-panic consumer proofs, while the atomic bit wrappers stay helper-local in `zigux/helpers/atomic.zig` to keep this focused route bounded.",
    "`zigux/helpers/allocator_policy.zig`, `zigux/helpers/panic_policy.zig`, and `zigux/unsafe/narrow.zig` stay owned by `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` and its coupled policy validators, even when the current low-level replay still imports them for the shared allocator-and-panic consumer proof.",
    "the policy-aware MMIO relays in `zigux/helpers/mmio.zig`, including `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*`, stay owned by the policy-and-unsafe packet even though the focused low-level replay currently exercises them.",
    "`zigux/tests/phase3_low_level_wrappers.zig` still exercises byte-scoped MMIO policy relays such as `allowsInteropPolicyByte`, `rangeInteropPolicyByte`, `read8InteropPolicyByte`, `write8InteropPolicyByte`, `read8InteropPolicyBytes`, and `write8InteropPolicyBytes`, but those focused checks continue to serve the adjacent policy-and-unsafe owner packet rather than widening direct MMIO ownership here.",
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
    'allocator_policy_helpers_module.addImport("abi_bindings", abi_bindings_module);',
    'panic_policy_helpers_module.addImport("abi_bindings", abi_bindings_module);',
    'root_module.addImport("allocator_policy_helpers", allocator_policy_helpers_module);',
    'root_module.addImport("panic_policy_helpers", panic_policy_helpers_module);',
    '"phase3-low-level-wrappers-test"',
)

REQUIRED_TEST_SNIPPETS = (
    'test "phase3 low-level wrappers cover the shipped helper surface directly" {',
    'test "phase3 low-level wrappers keep mmio interop policy gates reviewable" {',
    'test "phase3 low-level wrappers keep raw pointer bridge policy gates reviewable" {',
    'test "phase3 low-level wrappers keep allocator and panic policy helpers reviewable" {',
    'test "phase3 low-level wrappers keep non-seq-cst orderings and signed atomic edges reviewable" {',
    'test "phase3 low-level wrappers keep barrier locality reviewable" {',
    'test "phase3 low-level wrappers keep barrier handoff reviewable" {',
    'atomic.store(u32, &handoff_value, 41, .release);',
    'atomic.load(u32, &handoff_value, .acquire)',
    'barrier.acquireRelease();',
    'mmio.write64(base, @sizeOf(u64), 0x0123_4567_89ab_cdef);',
    'mmio.write16(base, 1, 0x1234);',
    'mmio.write32(base, 3, 0x89abcdef);',
    'mmio.write64(base, 5, 0xfedc_ba98_7654_3210);',
    'mmio.allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio))',
    'const byte_scoped_desc = try mmio.rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.volatile_mmio));',
    'const bytes_scoped_desc = try mmio.rangeInteropPolicyBytes(',
    'mmio.write8InteropPolicyByte(base, 3, 0x7e, @intFromEnum(abi.UnsafeScope.volatile_mmio));',
    'mmio.read8InteropPolicyByte(base, 3, @intFromEnum(abi.UnsafeScope.volatile_mmio))',
    'mmio.write8InteropPolicyBytes(base, 1, 0x44, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0);',
    'mmio.read8InteropPolicyBytes(base, 1, @intFromEnum(abi.UnsafeScope.volatile_mmio), 0)',
    'mmio.write64InteropPolicyByte(base, 8, 0xfedc_ba98_7654_3210, @intFromEnum(abi.UnsafeScope.volatile_mmio));',
    'narrow.pointerAtInteropPolicy(u32, base, @sizeOf(u32), raw_policy)',
    'allocator_policy.modeFromInteropPolicy(caller_abort_policy)',
    'panic_policy.actionForInteropPolicy(caller_abort_policy)',
    'atomic.fetchNand(u32, &value, 10, .seq_cst)',
    'atomic.fetchMin(i32, &ordered_fetch_value, -7, .acquire)',
    'atomic.compareExchangeWeak(u32, &weak_release_value, 13, 19, .release, .monotonic)',
)

REQUIRED_ATOMIC_SNIPPETS = (
    'pub fn fetchNand(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {',
    'pub fn fetchMin(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {',
    'pub fn fetchMax(comptime T: type, ptr: *T, value: T, comptime order: std.builtin.AtomicOrder) T {',
    'pub fn bitTest(comptime T: type, ptr: *const T, bit_index: u16, comptime order: std.builtin.AtomicOrder) u1 {',
    'pub fn bitSet(comptime T: type, ptr: *T, bit_index: u16, comptime order: std.builtin.AtomicOrder) u1 {',
    'pub fn bitReset(comptime T: type, ptr: *T, bit_index: u16, comptime order: std.builtin.AtomicOrder) u1 {',
    'pub fn bitToggle(comptime T: type, ptr: *T, bit_index: u16, comptime order: std.builtin.AtomicOrder) u1 {',
    'pub fn compareExchangeWeak(',
    'test "phase3 atomic wrappers keep non-seq-cst orderings reviewable"',
    'test "phase3 atomic wrappers keep bit wrappers reviewable"',
    'bitTest(u8, &flags, 2, .acquire)',
    'bitTest(u64, &high_bit_flags, high_bit_index, .acquire)',
)

REQUIRED_BARRIER_SNIPPETS = (
    'pub fn acquireRelease() void {',
    'test "phase3 barrier wrappers keep barrier locality reviewable"',
    'test "phase3 barrier wrappers keep barrier handoff reviewable"',
)

REQUIRED_MMIO_SNIPPETS = (
    'pub fn range(base_addr: usize, length: u32, stride: u32) Range {',
    'pub fn allowsInteropPolicyByte(unsafe_scope: u8) bool {',
    'pub fn rangeInteropPolicyBytes(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8, reserved: u8) MmioError!Range {',
    'pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) MmioError!Range {',
    'pub fn read8(base_addr: usize, offset: usize) u8 {',
    'pub fn read16(base_addr: usize, offset: usize) u16 {',
    'pub fn read32(base_addr: usize, offset: usize) u32 {',
    'pub fn read64(base_addr: usize, offset: usize) u64 {',
    'pub fn write8(base_addr: usize, offset: usize, value: u8) void {',
    'pub fn write16(base_addr: usize, offset: usize, value: u16) void {',
    'pub fn write32(base_addr: usize, offset: usize, value: u32) void {',
    'pub fn write64(base_addr: usize, offset: usize, value: u64) void {',
    'pub fn read8InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u8 {',
    'pub fn write8InteropPolicyBytes(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8, reserved: u8) MmioError!void {',
    'pub fn read8InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u8 {',
    'pub fn write8InteropPolicyByte(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8) MmioError!void {',
    'test "phase3 mmio wrappers keep direct reads and writes reviewable" {',
    'test "phase3 mmio wrappers keep odd-offset volatile accesses reviewable" {',
)

REFERENCE_MARKERS = (
    (ABI_SLICE_REL, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    (ABI_SLICE_REL, "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    (DOCS_ROOT_REL, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    (DOCS_ROOT_REL, "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    (SCRIPTS_README_REL, "validate-phase3-low-level-wrapper-survey.py"),
    (TESTS_README_REL, "validate-phase3-low-level-wrapper-survey.py"),
    (MAKEFILE_REL, "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    (MAKEFILE_REL, "phase3-low-level-wrappers-test:"),
    (MAKEFILE_REL, "phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"),
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
    mmio = _read(root, MMIO_REL, issues)

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
    if mmio:
        _require(mmio, REQUIRED_MMIO_SNIPPETS, "missing_mmio_snippet", issues)

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
        _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
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
            issue == 'missing_test_snippet:test "phase3 low-level wrappers keep barrier handoff reviewable" {'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing barrier handoff replay failure")
            return 1

        _write(
            root,
            SURVEY_REL,
            (root / SURVEY_REL).read_text(encoding="utf-8").replace(
                "`zigux/helpers/allocator_policy.zig`, `zigux/helpers/panic_policy.zig`, and `zigux/unsafe/narrow.zig` stay owned by `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` and its coupled policy validators, even when the current low-level replay still imports them for the shared allocator-and-panic consumer proof.",
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue.startswith(
                "missing_survey_snippet:`zigux/helpers/allocator_policy.zig`, `zigux/helpers/panic_policy.zig`, and `zigux/unsafe/narrow.zig` stay owned"
            )
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing allocator and panic owner-split survey failure")
            return 1

        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS + REQUIRED_SURVEY_SNIPPETS) + "\n")
        _write(root, TEST_REL, "\n".join(REQUIRED_TEST_SNIPPETS) + "\n")
        _write(
            root,
            MMIO_REL,
            (root / MMIO_REL).read_text(encoding="utf-8").replace(
                'test "phase3 mmio wrappers keep direct reads and writes reviewable" {',
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == 'missing_mmio_snippet:test "phase3 mmio wrappers keep direct reads and writes reviewable" {'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing direct mmio replay failure")
            return 1

        _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
        _write(
            root,
            BUILD_REL,
            (root / BUILD_REL).read_text(encoding="utf-8").replace(
                'root_module.addImport("mmio_helpers", mmio_helpers_module);',
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == 'missing_build_snippet:root_module.addImport("mmio_helpers", mmio_helpers_module);'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing mmio build wiring failure")
            return 1

        _write(root, BUILD_REL, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
        _write(
            root,
            MMIO_REL,
            (root / MMIO_REL).read_text(encoding="utf-8").replace(
                'pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) MmioError!Range {',
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == 'missing_mmio_snippet:pub fn rangeInteropPolicyByte(base_addr: usize, length: u32, stride: u32, unsafe_scope: u8) MmioError!Range {'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing byte-scoped mmio range helper failure")
            return 1

        _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
        _write(
            root,
            MMIO_REL,
            (root / MMIO_REL).read_text(encoding="utf-8").replace(
                'test "phase3 mmio wrappers keep odd-offset volatile accesses reviewable" {',
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == 'missing_mmio_snippet:test "phase3 mmio wrappers keep odd-offset volatile accesses reviewable" {'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing odd-offset mmio replay failure")
            return 1

        _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
        _write(
            root,
            TEST_REL,
            (root / TEST_REL).read_text(encoding="utf-8").replace(
                'allocator_policy.modeFromInteropPolicy(caller_abort_policy)',
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == 'missing_test_snippet:allocator_policy.modeFromInteropPolicy(caller_abort_policy)'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing allocator-policy replay failure")
            return 1

        _write(root, TEST_REL, "\n".join(REQUIRED_TEST_SNIPPETS) + "\n")
        _write(
            root,
            TEST_REL,
            (root / TEST_REL).read_text(encoding="utf-8").replace(
                'const byte_scoped_desc = try mmio.rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.volatile_mmio));',
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == 'missing_test_snippet:const byte_scoped_desc = try mmio.rangeInteropPolicyByte(base, 12, 2, @intFromEnum(abi.UnsafeScope.volatile_mmio));'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing byte-scoped mmio replay failure")
            return 1

        _write(root, TEST_REL, "\n".join(REQUIRED_TEST_SNIPPETS) + "\n")
        _write(
            root,
            TEST_REL,
            (root / TEST_REL).read_text(encoding="utf-8").replace(
                'test "phase3 low-level wrappers keep raw pointer bridge policy gates reviewable" {',
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == 'missing_test_snippet:test "phase3 low-level wrappers keep raw pointer bridge policy gates reviewable" {'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing raw-pointer bridge replay failure")
            return 1

        _write(root, TEST_REL, "\n".join(REQUIRED_TEST_SNIPPETS) + "\n")
        _write(
            root,
            ATOMIC_REL,
            (root / ATOMIC_REL).read_text(encoding="utf-8").replace(
                'pub fn bitTest(comptime T: type, ptr: *const T, bit_index: u16, comptime order: std.builtin.AtomicOrder) u1 {',
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == 'missing_atomic_snippet:pub fn bitTest(comptime T: type, ptr: *const T, bit_index: u16, comptime order: std.builtin.AtomicOrder) u1 {'
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing atomic bit-test helper failure")
            return 1

        _write(root, ATOMIC_REL, "\n".join(REQUIRED_ATOMIC_SNIPPETS) + "\n")
        _write(
            root,
            MAKEFILE_REL,
            (root / MAKEFILE_REL).read_text(encoding="utf-8").replace(
                "phase3-low-level-wrappers-test:\n",
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue == "missing_reference:zigux/Makefile:phase3-low-level-wrappers-test:"
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing low-level-wrapper make target failure")
            return 1

        _write(root, MAKEFILE_REL, "\n".join(grouped_markers[MAKEFILE_REL]) + "\n")
        _write(
            root,
            MAKEFILE_REL,
            (root / MAKEFILE_REL).read_text(encoding="utf-8").replace(
                "phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue
            == "missing_reference:zigux/Makefile:phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing low-level-wrapper make route reference failure")
            return 1

        _write(root, MAKEFILE_REL, "\n".join(grouped_markers[MAKEFILE_REL]) + "\n")
        _write(
            root,
            SURVEY_REL,
            (root / SURVEY_REL).read_text(encoding="utf-8").replace(
                "the policy-aware MMIO relays in `zigux/helpers/mmio.zig`, including `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*`, stay owned by the policy-and-unsafe packet even though the focused low-level replay currently exercises them.",
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue.startswith("missing_survey_snippet:the policy-aware MMIO relays in `zigux/helpers/mmio.zig`")
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing owner-split survey failure")
            return 1

        _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS + REQUIRED_SURVEY_SNIPPETS) + "\n")
        _write(
            root,
            SURVEY_REL,
            (root / SURVEY_REL).read_text(encoding="utf-8").replace(
                "`zigux/tests/phase3_low_level_wrappers.zig` still exercises byte-scoped MMIO policy relays such as `allowsInteropPolicyByte`, `rangeInteropPolicyByte`, `read8InteropPolicyByte`, `write8InteropPolicyByte`, `read8InteropPolicyBytes`, and `write8InteropPolicyBytes`, but those focused checks continue to serve the adjacent policy-and-unsafe owner packet rather than widening direct MMIO ownership here.",
                "",
                1,
            ),
        )
        issues = validate(root)
        if not any(
            issue.startswith("missing_survey_snippet:`zigux/tests/phase3_low_level_wrappers.zig` still exercises byte-scoped MMIO policy relays")
            for issue in issues
        ):
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("expected missing byte-scoped owner-split survey failure")
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

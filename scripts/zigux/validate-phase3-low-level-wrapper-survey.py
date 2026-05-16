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
ABI_MANIFEST_REL = Path("zigux/tests/fixtures/phase3_abi_manifest.json")

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_ATOMIC_PATH=zigux/helpers/atomic.zig",
    "PHASE3_ATOMIC_SCOPE=load-store-exchange-fetchadd-fetchsub-fetchand-fetchor-fetchxor-fetchnand-fetchmin-fetchmax-bittest-bitset-bitreset-bittoggle-compareexchange-compareexchangeweak",
    "PHASE3_BARRIER_PATH=zigux/helpers/barrier.zig",
    "PHASE3_BARRIER_SCOPE=compiler-acquire-release-full-acquirerelease",
    "PHASE3_MMIO_PATH=zigux/helpers/mmio.zig",
    "PHASE3_MMIO_SCOPE=direct-range-indexed-read-write-8-16-32-64-width-alignment-and-odd-offset-replay",
    "PHASE3_LOW_LEVEL_BUILD_PATH=zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_LOW_LEVEL_TEST_PATH=zigux/tests/phase3_low_level_wrappers.zig",
    "PHASE3_LOW_LEVEL_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "PHASE3_BOUNDARY_GAP=no-new-kernel-style-low-level-family-landed-beyond-current-atomic-barrier-and-direct-mmio-packet",
    "PHASE3_SHARED_CONSUMER_RULE=consumer-only-policy-and-unsafe-drift-inside-the-focused-low-level-wrapper-replay-stays-with-the-adjacent-owner-packet",
    "PHASE3_NEXT_BOUNDED_STEP=keep-this-lane-limited-to-packet-local-survey-validator-or-build-surface-repairs-for-atomic-barrier-and-direct-mmio-ownership-only",
)

REQUIRED_SURVEY_SNIPPETS = (
    "`zigux/helpers/atomic.zig` keeps the approved atomic surface explicit through `load`, `store`, `exchange`, `fetchAdd`, `fetchSub`, `fetchAnd`, `fetchOr`, `fetchXor`, `fetchNand`, `fetchMin`, `fetchMax`, `bitTest`, `bitSet`, `bitReset`, `bitToggle`, `compareExchange`, and `compareExchangeWeak`, including helper-local non-`seq_cst` ordering, signed min/max, and bit-wrapper replays.",
    "`zigux/helpers/barrier.zig` keeps the approved barrier surface explicit through `compiler`, `acquire`, `release`, `full`, and `acquireRelease`, with `compiler()` staying helper-local while current `master` also ships helper-local side-effect-free storage proof plus the barrier-locality and handoff replays in the focused route.",
    "`zigux/helpers/mmio.zig` keeps the approved direct MMIO packet explicit through `range()`, direct 8-, 16-, 32-, and 64-bit reads and writes, indexed reads and writes, width coverage, alignment handling, and odd-offset replay behavior in the focused test route.",
    "`zigux/tests/phase3_low_level_wrappers.zig` remains the current focused replay for the shared direct wrapper packet, including the direct MMIO width, alignment, odd-offset, and byte-scoped interop-policy checks plus the non-`seq_cst` atomic, barrier locality or handoff, and shared allocator-or-panic consumer proofs, while the atomic bit wrappers stay helper-local in `zigux/helpers/atomic.zig` and `compiler()` stays helper-local in `zigux/helpers/barrier.zig` to keep this focused route bounded.",
    "Current `master` no longer treats `zigux/helpers/mmio.zig` as declarations-only support for the focused replay. The helper file itself now ships direct MMIO range-boundary, odd-offset volatile-access, and volatile-MMIO policy-gate replays, while `zigux/tests/phase3_low_level_wrappers.zig` remains the shared cross-helper route that keeps those already-landed MMIO calls visible beside the atomic, barrier, raw-pointer, allocator, and panic consumers.",
    "`zigux/helpers/allocator_policy.zig`, `zigux/helpers/panic_policy.zig`, and `zigux/unsafe/narrow.zig` stay owned by `Documentation/zigux/phase3-policy-unsafe-boundary-survey.md` and its coupled policy validators, even when the current low-level replay still imports them for the shared allocator-and-panic consumer proof.",
    "the policy-aware MMIO relays in `zigux/helpers/mmio.zig`, including `allowsInteropPolicy*`, `requireInteropPolicy*`, `rangeInteropPolicy*`, `read*InteropPolicy*`, and `write*InteropPolicy*`, stay owned by the policy-and-unsafe packet even though the focused low-level replay currently exercises them.",
    "that helper-local MMIO proof surface does not move volatile-MMIO policy relay ownership into this lane; it only means the already-landed policy relays now have both helper-local and focused-route evidence on current `master`.",
    "`zigux/tests/phase3_low_level_wrappers.zig` still exercises byte-scoped MMIO policy relays such as `allowsInteropPolicyByte`, `rangeInteropPolicyByte`, `read8InteropPolicyByte`, `write8InteropPolicyByte`, `read8InteropPolicyBytes`, and `write8InteropPolicyBytes`, but those focused checks continue to serve the adjacent policy-and-unsafe owner packet rather than widening direct MMIO ownership here.",
    "`zigux/tests/phase3_low_level_wrappers.zig` now also replays raw-pointer bridge admission helpers such as `permitsRawPointerBridgeInteropPolicy`, `pointerAtInteropPolicy`, `sliceAtInteropPolicy`, `constSliceAtInteropPolicy`, and `writeValueAtInteropPolicy`, but those focused checks still belong to the adjacent policy-and-unsafe packet instead of widening this lane beyond the direct atomic, barrier, and MMIO wrapper family.",
    "helper-local `compiler()` barrier coverage plus side-effect-free storage proof in `zigux/helpers/barrier.zig`",
    "helper-local MMIO range-boundary, odd-offset volatile-access, and volatile-MMIO policy-gate coverage in `zigux/helpers/mmio.zig`",
    "helper-local MMIO stride-boundary and typed-index coverage in `zigux/helpers/mmio.zig` through `containsOffset`, `containsAccess`, `offsetForIndex`, and `typedOffsetForIndex`",
    "The same helper-local MMIO packet now also keeps stride-indexed access replays through `readIndex()` and `writeIndex()` plus width-specific indexed relays through `read8Index()`, `read16Index()`, `read32Index()`, `read64Index()`, `write8Index()`, `write16Index()`, `write32Index()`, and `write64Index()` explicit in `zigux/helpers/mmio.zig` instead of leaving that direct-access slice visible only through the focused route.",
)

REQUIRED_BUILD_SNIPPETS = (
    '.root_source_file = b.path("../bindings/abi.zig")',
    '.root_source_file = b.path("../unsafe/narrow.zig")',
    'narrow_unsafe_module.addImport("abi_bindings", abi_bindings_module);',
    '.root_source_file = b.path("../helpers/atomic.zig")',
    '.root_source_file = b.path("../helpers/barrier.zig")',
    '.root_source_file = b.path("../helpers/mmio.zig")',
    'mmio_helpers_module.addImport("abi_bindings", abi_bindings_module);',
    'mmio_helpers_module.addImport("narrow_unsafe", narrow_unsafe_module);',
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
    'bitSet(u8, &flags, 1, .monotonic)',
    'bitReset(u8, &flags, 4, .acquire)',
    'bitToggle(u64, &high_bit_flags, high_bit_index, .seq_cst)',
    'bitTest(u64, &high_bit_flags, high_bit_index, .acquire)',
)

REQUIRED_BARRIER_SNIPPETS = (
    'pub fn compiler() void {',
    'pub fn acquireRelease() void {',
    'test "phase3 barrier wrappers compile"',
    'test "phase3 barrier wrappers keep compiler fences reviewable"',
    'test "phase3 barrier wrappers keep barrier locality reviewable"',
    'test "phase3 barrier wrappers keep barrier handoff reviewable"',
    'test "phase3 barrier wrappers stay side-effect free on unrelated storage"',
)

REQUIRED_MMIO_SNIPPETS = (
    'pub fn range(base_addr: usize, length: u32, stride: u32) Range {',
    'pub fn containsOffset(desc: Range, offset: usize) bool {',
    'pub fn containsAccess(desc: Range, offset: usize, width: usize) bool {',
    'pub fn offsetForIndex(desc: Range, index: usize) ?usize {',
    'pub fn typedOffsetForIndex(desc: Range, comptime T: type, index: usize) ?usize {',
    'pub fn readIndex(comptime T: type, desc: Range, index: usize) ?T {',
    'pub fn writeIndex(comptime T: type, desc: Range, index: usize, value: T) bool {',
    'pub fn read8Index(desc: Range, index: usize) ?u8 {',
    'pub fn read16Index(desc: Range, index: usize) ?u16 {',
    'pub fn read32Index(desc: Range, index: usize) ?u32 {',
    'pub fn read64Index(desc: Range, index: usize) ?u64 {',
    'pub fn write8Index(desc: Range, index: usize, value: u8) bool {',
    'pub fn write16Index(desc: Range, index: usize, value: u16) bool {',
    'pub fn write32Index(desc: Range, index: usize, value: u32) bool {',
    'pub fn write64Index(desc: Range, index: usize, value: u64) bool {',
    'pub fn allowsInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {',
    'pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {',
    'pub fn allowsInteropPolicyByte(unsafe_scope: u8) bool {',
    'pub fn requireInteropPolicyBytes(unsafe_scope: u8, reserved: u8) MmioError!void {',
    'pub fn requireInteropPolicy(policy: abi.InteropPolicy) MmioError!void {',
    'pub fn requireInteropPolicyByte(unsafe_scope: u8) MmioError!void {',
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
    'pub fn readInteropPolicy(comptime T: type, base_addr: usize, offset: usize, policy: abi.InteropPolicy) MmioError!T {',
    'pub fn writeInteropPolicy(',
    'pub fn readInteropPolicyBytes(',
    'pub fn writeInteropPolicyBytes(',
    'pub fn read8InteropPolicyBytes(base_addr: usize, offset: usize, unsafe_scope: u8, reserved: u8) MmioError!u8 {',
    'pub fn write8InteropPolicyBytes(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8, reserved: u8) MmioError!void {',
    'pub fn readInteropPolicyByte(comptime T: type, base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!T {',
    'pub fn writeInteropPolicyByte(',
    'pub fn read8InteropPolicyByte(base_addr: usize, offset: usize, unsafe_scope: u8) MmioError!u8 {',
    'pub fn write8InteropPolicyByte(base_addr: usize, offset: usize, value: u8, unsafe_scope: u8) MmioError!void {',
    'test "phase3 mmio wrappers keep direct reads and writes reviewable" {',
    'test "phase3 mmio ranges keep byte and stride boundaries explicit" {',
    'test "phase3 mmio wrappers keep stride-indexed accesses reviewable" {',
    'test "phase3 mmio wrappers keep odd-offset volatile accesses reviewable" {',
    'test "phase3 mmio wrappers keep volatile-mmio policy gates reviewable" {',
    'try std.testing.expectEqual(@as(?usize, 24), typedOffsetForIndex(desc, u64, 3));',
    'try std.testing.expect(writeIndex(u64, desc, 4, 0x0123_4567_89ab_cdef));',
    'try std.testing.expectEqual(@as(?u64, 0x0123_4567_89ab_cdef), readIndex(u64, desc, 4));',
    'try std.testing.expect(!writeIndex(u64, desc, 5, 0xfedc_ba98_7654_3210));',
    'try requireInteropPolicy(mmio_policy);',
    'try requireInteropPolicyBytes(@intFromEnum(abi.UnsafeScope.volatile_mmio), 0);',
    'try requireInteropPolicyByte(@intFromEnum(abi.UnsafeScope.volatile_mmio));',
    'try writeInteropPolicyByte(u32, base, 4, 0xc001_d00d, @intFromEnum(abi.UnsafeScope.volatile_mmio));',
    'try std.testing.expectError(error.UnsafeScopeDenied, writeInteropPolicy(u8, base, 0, 0x44, raw_policy));',
    'try std.testing.expect(!allowsInteropPolicyByte(@intFromEnum(abi.UnsafeScope.none)));',
)

REFERENCE_MARKERS = (
    (ABI_SLICE_REL, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    (ABI_SLICE_REL, "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    (ABI_MANIFEST_REL, "zigux/tests/phase3_low_level_wrappers.zig"),
    (DOCS_ROOT_REL, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    (DOCS_ROOT_REL, "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    (SCRIPTS_README_REL, "validate-phase3-low-level-wrapper-survey.py"),
    (SCRIPTS_README_REL, "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    (TESTS_README_REL, "validate-phase3-low-level-wrapper-survey.py"),
    (TESTS_README_REL, "zigux/tests/phase3_low_level_wrappers.zig"),
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
            raise AssertionError(f"expected clean fixture, got {issues}")

        bad_cases = [
            (SURVEY_REL, REQUIRED_SURVEY_MARKERS[0], "missing_survey_marker"),
            (SURVEY_REL, REQUIRED_SURVEY_MARKERS[10], "missing_survey_marker"),
            (SURVEY_REL, REQUIRED_SURVEY_SNIPPETS[0], "missing_survey_snippet"),
            (SURVEY_REL, REQUIRED_SURVEY_SNIPPETS[-1], "missing_survey_snippet"),
            (BUILD_REL, REQUIRED_BUILD_SNIPPETS[0], "missing_build_snippet"),
            (TEST_REL, REQUIRED_TEST_SNIPPETS[0], "missing_test_snippet"),
            (ATOMIC_REL, REQUIRED_ATOMIC_SNIPPETS[0], "missing_atomic_snippet"),
            (ATOMIC_REL, REQUIRED_ATOMIC_SNIPPETS[8], "missing_atomic_snippet"),
            (ATOMIC_REL, REQUIRED_ATOMIC_SNIPPETS[9], "missing_atomic_snippet"),
            (ATOMIC_REL, REQUIRED_ATOMIC_SNIPPETS[10], "missing_atomic_snippet"),
            (ATOMIC_REL, REQUIRED_ATOMIC_SNIPPETS[11], "missing_atomic_snippet"),
            (ATOMIC_REL, REQUIRED_ATOMIC_SNIPPETS[12], "missing_atomic_snippet"),
            (ATOMIC_REL, REQUIRED_ATOMIC_SNIPPETS[13], "missing_atomic_snippet"),
            (ATOMIC_REL, REQUIRED_ATOMIC_SNIPPETS[14], "missing_atomic_snippet"),
            (BARRIER_REL, REQUIRED_BARRIER_SNIPPETS[0], "missing_barrier_snippet"),
            (BARRIER_REL, REQUIRED_BARRIER_SNIPPETS[2], "missing_barrier_snippet"),
            (BARRIER_REL, REQUIRED_BARRIER_SNIPPETS[3], "missing_barrier_snippet"),
            (BARRIER_REL, REQUIRED_BARRIER_SNIPPETS[4], "missing_barrier_snippet"),
            (BARRIER_REL, REQUIRED_BARRIER_SNIPPETS[5], "missing_barrier_snippet"),
            (BARRIER_REL, REQUIRED_BARRIER_SNIPPETS[6], "missing_barrier_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[0], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[6], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[7], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[8], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[9], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[10], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[13], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[14], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[21], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[22], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[23], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[24], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[25], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[26], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[27], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[28], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[39], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[40], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[41], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[42], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[43], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[44], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[45], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[46], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[47], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[48], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[49], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[50], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[51], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[52], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[53], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[54], "missing_mmio_snippet"),
            (MMIO_REL, REQUIRED_MMIO_SNIPPETS[55], "missing_mmio_snippet"),
            (ABI_SLICE_REL, REFERENCE_MARKERS[0][1], "missing_reference"),
            (DOCS_ROOT_REL, REFERENCE_MARKERS[3][1], "missing_reference"),
            (SCRIPTS_README_REL, REFERENCE_MARKERS[5][1], "missing_reference"),
            (TESTS_README_REL, REFERENCE_MARKERS[7][1], "missing_reference"),
            (MAKEFILE_REL, REFERENCE_MARKERS[9][1], "missing_reference"),
        ]

        for rel, snippet, prefix in bad_cases:
            grouped_markers = {}
            _write(root, SURVEY_REL, "\n".join(REQUIRED_SURVEY_MARKERS + REQUIRED_SURVEY_SNIPPETS) + "\n")
            _write(root, BUILD_REL, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
            _write(root, TEST_REL, "\n".join(REQUIRED_TEST_SNIPPETS) + "\n")
            _write(root, ATOMIC_REL, "\n".join(REQUIRED_ATOMIC_SNIPPETS) + "\n")
            _write(root, BARRIER_REL, "\n".join(REQUIRED_BARRIER_SNIPPETS) + "\n")
            _write(root, MMIO_REL, "\n".join(REQUIRED_MMIO_SNIPPETS) + "\n")
            for ref_rel, marker in REFERENCE_MARKERS:
                grouped_markers.setdefault(ref_rel, []).append(marker)
            for ref_rel, markers in grouped_markers.items():
                _write(root, ref_rel, "\n".join(markers) + "\n")

            target = root / rel
            text = target.read_text(encoding="utf-8")
            target.write_text(text.replace(snippet + "\n", "", 1), encoding="utf-8")

            issues = validate(root)
            if not issues:
                raise AssertionError(f"expected {prefix} for {rel}:{snippet}")
            expected = f"{prefix}:{snippet}"
            if not any(issue == expected or issue.endswith(f":{snippet}") for issue in issues):
                raise AssertionError(f"expected {expected}, got {issues}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.repo_root)
    if issues:
        for issue in issues:
            print(issue)
        return 1
    print("phase3 low-level wrapper survey validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-close the current Phase 3 low-level wrapper survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
ATOMIC_PATH = Path("zigux/helpers/atomic.zig")
BARRIER_PATH = Path("zigux/helpers/barrier.zig")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
WRAPPER_REPLAY_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
WRAPPER_BUILD_PATH = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
SHARED_TESTS_README_PATH = Path("zigux/tests/README.md")
SHARED_TESTS_BUILD_PATH = Path("zigux/tests/build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_MARKERS = {
    NOTE_PATH: (
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder plus directly readable interop-policy raw-pointer bridge entrypoints, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one shared tests-root reminder, and one returned shared Makefile replay gate",
        "PHASE3_LOW_LEVEL_WRAPPER_GAP=direct current-head readback reaches Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md, zigux/helpers/atomic.zig, zigux/helpers/barrier.zig, zigux/helpers/mmio.zig, zigux/helpers/unsafe_policy.zig, zigux/unsafe/narrow.zig, scripts/zigux/validate-phase3-low-level-wrapper-survey.py, zigux/tests/phase3_low_level_wrappers.zig, zigux/tests/phase3_low_level_wrappers_build.zig, zigux/tests/README.md, zigux/tests/build.zig, and zigux/Makefile; adjacent shared Phase 3 validator, shared ABI checker, shared ABI catalog helper, export/UAPI survey-validator, and catalog-selftest guard surfaces now read separately on current master, while the low-level-wrapper packet stays bounded to its own helper-local evidence",
        "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the directly coupled unsafe-policy companion, the shared narrow-unsafe interop-policy bridge entrypoints, the dedicated build companion, the shared tests-root reminder, the direct zig build phase3-low-level-wrappers-test replay route, and the returned Makefile replay gate while the adjacent catalog-selftest guard stays outside this wrapper packet",
        "`zigux/helpers/atomic.zig`",
        "`zigux/helpers/barrier.zig`",
        "`zigux/helpers/mmio.zig`",
        "`zigux/helpers/unsafe_policy.zig`",
        "`zigux/unsafe/narrow.zig`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`zigux/tests/README.md`",
        "`zigux/tests/build.zig`",
        "`zigux/Makefile`",
        "`zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`make -C zigux phase3-low-level-wrappers-test`",
        "## Adjacent Directly Readable Phase 3 Support",
        "`scripts/zigux/check-phase3-catalog-selftest.py`",
        "The shared tests-root reminder in `zigux/tests/README.md` now keeps `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, `scripts/zigux/validate-phase3-export-uapi-survey.py`, `Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, `zigux/tests/phase3_low_level_wrappers_build.zig`, and `zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig` explicit beside the starter, helper, policy, and layout-replay packet, so the low-level-wrapper survey no longer treats shared tests-root coverage as a separate missing follow-through.",
        "Current `master` also keeps `zigux/Makefile` and `make -C zigux phase3-low-level-wrappers-test` explicit beside the dedicated shared build companion, so the low-level-wrapper packet now has both the direct Zig replay command and the returned shared Makefile replay gate without widening into broader Phase 3 completion claims.",
        "That directly coupled build companion and the live `zigux/helpers/mmio.zig` helper both depend on `zigux/helpers/unsafe_policy.zig`, so the packet reminder needs to keep that helper-local unsafe-policy surface explicit instead of undercounting it as if the MMIO wrapper stood alone.",
        "Current `master` also keeps the whole-record MMIO interop-policy predicates plus `readInteropPolicy()`, `writeInteropPolicy()`, `exchangeInteropPolicy()`, and `writeMaskedInteropPolicy()` directly readable in `zigux/helpers/mmio.zig`, so the low-level-wrapper survey and validator need to exact-require that same helper-local policy surface instead of only the byte-policy shorthand.",
        "The focused replay in `zigux/tests/phase3_low_level_wrappers.zig` now keeps both the byte-policy shorthand checks and one dedicated whole-record `InteropPolicy` replay explicit beside the atomic, barrier, and raw-pointer bridge coverage, so the whole-record accessors should now be treated as landed replay evidence on current `master`.",
        "Reviewers should treat the low-level wrapper family as materially landed as a bounded packet on current `master`: one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, the shared narrow-unsafe decoder plus interop-policy raw-pointer bridge entrypoints, the dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one returned shared Makefile replay gate, and one direct replay command are directly readable, while the separately readable Phase 3 catalog-selftest guard stays adjacent cross-packet support rather than extra low-level-wrapper proof.",
        "Current `master` now separately exposes the adjacent shared Phase 3 validator entrypoint through `scripts/zigux/validate-phase3.py`, the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, the shared ABI catalog helper through `scripts/zigux/phase3_catalog.py`, the export/UAPI boundary survey note through `Documentation/zigux/phase3-export-uapi-boundary-survey.md`, the packet-local export/UAPI survey validator through `scripts/zigux/validate-phase3-export-uapi-survey.py`, the focused export/UAPI layout replay through `zigux/tests/phase3_export_uapi_layout.zig` plus `zigux/tests/phase3_export_uapi_layout_build.zig`, and the adjacent catalog-selftest guard through `scripts/zigux/check-phase3-catalog-selftest.py`, and those separate surfaces should stay framed as cross-packet support rather than as landed same-lane proof.",
    ),
    ATOMIC_PATH: (
        "pub fn strongestAllowedFailureOrder(success: Ordering) ?Ordering {",
        "pub fn weakestAllowedFailureOrder(success: Ordering) ?Ordering {",
        "pub fn load(comptime T: type, ptr: *const T, comptime order: Ordering) LoadError!T {",
        "pub fn store(comptime T: type, ptr: *T, value: T, comptime order: Ordering) StoreError!void {",
        "pub fn exchange(",
        "pub fn compareExchangeFailureOrderAllowed(success: Ordering, failure: Ordering) bool {",
        "pub fn compareExchangeStrong(",
        "pub fn compareExchangeWeak(",
        "pub fn fetchAdd(",
        "pub fn fetchSub(",
        "pub fn fetchNand(",
        "pub fn fetchOr(",
        "pub fn fetchAnd(",
        "pub fn fetchXor(",
        "pub fn fetchMin(",
        "pub fn fetchMax(",
    ),
    BARRIER_PATH: (
        "pub fn compiler() void {",
        "pub fn acquire() void {",
        "pub fn release() void {",
        "pub fn full() void {",
        "pub fn acquireRelease() void {",
        "pub fn fullFence() void {",
    ),
    MMIO_PATH: (
        "pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn allowsInteropPolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
        "pub fn allowsInteropPolicyByte(unsafe_scope: u8) bool {",
        "pub fn requireVolatileMmioScope(scope: abi.UnsafeScope) PolicyError!void {",
        "pub fn requireInteropPolicy(policy: abi.InteropPolicy) PolicyError!void {",
        "pub fn requireInteropPolicyBytes(unsafe_scope: u8, reserved: u8) PolicyError!void {",
        "pub fn requireInteropPolicyByte(unsafe_scope: u8) PolicyError!void {",
        "pub fn read(comptime T: type, ptr: *const volatile T) T {",
        "pub fn write(comptime T: type, ptr: *volatile T, value: T) void {",
        "pub fn exchange(comptime T: type, ptr: *volatile T, value: T) T {",
        "pub fn writeMasked(comptime T: type, ptr: *volatile T, clear_mask: T, set_mask: T) T {",
        "pub fn readScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *const volatile T) PolicyError!T {",
        "pub fn writeScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *volatile T, value: T) PolicyError!void {",
        "pub fn exchangeScoped(comptime T: type, scope: abi.UnsafeScope, ptr: *volatile T, value: T) PolicyError!T {",
        "pub fn writeMaskedScoped(",
        "pub fn readInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *const volatile T) PolicyError!T {",
        "pub fn writeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!void {",
        "pub fn exchangeInteropPolicy(comptime T: type, policy: abi.InteropPolicy, ptr: *volatile T, value: T) PolicyError!T {",
        "pub fn writeMaskedInteropPolicy(",
        "pub fn readInteropPolicyBytes(",
        "pub fn readInteropPolicyByte(comptime T: type, unsafe_scope: u8, ptr: *const volatile T) PolicyError!T {",
        "pub fn writeInteropPolicyBytes(",
        "pub fn writeInteropPolicyByte(",
        "pub fn exchangeInteropPolicyBytes(",
        "pub fn exchangeInteropPolicyByte(",
        "pub fn writeMaskedInteropPolicyBytes(",
        "pub fn writeMaskedInteropPolicyByte(",
    ),
    UNSAFE_POLICY_PATH: (
        "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {",
        "pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {",
        "pub fn permitsVolatileMmio(mode: abi.UnsafeScope) bool {",
        "pub fn permitsRawPointerBridge(mode: abi.UnsafeScope) bool {",
        "pub fn permitsRawPointerBridgeByte(scope: u8) bool {",
    ),
    NARROW_PATH: (
        "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
        "pub fn permitsRawPointerBridge(scope: UnsafeScopeTag) bool {",
        "pub fn permitsRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) bool {",
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requireRawPointerBridgePolicyBytes(unsafe_scope: u8, reserved: u8) UnsafeScopeError!void {",
        "pub fn requireRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) UnsafeScopeError!void {",
        "pub fn pointerAtInteropPolicyBytes(comptime T: type, address: usize, byte_len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) T {",
        "pub fn pointerAtInteropPolicy(comptime T: type, address: usize, byte_len: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) T {",
        "pub fn pointerAtByte(comptime T: type, address: usize, byte_len: usize, scope: u8) RawPointerBridgeError!*align(1) T {",
        "pub fn constPointerAtInteropPolicyBytes(comptime T: type, address: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!*align(1) const T {",
        "pub fn constPointerAtInteropPolicy(comptime T: type, address: usize, policy: abi.InteropPolicy) RawPointerBridgeError!*align(1) const T {",
        "pub fn constPointerAtByte(comptime T: type, address: usize, scope: u8) RawPointerBridgeError!*align(1) const T {",
        "pub fn constSliceAtInteropPolicyBytes(comptime T: type, address: usize, len: usize, unsafe_scope: u8, reserved: u8) RawPointerBridgeError![]align(1) const T {",
        "pub fn constSliceAtInteropPolicy(comptime T: type, address: usize, len: usize, policy: abi.InteropPolicy) RawPointerBridgeError![]align(1) const T {",
        "pub fn constSliceAtByte(comptime T: type, address: usize, len: usize, scope: u8) RawPointerBridgeError![]align(1) const T {",
        "pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {",
        "pub fn writeValueAtInteropPolicy(comptime T: type, address: usize, value: T, policy: abi.InteropPolicy) RawPointerBridgeError!void {",
        "pub fn writeValueAtByte(comptime T: type, address: usize, value: T, scope: u8) RawPointerBridgeError!void {",
    ),
    WRAPPER_REPLAY_PATH: (
        'test "phase3 low-level wrappers keep atomic ordering, barriers, and MMIO handoffs aligned" {',
        'test "phase3 low-level wrappers keep masked MMIO updates explicit after compare-exchange setup" {',
        'test "phase3 low-level wrappers keep monotonic strong compare-exchange mismatch explicit before MMIO publish" {',
        'test "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff" {',
        'test "phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates" {',
        'test "phase3 low-level wrappers keep MMIO single-byte interop-policy shorthands explicit" {',
        'test "phase3 low-level wrappers keep whole-record MMIO interop-policy helpers explicit" {',
        'test "phase3 low-level wrappers keep direct MMIO scope gates explicit" {',
        'test "phase3 low-level wrappers keep atomic load-store exchange and MMIO echo explicit" {',
        'test "phase3 low-level wrappers keep additive and bitwise atomic updates explicit before MMIO publish" {',
        'test "phase3 low-level wrappers keep exchange-style MMIO policy handoffs explicit" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge scope gates explicit beside MMIO policy gates" {',
        'test "phase3 low-level wrappers keep raw-pointer bridge byte coverage explicit" {',
        "try mmio.writeInteropPolicyBytes(u32, 1, 0, register_ptr, state);",
        "try mmio.readInteropPolicyBytes(u32, 1, 0, const_register_ptr),",
        "mmio.readInteropPolicyByte(u32, 1, const_register_ptr)",
        "mmio.writeInteropPolicyByte(u32, 1, register_ptr, 0x1234_5678)",
        "mmio.exchangeInteropPolicyByte(u32, 1, register_ptr, 0xCAFE_BABE)",
        "mmio.writeMaskedInteropPolicyByte(u32, 1, register_ptr, 0x00F0_0FF0, 0x000E_000E)",
        "const updated = try mmio.writeMaskedInteropPolicyBytes(",
        "try mmio.exchangeInteropPolicyBytes(u16, 1, 0, register_ptr, 0x0F0F),",
    ),
    WRAPPER_BUILD_PATH: (
        '.root_source_file = b.path("../helpers/atomic.zig"),',
        '.root_source_file = b.path("../helpers/barrier.zig"),',
        '.root_source_file = b.path("../helpers/mmio.zig"),',
        'narrow.addImport("abi_bindings", abi_bindings);',
        'root_module.addImport("atomic", atomic);',
        'root_module.addImport("barrier", barrier);',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("narrow", narrow);',
        'mmio.addImport("abi_bindings", abi_bindings);',
        'mmio.addImport("unsafe_policy", unsafe_policy);',
        '"phase3-low-level-wrappers-test"',
    ),
    SHARED_TESTS_README_PATH: (
        "## Phase 3 shared substrate packet",
        "`Documentation/zigux/phase3-export-uapi-boundary-survey.md`",
        "`scripts/zigux/validate-phase3-export-uapi-survey.py`",
        "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/tests/phase3_low_level_wrappers.zig`",
        "`zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`zig build phase3-export-uapi-layout --build-file zigux/tests/build.zig`",
        "`zig build phase3-low-level-wrappers --build-file zigux/tests/build.zig`",
        "`zig build phase3-test --build-file zigux/tests/build.zig`",
    ),
    SHARED_TESTS_BUILD_PATH: (
        "fn addPhase3LowLevelWrappers(",
        '.root_source_file = b.path("../helpers/atomic.zig"),',
        '.root_source_file = b.path("../helpers/barrier.zig"),',
        '.root_source_file = b.path("../helpers/mmio.zig"),',
        '"phase3-low-level-wrappers"',
        '"phase3-test"',
        "phase3_low_level_wrapper_step.dependOn(&phase3_low_level_wrappers.step);",
        "phase3_test_step.dependOn(&phase3_low_level_wrappers.step);",
    ),
    MAKEFILE_PATH: (
        "phase3: phase3-validate phase3-export-uapi-layout phase3-low-level-wrappers phase3-test phase3-policy-dump phase3-dump",
        "phase3-low-level-wrappers-test:",
        "cd $(ZIGUX_ROOT) && $(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    WORKFLOW_PATH: (
        "name: Self-test current Phase 3 low-level wrapper survey validator",
        "run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
        "name: Check current Phase 3 low-level wrapper survey packet",
        "name: Run current Phase 3 low-level wrapper replay",
        "run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
}

SELF_TEST_CASES = tuple(
    (relative_path, marker)
    for relative_path, markers in REQUIRED_MARKERS.items()
    for marker in markers
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_low_level_wrapper_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, ""), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 low-level wrapper survey packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 low-level wrapper survey packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    print("PHASE3_LOW_LEVEL_WRAPPER_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
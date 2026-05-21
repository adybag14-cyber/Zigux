#!/usr/bin/env python3
"""Fail-close the current Phase 3 policy and unsafe boundary survey packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md")
POLICY_SLICE_PATH = Path("Documentation/zigux/phase3-policy-slice.md")
LOW_LEVEL_WRAPPER_PATH = Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md")
LAYOUT_ASSERT_PATH = Path("zigux/helpers/layout_assert.zig")
PANIC_POLICY_PATH = Path("zigux/helpers/panic_policy.zig")
ALLOCATOR_POLICY_PATH = Path("zigux/helpers/allocator_policy.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
MMIO_PATH = Path("zigux/helpers/mmio.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
POLICY_STARTER_PACKET_PATH = Path("zigux/tests/phase3_policy_starter_packet.zig")
POLICY_STARTER_PACKET_BUILD_PATH = Path(
    "zigux/tests/phase3_policy_starter_packet_build.zig"
)
POLICY_STARTER_PACKET_MANIFEST_PATH = Path(
    "zigux/tests/phase3_policy_starter_packet_manifest.json"
)
POLICY_STARTER_PACKET_CHECK_PATH = Path(
    "scripts/zigux/check-phase3-policy-starter-packet.py"
)
POLICY_DUMP_PATH = Path("zigux/tests/phase3_policy_dump.zig")
POLICY_DUMP_BUILD_PATH = Path("zigux/tests/phase3_policy_dump_build.zig")
POLICY_DUMP_EXPECTED_PATH = Path("zigux/tests/fixtures/phase3_policy_dump_expected.txt")
POLICY_DUMP_CHECK_PATH = Path("scripts/zigux/check-phase3-policy-dump.py")
LOW_LEVEL_WRAPPER_SURVEY_CHECK_PATH = Path(
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"
)

REQUIRED_MARKERS = {
    NOTE_PATH: (
        "PHASE3_POLICY_SLICE_DOC_BLOB_SHA=",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_DOC_BLOB_SHA=",
        "PHASE3_POLICY_PACKET_GATE=python3 scripts/zigux/check-phase3-policy-starter-packet.py",
        "PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_GATE=python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
        "PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
        "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-helper-local-policy-slice-and-the-directly-coupled-low-level-wrapper-packet",
        "PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-layout-assert-panic-policy-allocator-policy-unsafe-policy-mmio-or-narrow-helper-surfaces-drift-again",
        "the live proof surface has split into a helper-local policy slice plus a directly coupled low-level-wrapper packet",
        "`zigux/helpers/unsafe_policy.zig` is now the helper-local unsafe-scope decoder",
        "`permitsVolatileMmio`, and `permitsRawPointerBridge`, including the newer scope and permits symmetry aliases",
        "`Documentation/zigux/phase3-policy-slice.md`, `zigux/tests/phase3_policy_starter_packet_manifest.json`, `scripts/zigux/check-phase3-policy-starter-packet.py`, `zigux/tests/phase3_policy_dump.zig`, `zigux/tests/phase3_policy_dump_build.zig`, `zigux/tests/fixtures/phase3_policy_dump_expected.txt`, and `scripts/zigux/check-phase3-policy-dump.py` now keep the helper-local panic, allocator, and unsafe-policy decoders reviewable as one bounded packet through both the starter manifest route and the focused policy dump route.",
        "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig` keep the directly coupled MMIO-plus-narrow wrapper packet explicit without implying broader Phase 3 completion.",
    ),
    POLICY_SLICE_PATH: (
        "PHASE3_POLICY_SLICE_FILE_COUNT=current master now carries one bounded policy helper slice with shared ABI bindings, three helper-local decoders, one reusable layout guard, one cross-check narrow-surface decoder plus whole-policy and byte-level review entry points, one machine-readable manifest, one focused self-check replay route, one focused dump replay route, one dump expectation fixture, and one dedicated dump validator",
        "PHASE3_POLICY_SLICE_SCOPE=this slice proves shared InteropPolicy layout assertions, panic escalation, allocator-init ownership, and unsafe-scope reviewability by cross-checking the helper-local decoder against zigux/unsafe/narrow.zig, including the newer whole-policy and byte-level review entry points, and by replaying one focused policy dump that now also proves raw-pointer bridge reads and writes over the same bounded records without widening into unsafe wrappers, runtime shims, or broader export-boundary claims",
        "zigux/tests/phase3_policy_dump.zig",
        "zigux/tests/phase3_policy_dump_build.zig",
        "zigux/tests/fixtures/phase3_policy_dump_expected.txt",
        "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
        "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
        "the helper-local `zigux/helpers/unsafe_policy.zig` decoder remains the main replay route",
    ),
    LOW_LEVEL_WRAPPER_PATH: (
        "PHASE3_LOW_LEVEL_WRAPPER_SCOPE=the roadmap and bootstrap ledger still reserve a bounded Phase 3 low-level wrapper family for approved atomic, barrier, and MMIO wrappers, and current master now directly exposes one atomic helper shard, one barrier helper companion, one MMIO helper companion, one directly readable unsafe-policy companion, one shared narrow-unsafe decoder, this dedicated survey note, a dedicated survey validator, one focused low-level-wrapper replay shard, one dedicated shared build companion, one shared tests-root reminder, and one returned shared Makefile replay gate",
        "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the directly coupled unsafe-policy companion, the dedicated build companion, the shared tests-root reminder, the direct zig build phase3-low-level-wrappers-test replay route, and the returned Makefile replay gate while the adjacent catalog-selftest guard stays outside this wrapper packet",
        "`zigux/helpers/mmio.zig`",
        "`zigux/helpers/unsafe_policy.zig`",
        "`zigux/unsafe/narrow.zig`",
        "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py`",
        "`zigux/tests/README.md`",
        "`zigux/Makefile`",
        "`zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig`",
        "`make -C zigux phase3-low-level-wrappers-test`",
    ),
    LAYOUT_ASSERT_PATH: (
        "pub fn assertInteropPolicyLayout() LayoutError!void {",
        "pub fn assertNotifierBlockLayout() LayoutError!void {",
        "pub fn assertNotifierChainPriorityIncreaseLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout() LayoutError!void {",
        "pub fn assertInteropPolicyModeValues() void {",
        "pub fn assertNotifierResultValues() void {",
    ),
    PANIC_POLICY_PATH: (
        "pub const Escalation = enum {",
        "pub fn escalationFor(mode: abi.PanicMode) Escalation {",
        "pub fn permitsWarningOnlyContinuation(mode: abi.PanicMode) bool {",
    ),
    ALLOCATOR_POLICY_PATH: (
        "pub const InitFlow = enum {",
        "pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {",
        "pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {",
    ),
    UNSAFE_POLICY_PATH: (
        "pub const AccessBoundary = enum {",
        "pub fn accessBoundaryFor(mode: abi.UnsafeScope) AccessBoundary {",
        "pub fn allowsTypedOnlyAccess(mode: abi.UnsafeScope) bool {",
        "pub fn requiresDedicatedAudit(mode: abi.UnsafeScope) bool {",
        "pub fn permitsVolatileMmio(mode: abi.UnsafeScope) bool {",
        "pub fn permitsRawPointerBridge(mode: abi.UnsafeScope) bool {",
    ),
    MMIO_PATH: (
        "pub fn exchangeInteropPolicyBytes(",
        "pub fn writeMaskedInteropPolicyBytes(",
        "pub fn allowsInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn requireInteropPolicy(policy: abi.InteropPolicy) PolicyError!void {",
    ),
    NARROW_PATH: (
        "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
        "pub fn surfaceFor(scope: UnsafeScopeTag) Surface {",
        "pub fn pointerAtInteropPolicyBytes(",
        "pub fn writeValueAtInteropPolicyBytes(",
    ),
    POLICY_STARTER_PACKET_PATH: (
        'test "policy starter packet decodes shared interop policy records" {',
        'test "policy starter packet keeps interop-policy layout explicit" {',
        'test "policy starter packet exercises exported layout assertion guards" {',
        'test "policy starter packet keeps narrow-surface decoding aligned" {',
        'test "policy starter packet keeps unsafe alias symmetry explicit on shared records" {',
        'test "policy starter packet keeps panic and allocator byte guards explicit" {',
        'test "panic policy starter packet keeps escalation semantics explicit" {',
        'test "allocator policy starter packet keeps init ownership semantics explicit" {',
        'test "unsafe policy starter packet keeps access semantics explicit" {',
    ),
    POLICY_STARTER_PACKET_BUILD_PATH: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../helpers/panic_policy.zig"),',
        '.root_source_file = b.path("../helpers/allocator_policy.zig"),',
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        '.root_source_file = b.path("../helpers/layout_assert.zig"),',
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        'root_module.addImport("narrow_surface", narrow_surface);',
        '"phase3-policy-starter-packet-test"',
    ),
    POLICY_STARTER_PACKET_MANIFEST_PATH: (
        '"slug": "phase3-policy-starter-packet"',
        '"status": "policy_slice_present"',
        '"scope": "layout, panic, allocator, and unsafe interop policy decoding replay"',
        '"zigux/helpers/layout_assert.zig"',
        '"zigux/helpers/unsafe_policy.zig"',
        '"zigux/unsafe/narrow.zig"',
        '"scripts/zigux/check-phase3-policy-starter-packet.py"',
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"',
        '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
    ),
    POLICY_STARTER_PACKET_CHECK_PATH: (
        '"""Fail-close the current Phase 3 policy starter packet."""',
        "zigux/tests/phase3_policy_starter_packet.zig",
        "zigux/tests/phase3_policy_starter_packet_build.zig",
        "zigux/tests/phase3_policy_starter_packet_manifest.json",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
        "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass",
    ),
    POLICY_DUMP_PATH: (
        "safe-default",
        "mmio-bug",
        "raw-bridge-warn",
        "reserved-invalid",
        "panic={s}",
        "allocator={s}",
        "init_flow={s}",
        "explicit_caller={any}",
        "owned_state={any}",
        "reset_on_init={any}",
        "unsafe={s}",
        "bridge_read_ok={any}",
        "bridge_write_ok={any}",
        "narrow={s}",
    ),
    POLICY_DUMP_BUILD_PATH: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../helpers/panic_policy.zig"),',
        '.root_source_file = b.path("../helpers/allocator_policy.zig"),',
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        '.root_source_file = b.path("phase3_policy_dump.zig"),',
        '"phase3-policy-dump"',
    ),
    POLICY_DUMP_CHECK_PATH: (
        '"""Validate the focused Phase 3 policy dump packet."""',
        "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
        "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
        "PHASE3_POLICY_DUMP_SELF_TEST=pass",
    ),
    LOW_LEVEL_WRAPPER_SURVEY_CHECK_PATH: (
        '"""Fail-close the current Phase 3 low-level wrapper survey packet."""',
        "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
        "PHASE3_LOW_LEVEL_WRAPPER_SURVEY_SELF_TEST=pass",
    ),
}

EXPECTED_DUMP_LINES = (
    "safe-default|panic=abort|allocator=caller_provided|init_flow=caller_prepared|explicit_caller=true|owned_state=false|reset_on_init=false|unsafe=none|typed_only=true|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|bridge_read_ok=false|bridge_write_ok=false|narrow=none",
    "mmio-bug|panic=bug|allocator=kernel_heap|init_flow=helper_owned|explicit_caller=false|owned_state=true|reset_on_init=false|unsafe=volatile_mmio|typed_only=false|global_fallback=true|warn_only=false|mmio=true|raw_bridge=false|audit=true|bridge_read_ok=false|bridge_write_ok=false|narrow=volatile_mmio",
    "raw-bridge-warn|panic=warn|allocator=arena|init_flow=helper_owned_with_reset|explicit_caller=false|owned_state=true|reset_on_init=true|unsafe=raw_pointer_bridge|typed_only=false|global_fallback=true|warn_only=true|mmio=false|raw_bridge=true|audit=true|bridge_read_ok=true|bridge_write_ok=true|narrow=raw_pointer_bridge",
    "reserved-invalid|panic=invalid|allocator=invalid|init_flow=invalid|explicit_caller=false|owned_state=false|reset_on_init=false|unsafe=invalid|typed_only=false|global_fallback=false|warn_only=false|mmio=false|raw_bridge=false|audit=false|bridge_read_ok=false|bridge_write_ok=false|narrow=invalid",
)

SELF_TEST_CASES = (
    (NOTE_PATH, "PHASE3_POLICY_DUMP_GATE=python3 scripts/zigux/check-phase3-policy-dump.py"),
    (
        NOTE_PATH,
        "PHASE3_LOW_LEVEL_WRAPPER_TEST_GATE=zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    (
        NOTE_PATH,
        "PHASE3_BOUNDARY_GAP=no-dedicated-policy-unsafe-subslice-beyond-the-helper-local-policy-slice-and-the-directly-coupled-low-level-wrapper-packet",
    ),
    (
        NOTE_PATH,
        "PHASE3_NEXT_BOUNDED_STEP=leave-this-survey-parked-unless-layout-assert-panic-policy-allocator-policy-unsafe-policy-mmio-or-narrow-helper-surfaces-drift-again",
    ),
    (
        NOTE_PATH,
        "`permitsVolatileMmio`, and `permitsRawPointerBridge`, including the newer scope and permits symmetry aliases",
    ),
    (
        NOTE_PATH,
        "`Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md`, `scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, `zigux/tests/phase3_low_level_wrappers.zig`, and `zigux/tests/phase3_low_level_wrappers_build.zig` keep the directly coupled MMIO-plus-narrow wrapper packet explicit without implying broader Phase 3 completion.",
    ),
    (
        POLICY_SLICE_PATH,
        "PHASE3_POLICY_SLICE_SCOPE=this slice proves shared InteropPolicy layout assertions, panic escalation, allocator-init ownership, and unsafe-scope reviewability by cross-checking the helper-local decoder against zigux/unsafe/narrow.zig, including the newer whole-policy and byte-level review entry points, and by replaying one focused policy dump that now also proves raw-pointer bridge reads and writes over the same bounded records without widening into unsafe wrappers, runtime shims, or broader export-boundary claims",
    ),
    (
        LOW_LEVEL_WRAPPER_PATH,
        "PHASE3_LOW_LEVEL_WRAPPER_NEXT_STEP=keep low-level wrapper follow-through bounded to shared validation truthfulness around the directly coupled unsafe-policy companion, the dedicated build companion, the shared tests-root reminder, the direct zig build phase3-low-level-wrappers-test replay route, and the returned Makefile replay gate while the adjacent catalog-selftest guard stays outside this wrapper packet",
    ),
    (LAYOUT_ASSERT_PATH, "pub fn assertNotifierBlockLayout() LayoutError!void {"),
    (
        LAYOUT_ASSERT_PATH,
        "pub fn assertNotifierChainPriorityIncreaseLayout() LayoutError!void {",
    ),
    (
        LAYOUT_ASSERT_PATH,
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout() LayoutError!void {",
    ),
    (
        LAYOUT_ASSERT_PATH,
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout() LayoutError!void {",
    ),
    (
        LAYOUT_ASSERT_PATH,
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout() LayoutError!void {",
    ),
    (
        LAYOUT_ASSERT_PATH,
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout() LayoutError!void {",
    ),
    (LAYOUT_ASSERT_PATH, "pub fn assertInteropPolicyModeValues() void {"),
    (PANIC_POLICY_PATH, "pub fn escalationFor(mode: abi.PanicMode) Escalation {"),
    (ALLOCATOR_POLICY_PATH, "pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {"),
    (
        UNSAFE_POLICY_PATH,
        "pub fn requiresDedicatedAudit(mode: abi.UnsafeScope) bool {",
    ),
    (UNSAFE_POLICY_PATH, "pub fn permitsVolatileMmio(mode: abi.UnsafeScope) bool {"),
    (
        UNSAFE_POLICY_PATH,
        "pub fn permitsRawPointerBridge(mode: abi.UnsafeScope) bool {",
    ),
    (MMIO_PATH, "pub fn exchangeInteropPolicyBytes("),
    (NARROW_PATH, "pub fn pointerAtInteropPolicyBytes("),
    (
        POLICY_STARTER_PACKET_PATH,
        'test "policy starter packet keeps unsafe alias symmetry explicit on shared records" {',
    ),
    (
        POLICY_STARTER_PACKET_BUILD_PATH,
        'root_module.addImport("narrow_surface", narrow_surface);',
    ),
    (
        POLICY_STARTER_PACKET_MANIFEST_PATH,
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"',
    ),
    (
        POLICY_STARTER_PACKET_CHECK_PATH,
        "PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass",
    ),
    (POLICY_DUMP_PATH, "raw-bridge-warn"),
    (POLICY_DUMP_PATH, "bridge_read_ok={any}"),
    (POLICY_DUMP_PATH, "bridge_write_ok={any}"),
    (
        POLICY_DUMP_BUILD_PATH,
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
    ),
    (
        POLICY_DUMP_CHECK_PATH,
        "python3 scripts/zigux/check-phase3-policy-dump.py --self-test",
    ),
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

    expected_path = repo_root / POLICY_DUMP_EXPECTED_PATH
    try:
        expected_lines = _read(expected_path).splitlines()
    except FileNotFoundError:
        issues.append(f"missing repo file: {POLICY_DUMP_EXPECTED_PATH.as_posix()}")
    else:
        if expected_lines != list(EXPECTED_DUMP_LINES):
            issues.append(f"unexpected {POLICY_DUMP_EXPECTED_PATH.as_posix()} contents")

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        _write(root / relative_path, "\n".join(markers) + "\n")
    _write(root / POLICY_DUMP_EXPECTED_PATH, "\n".join(EXPECTED_DUMP_LINES) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_unsafe_survey_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

    print("PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST=pass")
    print(f"PHASE3_POLICY_UNSAFE_SURVEY_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 policy and unsafe boundary survey packet."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_POLICY_UNSAFE_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / NOTE_PATH}")
    print(f"validated {args.repo_root / POLICY_DUMP_PATH}")
    print(f"validated {args.repo_root / POLICY_DUMP_EXPECTED_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

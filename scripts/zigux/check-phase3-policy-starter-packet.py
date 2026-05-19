#!/usr/bin/env python3
"""Fail-close the current Phase 3 policy starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

POLICY_NOTE_PATH = Path("Documentation/zigux/phase3-policy-slice.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
SHARED_REMINDER_GAP_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDING_PATH = Path("zigux/bindings/abi.zig")
LAYOUT_ASSERT_PATH = Path("zigux/helpers/layout_assert.zig")
PANIC_POLICY_PATH = Path("zigux/helpers/panic_policy.zig")
ALLOCATOR_POLICY_PATH = Path("zigux/helpers/allocator_policy.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
TEST_PATH = Path("zigux/tests/phase3_policy_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_policy_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_policy_starter_packet_manifest.json")

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-policy-starter-packet.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig",
)

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-policy-starter-packet",
    "status": "policy_slice_present",
    "scope": "layout, panic, allocator, and unsafe interop policy decoding replay",
    "next_safe_step": "keep the policy helper family bounded to layout assertions, manifest-backed replay, and narrow-surface cross-checks before widening into mmio, low-level wrapper, or shared runtime-shim families",
}

REQUIRED_MARKERS = {
    POLICY_NOTE_PATH: (
        "PHASE3_POLICY_SLICE_FILE_COUNT=",
        "PHASE3_POLICY_SLICE_SCOPE=",
        "PHASE3_POLICY_NEXT_SAFE_STEP=",
        "zigux/helpers/layout_assert.zig",
        "zigux/helpers/unsafe_policy.zig",
        "zigux/unsafe/narrow.zig",
        "zigux/tests/phase3_policy_starter_packet_manifest.json",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
        "zigux/tests/phase3_abi.zig",
        "scripts/zigux/check-phase3-abi.py",
        "scripts/zigux/validate-phase3.py",
    ),
    VALIDATOR_NOTE_PATH: (
        "## Focused policy slice present on `master`",
        "Documentation/zigux/phase3-policy-slice.md",
        "zigux/helpers/layout_assert.zig",
        "zigux/helpers/panic_policy.zig",
        "zigux/helpers/allocator_policy.zig",
        "zigux/helpers/unsafe_policy.zig",
        "zigux/unsafe/narrow.zig",
        "zigux/tests/phase3_policy_starter_packet_manifest.json",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    ),
    SHARED_REMINDER_GAP_PATH: (
        "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the shared ABI catalog helper plus manifest-backed inventory companion, and the shared docs-root plus tests-root Phase 3 summaries now all reflect that return while scripts-root inventory work stays separate",
        "Documentation/zigux/phase3-policy-slice.md",
        "Documentation/zigux/README.md",
        "zigux/tests/README.md",
        "scripts/zigux/README.md remains a separate scripts-root reminder surface",
        "PHASE3_SHARED_REMINDER_NEXT_STEP=keep any future same-lane follow-through scoped to scripts/zigux/README.md inventory truthfulness, or rerun the shared-summary reread only if current master changes reopen Phase 3 reminder drift",
    ),
    ABI_HEADER_PATH: (
        "#define ZIGUX_PANIC_ABORT 0U",
        "#define ZIGUX_PANIC_BUG 1U",
        "#define ZIGUX_PANIC_WARN 2U",
        "#define ZIGUX_ALLOC_CALLER_PROVIDED 0U",
        "#define ZIGUX_ALLOC_KERNEL_HEAP 1U",
        "#define ZIGUX_ALLOC_ARENA 2U",
        "#define ZIGUX_UNSAFE_NONE 0U",
        "#define ZIGUX_UNSAFE_VOLATILE_MMIO 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "struct zigux_interop_policy {",
    ),
    ABI_BINDING_PATH: (
        "pub const PanicMode = enum(u8) {",
        "pub const AllocatorMode = enum(u8) {",
        "pub const UnsafeScope = enum(u8) {",
        "pub const InteropPolicy = extern struct {",
        "panic_mode: u8,",
        "allocator_mode: u8,",
        "unsafe_scope: u8,",
        "reserved: u8,",
    ),
    LAYOUT_ASSERT_PATH: (
        "pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void {",
        "pub fn expectFieldLayout(",
        'test "layout assert keeps starter header layouts explicit" {',
    ),
    PANIC_POLICY_PATH: (
        "pub const Escalation = enum {",
        "pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.PanicMode {",
        "pub fn escalationFor(mode: abi.PanicMode) Escalation {",
        "pub fn causesImmediateHalt(mode: abi.PanicMode) bool {",
        "pub fn emitsKernelBug(mode: abi.PanicMode) bool {",
        "pub fn permitsWarningOnlyContinuation(mode: abi.PanicMode) bool {",
    ),
    ALLOCATOR_POLICY_PATH: (
        "pub const InitFlow = enum {",
        "pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.AllocatorMode {",
        "pub fn initFlowFor(mode: abi.AllocatorMode) InitFlow {",
        "pub fn requiresExplicitCaller(mode: abi.AllocatorMode) bool {",
        "pub fn initializesOwnedState(mode: abi.AllocatorMode) bool {",
        "pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {",
    ),
    UNSAFE_POLICY_PATH: (
        "pub const AccessBoundary = enum {",
        "pub fn modeFromInteropPolicy(policy: abi.InteropPolicy) ?abi.UnsafeScope {",
        "pub fn scopeFromInteropPolicyBytes(scope: u8, reserved: u8) ?abi.UnsafeScope {",
        "pub fn accessBoundaryFor(mode: abi.UnsafeScope) AccessBoundary {",
        "pub fn allowsTypedOnlyAccess(mode: abi.UnsafeScope) bool {",
        "pub fn permitsVolatileMmio(mode: abi.UnsafeScope) bool {",
        "pub fn permitsRawPointerBridge(mode: abi.UnsafeScope) bool {",
        "pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    ),
    NARROW_PATH: (
        "pub const Surface = enum {",
        "pub fn scopeFromInteropPolicy(policy: abi.InteropPolicy) ?UnsafeScopeTag {",
        "pub fn allowsVolatileMmio(scope: UnsafeScopeTag) bool {",
        "pub fn allowsRawPointerBridge(scope: UnsafeScopeTag) bool {",
        "pub fn requiresDedicatedAudit(scope: UnsafeScopeTag) bool {",
    ),
    TEST_PATH: (
        'test "policy starter packet decodes shared interop policy records" {',
        'test "policy starter packet keeps interop-policy layout explicit" {',
        "layout_assert.expectLayout(abi.InteropPolicy, 4, 1)",
        'test "policy starter packet keeps narrow-surface decoding aligned" {',
        "narrow_surface.scopeFromInteropPolicy(case.policy)",
        "narrow_surface.requiresDedicatedAudit(scope)",
        'test "policy starter packet keeps unsafe alias symmetry explicit on shared records" {',
        "unsafe_policy.scopeFromInteropPolicy(case.policy)",
        "unsafe_policy.permitsNoUnsafeInteropPolicy(case.policy)",
        "unsafe_policy.allowsTypedOnlyAccessInteropPolicy(case.policy)",
        "unsafe_policy.permitsVolatileMmioInteropPolicy(case.policy)",
        "unsafe_policy.permitsRawPointerBridgeInteropPolicy(case.policy)",
        'test "panic policy starter packet keeps escalation semantics explicit" {',
        'test "allocator policy starter packet keeps init ownership semantics explicit" {',
        'test "unsafe policy starter packet keeps access semantics explicit" {',
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../helpers/panic_policy.zig"),',
        '.root_source_file = b.path("../helpers/allocator_policy.zig"),',
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        '.root_source_file = b.path("../helpers/layout_assert.zig"),',
        '.root_source_file = b.path("../unsafe/narrow.zig"),',
        '.root_source_file = b.path("phase3_policy_starter_packet.zig"),',
        'root_module.addImport("panic_policy", panic_policy);',
        'root_module.addImport("allocator_policy", allocator_policy);',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        'root_module.addImport("layout_assert", layout_assert);',
        'root_module.addImport("narrow_surface", narrow_surface);',
        '"phase3-policy-starter-packet-test"',
    ),
}

SAMPLE_MANIFEST = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-policy-starter-packet",
    "status": "policy_slice_present",
    "scope": "layout, panic, allocator, and unsafe interop policy decoding replay",
    "packet_files": list(REQUIRED_PACKET_FILES),
    "replay_routes": list(REQUIRED_REPLAY_ROUTES),
    "repo_reality_gaps": [],
    "next_safe_step": "keep the policy helper family bounded to layout assertions, manifest-backed replay, and narrow-surface cross-checks before widening into mmio, low-level wrapper, or shared runtime-shim families",
}

SELF_TEST_CASES = (
    (POLICY_NOTE_PATH, "PHASE3_POLICY_SLICE_FILE_COUNT="),
    (VALIDATOR_NOTE_PATH, "## Focused policy slice present on `master`"),
    (SHARED_REMINDER_GAP_PATH, "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the shared ABI catalog helper plus manifest-backed inventory companion, and the shared docs-root plus tests-root Phase 3 summaries now all reflect that return while scripts-root inventory work stays separate"),
    (ABI_HEADER_PATH, "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U"),
    (ABI_BINDING_PATH, "pub const UnsafeScope = enum(u8) {"),
    (LAYOUT_ASSERT_PATH, "pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void {"),
    (PANIC_POLICY_PATH, "pub fn emitsKernelBug(mode: abi.PanicMode) bool {"),
    (ALLOCATOR_POLICY_PATH, "pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {"),
    (UNSAFE_POLICY_PATH, "pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {"),
    (NARROW_PATH, "pub fn requiresDedicatedAudit(scope: UnsafeScopeTag) bool {"),
    (TEST_PATH, 'test "policy starter packet keeps unsafe alias symmetry explicit on shared records" {'),
    (BUILD_PATH, 'root_module.addImport("narrow_surface", narrow_surface);'),
)

SAMPLE_FILES = {path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()}
SAMPLE_FILES[MANIFEST_PATH] = json.dumps(SAMPLE_MANIFEST, indent=2) + "\n"


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

    manifest_path = repo_root / MANIFEST_PATH
    try:
        manifest = json.loads(_read(manifest_path))
    except FileNotFoundError:
        issues.append(f"missing repo file: {MANIFEST_PATH.as_posix()}")
        return issues
    except json.JSONDecodeError as exc:
        issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        return issues

    for field, expected in EXPECTED_MANIFEST_FIELDS.items():
        actual = manifest.get(field)
        if actual != expected:
            issues.append(
                "phase3_policy_starter_packet_manifest.json wrong "
                f"{field}: {actual!r} != {expected!r}"
            )

    packet_files = manifest.get("packet_files")
    replay_routes = manifest.get("replay_routes")
    repo_reality_gaps = manifest.get("repo_reality_gaps")
    if not isinstance(packet_files, list):
        issues.append("phase3_policy_starter_packet_manifest.json packet_files is not a list")
    if not isinstance(replay_routes, list):
        issues.append("phase3_policy_starter_packet_manifest.json replay_routes is not a list")
    if repo_reality_gaps != []:
        issues.append(
            "phase3_policy_starter_packet_manifest.json repo_reality_gaps should be [] "
            f"but was {repo_reality_gaps!r}"
        )

    if isinstance(packet_files, list):
        for required_path in REQUIRED_PACKET_FILES:
            if required_path not in packet_files:
                issues.append(
                    "phase3_policy_starter_packet_manifest.json missing packet_files entry: "
                    f"{required_path}"
                )

    if isinstance(replay_routes, list):
        for route in REQUIRED_REPLAY_ROUTES:
            if route not in replay_routes:
                issues.append(
                    "phase3_policy_starter_packet_manifest.json missing replay route: "
                    f"{route}"
                )

    return issues


def _populate_repo(root: Path) -> None:
    for relative_path, text in SAMPLE_FILES.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_policy_starter_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for relative_path, marker in SELF_TEST_CASES:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["repo_reality_gaps"] = ["zigux/tests/phase3_abi.zig"]
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected = (
            "phase3_policy_starter_packet_manifest.json repo_reality_gaps should be [] "
            "but was ['zigux/tests/phase3_abi.zig']"
        )
        if expected not in issues:
            print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=fail")
            print("expected stale repo_reality_gaps report was not emitted")
            return 1

    print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES) + 1}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 policy starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 policy starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_POLICY_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

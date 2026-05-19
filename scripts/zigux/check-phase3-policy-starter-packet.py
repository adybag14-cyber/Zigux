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
NOTIFIER_BINDING_PATH = Path("zigux/bindings/notifier_abi.zig")
LAYOUT_ASSERT_PATH = Path("zigux/helpers/layout_assert.zig")
PANIC_POLICY_PATH = Path("zigux/helpers/panic_policy.zig")
ALLOCATOR_POLICY_PATH = Path("zigux/helpers/allocator_policy.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
NARROW_PATH = Path("zigux/unsafe/narrow.zig")
TEST_PATH = Path("zigux/tests/phase3_policy_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_policy_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_policy_starter_packet_manifest.json")

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-policy-starter-packet",
    "status": "policy_slice_present",
    "scope": "layout, panic, allocator, and unsafe interop policy decoding replay",
    "next_safe_step": "keep the policy helper family bounded to layout assertions, manifest-backed replay, and narrow-surface cross-checks before widening into mmio, low-level wrapper, or shared runtime-shim families",
}

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

REQUIRED_REPO_REALITY_GAPS = (
    "scripts/zigux/check-phase3-catalog-selftest.py",
)

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
        "Current `master` now separately serves the shared ABI core replay through `zigux/tests/phase3_abi.zig`, the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, and the shared Phase 3 validator entrypoint through `scripts/zigux/validate-phase3.py`",
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
        "scripts/zigux/check-phase3-policy-starter-packet.py",
        "scripts/zigux/check-phase3-abi.py",
        "scripts/zigux/validate-phase3.py",
    ),
    SHARED_REMINDER_GAP_PATH: (
        "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the shared ABI catalog helper plus manifest-backed inventory companion, and the shared docs-root plus tests-root Phase 3 summaries now all reflect that return while scripts-root inventory work stays separate",
        "Documentation/zigux/phase3-policy-slice.md",
        "Documentation/zigux/README.md",
        "zigux/tests/README.md",
        "scripts/zigux/README.md",
        "scripts/zigux/phase3_catalog.py",
        "zigux/tests/fixtures/phase3_abi_manifest.json",
        "PHASE3_SHARED_REMINDER_NEXT_STEP=keep any future same-lane follow-through scoped to scripts/zigux/README.md inventory truthfulness, or rerun the shared-summary reread only if current master changes reopen Phase 3 reminder drift",
    ),
    ABI_HEADER_PATH: (
        "#define ZIGUX_PANIC_ABORT 0U",
        "#define ZIGUX_ALLOC_KERNEL_HEAP 1U",
        "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U",
        "struct zigux_interop_policy {",
    ),
    ABI_BINDING_PATH: (
        "pub const PanicMode = enum(u8) {",
        "pub const AllocatorMode = enum(u8) {",
        "pub const UnsafeScope = enum(u8) {",
        "pub const InteropPolicy = extern struct {",
    ),
    NOTIFIER_BINDING_PATH: (
        "pub const NotifierBlock = extern struct {",
    ),
    LAYOUT_ASSERT_PATH: (
        "pub fn expectLayout(comptime T: type, size: usize, alignment: usize) LayoutError!void {",
        "pub fn assertBoundaryHeaderLayout() LayoutError!void {",
        "pub fn assertExportStatusLayout() LayoutError!void {",
        "pub fn assertInteropPolicyLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout() LayoutError!void {",
        "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout() LayoutError!void {",
        "pub fn assertInteropPolicyModeValues() void {",
    ),
    PANIC_POLICY_PATH: (
        "pub const Escalation = enum {",
        "pub fn emitsKernelBug(mode: abi.PanicMode) bool {",
    ),
    ALLOCATOR_POLICY_PATH: (
        "pub const InitFlow = enum {",
        "pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {",
    ),
    UNSAFE_POLICY_PATH: (
        "pub const AccessBoundary = enum {",
        "pub fn permitsNoUnsafeInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn permitsVolatileMmioInteropPolicy(policy: abi.InteropPolicy) bool {",
        "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {",
    ),
    NARROW_PATH: (
        "pub const Surface = enum {",
        "pub fn scopeFromInteropPolicyBytes(unsafe_scope: u8, reserved: u8) ?UnsafeScopeTag {",
        "pub fn writeValueAtInteropPolicyBytes(comptime T: type, address: usize, value: T, unsafe_scope: u8, reserved: u8) RawPointerBridgeError!void {",
    ),
    TEST_PATH: (
        'test "policy starter packet decodes shared interop policy records" {',
        'test "policy starter packet keeps unsafe alias symmetry explicit on shared records" {',
        'test "panic policy starter packet keeps escalation semantics explicit" {',
        'test "allocator policy starter packet keeps init ownership semantics explicit" {',
        'test "unsafe policy starter packet keeps access semantics explicit" {',
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        'root_module.addImport("narrow_surface", narrow_surface);',
        '"phase3-policy-starter-packet-test"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-policy-starter-packet"',
        '"status": "policy_slice_present"',
        '"zigux/helpers/layout_assert.zig"',
        '"zigux/unsafe/narrow.zig"',
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"',
        '"scripts/zigux/check-phase3-catalog-selftest.py"',
    ),
}

SELF_TEST_CASES = (
    (POLICY_NOTE_PATH, "PHASE3_POLICY_SLICE_FILE_COUNT="),
    (POLICY_NOTE_PATH, "Current `master` now separately serves the shared ABI core replay through `zigux/tests/phase3_abi.zig`, the shared ABI checker through `scripts/zigux/check-phase3-abi.py`, and the shared Phase 3 validator entrypoint through `scripts/zigux/validate-phase3.py`"),
    (VALIDATOR_NOTE_PATH, "## Focused policy slice present on `master`"),
    (SHARED_REMINDER_GAP_PATH, "PHASE3_SHARED_REMINDER_GAP=current master now directly serves the packet-local export/UAPI survey note and validator, the shared ABI catalog helper plus manifest-backed inventory companion, and the shared docs-root plus tests-root Phase 3 summaries now all reflect that return while scripts-root inventory work stays separate"),
    (ABI_HEADER_PATH, "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U"),
    (LAYOUT_ASSERT_PATH, "pub fn assertInteropPolicyLayout() LayoutError!void {"),
    (LAYOUT_ASSERT_PATH, "pub fn assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout() LayoutError!void {"),
    (LAYOUT_ASSERT_PATH, "pub fn assertInteropPolicyModeValues() void {"),
    (UNSAFE_POLICY_PATH, "pub fn permitsRawPointerBridgeInteropPolicy(policy: abi.InteropPolicy) bool {"),
    (TEST_PATH, 'test "unsafe policy starter packet keeps access semantics explicit" {'),
    (BUILD_PATH, '"phase3-policy-starter-packet-test"'),
    (MANIFEST_PATH, '"scripts/zigux/check-phase3-catalog-selftest.py"'),
)

SAMPLE_FILES = {path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()}
SAMPLE_FILES[MANIFEST_PATH] = json.dumps(
    {
        **EXPECTED_MANIFEST_FIELDS,
        "packet_files": list(REQUIRED_PACKET_FILES),
        "replay_routes": list(REQUIRED_REPLAY_ROUTES),
        "repo_reality_gaps": list(REQUIRED_REPO_REALITY_GAPS),
    },
    indent=2,
) + "\n"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _append_duplicate_list_entry_issues(
    manifest_name: str,
    field_name: str,
    values: list[object],
    issues: list[str],
) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{manifest_name} duplicate {field_name} entry: "
            f"{value!r} (first index {first_index}, duplicate index {index})"
        )


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
    if manifest_path.exists():
        try:
            manifest = json.loads(_read(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
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
            if not isinstance(repo_reality_gaps, list):
                issues.append(
                    "phase3_policy_starter_packet_manifest.json repo_reality_gaps is not a list"
                )
            if isinstance(packet_files, list):
                _append_duplicate_list_entry_issues(
                    "phase3_policy_starter_packet_manifest.json",
                    "packet_files",
                    packet_files,
                    issues,
                )
                for required_path in REQUIRED_PACKET_FILES:
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_policy_starter_packet_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                _append_duplicate_list_entry_issues(
                    "phase3_policy_starter_packet_manifest.json",
                    "replay_routes",
                    replay_routes,
                    issues,
                )
                for route in REQUIRED_REPLAY_ROUTES:
                    if route not in replay_routes:
                        issues.append(
                            "phase3_policy_starter_packet_manifest.json missing replay route: "
                            f"{route}"
                        )
            if isinstance(repo_reality_gaps, list):
                _append_duplicate_list_entry_issues(
                    "phase3_policy_starter_packet_manifest.json",
                    "repo_reality_gaps",
                    repo_reality_gaps,
                    issues,
                )
                for gap in repo_reality_gaps:
                    if (repo_root / gap).exists():
                        issues.append(
                            "phase3_policy_starter_packet_manifest.json repo_reality_gaps entry is present on disk: "
                            f"{gap}"
                        )
                for gap in REQUIRED_REPO_REALITY_GAPS:
                    if gap not in repo_reality_gaps:
                        issues.append(
                            "phase3_policy_starter_packet_manifest.json missing repo_reality_gaps entry: "
                            f"{gap}"
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
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].append(REQUIRED_REPLAY_ROUTES[0])
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_duplicate_replay = (
            "phase3_policy_starter_packet_manifest.json duplicate replay_routes entry: "
            "'python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test' "
        )
        if not any(issue.startswith(expected_duplicate_replay) for issue in issues):
            print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=fail")
            print(f"expected duplicate replay-route guard was not reported: {expected_duplicate_replay}")
            return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"] = []
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_missing_gap = (
            "phase3_policy_starter_packet_manifest.json missing repo_reality_gaps entry: "
            "scripts/zigux/check-phase3-catalog-selftest.py"
        )
        if expected_missing_gap not in issues:
            print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=fail")
            print(f"expected repo-reality-gap guard was not reported: {expected_missing_gap}")
            return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["repo_reality_gaps"].append(TEST_PATH.as_posix())
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_present_gap = (
            "phase3_policy_starter_packet_manifest.json repo_reality_gaps entry is present on disk: "
            "zigux/tests/phase3_policy_starter_packet.zig"
        )
        if expected_present_gap not in issues:
            print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=fail")
            print(f"expected present-on-disk gap guard was not reported: {expected_present_gap}")
            return 1

    print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES) + 3}")
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

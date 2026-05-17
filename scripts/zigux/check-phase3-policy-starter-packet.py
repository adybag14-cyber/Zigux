#!/usr/bin/env python3
"""Fail-close the current Phase 3 policy starter packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


POLICY_NOTE_PATH = Path("Documentation/zigux/phase3-policy-slice.md")
VALIDATOR_NOTE_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
SHARED_REMINDER_GAP_PATH = Path("Documentation/zigux/phase3-shared-reminder-gap.md")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDING_PATH = Path("zigux/bindings/abi.zig")
PANIC_POLICY_PATH = Path("zigux/helpers/panic_policy.zig")
ALLOCATOR_POLICY_PATH = Path("zigux/helpers/allocator_policy.zig")
UNSAFE_POLICY_PATH = Path("zigux/helpers/unsafe_policy.zig")
TEST_PATH = Path("zigux/tests/phase3_policy_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_policy_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_policy_starter_packet_manifest.json")

HEADER_TYPEDEF_ALIAS_RE = re.compile(r"^\s*}\s*([A-Za-z_][A-Za-z0-9_]*)\s*;")
ZIG_PUB_FN_RE = re.compile(r"^\s*pub fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
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
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3.py",
    "zigux/tests/phase3_export_uapi_layout.zig",
)

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-policy-starter-packet",
    "status": "policy_slice_present",
    "scope": "panic, allocator, and unsafe interop policy decoding replay",
    "next_safe_step": "keep the policy helper family bounded to manifest-backed replay and truthful reminder surfaces before widening into mmio, low-level wrapper, or shared runtime-shim families",
}

REQUIRED_MARKERS = {
    POLICY_NOTE_PATH: (
        "PHASE3_POLICY_SLICE_FILE_COUNT=",
        "PHASE3_POLICY_SLICE_SCOPE=",
        "PHASE3_POLICY_NEXT_SAFE_STEP=",
        "zigux/helpers/unsafe_policy.zig",
        "zigux/tests/phase3_policy_starter_packet_manifest.json",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
        "zigux/unsafe/narrow.zig",
    ),
    VALIDATOR_NOTE_PATH: (
        "## Focused policy slice present on `master`",
        "Documentation/zigux/phase3-policy-slice.md",
        "zigux/helpers/panic_policy.zig",
        "zigux/helpers/allocator_policy.zig",
        "zigux/helpers/unsafe_policy.zig",
        "zigux/tests/phase3_policy_starter_packet_manifest.json",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
        "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    ),
    SHARED_REMINDER_GAP_PATH: (
        "PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit",
        "Documentation/zigux/phase3-policy-slice.md",
        "include/zigux/abi.h",
        "zigux/bindings/abi.zig",
        "zigux/helpers/panic_policy.zig",
        "zigux/helpers/allocator_policy.zig",
        "zigux/helpers/unsafe_policy.zig",
        "zigux/tests/phase3_policy_starter_packet.zig",
        "zigux/tests/phase3_policy_starter_packet_build.zig",
        "Documentation/zigux/README.md",
        "zigux/tests/README.md",
        "Documentation/zigux/review-checklist.md",
        "PHASE3_SHARED_REMINDER_NEXT_STEP=narrow Documentation/zigux/README.md, zigux/tests/README.md, and Documentation/zigux/review-checklist.md so they all describe the bounded three-slice Phase 3 posture",
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
        "pub fn accessBoundaryFor(mode: abi.UnsafeScope) AccessBoundary {",
        "pub fn allowsTypedOnlyAccess(mode: abi.UnsafeScope) bool {",
        "pub fn requiresVolatileMmioAccess(mode: abi.UnsafeScope) bool {",
        "pub fn requiresRawPointerBridge(mode: abi.UnsafeScope) bool {",
    ),
    TEST_PATH: (
        'test "policy starter packet decodes shared interop policy records" {',
        'test "panic policy starter packet keeps escalation semantics explicit" {',
        'test "allocator policy starter packet keeps init ownership semantics explicit" {',
        'test "unsafe policy starter packet keeps access semantics explicit" {',
        "panic_policy.modeFromInteropPolicy(bug_heap)",
        "allocator_policy.modeFromInteropPolicy(warn_arena)",
        "unsafe_policy.modeFromInteropPolicy(warn_arena)",
        "unsafe_policy.requiresRawPointerBridge(.raw_pointer_bridge)",
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../bindings/abi.zig"),',
        '.root_source_file = b.path("../helpers/panic_policy.zig"),',
        '.root_source_file = b.path("../helpers/allocator_policy.zig"),',
        '.root_source_file = b.path("../helpers/unsafe_policy.zig"),',
        '.root_source_file = b.path("phase3_policy_starter_packet.zig"),',
        'root_module.addImport("panic_policy", panic_policy);',
        'root_module.addImport("allocator_policy", allocator_policy);',
        'root_module.addImport("unsafe_policy", unsafe_policy);',
        '"phase3-policy-starter-packet-test"',
    ),
    MANIFEST_PATH: (
        '"slug": "phase3-policy-starter-packet"',
        '"status": "policy_slice_present"',
        '"Documentation/zigux/phase3-policy-slice.md"',
        '"zigux/helpers/panic_policy.zig"',
        '"zigux/helpers/allocator_policy.zig"',
        '"zigux/helpers/unsafe_policy.zig"',
        '"python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test"',
        '"zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"',
        '"next_safe_step": "keep the policy helper family bounded to manifest-backed replay and truthful reminder surfaces before widening into mmio, low-level wrapper, or shared runtime-shim families"',
        '"repo_reality_gaps": [',
        '"scripts/zigux/validate-phase3.py"',
    ),
}

DUPLICATE_DECLARATION_PATTERNS = {
    ABI_HEADER_PATH: (("ABI typedef alias", HEADER_TYPEDEF_ALIAS_RE),),
    ABI_BINDING_PATH: (("ABI binding pub fn", ZIG_PUB_FN_RE),),
}

SELF_TEST_CASES = (
    (POLICY_NOTE_PATH, "PHASE3_POLICY_SLICE_FILE_COUNT="),
    (VALIDATOR_NOTE_PATH, "## Focused policy slice present on `master`"),
    (
        SHARED_REMINDER_GAP_PATH,
        "PHASE3_SHARED_REMINDER_GAP=current master now keeps the bounded dev_t starter packet plus the focused err_ptr/xarray and policy slices explicit",
    ),
    (ABI_HEADER_PATH, "#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U"),
    (ABI_BINDING_PATH, "pub const UnsafeScope = enum(u8) {"),
    (PANIC_POLICY_PATH, "pub fn emitsKernelBug(mode: abi.PanicMode) bool {"),
    (ALLOCATOR_POLICY_PATH, "pub fn requiresResetOnInit(mode: abi.AllocatorMode) bool {"),
    (UNSAFE_POLICY_PATH, "pub fn requiresRawPointerBridge(mode: abi.UnsafeScope) bool {"),
    (TEST_PATH, "unsafe_policy.requiresRawPointerBridge(.raw_pointer_bridge)"),
    (BUILD_PATH, 'root_module.addImport("unsafe_policy", unsafe_policy);'),
    (MANIFEST_PATH, '"zigux/helpers/unsafe_policy.zig"'),
)


SAMPLE_FILES = {path: "\n".join(markers) + "\n" for path, markers in REQUIRED_MARKERS.items()}
SAMPLE_FILES[ABI_HEADER_PATH] = """#define ZIGUX_PANIC_ABORT 0U
#define ZIGUX_PANIC_BUG 1U
#define ZIGUX_PANIC_WARN 2U
#define ZIGUX_ALLOC_CALLER_PROVIDED 0U
#define ZIGUX_ALLOC_KERNEL_HEAP 1U
#define ZIGUX_ALLOC_ARENA 2U
#define ZIGUX_UNSAFE_NONE 0U
#define ZIGUX_UNSAFE_VOLATILE_MMIO 1U
#define ZIGUX_UNSAFE_RAW_POINTER_BRIDGE 2U
struct zigux_interop_policy {
    unsigned char panic_mode;
    unsigned char allocator_mode;
    unsigned char unsafe_scope;
    unsigned char reserved;
} zigux_boundary_header;
"""
SAMPLE_FILES[ABI_BINDING_PATH] = """pub const PanicMode = enum(u8) {
pub const AllocatorMode = enum(u8) {
pub const UnsafeScope = enum(u8) {
pub const InteropPolicy = extern struct {
panic_mode: u8,
allocator_mode: u8,
unsafe_scope: u8,
reserved: u8,
pub fn defaultHeader(flags: u16) BoundaryHeader {
"""
SAMPLE_FILES[MANIFEST_PATH] = """{
  "phase": "Phase 3",
  "lane": "abi-runtime",
  "slug": "phase3-policy-starter-packet",
  "status": "policy_slice_present",
  "scope": "panic, allocator, and unsafe interop policy decoding replay",
  "packet_files": [
    "Documentation/zigux/phase3-policy-slice.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    "zigux/tests/phase3_policy_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-policy-starter-packet.py"
  ],
  "replay_routes": [
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-policy-starter-packet.py",
    "zig build phase3-policy-starter-packet-test --build-file zigux/tests/phase3_policy_starter_packet_build.zig"
  ],
  "repo_reality_gaps": [
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/validate-phase3.py",
    "zigux/tests/phase3_export_uapi_layout.zig"
  ],
  "next_safe_step": "keep the policy helper family bounded to manifest-backed replay and truthful reminder surfaces before widening into mmio, low-level wrapper, or shared runtime-shim families"
}
"""


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _append_duplicate_declaration_issues(
    relative_path: Path,
    text: str,
    label: str,
    pattern: re.Pattern[str],
    issues: list[str],
) -> None:
    seen: dict[str, int] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = pattern.match(line)
        if match is None:
            continue
        name = match.group(1)
        first_line = seen.get(name)
        if first_line is None:
            seen[name] = line_no
            continue
        issues.append(
            f"duplicate {label}: {name} "
            f"(first line {first_line}, duplicate line {line_no})"
        )


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
        for label, pattern in DUPLICATE_DECLARATION_PATTERNS.get(relative_path, ()):
            _append_duplicate_declaration_issues(relative_path, text, label, pattern, issues)

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
        header_path = root / ABI_HEADER_PATH
        header_path.writeText = None
        header_path.write_text(
            _read(header_path)
            + "\ntypedef struct zigux_alias_probe {\n"
            + "    int value;\n"
            + "} zigux_boundary_header;\n",
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected_duplicate_typedef = "duplicate ABI typedef alias: zigux_boundary_header "
        if not any(issue.startswith(expected_duplicate_typedef) for issue in issues):
            print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=fail")
            print(f"expected duplicate typedef guard was not reported: {expected_duplicate_typedef}")
            return 1

        _populate_repo(root)
        binding_path = root / ABI_BINDING_PATH
        binding_path.write_text(
            _read(binding_path)
            + "\npub fn defaultHeader(flags: u16) BoundaryHeader {\n"
            + "    return .{ .size = flags, .abi_version = ABI_VERSION, .flags = flags };\n"
            + "}\n",
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected_duplicate_pub_fn = "duplicate ABI binding pub fn: defaultHeader "
        if not any(issue.startswith(expected_duplicate_pub_fn) for issue in issues):
            print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=fail")
            print(f"expected duplicate pub-fn guard was not reported: {expected_duplicate_pub_fn}")
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
        manifest["repo_reality_gaps"].remove(REQUIRED_REPO_REALITY_GAPS[3])
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_missing_gap = (
            "phase3_policy_starter_packet_manifest.json missing repo_reality_gaps entry: "
            "scripts/zigux/validate-phase3.py"
        )
        if expected_missing_gap not in issues:
            print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=fail")
            print(f"expected repo-reality-gap guard was not reported: {expected_missing_gap}")
            return 1

    print("PHASE3_POLICY_STARTER_PACKET_SELF_TEST=pass")
    print(f"PHASE3_POLICY_STARTER_PACKET_SELF_TEST_CASES={len(SELF_TEST_CASES) + 4}")
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

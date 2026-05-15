#!/usr/bin/env python3
"""Validate the shared Phase 3 ABI/bindings syntax review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile


SLICE_NOTE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
BINDINGS_SURVEY_PATH = Path("Documentation/zigux/phase3-abi-bindings-survey.md")
BINDINGS_GOVERNANCE_PATH = Path("Documentation/zigux/phase3-bindings-governance.md")
LINUX_ZIGUX_HEADER_GOVERNANCE_PATH = Path(
    "Documentation/zigux/phase3-linux-zigux-header-governance.md"
)
NEXT_STEP_NOTE_PATH = Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")
README_PATH = Path("scripts/zigux/README.md")
MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
ABI_HEADER_PATH = Path("include/zigux/abi.h")
ABI_BINDING_PATH = Path("zigux/bindings/abi.zig")
DEV_T_HEADER_PATH = Path("include/zigux/dev_t.h")
DEV_T_BINDING_PATH = Path("zigux/bindings/dev_t.zig")
NOTIFIER_BINDING_PATH = Path("zigux/bindings/notifier_abi.zig")

MANIFEST_SLICE_FILES = (
    Path("Documentation/zigux/phase3-bindings-governance.md"),
    Path("Documentation/zigux/phase3-abi-bindings-survey.md"),
    Path("Documentation/zigux/phase3-boundary-lane-sequencing.md"),
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("Documentation/zigux/phase3-kernel-export-shim-governance.md"),
    Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-linux-zigux-header-governance.md"),
    Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("include/linux/zigux.h"),
    ABI_HEADER_PATH,
    DEV_T_HEADER_PATH,
    ABI_BINDING_PATH,
    DEV_T_BINDING_PATH,
    NOTIFIER_BINDING_PATH,
    Path("zigux/helpers/layout_assert.zig"),
    Path("zigux/helpers/panic_policy.zig"),
    Path("zigux/helpers/allocator_policy.zig"),
    Path("zigux/helpers/atomic.zig"),
    Path("zigux/helpers/barrier.zig"),
    Path("zigux/helpers/mmio.zig"),
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/unsafe/narrow.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/tests/phase3_abi.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
    Path("zigux/tests/phase3_low_level_wrappers.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
    Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"),
    Path("zigux/tests/fixtures/phase3_abi/expected.json"),
    MANIFEST_PATH,
    Path("scripts/zigux/check-phase3-abi.py"),
    Path("scripts/zigux/check-phase3-abi-dump-gate.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"),
    Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),
    Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"),
    Path("scripts/zigux/survey-phase3-abi-constant-parity.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
)

REQUIRED_FILES = (
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("Documentation/zigux/phase3-abi-bindings-survey.md"),
    Path("Documentation/zigux/phase3-bindings-governance.md"),
    Path("Documentation/zigux/phase3-boundary-lane-sequencing.md"),
    Path("Documentation/zigux/phase3-kernel-export-shim-governance.md"),
    Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    LINUX_ZIGUX_HEADER_GOVERNANCE_PATH,
    Path("include/linux/zigux.h"),
    ABI_HEADER_PATH,
    DEV_T_HEADER_PATH,
    ABI_BINDING_PATH,
    DEV_T_BINDING_PATH,
    NOTIFIER_BINDING_PATH,
    Path("zigux/helpers/layout_assert.zig"),
    Path("zigux/helpers/panic_policy.zig"),
    Path("zigux/helpers/allocator_policy.zig"),
    Path("zigux/helpers/atomic.zig"),
    Path("zigux/helpers/barrier.zig"),
    Path("zigux/helpers/mmio.zig"),
    Path("zigux/kernel/export_shim.zig"),
    Path("zigux/unsafe/narrow.zig"),
    Path("zigux/uapi/version.zig"),
    Path("zigux/uapi/dev_t.zig"),
    Path("zigux/tests/phase3_abi.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
    Path("zigux/tests/phase3_low_level_wrappers.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
    Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"),
    Path("zigux/tests/fixtures/phase3_abi/expected.json"),
    MANIFEST_PATH,
    Path("scripts/zigux/check-phase3-abi.py"),
    Path("scripts/zigux/check-phase3-abi-dump-gate.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
    Path("scripts/zigux/survey-phase3-abi-constant-parity.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),
    Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
)

SLICE_NOTE_MARKERS = (
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-abi-bindings-survey.md",
    "Documentation/zigux/phase3-bindings-governance.md",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-kernel-export-shim-governance.md",
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-linux-zigux-header-governance.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/linux/zigux.h",
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py",
    "scripts/zigux/check-phase3-policy-byte-guards.py",
    "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py",
    "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py",
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "PHASE3_ABI_MANIFEST_FILE_COUNT=",
    "PHASE3_CURRENT_INTEROP_GAP=",
    "PHASE3_CURRENT_INTEROP_GAP_DETAIL=",
    "PHASE3_NEXT_SAFE_STEP=",
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "zig build phase3-dump --build-file zigux/tests/build.zig",
    "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
)

BINDINGS_SURVEY_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-bindings-governance.md",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/layout_assert.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "scripts/zigux/check-phase3-abi.py",
    "scripts/zigux/check-phase3-abi-dump-gate.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "PHASE3_CURRENT_INTEROP_GAP=",
    "PHASE3_NEXT_SAFE_STEP=",
)

BINDINGS_GOVERNANCE_MARKERS = (
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-abi-slice.md",
    "include/zigux/abi.h",
    "include/zigux/dev_t.h",
    "zigux/bindings/abi.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
)

NEXT_STEP_NOTE_MARKERS = (
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
    "scripts/zigux/survey-phase3-abi-constant-parity.py",
    "scripts/zigux/validate-phase3-abi-header-family-survey.py",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
)

README_MARKERS = (
    "validate-phase3-export-uapi-survey.py",
    "validate-phase3-low-level-wrapper-survey.py",
    "validate-phase3-validator-support-surface.py",
    "validate-phase3-abi-bindings-syntax.py",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/version.zig",
    "zigux/uapi/dev_t.zig",
    "python3 scripts/zigux/run-phase3-checks.py --slug abi",
    "make -C zigux phase3-validate",
    "make -C zigux phase3",
)

ABI_HEADER_MARKERS = (
    "#define ZIGUX_ABI_VERSION 1U",
    "#define ZIGUX_FACILITY_KERNEL 1U",
    "#define ZIGUX_STATUS_FLAG_ERROR 1U",
    "typedef struct zigux_boundary_header {",
    "struct zigux_export_status {",
    "struct zigux_interop_policy {",
    "struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {",
    "struct zigux_notifier_block {",
    "static inline int zigux_notifier_chain_has_nonincreasing_priority(",
    "static inline zigux_boundary_header zigux_default_header(uint16_t flags)",
)

ABI_BINDING_MARKERS = (
    "pub const ABI_VERSION: u16 = 1;",
    "pub const FACILITY_KERNEL: u16 = 1;",
    "pub const STATUS_FLAG_ERROR: u16 = 1;",
    "pub const BoundaryHeader = extern struct {",
    "pub const ExportStatus = extern struct {",
    "pub const InteropPolicy = extern struct {",
    "pub const Facility = enum(u16) {",
    "pub const PanicMode = enum(u8) {",
    "pub const AllocatorMode = enum(u8) {",
    "pub const UnsafeScope = enum(u8) {",
    "pub const NotifierBlock = extern struct {",
    "pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {",
    "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {",
    "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
    "pub fn defaultHeader(flags: u16) BoundaryHeader {",
    'test "abi binding keeps notifier block layout and chain helper explicit" {',
)

DEV_T_HEADER_MARKERS = (
    "#define ZIGUX_DEV_MINOR_BITS 20U",
    "#define ZIGUX_DEV_MINOR_MASK ((1U << ZIGUX_DEV_MINOR_BITS) - 1U)",
    "#define ZIGUX_DEV_MAJOR_MAX ((1U << (32U - ZIGUX_DEV_MINOR_BITS)) - 1U)",
    "static inline uint32_t zigux_mkdev(uint32_t major_id, uint32_t minor_id)",
    "static inline uint32_t zigux_major(uint32_t dev)",
    "static inline uint32_t zigux_minor(uint32_t dev)",
)

DEV_T_BINDING_MARKERS = (
    "pub const minor_bits: u5 = 20;",
    "pub const minor_mask: u32 = (@as(u32, 1) << minor_bits) - 1;",
    "pub const max_major: u32 = ~@as(u32, 0) >> minor_bits;",
    "pub const EncodeError = error{",
    "    MajorOutOfRange,",
    "    MinorOutOfRange,",
    "    RangeExhausted,",
    "pub fn majorValid(major_id: u32) bool {",
    "pub fn minorValid(minor_id: u32) bool {",
    "pub fn encode(major_id: u32, minor_id: u32) EncodeError!u32 {",
    "pub fn major(dev: u32) u32 {",
    "pub fn minor(dev: u32) u32 {",
    "pub fn rangeFits(first_minor: u32, count: u32) bool {",
    "pub fn lastInRange(major_id: u32, first_minor: u32, count: u32) EncodeError!u32 {",
)

NOTIFIER_BINDING_MARKERS = (
    'const std = @import("std");',
    "pub const NOTIFIER_DONE: u32 = 0;",
    "pub const NOTIFIER_OK: u32 = 1;",
    "pub const NOTIFIER_STOP: u32 = 2;",
    "pub const NotifierResult = enum(u32) {",
    "    done = NOTIFIER_DONE,",
    "    ok = NOTIFIER_OK,",
    "    stop = NOTIFIER_STOP,",
    "pub const NotifierBlock = extern struct {",
    "    notifier_call: usize,",
    "    next: usize,",
    "    priority: i32,",
    "pub const PriorityIncrease = struct {",
    "pub const ChainPriorityIncrease = struct {",
    "pub fn prioritiesNonincreasing(blocks: []const NotifierBlock) bool {",
    "    return firstPriorityIncrease(blocks) == null;",
    "pub fn firstPriorityIncrease(blocks: []const NotifierBlock) ?PriorityIncrease {",
    "    if (blocks.len < 2) return null;",
    "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
    "    return firstChainPriorityIncrease(head) == null;",
    "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?ChainPriorityIncrease {",
    'test "notifier priority helper reports the first chain priority increase" {',
    'test "notifier abi reports the first priority increase" {',
    'test "notifier abi keeps nonincreasing priority order reviewable" {',
    'test "notifier abi accepts empty and singleton priority samples" {',
    'test "notifier abi keeps result codes and block layout explicit" {',
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _check_markers(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    if not path.is_file():
        return [f"missing repo file: {path.as_posix()}"]

    text = _read(path)
    return [f"missing {label} marker: {marker}" for marker in markers if marker not in text]


def _load_manifest(path: Path) -> tuple[list[str], list[str]]:
    if not path.is_file():
        return [], [f"missing repo file: {path.as_posix()}"]

    try:
        data = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        return [], [f"invalid manifest json: {path.as_posix()}: {exc.msg}"]

    issues: list[str] = []
    files = data.get("files")
    if not isinstance(files, list) or not all(isinstance(entry, str) for entry in files):
        issues.append(f"invalid manifest files list: {path.as_posix()}")
        return [], issues

    file_count = data.get("file_count")
    if not isinstance(file_count, int):
        issues.append(f"invalid manifest file_count: {path.as_posix()}")
    elif file_count != len(files):
        issues.append(
            f"manifest file_count mismatch: {path.as_posix()} expected {len(files)} got {file_count}"
        )

    return files, issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in (SLICE_NOTE_PATH, BINDINGS_SURVEY_PATH, BINDINGS_GOVERNANCE_PATH, NEXT_STEP_NOTE_PATH, README_PATH):
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    if (repo_root / SLICE_NOTE_PATH).is_file():
        issues.extend(_check_markers(repo_root / SLICE_NOTE_PATH, SLICE_NOTE_MARKERS, "slice"))
    if (repo_root / NEXT_STEP_NOTE_PATH).is_file():
        issues.extend(_check_markers(repo_root / NEXT_STEP_NOTE_PATH, NEXT_STEP_NOTE_MARKERS, "next-step"))
    if (repo_root / README_PATH).is_file():
        issues.extend(_check_markers(repo_root / README_PATH, README_MARKERS, "scripts README"))

    manifest_files, manifest_issues = _load_manifest(repo_root / MANIFEST_PATH)
    issues.extend(manifest_issues)
    if manifest_files:
        manifest_set = set(manifest_files)
        for rel_path in MANIFEST_SLICE_FILES:
            rel_path_text = rel_path.as_posix()
            if rel_path_text not in manifest_set:
                issues.append(f"missing manifest file entry: {rel_path_text}")

    issues.extend(_check_markers(repo_root / BINDINGS_SURVEY_PATH, BINDINGS_SURVEY_MARKERS, "bindings survey"))
    issues.extend(
        _check_markers(
            repo_root / BINDINGS_GOVERNANCE_PATH,
            BINDINGS_GOVERNANCE_MARKERS,
            "bindings governance",
        )
    )
    issues.extend(_check_markers(repo_root / ABI_HEADER_PATH, ABI_HEADER_MARKERS, "abi header"))
    issues.extend(_check_markers(repo_root / ABI_BINDING_PATH, ABI_BINDING_MARKERS, "abi binding"))
    issues.extend(_check_markers(repo_root / DEV_T_HEADER_PATH, DEV_T_HEADER_MARKERS, "dev_t header"))
    issues.extend(_check_markers(repo_root / DEV_T_BINDING_PATH, DEV_T_BINDING_MARKERS, "dev_t binding"))
    issues.extend(_check_markers(repo_root / NOTIFIER_BINDING_PATH, NOTIFIER_BINDING_MARKERS, "notifier binding"))
    return issues


def _manifest_text(files: tuple[Path, ...] = MANIFEST_SLICE_FILES) -> str:
    manifest = {
        "phase": "Phase 3",
        "status": "active",
        "slice": "abi-substrate-skeleton",
        "file_count": len(files),
        "files": [path.as_posix() for path in files],
    }
    return json.dumps(manifest, indent=2) + "\n"


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path, "# stub\n")
    _write(root / ABI_HEADER_PATH, "\n".join(ABI_HEADER_MARKERS) + "\n")
    _write(root / ABI_BINDING_PATH, "\n".join(ABI_BINDING_MARKERS) + "\n")
    _write(root / DEV_T_HEADER_PATH, "\n".join(DEV_T_HEADER_MARKERS) + "\n")
    _write(root / DEV_T_BINDING_PATH, "\n".join(DEV_T_BINDING_MARKERS) + "\n")
    _write(root / NOTIFIER_BINDING_PATH, "\n".join(NOTIFIER_BINDING_MARKERS) + "\n")
    _write(root / MANIFEST_PATH, _manifest_text())
    _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
    _write(root / BINDINGS_SURVEY_PATH, "\n".join(BINDINGS_SURVEY_MARKERS) + "\n")
    _write(root / BINDINGS_GOVERNANCE_PATH, "\n".join(BINDINGS_GOVERNANCE_MARKERS) + "\n")
    _write(root / NEXT_STEP_NOTE_PATH, "\n".join(NEXT_STEP_NOTE_MARKERS) + "\n")
    _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")


def _require_issue(issues: list[str], expected: str, label: str) -> int:
    if expected not in issues:
        print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
        print(f"expected {label} was not reported")
        return 1
    return 0


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_bindings_syntax_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        missing_rel = REQUIRED_FILES[0]
        (root / missing_rel).unlink()
        issues = validate_repo(root)
        rc = _require_issue(issues, f"missing repo file: {missing_rel.as_posix()}", "missing repo file")
        if rc:
            return rc
        case_count += 1

        _populate_repo(root)
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("zigux/uapi/version.zig\n", "", 1))
        issues = validate_repo(root)
        rc = _require_issue(issues, "missing slice marker: zigux/uapi/version.zig", "missing slice marker")
        if rc:
            return rc
        case_count += 1

        _populate_repo(root)
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["files"].remove("zigux/tests/phase3_low_level_wrappers_build.zig")
        manifest["file_count"] -= 1
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        rc = _require_issue(
            issues,
            "missing manifest file entry: zigux/tests/phase3_low_level_wrappers_build.zig",
            "missing manifest file entry",
        )
        if rc:
            return rc
        case_count += 1

        _populate_repo(root)
        _write(
            root / BINDINGS_SURVEY_PATH,
            _read(root / BINDINGS_SURVEY_PATH).replace(
                "Documentation/zigux/phase3-bindings-governance.md\n", "", 1
            ),
        )
        issues = validate_repo(root)
        rc = _require_issue(
            issues,
            "missing bindings survey marker: Documentation/zigux/phase3-bindings-governance.md",
            "missing bindings survey marker",
        )
        if rc:
            return rc
        case_count += 1

        _populate_repo(root)
        _write(
            root / BINDINGS_GOVERNANCE_PATH,
            _read(root / BINDINGS_GOVERNANCE_PATH).replace(
                "zigux/tests/fixtures/phase3_abi_manifest.json\n", "", 1
            ),
        )
        issues = validate_repo(root)
        rc = _require_issue(
            issues,
            "missing bindings governance marker: zigux/tests/fixtures/phase3_abi_manifest.json",
            "missing bindings governance marker",
        )
        if rc:
            return rc
        case_count += 1

        _populate_repo(root)
        _write(
            root / ABI_HEADER_PATH,
            _read(root / ABI_HEADER_PATH).replace(
                "static inline int zigux_notifier_chain_has_nonincreasing_priority(\n", "", 1
            ),
        )
        issues = validate_repo(root)
        rc = _require_issue(
            issues,
            "missing abi header marker: static inline int zigux_notifier_chain_has_nonincreasing_priority(",
            "missing abi header marker",
        )
        if rc:
            return rc
        case_count += 1

        _populate_repo(root)
        _write(
            root / ABI_BINDING_PATH,
            _read(root / ABI_BINDING_PATH).replace(
                "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        rc = _require_issue(
            issues,
            "missing abi binding marker: pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
            "missing abi binding marker",
        )
        if rc:
            return rc
        case_count += 1

        _populate_repo(root)
        _write(
            root / DEV_T_HEADER_PATH,
            _read(root / DEV_T_HEADER_PATH).replace(
                "#define ZIGUX_DEV_MAJOR_MAX ((1U << (32U - ZIGUX_DEV_MINOR_BITS)) - 1U)\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        rc = _require_issue(
            issues,
            "missing dev_t header marker: #define ZIGUX_DEV_MAJOR_MAX ((1U << (32U - ZIGUX_DEV_MINOR_BITS)) - 1U)",
            "missing dev_t header marker",
        )
        if rc:
            return rc
        case_count += 1

        _populate_repo(root)
        _write(
            root / DEV_T_BINDING_PATH,
            _read(root / DEV_T_BINDING_PATH).replace(
                "pub fn rangeFits(first_minor: u32, count: u32) bool {\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        rc = _require_issue(
            issues,
            "missing dev_t binding marker: pub fn rangeFits(first_minor: u32, count: u32) bool {",
            "missing dev_t binding marker",
        )
        if rc:
            return rc
        case_count += 1

        _populate_repo(root)
        _write(
            root / NOTIFIER_BINDING_PATH,
            _read(root / NOTIFIER_BINDING_PATH).replace("    priority: i32,\n", "", 1),
        )
        issues = validate_repo(root)
        rc = _require_issue(
            issues,
            "missing notifier binding marker:     priority: i32,",
            "missing notifier binding marker",
        )
        if rc:
            return rc
        case_count += 1

    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass")
    print(f"PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 3 ABI and bindings syntax review packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 ABI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI_BINDINGS_SYNTAX=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / SLICE_NOTE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

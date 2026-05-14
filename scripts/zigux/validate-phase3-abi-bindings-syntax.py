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
    Path("include/zigux/abi.h"),
    Path("include/zigux/dev_t.h"),
    Path("zigux/bindings/abi.zig"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/bindings/notifier_abi.zig"),
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
    Path("include/zigux/abi.h"),
    Path("include/zigux/dev_t.h"),
    Path("zigux/bindings/abi.zig"),
    Path("zigux/bindings/dev_t.zig"),
    Path("zigux/bindings/notifier_abi.zig"),
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
    "pub const NotifierResult = enum(u32) {",
    "    done = 0,",
    "    ok = 1,",
    "    stop = 2,",
    "pub const NotifierBlock = extern struct {",
    "    notifier_call: usize,",
    "    next: usize,",
    "    priority: i32,",
    "pub fn prioritiesNonincreasing(blocks: []const NotifierBlock) bool {",
    "    if (blocks.len < 2) return true;",
    "        if (block.priority > previous_priority) return false;",
    'test "notifier abi keeps nonincreasing priority order reviewable" {',
    'test "notifier abi accepts empty and singleton priority samples" {',
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
    if not (repo_root / SLICE_NOTE_PATH).is_file():
        issues.append(f"missing repo file: {SLICE_NOTE_PATH.as_posix()}")
    if not (repo_root / BINDINGS_SURVEY_PATH).is_file():
        issues.append(f"missing repo file: {BINDINGS_SURVEY_PATH.as_posix()}")
    if not (repo_root / BINDINGS_GOVERNANCE_PATH).is_file():
        issues.append(f"missing repo file: {BINDINGS_GOVERNANCE_PATH.as_posix()}")
    if not (repo_root / NEXT_STEP_NOTE_PATH).is_file():
        issues.append(f"missing repo file: {NEXT_STEP_NOTE_PATH.as_posix()}")
    if not (repo_root / README_PATH).is_file():
        issues.append(f"missing repo file: {README_PATH.as_posix()}")
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")
    slice_note_path = repo_root / SLICE_NOTE_PATH
    if slice_note_path.is_file():
        slice_note_text = _read(slice_note_path)
        for marker in SLICE_NOTE_MARKERS:
            if marker not in slice_note_text:
                issues.append(f"missing slice marker: {marker}")
    next_step_note_path = repo_root / NEXT_STEP_NOTE_PATH
    if next_step_note_path.is_file():
        next_step_note_text = _read(next_step_note_path)
        for marker in NEXT_STEP_NOTE_MARKERS:
            if marker not in next_step_note_text:
                issues.append(f"missing next-step marker: {marker}")
    readme_path = repo_root / README_PATH
    if readme_path.is_file():
        readme_text = _read(readme_path)
        for marker in README_MARKERS:
            if marker not in readme_text:
                issues.append(f"missing scripts README marker: {marker}")
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
    issues.extend(
        _check_markers(repo_root / Path("include/zigux/dev_t.h"), DEV_T_HEADER_MARKERS, "dev_t header")
    )
    issues.extend(
        _check_markers(repo_root / Path("zigux/bindings/dev_t.zig"), DEV_T_BINDING_MARKERS, "dev_t binding")
    )
    issues.extend(
        _check_markers(
            repo_root / Path("zigux/bindings/notifier_abi.zig"),
            NOTIFIER_BINDING_MARKERS,
            "notifier binding",
        )
    )
    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
    _write(root / Path("include/zigux/dev_t.h"), "\n".join(DEV_T_HEADER_MARKERS) + "\n")
    _write(root / Path("zigux/bindings/dev_t.zig"), "\n".join(DEV_T_BINDING_MARKERS) + "\n")
    _write(
        root / Path("zigux/bindings/notifier_abi.zig"),
        "\n".join(NOTIFIER_BINDING_MARKERS) + "\n",
    )
    _write(root / MANIFEST_PATH, _manifest_text())
    _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
    _write(root / BINDINGS_SURVEY_PATH, "\n".join(BINDINGS_SURVEY_MARKERS) + "\n")
    _write(root / BINDINGS_GOVERNANCE_PATH, "\n".join(BINDINGS_GOVERNANCE_MARKERS) + "\n")
    _write(root / NEXT_STEP_NOTE_PATH, "\n".join(NEXT_STEP_NOTE_MARKERS) + "\n")
    _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")


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
        expected_missing = f"missing repo file: {missing_rel.as_posix()}"
        if expected_missing not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing repo file was not reported")
            return 1
        case_count += 1
        phase3_abi_rel = Path("zigux/tests/phase3_abi.zig")
        _write(root / missing_rel, "# restored\n")
        (root / phase3_abi_rel).unlink()
        issues = validate_repo(root)
        expected_phase3_abi_missing = f"missing repo file: {phase3_abi_rel.as_posix()}"
        if expected_phase3_abi_missing not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing phase3_abi replay file was not reported")
            return 1
        case_count += 1
        boundary_lane_note_rel = Path("Documentation/zigux/phase3-boundary-lane-sequencing.md")
        _write(root / phase3_abi_rel, "# restored\n")
        (root / boundary_lane_note_rel).unlink()
        issues = validate_repo(root)
        expected_boundary_lane_note_missing = (
            f"missing repo file: {boundary_lane_note_rel.as_posix()}"
        )
        if expected_boundary_lane_note_missing not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing boundary-lane note was not reported")
            return 1
        case_count += 1
        _write(root / boundary_lane_note_rel, "# restored\n")
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("zigux/uapi/version.zig\n", "", 1))
        issues = validate_repo(root)
        expected_slice_marker = "missing slice marker: zigux/uapi/version.zig"
        if expected_slice_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "zigux/tests/phase3_abi.zig\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_phase3_abi_slice_marker = "missing slice marker: zigux/tests/phase3_abi.zig"
        if expected_phase3_abi_slice_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing phase3_abi slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "Documentation/zigux/phase3-export-uapi-boundary-survey.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_export_uapi_marker = (
            "missing slice marker: Documentation/zigux/phase3-export-uapi-boundary-survey.md"
        )
        if expected_export_uapi_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing export-uapi slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_policy_marker = (
            "missing slice marker: Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
        )
        if expected_policy_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing policy-unsafe slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "Documentation/zigux/phase3-abi-bindings-survey.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_bindings_survey_marker = (
            "missing slice marker: Documentation/zigux/phase3-abi-bindings-survey.md"
        )
        if expected_bindings_survey_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing bindings-survey slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "Documentation/zigux/phase3-bindings-governance.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_bindings_governance_marker = (
            "missing slice marker: Documentation/zigux/phase3-bindings-governance.md"
        )
        if expected_bindings_governance_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing bindings-governance slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("zigux/uapi/dev_t.zig\n", "", 1))
        issues = validate_repo(root)
        expected_dev_t_marker = "missing slice marker: zigux/uapi/dev_t.zig"
        if expected_dev_t_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing dev_t slice marker was not reported")
            return 1
        case_count += 1
        _write(root / NEXT_STEP_NOTE_PATH, _read(root / NEXT_STEP_NOTE_PATH).replace(
            "scripts/zigux/validate-phase3-abi-bindings-syntax.py\n",
            "",
            1,
        ))
        issues = validate_repo(root)
        expected_next_step_marker = (
            "missing next-step marker: scripts/zigux/validate-phase3-abi-bindings-syntax.py"
        )
        if expected_next_step_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing next-step marker was not reported")
            return 1
        case_count += 1
        _write(root / NEXT_STEP_NOTE_PATH, "\n".join(NEXT_STEP_NOTE_MARKERS) + "\n")
        _write(root / SLICE_NOTE_PATH, _read(root / SLICE_NOTE_PATH).replace("PHASE3_CURRENT_INTEROP_GAP=\n", "", 1))
        issues = validate_repo(root)
        expected_gap_marker = "missing slice marker: PHASE3_CURRENT_INTEROP_GAP="
        if expected_gap_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing interop-gap marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "scripts/zigux/check-phase3-abi-dump-gate.py\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_dump_gate_marker = "missing slice marker: scripts/zigux/check-phase3-abi-dump-gate.py"
        if expected_dump_gate_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing dump-gate marker was not reported")
            return 1
        case_count += 1
        _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
        _write(root / README_PATH, _read(root / README_PATH).replace("zigux/uapi/dev_t.zig\n", "", 1))
        issues = validate_repo(root)
        expected_readme_marker = "missing scripts README marker: zigux/uapi/dev_t.zig"
        if expected_readme_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing README dev_t marker was not reported")
            return 1
        case_count += 1
        _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
        _write(
            root / BINDINGS_SURVEY_PATH,
            _read(root / BINDINGS_SURVEY_PATH).replace(
                "Documentation/zigux/phase3-bindings-governance.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_bindings_survey_local_marker = (
            "missing bindings survey marker: Documentation/zigux/phase3-bindings-governance.md"
        )
        if expected_bindings_survey_local_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing bindings-survey local marker was not reported")
            return 1
        case_count += 1
        _write(root / BINDINGS_SURVEY_PATH, "\n".join(BINDINGS_SURVEY_MARKERS) + "\n")
        _write(
            root / BINDINGS_GOVERNANCE_PATH,
            _read(root / BINDINGS_GOVERNANCE_PATH).replace(
                "zigux/tests/fixtures/phase3_abi_manifest.json\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_bindings_governance_local_marker = (
            "missing bindings governance marker: zigux/tests/fixtures/phase3_abi_manifest.json"
        )
        if expected_bindings_governance_local_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing bindings-governance local marker was not reported")
            return 1
        case_count += 1
        _write(root / BINDINGS_GOVERNANCE_PATH, "\n".join(BINDINGS_GOVERNANCE_MARKERS) + "\n")
        _write(
            root / BINDINGS_SURVEY_PATH,
            _read(root / BINDINGS_SURVEY_PATH).replace(
                "zigux/tests/phase3_low_level_wrappers_build.zig\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_bindings_wrapper_marker = (
            "missing bindings survey marker: zigux/tests/phase3_low_level_wrappers_build.zig"
        )
        if expected_bindings_wrapper_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing low-level-wrapper build marker was not reported")
            return 1
        case_count += 1
        _write(root / BINDINGS_SURVEY_PATH, "\n".join(BINDINGS_SURVEY_MARKERS) + "\n")
        manifest = json.loads(_read(root / MANIFEST_PATH))
        manifest["files"].remove("zigux/tests/phase3_low_level_wrappers_build.zig")
        manifest["file_count"] -= 1
        _write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_manifest_marker = (
            "missing manifest file entry: zigux/tests/phase3_low_level_wrappers_build.zig"
        )
        if expected_manifest_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing manifest file entry was not reported")
            return 1
        case_count += 1
        _write(root / MANIFEST_PATH, _manifest_text())
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "Documentation/zigux/phase3-validator-support-surface.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_validator_support_marker = (
            "missing slice marker: Documentation/zigux/phase3-validator-support-surface.md"
        )
        if expected_validator_support_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing validator-support slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_low_level_selftest_marker = (
            "missing slice marker: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"
        )
        if expected_low_level_selftest_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing low-level self-test slice marker was not reported")
            return 1
        case_count += 1
        _write(root / SLICE_NOTE_PATH, "\n".join(SLICE_NOTE_MARKERS) + "\n")
        _write(
            root / README_PATH,
            _read(root / README_PATH).replace(
                "Documentation/zigux/phase3-validator-support-surface.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_validator_support_readme_marker = (
            "missing scripts README marker: Documentation/zigux/phase3-validator-support-surface.md"
        )
        if expected_validator_support_readme_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected validator-support README marker was not reported")
            return 1
        case_count += 1
        _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
        _write(
            root / README_PATH,
            _read(root / README_PATH).replace(
                "validate-phase3-low-level-wrapper-survey.py\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_low_level_readme_marker = (
            "missing scripts README marker: validate-phase3-low-level-wrapper-survey.py"
        )
        if expected_low_level_readme_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected low-level README marker was not reported")
            return 1
        case_count += 1
        _populate_repo(root)
        _write(
            root / SLICE_NOTE_PATH,
            _read(root / SLICE_NOTE_PATH).replace(
                "Documentation/zigux/phase3-linux-zigux-header-governance.md\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_linux_header_governance_marker = (
            "missing slice marker: Documentation/zigux/phase3-linux-zigux-header-governance.md"
        )
        if expected_linux_header_governance_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing linux-zigux-header governance slice marker was not reported")
            return 1
        case_count += 1
        _populate_repo(root)
        missing_header_governance_note = LINUX_ZIGUX_HEADER_GOVERNANCE_PATH
        (root / missing_header_governance_note).unlink()
        issues = validate_repo(root)
        expected_missing_header_governance_note = (
            f"missing repo file: {missing_header_governance_note.as_posix()}"
        )
        if expected_missing_header_governance_note not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing linux-zigux-header governance note was not reported")
            return 1
        case_count += 1
        _populate_repo(root)
        missing_header_governance_validator = Path(
            "scripts/zigux/validate-phase3-linux-zigux-header-governance.py"
        )
        (root / missing_header_governance_validator).unlink()
        issues = validate_repo(root)
        expected_missing_header_governance_validator = (
            f"missing repo file: {missing_header_governance_validator.as_posix()}"
        )
        if expected_missing_header_governance_validator not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing linux-zigux-header governance validator was not reported")
            return 1
        case_count += 1
        _populate_repo(root)
        _write(
            root / Path("zigux/bindings/dev_t.zig"),
            _read(root / Path("zigux/bindings/dev_t.zig")).replace(
                "pub fn rangeFits(first_minor: u32, count: u32) bool {\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_dev_t_binding_marker = (
            "missing dev_t binding marker: pub fn rangeFits(first_minor: u32, count: u32) bool {"
        )
        if expected_dev_t_binding_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing dev_t binding marker was not reported")
            return 1
        case_count += 1
        _populate_repo(root)
        _write(
            root / Path("zigux/bindings/notifier_abi.zig"),
            _read(root / Path("zigux/bindings/notifier_abi.zig")).replace(
                "    priority: i32,\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_notifier_binding_marker = "missing notifier binding marker:     priority: i32,"
        if expected_notifier_binding_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing notifier binding marker was not reported")
            return 1
        case_count += 1
        _populate_repo(root)
        _write(
            root / Path("zigux/bindings/notifier_abi.zig"),
            _read(root / Path("zigux/bindings/notifier_abi.zig")).replace(
                "pub fn prioritiesNonincreasing(blocks: []const NotifierBlock) bool {\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_notifier_helper_marker = (
            "missing notifier binding marker: pub fn prioritiesNonincreasing(blocks: []const NotifierBlock) bool {"
        )
        if expected_notifier_helper_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing notifier helper marker was not reported")
            return 1
        case_count += 1
        _populate_repo(root)
        _write(
            root / Path("zigux/bindings/notifier_abi.zig"),
            _read(root / Path("zigux/bindings/notifier_abi.zig")).replace(
                'test "notifier abi keeps nonincreasing priority order reviewable" {\n',
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_notifier_test_marker = (
            'missing notifier binding marker: test "notifier abi keeps nonincreasing priority order reviewable" {'
        )
        if expected_notifier_test_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing notifier test marker was not reported")
            return 1
        case_count += 1
        _populate_repo(root)
        _write(
            root / Path("include/zigux/dev_t.h"),
            _read(root / Path("include/zigux/dev_t.h")).replace(
                "#define ZIGUX_DEV_MAJOR_MAX ((1U << (32U - ZIGUX_DEV_MINOR_BITS)) - 1U)\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_dev_t_header_marker = (
            "missing dev_t header marker: #define ZIGUX_DEV_MAJOR_MAX ((1U << (32U - ZIGUX_DEV_MINOR_BITS)) - 1U)"
        )
        if expected_dev_t_header_marker not in issues:
            print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=fail")
            print("expected missing dev_t header marker was not reported")
            return 1
        case_count += 1
    print("PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST=pass")
    print(f"PHASE3_ABI_BINDINGS_SYNTAX_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the shared Phase 3 ABI and bindings syntax review packet.")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root that contains the shared Phase 3 ABI packet")
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

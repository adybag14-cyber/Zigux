#!/usr/bin/env python3
"""Fail-close the focused Phase 3 ABI replay route."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile


ABI_SLICE_NOTE_PATH = Path("Documentation/zigux/phase3-abi-slice.md")
ABI_MANIFEST_PATH = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
REQUIRED_FILES = (
    ABI_SLICE_NOTE_PATH,
    Path("Documentation/zigux/phase3-abi-bindings-survey.md"),
    Path("Documentation/zigux/phase3-bindings-governance.md"),
    Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("Documentation/zigux/phase3-abi-header-family-survey.md"),
    Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md"),
    Path("Documentation/zigux/phase3-kernel-export-shim-governance.md"),
    Path("Documentation/zigux/phase3-linux-zigux-header-governance.md"),
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
    Path("zigux/tests/phase3_low_level_wrappers.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
    Path("zigux/tests/phase3_abi_dump.zig"),
    Path("zigux/tests/fixtures/phase3_abi/expected.json"),
    Path("zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c"),
    ABI_MANIFEST_PATH,
    Path("scripts/zigux/validate-phase3.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    Path("scripts/zigux/validate-phase3-policy-unsafe-survey.py"),
    Path("scripts/zigux/check-phase3-policy-byte-guards.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"),
    Path("scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"),
    Path("scripts/zigux/validate-phase3-export-uapi-survey.py"),
    Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py"),
    Path("scripts/zigux/validate-phase3-abi-header-family-survey.py"),
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
    Path("scripts/zigux/validate-phase3-abi-bindings-syntax.py"),
    Path("scripts/zigux/survey-phase3-abi-constant-parity.py"),
    Path("scripts/zigux/check-phase3-abi-dump-gate.py"),
    Path("scripts/zigux/phase3_catalog.py"),
    Path("scripts/zigux/phase3_check_lib.py"),
    Path("scripts/zigux/generate-phase3-check-wrappers.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
)
REQUIRED_MANIFEST_ENTRIES = (
    ABI_SLICE_NOTE_PATH,
    Path("Documentation/zigux/phase3-abi-bindings-survey.md"),
    Path("Documentation/zigux/phase3-bindings-governance.md"),
    Path("Documentation/zigux/phase3-boundary-lane-sequencing.md"),
    Path("Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"),
    Path("Documentation/zigux/phase3-export-uapi-boundary-survey.md"),
    Path("Documentation/zigux/phase3-kernel-export-shim-governance.md"),
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
    Path("zigux/tests/phase3_abi_dump.zig"),
    Path("zigux/tests/phase3_abi.zig"),
    Path("zigux/tests/phase3_low_level_wrappers.zig"),
    Path("zigux/tests/phase3_low_level_wrappers_build.zig"),
    Path("scripts/zigux/check-phase3-abi.py"),
    Path("scripts/zigux/phase3_catalog.py"),
    Path("scripts/zigux/phase3_check_lib.py"),
    Path("scripts/zigux/generate-phase3-check-wrappers.py"),
    Path("scripts/zigux/run-phase3-checks.py"),
)

# The export/UAPI lane explicitly keeps these dedicated replay files out of the
# current shared ABI packet until they land with the rest of that packet.
OPTIONAL_EXPORT_UAPI_REPLAY_FILES = (
    Path("zigux/tests/phase3_export_uapi.zig"),
    Path("zigux/tests/phase3_export_uapi_layout.zig"),
)

ABI_SLICE_CURRENT_GAP_MARKERS = {
    "Documentation/zigux/phase3-bindings-governance.md": 1,
    "Documentation/zigux/phase3-boundary-lane-sequencing.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "Documentation/zigux/phase3-validator-support-surface.md": 1,
    "direct `phase3_abi` replay": 1,
    "zigux/tests/phase3_export_uapi_layout_build.zig": 1,
    "zigux/tests/phase3_export_uapi_layout.zig": 1,
    "scripts/zigux/validate-phase3-export-uapi-survey.py": 1,
    "focused `phase3_export_uapi_layout` proof aligned": 1,
}

MAKEFILE_PATH = Path("zigux/Makefile")
RUNNER_PATH = Path("scripts/zigux/run-phase3-checks.py")
CHECK_LIB_PATH = Path("scripts/zigux/phase3_check_lib.py")
MAKE_MARKERS = (
    "phase3-abi:",
    "$(ZIG) build phase3-test --build-file zigux/tests/build.zig",
    "phase3-low-level-wrappers-test:",
    "$(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
)
RUNNER_MARKERS = (
    "from phase3_check_lib import run_phase3_slice_entry",
    "return run_phase3_slice_entry(entry, root=root)",
)
CHECK_LIB_MARKERS = (
    'if slug == "abi":',
    '(sys.executable, "scripts/zigux/check-phase3-abi.py"),',
    '(sys.executable, "scripts/zigux/check-phase3-policy-byte-guards.py"),',
    '(sys.executable, "scripts/zigux/check-phase3-policy-unsafe-focused-replay.py"),',
    '(sys.executable, "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"),',
    '("zig", "build", "phase3-test", "--build-file", "zigux/tests/build.zig"),',
    '("zig", "build", "phase3-dump", "--build-file", "zigux/tests/build.zig"),',
    "def run_phase3_slice_entry(",
)
HEADER_DEFINE_RE = re.compile(r"^\s*#define\s+([A-Z0-9_]+)\b")
HEADER_STRUCT_RE = re.compile(r"^\s*struct\s+([A-Za-z_][A-Za-z0-9_]*)\b")
HEADER_TYPEDEF_ALIAS_RE = re.compile(r"^\s*}\s*([A-Za-z_][A-Za-z0-9_]*)\s*;")
ZIG_CONST_RE = re.compile(r"^\s*pub const\s+([A-Za-z_][A-Za-z0-9_]*)\s*[:=]")
ZIG_EXTERN_STRUCT_RE = re.compile(
    r"^\s*pub const\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*extern struct\b"
)
SOURCE_MARKERS = {
    Path("include/linux/zigux.h"): (
        "zigux_boundary_header_make(",
        "zigux_boundary_header_make_compatible(",
        "zigux_boundary_header_is_current_abi_version(",
        "zigux_boundary_header_is_compatible_size(",
        "zigux_boundary_header_is_canonical_size(",
    ),
    Path("zigux/kernel/export_shim.zig"): (
        "pub fn boundaryHeader(",
        "pub fn compatibleHeader(",
        "pub fn headerCompatibility(",
        "pub fn acceptHeader(",
        "pub fn isCompatibleHeader(",
        "pub fn isCanonicalHeader(",
        "pub fn canonicalizeHeader(",
        "pub fn extendsBoundary(",
        "pub fn requestedExtraBytes(",
        "pub fn encodeDeviceNumber(",
        "pub fn lastDeviceNumberInRange(",
    ),
    Path("zigux/uapi/version.zig"): (
        "pub const AcceptedHeader = struct {",
        "pub const HeaderEvaluation = struct {",
        "pub fn boundaryHeader(",
        "pub fn compatibleHeader(",
        "pub fn compatibility(",
        "pub fn acceptHeader(",
        "pub fn evaluateHeader(",
        "pub fn canonicalizeHeader(",
    ),
    Path("zigux/uapi/dev_t.zig"): (
        "pub fn encode(",
        "pub fn lastInRange(",
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _record_duplicate(
    seen: dict[str, int], issues: list[str], label: str, name: str, lineno: int
) -> None:
    previous = seen.get(name)
    if previous is None:
        seen[name] = lineno
        return
    issues.append(
        f"duplicate {label}: {name} (first line {previous}, duplicate line {lineno})"
    )


def _validate_duplicate_declarations(
    text: str, matchers: tuple[tuple[str, re.Pattern[str]], ...]
) -> list[str]:
    issues: list[str] = []
    for label, pattern in matchers:
        seen: dict[str, int] = {}
        for lineno, line in enumerate(text.splitlines(), start=1):
            match = pattern.match(line)
            if match is None:
                continue
            _record_duplicate(seen, issues, label, match.group(1), lineno)
    return issues


def extract_section(text: str, heading: str, next_heading: str | None) -> str | None:
    if heading not in text:
        return None
    section = text.split(heading, 1)[1]
    if next_heading is not None and next_heading in section:
        section = section.split(next_heading, 1)[0]
    elif next_heading is None and "\n## " in section:
        section = section.split("\n## ", 1)[0]
    return section


def check_marker_counts(
    section: str | None,
    marker_counts: dict[str, int],
    label: str,
    missing_message: str,
) -> list[str]:
    if section is None:
        return [missing_message]
    issues: list[str] = []
    for marker, expected_count in marker_counts.items():
        actual_count = section.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"{label} marker count drift: {marker} "
                f"(expected {expected_count}, found {actual_count})"
            )
    return issues


def validate_manifest_entries(repo_root: Path) -> list[str]:
    manifest_path = repo_root / ABI_MANIFEST_PATH
    if not manifest_path.is_file():
        return []

    try:
        manifest = json.loads(_read(manifest_path))
    except json.JSONDecodeError as exc:
        return [f"invalid phase3 ABI manifest JSON: {exc.msg}"]

    files = manifest.get("files")
    if not isinstance(files, list):
        return ["invalid phase3 ABI manifest files list"]

    issues: list[str] = []
    file_entries: set[str] = set()
    for entry in files:
        if not isinstance(entry, str):
            issues.append(f"invalid phase3 ABI manifest file entry: {entry!r}")
            continue
        file_entries.add(entry)

    for rel_path in REQUIRED_MANIFEST_ENTRIES:
        if rel_path.as_posix() not in file_entries:
            issues.append(f"missing phase3 ABI manifest entry: {rel_path.as_posix()}")

    return issues


def validate_source_markers(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path, markers in SOURCE_MARKERS.items():
        source_path = repo_root / rel_path
        if not source_path.is_file():
            continue
        source_text = _read(source_path)
        for marker in markers:
            if marker not in source_text:
                issues.append(
                    f"missing source marker: {rel_path.as_posix()} :: {marker}"
                )
    return issues


def validate_abi_surface_sanity(repo_root: Path) -> list[str]:
    issues: list[str] = []

    header_path = repo_root / Path("include/zigux/abi.h")
    if header_path.is_file():
        issues.extend(
            _validate_duplicate_declarations(
                _read(header_path),
                (
                    ("ABI header #define", HEADER_DEFINE_RE),
                    ("ABI header struct", HEADER_STRUCT_RE),
                    ("ABI header typedef alias", HEADER_TYPEDEF_ALIAS_RE),
                ),
            )
        )

    bindings_path = repo_root / Path("zigux/bindings/abi.zig")
    if bindings_path.is_file():
        issues.extend(
            _validate_duplicate_declarations(
                _read(bindings_path),
                (
                    ("ABI binding const", ZIG_CONST_RE),
                    ("ABI binding extern struct", ZIG_EXTERN_STRUCT_RE),
                ),
            )
        )

    return issues


def validate_abi_slice_note(repo_root: Path) -> list[str]:
    note_path = repo_root / ABI_SLICE_NOTE_PATH
    if not note_path.is_file():
        return []
    note_text = _read(note_path)
    return check_marker_counts(
        extract_section(note_text, "## Current Gap", "## Scope"),
        ABI_SLICE_CURRENT_GAP_MARKERS,
        "Phase 3 ABI slice current gap",
        "missing ABI slice section: ## Current Gap",
    )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    makefile_path = repo_root / MAKEFILE_PATH
    if not makefile_path.is_file():
        issues.append(f"missing repo file: {MAKEFILE_PATH.as_posix()}")
    else:
        makefile_text = _read(makefile_path)
        for marker in MAKE_MARKERS:
            if marker not in makefile_text:
                issues.append(f"missing make marker: {marker}")

    runner_path = repo_root / RUNNER_PATH
    if runner_path.is_file():
        runner_text = _read(runner_path)
        for marker in RUNNER_MARKERS:
            if marker not in runner_text:
                issues.append(f"missing runner marker: {marker}")

    check_lib_path = repo_root / CHECK_LIB_PATH
    if check_lib_path.is_file():
        check_lib_text = _read(check_lib_path)
        for marker in CHECK_LIB_MARKERS:
            if marker not in check_lib_text:
                issues.append(f"missing shared helper marker: {marker}")

    issues.extend(validate_manifest_entries(repo_root))
    issues.extend(validate_source_markers(repo_root))
    issues.extend(validate_abi_surface_sanity(repo_root))
    issues.extend(validate_abi_slice_note(repo_root))
    return issues


def _write(path: Path, text: str = "# stub\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _manifest_payload(files: list[Path] | tuple[Path, ...]) -> str:
    payload = {
        "phase": "Phase 3",
        "status": "active",
        "slice": "abi-substrate-skeleton",
        "file_count": len(files),
        "files": [path.as_posix() for path in files],
    }
    return json.dumps(payload, indent=2) + "\n"


def _source_marker_stub(rel_path: Path) -> str:
    return "\n".join(SOURCE_MARKERS[rel_path]) + "\n"


def _abi_slice_note_stub() -> str:
    current_gap_lines = "\n".join(f"- `{marker}`" for marker in ABI_SLICE_CURRENT_GAP_MARKERS)
    return (
        "# Phase 3 ABI Slice\n\n"
        "## Packet Markers\n\n"
        "- `Documentation/zigux/phase3-abi-bindings-survey.md`\n"
        "- `Documentation/zigux/phase3-bindings-governance.md`\n"
        "- `Documentation/zigux/phase3-boundary-lane-sequencing.md`\n"
        "- `Documentation/zigux/phase3-validator-support-surface.md`\n"
        "\n"
        "## Current Gap\n\n"
        f"{current_gap_lines}\n\n"
        "## Scope\n\n"
        "- stub\n"
    )


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path)
    _write(root / ABI_MANIFEST_PATH, _manifest_payload(REQUIRED_MANIFEST_ENTRIES))
    _write(root / MAKEFILE_PATH, "\n".join(MAKE_MARKERS) + "\n")
    _write(root / RUNNER_PATH, "\n".join(RUNNER_MARKERS) + "\n")
    _write(root / CHECK_LIB_PATH, "\n".join(CHECK_LIB_MARKERS) + "\n")
    _write(root / ABI_SLICE_NOTE_PATH, _abi_slice_note_stub())
    for rel_path in SOURCE_MARKERS:
        _write(root / rel_path, _source_marker_stub(rel_path))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_abi_gate_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        for rel_path in OPTIONAL_EXPORT_UAPI_REPLAY_FILES:
            _write(root / rel_path)
            (root / rel_path).unlink()
        issues = validate_repo(root)
        if issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected ABI gate to keep export/UAPI-only replay files optional")
            print("\n".join(issues))
            return 1
        case_count += 1

        for manifest_entry_rel in REQUIRED_MANIFEST_ENTRIES:
            _write(
                root / ABI_MANIFEST_PATH,
                _manifest_payload(
                    [
                        rel_path
                        for rel_path in REQUIRED_MANIFEST_ENTRIES
                        if rel_path != manifest_entry_rel
                    ]
                ),
            )
            issues = validate_repo(root)
            expected_manifest_entry_missing = (
                f"missing phase3 ABI manifest entry: {manifest_entry_rel.as_posix()}"
            )
            if expected_manifest_entry_missing not in issues:
                print("PHASE3_ABI_SELF_TEST=fail")
                print("expected missing phase3 ABI manifest entry was not reported")
                return 1
            case_count += 1
            _write(root / ABI_MANIFEST_PATH, _manifest_payload(REQUIRED_MANIFEST_ENTRIES))

        low_level_wrapper_test_rel = Path("zigux/tests/phase3_low_level_wrappers.zig")
        (root / low_level_wrapper_test_rel).unlink()
        issues = validate_repo(root)
        expected_low_level_wrapper_test_missing = (
            f"missing repo file: {low_level_wrapper_test_rel.as_posix()}"
        )
        if expected_low_level_wrapper_test_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing low-level-wrapper test file was not reported")
            return 1
        case_count += 1
        _write(root / low_level_wrapper_test_rel)

        low_level_build_rel = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
        (root / low_level_build_rel).unlink()
        issues = validate_repo(root)
        expected_low_level_build_missing = (
            f"missing repo file: {low_level_build_rel.as_posix()}"
        )
        if expected_low_level_build_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing low-level-wrapper build file was not reported")
            return 1
        case_count += 1
        _write(root / low_level_build_rel)

        generated_wrapper_rel = Path("scripts/zigux/generate-phase3-check-wrappers.py")
        (root / generated_wrapper_rel).unlink()
        issues = validate_repo(root)
        expected_generated_wrapper_missing = (
            f"missing repo file: {generated_wrapper_rel.as_posix()}"
        )
        if expected_generated_wrapper_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing generated wrapper checker was not reported")
            return 1
        case_count += 1
        _write(root / generated_wrapper_rel)

        phase3_catalog_rel = Path("scripts/zigux/phase3_catalog.py")
        (root / phase3_catalog_rel).unlink()
        issues = validate_repo(root)
        expected_phase3_catalog_missing = (
            f"missing repo file: {phase3_catalog_rel.as_posix()}"
        )
        if expected_phase3_catalog_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing phase3 catalog helper was not reported")
            return 1
        case_count += 1
        _write(root / phase3_catalog_rel)

        policy_unsafe_survey_rel = Path(
            "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
        )
        (root / policy_unsafe_survey_rel).unlink()
        issues = validate_repo(root)
        expected_policy_unsafe_survey_missing = (
            f"missing repo file: {policy_unsafe_survey_rel.as_posix()}"
        )
        if expected_policy_unsafe_survey_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing policy-and-unsafe survey note was not reported")
            return 1
        case_count += 1
        _write(root / policy_unsafe_survey_rel)

        low_level_wrapper_survey_rel = Path(
            "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"
        )
        (root / low_level_wrapper_survey_rel).unlink()
        issues = validate_repo(root)
        expected_low_level_wrapper_survey_missing = (
            f"missing repo file: {low_level_wrapper_survey_rel.as_posix()}"
        )
        if expected_low_level_wrapper_survey_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing low-level-wrapper survey note was not reported")
            return 1
        case_count += 1
        _write(root / low_level_wrapper_survey_rel)

        export_uapi_survey_rel = Path(
            "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
        )
        (root / export_uapi_survey_rel).unlink()
        issues = validate_repo(root)
        expected_export_uapi_survey_missing = (
            f"missing repo file: {export_uapi_survey_rel.as_posix()}"
        )
        if expected_export_uapi_survey_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing export/UAPI survey note was not reported")
            return 1
        case_count += 1
        _write(root / export_uapi_survey_rel)

        abi_bindings_survey_rel = Path("Documentation/zigux/phase3-abi-bindings-survey.md")
        (root / abi_bindings_survey_rel).unlink()
        issues = validate_repo(root)
        expected_abi_bindings_survey_missing = (
            f"missing repo file: {abi_bindings_survey_rel.as_posix()}"
        )
        if expected_abi_bindings_survey_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing ABI-and-bindings survey note was not reported")
            return 1
        case_count += 1
        _write(root / abi_bindings_survey_rel)

        bindings_governance_rel = Path("Documentation/zigux/phase3-bindings-governance.md")
        (root / bindings_governance_rel).unlink()
        issues = validate_repo(root)
        expected_bindings_governance_missing = (
            f"missing repo file: {bindings_governance_rel.as_posix()}"
        )
        if expected_bindings_governance_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing bindings-governance note was not reported")
            return 1
        case_count += 1
        _write(root / bindings_governance_rel)

        kernel_export_note_rel = Path(
            "Documentation/zigux/phase3-kernel-export-shim-governance.md"
        )
        (root / kernel_export_note_rel).unlink()
        issues = validate_repo(root)
        expected_kernel_export_note_missing = (
            f"missing repo file: {kernel_export_note_rel.as_posix()}"
        )
        if expected_kernel_export_note_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing kernel-export governance note was not reported")
            return 1
        case_count += 1
        _write(root / kernel_export_note_rel)

        header_governance_rel = Path(
            "Documentation/zigux/phase3-linux-zigux-header-governance.md"
        )
        (root / header_governance_rel).unlink()
        issues = validate_repo(root)
        expected_header_governance_missing = (
            f"missing repo file: {header_governance_rel.as_posix()}"
        )
        if expected_header_governance_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing Linux-facing header governance note was not reported")
            return 1
        case_count += 1
        _write(root / header_governance_rel)

        validator_support_note_rel = Path(
            "Documentation/zigux/phase3-validator-support-surface.md"
        )
        (root / validator_support_note_rel).unlink()
        issues = validate_repo(root)
        expected_validator_support_note_missing = (
            f"missing repo file: {validator_support_note_rel.as_posix()}"
        )
        if expected_validator_support_note_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing validator-support note was not reported")
            return 1
        case_count += 1
        _write(root / validator_support_note_rel)

        validator_support_checker_rel = Path(
            "scripts/zigux/validate-phase3-validator-support-surface.py"
        )
        (root / validator_support_checker_rel).unlink()
        issues = validate_repo(root)
        expected_validator_support_checker_missing = (
            f"missing repo file: {validator_support_checker_rel.as_posix()}"
        )
        if expected_validator_support_checker_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing validator-support checker was not reported")
            return 1
        case_count += 1
        _write(root / validator_support_checker_rel)

        linux_zigux_header_governance_validator_rel = Path(
            "scripts/zigux/validate-phase3-linux-zigux-header-governance.py"
        )
        (root / linux_zigux_header_governance_validator_rel).unlink()
        issues = validate_repo(root)
        expected_linux_zigux_header_governance_validator_missing = (
            "missing repo file: "
            f"{linux_zigux_header_governance_validator_rel.as_posix()}"
        )
        if expected_linux_zigux_header_governance_validator_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing Linux zigux header-governance validator was not reported")
            return 1
        case_count += 1
        _write(root / linux_zigux_header_governance_validator_rel)

        layout_assert_rel = Path("zigux/helpers/layout_assert.zig")
        (root / layout_assert_rel).unlink()
        issues = validate_repo(root)
        expected_layout_assert_missing = f"missing repo file: {layout_assert_rel.as_posix()}"
        if expected_layout_assert_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing layout-assert helper was not reported")
            return 1
        case_count += 1
        _write(root / layout_assert_rel)

        panic_policy_rel = Path("zigux/helpers/panic_policy.zig")
        (root / panic_policy_rel).unlink()
        issues = validate_repo(root)
        expected_panic_policy_missing = f"missing repo file: {panic_policy_rel.as_posix()}"
        if expected_panic_policy_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing panic-policy helper was not reported")
            return 1
        case_count += 1
        _write(root / panic_policy_rel)

        allocator_policy_rel = Path("zigux/helpers/allocator_policy.zig")
        (root / allocator_policy_rel).unlink()
        issues = validate_repo(root)
        expected_allocator_policy_missing = (
            f"missing repo file: {allocator_policy_rel.as_posix()}"
        )
        if expected_allocator_policy_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing allocator-policy helper was not reported")
            return 1
        case_count += 1
        _write(root / allocator_policy_rel)

        atomic_rel = Path("zigux/helpers/atomic.zig")
        (root / atomic_rel).unlink()
        issues = validate_repo(root)
        expected_atomic_missing = f"missing repo file: {atomic_rel.as_posix()}"
        if expected_atomic_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing atomic helper was not reported")
            return 1
        case_count += 1
        _write(root / atomic_rel)

        barrier_rel = Path("zigux/helpers/barrier.zig")
        (root / barrier_rel).unlink()
        issues = validate_repo(root)
        expected_barrier_missing = f"missing repo file: {barrier_rel.as_posix()}"
        if expected_barrier_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing barrier helper was not reported")
            return 1
        case_count += 1
        _write(root / barrier_rel)

        mmio_rel = Path("zigux/helpers/mmio.zig")
        (root / mmio_rel).unlink()
        issues = validate_repo(root)
        expected_mmio_missing = f"missing repo file: {mmio_rel.as_posix()}"
        if expected_mmio_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing mmio helper was not reported")
            return 1
        case_count += 1
        _write(root / mmio_rel)

        narrow_unsafe_rel = Path("zigux/unsafe/narrow.zig")
        (root / narrow_unsafe_rel).unlink()
        issues = validate_repo(root)
        expected_narrow_unsafe_missing = (
            f"missing repo file: {narrow_unsafe_rel.as_posix()}"
        )
        if expected_narrow_unsafe_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing narrow-unsafe helper was not reported")
            return 1
        case_count += 1
        _write(root / narrow_unsafe_rel)

        mmio_consumer_rel = Path("scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py")
        (root / mmio_consumer_rel).unlink()
        issues = validate_repo(root)
        expected_mmio_consumer_missing = (
            f"missing repo file: {mmio_consumer_rel.as_posix()}"
        )
        if expected_mmio_consumer_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing policy/unsafe mmio-consumer checker was not reported")
            return 1
        case_count += 1
        _write(root / mmio_consumer_rel)

        linux_header_rel = Path("include/linux/zigux.h")
        _write(
            root / linux_header_rel,
            _read(root / linux_header_rel).replace(
                "zigux_boundary_header_is_compatible_size(\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_linux_header_marker_missing = (
            "missing source marker: include/linux/zigux.h :: "
            "zigux_boundary_header_is_compatible_size("
        )
        if expected_linux_header_marker_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing Linux-facing header marker was not reported")
            return 1
        case_count += 1
        _write(root / linux_header_rel, _source_marker_stub(linux_header_rel))

        export_shim_rel = Path("zigux/kernel/export_shim.zig")
        _write(
            root / export_shim_rel,
            _read(root / export_shim_rel).replace(
                "pub fn canonicalizeHeader(\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_export_shim_marker_missing = (
            "missing source marker: zigux/kernel/export_shim.zig :: "
            "pub fn canonicalizeHeader("
        )
        if expected_export_shim_marker_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing export_shim relay marker was not reported")
            return 1
        case_count += 1
        _write(root / export_shim_rel, _source_marker_stub(export_shim_rel))

        uapi_version_rel = Path("zigux/uapi/version.zig")
        _write(
            root / uapi_version_rel,
            _read(root / uapi_version_rel).replace(
                "pub fn evaluateHeader(\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_uapi_version_marker_missing = (
            "missing source marker: zigux/uapi/version.zig :: "
            "pub fn evaluateHeader("
        )
        if expected_uapi_version_marker_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing uapi version relay marker was not reported")
            return 1
        case_count += 1
        _write(root / uapi_version_rel, _source_marker_stub(uapi_version_rel))

        abi_slice_note_rel = ABI_SLICE_NOTE_PATH
        _write(
            root / abi_slice_note_rel,
            _read(root / abi_slice_note_rel).replace(
                "- `zigux/tests/phase3_export_uapi_layout_build.zig`\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_abi_slice_marker_missing = (
            "Phase 3 ABI slice current gap marker count drift: "
            "zigux/tests/phase3_export_uapi_layout_build.zig (expected 1, found 0)"
        )
        if expected_abi_slice_marker_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing ABI slice layout-build marker was not reported")
            return 1
        case_count += 1
        _write(root / abi_slice_note_rel, _abi_slice_note_stub())

        _write(
            root / abi_slice_note_rel,
            _read(root / abi_slice_note_rel).replace(
                "- `direct `phase3_abi` replay`\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_abi_slice_direct_replay_missing = (
            "Phase 3 ABI slice current gap marker count drift: "
            "direct `phase3_abi` replay (expected 1, found 0)"
        )
        if expected_abi_slice_direct_replay_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing ABI slice direct replay phrase was not reported")
            return 1
        case_count += 1
        _write(root / abi_slice_note_rel, _abi_slice_note_stub())

        _write(
            root / abi_slice_note_rel,
            _read(root / abi_slice_note_rel).replace(
                "- `focused `phase3_export_uapi_layout` proof aligned`\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_abi_slice_phrase_missing = (
            "Phase 3 ABI slice current gap marker count drift: "
            "focused `phase3_export_uapi_layout` proof aligned (expected 1, found 0)"
        )
        if expected_abi_slice_phrase_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing ABI slice focused-layout phrase was not reported")
            return 1
        case_count += 1
        _write(root / abi_slice_note_rel, _abi_slice_note_stub())

        missing_rel = REQUIRED_FILES[0]
        (root / missing_rel).unlink()
        issues = validate_repo(root)
        expected_missing = f"missing repo file: {missing_rel.as_posix()}"
        if expected_missing not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing repo file was not reported")
            return 1
        case_count += 1

        _write(root / missing_rel, _abi_slice_note_stub())
        _write(root / MAKEFILE_PATH, "phase3-abi:\n")
        issues = validate_repo(root)
        expected_make_marker = (
            "missing make marker: $(ZIG) build phase3-test --build-file zigux/tests/build.zig"
        )
        if expected_make_marker not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing make marker was not reported")
            return 1
        case_count += 1

        _write(root / MAKEFILE_PATH, "\n".join(MAKE_MARKERS) + "\n")
        _write(
            root / MAKEFILE_PATH,
            _read(root / MAKEFILE_PATH).replace(
                "$(ZIG) build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig\n",
                "",
                1,
            ),
        )
        issues = validate_repo(root)
        expected_low_level_make_marker = (
            "missing make marker: $(ZIG) build phase3-low-level-wrappers-test "
            "--build-file zigux/tests/phase3_low_level_wrappers_build.zig"
        )
        if expected_low_level_make_marker not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing low-level-wrapper make marker was not reported")
            return 1
        case_count += 1

        _write(root / MAKEFILE_PATH, "\n".join(MAKE_MARKERS) + "\n")
        _write(root / RUNNER_PATH, "from phase3_check_lib import run_phase3_slice_entry\n")
        issues = validate_repo(root)
        expected_runner_marker = (
            "missing runner marker: return run_phase3_slice_entry(entry, root=root)"
        )
        if expected_runner_marker not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing runner marker was not reported")
            return 1
        case_count += 1

        _write(root / RUNNER_PATH, "\n".join(RUNNER_MARKERS) + "\n")
        _write(root / CHECK_LIB_PATH, "def run_phase3_slice_entry(entry, root=root):\n    return 0\n")
        issues = validate_repo(root)
        expected_helper_marker = 'missing shared helper marker: if slug == "abi":'
        if expected_helper_marker not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing shared helper marker was not reported")
            return 1
        case_count += 1

        _write(root / CHECK_LIB_PATH, "\n".join(CHECK_LIB_MARKERS) + "\n")
        _write(
            root / Path("include/zigux/abi.h"),
            "#define ZIGUX_ABI_VERSION 1U\n"
            "struct zigux_layout {\n"
            "    int value;\n"
            "};\n"
            "#define ZIGUX_ABI_VERSION 2U\n"
            "struct zigux_layout {\n"
            "    int value2;\n"
            "};\n",
        )
        issues = validate_repo(root)
        expected_duplicate_define = (
            "duplicate ABI header #define: ZIGUX_ABI_VERSION "
            "(first line 1, duplicate line 5)"
        )
        if expected_duplicate_define not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected duplicate ABI header define was not reported")
            return 1
        expected_duplicate_struct = (
            "duplicate ABI header struct: zigux_layout (first line 2, duplicate line 6)"
        )
        if expected_duplicate_struct not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected duplicate ABI header struct was not reported")
            return 1
        case_count += 1
        _write(root / Path("include/zigux/abi.h"))

        _write(
            root / Path("include/zigux/abi.h"),
            "typedef struct zigux_layout {\n"
            "    int value;\n"
            "} zigux_layout;\n"
            "typedef struct zigux_layout_alias {\n"
            "    int value2;\n"
            "} zigux_layout;\n",
        )
        issues = validate_repo(root)
        expected_duplicate_typedef_alias = (
            "duplicate ABI header typedef alias: zigux_layout "
            "(first line 3, duplicate line 6)"
        )
        if expected_duplicate_typedef_alias not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected duplicate ABI header typedef alias was not reported")
            return 1
        case_count += 1
        _write(root / Path("include/zigux/abi.h"))

        _write(
            root / Path("zigux/bindings/abi.zig"),
            "pub const ABI_VERSION: u16 = 1;\n"
            "pub const BoundaryHeader = extern struct {};\n"
            "pub const ABI_VERSION: u16 = 2;\n"
            "pub const BoundaryHeader = extern struct {};\n",
        )
        issues = validate_repo(root)
        expected_duplicate_const = (
            "duplicate ABI binding const: ABI_VERSION (first line 1, duplicate line 3)"
        )
        if expected_duplicate_const not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected duplicate ABI binding const was not reported")
            return 1
        expected_duplicate_extern_struct = (
            "duplicate ABI binding extern struct: BoundaryHeader "
            "(first line 2, duplicate line 4)"
        )
        if expected_duplicate_extern_struct not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected duplicate ABI binding extern struct was not reported")
            return 1
        case_count += 1

        _write(root / CHECK_LIB_PATH, "\n".join(CHECK_LIB_MARKERS) + "\n")
        _write(
            root / CHECK_LIB_PATH,
            "\n".join(
                marker
                for marker in CHECK_LIB_MARKERS
                if marker
                != '(sys.executable, "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"),'
            )
            + "\n",
        )
        issues = validate_repo(root)
        expected_helper_marker = (
            "missing shared helper marker: "
            '(sys.executable, "scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py"),'
        )
        if expected_helper_marker not in issues:
            print("PHASE3_ABI_SELF_TEST=fail")
            print("expected missing mmio-consumer shared helper marker was not reported")
            return 1
        case_count += 1

    print("PHASE3_ABI_SELF_TEST=pass")
    print(f"PHASE3_ABI_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the focused Phase 3 ABI replay route against the live shared ABI packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 ABI packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_ABI=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / MAKEFILE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-close the shared Phase 3 selftest reminder surface."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


README_PATH = Path("Documentation/zigux/README.md")
NOTE_PATH = Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")
SURVEY_PATH = Path("Documentation/zigux/phase3-abi-header-family-survey.md")
VALIDATOR_SUPPORT_PATH = Path("Documentation/zigux/phase3-validator-support-surface.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
MAKEFILE_PATH = Path("zigux/Makefile")

README_MARKERS = ("validate_phase3_selftest.py",)
README_PHASE3_PREFIX = "Phase 3 notes - "
README_PHASE3_NEXT_PREFIX = "Phase 5 notes - "
README_PHASE3_MARKER_COUNTS = {
    "Documentation/zigux/phase3-abi-slice.md": 1,
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md": 1,
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md": 1,
    "Documentation/zigux/phase3-validator-support-surface.md": 1,
    "scripts/zigux/validate-phase3.py": 1,
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py": 1,
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py": 1,
    "scripts/zigux/check-phase3-readme-tooling-inventory.py": 1,
    "scripts/zigux/check-phase3-selftest-surface.py": 1,
    "scripts/zigux/phase3_catalog.py": 1,
    "scripts/zigux/validate_phase3_selftest.py": 1,
    "python3 scripts/zigux/run-phase3-checks.py --slug abi": 1,
    "zig build phase3-test --build-file zigux/tests/build.zig": 1,
    "make -C zigux phase3-validate": 1,
    "make -C zigux phase3-selftest": 1,
}

NOTE_POLICY_MARKERS = (
    "keeping `zigux/uapi/dev_t.zig` explicit beside the dedicated survey",
    "and next-step notes while leaving the narrower `zigux/uapi/version.zig`",
    "export/UAPI packet actually grows",
)
NOTE_NEXT_STEP_PREFIX = "## Next bounded step"
NOTE_NEXT_STEP_NEXT_PREFIX = "## Non-goals"

HEADER_FAMILY_SURVEY_CURRENT_PACKET_PREFIX = "## Current packet"
HEADER_FAMILY_SURVEY_CURRENT_PACKET_NEXT_PREFIX = "## Review boundary"
HEADER_FAMILY_SURVEY_CURRENT_PACKET_MARKER_COUNTS = {
    "include/zigux/dev_t.h": 1,
    "zigux/bindings/abi.zig": 1,
    "zigux/bindings/dev_t.zig": 1,
    "zigux/uapi/version.zig": 1,
    "zigux/uapi/dev_t.zig": 1,
    "zigux/tests/phase3_abi_dump.zig": 1,
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c": 1,
    "zigux/tests/fixtures/phase3_abi/expected.json": 1,
    "scripts/zigux/validate-phase3-export-uapi-survey.py": 1,
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py": 1,
    "scripts/zigux/survey-phase3-abi-constant-parity.py": 1,
}

HEADER_FAMILY_SURVEY_SHARED_REMINDER_MARKER_COUNTS = {
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md": 1,
    "Documentation/zigux/phase3-linux-zigux-header-governance.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "Documentation/zigux/README.md": 1,
    "Documentation/zigux/review-checklist.md": 1,
    "scripts/zigux/README.md": 1,
    "zigux/tests/README.md": 1,
    "zigux/uapi/dev_t.zig": 1,
    "zigux/bindings/dev_t.zig": 1,
    "zigux/bindings/abi.zig": 1,
    "zigux/tests/phase3_abi_dump.zig": 1,
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c": 1,
    "zigux/tests/fixtures/phase3_abi/expected.json": 1,
    "scripts/zigux/validate-phase3-export-uapi-survey.py": 1,
    "scripts/zigux/validate-phase3-abi-bindings-syntax.py": 1,
    "scripts/zigux/survey-phase3-abi-constant-parity.py": 1,
    "`include/zigux/dev_t.h` plus `zigux/uapi/version.zig` starter-companion detail": 1,
    "should stay anchored in this dedicated survey and the paired next-step note": 1,
}
HEADER_FAMILY_SURVEY_SHARED_REMINDER_PREFIX = "## Shared reminder"

VALIDATOR_SUPPORT_SHARED_REMINDER_PREFIX = "## Shared reminder"
VALIDATOR_SUPPORT_SHARED_REMINDER_MARKER_COUNTS = {
    "scripts/zigux/README.md": 1,
    "zigux/tests/README.md": 1,
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py": 2,
    "Documentation/zigux/phase3-kernel-export-shim-governance.md": 1,
    "include/zigux/dev_t.h": 2,
    "zigux/uapi/version.zig": 2,
    "zigux/uapi/dev_t.zig": 1,
    "zigux/bindings/abi.zig": 1,
    "zigux/kernel/export_shim.zig": 1,
    "keep the canonical `include/zigux/dev_t.h` plus `zigux/uapi/version.zig`": 1,
    "starter-companion split explicit here whenever this validator-support packet": 1,
    "names the dedicated header-family survey and next-step note": 1,
    "header-governance context through the paired survey and next-step notes": 1,
    "naming that validator directly": 1,
    "kernel-facing governance note is already a broad": 1,
}

REVIEW_CHECKLIST_PHASE3_PROMPT_PREFIX = (
    "  * if the change touches the shared Phase 3 ABI packet or a broad reminder surface, do "
)
REVIEW_CHECKLIST_PHASE3_PROMPT_NEXT_PREFIX = (
    "  * if the change touches the parked Phase 8 `help` packet, do "
)
REVIEW_CHECKLIST_PHASE3_PROMPT_MARKER_COUNTS = {
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/review-checklist.md": 1,
    "include/zigux/dev_t.h": 1,
    "zigux/uapi/version.zig": 1,
    "zigux/uapi/dev_t.zig": 1,
    "bounded header-family and starter-companion packet": 1,
}

TESTS_README_MARKERS = (
    "scripts/zigux/check-phase3-selftest-surface.py",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "make -C zigux phase3-selftest",
)
TESTS_README_MARKER_COUNTS = {
    "scripts/zigux/run-phase3-checks.py --self-test": 1,
    "scripts/zigux/phase3_catalog.py --audit-doc-sync": 1,
    "scripts/zigux/survey-phase3-abi-constant-parity.py": 1,
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "Documentation/zigux/phase3-validator-support-surface.md": 1,
    "scripts/zigux/validate-phase3-abi-header-family-survey.py": 1,
    "include/zigux/dev_t.h": 1,
    "zigux/uapi/version.zig": 1,
    "zigux/uapi/dev_t.zig": 1,
}
TESTS_README_REMINDER_ONLY_MARKER_COUNTS = {
    "scripts/zigux/phase3_catalog.py --self-test": 1,
    "scripts/zigux/phase3_check_lib.py --self-test": 1,
    "scripts/zigux/generate-phase3-check-wrappers.py --check": 1,
}
TESTS_README_PHASE3_REMINDER_MARKER_COUNTS = {
    **{marker: 1 for marker in TESTS_README_MARKERS},
    **TESTS_README_MARKER_COUNTS,
    **TESTS_README_REMINDER_ONLY_MARKER_COUNTS,
}
TESTS_README_PHASE3_REMINDER_PREFIX = (
    "  * keep the focused Phase 3 validator-support replay explicit in the tests root too:"
)
TESTS_README_PHASE3_REMINDER_NEXT_PREFIX = (
    "  * keep the shared Phase 4 rollback packet explicit in the tests root too:"
)

SCRIPTS_README_MARKERS = (
    "check-phase3-selftest-surface.py",
    "validate_phase3_selftest.py",
    "make -C zigux phase3-selftest",
)
SCRIPTS_README_PHASE3_MARKER_COUNTS = {
    "Documentation/zigux/phase3-validator-support-surface.md": 1,
    "zigux/kernel/export_shim.zig": 1,
    "zigux/uapi/dev_t.zig": 1,
}
SCRIPTS_README_PHASE3_PREFIX = "Phase 3 flow - "
SCRIPTS_README_PHASE3_NEXT_PREFIX = "Phase 4 flow - "
SCRIPTS_HEADER_FAMILY_REMINDER_PREFIX = "Phase 3 header-family reminder - "
SCRIPTS_HEADER_FAMILY_REMINDER_MARKER_COUNTS = {
    "validate-phase3-abi-header-family-survey.py": 1,
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/phase3-linux-zigux-header-governance.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "include/zigux/dev_t.h": 1,
    "zigux/uapi/version.zig": 1,
    "zigux/uapi/dev_t.zig": 1,
}

SELFTEST_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-selftest-surface.py")',
    'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
    'Path("scripts/zigux/validate-phase3-linux-zigux-header-governance.py")',
    "PHASE3_VALIDATE_SELFTEST=pass",
)
MAKEFILE_MARKERS = (
    "phase3-validate:",
    "$(PYTHON) scripts/zigux/check-phase3-selftest-surface.py --self-test",
    "$(PYTHON) scripts/zigux/check-phase3-selftest-surface.py",
    "$(PYTHON) scripts/zigux/validate_phase3_selftest.py",
    "phase3-selftest:",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _check_markers(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]
    return [f"missing {label} marker: {marker}" for marker in markers if marker not in text]


def _extract_section(text: str, start_prefix: str, next_prefix: str | None) -> str | None:
    if start_prefix not in text:
        return None
    section = text.split(start_prefix, 1)[1]
    if next_prefix is not None and next_prefix in section:
        section = section.split(next_prefix, 1)[0]
    elif next_prefix is None and "\n## " in section:
        section = section.split("\n## ", 1)[0]
    return section


def _check_section_marker_counts(
    path: Path,
    start_prefix: str,
    next_prefix: str | None,
    marker_counts: dict[str, int],
    label: str,
) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]

    section = _extract_section(text, start_prefix, next_prefix)
    if section is None:
        return [f"missing {label} section"]

    issues: list[str] = []
    for marker, expected_count in marker_counts.items():
        actual_count = section.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"{label} marker count drift: {marker} (expected {expected_count}, found {actual_count})"
            )
    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []

    issues.extend(_check_markers(repo_root / README_PATH, README_MARKERS, "docs README"))
    issues.extend(
        _check_section_marker_counts(
            repo_root / README_PATH,
            README_PHASE3_PREFIX,
            README_PHASE3_NEXT_PREFIX,
            README_PHASE3_MARKER_COUNTS,
            "docs README Phase 3 notes",
        )
    )
    issues.extend(
        _check_section_marker_counts(
            repo_root / NOTE_PATH,
            NOTE_NEXT_STEP_PREFIX,
            NOTE_NEXT_STEP_NEXT_PREFIX,
            {marker: 1 for marker in NOTE_POLICY_MARKERS},
            "abi.h next-step note",
        )
    )
    issues.extend(
        _check_section_marker_counts(
            repo_root / SURVEY_PATH,
            HEADER_FAMILY_SURVEY_CURRENT_PACKET_PREFIX,
            HEADER_FAMILY_SURVEY_CURRENT_PACKET_NEXT_PREFIX,
            HEADER_FAMILY_SURVEY_CURRENT_PACKET_MARKER_COUNTS,
            "header-family survey current packet",
        )
    )
    issues.extend(
        _check_section_marker_counts(
            repo_root / SURVEY_PATH,
            HEADER_FAMILY_SURVEY_SHARED_REMINDER_PREFIX,
            None,
            HEADER_FAMILY_SURVEY_SHARED_REMINDER_MARKER_COUNTS,
            "header-family survey shared reminder",
        )
    )
    issues.extend(
        _check_section_marker_counts(
            repo_root / VALIDATOR_SUPPORT_PATH,
            VALIDATOR_SUPPORT_SHARED_REMINDER_PREFIX,
            None,
            VALIDATOR_SUPPORT_SHARED_REMINDER_MARKER_COUNTS,
            "validator-support shared reminder",
        )
    )
    issues.extend(
        _check_section_marker_counts(
            repo_root / REVIEW_CHECKLIST_PATH,
            REVIEW_CHECKLIST_PHASE3_PROMPT_PREFIX,
            REVIEW_CHECKLIST_PHASE3_PROMPT_NEXT_PREFIX,
            REVIEW_CHECKLIST_PHASE3_PROMPT_MARKER_COUNTS,
            "review checklist Phase 3 prompt",
        )
    )

    issues.extend(_check_markers(repo_root / TESTS_README_PATH, TESTS_README_MARKERS, "tests README"))
    issues.extend(
        _check_section_marker_counts(
            repo_root / TESTS_README_PATH,
            TESTS_README_PHASE3_REMINDER_PREFIX,
            TESTS_README_PHASE3_REMINDER_NEXT_PREFIX,
            TESTS_README_PHASE3_REMINDER_MARKER_COUNTS,
            "tests README Phase 3 reminder",
        )
    )

    issues.extend(
        _check_markers(repo_root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS, "scripts README")
    )
    issues.extend(
        _check_section_marker_counts(
            repo_root / SCRIPTS_README_PATH,
            SCRIPTS_README_PHASE3_PREFIX,
            SCRIPTS_README_PHASE3_NEXT_PREFIX,
            SCRIPTS_README_PHASE3_MARKER_COUNTS,
            "scripts README Phase 3 flow",
        )
    )
    issues.extend(
        _check_section_marker_counts(
            repo_root / SCRIPTS_README_PATH,
            SCRIPTS_HEADER_FAMILY_REMINDER_PREFIX,
            None,
            SCRIPTS_HEADER_FAMILY_REMINDER_MARKER_COUNTS,
            "scripts README header-family reminder",
        )
    )

    issues.extend(
        _check_markers(repo_root / SELFTEST_DRIVER_PATH, SELFTEST_DRIVER_MARKERS, "selftest driver")
    )
    issues.extend(_check_markers(repo_root / MAKEFILE_PATH, MAKEFILE_MARKERS, "makefile"))
    return issues


def _expanded_marker_lines(marker_counts: dict[str, int]) -> list[str]:
    lines: list[str] = []
    for marker, count in marker_counts.items():
        lines.extend(marker for _ in range(count))
    return lines


def _populate_repo(root: Path) -> None:
    _write(
        root / README_PATH,
        "\n".join(
            (
                "# Zigux Documentation",
                README_PHASE3_PREFIX + " ".join((*README_MARKERS, *README_PHASE3_MARKER_COUNTS.keys())),
                README_PHASE3_NEXT_PREFIX + "later lane",
            )
        )
        + "\n",
    )
    _write(
        root / NOTE_PATH,
        "\n".join(
            (
                "# Phase 3 ABI H Boundary Next Step",
                "## Current landed surface",
                NOTE_NEXT_STEP_PREFIX,
                *NOTE_POLICY_MARKERS,
                NOTE_NEXT_STEP_NEXT_PREFIX,
                "## Non-goals",
            )
        )
        + "\n",
    )
    _write(
        root / SURVEY_PATH,
        "\n".join(
            (
                "# Phase 3 ABI Header Family Survey",
                HEADER_FAMILY_SURVEY_CURRENT_PACKET_PREFIX,
                *_expanded_marker_lines(HEADER_FAMILY_SURVEY_CURRENT_PACKET_MARKER_COUNTS),
                HEADER_FAMILY_SURVEY_CURRENT_PACKET_NEXT_PREFIX,
                "review boundary marker",
                HEADER_FAMILY_SURVEY_SHARED_REMINDER_PREFIX,
                *_expanded_marker_lines(HEADER_FAMILY_SURVEY_SHARED_REMINDER_MARKER_COUNTS),
            )
        )
        + "\n",
    )
    _write(
        root / VALIDATOR_SUPPORT_PATH,
        "\n".join(
            (
                "# Phase 3 Validator Support Surface",
                VALIDATOR_SUPPORT_SHARED_REMINDER_PREFIX,
                *VALIDATOR_SUPPORT_SHARED_REMINDER_MARKER_COUNTS.keys(),
                "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
            )
        )
        + "\n",
    )
    _write(
        root / REVIEW_CHECKLIST_PATH,
        "\n".join(
            (
                "# Zigux Review Checklist",
                "## Validation",
                REVIEW_CHECKLIST_PHASE3_PROMPT_PREFIX
                + " ".join(REVIEW_CHECKLIST_PHASE3_PROMPT_MARKER_COUNTS.keys()),
                REVIEW_CHECKLIST_PHASE3_PROMPT_NEXT_PREFIX + "later lane",
            )
        )
        + "\n",
    )
    _write(
        root / TESTS_README_PATH,
        "\n".join(
            (
                "# zigux/tests",
                TESTS_README_PHASE3_REMINDER_PREFIX,
                *TESTS_README_PHASE3_REMINDER_MARKER_COUNTS.keys(),
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX,
            )
        )
        + "\n",
    )
    _write(
        root / SCRIPTS_README_PATH,
        "\n".join(
            (
                "# scripts/zigux",
                "Phase 2 flow - previous lane",
                SCRIPTS_README_PHASE3_PREFIX + " ".join(SCRIPTS_README_MARKERS),
                *SCRIPTS_README_PHASE3_MARKER_COUNTS.keys(),
                SCRIPTS_README_PHASE3_NEXT_PREFIX + "later lane",
                SCRIPTS_HEADER_FAMILY_REMINDER_PREFIX
                + " ".join(SCRIPTS_HEADER_FAMILY_REMINDER_MARKER_COUNTS.keys()),
            )
        )
        + "\n",
    )
    _write(root / SELFTEST_DRIVER_PATH, "\n".join(SELFTEST_DRIVER_MARKERS) + "\n")
    _write(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")


def _expect_issue(issues: list[str], expected: str) -> bool:
    return expected in issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_selftest_surface_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        docs_path = root / README_PATH
        docs_path.write_text(_read(docs_path).replace(README_PHASE3_PREFIX, "Phase 3 overview - ", 1), encoding="utf-8")
        issues = validate_repo(root)
        if not _expect_issue(issues, "missing docs README Phase 3 notes section"):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected missing docs README Phase 3 notes section was not reported")
            return 1

        _populate_repo(root)
        docs_path.write_text(
            _read(docs_path).replace(
                "scripts/zigux/validate-phase3.py",
                README_PHASE3_NEXT_PREFIX + "\nscripts/zigux/validate-phase3.py",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "docs README Phase 3 notes marker count drift: "
            "scripts/zigux/validate-phase3.py (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected docs README section-scoped validator drift was not reported")
            return 1

        _populate_repo(root)
        note_path = root / NOTE_PATH
        note_path.write_text(_read(note_path).replace(NOTE_POLICY_MARKERS[0], "", 1), encoding="utf-8")
        issues = validate_repo(root)
        expected = (
            "abi.h next-step note marker count drift: "
            + NOTE_POLICY_MARKERS[0]
            + " (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected abi.h next-step drift was not reported")
            return 1

        _populate_repo(root)
        validator_support_path = root / VALIDATOR_SUPPORT_PATH
        validator_support_path.write_text(
            _read(validator_support_path).replace(
                "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "validator-support shared reminder marker count drift: "
            "Documentation/zigux/phase3-abi-h-boundary-next-step.md (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support next-step drift was not reported")
            return 1

        _populate_repo(root)
        validator_support_path.write_text(
            _read(validator_support_path).replace("include/zigux/dev_t.h", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "validator-support shared reminder marker count drift: "
            "include/zigux/dev_t.h (expected 2, found 1)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support dev_t header drift was not reported")
            return 1

        _populate_repo(root)
        validator_support_path.write_text(
            _read(validator_support_path).replace("zigux/uapi/version.zig", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "validator-support shared reminder marker count drift: "
            "zigux/uapi/version.zig (expected 2, found 1)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support version companion drift was not reported")
            return 1

        _populate_repo(root)
        validator_support_path.write_text(
            _read(validator_support_path).replace(
                "scripts/zigux/validate-phase3-linux-zigux-header-governance.py",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "validator-support shared reminder marker count drift: "
            "scripts/zigux/validate-phase3-linux-zigux-header-governance.py (expected 2, found 1)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support header-governance validator drift was not reported")
            return 1

        _populate_repo(root)
        validator_support_path.write_text(
            _read(validator_support_path).replace(
                "Documentation/zigux/phase3-kernel-export-shim-governance.md",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "validator-support shared reminder marker count drift: "
            "Documentation/zigux/phase3-kernel-export-shim-governance.md (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support export-shim governance drift was not reported")
            return 1

        _populate_repo(root)
        validator_support_path.write_text(
            _read(validator_support_path).replace(
                "header-governance context through the paired survey and next-step notes",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "validator-support shared reminder marker count drift: "
            "header-governance context through the paired survey and next-step notes (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support paired-survey wording drift was not reported")
            return 1

        _populate_repo(root)
        validator_support_path.write_text(
            _read(validator_support_path).replace(
                "kernel-facing governance note is already a broad",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "validator-support shared reminder marker count drift: "
            "kernel-facing governance note is already a broad (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support kernel-governance wording drift was not reported")
            return 1

        _populate_repo(root)
        tests_path = root / TESTS_README_PATH
        tests_path.write_text(
            _read(tests_path).replace("scripts/zigux/phase3_catalog.py --self-test", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: "
            "scripts/zigux/phase3_catalog.py --self-test (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected tests README reminder-only drift was not reported")
            return 1

        _populate_repo(root)
        tests_path.write_text(
            _read(tests_path).replace("include/zigux/dev_t.h", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: "
            "include/zigux/dev_t.h (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected tests README dev_t header drift was not reported")
            return 1

        _populate_repo(root)
        tests_path.write_text(
            _read(tests_path).replace("zigux/uapi/version.zig", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: "
            "zigux/uapi/version.zig (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected tests README version companion drift was not reported")
            return 1

        _populate_repo(root)
        scripts_path = root / SCRIPTS_README_PATH
        scripts_path.write_text(
            _read(scripts_path).replace("include/zigux/dev_t.h", "", 1),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "scripts README header-family reminder marker count drift: "
            "include/zigux/dev_t.h (expected 1, found 0)"
        )
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected scripts README dev_t header reminder drift was not reported")
            return 1

        _populate_repo(root)
        driver_path = root / SELFTEST_DRIVER_PATH
        driver_path.write_text(_read(driver_path).replace(SELFTEST_DRIVER_MARKERS[0], "", 1), encoding="utf-8")
        issues = validate_repo(root)
        expected = f"missing selftest driver marker: {SELFTEST_DRIVER_MARKERS[0]}"
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected selftest driver drift was not reported")
            return 1

        _populate_repo(root)
        makefile_path = root / MAKEFILE_PATH
        makefile_path.write_text(_read(makefile_path).replace(MAKEFILE_MARKERS[1], "", 1), encoding="utf-8")
        issues = validate_repo(root)
        expected = f"missing makefile marker: {MAKEFILE_MARKERS[1]}"
        if not _expect_issue(issues, expected):
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected makefile drift was not reported")
            return 1

    print("PHASE3_SELFTEST_SURFACE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 3 selftest reminder surface."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the shared Phase 3 reminder files",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_SELFTEST_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / SCRIPTS_README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
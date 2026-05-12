#!/usr/bin/env python3
"""Fail-close the shared Phase 3 selftest reminder surface."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


README_PATH = Path("Documentation/zigux/README.md")
CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
NOTE_PATH = Path("Documentation/zigux/phase3-abi-h-boundary-next-step.md")
SURVEY_PATH = Path("Documentation/zigux/phase3-abi-header-family-survey.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
MAKEFILE_PATH = Path("zigux/Makefile")

README_MARKERS = (
    "make -C zigux phase3-selftest",
    "validate_phase3_selftest.py",
)
README_PHASE3_MARKER_COUNTS = {
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "Documentation/zigux/phase3-validator-support-surface.md": 1,
    "scripts/zigux/validate-phase3-abi-header-family-survey.py": 1,
    "zigux/uapi/dev_t.zig": 1,
}
README_PHASE3_PREFIX = "Phase 3 notes - "
README_PHASE3_NEXT_PREFIX = "Phase 5 notes - "
CHECKLIST_MARKERS = (
    "scripts/zigux/check-phase3-selftest-surface.py",
    "make -C zigux phase3-selftest",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "Documentation/zigux/phase3-validator-support-surface.md",
    "zigux/uapi/dev_t.zig",
)
CHECKLIST_PHASE3_REMINDER_PREFIX = (
    "  * if the change touches the shared Phase 3 ABI/runtime packet, do "
)
CHECKLIST_PHASE3_REMINDER_NEXT_PREFIX = (
    "  * if the change touches the shared Phase 4 validation packet, do "
)
CHECKLIST_PHASE3_REMINDER_MARKER_COUNTS = {marker: 1 for marker in CHECKLIST_MARKERS}
NOTE_POLICY_MARKERS = (
    "keeping `zigux/uapi/dev_t.zig` explicit beside the dedicated survey",
    "and next-step notes while leaving the narrower `zigux/uapi/version.zig`",
    "export/UAPI packet actually grows",
)
NOTE_NEXT_STEP_PREFIX = "## Next bounded step"
NOTE_NEXT_STEP_NEXT_PREFIX = "## Non-goals"
HEADER_FAMILY_SURVEY_SHARED_REMINDER_MARKER_COUNTS = {
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md": 1,
    "Documentation/zigux/phase3-linux-zigux-header-governance.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "Documentation/zigux/README.md": 1,
    "Documentation/zigux/review-checklist.md": 1,
    "scripts/zigux/README.md": 1,
    "zigux/tests/README.md": 1,
    "zigux/uapi/dev_t.zig": 1,
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
TESTS_README_MARKERS = (
    "scripts/zigux/check-phase3-selftest-surface.py",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "make -C zigux phase3-selftest",
)
TESTS_README_MARKER_COUNTS = {
    "scripts/zigux/phase3_catalog.py --self-test": 1,
    "scripts/zigux/phase3_check_lib.py --self-test": 1,
    "scripts/zigux/generate-phase3-check-wrappers.py --check": 1,
    "scripts/zigux/run-phase3-checks.py --self-test": 1,
    "scripts/zigux/phase3_catalog.py --audit-doc-sync": 1,
    "scripts/zigux/survey-phase3-abi-constant-parity.py": 1,
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "Documentation/zigux/phase3-validator-support-surface.md": 1,
    "scripts/zigux/validate-phase3-abi-header-family-survey.py": 1,
    "zigux/uapi/dev_t.zig": 1,
}
TESTS_README_PHASE3_REMINDER_MARKER_COUNTS = {
    **{marker: 1 for marker in TESTS_README_MARKERS},
    **TESTS_README_MARKER_COUNTS,
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
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "Documentation/zigux/phase3-validator-support-surface.md": 1,
    "scripts/zigux/validate-phase3-abi-header-family-survey.py": 1,
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
    "zigux/uapi/dev_t.zig": 1,
}
SELFTEST_DRIVER_MARKERS = (
    'Path("scripts/zigux/check-phase3-selftest-surface.py")',
    'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
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

def _check_markers(path: Path, markers: tuple[str, ...], label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]
    return [
        f"missing {label} marker: {marker}"
        for marker in markers
        if marker not in text
    ]

def _check_marker_counts(path: Path, marker_counts: dict[str, int], label: str) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]

    issues: list[str] = []
    for marker, expected_count in marker_counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            issues.append(
                f"{label} marker count drift: {marker} (expected {expected_count}, found {actual_count})"
            )
    return issues

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

def _check_tests_readme_phase3_reminder(path: Path) -> list[str]:
    return _check_section_marker_counts(
        path,
        TESTS_README_PHASE3_REMINDER_PREFIX,
        TESTS_README_PHASE3_REMINDER_NEXT_PREFIX,
        TESTS_README_PHASE3_REMINDER_MARKER_COUNTS,
        "tests README Phase 3 reminder",
    )

def _check_header_family_survey_shared_reminder(path: Path) -> list[str]:
    return _check_section_marker_counts(
        path,
        HEADER_FAMILY_SURVEY_SHARED_REMINDER_PREFIX,
        None,
        HEADER_FAMILY_SURVEY_SHARED_REMINDER_MARKER_COUNTS,
        "header-family survey shared reminder",
    )

def _check_review_checklist_phase3_reminder(path: Path) -> list[str]:
    return _check_section_marker_counts(
        path,
        CHECKLIST_PHASE3_REMINDER_PREFIX,
        CHECKLIST_PHASE3_REMINDER_NEXT_PREFIX,
        CHECKLIST_PHASE3_REMINDER_MARKER_COUNTS,
        "review checklist Phase 3 reminder",
    )

def _check_note_next_step(path: Path) -> list[str]:
    return _check_section_marker_counts(
        path,
        NOTE_NEXT_STEP_PREFIX,
        NOTE_NEXT_STEP_NEXT_PREFIX,
        {marker: 1 for marker in NOTE_POLICY_MARKERS},
        "abi.h next-step note",
    )

def _check_scripts_header_family_reminder(path: Path) -> list[str]:
    return _check_section_marker_counts(
        path,
        SCRIPTS_HEADER_FAMILY_REMINDER_PREFIX,
        None,
        SCRIPTS_HEADER_FAMILY_REMINDER_MARKER_COUNTS,
        "scripts README header-family reminder",
    )

def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    docs_readme = repo_root / README_PATH
    issues.extend(_check_markers(docs_readme, README_MARKERS, "docs README"))
    issues.extend(
        _check_section_marker_counts(
            docs_readme,
            README_PHASE3_PREFIX,
            README_PHASE3_NEXT_PREFIX,
            README_PHASE3_MARKER_COUNTS,
            "docs README Phase 3 notes",
        )
    )
    issues.extend(
        _check_markers(
            repo_root / CHECKLIST_PATH, CHECKLIST_MARKERS, "review checklist"
        )
    )
    issues.extend(
        _check_review_checklist_phase3_reminder(repo_root / CHECKLIST_PATH)
    )
    issues.extend(_check_note_next_step(repo_root / NOTE_PATH))
    issues.extend(
        _check_header_family_survey_shared_reminder(repo_root / SURVEY_PATH)
    )
    tests_readme = repo_root / TESTS_README_PATH
    issues.extend(
        _check_markers(tests_readme, TESTS_README_MARKERS, "tests README")
    )
    issues.extend(
        _check_marker_counts(
            tests_readme,
            TESTS_README_MARKER_COUNTS,
            "tests README",
        )
    )
    issues.extend(_check_tests_readme_phase3_reminder(tests_readme))
    scripts_readme = repo_root / SCRIPTS_README_PATH
    issues.extend(
        _check_markers(
            scripts_readme, SCRIPTS_README_MARKERS, "scripts README"
        )
    )
    issues.extend(
        _check_section_marker_counts(
            scripts_readme,
            SCRIPTS_README_PHASE3_PREFIX,
            SCRIPTS_README_PHASE3_NEXT_PREFIX,
            SCRIPTS_README_PHASE3_MARKER_COUNTS,
            "scripts README Phase 3 flow",
        )
    )
    issues.extend(_check_scripts_header_family_reminder(scripts_readme))
    issues.extend(
        _check_markers(
            repo_root / SELFTEST_DRIVER_PATH,
            SELFTEST_DRIVER_MARKERS,
            "selftest driver",
        )
    )
    issues.extend(
        _check_markers(repo_root / MAKEFILE_PATH, MAKEFILE_MARKERS, "makefile")
    )
    return issues

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def _populate_repo(root: Path) -> None:
    _write(
        root / README_PATH,
        "\n".join(
            (
                *README_MARKERS,
                README_PHASE3_PREFIX,
                *README_PHASE3_MARKER_COUNTS.keys(),
                README_PHASE3_NEXT_PREFIX,
            )
        )
        + "\n",
    )
    _write(
        root / CHECKLIST_PATH,
        "\n".join(
            (
                "## Validation",
                CHECKLIST_PHASE3_REMINDER_PREFIX,
                *CHECKLIST_PHASE3_REMINDER_MARKER_COUNTS.keys(),
                CHECKLIST_PHASE3_REMINDER_NEXT_PREFIX,
            )
        )
        + "\n",
    )
    _write(
        root / NOTE_PATH,
        "\n".join(
            (
                "## Current landed surface",
                "current surface marker",
                NOTE_NEXT_STEP_PREFIX,
                *NOTE_POLICY_MARKERS,
                NOTE_NEXT_STEP_NEXT_PREFIX,
            )
        )
        + "\n",
    )
    _write(
        root / SURVEY_PATH,
        "\n".join(
            (
                "## Current packet",
                "current packet marker",
                "## Review boundary",
                "review boundary marker",
                HEADER_FAMILY_SURVEY_SHARED_REMINDER_PREFIX,
                *HEADER_FAMILY_SURVEY_SHARED_REMINDER_MARKER_COUNTS.keys(),
            )
        )
        + "\n",
    )
    _write(
        root / TESTS_README_PATH,
        "\n".join(
            (
                TESTS_README_PHASE3_REMINDER_PREFIX,
                *TESTS_README_MARKERS,
                *TESTS_README_MARKER_COUNTS.keys(),
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX,
            )
        )
        + "\n",
    )
    _write(
        root / SCRIPTS_README_PATH,
        "\n".join(
            (
                *SCRIPTS_README_MARKERS,
                SCRIPTS_README_PHASE3_PREFIX,
                *SCRIPTS_README_PHASE3_MARKER_COUNTS.keys(),
                SCRIPTS_README_PHASE3_NEXT_PREFIX,
                SCRIPTS_HEADER_FAMILY_REMINDER_PREFIX,
                *SCRIPTS_HEADER_FAMILY_REMINDER_MARKER_COUNTS.keys(),
            )
        )
        + "\n",
    )
    _write(root / SELFTEST_DRIVER_PATH, "\n".join(SELFTEST_DRIVER_MARKERS) + "\n")
    _write(root / MAKEFILE_PATH, "\n".join(MAKEFILE_MARKERS) + "\n")

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_selftest_surface_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        broken_path = root / TESTS_README_PATH
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/check-phase3-selftest-surface.py", "", 1
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "missing tests README marker: scripts/zigux/check-phase3-selftest-surface.py"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected missing tests README marker was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/run-phase3-checks.py --self-test",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: "
            "scripts/zigux/run-phase3-checks.py --self-test "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected phase3 run-phase3-checks self-test drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/check-phase3-selftest-surface.py",
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX
                + "\n"
                + "scripts/zigux/check-phase3-selftest-surface.py",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: "
            "scripts/zigux/check-phase3-selftest-surface.py "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected section-scoped tests README checker drift was not reported")
            return 1

        _populate_repo(root)
        checklist_path = root / CHECKLIST_PATH
        checklist_path.write_text(
            _read(checklist_path).replace(
                "Documentation/zigux/phase3-abi-header-family-survey.md",
                CHECKLIST_PHASE3_REMINDER_NEXT_PREFIX
                + "\n"
                + "Documentation/zigux/phase3-abi-header-family-survey.md",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "review checklist Phase 3 reminder marker count drift: "
            "Documentation/zigux/phase3-abi-header-family-survey.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print(
                "expected review checklist Phase 3 section-scoped drift was not reported"
            )
            return 1

        _populate_repo(root)
        checklist_path.write_text(
            _read(checklist_path).replace(
                "Documentation/zigux/phase3-validator-support-surface.md",
                CHECKLIST_PHASE3_REMINDER_NEXT_PREFIX
                + "\n"
                + "Documentation/zigux/phase3-validator-support-surface.md",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "review checklist Phase 3 reminder marker count drift: "
            "Documentation/zigux/phase3-validator-support-surface.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print(
                "expected review checklist validator-support section-scoped drift "
                "was not reported"
            )
            return 1

        _populate_repo(root)
        note_path = root / NOTE_PATH
        note_path.write_text(
            _read(note_path).replace(
                "keeping `zigux/uapi/dev_t.zig` explicit beside the dedicated survey",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "abi.h next-step note marker count drift: "
            "keeping `zigux/uapi/dev_t.zig` explicit beside the dedicated survey "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected abi.h next-step note policy drift was not reported")
            return 1

        _populate_repo(root)
        note_path.write_text(
            _read(note_path).replace(
                "and next-step notes while leaving the narrower `zigux/uapi/version.zig`",
                NOTE_NEXT_STEP_NEXT_PREFIX
                + "\n"
                + "and next-step notes while leaving the narrower `zigux/uapi/version.zig`",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "abi.h next-step note marker count drift: "
            "and next-step notes while leaving the narrower `zigux/uapi/version.zig` "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected abi.h next-step note section-scoped drift was not reported")
            return 1

        _populate_repo(root)
        survey_path = root / SURVEY_PATH
        survey_path.write_text(
            _read(survey_path).replace(
                "`include/zigux/dev_t.h` plus `zigux/uapi/version.zig` starter-companion detail",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "header-family survey shared reminder marker count drift: "
            "`include/zigux/dev_t.h` plus `zigux/uapi/version.zig` starter-companion detail "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected header-family starter-companion reminder drift was not reported")
            return 1

        _populate_repo(root)
        survey_path.write_text(
            _read(survey_path).replace(
                "Documentation/zigux/phase3-linux-zigux-header-governance.md",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "header-family survey shared reminder marker count drift: "
            "Documentation/zigux/phase3-linux-zigux-header-governance.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected header-governance reminder drift was not reported")
            return 1

        _populate_repo(root)
        survey_path.write_text(
            _read(survey_path).replace(
                "zigux/uapi/dev_t.zig",
                "## Future follow-through\n" + "zigux/uapi/dev_t.zig",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "header-family survey shared reminder marker count drift: "
            "zigux/uapi/dev_t.zig "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected section-scoped dev_t reminder drift was not reported")
            return 1

        _populate_repo(root)
        survey_path.write_text(
            _read(survey_path).replace(
                HEADER_FAMILY_SURVEY_SHARED_REMINDER_PREFIX
                + "\n"
                + "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
                "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
                + "\n"
                + HEADER_FAMILY_SURVEY_SHARED_REMINDER_PREFIX
                + "\n",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "header-family survey shared reminder marker count drift: "
            "Documentation/zigux/phase3-export-uapi-boundary-survey.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected section-scoped header-family survey drift was not reported")
            return 1

        _populate_repo(root)
        survey_path.write_text(
            _read(survey_path).replace(
                "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
                "## Future follow-through\n"
                + "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "header-family survey shared reminder marker count drift: "
            "Documentation/zigux/phase3-export-uapi-boundary-survey.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print(
                "expected next-heading-bounded header-family survey drift was not reported"
            )
            return 1

        _populate_repo(root)
        scripts_path = root / SCRIPTS_README_PATH
        scripts_path.write_text(
            _read(scripts_path).replace(
                "Documentation/zigux/phase3-linux-zigux-header-governance.md",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "scripts README header-family reminder marker count drift: "
            "Documentation/zigux/phase3-linux-zigux-header-governance.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected scripts README header-governance drift was not reported")
            return 1

        _populate_repo(root)
        scripts_path.write_text(
            _read(scripts_path).replace(
                "Documentation/zigux/phase3-linux-zigux-header-governance.md",
                "",
                1,
            ).replace(
                SCRIPTS_HEADER_FAMILY_REMINDER_PREFIX,
                "Documentation/zigux/phase3-linux-zigux-header-governance.md\n"
                + SCRIPTS_HEADER_FAMILY_REMINDER_PREFIX,
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "scripts README header-family reminder marker count drift: "
            "Documentation/zigux/phase3-linux-zigux-header-governance.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected scripts README section-bounded governance drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/phase3_catalog.py --self-test",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: scripts/zigux/phase3_catalog.py --self-test "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected phase3 catalog self-test drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/phase3_check_lib.py --self-test",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: scripts/zigux/phase3_check_lib.py --self-test "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected phase3 check-lib self-test drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/generate-phase3-check-wrappers.py --check",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: scripts/zigux/generate-phase3-check-wrappers.py --check "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected wrapper-check drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/phase3_catalog.py --audit-doc-sync",
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX
                + "\n"
                + "scripts/zigux/phase3_catalog.py --audit-doc-sync",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: scripts/zigux/phase3_catalog.py --audit-doc-sync "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected section-scoped audit-doc-sync drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/survey-phase3-abi-constant-parity.py",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: scripts/zigux/survey-phase3-abi-constant-parity.py "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected constant-parity marker count drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "scripts/zigux/survey-phase3-abi-constant-parity.py",
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX
                + "\n"
                + "scripts/zigux/survey-phase3-abi-constant-parity.py",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: scripts/zigux/survey-phase3-abi-constant-parity.py "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected section-scoped constant-parity drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "Documentation/zigux/phase3-abi-header-family-survey.md",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: Documentation/zigux/phase3-abi-header-family-survey.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected header-family survey marker count drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: Documentation/zigux/phase3-abi-h-boundary-next-step.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected abi.h next-step marker count drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "Documentation/zigux/phase3-validator-support-surface.md",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: Documentation/zigux/phase3-validator-support-surface.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support note drift in tests README was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "zigux/uapi/dev_t.zig",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: zigux/uapi/dev_t.zig (expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected dev_t marker count drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "python3 scripts/zigux/validate_phase3_selftest.py",
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX
                + "\n"
                + "python3 scripts/zigux/validate_phase3_selftest.py",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: "
            "python3 scripts/zigux/validate_phase3_selftest.py "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected tests README selftest-driver section drift was not reported")
            return 1

        _populate_repo(root)
        broken_path.write_text(
            _read(broken_path).replace(
                "make -C zigux phase3-selftest",
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX
                + "\n"
                + "make -C zigux phase3-selftest",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "tests README Phase 3 reminder marker count drift: "
            "make -C zigux phase3-selftest "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected tests README selftest-route section drift was not reported")
            return 1

        _populate_repo(root)
        docs_path = root / README_PATH
        docs_path.write_text(
            _read(docs_path).replace(
                "Documentation/zigux/phase3-abi-header-family-survey.md",
                README_PHASE3_NEXT_PREFIX
                + "\n"
                + "Documentation/zigux/phase3-abi-header-family-survey.md",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "docs README Phase 3 notes marker count drift: Documentation/zigux/phase3-abi-header-family-survey.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected docs README section-scoped drift was not reported")
            return 1

        _populate_repo(root)
        docs_path.write_text(
            _read(docs_path).replace(
                "Documentation/zigux/phase3-validator-support-surface.md",
                README_PHASE3_NEXT_PREFIX
                + "\n"
                + "Documentation/zigux/phase3-validator-support-surface.md",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "docs README Phase 3 notes marker count drift: Documentation/zigux/phase3-validator-support-surface.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support note drift in docs README was not reported")
            return 1

        _populate_repo(root)
        docs_path.write_text(
            _read(docs_path).replace(
                "scripts/zigux/validate-phase3-abi-header-family-survey.py",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "docs README Phase 3 notes marker count drift: scripts/zigux/validate-phase3-abi-header-family-survey.py "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected header-family validator drift in docs README was not reported")
            return 1

        _populate_repo(root)
        docs_path.write_text(
            _read(docs_path).replace(
                "scripts/zigux/validate-phase3-abi-header-family-survey.py",
                README_PHASE3_NEXT_PREFIX
                + "\n"
                + "scripts/zigux/validate-phase3-abi-header-family-survey.py",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "docs README Phase 3 notes marker count drift: scripts/zigux/validate-phase3-abi-header-family-survey.py "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected section-scoped header-family validator drift in docs README was not reported")
            return 1

        _populate_repo(root)
        scripts_path.write_text(
            _read(scripts_path).replace(
                "zigux/uapi/dev_t.zig",
                SCRIPTS_README_PHASE3_NEXT_PREFIX + "\n" + "zigux/uapi/dev_t.zig",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "scripts README Phase 3 flow marker count drift: zigux/uapi/dev_t.zig "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected scripts README section-scoped drift was not reported")
            return 1

        _populate_repo(root)
        scripts_path.write_text(
            _read(scripts_path).replace(
                "Documentation/zigux/phase3-validator-support-surface.md",
                SCRIPTS_README_PHASE3_NEXT_PREFIX
                + "\n"
                + "Documentation/zigux/phase3-validator-support-surface.md",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            "scripts README Phase 3 flow marker count drift: Documentation/zigux/phase3-validator-support-surface.md "
            "(expected 1, found 0)"
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected validator-support note drift in scripts README was not reported")
            return 1

        _populate_repo(root)
        driver_path = root / SELFTEST_DRIVER_PATH
        driver_path.write_text(
            _read(driver_path).replace(
                'Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = (
            'missing selftest driver marker: Path("scripts/zigux/validate-phase3-low-level-wrapper-survey.py")'
        )
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected missing low-level-wrapper selftest marker was not reported")
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

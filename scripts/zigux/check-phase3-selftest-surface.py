#!/usr/bin/env python3
"""Fail-close the shared Phase 3 selftest reminder surface."""

from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


README_PATH = Path("Documentation/zigux/README.md")
CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
SELFTEST_DRIVER_PATH = Path("scripts/zigux/validate_phase3_selftest.py")
MAKEFILE_PATH = Path("zigux/Makefile")

README_MARKERS = (
    "make -C zigux phase3-selftest",
    "validate_phase3_selftest.py",
)
CHECKLIST_MARKERS = (
    "scripts/zigux/check-phase3-selftest-surface.py",
    "make -C zigux phase3-selftest",
    "Documentation/zigux/phase3-abi-header-family-survey.md",
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md",
    "zigux/uapi/dev_t.zig",
)
TESTS_README_MARKERS = (
    "scripts/zigux/check-phase3-selftest-surface.py",
    "python3 scripts/zigux/validate_phase3_selftest.py",
    "make -C zigux phase3-selftest",
)
TESTS_README_MARKER_COUNTS = {
    "scripts/zigux/survey-phase3-abi-constant-parity.py": 1,
    "Documentation/zigux/phase3-abi-header-family-survey.md": 1,
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md": 1,
    "zigux/uapi/dev_t.zig": 1,
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


def _extract_tests_phase3_reminder(text: str) -> str | None:
    if TESTS_README_PHASE3_REMINDER_PREFIX not in text:
        return None
    reminder = text.split(TESTS_README_PHASE3_REMINDER_PREFIX, 1)[1]
    if TESTS_README_PHASE3_REMINDER_NEXT_PREFIX in reminder:
        reminder = reminder.split(TESTS_README_PHASE3_REMINDER_NEXT_PREFIX, 1)[0]
    return reminder


def _check_tests_readme_phase3_reminder(path: Path) -> list[str]:
    try:
        text = _read(path)
    except FileNotFoundError:
        return [f"missing repo file: {path.as_posix()}"]

    reminder = _extract_tests_phase3_reminder(text)
    if reminder is None:
        return [
            "missing tests README Phase 3 validator-support reminder block"
        ]

    issues: list[str] = []
    for marker, expected_count in TESTS_README_MARKER_COUNTS.items():
        actual_count = reminder.count(marker)
        if actual_count != expected_count:
            issues.append(
                "tests README Phase 3 reminder marker count drift: "
                f"{marker} (expected {expected_count}, found {actual_count})"
            )
    return issues


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    issues.extend(_check_markers(repo_root / README_PATH, README_MARKERS, "docs README"))
    issues.extend(
        _check_markers(
            repo_root / CHECKLIST_PATH, CHECKLIST_MARKERS, "review checklist"
        )
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
    issues.extend(
        _check_markers(
            repo_root / SCRIPTS_README_PATH, SCRIPTS_README_MARKERS, "scripts README"
        )
    )
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
    _write(root / README_PATH, "\n".join(README_MARKERS) + "\n")
    _write(root / CHECKLIST_PATH, "\n".join(CHECKLIST_MARKERS) + "\n")
    _write(
        root / TESTS_README_PATH,
        "\n".join(
            (
                *TESTS_README_MARKERS,
                TESTS_README_PHASE3_REMINDER_PREFIX,
                *TESTS_README_MARKER_COUNTS.keys(),
                TESTS_README_PHASE3_REMINDER_NEXT_PREFIX,
            )
        )
        + "\n",
    )
    _write(root / SCRIPTS_README_PATH, "\n".join(SCRIPTS_README_MARKERS) + "\n")
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
        checklist_path = root / CHECKLIST_PATH
        checklist_path.write_text(
            _read(checklist_path).replace(
                "zigux/uapi/dev_t.zig",
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = validate_repo(root)
        expected = "missing review checklist marker: zigux/uapi/dev_t.zig"
        if expected not in issues:
            print("PHASE3_SELFTEST_SURFACE_SELF_TEST=fail")
            print("expected missing review checklist dev_t marker was not reported")
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

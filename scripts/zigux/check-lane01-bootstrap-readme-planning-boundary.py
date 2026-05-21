#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")

REQUIRED_LINES = (
    "It does not exist to become a permanent parallel subsystem tree.",
    "Rules",
    "- Keep product planning and bootstrap artifacts here first.",
)

PURPOSE_MARKER = "- first-commit sequencing for the Zigux product buildout"
BOUNDARY_LINE = REQUIRED_LINES[0]
RULES_HEADING = REQUIRED_LINES[1]
RULES_FIRST_LINE = REQUIRED_LINES[2]


def collect_issues(root: Path) -> list[str]:
    readme = (root / README_PATH).read_text(encoding="utf-8")

    issues: list[str] = []
    for line in REQUIRED_LINES:
        if line not in readme:
            issues.append(f"missing:{line}")

    if issues:
        return issues

    lines = readme.splitlines()
    purpose_index = lines.index(PURPOSE_MARKER)
    boundary_index = lines.index(BOUNDARY_LINE)
    rules_heading_index = lines.index(RULES_HEADING)
    rules_first_index = lines.index(RULES_FIRST_LINE)

    if not (purpose_index < boundary_index < rules_heading_index < rules_first_index):
        issues.append("order:purpose-boundary-rules")

    if boundary_index - purpose_index != 2:
        issues.append("spacing:purpose-to-boundary")

    if rules_heading_index - boundary_index != 2:
        issues.append("spacing:boundary-to-rules")

    if rules_first_index - rules_heading_index != 1:
        issues.append("spacing:rules-heading-to-first-rule")

    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

It exists to hold:
- program-level planning
- source maps
- phase ledgers
- validation and porting rules
- first-commit sequencing for the Zigux product buildout

It does not exist to become a permanent parallel subsystem tree.

Rules
- Keep product planning and bootstrap artifacts here first.
- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_planning_boundary_") as tmp_dir:
        root = Path(tmp_dir)
        baseline = _sample_readme()
        _write(root / README_PATH, baseline)

        if collect_issues(root):
            raise AssertionError("baseline Lane 01 planning-boundary fixture should pass")
        case_count += 1

        _write(root / README_PATH, baseline.replace(f"{BOUNDARY_LINE}\n\n", "", 1))
        issues = collect_issues(root)
        expected = [f"missing:{BOUNDARY_LINE}"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for missing boundary line: {issues}")
        _write(root / README_PATH, baseline)
        case_count += 1

        _write(root / README_PATH, baseline.replace("Rules\n", "", 1))
        issues = collect_issues(root)
        expected = ["missing:Rules"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for missing rules heading: {issues}")
        _write(root / README_PATH, baseline)
        case_count += 1

        _write(
            root / README_PATH,
            baseline.replace(
                f"{BOUNDARY_LINE}\n\nRules\n",
                "Rules\n\n" + f"{BOUNDARY_LINE}\n",
                1,
            ),
        )
        issues = collect_issues(root)
        expected = [
            "order:purpose-boundary-rules",
            "spacing:purpose-to-boundary",
            "spacing:boundary-to-rules",
            "spacing:rules-heading-to-first-rule",
        ]
        if issues != expected:
            raise AssertionError(f"unexpected issues for reordered boundary line: {issues}")
        _write(root / README_PATH, baseline)
        case_count += 1

        _write(
            root / README_PATH,
            baseline.replace(
                f"{PURPOSE_MARKER}\n\n{BOUNDARY_LINE}",
                f"{PURPOSE_MARKER}\n{BOUNDARY_LINE}",
                1,
            ),
        )
        issues = collect_issues(root)
        expected = ["spacing:purpose-to-boundary"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for collapsed purpose spacing: {issues}")
        _write(root / README_PATH, baseline)
        case_count += 1

        _write(
            root / README_PATH,
            baseline.replace(
                f"{BOUNDARY_LINE}\n\nRules",
                f"{BOUNDARY_LINE}\nRules",
                1,
            ),
        )
        issues = collect_issues(root)
        expected = ["spacing:boundary-to-rules"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for collapsed boundary spacing: {issues}")
        _write(root / README_PATH, baseline)
        case_count += 1

        _write(
            root / README_PATH,
            baseline.replace(
                "Rules\n- Keep product planning and bootstrap artifacts here first.",
                "Rules\n\n- Keep product planning and bootstrap artifacts here first.",
                1,
            ),
        )
        issues = collect_issues(root)
        expected = ["spacing:rules-heading-to-first-rule"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for expanded rules spacing: {issues}")
        case_count += 1

    print("LANE01_BOOTSTRAP_README_PLANNING_BOUNDARY_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_README_PLANNING_BOUNDARY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 bootstrap README planning-only boundary stays intact."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic Lane 01 README fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        for item in issues:
            print(f"ERROR: {item}")
        return 1

    print("Lane 01 bootstrap README planning-boundary check passed.")
    print(f"LANE01_BOOTSTRAP_README_PLANNING_BOUNDARY_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
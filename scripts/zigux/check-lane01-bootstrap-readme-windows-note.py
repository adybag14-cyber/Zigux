#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")

WINDOWS_NOTE = (
    "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo."
)
PRECEDING_RULE = (
    "- Treat ZAR as the research and proving repo and Zigux as the product repo."
)
NEXT_HEADING = "Active product surfaces"


def readme_lines(root: Path) -> list[str]:
    return (root / README_PATH).read_text(encoding="utf-8").splitlines()


def collect_issues(root: Path) -> list[str]:
    lines = readme_lines(root)
    issues: list[str] = []

    note_indexes = [index for index, line in enumerate(lines) if line == WINDOWS_NOTE]
    if not note_indexes:
        issues.append(f"missing:{WINDOWS_NOTE}")
        return issues
    if len(note_indexes) != 1:
        issues.append(f"count:{len(note_indexes)}")

    try:
        preceding_index = lines.index(PRECEDING_RULE)
    except ValueError:
        issues.append(f"missing:{PRECEDING_RULE}")
        return issues

    try:
        next_heading_index = lines.index(NEXT_HEADING)
    except ValueError:
        issues.append(f"missing:{NEXT_HEADING}")
        return issues

    note_index = note_indexes[0]
    if not (preceding_index < note_index < next_heading_index):
        issues.append("order:windows-note-must-stay-between-final-rule-and-active-product-surfaces")

    return issues


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return """# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

Rules
- Keep product planning and bootstrap artifacts here first.
- Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.
- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.
- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.
- Treat ZAR as the research and proving repo and Zigux as the product repo.
- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.

Active product surfaces
- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_windows_note_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        if collect_issues(root):
            raise AssertionError("baseline Lane 01 Windows note fixture should pass")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{WINDOWS_NOTE}\n", "", 1))
        issues = collect_issues(root)
        expected = [f"missing:{WINDOWS_NOTE}"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for missing note case: {issues}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        duplicated = _sample_readme().replace(
            WINDOWS_NOTE,
            f"{WINDOWS_NOTE}\n{WINDOWS_NOTE}",
            1,
        )
        _write(root / README_PATH, duplicated)
        issues = collect_issues(root)
        expected = ["count:2"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for duplicate note case: {issues}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        misplaced = _sample_readme().replace(
            f"{WINDOWS_NOTE}\n\nActive product surfaces",
            "\n\nActive product surfaces\n"
            f"{WINDOWS_NOTE}",
            1,
        )
        _write(root / README_PATH, misplaced)
        issues = collect_issues(root)
        expected = ["order:windows-note-must-stay-between-final-rule-and-active-product-surfaces"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for order case: {issues}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{PRECEDING_RULE}\n", "", 1))
        issues = collect_issues(root)
        expected = [f"missing:{PRECEDING_RULE}"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for missing preceding rule case: {issues}")
        _write(root / README_PATH, _sample_readme())
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{NEXT_HEADING}\n", "", 1))
        issues = collect_issues(root)
        expected = [f"missing:{NEXT_HEADING}"]
        if issues != expected:
            raise AssertionError(f"unexpected issues for missing heading case: {issues}")
        case_count += 1

    print("LANE01_BOOTSTRAP_README_WINDOWS_NOTE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_README_WINDOWS_NOTE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Lane 01 bootstrap README Windows filesystem note."
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
        help="exercise the checker against synthetic Lane 01 fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root)
    if issues:
        for issue in issues:
            print(f"LANE01_BOOTSTRAP_README_WINDOWS_NOTE_ISSUE={issue}")
        return 1

    print("Lane 01 bootstrap README Windows note check passed.")
    print("LANE01_BOOTSTRAP_README_WINDOWS_NOTE_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

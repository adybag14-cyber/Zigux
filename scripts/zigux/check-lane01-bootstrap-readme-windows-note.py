#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")
WINDOWS_NOTE = "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo."
RULES_HEADING = "Rules"
ACTIVE_PRODUCT_SURFACES_HEADING = "Active product surfaces"


def read_readme(root: Path) -> str:
    return (root / README_PATH).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    readme = read_readme(root)
    failures: list[str] = []

    if WINDOWS_NOTE not in readme:
        failures.append(f"missing:{WINDOWS_NOTE}")

    rules_index = readme.find(RULES_HEADING)
    active_index = readme.find(ACTIVE_PRODUCT_SURFACES_HEADING)
    note_index = readme.find(WINDOWS_NOTE)

    if rules_index == -1:
        failures.append(f"missing:{RULES_HEADING}")
    if active_index == -1:
        failures.append(f"missing:{ACTIVE_PRODUCT_SURFACES_HEADING}")
    if note_index != -1 and rules_index != -1 and note_index < rules_index:
        failures.append("order:windows note appears before Rules")
    if note_index != -1 and active_index != -1 and note_index > active_index:
        failures.append("order:windows note appears after Active product surfaces")

    return failures


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
- The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.
- Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.
- Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.
- Treat ZAR as the research and proving repo and Zigux as the product repo.
- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.

Active product surfaces
- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
"""


def write_sample_root(root: Path) -> None:
    _write(root / README_PATH, _sample_readme())


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_windows_note_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)

        if collect_failures(root):
            raise AssertionError("baseline Lane 01 Windows note fixture should pass")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{WINDOWS_NOTE}\n", "", 1))
        failures = collect_failures(root)
        expected = [f"missing:{WINDOWS_NOTE}"]
        if failures != expected:
            raise AssertionError(
                f"unexpected failures for missing Windows note case: {failures}"
            )
        write_sample_root(root)
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Rules\n", "", 1))
        failures = collect_failures(root)
        expected = [f"missing:{RULES_HEADING}"]
        if failures != expected:
            raise AssertionError(
                f"unexpected failures for missing Rules heading case: {failures}"
            )
        write_sample_root(root)
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Active product surfaces\n", "", 1))
        failures = collect_failures(root)
        expected = [f"missing:{ACTIVE_PRODUCT_SURFACES_HEADING}"]
        if failures != expected:
            raise AssertionError(
                "unexpected failures for missing Active product surfaces heading case: "
                f"{failures}"
            )
        write_sample_root(root)
        case_count += 1

        readme = _sample_readme()
        without_note = readme.replace(f"{WINDOWS_NOTE}\n", "", 1)
        reordered = without_note
        reordered = reordered.replace(
            "\nActive product surfaces\n",
            "\nActive product surfaces\n" + WINDOWS_NOTE + "\n",
            1,
        )
        _write(root / README_PATH, reordered)
        failures = collect_failures(root)
        expected = ["order:windows note appears after Active product surfaces"]
        if failures != expected:
            raise AssertionError(
                f"unexpected failures for reordered Windows note case: {failures}"
            )
        case_count += 1

    print("LANE01_BOOTSTRAP_README_WINDOWS_NOTE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_README_WINDOWS_NOTE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the landed Lane 01 bootstrap README keeps the Windows note."
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
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root for focused local validation",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"Wrote sample root to {args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"LANE01_BOOTSTRAP_README_WINDOWS_NOTE_FAILURE={failure}")
        return 1

    print("Lane 01 bootstrap README Windows note check passed.")
    print("LANE01_BOOTSTRAP_README_WINDOWS_NOTE=pass")
    print("LANE01_BOOTSTRAP_README_WINDOWS_NOTE_COUNT=1")
    print(
        "LANE01_BOOTSTRAP_README_WINDOWS_NOTE_SECTION_ORDER="
        "Rules->WindowsNote->ActiveProductSurfaces"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

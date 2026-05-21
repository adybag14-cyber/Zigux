#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")

EXPECTED_HEADING = "# zigux-alpha"
EXPECTED_IDENTITY = "`zigux-alpha` is the Zigux bootstrap workspace."
EXPECTED_NEXT_HEADING = "It exists to hold:"


def _read_nonempty_lines(root: Path) -> list[str]:
    return [line for line in (root / README_PATH).read_text(encoding="utf-8").splitlines() if line]


def check_readme_identity(root: Path) -> list[str]:
    lines = _read_nonempty_lines(root)
    problems: list[str] = []

    if not lines:
        return ["missing_readme_content"]

    if lines[0] != EXPECTED_HEADING:
        if EXPECTED_HEADING not in lines:
            problems.append(f"missing_heading:{EXPECTED_HEADING}")
        else:
            problems.append(f"misordered_heading:{EXPECTED_HEADING}")

    if EXPECTED_IDENTITY not in lines:
        problems.append(f"missing_identity_sentence:{EXPECTED_IDENTITY}")
    elif lines.index(EXPECTED_IDENTITY) != 1:
        problems.append(
            f"misordered_identity_sentence:{EXPECTED_IDENTITY}:found_at={lines.index(EXPECTED_IDENTITY) + 1}:expected_at=2"
        )

    if EXPECTED_NEXT_HEADING not in lines:
        problems.append(f"missing_next_heading:{EXPECTED_NEXT_HEADING}")
    elif lines.index(EXPECTED_NEXT_HEADING) != 2:
        problems.append(
            f"misordered_next_heading:{EXPECTED_NEXT_HEADING}:found_at={lines.index(EXPECTED_NEXT_HEADING) + 1}:expected_at=3"
        )

    return problems


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    return f"""\\
{EXPECTED_HEADING}

{EXPECTED_IDENTITY}

{EXPECTED_NEXT_HEADING}
- program-level planning
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_readme_identity_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        if check_readme_identity(root):
            raise AssertionError("baseline README identity packet should pass")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{EXPECTED_HEADING}\n\n", "", 1))
        problems = check_readme_identity(root)
        expected = [
            f"missing_heading:{EXPECTED_HEADING}",
            f"misordered_identity_sentence:{EXPECTED_IDENTITY}:found_at=1:expected_at=2",
            f"misordered_next_heading:{EXPECTED_NEXT_HEADING}:found_at=2:expected_at=3",
        ]
        if problems != expected:
            raise AssertionError(f"unexpected missing heading result: {problems}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(EXPECTED_HEADING, "# zigux beta", 1))
        problems = check_readme_identity(root)
        expected = [f"missing_heading:{EXPECTED_HEADING}"]
        if problems != expected:
            raise AssertionError(f"unexpected wrong heading result: {problems}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{EXPECTED_IDENTITY}\n\n", "", 1))
        problems = check_readme_identity(root)
        expected = [
            f"missing_identity_sentence:{EXPECTED_IDENTITY}",
            f"misordered_next_heading:{EXPECTED_NEXT_HEADING}:found_at=2:expected_at=3",
        ]
        if problems != expected:
            raise AssertionError(f"unexpected missing identity result: {problems}")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                EXPECTED_IDENTITY,
                "`zigux-alpha` is the permanent Zigux product tree.",
                1,
            ),
        )
        problems = check_readme_identity(root)
        expected = [f"missing_identity_sentence:{EXPECTED_IDENTITY}"]
        if problems != expected:
            raise AssertionError(f"unexpected wrong identity result: {problems}")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{EXPECTED_NEXT_HEADING}\n", "", 1))
        problems = check_readme_identity(root)
        expected = [f"missing_next_heading:{EXPECTED_NEXT_HEADING}"]
        if problems != expected:
            raise AssertionError(f"unexpected missing next heading result: {problems}")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                f"{EXPECTED_IDENTITY}\n\n{EXPECTED_NEXT_HEADING}",
                f"{EXPECTED_NEXT_HEADING}\n\n{EXPECTED_IDENTITY}",
                1,
            ),
        )
        problems = check_readme_identity(root)
        expected = [
            f"misordered_identity_sentence:{EXPECTED_IDENTITY}:found_at=3:expected_at=2",
            f"misordered_next_heading:{EXPECTED_NEXT_HEADING}:found_at=2:expected_at=3",
        ]
        if problems != expected:
            raise AssertionError(f"unexpected swapped order result: {problems}")
        case_count += 1

    print("LANE01_BOOTSTRAP_README_IDENTITY_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_README_IDENTITY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the top Lane 01 zigux-alpha README identity packet stays intact."
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
        help="exercise the checker against synthetic README fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    problems = check_readme_identity(args.root)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1

    print("Lane 01 bootstrap README identity check passed.")
    print("LANE01_BOOTSTRAP_README_IDENTITY_REQUIRED_LINE_COUNT=3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")

EXPECTED_PURPOSE_BULLETS = (
    "program-level planning",
    "source maps",
    "phase ledgers",
    "validation and porting rules",
    "first-commit sequencing for the Zigux product buildout",
)

PURPOSE_HEADING = "It exists to hold:"
BOUNDARY_SENTENCE = "It does not exist to become a permanent parallel subsystem tree."
NEXT_SECTION_HEADING = "Rules"


def read_workspace_purpose(root: Path) -> tuple[list[str], str]:
    lines = (root / README_PATH).read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(PURPOSE_HEADING)
    except ValueError as exc:
        raise AssertionError("missing workspace-purpose heading") from exc

    try:
        end = lines.index(NEXT_SECTION_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError("missing Rules heading") from exc

    if end <= start + 1:
        raise AssertionError("workspace-purpose section is empty")

    section_lines = [line for line in lines[start + 1 : end] if line]
    if not section_lines:
        raise AssertionError("workspace-purpose section is empty")

    boundary_sentence = section_lines[-1]
    bullets: list[str] = []
    for line in section_lines[:-1]:
        if not line.startswith("- "):
            raise AssertionError(f"unexpected non-bullet line in workspace-purpose section: {line}")
        bullets.append(line[2:])

    return bullets, boundary_sentence


def check_workspace_purpose(root: Path) -> list[str]:
    try:
        actual_bullets, boundary_sentence = read_workspace_purpose(root)
    except AssertionError as exc:
        return [str(exc)]

    problems: list[str] = []
    if actual_bullets != list(EXPECTED_PURPOSE_BULLETS):
        for index, expected in enumerate(EXPECTED_PURPOSE_BULLETS):
            if index >= len(actual_bullets):
                problems.append(f"missing_purpose_bullet:{expected}")
                continue
            if actual_bullets[index] != expected:
                if expected not in actual_bullets:
                    problems.append(f"missing_purpose_bullet:{expected}")
                else:
                    problems.append(
                        "misordered_purpose_bullet:"
                        f"{expected}:found_at={actual_bullets.index(expected) + 1}:expected_at={index + 1}"
                    )
        if len(actual_bullets) > len(EXPECTED_PURPOSE_BULLETS):
            for extra in actual_bullets[len(EXPECTED_PURPOSE_BULLETS) :]:
                problems.append(f"unexpected_purpose_bullet:{extra}")

    if boundary_sentence != BOUNDARY_SENTENCE:
        if boundary_sentence.startswith("- "):
            problems.append(f"missing_boundary_sentence:{BOUNDARY_SENTENCE}")
            problems.append(f"unexpected_purpose_bullet:{boundary_sentence[2:]}")
        elif boundary_sentence != BOUNDARY_SENTENCE:
            problems.append(f"wrong_boundary_sentence:{boundary_sentence}")

    return problems


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    bullets = "\n".join(f"- {bullet}" for bullet in EXPECTED_PURPOSE_BULLETS)
    return f"""# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

{PURPOSE_HEADING}
{bullets}

{BOUNDARY_SENTENCE}

{NEXT_SECTION_HEADING}
- Keep product planning and bootstrap artifacts here first.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_workspace_purpose_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        if check_workspace_purpose(root):
            raise AssertionError("baseline workspace-purpose packet should pass")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{PURPOSE_HEADING}\n", "", 1))
        if check_workspace_purpose(root) != ["missing workspace-purpose heading"]:
            raise AssertionError("missing workspace-purpose heading case failed")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace(f"{NEXT_SECTION_HEADING}\n", "", 1))
        if check_workspace_purpose(root) != ["missing Rules heading"]:
            raise AssertionError("missing Rules heading case failed")
        case_count += 1

        reordered_bullets = list(EXPECTED_PURPOSE_BULLETS)
        reordered_bullets[1], reordered_bullets[2] = reordered_bullets[2], reordered_bullets[1]
        _write(
            root / README_PATH,
            _sample_readme().replace(
                "\n".join(f"- {bullet}" for bullet in EXPECTED_PURPOSE_BULLETS),
                "\n".join(f"- {bullet}" for bullet in reordered_bullets),
                1,
            ),
        )
        problems = check_workspace_purpose(root)
        expected = [
            "misordered_purpose_bullet:source maps:found_at=3:expected_at=2",
            "misordered_purpose_bullet:phase ledgers:found_at=2:expected_at=3",
        ]
        if problems != expected:
            raise AssertionError(f"unexpected reorder result: {problems}")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- first-commit sequencing for the Zigux product buildout\n",
                "",
                1,
            ),
        )
        problems = check_workspace_purpose(root)
        expected = ["missing_purpose_bullet:first-commit sequencing for the Zigux product buildout"]
        if problems != expected:
            raise AssertionError(f"unexpected missing bullet result: {problems}")
        case_count += 1

        extra_bullet = (
            "- bootstrap-only staging for README navigation packets\n\n"
            f"{BOUNDARY_SENTENCE}\n"
        )
        _write(
            root / README_PATH,
            _sample_readme().replace(f"\n{BOUNDARY_SENTENCE}\n", f"\n{extra_bullet}", 1),
        )
        problems = check_workspace_purpose(root)
        expected = ["unexpected_purpose_bullet:bootstrap-only staging for README navigation packets"]
        if problems != expected:
            raise AssertionError(f"unexpected extra bullet result: {problems}")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                BOUNDARY_SENTENCE,
                "It does not exist to become a permanent product subtree.",
                1,
            ),
        )
        problems = check_workspace_purpose(root)
        expected = ["wrong_boundary_sentence:It does not exist to become a permanent product subtree."]
        if problems != expected:
            raise AssertionError(f"unexpected boundary sentence result: {problems}")
        case_count += 1

    print("LANE01_BOOTSTRAP_WORKSPACE_PURPOSE_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_WORKSPACE_PURPOSE_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 zigux-alpha README workspace-purpose packet stays intact."
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

    problems = check_workspace_purpose(args.root)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1

    print("Lane 01 bootstrap workspace-purpose check passed.")
    print(f"LANE01_BOOTSTRAP_WORKSPACE_PURPOSE_COUNT={len(EXPECTED_PURPOSE_BULLETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

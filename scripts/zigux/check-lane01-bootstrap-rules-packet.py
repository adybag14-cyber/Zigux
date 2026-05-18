#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

README_PATH = Path("zigux-alpha/README.md")

EXPECTED_RULES = (
    "Keep product planning and bootstrap artifacts here first.",
    "Use the roadmap and bootstrap commit ledger together when choosing the next bootstrap lane.",
    "The bootstrap commit ledger currently records the bounded early commit train through the broadened Phase 2 tranche, so confirm later-lane state in the live product docs, current repo tree, and active lane notes before using it as a sole source of truth.",
    "Move actual product code into the native Linux locations or the small `zigux/` support root once a slice is approved.",
    "Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.",
    "Treat ZAR as the research and proving repo and Zigux as the product repo.",
    "On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.",
)

RULES_HEADING = "Rules"
NEXT_SECTION_HEADING = "Active product surfaces"


def read_rules_block(root: Path) -> list[str]:
    lines = (root / README_PATH).read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(RULES_HEADING)
    except ValueError as exc:
        raise AssertionError("missing Rules heading") from exc

    try:
        end = lines.index(NEXT_SECTION_HEADING, start + 1)
    except ValueError as exc:
        raise AssertionError("missing Active product surfaces heading") from exc

    rules: list[str] = []
    for line in lines[start + 1 : end]:
        if not line:
            continue
        if not line.startswith("- "):
            raise AssertionError(f"unexpected non-bullet line in Rules section: {line}")
        rules.append(line[2:])
    return rules


def check_rules_packet(root: Path) -> list[str]:
    try:
        actual = read_rules_block(root)
    except AssertionError as exc:
        return [str(exc)]

    problems: list[str] = []
    if actual != list(EXPECTED_RULES):
        for index, expected in enumerate(EXPECTED_RULES):
            if index >= len(actual):
                problems.append(f"missing_rule:{expected}")
                continue
            if actual[index] != expected:
                if expected not in actual:
                    problems.append(f"missing_rule:{expected}")
                else:
                    problems.append(
                        f"misordered_rule:{expected}:found_at={actual.index(expected) + 1}:expected_at={index + 1}"
                    )
        if len(actual) > len(EXPECTED_RULES):
            for extra in actual[len(EXPECTED_RULES) :]:
                problems.append(f"unexpected_rule:{extra}")
    return problems


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_readme() -> str:
    rules = "\n".join(f"- {rule}" for rule in EXPECTED_RULES)
    return f"""# zigux-alpha

`zigux-alpha` is the Zigux bootstrap workspace.

Rules
{rules}

Active product surfaces
- `Documentation/zigux/README.md` is the live product documentation root once a slice has moved beyond bootstrap planning.
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_rules_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / README_PATH, _sample_readme())

        if check_rules_packet(root):
            raise AssertionError("baseline Rules packet should pass")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Rules\n", "", 1))
        if check_rules_packet(root) != ["missing Rules heading"]:
            raise AssertionError("missing Rules heading case failed")
        case_count += 1

        _write(root / README_PATH, _sample_readme().replace("Active product surfaces\n", "", 1))
        if check_rules_packet(root) != ["missing Active product surfaces heading"]:
            raise AssertionError("missing next heading case failed")
        case_count += 1

        reordered_rules = list(EXPECTED_RULES)
        reordered_rules[4], reordered_rules[5] = reordered_rules[5], reordered_rules[4]
        _write(
            root / README_PATH,
            _sample_readme().replace(
                "\n".join(f"- {rule}" for rule in EXPECTED_RULES),
                "\n".join(f"- {rule}" for rule in reordered_rules),
                1,
            ),
        )
        problems = check_rules_packet(root)
        expected = [
            "misordered_rule:Do not create `zigux-alpha/ports/` or any mirror-tree equivalent.:found_at=6:expected_at=5",
            "misordered_rule:Treat ZAR as the research and proving repo and Zigux as the product repo.:found_at=5:expected_at=6",
        ]
        if problems != expected:
            raise AssertionError(f"unexpected reorder result: {problems}")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "- On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo.\n",
                "",
                1,
            ),
        )
        problems = check_rules_packet(root)
        expected = [
            "missing_rule:On Windows, use a case-sensitive repo directory or a Linux filesystem for this repo."
        ]
        if problems != expected:
            raise AssertionError(f"unexpected missing Windows rule result: {problems}")
        case_count += 1

        _write(
            root / README_PATH,
            _sample_readme().replace(
                "Treat ZAR as the research and proving repo and Zigux as the product repo.",
                "Treat ZAR as the proving repo and Zigux as the product repo.",
                1,
            ),
        )
        problems = check_rules_packet(root)
        expected = [
            "missing_rule:Treat ZAR as the research and proving repo and Zigux as the product repo."
        ]
        if problems != expected:
            raise AssertionError(f"unexpected repo-role rule result: {problems}")
        case_count += 1

        extra_rule = (
            "- Treat bootstrap planning notes as the final product documentation root.\n"
            "Active product surfaces\n"
        )
        _write(
            root / README_PATH,
            _sample_readme().replace("Active product surfaces\n", extra_rule, 1),
        )
        problems = check_rules_packet(root)
        expected = [
            "unexpected_rule:Treat bootstrap planning notes as the final product documentation root."
        ]
        if problems != expected:
            raise AssertionError(f"unexpected extra rule result: {problems}")
        case_count += 1

    print("LANE01_BOOTSTRAP_RULES_PACKET_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_RULES_PACKET_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 zigux-alpha README Rules packet stays intact."
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

    problems = check_rules_packet(args.root)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        return 1

    print("Lane 01 bootstrap Rules packet check passed.")
    print(f"LANE01_BOOTSTRAP_RULE_COUNT={len(EXPECTED_RULES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

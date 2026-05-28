#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")

NORMALIZATION_HEADING = "## Bundle Normalization Notes"
LICENSING_HEADING = "## Licensing and Reuse Policy"
RULES_HEADING = "## Non-Negotiable Product Rules"

REQUIRED_LINES = (
    "For Zigux product work, licensing is not the blocker.",
    "Working rule for this repo:",
    "- direct copies from same-license Zigux or ZAR material are allowed when legally valid and reviewable",
    "- machine translations or human translations from Linux C into Zig are allowed when legally valid and reviewable",
    "- adaptations from Linux, ZAR, or other same-license material are allowed when legally valid and reviewable",
    "That does not remove engineering discipline.",
    "Even when copying or translating is legally allowed, the product still requires:",
    "- bounded scope",
    "- explicit ownership",
    "- parity and validation gates",
    "- rollback paths",
    "- maintainable placement in the Linux-owned tree",
    "Legal permission expands the implementation options.",
    "It does not justify mirror-tree sprawl, unclear ownership, or skipping validation.",
)


def read_text(root: Path) -> str:
    return (root / ROADMAP_PATH).read_text(encoding="utf-8")


def extract_section(text: str, heading: str, next_heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    end = text.find(next_heading, start + len(heading))
    if end == -1:
        return text[start:]
    return text[start:end]


def collect_failures(root: Path) -> list[str]:
    text = read_text(root)
    failures: list[str] = []

    normalization_index = text.find(NORMALIZATION_HEADING)
    licensing_index = text.find(LICENSING_HEADING)
    rules_index = text.find(RULES_HEADING)

    if normalization_index == -1:
        failures.append(f"missing-heading:{NORMALIZATION_HEADING}")
    if licensing_index == -1:
        failures.append(f"missing-heading:{LICENSING_HEADING}")
    if rules_index == -1:
        failures.append(f"missing-heading:{RULES_HEADING}")

    if (
        normalization_index != -1
        and licensing_index != -1
        and rules_index != -1
        and not (normalization_index < licensing_index < rules_index)
    ):
        failures.append(
            f"wrong-order:{NORMALIZATION_HEADING}->{LICENSING_HEADING}->{RULES_HEADING}"
        )

    section = extract_section(text, LICENSING_HEADING, RULES_HEADING)
    if section:
        for line in REQUIRED_LINES:
            if line not in section:
                failures.append(f"missing-line:{line}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_roadmap() -> str:
    required = "\n".join(REQUIRED_LINES)
    return (
        "# ZAR to Zigux Product Roadmap\n\n"
        "## Bundle Normalization Notes\n\n"
        "Normalized counts live here.\n\n"
        "## Licensing and Reuse Policy\n\n"
        f"{required}\n\n"
        "## Non-Negotiable Product Rules\n\n"
        "1. No flag-day rewrite.\n"
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_lane01_licensing_") as tmp_dir:
        root = Path(tmp_dir)
        roadmap = root / ROADMAP_PATH

        _write(roadmap, _sample_roadmap())
        if collect_failures(root):
            raise AssertionError("baseline licensing fixture should pass")
        case_count += 1

        _write(roadmap, _sample_roadmap().replace("## Licensing and Reuse Policy\n\n", "", 1))
        failures = collect_failures(root)
        expected = [f"missing-heading:{LICENSING_HEADING}"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for missing heading: {failures}")
        case_count += 1

        _write(
            roadmap,
            _sample_roadmap().replace(
                "- machine translations or human translations from Linux C into Zig are allowed when legally valid and reviewable\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing-line:- machine translations or human translations from Linux C into Zig are allowed when legally valid and reviewable"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected failures for missing translation rule: {failures}")
        case_count += 1

        _write(
            roadmap,
            _sample_roadmap().replace(
                "- parity and validation gates\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = ["missing-line:- parity and validation gates"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for missing validation gate: {failures}")
        case_count += 1

        _write(
            roadmap,
            _sample_roadmap().replace(
                "It does not justify mirror-tree sprawl, unclear ownership, or skipping validation.\n",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "missing-line:It does not justify mirror-tree sprawl, unclear ownership, or skipping validation."
        ]
        if failures != expected:
            raise AssertionError(f"unexpected failures for missing closeout line: {failures}")
        case_count += 1

        _write(
            roadmap,
            _sample_roadmap().replace(
                "## Bundle Normalization Notes\n\n"
                "Normalized counts live here.\n\n"
                "## Licensing and Reuse Policy\n\n",
                "## Licensing and Reuse Policy\n\n"
                + "\n".join(REQUIRED_LINES)
                + "\n\n## Bundle Normalization Notes\n\nNormalized counts live here.\n\n",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            f"wrong-order:{NORMALIZATION_HEADING}->{LICENSING_HEADING}->{RULES_HEADING}"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected failures for wrong order: {failures}")
        case_count += 1

        _write(roadmap, _sample_roadmap().replace("## Non-Negotiable Product Rules\n\n", "", 1))
        failures = collect_failures(root)
        expected = [f"missing-heading:{RULES_HEADING}"]
        if failures != expected:
            raise AssertionError(f"unexpected failures for missing next heading: {failures}")
        case_count += 1

    print("LANE01_BOOTSTRAP_ROADMAP_LICENSING_SELF_TEST=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_LICENSING_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Lane 01 roadmap licensing packet remains intact."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic licensing fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("LANE01_BOOTSTRAP_ROADMAP_LICENSING=pass")
    print(f"LANE01_BOOTSTRAP_ROADMAP_LICENSING_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

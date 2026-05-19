#!/usr/bin/env python3
"""Guard the Lane 01 roadmap licensing and reuse policy packet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROADMAP_PATH = Path("zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md")
PASS_LABEL = "LANE01_BOOTSTRAP_ROADMAP_LICENSING=pass"
SELF_TEST_LABEL = "LANE01_BOOTSTRAP_ROADMAP_LICENSING_SELF_TEST=pass"

REQUIRED_LINES = [
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
]


class CheckFailure(Exception):
    pass


def fail(message: str) -> None:
    raise CheckFailure(message)


def require(text: str, needle: str) -> None:
    if needle not in text:
        fail(f"MISSING_REQUIRED_LINE={needle}")


def require_heading_order(text: str) -> None:
    headings = [
        "## Bundle Normalization Notes",
        "## Licensing and Reuse Policy",
        "## Non-Negotiable Product Rules",
    ]
    positions = []
    for heading in headings:
        index = text.find(heading)
        if index == -1:
            fail(f"MISSING_HEADING={heading}")
        positions.append(index)
    if positions != sorted(positions):
        fail("LICENSING_SECTION_ORDER_INVALID")


def check(root: Path) -> None:
    roadmap = root / ROADMAP_PATH
    if not roadmap.is_file():
        fail(f"MISSING_FILE={ROADMAP_PATH}")
    text = roadmap.read_text(encoding="utf-8")
    require_heading_order(text)
    for line in REQUIRED_LINES:
        require(text, line)
    print(PASS_LABEL)
    print(
        f"LANE01_BOOTSTRAP_ROADMAP_LICENSING_REQUIRED_LINE_COUNT={len(REQUIRED_LINES)}"
    )


def run_self_test() -> None:
    base = """# ZAR to Zigux Product Roadmap

## Bundle Normalization Notes

The workbook and CSV corpus are directionally aligned, but the workbook executive summary contains stale aggregate counts.

## Licensing and Reuse Policy

For Zigux product work, licensing is not the blocker.

Working rule for this repo:
- direct copies from same-license Zigux or ZAR material are allowed when legally valid and reviewable
- machine translations or human translations from Linux C into Zig are allowed when legally valid and reviewable
- adaptations from Linux, ZAR, or other same-license material are allowed when legally valid and reviewable

That does not remove engineering discipline.

Even when copying or translating is legally allowed, the product still requires:
- bounded scope
- explicit ownership
- parity and validation gates
- rollback paths
- maintainable placement in the Linux-owned tree

Legal permission expands the implementation options.
It does not justify mirror-tree sprawl, unclear ownership, or skipping validation.

## Non-Negotiable Product Rules
"""
    failing_cases = {
        "missing_heading": base.replace("## Licensing and Reuse Policy\n\n", ""),
        "missing_rule_intro": base.replace("Working rule for this repo:\n", ""),
        "missing_translation_rule": base.replace(
            "- machine translations or human translations from Linux C into Zig are allowed when legally valid and reviewable\n",
            "",
        ),
        "missing_gate": base.replace("- parity and validation gates\n", ""),
        "missing_close": base.replace(
            "It does not justify mirror-tree sprawl, unclear ownership, or skipping validation.\n",
            "",
        ),
        "bad_order": base.replace(
            "## Bundle Normalization Notes\n\nThe workbook and CSV corpus are directionally aligned, but the workbook executive summary contains stale aggregate counts.\n\n## Licensing and Reuse Policy\n\n",
            "## Licensing and Reuse Policy\n\n",
        )
        + "\n## Bundle Normalization Notes\n",
    }

    cases_run = 1
    test_root = Path("/tmp/lane01_licensing_self_test")
    test_root.mkdir(parents=True, exist_ok=True)
    roadmap = test_root / ROADMAP_PATH
    roadmap.parent.mkdir(parents=True, exist_ok=True)
    roadmap.write_text(base, encoding="utf-8")
    check(test_root)

    for name, content in failing_cases.items():
        cases_run += 1
        roadmap.write_text(content, encoding="utf-8")
        try:
            check(test_root)
        except CheckFailure:
            pass
        else:
            fail(f"SELF_TEST_CASE_DID_NOT_FAIL={name}")

    print(SELF_TEST_LABEL)
    print(f"LANE01_BOOTSTRAP_ROADMAP_LICENSING_SELF_TEST_CASES={cases_run}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    try:
        check(args.root)
    except CheckFailure as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

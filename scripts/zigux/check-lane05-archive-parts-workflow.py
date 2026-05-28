#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap-archive-parts-packet.yml")

REQUIRED_LINES = [
    ("branches: [ master ]", "master push trigger"),
    ("- 'scripts/zigux/check-lane05-archive-parts-workflow.py'", "workflow checker path"),
    ("- 'scripts/zigux/check-lane05-archive-parts-packet.py'", "packet checker path"),
    ("- 'scripts/zigux/stage-pinned-zig-archive.py'", "stage helper path"),
    ("- 'scripts/zigux/zig-toolchain-policy.json'", "policy path"),
    ("- 'third_party/**'", "third-party path"),
    ("- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'", "workflow path"),
    ("contents: read", "contents permission"),
    ("- name: Checkout workspace snapshot", "checkout step"),
    ("- name: Setup Python", "python setup step"),
    ("- name: Compile current Lane 05 archive-parts workflow scripts", "compile step"),
    (
        "run: python3 -m py_compile scripts/zigux/check-zig-toolchain.py "
        "scripts/zigux/check-lane05-archive-parts-packet.py "
        "scripts/zigux/stage-pinned-zig-archive.py "
        "scripts/zigux/check-lane05-archive-parts-workflow.py",
        "compile command",
    ),
    (
        "- name: Self-test current Lane 05 archive-parts workflow checker",
        "workflow checker self-test step",
    ),
    (
        "run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test",
        "workflow checker self-test command",
    ),
    ("- name: Check current Lane 05 archive-parts workflow packet", "workflow checker step"),
    (
        "run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py",
        "workflow checker command",
    ),
    (
        "- name: Self-test current Lane 05 archive parts packet checker",
        "packet checker self-test step",
    ),
    (
        "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test",
        "packet checker self-test command",
    ),
    ("- name: Check current Lane 05 archive parts packet", "packet check step"),
    (
        "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing",
        "packet check command",
    ),
]

REQUIRED_ORDER = [
    "- 'scripts/zigux/check-lane05-archive-parts-workflow.py'",
    "- 'scripts/zigux/check-lane05-archive-parts-packet.py'",
    "- 'scripts/zigux/stage-pinned-zig-archive.py'",
    "- 'scripts/zigux/zig-toolchain-policy.json'",
    "- 'third_party/**'",
    "- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'",
    "- name: Checkout workspace snapshot",
    "- name: Setup Python",
    "- name: Compile current Lane 05 archive-parts workflow scripts",
    "- name: Self-test current Lane 05 archive-parts workflow checker",
    "- name: Check current Lane 05 archive-parts workflow packet",
    "- name: Self-test current Lane 05 archive parts packet checker",
    "- name: Check current Lane 05 archive parts packet",
]


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 archive-parts workflow checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def check_order(text: str) -> None:
    previous_marker = REQUIRED_ORDER[0]
    previous_index = text.find(previous_marker)
    if previous_index == -1:
        raise SystemExit(f"lane05 archive-parts workflow checker missing ordered marker: {previous_marker}")
    for marker in REQUIRED_ORDER[1:]:
        marker_index = text.find(marker)
        if marker_index == -1:
            raise SystemExit(f"lane05 archive-parts workflow checker missing ordered marker: {marker}")
        if marker_index <= previous_index:
            raise SystemExit(
                "lane05 archive-parts workflow checker expected ordered marker "
                f"`{previous_marker}` before `{marker}`"
            )
        previous_marker = marker
        previous_index = marker_index


def check_workflow(text: str) -> None:
    if "name: zigux-bootstrap-archive-parts-packet" not in text:
        raise SystemExit("lane05 archive-parts workflow checker missing workflow name")
    for line, label in REQUIRED_LINES:
        require_exact_line(text, line, label)
    check_order(text)


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap-archive-parts-packet

on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'scripts/zigux/check-lane05-archive-parts-workflow.py'
      - 'scripts/zigux/check-lane05-archive-parts-packet.py'
      - 'scripts/zigux/stage-pinned-zig-archive.py'
      - 'scripts/zigux/zig-toolchain-policy.json'
      - 'third_party/**'
      - '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  lane05-archive-parts-packet:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout workspace snapshot
        run: true

      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'

      - name: Compile current Lane 05 archive-parts workflow scripts
        run: python3 -m py_compile scripts/zigux/check-zig-toolchain.py scripts/zigux/check-lane05-archive-parts-packet.py scripts/zigux/stage-pinned-zig-archive.py scripts/zigux/check-lane05-archive-parts-workflow.py

      - name: Self-test current Lane 05 archive-parts workflow checker
        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test

      - name: Check current Lane 05 archive-parts workflow packet
        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py

      - name: Self-test current Lane 05 archive parts packet checker
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test

      - name: Check current Lane 05 archive parts packet
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing
"""
    check_workflow(good_workflow)
    case_count = 1

    missing_stage_path = good_workflow.replace(
        "      - 'scripts/zigux/stage-pinned-zig-archive.py'\n", "", 1
    )
    try:
        check_workflow(missing_stage_path)
    except SystemExit as exc:
        assert "stage helper path" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing stage helper path to fail")

    missing_stage_compile = good_workflow.replace(
        " scripts/zigux/stage-pinned-zig-archive.py", "", 1
    )
    try:
        check_workflow(missing_stage_compile)
    except SystemExit as exc:
        assert "compile command" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing stage helper compile command to fail")

    duplicated_permission = good_workflow + "permissions:\n  contents: read\n"
    try:
        check_workflow(duplicated_permission)
    except SystemExit as exc:
        assert "contents permission" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate permission line to fail")

    reordered_paths = good_workflow.replace(
        "      - 'scripts/zigux/check-lane05-archive-parts-packet.py'\n"
        "      - 'scripts/zigux/stage-pinned-zig-archive.py'\n",
        "      - 'scripts/zigux/stage-pinned-zig-archive.py'\n"
        "      - 'scripts/zigux/check-lane05-archive-parts-packet.py'\n",
        1,
    )
    try:
        check_workflow(reordered_paths)
    except SystemExit as exc:
        assert "ordered marker" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered paths to fail")

    reordered_steps = good_workflow.replace(
        "      - name: Check current Lane 05 archive-parts workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py\n\n"
        "      - name: Self-test current Lane 05 archive parts packet checker\n",
        "      - name: Self-test current Lane 05 archive parts packet checker\n"
        "      - name: Check current Lane 05 archive-parts workflow packet\n"
        "        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py\n\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "ordered marker" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered steps to fail")

    print("LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_ARCHIVE_PARTS_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 archive-parts workflow keeps its expected guard steps."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap-archive-parts-packet.yml",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_workflow(args.workflow.read_text(encoding="utf-8"))
    print("LANE05_ARCHIVE_PARTS_WORKFLOW=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())

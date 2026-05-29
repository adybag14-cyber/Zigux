#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap-archive-parts-packet.yml")

WORKFLOW_NAME = "name: zigux-bootstrap-archive-parts-packet"
PUSH_BRANCH = "branches: [ master ]"
CHECKER_PATH = "- 'scripts/zigux/check-lane05-archive-parts-workflow.py'"
PACKET_CHECKER_PATH = "- 'scripts/zigux/check-lane05-archive-parts-packet.py'"
TEXT_CEILING_CHECKER_PATH = "- 'scripts/zigux/check-lane05-archive-parts-text-ceiling.py'"
POLICY_PATH = "- 'scripts/zigux/zig-toolchain-policy.json'"
THIRD_PARTY_PATH = "- 'third_party/**'"
WORKFLOW_PATH_FILTER = "- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'"
PERMISSIONS = "contents: read"
CHECKOUT_STEP = "- name: Checkout workspace snapshot"
SETUP_PYTHON_STEP = "- name: Setup Python"
COMPILE_STEP = "- name: Compile current Lane 05 archive-parts workflow scripts"
COMPILE_CMD = (
    "python3 -m py_compile "
    "scripts/zigux/check-zig-toolchain.py "
    "scripts/zigux/check-lane05-archive-parts-packet.py "
    "scripts/zigux/check-lane05-archive-parts-text-ceiling.py "
    "scripts/zigux/check-lane05-archive-parts-workflow.py"
)
WORKFLOW_CHECKER_SELF_TEST_STEP = "- name: Self-test current Lane 05 archive-parts workflow checker"
WORKFLOW_CHECKER_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test"
WORKFLOW_CHECKER_STEP = "- name: Check current Lane 05 archive-parts workflow packet"
WORKFLOW_CHECKER_CMD = "python3 scripts/zigux/check-lane05-archive-parts-workflow.py"
PACKET_SELF_TEST_STEP = "- name: Self-test current Lane 05 archive parts packet checker"
PACKET_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test"
PACKET_CHECK_STEP = "- name: Check current Lane 05 archive parts packet"
PACKET_CHECK_CMD = "python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing"
TEXT_CEILING_SELF_TEST_STEP = "- name: Self-test current Lane 05 archive parts text ceiling checker"
TEXT_CEILING_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-archive-parts-text-ceiling.py --self-test"
TEXT_CEILING_CHECK_STEP = "- name: Check current Lane 05 archive parts text ceiling"
TEXT_CEILING_CHECK_CMD = "python3 scripts/zigux/check-lane05-archive-parts-text-ceiling.py --allow-missing"


REQUIRED_MARKERS = (
    (WORKFLOW_NAME, "workflow name"),
    (PUSH_BRANCH, "master push trigger"),
    (CHECKER_PATH, "workflow checker path filter"),
    (PACKET_CHECKER_PATH, "packet checker path filter"),
    (TEXT_CEILING_CHECKER_PATH, "text ceiling checker path filter"),
    (POLICY_PATH, "policy path filter"),
    (THIRD_PARTY_PATH, "third-party path filter"),
    (WORKFLOW_PATH_FILTER, "workflow path filter"),
    (PERMISSIONS, "contents permission"),
    (CHECKOUT_STEP, "checkout step"),
    (SETUP_PYTHON_STEP, "python setup step"),
    (COMPILE_STEP, "compile step"),
    (COMPILE_CMD, "compile command"),
    (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
    (WORKFLOW_CHECKER_SELF_TEST_CMD, "workflow checker self-test command"),
    (WORKFLOW_CHECKER_STEP, "workflow checker step"),
    (WORKFLOW_CHECKER_CMD, "workflow checker command"),
    (PACKET_SELF_TEST_STEP, "packet checker self-test step"),
    (PACKET_SELF_TEST_CMD, "packet checker self-test command"),
    (PACKET_CHECK_STEP, "packet check step"),
    (PACKET_CHECK_CMD, "packet check command"),
    (TEXT_CEILING_SELF_TEST_STEP, "text ceiling checker self-test step"),
    (TEXT_CEILING_SELF_TEST_CMD, "text ceiling checker self-test command"),
    (TEXT_CEILING_CHECK_STEP, "text ceiling check step"),
    (TEXT_CEILING_CHECK_CMD, "text ceiling check command"),
)

EXACT_LINES = (
    (PUSH_BRANCH, "master push trigger"),
    (CHECKER_PATH, "workflow checker path filter"),
    (PACKET_CHECKER_PATH, "packet checker path filter"),
    (TEXT_CEILING_CHECKER_PATH, "text ceiling checker path filter"),
    (POLICY_PATH, "policy path filter"),
    (THIRD_PARTY_PATH, "third-party path filter"),
    (WORKFLOW_PATH_FILTER, "workflow path filter"),
    (PERMISSIONS, "contents permission"),
    (f"run: {COMPILE_CMD}", "compile command"),
    (f"run: {WORKFLOW_CHECKER_SELF_TEST_CMD}", "workflow checker self-test command"),
    (f"run: {WORKFLOW_CHECKER_CMD}", "workflow checker command"),
    (f"run: {PACKET_SELF_TEST_CMD}", "packet checker self-test command"),
    (f"run: {PACKET_CHECK_CMD}", "packet check command"),
    (f"run: {TEXT_CEILING_SELF_TEST_CMD}", "text ceiling checker self-test command"),
    (f"run: {TEXT_CEILING_CHECK_CMD}", "text ceiling check command"),
    (COMPILE_STEP, "compile step"),
    (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
    (WORKFLOW_CHECKER_STEP, "workflow checker step"),
    (PACKET_SELF_TEST_STEP, "packet checker self-test step"),
    (PACKET_CHECK_STEP, "packet check step"),
    (TEXT_CEILING_SELF_TEST_STEP, "text ceiling checker self-test step"),
    (TEXT_CEILING_CHECK_STEP, "text ceiling check step"),
)

ORDERED_MARKERS = (
    (CHECKER_PATH, PACKET_CHECKER_PATH, "pull_request path order"),
    (PACKET_CHECKER_PATH, TEXT_CEILING_CHECKER_PATH, "pull_request path order"),
    (TEXT_CEILING_CHECKER_PATH, POLICY_PATH, "pull_request path order"),
    (POLICY_PATH, THIRD_PARTY_PATH, "pull_request path order"),
    (THIRD_PARTY_PATH, WORKFLOW_PATH_FILTER, "pull_request path order"),
    (CHECKOUT_STEP, SETUP_PYTHON_STEP, "step order"),
    (SETUP_PYTHON_STEP, COMPILE_STEP, "step order"),
    (COMPILE_STEP, WORKFLOW_CHECKER_SELF_TEST_STEP, "step order"),
    (WORKFLOW_CHECKER_SELF_TEST_STEP, WORKFLOW_CHECKER_STEP, "step order"),
    (WORKFLOW_CHECKER_STEP, PACKET_SELF_TEST_STEP, "step order"),
    (PACKET_SELF_TEST_STEP, PACKET_CHECK_STEP, "step order"),
    (PACKET_CHECK_STEP, TEXT_CEILING_SELF_TEST_STEP, "step order"),
    (TEXT_CEILING_SELF_TEST_STEP, TEXT_CEILING_CHECK_STEP, "step order"),
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 archive-parts workflow checker missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 archive-parts workflow checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(f"lane05 archive-parts workflow checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 archive-parts workflow checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    for marker, label in REQUIRED_MARKERS:
        require_marker(text, marker, label)
    for line, label in EXACT_LINES:
        require_exact_line(text, line, label)
    for earlier, later, label in ORDERED_MARKERS:
        require_order(text, earlier, later, label)


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap-archive-parts-packet

on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'scripts/zigux/check-lane05-archive-parts-workflow.py'
      - 'scripts/zigux/check-lane05-archive-parts-packet.py'
      - 'scripts/zigux/check-lane05-archive-parts-text-ceiling.py'
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
        run: |
          set -euxo pipefail
          tmpdir=\"$(mktemp -d)\"
          archive=\"$tmpdir/source.tar.gz\"
          curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"
          tar -xzf \"$archive\" -C \"$tmpdir\"
          src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"
          find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
          shopt -s dotglob
          mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/

      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'

      - name: Compile current Lane 05 archive-parts workflow scripts
        run: python3 -m py_compile scripts/zigux/check-zig-toolchain.py scripts/zigux/check-lane05-archive-parts-packet.py scripts/zigux/check-lane05-archive-parts-text-ceiling.py scripts/zigux/check-lane05-archive-parts-workflow.py

      - name: Self-test current Lane 05 archive-parts workflow checker
        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test

      - name: Check current Lane 05 archive-parts workflow packet
        run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py

      - name: Self-test current Lane 05 archive parts packet checker
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test

      - name: Check current Lane 05 archive parts packet
        run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing

      - name: Self-test current Lane 05 archive parts text ceiling checker
        run: python3 scripts/zigux/check-lane05-archive-parts-text-ceiling.py --self-test

      - name: Check current Lane 05 archive parts text ceiling
        run: python3 scripts/zigux/check-lane05-archive-parts-text-ceiling.py --allow-missing
"""
    check_workflow(good_workflow)
    case_count = 1

    for broken_text, expected in (
        (good_workflow.replace(TEXT_CEILING_CHECKER_PATH + "\n", "", 1), TEXT_CEILING_CHECKER_PATH),
        (good_workflow.replace(TEXT_CEILING_SELF_TEST_STEP + "\n", "", 1), TEXT_CEILING_SELF_TEST_STEP),
        (good_workflow.replace(TEXT_CEILING_CHECK_STEP + "\n", "", 1), TEXT_CEILING_CHECK_STEP),
        (good_workflow.replace(f"        run: {TEXT_CEILING_CHECK_CMD}\n", "", 1), TEXT_CEILING_CHECK_CMD),
    ):
        try:
            check_workflow(broken_text)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected failure for {expected}")

    reordered_steps = good_workflow.replace(
        TEXT_CEILING_SELF_TEST_STEP,
        "- name: TEMP-TEXT-CEILING-SELF-TEST",
        1,
    ).replace(
        PACKET_CHECK_STEP,
        TEXT_CEILING_SELF_TEST_STEP,
        1,
    ).replace(
        "- name: TEMP-TEXT-CEILING-SELF-TEST",
        PACKET_CHECK_STEP,
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered step failure")

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

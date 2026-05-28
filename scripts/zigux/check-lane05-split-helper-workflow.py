#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap-split-helper.yml")

WORKFLOW_NAME = "name: zigux-bootstrap-split-helper"
PUSH_BRANCH = "branches: [ master ]"
SCRIPTS_PATH = "- 'scripts/zigux/**'"
THIRD_PARTY_PATH = "- 'third_party/**'"
WORKFLOW_PATH_FILTER = "- '.github/workflows/zigux-bootstrap-split-helper.yml'"
PERMISSIONS = "contents: read"
CHECKOUT_STEP = "- name: Checkout workspace snapshot"
PYTHON_STEP = "- name: Setup Python"
COMPILE_STEP = "- name: Compile current split-helper packet scripts"
COMPILE_CMD = (
    "python3 -m py_compile "
    "scripts/zigux/split-pinned-zig-archive.py "
    "scripts/zigux/check-lane05-split-helper-selftest.py "
    "scripts/zigux/check-lane05-split-helper-workflow.py"
)
HELPER_SELF_TEST_STEP = "- name: Self-test current split pinned Zig archive helper"
HELPER_SELF_TEST_CMD = "python3 scripts/zigux/split-pinned-zig-archive.py --self-test"
SELFTEST_CHECKER_STEP = "- name: Self-test current Lane 05 split helper selftest checker"
SELFTEST_CHECKER_CMD = "python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test"
WORKFLOW_CHECKER_SELF_TEST_STEP = "- name: Self-test current Lane 05 split-helper workflow checker"
WORKFLOW_CHECKER_SELF_TEST_CMD = (
    "python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test"
)
WORKFLOW_CHECKER_STEP = "- name: Check current Lane 05 split-helper workflow packet"
WORKFLOW_CHECKER_CMD = "python3 scripts/zigux/check-lane05-split-helper-workflow.py"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 split-helper workflow checker missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 split-helper workflow checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 split-helper workflow checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 split-helper workflow checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    for marker, label in (
        (WORKFLOW_NAME, "workflow name"),
        (PUSH_BRANCH, "master push trigger"),
        (SCRIPTS_PATH, "scripts path filter"),
        (THIRD_PARTY_PATH, "third-party path filter"),
        (WORKFLOW_PATH_FILTER, "workflow path filter"),
        (PERMISSIONS, "contents permission"),
        (CHECKOUT_STEP, "checkout step"),
        (PYTHON_STEP, "python setup step"),
        (COMPILE_STEP, "compile step"),
        (COMPILE_CMD, "compile command"),
        (HELPER_SELF_TEST_STEP, "helper self-test step"),
        (HELPER_SELF_TEST_CMD, "helper self-test command"),
        (SELFTEST_CHECKER_STEP, "selftest checker step"),
        (SELFTEST_CHECKER_CMD, "selftest checker command"),
        (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
        (WORKFLOW_CHECKER_SELF_TEST_CMD, "workflow checker self-test command"),
        (WORKFLOW_CHECKER_STEP, "workflow checker step"),
        (WORKFLOW_CHECKER_CMD, "workflow checker command"),
    ):
        require_marker(text, marker, label)

    for line, label in (
        (PUSH_BRANCH, "master push trigger"),
        (SCRIPTS_PATH, "scripts path filter"),
        (THIRD_PARTY_PATH, "third-party path filter"),
        (WORKFLOW_PATH_FILTER, "workflow path filter"),
        (PERMISSIONS, "contents permission"),
        (f"run: {COMPILE_CMD}", "compile command"),
        (f"run: {HELPER_SELF_TEST_CMD}", "helper self-test command"),
        (f"run: {SELFTEST_CHECKER_CMD}", "selftest checker command"),
        (f"run: {WORKFLOW_CHECKER_SELF_TEST_CMD}", "workflow checker self-test command"),
        (f"run: {WORKFLOW_CHECKER_CMD}", "workflow checker command"),
    ):
        require_exact_line(text, line, label)

    for line, label in (
        (CHECKOUT_STEP, "checkout step"),
        (COMPILE_STEP, "compile step"),
        (HELPER_SELF_TEST_STEP, "helper self-test step"),
        (SELFTEST_CHECKER_STEP, "selftest checker step"),
        (WORKFLOW_CHECKER_SELF_TEST_STEP, "workflow checker self-test step"),
        (WORKFLOW_CHECKER_STEP, "workflow checker step"),
    ):
        require_exact_line(text, line, label)

    require_order(text, SCRIPTS_PATH, THIRD_PARTY_PATH, "pull_request path order")
    require_order(
        text,
        THIRD_PARTY_PATH,
        WORKFLOW_PATH_FILTER,
        "pull_request path order",
    )
    require_order(text, CHECKOUT_STEP, PYTHON_STEP, "step order")
    require_order(text, PYTHON_STEP, COMPILE_STEP, "step order")
    require_order(text, COMPILE_STEP, HELPER_SELF_TEST_STEP, "step order")
    require_order(text, HELPER_SELF_TEST_STEP, SELFTEST_CHECKER_STEP, "step order")
    require_order(
        text,
        SELFTEST_CHECKER_STEP,
        WORKFLOW_CHECKER_SELF_TEST_STEP,
        "step order",
    )
    require_order(
        text,
        WORKFLOW_CHECKER_SELF_TEST_STEP,
        WORKFLOW_CHECKER_STEP,
        "step order",
    )


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap-split-helper

on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'scripts/zigux/**'
      - 'third_party/**'
      - '.github/workflows/zigux-bootstrap-split-helper.yml'
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  split-helper:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout workspace snapshot
        run: |
          set -euxo pipefail
          tmpdir="$(mktemp -d)"
          archive="$tmpdir/source.tar.gz"
          curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" -o "$archive"
          tar -xzf "$archive" -C "$tmpdir"
          src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
          find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
          shopt -s dotglob
          mv "$src_dir"/* "$GITHUB_WORKSPACE"/

      - name: Setup Python
        uses: actions/setup-python@v6.2.0
        with:
          python-version: '3.x'

      - name: Compile current split-helper packet scripts
        run: python3 -m py_compile scripts/zigux/split-pinned-zig-archive.py scripts/zigux/check-lane05-split-helper-selftest.py scripts/zigux/check-lane05-split-helper-workflow.py

      - name: Self-test current split pinned Zig archive helper
        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test

      - name: Self-test current Lane 05 split helper selftest checker
        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test

      - name: Self-test current Lane 05 split-helper workflow checker
        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test

      - name: Check current Lane 05 split-helper workflow packet
        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py
"""
    check_workflow(good_workflow)
    case_count = 1

    for broken_text, expected in (
        (
            good_workflow.replace(
                "permissions:\n  contents: read\n\n",
                "",
                1,
            ),
            PERMISSIONS,
        ),
        (
            good_workflow.replace(
                "      - name: Checkout workspace snapshot\n"
                "        run: |\n"
                "          set -euxo pipefail\n"
                "          tmpdir=\"$(mktemp -d)\"\n"
                "          archive=\"$tmpdir/source.tar.gz\"\n"
                "          curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"\n"
                "          tar -xzf \"$archive\" -C \"$tmpdir\"\n"
                "          src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"\n"
                "          find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +\n"
                "          shopt -s dotglob\n"
                "          mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/\n\n",
                "",
                1,
            ),
            CHECKOUT_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Compile current split-helper packet scripts\n"
                "        run: python3 -m py_compile scripts/zigux/split-pinned-zig-archive.py scripts/zigux/check-lane05-split-helper-selftest.py scripts/zigux/check-lane05-split-helper-workflow.py\n",
                "",
                1,
            ),
            COMPILE_STEP,
        ),
        (
            good_workflow.replace(
                "scripts/zigux/check-lane05-split-helper-workflow.py",
                "",
                1,
            ),
            COMPILE_CMD,
        ),
        (
            good_workflow.replace(
                "      - name: Self-test current Lane 05 split-helper workflow checker\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test\n",
                "",
                1,
            ),
            WORKFLOW_CHECKER_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 split-helper workflow packet\n"
                "        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py\n",
                "",
                1,
            ),
            WORKFLOW_CHECKER_STEP,
        ),
    ):
        try:
            check_workflow(broken_text)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected failure for {expected}")

    reordered_steps = good_workflow.replace(
        "      - name: Self-test current Lane 05 split helper selftest checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n\n"
        "      - name: Self-test current Lane 05 split-helper workflow checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test\n",
        "      - name: Self-test current Lane 05 split-helper workflow checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test\n\n"
        "      - name: Self-test current Lane 05 split helper selftest checker\n"
        "        run: python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "step order" in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered step failure")

    duplicate_step = good_workflow.replace(
        "      - name: Check current Lane 05 split-helper workflow packet\n",
        "      - name: Check current Lane 05 split-helper workflow packet\n"
        "      - name: Check current Lane 05 split-helper workflow packet\n",
        1,
    )
    try:
        check_workflow(duplicate_step)
    except SystemExit as exc:
        assert WORKFLOW_CHECKER_STEP in str(exc), str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate workflow checker step failure")

    print("LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split-helper workflow keeps its expected guard steps."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap-split-helper.yml",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_workflow(args.workflow.read_text(encoding="utf-8"))
    print("LANE05_SPLIT_HELPER_WORKFLOW=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())

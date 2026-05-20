#!/usr/bin/env python3
"""Fail-close guard for the current Lane 05 local-first archive workflow shape."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

PUSH_STEP = "  push:"
PUSH_BRANCHES = "    branches: [ master ]"
PULL_REQUEST_STEP = "  pull_request:"
WORKFLOW_DISPATCH_STEP = "  workflow_dispatch:"
CONCURRENCY_STEP = "concurrency:"
CONCURRENCY_GROUP = "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}"
CONCURRENCY_CANCEL = "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}"
ENV_STEP = "env:"
JOBS_STEP = "jobs:"
CHECKOUT_STEP = "- name: Checkout"
SETUP_STEP = "- name: Setup pinned Zig toolchain"
TOOLCHAIN_SELF_TEST_STEP = "- name: Self-test current Zig toolchain checker"
POLICY_STEP = "- name: Check current Zig toolchain policy packet"
POLICY_CMD = "python3 scripts/zigux/check-zig-toolchain.py --policy-only"
ARCHIVE_CHECK_STEP = "- name: Check current pinned Zig archive packet"
ARCHIVE_CHECK_CMD = "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing"
SELF_TEST_STEP = "- name: Self-test current Lane 05 local-first archive checker"
SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test"
CHECK_STEP = "- name: Check current Lane 05 local-first archive packet"
CHECK_CMD = "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py"
README_SELF_TEST_STEP = "- name: Self-test current Lane 05 local archive README checker"
README_SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test"
README_CHECK_STEP = "- name: Check current Lane 05 local archive README packet"
README_CHECK_CMD = "python3 scripts/zigux/check-lane05-local-archive-readme.py"
NEXT_PHASE_STEP = "- name: Self-test current Zig installer helper"

THIRD_PARTY_PATH = "- 'third_party/**'"
SCRIPTS_PATH = "- 'scripts/zigux/**'"
TOOLS_PATH = "- 'tools/lib/*.zig'"

POLICY_MARKERS = (
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'targets = policy["upgrade_policy"]["archive_target_scope"]',
    'channel = policy["channel"]',
    'filename = f"zig-{target}-{channel}.tar.xz"',
    'url = f"https://ziglang.org/builds/{filename}"',
    'print(f"ZIGUX_ZIG_TARGET=\'{target}\'")',
    'print(f"ZIGUX_ZIG_CHANNEL=\'{channel}\'")',
    'print(f"ZIGUX_ZIG_FILENAME=\'{filename}\'")',
    'print(f"ZIGUX_ZIG_URL=\'{url}\'")',
)

LOCAL_ARCHIVE_MARKERS = (
    'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    'extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    "try_local_archive() {",
    'if [ ! -f "$repo_archive_path" ]; then',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'tar -xJf "$repo_archive_path" -C .zig-toolchain',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    "if try_local_archive; then",
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
)

RETAINED_STEP_PAIRS = (
    (
        "- name: Self-test current Phase 1 route summary checker",
        "- name: Check current Phase 1 route summary packet",
    ),
    (
        "- name: Self-test current Phase 2 tool manifest checker",
        "- name: Check current Phase 2 tool manifest packet",
    ),
    (
        "- name: Self-test current Phase 2 artifact tools manifest checker",
        "- name: Check current Phase 2 artifact tools manifest packet",
    ),
    (
        "- name: Self-test current Phase 7 make-wrapper selftest alignment checker",
        "- name: Check current Phase 7 make-wrapper selftest alignment packet",
    ),
    (
        "- name: Self-test current Phase 9 freeze-map study-boundaries checker",
        "- name: Check current Phase 9 freeze-map study-boundaries packet",
    ),
    (
        "- name: Self-test current Phase 11 build inventory checker",
        "- name: Check current Phase 11 build inventory packet",
    ),
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 local-first archive checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            f"lane05 local-first archive checker expected {expected} {label} occurrence(s) for {marker}, found {actual}"
        )


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line.strip() == marker)
    if actual != expected:
        raise SystemExit(
            f"lane05 local-first archive checker expected {expected} {label} line(s) for {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(f"lane05 local-first archive checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise SystemExit(
            f"lane05 local-first archive checker expected {label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    top_level_markers = (
        (PUSH_STEP, "workflow push trigger"),
        (PUSH_BRANCHES, "workflow push branch filter"),
        (PULL_REQUEST_STEP, "workflow pull-request trigger"),
        (WORKFLOW_DISPATCH_STEP, "workflow dispatch trigger"),
        (ENV_STEP, "workflow env block"),
        (CONCURRENCY_STEP, "workflow concurrency block"),
        (CONCURRENCY_GROUP, "workflow concurrency group"),
        (CONCURRENCY_CANCEL, "workflow concurrency cancel policy"),
        (JOBS_STEP, "workflow jobs block"),
    )
    for marker, label in top_level_markers:
        require_marker(text, marker, label)

    for marker in POLICY_MARKERS:
        require_marker(text, marker, "workflow policy marker")
    for marker in LOCAL_ARCHIVE_MARKERS:
        require_marker(text, marker, "workflow local-first marker")

    for marker, label in (
        (CHECKOUT_STEP, "workflow checkout step"),
        (SETUP_STEP, "workflow setup step"),
        (TOOLCHAIN_SELF_TEST_STEP, "toolchain self-test step"),
        (POLICY_STEP, "toolchain policy step"),
        (ARCHIVE_CHECK_STEP, "toolchain archive step"),
        (SELF_TEST_STEP, "lane05 checker self-test step"),
        (CHECK_STEP, "lane05 checker step"),
        (README_SELF_TEST_STEP, "lane05 readme self-test step"),
        (README_CHECK_STEP, "lane05 readme step"),
        (NEXT_PHASE_STEP, "next-step anchor"),
        (THIRD_PARTY_PATH, "third-party path filter"),
    ):
        require_marker(text, marker, label)

    for self_test_step, check_step in RETAINED_STEP_PAIRS:
        require_marker(text, self_test_step, "retained bootstrap self-test")
        require_marker(text, check_step, "retained bootstrap check")

    for marker in (
        PUSH_STEP,
        PULL_REQUEST_STEP,
        WORKFLOW_DISPATCH_STEP,
        CONCURRENCY_STEP,
        SETUP_STEP,
        TOOLCHAIN_SELF_TEST_STEP,
        POLICY_STEP,
        ARCHIVE_CHECK_STEP,
        SELF_TEST_STEP,
        CHECK_STEP,
        README_SELF_TEST_STEP,
        README_CHECK_STEP,
    ):
        require_exact_count(text, marker, 1, "marker")

    require_exact_line_count(text, CONCURRENCY_GROUP, 1, "concurrency")
    require_exact_line_count(text, CONCURRENCY_CANCEL, 1, "concurrency")
    require_exact_line_count(text, THIRD_PARTY_PATH, 1, "path filter")
    require_exact_line_count(text, f"run: {POLICY_CMD}", 1, "run command")
    require_exact_line_count(text, f"run: {ARCHIVE_CHECK_CMD}", 1, "run command")
    require_exact_line_count(text, f"run: {SELF_TEST_CMD}", 1, "run command")
    require_exact_line_count(text, f"run: {CHECK_CMD}", 1, "run command")
    require_exact_line_count(text, f"run: {README_SELF_TEST_CMD}", 1, "run command")
    require_exact_line_count(text, f"run: {README_CHECK_CMD}", 1, "run command")
    require_exact_count(text, 'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"', 1, "archive path")
    require_exact_count(text, 'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"', 1, "repo archive path")
    require_exact_count(
        text,
        'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
        1,
        "downloaded archive validation",
    )
    require_exact_count(text, "if try_local_archive; then", 1, "local-first fallback branch")

    require_order(text, PUSH_STEP, PUSH_BRANCHES, "trigger order")
    require_order(text, PUSH_BRANCHES, PULL_REQUEST_STEP, "trigger order")
    require_order(text, PULL_REQUEST_STEP, WORKFLOW_DISPATCH_STEP, "trigger order")
    require_order(text, WORKFLOW_DISPATCH_STEP, ENV_STEP, "top-level order")
    require_order(text, ENV_STEP, CONCURRENCY_STEP, "top-level order")
    require_order(text, CONCURRENCY_STEP, JOBS_STEP, "top-level order")
    require_order(text, CONCURRENCY_GROUP, CONCURRENCY_CANCEL, "concurrency order")
    require_order(text, CHECKOUT_STEP, SETUP_STEP, "bootstrap step order")
    require_order(text, SETUP_STEP, TOOLCHAIN_SELF_TEST_STEP, "bootstrap step order")
    require_order(text, TOOLCHAIN_SELF_TEST_STEP, POLICY_STEP, "bootstrap step order")
    require_order(text, POLICY_STEP, ARCHIVE_CHECK_STEP, "bootstrap step order")
    require_order(text, ARCHIVE_CHECK_STEP, SELF_TEST_STEP, "bootstrap step order")
    require_order(text, SELF_TEST_STEP, CHECK_STEP, "bootstrap step order")
    require_order(text, CHECK_STEP, README_SELF_TEST_STEP, "bootstrap step order")
    require_order(text, README_SELF_TEST_STEP, README_CHECK_STEP, "bootstrap step order")
    require_order(text, README_CHECK_STEP, NEXT_PHASE_STEP, "bootstrap step order")
    require_order(text, SCRIPTS_PATH, THIRD_PARTY_PATH, "pull_request path order")
    require_order(text, THIRD_PARTY_PATH, TOOLS_PATH, "pull_request path order")

    for self_test_step, check_step in RETAINED_STEP_PAIRS:
        require_exact_count(text, self_test_step, 1, "retained self-test")
        require_exact_count(text, check_step, 1, "retained check")
        require_order(text, self_test_step, check_step, "retained step order")

    require_order(
        text,
        'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
        'targets = policy["upgrade_policy"]["archive_target_scope"]',
        "policy derivation order",
    )
    require_order(
        text,
        'targets = policy["upgrade_policy"]["archive_target_scope"]',
        'channel = policy["channel"]',
        "policy derivation order",
    )
    require_order(
        text,
        'channel = policy["channel"]',
        'filename = f"zig-{target}-{channel}.tar.xz"',
        "policy derivation order",
    )
    require_order(
        text,
        'filename = f"zig-{target}-{channel}.tar.xz"',
        'url = f"https://ziglang.org/builds/{filename}"',
        "policy derivation order",
    )
    require_order(
        text,
        'url = f"https://ziglang.org/builds/{filename}"',
        'print(f"ZIGUX_ZIG_TARGET=\'{target}\'")',
        "policy export order",
    )
    require_order(
        text,
        'print(f"ZIGUX_ZIG_TARGET=\'{target}\'")',
        'print(f"ZIGUX_ZIG_URL=\'{url}\'")',
        "policy export order",
    )
    require_order(
        text,
        'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
        "try_local_archive() {",
        "helper definition order",
    )
    require_order(
        text,
        "try_local_archive() {",
        "try_download() {",
        "helper definition order",
    )
    require_order(
        text,
        "try_download() {",
        "download_success=0",
        "fallback setup order",
    )
    require_order(
        text,
        "download_success=0",
        "if try_local_archive; then",
        "fallback execution order",
    )
    require_order(
        text,
        "if try_local_archive; then",
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        "local-first before mirrors order",
    )
    require_order(
        text,
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        'if try_download "$ZIGUX_ZIG_URL"; then',
        "mirrors before direct order",
    )


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'scripts/zigux/**'
      - 'third_party/**'
      - 'tools/lib/*.zig'
  workflow_dispatch:

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

concurrency:
  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}

jobs:
  bootstrap:
    steps:
      - name: Checkout
      - name: Setup pinned Zig toolchain
        run: |
          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))
          targets = policy["upgrade_policy"]["archive_target_scope"]
          channel = policy["channel"]
          filename = f"zig-{target}-{channel}.tar.xz"
          url = f"https://ziglang.org/builds/{filename}"
          print(f"ZIGUX_ZIG_TARGET='{target}'")
          print(f"ZIGUX_ZIG_CHANNEL='{channel}'")
          print(f"ZIGUX_ZIG_FILENAME='{filename}'")
          print(f"ZIGUX_ZIG_URL='{url}'")
          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
          try_local_archive() {
            if [ ! -f "$repo_archive_path" ]; then
              return 1
            fi
            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
              tar -xJf "$repo_archive_path" -C .zig-toolchain
            fi
          }
          try_download() {
            return 0
          }
          download_success=0
          if try_local_archive; then
            download_success=1
          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
            download_success=0
          fi
          if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
            download_success=1
          fi
          if try_download "$ZIGUX_ZIG_URL"; then
            download_success=1
          fi
          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2
      - name: Self-test current Zig toolchain checker
        run: python3 scripts/zigux/check-zig-toolchain.py --self-test
      - name: Check current Zig toolchain policy packet
        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only
      - name: Check current pinned Zig archive packet
        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
      - name: Self-test current Lane 05 local-first archive checker
        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test
      - name: Check current Lane 05 local-first archive packet
        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py
      - name: Self-test current Lane 05 local archive README checker
        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test
      - name: Check current Lane 05 local archive README packet
        run: python3 scripts/zigux/check-lane05-local-archive-readme.py
      - name: Self-test current Zig installer helper
      - name: Self-test current Phase 1 route summary checker
      - name: Check current Phase 1 route summary packet
      - name: Self-test current Phase 2 tool manifest checker
      - name: Check current Phase 2 tool manifest packet
      - name: Self-test current Phase 2 artifact tools manifest checker
      - name: Check current Phase 2 artifact tools manifest packet
      - name: Self-test current Phase 7 make-wrapper selftest alignment checker
      - name: Check current Phase 7 make-wrapper selftest alignment packet
      - name: Self-test current Phase 9 freeze-map study-boundaries checker
      - name: Check current Phase 9 freeze-map study-boundaries packet
      - name: Self-test current Phase 11 build inventory checker
      - name: Check current Phase 11 build inventory packet
"""
    check_workflow(good_workflow)
    case_count = 1

    failure_cases = [
        (
            good_workflow.replace("  workflow_dispatch:\n", "", 1),
            "workflow dispatch trigger",
        ),
        (
            good_workflow.replace(CONCURRENCY_GROUP + "\n", "", 1),
            "workflow concurrency group",
        ),
        (
            good_workflow.replace(
                'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))\n',
                "",
                1,
            ),
            "workflow policy marker",
        ),
        (
            good_workflow.replace(
                'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
                'python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing',
                1,
            ),
            '--archive "$repo_archive_path"',
        ),
        (
            good_workflow.replace("      - 'third_party/**'\n", "", 1),
            "third-party path filter",
        ),
        (
            good_workflow.replace(
                f"      {README_SELF_TEST_STEP}\n        run: {README_SELF_TEST_CMD}\n",
                "",
                1,
            ),
            "lane05 readme self-test step",
        ),
        (
            good_workflow.replace(
                "          if try_local_archive; then\n"
                "            download_success=1\n"
                '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then\n'
                "            download_success=0\n"
                "          fi\n",
                '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then\n'
                "            download_success=0\n"
                "          fi\n"
                "          if try_local_archive; then\n"
                "            download_success=1\n",
                1,
            ),
            "local-first before mirrors order",
        ),
    ]

    for broken_workflow, expected_fragment in failure_cases:
        try:
            check_workflow(broken_workflow)
        except SystemExit as exc:
            assert expected_fragment in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected failure containing {expected_fragment!r}")

    print("LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current bootstrap workflow keeps the Lane 05 local-first archive route explicit."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap.yml",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_workflow(args.workflow.read_text(encoding="utf-8"))
    print("LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 repo-local pinned-archive bootstrap path."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

CHECKOUT_STEP = "- name: Checkout"
SETUP_STEP = "- name: Setup pinned Zig toolchain"
ARCHIVE_CHECK_STEP = "- name: Check current pinned Zig archive packet"
SELF_TEST_STEP = "- name: Self-test current Lane 05 local-first archive checker"
SELF_TEST_CMD = "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test"
CHECK_STEP = "- name: Check current Lane 05 local-first archive packet"
CHECK_CMD = "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py"
NEXT_PHASE_STEP = "- name: Self-test current Phase 2 fixdep gate checker"

LOCAL_ARCHIVE_MARKERS = (
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    "try_local_archive() {",
    'if [ ! -f "$repo_archive_path" ]; then',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'tar -xJf "$repo_archive_path" -C .zig-toolchain',
    "if try_local_archive; then",
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 local-first archive checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 local-first archive checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line.strip() == marker)
    if actual != expected:
        raise SystemExit(
            "lane05 local-first archive checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 local-first archive checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 local-first archive checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    for marker in LOCAL_ARCHIVE_MARKERS:
        require_marker(text, marker, "workflow local-first marker")

    require_marker(text, CHECKOUT_STEP, "workflow checkout step name")
    require_marker(text, SETUP_STEP, "workflow setup step name")
    require_marker(text, ARCHIVE_CHECK_STEP, "workflow archive-check step name")
    require_marker(text, SELF_TEST_STEP, "workflow checker self-test step name")
    require_marker(text, SELF_TEST_CMD, "workflow checker self-test command")
    require_marker(text, CHECK_STEP, "workflow checker step name")
    require_marker(text, CHECK_CMD, "workflow checker command")
    require_marker(text, NEXT_PHASE_STEP, "workflow next-step anchor")

    require_exact_count(text, SETUP_STEP, 1, "workflow step name")
    require_exact_count(text, ARCHIVE_CHECK_STEP, 1, "workflow step name")
    require_exact_count(text, SELF_TEST_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {SELF_TEST_CMD}", 1, "workflow run line")
    require_exact_count(text, CHECK_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {CHECK_CMD}", 1, "workflow run line")
    require_exact_count(text, 'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"', 1, "local archive path marker")
    require_exact_count(text, "try_local_archive() {", 1, "local archive helper definition")
    require_exact_count(text, "if try_local_archive; then", 1, "local archive helper invocation")

    require_order(text, CHECKOUT_STEP, SETUP_STEP, "workflow step order")
    require_order(text, SETUP_STEP, ARCHIVE_CHECK_STEP, "workflow step order")
    require_order(text, ARCHIVE_CHECK_STEP, SELF_TEST_STEP, "workflow step order")
    require_order(text, SELF_TEST_STEP, CHECK_STEP, "workflow step order")
    require_order(text, CHECK_STEP, NEXT_PHASE_STEP, "workflow step order")

    require_order(
        text,
        'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
        "try_local_archive() {",
        "workflow local-first helper order",
    )
    require_order(
        text,
        "try_local_archive() {",
        "try_download() {",
        "workflow helper definition order",
    )
    require_order(
        text,
        "try_download() {",
        "download_success=0",
        "workflow fallback-state setup order",
    )
    require_order(
        text,
        "download_success=0",
        "if try_local_archive; then",
        "workflow fallback attempt order",
    )
    require_order(
        text,
        "if try_local_archive; then",
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        "workflow local-first before mirrors order",
    )
    require_order(
        text,
        'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        'if try_download "$ZIGUX_ZIG_URL"; then',
        "workflow mirrors before direct download order",
    )


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Checkout
        uses: actions/checkout@v6.0.2
      - name: Setup pinned Zig toolchain
        run: |
          repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"
          try_local_archive() {
            if [ ! -f \"$repo_archive_path\" ]; then
              return 1
            fi
            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"; then
              tar -xJf \"$repo_archive_path\" -C .zig-toolchain
            fi
          }
          try_download() {
            return 0
          }
          download_success=0
          if try_local_archive; then
            download_success=1
          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then
            download_success=0
          fi
          if try_download \"$ZIGUX_ZIG_URL\"; then
            download_success=1
          fi
          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2
      - name: Check current pinned Zig archive packet
        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing
      - name: Self-test current Lane 05 local-first archive checker
        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test
      - name: Check current Lane 05 local-first archive packet
        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py
      - name: Self-test current Phase 2 fixdep gate checker
        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
"""
    check_workflow(good_workflow)

    missing_repo_archive = good_workflow.replace(
        'repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"\n',
        "",
        1,
    )
    try:
        check_workflow(missing_repo_archive)
    except SystemExit as exc:
        assert "repo_archive_path" in str(exc)
    else:
        raise AssertionError("expected missing repo archive path failure")

    missing_local_validation = good_workflow.replace(
        'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive \"$repo_archive_path\" --archive-target \"$ZIGUX_ZIG_TARGET\"',
        'python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing',
        1,
    )
    try:
        check_workflow(missing_local_validation)
    except SystemExit as exc:
        assert '--archive \"$repo_archive_path\"' in str(exc)
    else:
        raise AssertionError("expected missing local validation command failure")

    missing_self_test_step = good_workflow.replace(
        f"      {SELF_TEST_STEP}\n        run: {SELF_TEST_CMD}\n",
        "",
        1,
    )
    try:
        check_workflow(missing_self_test_step)
    except SystemExit as exc:
        assert SELF_TEST_STEP in str(exc) or SELF_TEST_CMD in str(exc)
    else:
        raise AssertionError("expected missing checker self-test step failure")

    missing_check_step = good_workflow.replace(
        f"      {CHECK_STEP}\n        run: {CHECK_CMD}\n",
        "",
        1,
    )
    try:
        check_workflow(missing_check_step)
    except SystemExit as exc:
        assert CHECK_STEP in str(exc) or CHECK_CMD in str(exc)
    else:
        raise AssertionError("expected missing checker step failure")

    reordered_fallback = good_workflow.replace(
        "          if try_local_archive; then\n"
        "            download_success=1\n"
        '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then\n'
        "            download_success=0\n"
        "          fi\n"
        '          if try_download \"$ZIGUX_ZIG_URL\"; then\n'
        "            download_success=1\n"
        "          fi\n",
        '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o \"$mirror_file\"; then\n'
        "            download_success=0\n"
        "          fi\n"
        "          if try_local_archive; then\n"
        "            download_success=1\n"
        '          if try_download \"$ZIGUX_ZIG_URL\"; then\n'
        "            download_success=1\n"
        "          fi\n",
        1,
    )
    try:
        check_workflow(reordered_fallback)
    except SystemExit as exc:
        assert "workflow local-first before mirrors order" in str(exc)
    else:
        raise AssertionError("expected reordered fallback failure")

    duplicate_check_step = good_workflow.replace(
        f"      {CHECK_STEP}\n        run: {CHECK_CMD}\n",
        f"      {CHECK_STEP}\n        run: {CHECK_CMD}\n"
        f"      {CHECK_STEP}\n        run: {CHECK_CMD}\n",
        1,
    )
    try:
        check_workflow(duplicate_check_step)
    except SystemExit as exc:
        assert CHECK_STEP in str(exc)
    else:
        raise AssertionError("expected duplicate checker step failure")

    print("LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST=pass")
    print("LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST_CASE_COUNT=7")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 bootstrap workflow keeps the repo-local pinned-archive fallback explicit."
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

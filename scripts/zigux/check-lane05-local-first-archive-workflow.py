#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 repo-local pinned-archive bootstrap path."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

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
NEXT_PHASE_STEP = "- name: Self-test current Phase 2 fixdep gate checker"
THIRD_PARTY_PATH = "- 'third_party/**'"

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
    for marker in POLICY_MARKERS:
        require_marker(text, marker, "workflow policy marker")
    for marker in LOCAL_ARCHIVE_MARKERS:
        require_marker(text, marker, "workflow local-first marker")

    require_marker(text, CHECKOUT_STEP, "workflow checkout step name")
    require_marker(text, SETUP_STEP, "workflow setup step name")
    require_marker(text, TOOLCHAIN_SELF_TEST_STEP, "workflow toolchain self-test step name")
    require_marker(text, POLICY_STEP, "workflow toolchain policy step name")
    require_marker(text, POLICY_CMD, "workflow toolchain policy command")
    require_marker(text, ARCHIVE_CHECK_STEP, "workflow archive-check step name")
    require_marker(text, ARCHIVE_CHECK_CMD, "workflow archive-check command")
    require_marker(text, SELF_TEST_STEP, "workflow checker self-test step name")
    require_marker(text, SELF_TEST_CMD, "workflow checker self-test command")
    require_marker(text, CHECK_STEP, "workflow checker step name")
    require_marker(text, CHECK_CMD, "workflow checker command")
    require_marker(text, NEXT_PHASE_STEP, "workflow next-step anchor")
    require_marker(text, THIRD_PARTY_PATH, "workflow third-party path filter")

    require_exact_count(text, SETUP_STEP, 1, "workflow step name")
    require_exact_count(text, TOOLCHAIN_SELF_TEST_STEP, 1, "workflow step name")
    require_exact_count(text, POLICY_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {POLICY_CMD}", 1, "workflow run line")
    require_exact_count(text, ARCHIVE_CHECK_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {ARCHIVE_CHECK_CMD}", 1, "workflow run line")
    require_exact_count(text, SELF_TEST_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {SELF_TEST_CMD}", 1, "workflow run line")
    require_exact_count(text, CHECK_STEP, 1, "workflow step name")
    require_exact_line_count(text, f"run: {CHECK_CMD}", 1, "workflow run line")
    require_exact_line_count(text, THIRD_PARTY_PATH, 1, "workflow path filter line")
    require_exact_count(text, 'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"', 1, "archive path marker")
    require_exact_count(text, 'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"', 1, "local archive path marker")
    require_exact_count(text, "try_local_archive() {", 1, "local archive helper definition")
    require_exact_count(text, "if try_local_archive; then", 1, "local archive helper invocation")

    require_order(text, CHECKOUT_STEP, SETUP_STEP, "workflow step order")
    require_order(text, SETUP_STEP, TOOLCHAIN_SELF_TEST_STEP, "workflow step order")
    require_order(text, TOOLCHAIN_SELF_TEST_STEP, POLICY_STEP, "workflow step order")
    require_order(text, POLICY_STEP, ARCHIVE_CHECK_STEP, "workflow step order")
    require_order(text, ARCHIVE_CHECK_STEP, SELF_TEST_STEP, "workflow step order")
    require_order(text, SELF_TEST_STEP, CHECK_STEP, "workflow step order")
    require_order(text, CHECK_STEP, NEXT_PHASE_STEP, "workflow step order")
    require_order(text, "- 'scripts/zigux/**'", THIRD_PARTY_PATH, "workflow pull_request path order")
    require_order(text, THIRD_PARTY_PATH, "- 'tools/lib/*.zig'", "workflow pull_request path order")

    require_order(
        text,
        'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
        'targets = policy["upgrade_policy"]["archive_target_scope"]',
        "workflow inline policy order",
    )
    require_order(
        text,
        'targets = policy["upgrade_policy"]["archive_target_scope"]',
        'channel = policy["channel"]',
        "workflow inline policy order",
    )
    require_order(
        text,
        'channel = policy["channel"]',
        'filename = f"zig-{target}-{channel}.tar.xz"',
        "workflow inline policy order",
    )
    require_order(
        text,
        'filename = f"zig-{target}-{channel}.tar.xz"',
        'url = f"https://ziglang.org/builds/{filename}"',
        "workflow inline policy order",
    )
    require_order(
        text,
        'url = f"https://ziglang.org/builds/{filename}"',
        'print(f"ZIGUX_ZIG_URL=\'{url}\'")',
        "workflow inline policy order",
    )

    require_order(
        text,
        'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
        'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
        "workflow archive path order",
    )
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
          paths:
            - 'scripts/zigux/**'
            - 'third_party/**'
            - 'tools/lib/*.zig'
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
      - name: Self-test current Phase 2 fixdep gate checker
        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test
"""
    check_workflow(good_workflow)
    case_count = 1

    missing_policy_load = good_workflow.replace(
        '          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))\n',
        "",
        1,
    )
    try:
        check_workflow(missing_policy_load)
    except SystemExit as exc:
        assert "zig-toolchain-policy.json" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing policy load failure")

    missing_policy_step = good_workflow.replace(
        "      - name: Check current Zig toolchain policy packet\n"
        "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\n",
        "",
        1,
    )
    try:
        check_workflow(missing_policy_step)
    except SystemExit as exc:
        assert POLICY_STEP in str(exc) or POLICY_CMD in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing policy step failure")

    reordered_policy_and_archive = good_workflow.replace(
        "      - name: Check current Zig toolchain policy packet\n"
        "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\n"
        "      - name: Check current pinned Zig archive packet\n"
        "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\n",
        "      - name: Check current pinned Zig archive packet\n"
        "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\n"
        "      - name: Check current Zig toolchain policy packet\n"
        "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\n",
        1,
    )
    try:
        check_workflow(reordered_policy_and_archive)
    except SystemExit as exc:
        assert "workflow step order" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered policy/archive failure")

    missing_repo_archive = good_workflow.replace(
        '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"\n',
        "",
        1,
    )
    try:
        check_workflow(missing_repo_archive)
    except SystemExit as exc:
        assert "repo_archive_path" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing repo archive path failure")

    missing_local_validation = good_workflow.replace(
        'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
        'python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing',
        1,
    )
    try:
        check_workflow(missing_local_validation)
    except SystemExit as exc:
        assert '--archive "$repo_archive_path"' in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing local validation command failure")

    missing_self_test_step = good_workflow.replace(
        "      - name: Self-test current Lane 05 local-first archive checker\n"
        "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test\n",
        "",
        1,
    )
    try:
        check_workflow(missing_self_test_step)
    except SystemExit as exc:
        assert SELF_TEST_STEP in str(exc) or SELF_TEST_CMD in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing checker self-test step failure")

    missing_check_step = good_workflow.replace(
        "      - name: Check current Lane 05 local-first archive packet\n"
        "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py\n",
        "",
        1,
    )
    try:
        check_workflow(missing_check_step)
    except SystemExit as exc:
        assert CHECK_STEP in str(exc) or CHECK_CMD in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing checker step failure")

    reordered_fallback = good_workflow.replace(
        "          if try_local_archive; then\n"
        "            download_success=1\n"
        '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then\n'
        "            download_success=0\n"
        "          fi\n"
        '          if try_download "$ZIGUX_ZIG_URL"; then\n'
        "            download_success=1\n"
        "          fi\n",
        '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then\n'
        "            download_success=0\n"
        "          fi\n"
        "          if try_local_archive; then\n"
        "            download_success=1\n"
        '          if try_download "$ZIGUX_ZIG_URL"; then\n'
        "            download_success=1\n"
        "          fi\n",
        1,
    )
    try:
        check_workflow(reordered_fallback)
    except SystemExit as exc:
        assert "workflow local-first before mirrors order" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered fallback failure")

    duplicate_check_step = good_workflow.replace(
        "      - name: Check current Lane 05 local-first archive packet\n"
        "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py\n",
        "      - name: Check current Lane 05 local-first archive packet\n"
        "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py\n"
        "      - name: Check current Lane 05 local-first archive packet\n"
        "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py\n",
        1,
    )
    try:
        check_workflow(duplicate_check_step)
    except SystemExit as exc:
        assert CHECK_STEP in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate checker step failure")

    missing_third_party_path = good_workflow.replace(
        "            - 'third_party/**'\n",
        "",
        1,
    )
    try:
        check_workflow(missing_third_party_path)
    except SystemExit as exc:
        assert "third_party/**" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing third-party path failure")

    duplicate_third_party_path = good_workflow.replace(
        "            - 'third_party/**'\n",
        "            - 'third_party/**'\n"
        "            - 'third_party/**'\n",
        1,
    )
    try:
        check_workflow(duplicate_third_party_path)
    except SystemExit as exc:
        assert "third_party/**" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate third-party path failure")

    print("LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST=pass")
    print(f"LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST_CASE_COUNT={case_count}")
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
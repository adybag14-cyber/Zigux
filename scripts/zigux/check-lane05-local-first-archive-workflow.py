#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 repo-local pinned-archive bootstrap path."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = ROOT / ".github/workflows/zigux-bootstrap.yml"

SETUP_STEP = "- name: Setup pinned Zig toolchain"
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
STAGE_HELPER_SELF_TEST_STEP = "- name: Self-test current staged pinned Zig archive helper"
STAGE_HELPER_SELF_TEST_CMD = "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test"
NEXT_PHASE_STEP = "- name: Self-test current Zig installer helper"
THIRD_PARTY_PATH = "- 'third_party/**'"
SCRIPTS_PATH = "- 'scripts/zigux/**'"
TOOLS_PATH = "- 'tools/lib/*.zig'"

RETRY_OPTIONS = (
    "--fail",
    "--location",
    "--retry 5",
    "--retry-all-errors",
    "--retry-delay 3",
    "--connect-timeout 20",
    "--speed-limit 1024",
    "--speed-time 30",
)

POLICY_MARKERS = (
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'targets = policy["upgrade_policy"]["archive_target_scope"]',
    'channel = policy["channel"]',
    'filename = f"zig-{target}-{channel}.tar.xz"',
    'canonical_repo = "adybag14-cyber/zig"',
    'canonical_tag = "upstream-748e7c5e39fc"',
    'url = f"https://ziglang.org/builds/{filename}"',
    'canonical_url = f"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}"',
    'print(f"ZIGUX_ZIG_URL=\'{url}\'")',
    'print(f"ZIGUX_ZIG_CANONICAL_URL=\'{canonical_url}\'")',
)

LOCAL_ARCHIVE_MARKERS = (
    'archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"',
    'extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    'try_local_archive() {',
    'if [ ! -f "$repo_archive_path" ]; then',
    'if [ ! -d "$repo_archive_parts_dir" ]; then',
    'python3 scripts/zigux/stage-pinned-zig-archive.py',
    '--root "$GITHUB_WORKSPACE"',
    '--parts-dir "$repo_archive_parts_dir"',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'tar -xJf "$repo_archive_path" -C .zig-toolchain',
    'try_download() {',
    'if try_local_archive; then',
    'elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then',
    'https://ziglang.org/download/community-mirrors.txt',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org',
)

STEP_RUN_PAIRS = (
    (POLICY_STEP, POLICY_CMD),
    (ARCHIVE_CHECK_STEP, ARCHIVE_CHECK_CMD),
    (SELF_TEST_STEP, SELF_TEST_CMD),
    (CHECK_STEP, CHECK_CMD),
    (README_SELF_TEST_STEP, README_SELF_TEST_CMD),
    (README_CHECK_STEP, README_CHECK_CMD),
    (STAGE_HELPER_SELF_TEST_STEP, STAGE_HELPER_SELF_TEST_CMD),
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
        raise SystemExit(f"lane05 local-first archive checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 local-first archive checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def require_retry_block(text: str, start: str, end: str, label: str) -> None:
    start_index = text.find(start)
    end_index = text.find(end, start_index)
    if start_index == -1 or end_index == -1:
        raise SystemExit(f"lane05 local-first archive checker missing retry block for {label}")
    block = text[start_index:end_index]
    for option in RETRY_OPTIONS:
        require_marker(block, option, f"{label} retry option")


def check_workflow(text: str) -> None:
    for marker in POLICY_MARKERS:
        require_marker(text, marker, "workflow policy marker")
    for marker in LOCAL_ARCHIVE_MARKERS:
        require_marker(text, marker, "workflow local-first marker")

    require_marker(text, SETUP_STEP, "workflow setup step name")
    require_marker(text, THIRD_PARTY_PATH, "workflow third-party path filter")
    require_marker(text, NEXT_PHASE_STEP, "workflow next-step anchor")
    for step, command in STEP_RUN_PAIRS:
        require_marker(text, step, "workflow step name")
        require_exact_line_count(text, f"run: {command}", 1, "workflow run line")

    require_exact_count(text, SETUP_STEP, 1, "workflow setup step")
    require_exact_count(text, 'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"', 1, "repo archive path marker")
    require_exact_count(text, 'repo_archive_parts_dir="${repo_archive_path}.parts"', 1, "repo archive parts-dir marker")
    require_exact_count(text, 'try_local_archive() {', 1, "local archive helper definition")
    require_exact_count(text, 'try_download() {', 1, "download helper definition")
    require_exact_line_count(text, THIRD_PARTY_PATH, 1, "workflow path filter line")

    require_order(text, SCRIPTS_PATH, THIRD_PARTY_PATH, "workflow pull_request path order")
    require_order(text, THIRD_PARTY_PATH, TOOLS_PATH, "workflow pull_request path order")
    require_order(text, SETUP_STEP, POLICY_STEP, "workflow setup before policy check")
    require_order(text, POLICY_STEP, ARCHIVE_CHECK_STEP, "workflow policy before archive check")
    require_order(text, ARCHIVE_CHECK_STEP, SELF_TEST_STEP, "workflow archive check before checker self-test")
    require_order(text, SELF_TEST_STEP, CHECK_STEP, "workflow checker self-test before checker run")
    require_order(text, CHECK_STEP, README_SELF_TEST_STEP, "workflow checker before README checker")
    require_order(text, README_CHECK_STEP, STAGE_HELPER_SELF_TEST_STEP, "workflow README checker before staged-helper self-test")
    require_order(text, STAGE_HELPER_SELF_TEST_STEP, NEXT_PHASE_STEP, "workflow stage helper before installer helper")
    require_order(text, 'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"', 'repo_archive_parts_dir="${repo_archive_path}.parts"', "workflow archive parts path order")
    require_order(text, 'repo_archive_parts_dir="${repo_archive_path}.parts"', 'try_local_archive() {', "workflow local helper setup order")
    require_order(text, 'if [ ! -f "$repo_archive_path" ]; then', 'if [ ! -d "$repo_archive_parts_dir" ]; then', "workflow parts-dir guard order")
    require_order(text, 'if [ ! -d "$repo_archive_parts_dir" ]; then', 'python3 scripts/zigux/stage-pinned-zig-archive.py', "workflow stage-helper order")
    require_order(text, '--parts-dir "$repo_archive_parts_dir"', 'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"', "workflow staged archive before validation order")
    require_order(text, 'try_local_archive() {', 'try_download() {', "workflow helper definition order")
    require_order(text, 'download_success=0', 'if try_local_archive; then', "workflow fallback state order")
    require_order(text, 'if try_local_archive; then', 'elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then', "workflow local-first before canonical order")
    require_order(text, 'elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then', 'https://ziglang.org/download/community-mirrors.txt', "workflow canonical before mirrors order")
    require_order(text, 'https://ziglang.org/download/community-mirrors.txt', 'if try_download "$ZIGUX_ZIG_URL"; then', "workflow mirrors before direct download order")

    require_retry_block(text, 'if curl --fail', 'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path"', "archive download")
    require_retry_block(text, 'elif curl --fail', 'while IFS= read -r mirror_url; do', "mirror roster")


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
on:
  pull_request:
    paths:
      - 'scripts/zigux/**'
      - 'third_party/**'
      - 'tools/lib/*.zig'
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))
          targets = policy["upgrade_policy"]["archive_target_scope"]
          channel = policy["channel"]
          filename = f"zig-{target}-{channel}.tar.xz"
          canonical_repo = "adybag14-cyber/zig"
          canonical_tag = "upstream-748e7c5e39fc"
          url = f"https://ziglang.org/builds/{filename}"
          canonical_url = f"https://github.com/{canonical_repo}/releases/download/{canonical_tag}/{filename}"
          print(f"ZIGUX_ZIG_URL='{url}'")
          print(f"ZIGUX_ZIG_CANONICAL_URL='{canonical_url}'")
          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
          repo_archive_parts_dir="${repo_archive_path}.parts"
          try_local_archive() {
            if [ ! -f "$repo_archive_path" ]; then
              if [ ! -d "$repo_archive_parts_dir" ]; then
                return 1
              fi
              python3 scripts/zigux/stage-pinned-zig-archive.py --root "$GITHUB_WORKSPACE" --parts-dir "$repo_archive_parts_dir" || return 1
            fi
            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
              tar -xJf "$repo_archive_path" -C .zig-toolchain
            fi
          }
          try_download() {
            if curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 "$url" -o "$archive_path"; then
              python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"
            fi
          }
          download_success=0
          if try_local_archive; then
            download_success=1
          elif try_download "$ZIGUX_ZIG_CANONICAL_URL"; then
            download_success=1
          elif curl --fail --location --retry 5 --retry-all-errors --retry-delay 3 --connect-timeout 20 --speed-limit 1024 --speed-time 30 https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
            while IFS= read -r mirror_url; do
              break
            done
          fi
          if try_download "$ZIGUX_ZIG_URL"; then
            download_success=1
          fi
          echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2
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
      - name: Self-test current staged pinned Zig archive helper
        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
      - name: Self-test current Zig installer helper
        run: python3 scripts/zigux/install-zig.py --self-test
"""
    check_workflow(good_workflow)
    case_count = 1

    failures = (
        ("missing policy", good_workflow.replace(POLICY_MARKERS[0] + "\n", "", 1), "zig-toolchain-policy"),
        ("missing parts dir", good_workflow.replace('          repo_archive_parts_dir="${repo_archive_path}.parts"\n', "", 1), "parts-dir"),
        ("missing mirror retry", good_workflow.replace("--retry-all-errors ", "", 1), "retry"),
        ("missing third-party path", good_workflow.replace("      - 'third_party/**'\n", "", 1), "third_party"),
        ("reordered fallback", good_workflow.replace("if try_local_archive; then", "if try_download \"$ZIGUX_ZIG_URL\"; then", 1), "local-first"),
    )
    for name, bad_workflow, expected in failures:
        try:
            check_workflow(bad_workflow)
        except SystemExit as exc:
            if expected not in str(exc):
                raise AssertionError(f"{name} failed with unexpected message: {exc}") from exc
            case_count += 1
        else:
            raise AssertionError(f"expected {name} failure")

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

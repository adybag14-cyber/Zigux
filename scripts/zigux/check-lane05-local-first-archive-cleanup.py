#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 local-first archive cleanup and retry path."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
README_PATH = Path("third_party/README.md")

SETUP_STEP = "- name: Setup pinned Zig toolchain"
README_CHECK_STEP = "- name: Check current Lane 05 local archive README packet"
README_CHECK_CMD = "python3 scripts/zigux/check-lane05-local-archive-readme.py"
NEXT_STEP = "- name: Self-test current Lane 05 install-zig archive verification checker"

MIRROR_FILE_MARKER = 'mirror_file=".zig-toolchain/community-mirrors.txt"'
INITIAL_FILE_CLEANUP = 'rm -f "$archive_path" "$mirror_file"'
INITIAL_EXTRACT_CLEANUP = 'rm -rf "$extract_root"'
DOWNLOAD_FAILURE_FILE_CLEANUP = 'rm -f "$archive_path"'
DOWNLOAD_FAILURE_EXTRACT_CLEANUP = 'rm -rf "$extract_root"'
LOCAL_ATTEMPT = "if try_local_archive; then"
MIRROR_ATTEMPT = 'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then'
MIRROR_LOOP = 'while IFS= read -r mirror_url; do'
DIRECT_ATTEMPT = 'if try_download "$ZIGUX_ZIG_URL"; then'
FAIL_MESSAGE = "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org"

README_MARKERS = (
    "Before retrying the mirror or direct-download path",
    "clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle",
    "stale partial recovery state is discarded before the next fallback attempt",
    "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 local cleanup checker missing {label}: {marker}")


def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 local cleanup checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 local cleanup checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 local cleanup checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def require_line_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index: int | None = None
    later_index: int | None = None
    for index, current in enumerate(text.splitlines()):
        stripped = current.strip()
        if earlier_index is None and stripped == earlier:
            earlier_index = index
        if later_index is None and stripped == later:
            later_index = index
    if earlier_index is None or later_index is None:
        raise SystemExit(
            f"lane05 local cleanup checker missing ordered lines for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 local cleanup checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def require_adjacent_lines(text: str, first: str, second: str, label: str) -> None:
    stripped_lines = [current.strip() for current in text.splitlines()]
    for index in range(len(stripped_lines) - 1):
        if stripped_lines[index] == first and stripped_lines[index + 1] == second:
            return
    raise SystemExit(
        "lane05 local cleanup checker expected adjacent lines for "
        f"{label}: `{first}` then `{second}`"
    )


def check_workflow(text: str) -> None:
    for marker, label in (
        (SETUP_STEP, "setup step"),
        (MIRROR_FILE_MARKER, "mirror-file marker"),
        (INITIAL_FILE_CLEANUP, "initial cleanup marker"),
        (INITIAL_EXTRACT_CLEANUP, "initial extract cleanup marker"),
        (LOCAL_ATTEMPT, "local-first attempt"),
        (MIRROR_ATTEMPT, "mirror attempt"),
        (MIRROR_LOOP, "mirror loop"),
        (DIRECT_ATTEMPT, "direct-download attempt"),
        (DOWNLOAD_FAILURE_FILE_CLEANUP, "download failure cleanup marker"),
        (DOWNLOAD_FAILURE_EXTRACT_CLEANUP, "download failure extract cleanup marker"),
        (FAIL_MESSAGE, "final failure message"),
        (README_CHECK_STEP, "readme checker step"),
        (README_CHECK_CMD, "readme checker command"),
        (NEXT_STEP, "next lane anchor"),
    ):
        require_marker(text, marker, label)

    require_exact_line(text, f"run: {README_CHECK_CMD}", "readme checker command")
    require_exact_line(text, INITIAL_FILE_CLEANUP, "initial cleanup")
    require_exact_line(text, DOWNLOAD_FAILURE_FILE_CLEANUP, "download failure cleanup")

    require_order(text, MIRROR_FILE_MARKER, INITIAL_FILE_CLEANUP, "cleanup setup order")
    require_line_order(
        text,
        INITIAL_FILE_CLEANUP,
        INITIAL_EXTRACT_CLEANUP,
        "cleanup setup order",
    )
    require_order(text, INITIAL_EXTRACT_CLEANUP, LOCAL_ATTEMPT, "retry order")
    require_order(text, LOCAL_ATTEMPT, MIRROR_ATTEMPT, "retry order")
    require_order(text, MIRROR_ATTEMPT, MIRROR_LOOP, "mirror fetch order")
    require_order(text, MIRROR_LOOP, DIRECT_ATTEMPT, "fallback order")
    require_line_order(
        text,
        DIRECT_ATTEMPT,
        DOWNLOAD_FAILURE_FILE_CLEANUP,
        "fallback cleanup order",
    )
    require_adjacent_lines(
        text,
        DOWNLOAD_FAILURE_FILE_CLEANUP,
        DOWNLOAD_FAILURE_EXTRACT_CLEANUP,
        "download failure cleanup block",
    )
    require_order(text, DIRECT_ATTEMPT, FAIL_MESSAGE, "terminal failure order")
    require_order(text, README_CHECK_STEP, NEXT_STEP, "lane step order")


def check_readme(text: str) -> None:
    for marker in README_MARKERS:
        require_marker(text, marker, "README marker")

    require_order(
        text,
        "Before retrying the mirror or direct-download path",
        "falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL",
        "README cleanup before fallback wording",
    )


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          mirror_file=".zig-toolchain/community-mirrors.txt"
          rm -f "$archive_path" "$mirror_file"
          rm -rf "$extract_root"
          if try_local_archive; then
            download_success=1
          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
            while IFS= read -r mirror_url; do
              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
                download_success=1
                break
              fi
            done < "$mirror_file"
          fi
          if try_download "$ZIGUX_ZIG_URL"; then
            download_success=1
          fi
          rm -f "$archive_path"
          rm -rf "$extract_root"
          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2
      - name: Check current Lane 05 local archive README packet
        run: python3 scripts/zigux/check-lane05-local-archive-readme.py
      - name: Self-test current Lane 05 install-zig archive verification checker
        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test
"""
    good_readme = """# Zigux third-party archives

- Before retrying the mirror or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.
- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.
"""
    check_workflow(good_workflow)
    check_readme(good_readme)
    case_count = 1

    for broken_workflow, expected in (
        (
            good_workflow.replace(f"          {MIRROR_FILE_MARKER}\n", "", 1),
            MIRROR_FILE_MARKER,
        ),
        (
            good_workflow.replace(f"          {INITIAL_FILE_CLEANUP}\n", "", 1),
            INITIAL_FILE_CLEANUP,
        ),
        (
            good_workflow.replace(
                f"          {INITIAL_FILE_CLEANUP}\n          {INITIAL_EXTRACT_CLEANUP}\n",
                f"          {INITIAL_EXTRACT_CLEANUP}\n          {INITIAL_FILE_CLEANUP}\n",
                1,
            ),
            "cleanup setup order",
        ),
        (
            good_workflow.replace(
                f"          {LOCAL_ATTEMPT}\n"
                f'            download_success=1\n'
                f"          {MIRROR_ATTEMPT}\n",
                f"          {MIRROR_ATTEMPT}\n"
                f"          {LOCAL_ATTEMPT}\n"
                f'            download_success=1\n',
                1,
            ),
            "retry order",
        ),
        (
            good_workflow.replace(
                f"          {DIRECT_ATTEMPT}\n"
                f'            download_success=1\n'
                f"          fi\n"
                f"          {DOWNLOAD_FAILURE_FILE_CLEANUP}\n",
                f"          {DOWNLOAD_FAILURE_FILE_CLEANUP}\n"
                f"          {DIRECT_ATTEMPT}\n"
                f'            download_success=1\n'
                f"          fi\n",
                1,
            ),
            "fallback cleanup order",
        ),
        (
            good_workflow.replace(
                "      - name: Check current Lane 05 local archive README packet\n"
                "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py\n",
                "",
                1,
            ),
            README_CHECK_STEP,
        ),
    ):
        try:
            check_workflow(broken_workflow)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected workflow failure for {expected}")

    for broken_readme, expected in (
        (
            good_readme.replace(
                "clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle ",
                "",
                1,
            ),
            "README marker",
        ),
        (
            good_readme.replace(
                "- Before retrying the mirror or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.\n"
                "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.\n",
                "- If the repo-local archive is unavailable, `.github/workflows/zigux-bootstrap.yml` falls back to `community-mirrors.txt` before the direct `ziglang.org` download URL.\n"
                "- Before retrying the mirror or direct-download path, `.github/workflows/zigux-bootstrap.yml` clears the extracted `.zig-toolchain` root plus the cached `community-mirrors.txt` handle so stale partial recovery state is discarded before the next fallback attempt.\n",
                1,
            ),
            "README cleanup before fallback wording",
        ),
    ):
        try:
            check_readme(broken_readme)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected README failure for {expected}")

    print("LANE05_LOCAL_FIRST_ARCHIVE_CLEANUP_SELF_TEST=pass")
    print(f"LANE05_LOCAL_FIRST_ARCHIVE_CLEANUP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that Lane 05 bootstrap keeps the local-first archive cleanup and "
            "retry order explicit."
        )
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap.yml",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=README_PATH,
        help="Path to third_party/README.md",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_workflow(args.workflow.read_text(encoding="utf-8"))
    check_readme(args.readme.read_text(encoding="utf-8"))
    print("LANE05_LOCAL_FIRST_ARCHIVE_CLEANUP=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())

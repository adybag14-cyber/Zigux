#!/usr/bin/env python3
"""Fail-close guard for Lane 05 bootstrap retry cleanup behavior."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

SETUP_STEP = "- name: Setup pinned Zig toolchain"
NEXT_STEP = "- name: Compile current scripts"

INITIAL_ARCHIVE_CLEANUP = 'rm -f "$archive_path" "$mirror_file"'
INITIAL_EXTRACT_CLEANUP = 'rm -rf "$extract_root"'
LOCAL_HELPER = "try_local_archive() {"
LOCAL_GUARD = 'if [ ! -f "$repo_archive_path" ]; then'
LOCAL_VALIDATE = (
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive '
    '"$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then'
)
LOCAL_EXTRACT = 'tar -xJf "$repo_archive_path" -C .zig-toolchain'
LOCAL_REVALIDATE = 'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then'
LOCAL_FAILURE_CLEANUP = 'rm -rf "$extract_root"'
DOWNLOAD_HELPER = "try_download() {"
DOWNLOAD_FETCH = 'if curl -L --fail "$url" -o "$archive_path"; then'
DOWNLOAD_VALIDATE = (
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive '
    '"$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then'
)
DOWNLOAD_EXTRACT = 'tar -xJf "$archive_path" -C .zig-toolchain'
DOWNLOAD_REVALIDATE = 'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then'
DOWNLOAD_ARCHIVE_CLEANUP = 'rm -f "$archive_path"'
DOWNLOAD_EXTRACT_CLEANUP = 'rm -rf "$extract_root"'
DOWNLOAD_CLEANUP_SNIPPET = (
    'rm -f "$archive_path"\n'
    '              rm -rf "$extract_root"'
)
MIRROR_FETCH = 'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then'
MIRROR_LOOP = "while IFS= read -r mirror_url; do"
MIRROR_TRY = 'if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then'
DIRECT_FALLBACK = 'if try_download "$ZIGUX_ZIG_URL"; then'
FINAL_FAILURE = "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org"

GOOD_WORKFLOW = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          archive_path=".zig-toolchain/$ZIGUX_ZIG_FILENAME"
          extract_root="$GITHUB_WORKSPACE/.zig-toolchain/zig-$ZIGUX_ZIG_TARGET-$ZIGUX_ZIG_CHANNEL"
          mirror_file=".zig-toolchain/community-mirrors.txt"
          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"
          rm -f "$archive_path" "$mirror_file"
          rm -rf "$extract_root"
          try_local_archive() {
            if [ ! -f "$repo_archive_path" ]; then
              return 1
            fi
            if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
              tar -xJf "$repo_archive_path" -C .zig-toolchain
              zig_path="$extract_root/zig"
              if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
                return 0
              fi
            fi
            rm -rf "$extract_root"
            return 1
          }
          try_download() {
            local url="$1"
            if curl -L --fail "$url" -o "$archive_path"; then
              if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then
                tar -xJf "$archive_path" -C .zig-toolchain
                zig_path="$extract_root/zig"
                if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then
                  return 0
                fi
              fi
              rm -f "$archive_path"
              rm -rf "$extract_root"
            fi
            return 1
          }
          download_success=0
          if try_local_archive; then
            download_success=1
          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then
            while IFS= read -r mirror_url; do
              [ -n "$mirror_url" ] || continue
              if try_download "${mirror_url%/}/$ZIGUX_ZIG_FILENAME?source=github-zigux-bootstrap"; then
                download_success=1
                break
              fi
            done < "$mirror_file"
          fi
          if [ "$download_success" -ne 1 ]; then
            if try_download "$ZIGUX_ZIG_URL"; then
              download_success=1
            fi
          fi
          if [ "$download_success" -ne 1 ]; then
            echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2
            exit 1
          fi
      - name: Compile current scripts
        run: python3 -m py_compile scripts/zigux/*.py
"""


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 retry-cleanup checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 retry-cleanup checker expected exactly "
            f"{expected} occurrences of {label} `{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(f"lane05 retry-cleanup checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 retry-cleanup checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def slice_between(text: str, start: str, end: str, label: str) -> str:
    start_index = text.find(start)
    end_index = text.find(end)
    if start_index == -1 or end_index == -1 or start_index >= end_index:
        raise SystemExit(f"lane05 retry-cleanup checker could not isolate {label}")
    return text[start_index:end_index]


def check_workflow_text(text: str) -> tuple[int, int, int]:
    required_markers = (
        SETUP_STEP,
        NEXT_STEP,
        INITIAL_ARCHIVE_CLEANUP,
        INITIAL_EXTRACT_CLEANUP,
        LOCAL_HELPER,
        LOCAL_GUARD,
        LOCAL_VALIDATE,
        LOCAL_EXTRACT,
        LOCAL_REVALIDATE,
        DOWNLOAD_HELPER,
        DOWNLOAD_FETCH,
        DOWNLOAD_VALIDATE,
        DOWNLOAD_EXTRACT,
        DOWNLOAD_REVALIDATE,
        DOWNLOAD_ARCHIVE_CLEANUP,
        DOWNLOAD_EXTRACT_CLEANUP,
        MIRROR_FETCH,
        MIRROR_LOOP,
        MIRROR_TRY,
        DIRECT_FALLBACK,
        FINAL_FAILURE,
    )
    for marker in required_markers:
        require_marker(text, marker, "workflow marker")

    local_section = slice_between(text, LOCAL_HELPER, DOWNLOAD_HELPER, "local helper section")
    download_section = slice_between(text, DOWNLOAD_HELPER, "download_success=0", "download helper section")
    fallback_section = slice_between(text, "download_success=0", NEXT_STEP, "fallback section")

    require_exact_count(text, SETUP_STEP, 1, "setup step")
    require_exact_count(text, INITIAL_ARCHIVE_CLEANUP, 1, "initial archive cleanup")
    require_exact_count(text, INITIAL_EXTRACT_CLEANUP, 3, "extract-root cleanup")
    require_exact_count(local_section, LOCAL_REVALIDATE, 1, "local zig revalidation guard")
    require_exact_count(download_section, DOWNLOAD_REVALIDATE, 1, "download zig revalidation guard")
    require_exact_count(download_section, DOWNLOAD_ARCHIVE_CLEANUP, 1, "download archive cleanup command")
    require_exact_count(download_section, DOWNLOAD_CLEANUP_SNIPPET, 1, "download cleanup snippet")

    require_order(text, SETUP_STEP, INITIAL_ARCHIVE_CLEANUP, "startup cleanup order")
    require_order(text, INITIAL_ARCHIVE_CLEANUP, INITIAL_EXTRACT_CLEANUP, "startup cleanup order")
    require_order(text, INITIAL_EXTRACT_CLEANUP, LOCAL_HELPER, "startup cleanup versus local helper")
    require_order(local_section, LOCAL_GUARD, LOCAL_VALIDATE, "local helper validation order")
    require_order(local_section, LOCAL_VALIDATE, LOCAL_EXTRACT, "local helper extraction order")
    require_order(local_section, LOCAL_REVALIDATE, LOCAL_FAILURE_CLEANUP, "local retry cleanup order")
    require_order(download_section, DOWNLOAD_FETCH, DOWNLOAD_VALIDATE, "download validation order")
    require_order(download_section, DOWNLOAD_VALIDATE, DOWNLOAD_EXTRACT, "download extraction order")
    require_order(download_section, DOWNLOAD_REVALIDATE, DOWNLOAD_ARCHIVE_CLEANUP, "download cleanup order")
    require_order(download_section, DOWNLOAD_ARCHIVE_CLEANUP, DOWNLOAD_EXTRACT_CLEANUP, "download cleanup order")
    require_order(fallback_section, MIRROR_FETCH, MIRROR_LOOP, "mirror loop order")
    require_order(fallback_section, MIRROR_TRY, DIRECT_FALLBACK, "mirror before direct fallback")
    require_order(fallback_section, DIRECT_FALLBACK, FINAL_FAILURE, "direct fallback before final failure")
    require_order(text, FINAL_FAILURE, NEXT_STEP, "failure block before next workflow step")

    return (2, 4, 4)


def validate_root(root: Path) -> tuple[int, int, int]:
    workflow_path = root / WORKFLOW_PATH
    try:
        workflow_text = workflow_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing workflow file: {workflow_path}") from exc
    return check_workflow_text(workflow_text)


def write_sample_root(root: Path) -> None:
    workflow_path = root / WORKFLOW_PATH
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(GOOD_WORKFLOW, encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_retry_cleanup_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            assert validate_root(root) == (2, 4, 4)
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_retry_cleanup_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            workflow_path = root / WORKFLOW_PATH
            mutator(workflow_path)
            try:
                validate_root(root)
            except SystemExit as exc:
                message = str(exc)
                assert expected_substring in message, message
                case_count += 1
                return
            raise AssertionError("expected validate_root to fail")

    expect_pass()
    expect_failure(
        lambda workflow_path: workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(INITIAL_ARCHIVE_CLEANUP + "\n", "", 1),
            encoding="utf-8",
        ),
        "missing workflow marker",
    )
    expect_failure(
        lambda workflow_path: workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                f"{DOWNLOAD_ARCHIVE_CLEANUP}\n              {DOWNLOAD_EXTRACT_CLEANUP}",
                f"{DOWNLOAD_EXTRACT_CLEANUP}\n              {DOWNLOAD_ARCHIVE_CLEANUP}",
                1,
            ),
            encoding="utf-8",
        ),
        "download cleanup",
    )
    expect_failure(
        lambda workflow_path: workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                f"{MIRROR_TRY}\n                download_success=1\n                break\n              fi\n            done < \"$mirror_file\"\n          fi\n          if [ \"$download_success\" -ne 1 ]; then\n            {DIRECT_FALLBACK}",
                f"{DIRECT_FALLBACK}\n              download_success=1\n            fi\n          elif {MIRROR_TRY}",
                1,
            ),
            encoding="utf-8",
        ),
        "mirror before direct fallback",
    )
    expect_failure(
        lambda workflow_path: workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                f"{LOCAL_REVALIDATE}\n                return 0\n              fi\n            fi\n            {LOCAL_FAILURE_CLEANUP}",
                f"{LOCAL_FAILURE_CLEANUP}\n            if python3 scripts/zigux/check-zig-toolchain.py --zig \"$zig_path\"; then\n                return 0\n              fi",
                1,
            ),
            encoding="utf-8",
        ),
        "local retry cleanup order",
    )
    expect_failure(
        lambda workflow_path: workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(DOWNLOAD_ARCHIVE_CLEANUP + "\n", "", 1),
            encoding="utf-8",
        ),
        "archive cleanup",
    )

    print("LANE05_BOOTSTRAP_RETRY_CLEANUP_SELF_TEST=pass")
    print(f"LANE05_BOOTSTRAP_RETRY_CLEANUP_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 bootstrap retry-cleanup contract."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for focused replay validation.",
    )
    parser.add_argument(
        "--workflow-stdin",
        action="store_true",
        help="Validate workflow text from stdin instead of reading a repo root.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        return 0

    if args.workflow_stdin:
        startup_count, retry_count, fallback_count = check_workflow_text(sys.stdin.read())
    else:
        startup_count, retry_count, fallback_count = validate_root(args.root)
    print("LANE05_BOOTSTRAP_RETRY_CLEANUP=pass")
    print(f"LANE05_BOOTSTRAP_RETRY_CLEANUP_STARTUP_MARKER_COUNT={startup_count}")
    print(f"LANE05_BOOTSTRAP_RETRY_CLEANUP_RETRY_MARKER_COUNT={retry_count}")
    print(f"LANE05_BOOTSTRAP_RETRY_CLEANUP_FALLBACK_MARKER_COUNT={fallback_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

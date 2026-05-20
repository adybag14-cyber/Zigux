#!/usr/bin/env python3
"""Fail-close guard for Lane 05 extracted Zig revalidation in bootstrap CI."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

CHECKOUT_STEP = "- name: Checkout"
SETUP_STEP = "- name: Setup pinned Zig toolchain"
NEXT_STEP = "- name: Compile current scripts"

LOCAL_ARCHIVE_VALIDATE = (
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive '
    '"$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then'
)
LOCAL_ARCHIVE_EXTRACT = 'tar -xJf "$repo_archive_path" -C .zig-toolchain'
LOCAL_ZIG_PATH = 'zig_path="$extract_root/zig"'
LOCAL_ZIG_VALIDATE = 'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then'
LOCAL_EXTRACT_CLEANUP = 'rm -rf "$extract_root"'

DOWNLOAD_HELPER = "try_download() {"
DOWNLOAD_FETCH = 'if curl -L --fail "$url" -o "$archive_path"; then'
DOWNLOAD_ARCHIVE_VALIDATE = (
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive '
    '"$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then'
)
DOWNLOAD_ARCHIVE_EXTRACT = 'tar -xJf "$archive_path" -C .zig-toolchain'
DOWNLOAD_ZIG_VALIDATE = 'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then'
DOWNLOAD_ARCHIVE_CLEANUP = 'rm -f "$archive_path"'
FAIL_MESSAGE = "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org"

LOCAL_REVALIDATION_SNIPPET = "\n".join(
    (
        LOCAL_ARCHIVE_EXTRACT,
        f"              {LOCAL_ZIG_PATH}",
        f"              {LOCAL_ZIG_VALIDATE}",
    )
)
DOWNLOAD_REVALIDATION_SNIPPET = "\n".join(
    (
        DOWNLOAD_ARCHIVE_EXTRACT,
        f"                {LOCAL_ZIG_PATH}",
        f"                {DOWNLOAD_ZIG_VALIDATE}",
    )
)

GOOD_WORKFLOW = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Checkout
        uses: actions/checkout@v6.0.2
      - name: Setup pinned Zig toolchain
        run: |
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
          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2
      - name: Compile current scripts
        run: python3 -m py_compile scripts/zigux/*.py
"""


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 extracted-zig checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 extracted-zig checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(f"lane05 extracted-zig checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 extracted-zig checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def require_exact_snippet_count(text: str, snippet: str, expected: int, label: str) -> None:
    actual = text.count(snippet)
    if actual != expected:
        raise SystemExit(
            "lane05 extracted-zig checker expected exactly "
            f"{expected} occurrences of {label}, found {actual}"
        )


def check_workflow(text: str) -> tuple[int, int]:
    required_markers = (
        CHECKOUT_STEP,
        SETUP_STEP,
        NEXT_STEP,
        LOCAL_ARCHIVE_VALIDATE,
        LOCAL_ARCHIVE_EXTRACT,
        LOCAL_ZIG_PATH,
        LOCAL_ZIG_VALIDATE,
        LOCAL_EXTRACT_CLEANUP,
        DOWNLOAD_HELPER,
        DOWNLOAD_FETCH,
        DOWNLOAD_ARCHIVE_VALIDATE,
        DOWNLOAD_ARCHIVE_EXTRACT,
        DOWNLOAD_ZIG_VALIDATE,
        DOWNLOAD_ARCHIVE_CLEANUP,
        FAIL_MESSAGE,
    )
    for marker in required_markers:
        require_marker(text, marker, "workflow marker")

    require_exact_count(text, SETUP_STEP, 1, "workflow step")
    require_exact_count(text, LOCAL_ZIG_VALIDATE, 2, "extracted zig validation command")
    require_exact_count(text, LOCAL_ARCHIVE_EXTRACT, 1, "repo-local archive extract")
    require_exact_count(text, DOWNLOAD_ARCHIVE_EXTRACT, 1, "download archive extract")
    require_exact_count(text, LOCAL_EXTRACT_CLEANUP, 2, "extract-root cleanup")
    require_exact_count(text, DOWNLOAD_ARCHIVE_CLEANUP, 1, "download archive cleanup")
    require_exact_snippet_count(
        text,
        LOCAL_REVALIDATION_SNIPPET,
        1,
        "repo-local extracted zig revalidation snippet",
    )
    require_exact_snippet_count(
        text,
        DOWNLOAD_REVALIDATION_SNIPPET,
        1,
        "download extracted zig revalidation snippet",
    )

    require_order(text, CHECKOUT_STEP, SETUP_STEP, "workflow step order")
    require_order(text, SETUP_STEP, NEXT_STEP, "workflow step order")

    require_order(text, LOCAL_ARCHIVE_VALIDATE, LOCAL_ARCHIVE_EXTRACT, "repo-local archive validation order")
    require_order(text, LOCAL_ZIG_VALIDATE, LOCAL_EXTRACT_CLEANUP, "repo-local cleanup order")

    require_order(text, DOWNLOAD_HELPER, DOWNLOAD_FETCH, "download helper order")
    require_order(text, DOWNLOAD_FETCH, DOWNLOAD_ARCHIVE_VALIDATE, "download validation order")
    require_order(text, DOWNLOAD_ARCHIVE_VALIDATE, DOWNLOAD_ARCHIVE_EXTRACT, "download extract order")
    require_order(text, DOWNLOAD_ZIG_VALIDATE, DOWNLOAD_ARCHIVE_CLEANUP, "download cleanup order")
    require_order(text, DOWNLOAD_ARCHIVE_CLEANUP, FAIL_MESSAGE, "download failure message order")

    return 4, 5


def validate_root(root: Path) -> tuple[int, int]:
    workflow_path = root / WORKFLOW_PATH
    try:
        workflow_text = workflow_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing workflow file: {workflow_path}") from exc
    return check_workflow(workflow_text)


def write_sample_root(root: Path) -> None:
    workflow_path = root / WORKFLOW_PATH
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(GOOD_WORKFLOW, encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_extract_revalidation_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            assert validate_root(root) == (4, 5)
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_extract_revalidation_fail_") as tmp_dir:
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
            workflow_path.read_text(encoding="utf-8").replace(LOCAL_ZIG_VALIDATE, "", 1),
            encoding="utf-8",
        ),
        "expected exactly 2 occurrences of extracted zig validation command",
    )
    expect_failure(
        lambda workflow_path: workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(DOWNLOAD_ZIG_VALIDATE, "", 1),
            encoding="utf-8",
        ),
        "expected exactly 2 occurrences of extracted zig validation command",
    )
    expect_failure(
        lambda workflow_path: workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                LOCAL_REVALIDATION_SNIPPET,
                "\n".join(
                    (
                        f"              {LOCAL_ZIG_PATH}",
                        LOCAL_ARCHIVE_EXTRACT,
                        f"              {LOCAL_ZIG_VALIDATE}",
                    )
                ),
                1,
            ),
            encoding="utf-8",
        ),
        "repo-local extracted zig revalidation snippet",
    )
    expect_failure(
        lambda workflow_path: workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                DOWNLOAD_REVALIDATION_SNIPPET,
                "\n".join(
                    (
                        f"                {LOCAL_ZIG_PATH}",
                        DOWNLOAD_ARCHIVE_EXTRACT,
                        f"                {DOWNLOAD_ZIG_VALIDATE}",
                    )
                ),
                1,
            ),
            encoding="utf-8",
        ),
        "download extracted zig revalidation snippet",
    )
    expect_failure(
        lambda workflow_path: workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(DOWNLOAD_ARCHIVE_CLEANUP + "\n", "", 1),
            encoding="utf-8",
        ),
        'missing workflow marker: rm -f "$archive_path"',
    )

    print("LANE05_EXTRACTED_ZIG_REVALIDATION_SELF_TEST=pass")
    print(f"LANE05_EXTRACTED_ZIG_REVALIDATION_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 05 extracted-zig revalidation packet."
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
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        return 0

    local_marker_count, download_marker_count = validate_root(args.root)
    print("LANE05_EXTRACTED_ZIG_REVALIDATION=pass")
    print(f"LANE05_EXTRACTED_ZIG_REVALIDATION_LOCAL_MARKER_COUNT={local_marker_count}")
    print(f"LANE05_EXTRACTED_ZIG_REVALIDATION_DOWNLOAD_MARKER_COUNT={download_marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

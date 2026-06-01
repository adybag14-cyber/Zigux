#!/usr/bin/env python3
"""Fail-close guard for the Lane 05 validated-Zig handoff packet."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

SETUP_STEP = "- name: Setup pinned Zig toolchain"
FAILURE_GATE = 'if [ "$download_success" -ne 1 ]; then'
FAILURE_MESSAGE = "failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org"
FINAL_ZIG_PATH = 'zig_path="$extract_root/zig"'
PATH_EXPORT = 'echo "$extract_root" >> "$GITHUB_PATH"'
FINAL_VERSION = '"$zig_path" version'
NEXT_STEP = "- name: Compile current scripts"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 zig-path export checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 zig-path export checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 zig-path export checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 zig-path export checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def require_order_before_last(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.rfind(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 zig-path export checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 zig-path export checker expected "
            f"{label} `{earlier}` before final `{later}`"
        )


def check_workflow(text: str) -> int:
    require_marker(text, SETUP_STEP, "workflow setup step")
    require_marker(text, FAILURE_GATE, "workflow failure gate")
    require_marker(text, FAILURE_MESSAGE, "workflow failure message")
    require_marker(text, FINAL_ZIG_PATH, "workflow final zig path marker")
    require_marker(text, PATH_EXPORT, "workflow PATH export marker")
    require_marker(text, FINAL_VERSION, "workflow final zig version probe")
    require_marker(text, NEXT_STEP, "workflow next-step anchor")

    require_exact_count(text, FAILURE_MESSAGE, 1, "workflow failure message")
    require_exact_count(text, PATH_EXPORT, 1, "workflow PATH export marker")
    require_exact_count(text, FINAL_VERSION, 1, "workflow final zig version probe")

    require_order(text, SETUP_STEP, FAILURE_GATE, "workflow setup flow")
    require_order_before_last(text, FAILURE_MESSAGE, FINAL_ZIG_PATH, "workflow success handoff order")
    require_order_before_last(text, FINAL_ZIG_PATH, PATH_EXPORT, "workflow finalization order")
    require_order(text, PATH_EXPORT, FINAL_VERSION, "workflow PATH export order")
    require_order(text, FINAL_VERSION, NEXT_STEP, "workflow step order")

    return sum(
        text.count(marker)
        for marker in (
            FAILURE_GATE,
            FINAL_ZIG_PATH,
            PATH_EXPORT,
            FINAL_VERSION,
        )
    )


def write_sample_root(root: Path) -> None:
    workflow_path = root / WORKFLOW_PATH
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          download_success=0
          if [ "$download_success" -ne 1 ]; then
            echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2
            exit 1
          fi
          zig_path="$extract_root/zig"
          echo "$extract_root" >> "$GITHUB_PATH"
          "$zig_path" version
      - name: Compile current scripts
        run: python3 -m py_compile scripts/zigux/check-zig-toolchain.py
""",
        encoding="utf-8",
    )


def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
        run: |
          download_success=0
          if [ "$download_success" -ne 1 ]; then
            echo 'failed to install a verified pinned Zig archive from third_party, canonical adybag14-cyber/zig release, mirrors, or ziglang.org' >&2
            exit 1
          fi
          zig_path="$extract_root/zig"
          echo "$extract_root" >> "$GITHUB_PATH"
          "$zig_path" version
      - name: Compile current scripts
        run: python3 -m py_compile scripts/zigux/check-zig-toolchain.py
"""
    marker_count = check_workflow(good_workflow)
    assert marker_count == 4
    case_count = 1

    def expect_failure(bad_workflow: str, expected_substring: str) -> None:
        nonlocal case_count
        try:
            check_workflow(bad_workflow)
        except SystemExit as exc:
            assert expected_substring in str(exc), str(exc)
            case_count += 1
            return
        raise AssertionError("expected workflow validation to fail")

    expect_failure(
        good_workflow.replace(PATH_EXPORT + "\n", "", 1),
        PATH_EXPORT,
    )
    expect_failure(
        good_workflow.replace(FINAL_VERSION + "\n", "", 1),
        FINAL_VERSION,
    )
    expect_failure(
        good_workflow.replace(FAILURE_GATE + "\n", "", 1),
        FAILURE_GATE,
    )
    expect_failure(
        good_workflow.replace(
            '          zig_path="$extract_root/zig"\n'
            '          echo "$extract_root" >> "$GITHUB_PATH"\n',
            '          echo "$extract_root" >> "$GITHUB_PATH"\n'
            '          zig_path="$extract_root/zig"\n',
            1,
        ),
        "workflow finalization order",
    )
    expect_failure(
        good_workflow.replace(
            '          echo "$extract_root" >> "$GITHUB_PATH"\n'
            '          "$zig_path" version\n',
            '          echo "$extract_root" >> "$GITHUB_PATH"\n'
            '          echo "$extract_root" >> "$GITHUB_PATH"\n'
            '          "$zig_path" version\n',
            1,
        ),
        PATH_EXPORT,
    )

    print("LANE05_ZIG_PATH_EXPORT_SELF_TEST=pass")
    print(f"LANE05_ZIG_PATH_EXPORT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 bootstrap exports and probes the validated Zig path."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for checker validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    workflow_text = (args.root.resolve() / WORKFLOW_PATH).read_text(encoding="utf-8")
    marker_count = check_workflow(workflow_text)
    print("LANE05_ZIG_PATH_EXPORT=pass")
    print(f"LANE05_ZIG_PATH_EXPORT_ROOT={args.root.resolve()}")
    print(f"LANE05_ZIG_PATH_EXPORT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

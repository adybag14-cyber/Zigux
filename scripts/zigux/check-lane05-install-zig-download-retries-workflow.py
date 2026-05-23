#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

INDEX_FALLBACK_CHECK_STEP = "- name: Check current Lane 05 install-zig index fallback packet"
DOWNLOAD_RETRIES_SELF_TEST_STEP = (
    "- name: Self-test current Lane 05 install-zig download retries checker"
)
DOWNLOAD_RETRIES_SELF_TEST_CMD = (
    "run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py --self-test"
)
DOWNLOAD_RETRIES_CHECK_STEP = (
    "- name: Check current Lane 05 install-zig download retries packet"
)
DOWNLOAD_RETRIES_CHECK_CMD = (
    "run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py"
)
ARCHIVE_VERIFICATION_SELF_TEST_STEP = (
    "- name: Self-test current Lane 05 install-zig archive verification checker"
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(
            f"lane05 download-retries workflow checker missing {label}: {marker}"
        )


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line.strip() == marker)
    if actual != expected:
        raise SystemExit(
            "lane05 download-retries workflow checker expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 download-retries workflow checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 download-retries workflow checker expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    require_marker(text, INDEX_FALLBACK_CHECK_STEP, "index-fallback anchor step")
    require_marker(
        text,
        DOWNLOAD_RETRIES_SELF_TEST_STEP,
        "download-retries self-test step",
    )
    require_marker(
        text,
        DOWNLOAD_RETRIES_SELF_TEST_CMD,
        "download-retries self-test command",
    )
    require_marker(text, DOWNLOAD_RETRIES_CHECK_STEP, "download-retries check step")
    require_marker(text, DOWNLOAD_RETRIES_CHECK_CMD, "download-retries check command")
    require_marker(
        text,
        ARCHIVE_VERIFICATION_SELF_TEST_STEP,
        "archive-verification anchor step",
    )

    require_exact_line_count(
        text,
        DOWNLOAD_RETRIES_SELF_TEST_STEP,
        1,
        "download-retries self-test step",
    )
    require_exact_line_count(
        text,
        DOWNLOAD_RETRIES_SELF_TEST_CMD,
        1,
        "download-retries self-test command",
    )
    require_exact_line_count(
        text,
        DOWNLOAD_RETRIES_CHECK_STEP,
        1,
        "download-retries check step",
    )
    require_exact_line_count(
        text,
        DOWNLOAD_RETRIES_CHECK_CMD,
        1,
        "download-retries check command",
    )

    require_order(
        text,
        INDEX_FALLBACK_CHECK_STEP,
        DOWNLOAD_RETRIES_SELF_TEST_STEP,
        "workflow step order",
    )
    require_order(
        text,
        DOWNLOAD_RETRIES_SELF_TEST_STEP,
        DOWNLOAD_RETRIES_CHECK_STEP,
        "workflow step order",
    )
    require_order(
        text,
        DOWNLOAD_RETRIES_CHECK_STEP,
        ARCHIVE_VERIFICATION_SELF_TEST_STEP,
        "workflow step order",
    )


def sample_workflow() -> str:
    return """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Check current Lane 05 install-zig index fallback packet
        run: python3 scripts/zigux/check-lane05-install-zig-index-fallback.py
      - name: Self-test current Lane 05 install-zig download retries checker
        run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py --self-test
      - name: Check current Lane 05 install-zig download retries packet
        run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py
      - name: Self-test current Lane 05 install-zig archive verification checker
        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test
"""


def run_self_test() -> int:
    workflow = sample_workflow()
    check_workflow(workflow)
    case_count = 1

    missing_self_test = workflow.replace(
        "      - name: Self-test current Lane 05 install-zig download retries checker\n"
        "        run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py --self-test\n",
        "",
        1,
    )
    try:
        check_workflow(missing_self_test)
    except SystemExit as exc:
        assert "download retries checker" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing download-retries self-test step failure")

    missing_check = workflow.replace(
        "      - name: Check current Lane 05 install-zig download retries packet\n"
        "        run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py\n",
        "",
        1,
    )
    try:
        check_workflow(missing_check)
    except SystemExit as exc:
        assert "download retries packet" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing download-retries check step failure")

    duplicate_check = workflow.replace(
        "      - name: Check current Lane 05 install-zig download retries packet\n"
        "        run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py\n",
        "      - name: Check current Lane 05 install-zig download retries packet\n"
        "        run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py\n"
        "      - name: Check current Lane 05 install-zig download retries packet\n"
        "        run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py\n",
        1,
    )
    try:
        check_workflow(duplicate_check)
    except SystemExit as exc:
        assert "expected exactly 1 occurrences" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate download-retries check step failure")

    reordered_steps = workflow.replace(
        "      - name: Check current Lane 05 install-zig index fallback packet\n"
        "        run: python3 scripts/zigux/check-lane05-install-zig-index-fallback.py\n"
        "      - name: Self-test current Lane 05 install-zig download retries checker\n"
        "        run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py --self-test\n",
        "      - name: Self-test current Lane 05 install-zig download retries checker\n"
        "        run: python3 scripts/zigux/check-lane05-install-zig-download-retries.py --self-test\n"
        "      - name: Check current Lane 05 install-zig index fallback packet\n"
        "        run: python3 scripts/zigux/check-lane05-install-zig-index-fallback.py\n",
        1,
    )
    try:
        check_workflow(reordered_steps)
    except SystemExit as exc:
        assert "workflow step order" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered download-retries step failure")

    print("LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_WORKFLOW_SELF_TEST=pass")
    print(
        "LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_WORKFLOW_SELF_TEST_CASE_COUNT="
        f"{case_count}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Lane 05 bootstrap workflow runs the install-zig "
            "download-retries checker before archive verification."
        )
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
    print("LANE05_INSTALL_ZIG_DOWNLOAD_RETRIES_WORKFLOW=pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())

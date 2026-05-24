#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")

INSTALL_SELF_TEST_STEP = "- name: Self-test current Zig installer helper"
INSTALL_SELF_TEST_CMD = "python3 scripts/zigux/install-zig.py --self-test"
STAGE_HELPER_SELF_TEST_STEP = "- name: Self-test current staged pinned Zig archive helper"
STAGE_HELPER_SELF_TEST_CMD = "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test"
SPLIT_HELPER_SELF_TEST_STEP = "- name: Self-test current split pinned Zig archive helper"
SPLIT_HELPER_SELF_TEST_CMD = "python3 scripts/zigux/split-pinned-zig-archive.py --self-test"
NEXT_STEP = "- name: Self-test current Lane 05 stage helper contract checker"

HELPER_MARKERS = (
    "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=",
    "expect_split_failure(",
    "split_archive_chunk_bytes_",
    "split_archive_manifest_",
    "split_archive_invalid_b64_",
    "split_archive_sha_mismatch_",
    '"output directory must be empty"',
    '"chunk_bytes must be positive"',
    '"missing expected shard"',
    '"expected reconstructed archive to have sha256"',
    'raise AssertionError("expected invalid base64 failure")',
)

EXACT_ONCE_HELPER_MARKERS = (
    "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=",
    "split_archive_chunk_bytes_",
    "split_archive_manifest_",
    "split_archive_invalid_b64_",
    "split_archive_sha_mismatch_",
)

ORDERED_HELPER_MARKERS = (
    ("split_archive_chunk_bytes_", "split_archive_manifest_"),
    ("split_archive_manifest_", "split_archive_invalid_b64_"),
    ("split_archive_invalid_b64_", "split_archive_sha_mismatch_"),
    ('"output directory must be empty"', '"chunk_bytes must be positive"'),
    ('"chunk_bytes must be positive"', '"missing expected shard"'),
    ('"missing expected shard"', '"expected reconstructed archive to have sha256"'),
    ("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass", "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT="),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc



def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 split-helper selftest checker missing {label}: {marker}")



def require_exact_line(text: str, line: str, label: str) -> None:
    count = sum(1 for current in text.splitlines() if current.strip() == line)
    if count != 1:
        raise SystemExit(
            "lane05 split-helper selftest checker expected exactly "
            f"1 {label} line `{line}`, found {count}"
        )



def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise SystemExit(
            "lane05 split-helper selftest checker expected exactly "
            f"{expected} {label} markers `{marker}`, found {actual}"
        )



def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 split-helper selftest checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 split-helper selftest checker expected "
            f"{label} `{earlier}` before `{later}`"
        )



def check_workflow(text: str) -> None:
    for marker, label in (
        (INSTALL_SELF_TEST_STEP, "installer self-test step"),
        (INSTALL_SELF_TEST_CMD, "installer self-test command"),
        (STAGE_HELPER_SELF_TEST_STEP, "stage helper self-test step"),
        (STAGE_HELPER_SELF_TEST_CMD, "stage helper self-test command"),
        (SPLIT_HELPER_SELF_TEST_STEP, "split helper self-test step"),
        (SPLIT_HELPER_SELF_TEST_CMD, "split helper self-test command"),
        (NEXT_STEP, "next lane05 anchor"),
    ):
        require_marker(text, marker, label)

    for line, label in (
        (f"run: {INSTALL_SELF_TEST_CMD}", "installer self-test command"),
        (f"run: {STAGE_HELPER_SELF_TEST_CMD}", "stage helper self-test command"),
        (f"run: {SPLIT_HELPER_SELF_TEST_CMD}", "split helper self-test command"),
    ):
        require_exact_line(text, line, label)

    for step, label in (
        (STAGE_HELPER_SELF_TEST_STEP, "stage helper self-test step"),
        (SPLIT_HELPER_SELF_TEST_STEP, "split helper self-test step"),
    ):
        require_exact_line(text, step, label)

    require_order(text, INSTALL_SELF_TEST_STEP, STAGE_HELPER_SELF_TEST_STEP, "lane05 step order")
    require_order(
        text,
        STAGE_HELPER_SELF_TEST_STEP,
        SPLIT_HELPER_SELF_TEST_STEP,
        "lane05 step order",
    )
    require_order(text, SPLIT_HELPER_SELF_TEST_STEP, NEXT_STEP, "lane05 step order")



def check_helper(text: str) -> None:
    for marker in HELPER_MARKERS:
        require_marker(text, marker, "helper self-test marker")

    for marker in EXACT_ONCE_HELPER_MARKERS:
        require_exact_count(text, marker, 1, "helper self-test")

    for earlier, later in ORDERED_HELPER_MARKERS:
        require_order(text, earlier, later, "helper self-test order")



def run_self_test() -> int:
    good_workflow = """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Self-test current Zig installer helper
        run: python3 scripts/zigux/install-zig.py --self-test
      - name: Self-test current staged pinned Zig archive helper
        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test
      - name: Self-test current split pinned Zig archive helper
        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test
      - name: Self-test current Lane 05 stage helper contract checker
        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test
"""
    good_helper = """def run_self_test() -> int:
    def expect_split_failure(mutator, expected_substring: str) -> None:
        pass
    def expect_split_failure_again(mutator, expected_substring: str) -> None:
        pass
    with tempfile.TemporaryDirectory(prefix=\"split_archive_chunk_bytes_\") as tmp_dir:
        pass
    with tempfile.TemporaryDirectory(prefix=\"split_archive_manifest_\") as tmp_dir:
        pass
    with tempfile.TemporaryDirectory(prefix=\"split_archive_invalid_b64_\") as tmp_dir:
        pass
    with tempfile.TemporaryDirectory(prefix=\"split_archive_sha_mismatch_\") as tmp_dir:
        pass
    error_a = \"output directory must be empty\"
    error_b = \"chunk_bytes must be positive\"
    error_c = \"missing expected shard\"
    error_d = \"expected reconstructed archive to have sha256\"
    raise AssertionError(\"expected invalid base64 failure\")
    print(\"SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass\")
    print(f\"SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT={case_count}\")
"""

    check_workflow(good_workflow)
    check_helper(good_helper)
    case_count = 1

    for broken_text, expected in (
        (
            good_workflow.replace(
                "      - name: Self-test current split pinned Zig archive helper\n"
                "        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test\n",
                "",
                1,
            ),
            SPLIT_HELPER_SELF_TEST_STEP,
        ),
        (
            good_workflow.replace(
                "        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test\n",
                "",
                1,
            ),
            SPLIT_HELPER_SELF_TEST_CMD,
        ),
        (
            good_workflow.replace(
                "      - name: Self-test current staged pinned Zig archive helper\n"
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\n"
                "      - name: Self-test current split pinned Zig archive helper\n"
                "        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test\n",
                "      - name: Self-test current split pinned Zig archive helper\n"
                "        run: python3 scripts/zigux/split-pinned-zig-archive.py --self-test\n"
                "      - name: Self-test current staged pinned Zig archive helper\n"
                "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\n",
                1,
            ),
            "lane05 step order",
        ),
    ):
        try:
            check_workflow(broken_text)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected workflow failure for {expected}")

    for broken_text, expected in (
        (good_helper.replace("split_archive_invalid_b64_", "split_archive_corrupt_b64_", 1), "split_archive_invalid_b64_"),
        (good_helper.replace('"missing expected shard"', '"missing shard"', 1), '"missing expected shard"'),
        (good_helper.replace('print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")\n', "", 1), "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass"),
        (
            good_helper.replace(
                '    error_b = "chunk_bytes must be positive"\n    error_c = "missing expected shard"\n',
                '    error_c = "missing expected shard"\n    error_b = "chunk_bytes must be positive"\n',
                1,
            ),
            "helper self-test order",
        ),
    ):
        try:
            check_helper(broken_text)
        except SystemExit as exc:
            assert expected in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError(f"expected helper failure for {expected}")

    print("LANE05_SPLIT_HELPER_SELFTEST_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_SELF_TEST_CASE_COUNT={case_count}")
    return 0



def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 bootstrap keeps the split pinned Zig archive helper self-test packet intact."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap.yml",
    )
    parser.add_argument(
        "--helper",
        type=Path,
        default=HELPER_PATH,
        help="Path to scripts/zigux/split-pinned-zig-archive.py",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    workflow_text = read_text(args.workflow)
    helper_text = read_text(args.helper)
    check_workflow(workflow_text)
    check_helper(helper_text)
    print("LANE05_SPLIT_HELPER_SELFTEST=pass")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_WORKFLOW={args.workflow.resolve()}")
    print(f"LANE05_SPLIT_HELPER_SELFTEST_HELPER={args.helper.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

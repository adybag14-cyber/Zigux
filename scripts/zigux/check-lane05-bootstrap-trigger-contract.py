#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

WORKFLOW_NAME = "name: zigux-bootstrap"
PUSH_MARKER = "push:"
MASTER_BRANCHES_MARKER = "branches: [ master ]"
PULL_REQUEST_MARKER = "pull_request:"
WORKFLOW_DISPATCH_MARKER = "workflow_dispatch:"
SCRIPTS_PATH_MARKER = "- 'scripts/zigux/**'"
THIRD_PARTY_PATH_MARKER = "- 'third_party/**'"
WORKFLOW_PATH_FILTER_MARKER = "- '.github/workflows/zigux-bootstrap.yml'"
CONCURRENCY_MARKER = "concurrency:"
GROUP_MARKER = (
    "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, "
    "github.sha) || format('{0}-{1}', github.workflow, github.ref) }}"
)
CANCEL_MARKER = "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}"
SETUP_STEP = "- name: Setup pinned Zig toolchain"
WORKFLOW_CHECKER_STEP = "- name: Check current Lane 05 local-first archive packet"
README_CHECKER_STEP = "- name: Check current Lane 05 local archive README packet"


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"expected exactly {expected} occurrences of {label} {marker}, found {actual}"
        )


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line.strip() == marker)
    if actual != expected:
        raise ValueError(
            f"expected exactly {expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"expected {label} `{earlier}` before `{later}`")


def validate_workflow(root: Path) -> int:
    workflow_path = root / WORKFLOW_PATH
    try:
        text = workflow_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing bootstrap workflow: {workflow_path}") from exc

    for marker, label in (
        (WORKFLOW_NAME, "workflow name"),
        (PUSH_MARKER, "push trigger"),
        (MASTER_BRANCHES_MARKER, "master push branch gate"),
        (PULL_REQUEST_MARKER, "pull request trigger"),
        (WORKFLOW_DISPATCH_MARKER, "workflow dispatch trigger"),
        (SCRIPTS_PATH_MARKER, "scripts path filter"),
        (THIRD_PARTY_PATH_MARKER, "third-party path filter"),
        (WORKFLOW_PATH_FILTER_MARKER, "workflow self-trigger path filter"),
        (CONCURRENCY_MARKER, "concurrency block"),
        (GROUP_MARKER, "exact-head concurrency group"),
        (CANCEL_MARKER, "master-safe cancel contract"),
        (SETUP_STEP, "setup step"),
        (WORKFLOW_CHECKER_STEP, "lane05 workflow checker step"),
        (README_CHECKER_STEP, "lane05 readme checker step"),
    ):
        require_marker(text, marker, label)

    for marker, label in (
        (PUSH_MARKER, "push trigger"),
        (MASTER_BRANCHES_MARKER, "master push branch gate"),
        (PULL_REQUEST_MARKER, "pull request trigger"),
        (WORKFLOW_DISPATCH_MARKER, "workflow dispatch trigger"),
        (CONCURRENCY_MARKER, "concurrency block"),
        (GROUP_MARKER, "exact-head concurrency group"),
        (CANCEL_MARKER, "master-safe cancel contract"),
        (SETUP_STEP, "setup step"),
        (WORKFLOW_CHECKER_STEP, "lane05 workflow checker step"),
        (README_CHECKER_STEP, "lane05 readme checker step"),
    ):
        require_exact_count(text, marker, 1, label)

    for marker, label in (
        (SCRIPTS_PATH_MARKER, "scripts path filter"),
        (THIRD_PARTY_PATH_MARKER, "third-party path filter"),
        (WORKFLOW_PATH_FILTER_MARKER, "workflow self-trigger path filter"),
    ):
        require_exact_line_count(text, marker, 1, label)

    require_order(text, PUSH_MARKER, PULL_REQUEST_MARKER, "trigger order")
    require_order(text, PULL_REQUEST_MARKER, WORKFLOW_DISPATCH_MARKER, "trigger order")
    require_order(text, WORKFLOW_DISPATCH_MARKER, CONCURRENCY_MARKER, "dispatch before concurrency order")
    require_order(text, SCRIPTS_PATH_MARKER, THIRD_PARTY_PATH_MARKER, "path filter order")
    require_order(text, THIRD_PARTY_PATH_MARKER, WORKFLOW_PATH_FILTER_MARKER, "path filter order")
    require_order(text, CONCURRENCY_MARKER, GROUP_MARKER, "concurrency block order")
    require_order(text, GROUP_MARKER, CANCEL_MARKER, "concurrency block order")
    require_order(text, SETUP_STEP, WORKFLOW_CHECKER_STEP, "lane05 step order")
    require_order(text, WORKFLOW_CHECKER_STEP, README_CHECKER_STEP, "lane05 step order")

    return 14


def write_sample_root(root: Path) -> None:
    (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (root / WORKFLOW_PATH).write_text(
        """name: zigux-bootstrap
on:
  push:
    branches: [ master ]
  pull_request:
    paths:
      - 'scripts/zigux/**'
      - 'third_party/**'
      - '.github/workflows/zigux-bootstrap.yml'
  workflow_dispatch:

concurrency:
  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}

jobs:
  bootstrap:
    steps:
      - name: Setup pinned Zig toolchain
      - name: Check current Lane 05 local-first archive packet
      - name: Check current Lane 05 local archive README packet
""",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_trigger_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            assert validate_workflow(root) == 14
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_trigger_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                validate_workflow(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected validate_workflow to fail")

    expect_pass()
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace("  push:\n", "", 1),
            encoding="utf-8",
        ),
        "missing push trigger",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace("branches: [ master ]", "branches: [ main ]", 1),
            encoding="utf-8",
        ),
        "master push branch gate",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace("workflow_dispatch:\n", "", 1),
            encoding="utf-8",
        ),
        "workflow dispatch trigger",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(WORKFLOW_PATH_FILTER_MARKER + "\n", "", 1),
            encoding="utf-8",
        ),
        "workflow self-trigger path filter",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(THIRD_PARTY_PATH_MARKER + "\n", "", 1),
            encoding="utf-8",
        ),
        "third-party path filter",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(SCRIPTS_PATH_MARKER + "\n", "", 1),
            encoding="utf-8",
        ),
        "scripts path filter",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(GROUP_MARKER + "\n", "", 1),
            encoding="utf-8",
        ),
        "exact-head concurrency group",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(CANCEL_MARKER + "\n", "", 1),
            encoding="utf-8",
        ),
        "master-safe cancel contract",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(
                "      - 'scripts/zigux/**'\n      - 'third_party/**'\n      - '.github/workflows/zigux-bootstrap.yml'\n",
                "      - '.github/workflows/zigux-bootstrap.yml'\n      - 'scripts/zigux/**'\n      - 'third_party/**'\n",
                1,
            ),
            encoding="utf-8",
        ),
        "path filter order",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(
                "  workflow_dispatch:\n",
                "  workflow_dispatch:\n  workflow_dispatch:\n",
                1,
            ),
            encoding="utf-8",
        ),
        "workflow dispatch trigger",
    )

    print("LANE05_BOOTSTRAP_TRIGGER_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_BOOTSTRAP_TRIGGER_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Lane 05 bootstrap trigger and exact-head concurrency contract."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root for replay validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"LANE05_BOOTSTRAP_TRIGGER_CONTRACT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    try:
        marker_count = validate_workflow(args.root.resolve())
    except ValueError as exc:
        print("LANE05_BOOTSTRAP_TRIGGER_CONTRACT=fail")
        print(f"LANE05_BOOTSTRAP_TRIGGER_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_BOOTSTRAP_TRIGGER_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_BOOTSTRAP_TRIGGER_CONTRACT=pass")
    print(f"LANE05_BOOTSTRAP_TRIGGER_CONTRACT_ROOT={args.root.resolve()}")
    print(f"LANE05_BOOTSTRAP_TRIGGER_CONTRACT_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

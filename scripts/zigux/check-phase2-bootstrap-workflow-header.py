#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
STATUS_NAME = "PHASE2_BOOTSTRAP_WORKFLOW_HEADER"
SELF_TEST_NAME = f"{STATUS_NAME}_SELF_TEST"

REQUIRED_HEADER_MARKERS = [
    "name: zigux-bootstrap",
    "on:",
    "  push:",
    "    branches: [ master ]",
    "  pull_request:",
    "    paths:",
    "      - 'lib/**'",
    "      - 'zigux-alpha/**'",
    "      - 'Documentation/zigux/**'",
    "      - 'samples/zigux/**'",
    "      - 'kernel/**/*.zig'",
    "      - 'net/**/*.zig'",
    "      - 'drivers/**/*.zig'",
    "      - 'scripts/basic/fixdep.c'",
    "      - 'scripts/include/xalloc.h'",
    "      - 'scripts/kconfig/conf.c'",
    "      - 'scripts/kconfig/confdata.c'",
    "      - 'scripts/zigux/**'",
    "      - 'third_party/**'",
    "      - 'tools/lib/*.zig'",
    "      - 'tools/lib/**/*.zig'",
    "      - 'tools/lib/subcmd/exec-cmd.c'",
    "      - 'tools/lib/subcmd/help.c'",
    "      - 'tools/lib/symbol/kallsyms.c'",
    "      - 'zigux/**'",
    "      - 'include/linux/zigux.h'",
    "      - 'include/zigux/**'",
    "      - '.github/workflows/zigux-bootstrap.yml'",
    "  workflow_dispatch:",
    "env:",
    "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
    "concurrency:",
    "  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
    "  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
    "jobs:",
]


def build_sample_workflow() -> str:
    header = "\n".join(REQUIRED_HEADER_MARKERS)
    return (
        "# Keep this lane tied to files that the current checkout actually contains.\n"
        "# Run every master push so exact-head bootstrap status stays attached even when path filtering misses a live change.\n\n"
        f"{header}\n"
        "  bootstrap:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - name: Checkout\n"
        "        uses: actions/checkout@v6.0.2\n"
        "        with:\n"
        "          fetch-depth: 1\n"
    )


def collect_failures(workflow_text: str) -> list[str]:
    failures: list[str] = []
    workflow_lines = workflow_text.splitlines()
    cursor = -1
    for marker in REQUIRED_HEADER_MARKERS:
        count = workflow_lines.count(marker)
        if count == 0:
            failures.append(f"missing required workflow header marker: {marker}")
            continue
        if count > 1:
            failures.append(f"duplicate required workflow header marker: {marker}")
            continue
        index = workflow_text.find(f"\n{marker}\n")
        if index == -1:
            if workflow_text.startswith(f"{marker}\n"):
                index = 0
            elif workflow_text.endswith(f"\n{marker}"):
                index = workflow_text.rfind(f"\n{marker}") + 1
            else:
                index = workflow_text.find(marker)
        if index <= cursor:
            failures.append(f"workflow header marker out of order: {marker}")
            continue
        cursor = index
    return failures


def write_sample_root(root: Path) -> Path:
    workflow_path = root / WORKFLOW_PATH
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(build_sample_workflow(), encoding="utf-8")
    return workflow_path


def validate_root(root: Path) -> int:
    workflow_path = root / WORKFLOW_PATH
    if not workflow_path.exists():
        print(f"{STATUS_NAME}=missing")
        print(f"{STATUS_NAME}_WORKFLOW_PATH={workflow_path}")
        print(f"{STATUS_NAME}_NOTE=missing workflow file")
        return 1

    workflow_text = workflow_path.read_text(encoding="utf-8")
    failures = collect_failures(workflow_text)
    if failures:
        print(f"{STATUS_NAME}=invalid")
        print(f"{STATUS_NAME}_WORKFLOW_PATH={workflow_path}")
        print(f"{STATUS_NAME}_REQUIRED_MARKER_COUNT={len(REQUIRED_HEADER_MARKERS)}")
        print(f"{STATUS_NAME}_PATH_FILTER_COUNT=22")
        for failure in failures:
            print(f"{STATUS_NAME}_NOTE={failure}")
        return 1

    print(f"{STATUS_NAME}=pass")
    print(f"{STATUS_NAME}_WORKFLOW_PATH={workflow_path}")
    print(f"{STATUS_NAME}_REQUIRED_MARKER_COUNT={len(REQUIRED_HEADER_MARKERS)}")
    print(f"{STATUS_NAME}_PATH_FILTER_COUNT=22")
    return 0


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_lane03_header_") as tmp_dir:
        root = Path(tmp_dir)
        workflow_path = write_sample_root(root)
        case_count += 1 if validate_root(root) == 0 else 0

        missing_text = workflow_path.read_text(encoding="utf-8").replace(
            "  workflow_dispatch:\n",
            "",
            1,
        )
        workflow_path.write_text(missing_text, encoding="utf-8")
        case_count += 1 if validate_root(root) != 0 else 0

        write_sample_root(root)
        duplicate_text = workflow_path.read_text(encoding="utf-8").replace(
            "  workflow_dispatch:\n",
            "  workflow_dispatch:\n  workflow_dispatch:\n",
            1,
        )
        workflow_path.write_text(duplicate_text, encoding="utf-8")
        case_count += 1 if validate_root(root) != 0 else 0

        write_sample_root(root)
        reordered_text = workflow_path.read_text(encoding="utf-8").replace(
            "concurrency:\n  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}\n  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}\n",
            "concurrency:\n  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}\n  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}\n",
            1,
        )
        workflow_path.write_text(reordered_text, encoding="utf-8")
        case_count += 1 if validate_root(root) != 0 else 0

        write_sample_root(root)
        drifted_env_text = workflow_path.read_text(encoding="utf-8").replace(
            "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true",
            "  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: false",
            1,
        )
        workflow_path.write_text(drifted_env_text, encoding="utf-8")
        case_count += 1 if validate_root(root) != 0 else 0

        write_sample_root(root)
        removed_path_text = workflow_path.read_text(encoding="utf-8").replace(
            "      - 'scripts/zigux/**'\n",
            "",
            1,
        )
        workflow_path.write_text(removed_path_text, encoding="utf-8")
        case_count += 1 if validate_root(root) != 0 else 0

    print(f"{SELF_TEST_NAME}=pass")
    print(f"{SELF_TEST_NAME}_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed when the current zigux-bootstrap workflow header packet drifts."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo root to validate.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for replay.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"{STATUS_NAME}_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    return validate_root(args.root)


if __name__ == "__main__":
    raise SystemExit(main())

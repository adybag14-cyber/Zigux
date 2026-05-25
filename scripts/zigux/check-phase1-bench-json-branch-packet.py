#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

SELF_REL = "scripts/zigux/check-phase1-bench-json-branch-packet.py"
BENCH_REL = "scripts/zigux/check-phase1-bench.py"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [SELF_REL, BENCH_REL, WORKFLOW_REL]

REQUIRED_BENCH_MARKERS = [
    'if kind == "expectations_json_error":',
    'print("PHASE1_BENCH_CHECK=fail")',
    'print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")',
    'print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")',
    'print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")',
]

REQUIRED_WORKFLOW_MARKERS = [
    "- name: Self-test current Phase 1 bench checker",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
]


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).is_file()]


def collect_missing_bench_markers(root: Path) -> list[str]:
    text = read_text(root, BENCH_REL)
    return [marker for marker in REQUIRED_BENCH_MARKERS if marker not in text]


def collect_missing_workflow_markers(root: Path) -> list[str]:
    text = read_text(root, WORKFLOW_REL)
    return [marker for marker in REQUIRED_WORKFLOW_MARKERS if marker not in text]


def make_sample_root(root: Path) -> None:
    write_text(root / SELF_REL, "# sample checker placeholder\n")
    write_text(root / BENCH_REL, "\n".join(REQUIRED_BENCH_MARKERS) + "\n")
    write_text(root / WORKFLOW_REL, "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n")


def run_self_test() -> None:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bench_json_branch_packet_") as tmp_dir:
        root = Path(tmp_dir)
        make_sample_root(root)

        assert collect_missing_files(root) == []
        assert collect_missing_bench_markers(root) == []
        assert collect_missing_workflow_markers(root) == []
        case_count += 1

        bench_path = root / BENCH_REL
        bench_path.write_text(
            bench_path.read_text(encoding="utf-8").replace(
                'print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_bench_markers(root) == ['print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")']
        case_count += 1

        make_sample_root(root)
        workflow_path = root / WORKFLOW_REL
        workflow_path.write_text(
            workflow_path.read_text(encoding="utf-8").replace(
                "run: python3 scripts/zigux/check-phase1-bench.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_workflow_markers(root) == [
            "run: python3 scripts/zigux/check-phase1-bench.py --self-test"
        ]
        case_count += 1

        make_sample_root(root)
        (root / BENCH_REL).unlink()
        assert collect_missing_files(root) == [BENCH_REL]
        case_count += 1

    print("PHASE1_BENCH_JSON_BRANCH_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_JSON_BRANCH_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 16 malformed-JSON bench branch packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    parser.add_argument(
        "--write-sample-root",
        help="Write a sample current-like root that satisfies this checker.",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        make_sample_root(root)
        print(f"PHASE1_BENCH_JSON_BRANCH_PACKET_SAMPLE_ROOT={root}")
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BENCH_JSON_BRANCH_PACKET=fail")
        print("MISSING_PHASE1_BENCH_JSON_BRANCH_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_BENCH_JSON_BRANCH_PACKET_FILES_END")
        return 1

    missing_bench_markers = collect_missing_bench_markers(root)
    if missing_bench_markers:
        print("PHASE1_BENCH_JSON_BRANCH_PACKET=fail")
        print("MISSING_PHASE1_BENCH_JSON_BRANCH_PACKET_BENCH_MARKERS_START")
        for item in missing_bench_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_JSON_BRANCH_PACKET_BENCH_MARKERS_END")
        return 1

    missing_workflow_markers = collect_missing_workflow_markers(root)
    if missing_workflow_markers:
        print("PHASE1_BENCH_JSON_BRANCH_PACKET=fail")
        print("MISSING_PHASE1_BENCH_JSON_BRANCH_PACKET_WORKFLOW_MARKERS_START")
        for item in missing_workflow_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_JSON_BRANCH_PACKET_WORKFLOW_MARKERS_END")
        return 1

    print("PHASE1_BENCH_JSON_BRANCH_PACKET=pass")
    print(f"PHASE1_BENCH_JSON_BRANCH_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_JSON_BRANCH_PACKET_BENCH_MARKER_COUNT="
        f"{len(REQUIRED_BENCH_MARKERS)}"
    )
    print(
        "PHASE1_BENCH_JSON_BRANCH_PACKET_WORKFLOW_MARKER_COUNT="
        f"{len(REQUIRED_WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

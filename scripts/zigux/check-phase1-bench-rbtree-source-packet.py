#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

SELF_REL = "scripts/zigux/check-phase1-bench-rbtree-source-packet.py"
BENCH_REL = "scripts/zigux/check-phase1-bench.py"
CLOSURE_REL = "Documentation/zigux/phase1-closure.md"
WORKFLOW_REL = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_FILES = [SELF_REL, BENCH_REL, CLOSURE_REL, WORKFLOW_REL]

REQUIRED_BENCH_MARKERS = [
    'RBTREE_REQUIRED_ITERATIONS = {"PHASE1_BENCH_RBTREE_ITERATIONS"}',
    'RBTREE_REQUIRED_EXACT_CHECKSUMS = {',
    '"PHASE1_BENCH_RBTREE_CHECKSUM"',
    '"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM"',
    '"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM"',
    '"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM"',
    '"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"',
    'RBTREE_REQUIRED_SOURCE_MARKERS = {',
    '"rbtree_bench_fn": "fn rbtreeBench() struct { checksum: u64 } {",',
    '"rbtree_cached_fn": "fn rbtreeCachedBench() struct { checksum: u64 } {",',
    '"rbtree_iterations_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\\\\n", .{iterations_rbtree});\',',
    '"rbtree_cached_print": \'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\\\n", .{rbtree_cached_result.checksum});\',',
    '"rbtree_cached_leftmost": "const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);",',
    'duplicate_rbtree_markers = duplicate_marker_labels(text, RBTREE_REQUIRED_SOURCE_MARKERS)',
    'return ("bench_source_duplicate_rbtree_markers", duplicate_rbtree_markers)',
    'return ("expectations_checksums_rbtree_exact_required", key)',
    'return ("missing_rbtree_iterations", [key])',
    'return ("rbtree_iteration_mismatch", (key, expected, actual))',
    'return ("missing_rbtree_exact_checksums", missing_exact)',
]

REQUIRED_CLOSURE_MARKERS = [
    "Current `master` also keeps the stricter rbtree bench-exactness packet explicit in that same checker: `scripts/zigux/check-phase1-bench.py` now hard-codes `PHASE1_BENCH_RBTREE_ITERATIONS=4000` and exact-checks `PHASE1_BENCH_RBTREE_CHECKSUM`, `PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM`, `PHASE1_BENCH_FIND_ADD_CHECKSUM`, `PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM`, and `PHASE1_BENCH_RBTREE_CACHED_CHECKSUM` whenever the broader expectations packet returns.",
    "- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`",
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


def collect_missing_markers(root: Path, relative_path: str, markers: list[str]) -> list[str]:
    text = read_text(root, relative_path)
    return [marker for marker in markers if marker not in text]


def make_sample_root(root: Path) -> None:
    write_text(root / SELF_REL, "# sample checker placeholder\n")
    write_text(root / BENCH_REL, "\n".join(REQUIRED_BENCH_MARKERS) + "\n")
    write_text(root / CLOSURE_REL, "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(root / WORKFLOW_REL, "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n")


def run_self_test() -> None:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_bench_rbtree_source_packet_") as tmp_dir:
        root = Path(tmp_dir)
        make_sample_root(root)

        assert collect_missing_files(root) == []
        assert collect_missing_markers(root, BENCH_REL, REQUIRED_BENCH_MARKERS) == []
        assert collect_missing_markers(root, CLOSURE_REL, REQUIRED_CLOSURE_MARKERS) == []
        assert collect_missing_markers(root, WORKFLOW_REL, REQUIRED_WORKFLOW_MARKERS) == []
        case_count += 1

        bench_path = root / BENCH_REL
        bench_path.write_text(
            bench_path.read_text(encoding="utf-8").replace(
                'return ("missing_rbtree_exact_checksums", missing_exact)\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_markers(root, BENCH_REL, REQUIRED_BENCH_MARKERS) == [
            'return ("missing_rbtree_exact_checksums", missing_exact)'
        ]
        case_count += 1

        make_sample_root(root)
        closure_path = root / CLOSURE_REL
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                REQUIRED_CLOSURE_MARKERS[1] + "\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert collect_missing_markers(root, CLOSURE_REL, REQUIRED_CLOSURE_MARKERS) == [
            REQUIRED_CLOSURE_MARKERS[1]
        ]
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
        assert collect_missing_markers(root, WORKFLOW_REL, REQUIRED_WORKFLOW_MARKERS) == [
            "run: python3 scripts/zigux/check-phase1-bench.py --self-test"
        ]
        case_count += 1

        make_sample_root(root)
        (root / BENCH_REL).unlink()
        assert collect_missing_files(root) == [BENCH_REL]
        case_count += 1

    print("PHASE1_BENCH_RBTREE_SOURCE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_RBTREE_SOURCE_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Lane 16 rbtree bench source packet."
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
        print(f"PHASE1_BENCH_RBTREE_SOURCE_PACKET_SAMPLE_ROOT={root}")
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_BENCH_RBTREE_SOURCE_PACKET=fail")
        print("MISSING_PHASE1_BENCH_RBTREE_SOURCE_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_BENCH_RBTREE_SOURCE_PACKET_FILES_END")
        return 1

    missing_bench_markers = collect_missing_markers(root, BENCH_REL, REQUIRED_BENCH_MARKERS)
    if missing_bench_markers:
        print("PHASE1_BENCH_RBTREE_SOURCE_PACKET=fail")
        print("MISSING_PHASE1_BENCH_RBTREE_SOURCE_PACKET_BENCH_MARKERS_START")
        for item in missing_bench_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_RBTREE_SOURCE_PACKET_BENCH_MARKERS_END")
        return 1

    missing_closure_markers = collect_missing_markers(root, CLOSURE_REL, REQUIRED_CLOSURE_MARKERS)
    if missing_closure_markers:
        print("PHASE1_BENCH_RBTREE_SOURCE_PACKET=fail")
        print("MISSING_PHASE1_BENCH_RBTREE_SOURCE_PACKET_CLOSURE_MARKERS_START")
        for item in missing_closure_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_RBTREE_SOURCE_PACKET_CLOSURE_MARKERS_END")
        return 1

    missing_workflow_markers = collect_missing_markers(root, WORKFLOW_REL, REQUIRED_WORKFLOW_MARKERS)
    if missing_workflow_markers:
        print("PHASE1_BENCH_RBTREE_SOURCE_PACKET=fail")
        print("MISSING_PHASE1_BENCH_RBTREE_SOURCE_PACKET_WORKFLOW_MARKERS_START")
        for item in missing_workflow_markers:
            print(item)
        print("MISSING_PHASE1_BENCH_RBTREE_SOURCE_PACKET_WORKFLOW_MARKERS_END")
        return 1

    print("PHASE1_BENCH_RBTREE_SOURCE_PACKET=pass")
    print(f"PHASE1_BENCH_RBTREE_SOURCE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_RBTREE_SOURCE_PACKET_BENCH_MARKER_COUNT="
        f"{len(REQUIRED_BENCH_MARKERS)}"
    )
    print(
        "PHASE1_BENCH_RBTREE_SOURCE_PACKET_CLOSURE_MARKER_COUNT="
        f"{len(REQUIRED_CLOSURE_MARKERS)}"
    )
    print(
        "PHASE1_BENCH_RBTREE_SOURCE_PACKET_WORKFLOW_MARKER_COUNT="
        f"{len(REQUIRED_WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

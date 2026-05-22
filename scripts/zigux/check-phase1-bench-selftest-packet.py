#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BENCH_PATH = Path("scripts/zigux/check-phase1-bench.py")
MIN_CASE_COUNT = 35

REQUIRED_WORKFLOW_MARKERS = (
    "- name: Self-test current Phase 1 bench checker",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
)

REQUIRED_BENCH_MARKERS = (
    "def run_self_test() -> None:",
    'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
    'print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
    'kind, payload = load_runtime_bench_source(missing_path)',
    'assert kind == "missing_bench_source_file"',
    'assert kind == "bench_source_missing_markers"',
    'assert kind == "expectations_duplicate_keys"',
    'assert kind == "expectations_duplicate_iteration_keys"',
    'assert kind == "expectations_duplicate_exact_checksum_keys"',
    'assert kind == "expectations_duplicate_checksums"',
    'assert kind == "missing_rbtree_iterations"',
    'assert kind == "rbtree_iteration_mismatch"',
    'assert kind == "missing_rbtree_exact_checksums"',
    'assert kind == "missing_bitmap_exact_checksums"',
    'assert kind == "missing_find_bit_exact_checksums"',
    'assert kind == "missing_string_exact_checksums"',
    'assert kind == "missing_hweight_exact_checksums"',
    'assert kind == "missing_list_sort_exact_checksums"',
    'assert kind == "exact_checksum_mismatch"',
    'assert kind == "expectations_checksums_bitmap_exact_required"',
    'assert kind == "expectations_checksums_find_bit_exact_required"',
    'assert kind == "expectations_checksums_string_exact_required"',
    'assert kind == "expectations_checksums_hweight_exact_required"',
    'assert kind == "expectations_checksums_list_sort_exact_required"',
    'assert kind == "expectations_checksums_rbtree_exact_required"',
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_root(root: Path) -> tuple[str, object]:
    workflow_file = root / WORKFLOW_PATH
    bench_file = root / BENCH_PATH

    missing_files = [str(path) for path in (workflow_file, bench_file) if not path.is_file()]
    if missing_files:
        return ("missing_files", missing_files)

    workflow_text = read_text(workflow_file)
    bench_text = read_text(bench_file)

    missing_workflow = [marker for marker in REQUIRED_WORKFLOW_MARKERS if marker not in workflow_text]
    if missing_workflow:
        return ("missing_workflow_markers", missing_workflow)

    missing_bench = [marker for marker in REQUIRED_BENCH_MARKERS if marker not in bench_text]
    if missing_bench:
        return ("missing_bench_markers", missing_bench)

    case_count = bench_text.count("case_count += 1")
    if case_count < MIN_CASE_COUNT:
        return ("case_count_too_small", {"expected_min": MIN_CASE_COUNT, "actual": case_count})

    return ("pass", {"case_count": case_count})


def write_sample_root(root: Path) -> None:
    (root / WORKFLOW_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / BENCH_PATH.parent).mkdir(parents=True, exist_ok=True)

    workflow_text = """name: zigux-bootstrap
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 1 bench checker
        run: python3 scripts/zigux/check-phase1-bench.py --self-test
"""

    bench_lines = [
        "#!/usr/bin/env python3",
        "def run_self_test() -> None:",
        "    kind, payload = load_runtime_bench_source(missing_path)",
        '    assert kind == "missing_bench_source_file"',
        '    assert kind == "bench_source_missing_markers"',
        '    assert kind == "expectations_duplicate_keys"',
        '    assert kind == "expectations_duplicate_iteration_keys"',
        '    assert kind == "expectations_duplicate_exact_checksum_keys"',
        '    assert kind == "expectations_duplicate_checksums"',
        '    assert kind == "missing_rbtree_iterations"',
        '    assert kind == "rbtree_iteration_mismatch"',
        '    assert kind == "missing_rbtree_exact_checksums"',
        '    assert kind == "missing_bitmap_exact_checksums"',
        '    assert kind == "missing_find_bit_exact_checksums"',
        '    assert kind == "missing_string_exact_checksums"',
        '    assert kind == "missing_hweight_exact_checksums"',
        '    assert kind == "missing_list_sort_exact_checksums"',
        '    assert kind == "exact_checksum_mismatch"',
        '    assert kind == "expectations_checksums_bitmap_exact_required"',
        '    assert kind == "expectations_checksums_find_bit_exact_required"',
        '    assert kind == "expectations_checksums_string_exact_required"',
        '    assert kind == "expectations_checksums_hweight_exact_required"',
        '    assert kind == "expectations_checksums_list_sort_exact_required"',
        '    assert kind == "expectations_checksums_rbtree_exact_required"',
    ]
    bench_lines.extend(["    case_count += 1"] * MIN_CASE_COUNT)
    bench_lines.extend(
        [
            '    print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
            '    print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
        ]
    )

    (root / WORKFLOW_PATH).write_text(workflow_text, encoding="utf-8")
    (root / BENCH_PATH).write_text("\n".join(bench_lines) + "\n", encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane16-bench-selftest-") as tmp:
        root = Path(tmp)
        write_sample_root(root)

        kind, payload = validate_root(root)
        assert kind == "pass", (kind, payload)
        assert payload == {"case_count": MIN_CASE_COUNT}
        case_count += 1

        workflow_text = read_text(root / WORKFLOW_PATH).replace(
            "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
            "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
            1,
        )
        (root / WORKFLOW_PATH).write_text(workflow_text, encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "missing_workflow_markers", (kind, payload)
        assert payload == ["run: python3 scripts/zigux/check-phase1-bench.py --self-test"]
        case_count += 1

        write_sample_root(root)
        bench_text = read_text(root / BENCH_PATH).replace(
            'assert kind == "missing_rbtree_exact_checksums"\n',
            "",
            1,
        )
        (root / BENCH_PATH).write_text(bench_text, encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "missing_bench_markers", (kind, payload)
        assert payload == ['assert kind == "missing_rbtree_exact_checksums"']
        case_count += 1

        write_sample_root(root)
        bench_lines = read_text(root / BENCH_PATH).splitlines()
        filtered_lines = [line for line in bench_lines if line != "    case_count += 1"]
        filtered_lines.extend(["    case_count += 1"] * (MIN_CASE_COUNT - 1))
        (root / BENCH_PATH).write_text("\n".join(filtered_lines) + "\n", encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "case_count_too_small", (kind, payload)
        assert payload == {"expected_min": MIN_CASE_COUNT, "actual": MIN_CASE_COUNT - 1}
        case_count += 1

        write_sample_root(root)
        (root / BENCH_PATH).unlink()
        kind, payload = validate_root(root)
        assert kind == "missing_files", (kind, payload)
        assert payload == [str(root / BENCH_PATH)]
        case_count += 1

    print("PHASE1_BENCH_SELFTEST_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_SELFTEST_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the shipped Phase 1 bench checker keeps its self-test contract explicit."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run checker self-tests",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root",
    )
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    kind, payload = validate_root(args.root)
    if kind != "pass":
        print("PHASE1_BENCH_SELFTEST_PACKET=fail")
        print(f"PHASE1_BENCH_SELFTEST_PACKET_REASON={kind}")
        print(payload)
        return 1

    case_count = payload["case_count"]
    print("PHASE1_BENCH_SELFTEST_PACKET=pass")
    print("PHASE1_BENCH_SELFTEST_PACKET_REQUIRED_FILE_COUNT=2")
    print(
        f"PHASE1_BENCH_SELFTEST_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_BENCH_MARKERS)}"
    )
    print(f"PHASE1_BENCH_SELFTEST_PACKET_CASE_COUNT_MIN={MIN_CASE_COUNT}")
    print(f"PHASE1_BENCH_SELFTEST_PACKET_CASE_COUNT={case_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

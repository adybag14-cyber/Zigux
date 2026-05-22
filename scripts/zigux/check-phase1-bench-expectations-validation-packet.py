#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

BENCH_MARKERS = {
    "validate_expectations_fn": "def validate_expectations(expectations: object) -> tuple[str, object]:",
    "expectations_type": 'return ("expectations_type", type(expectations).__name__)',
    "duplicate_top_level_keys": 'return ("expectations_duplicate_keys", expectations.duplicate_keys)',
    "expectations_status": 'return ("expectations_status", expectations.get("status"))',
    "iterations_type": 'return ("expectations_iterations_type", type(iterations).__name__)',
    "duplicate_iteration_keys": 'return ("expectations_duplicate_iteration_keys", iterations.duplicate_keys)',
    "checksums_type": 'return ("expectations_checksums_type", type(checksums).__name__)',
    "exact_checksums_type": 'return ("expectations_exact_checksums_type", type(exact_checksums).__name__)',
    "duplicate_exact_checksum_keys": 'return ("expectations_duplicate_exact_checksum_keys", exact_checksums.duplicate_keys)',
    "missing_rbtree_iterations": 'return ("expectations_missing_rbtree_iterations", missing_rbtree_iterations)',
    "missing_iterations": 'return ("expectations_missing_iterations", missing)',
    "unexpected_iteration": 'return ("expectations_unexpected_iteration", unexpected[0])',
    "iteration_value_type": 'return ("expectations_iteration_value_type", (key, type(value).__name__))',
    "rbtree_iteration_value": 'return ("expectations_rbtree_iteration_value", (key, expected, value))',
    "iteration_value": 'return ("expectations_iteration_value", (key, expected, value))',
    "duplicate_checksums": 'return ("expectations_duplicate_checksums", duplicates)',
    "checksum_order": 'return ("expectations_checksum_order", checksums)',
    "missing_checksums": 'return ("expectations_missing_checksums", missing)',
    "unexpected_checksums": 'return ("expectations_unexpected_checksums", unexpected)',
    "missing_exact_checksums": 'return ("expectations_missing_exact_checksums", missing)',
    "unexpected_exact_checksums": 'return ("expectations_unexpected_exact_checksums", unexpected)',
    "exact_checksum_value_type": 'return ("expectations_exact_checksum_value_type", (key, type(value).__name__))',
    "exact_checksum_nonpositive": 'return ("expectations_exact_checksum_nonpositive", (key, value))',
    "failure_reason_line": 'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
}

SELF_TEST_MARKERS = {
    "duplicate_top_level_text": 'kind, payload = validate_expectations(load_expectations_text(duplicate_top_level_text))',
    "duplicate_iteration_text": 'kind, payload = validate_expectations(load_expectations_text(duplicate_iteration_text))',
    "duplicate_exact_checksum_text": 'kind, payload = validate_expectations(load_expectations_text(duplicate_exact_checksum_text))',
    "duplicate_checksum_list": 'kind, payload = validate_expectations(duplicate_checksum_list)',
    "missing_rbtree_iterations_case": 'kind, payload = validate_expectations(missing_rbtree_iterations)',
    "reordered_checksums_case": 'kind, payload = validate_expectations(reordered_checksums)',
}

WORKFLOW_MARKERS = {
    "bench_self_test_command": "python3 scripts/zigux/check-phase1-bench.py --self-test",
}


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def validate_text(text: str, markers: dict[str, str]) -> tuple[str, object]:
    missing = [label for label, marker in markers.items() if marker not in text]
    if missing:
        return ("missing_markers", missing)
    return ("pass", len(markers))


def validate_root(root: Path) -> tuple[str, object]:
    try:
        bench_text = read_text(root, BENCH_REL)
    except FileNotFoundError:
        return ("missing_file", str(BENCH_REL))
    try:
        workflow_text = read_text(root, WORKFLOW_REL)
    except FileNotFoundError:
        return ("missing_file", str(WORKFLOW_REL))

    kind, payload = validate_text(bench_text, BENCH_MARKERS)
    if kind != "pass":
        return (f"bench_{kind}", payload)

    kind, payload = validate_text(bench_text, SELF_TEST_MARKERS)
    if kind != "pass":
        return (f"bench_self_test_{kind}", payload)

    kind, payload = validate_text(workflow_text, WORKFLOW_MARKERS)
    if kind != "pass":
        return (f"workflow_{kind}", payload)

    return ("pass", None)


def write_sample_root(root: Path) -> None:
    bench_path = root / BENCH_REL
    workflow_path = root / WORKFLOW_REL
    bench_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.parent.mkdir(parents=True, exist_ok=True)

    bench_lines = ["# synthetic sample root for Lane 16 expectations-validation checker", ""]
    bench_lines.extend(BENCH_MARKERS.values())
    bench_lines.append("")
    bench_lines.extend(SELF_TEST_MARKERS.values())
    bench_lines.append("")
    bench_path.write_text("\n".join(bench_lines) + "\n", encoding="utf-8")

    workflow_lines = ["jobs:", "  bootstrap:", "    steps:"]
    workflow_lines.extend([f"      - run: {marker}" for marker in WORKFLOW_MARKERS.values()])
    workflow_path.write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane16-bench-expectations-validation-") as tmp:
        root = Path(tmp)
        write_sample_root(root)

        kind, payload = validate_root(root)
        assert kind == "pass", (kind, payload)
        case_count += 1

        bench_path = root / BENCH_REL
        original_bench = bench_path.read_text(encoding="utf-8")
        bench_path.write_text(
            original_bench.replace(BENCH_MARKERS["duplicate_checksums"], "", 1),
            encoding="utf-8",
        )
        kind, payload = validate_root(root)
        assert kind == "bench_missing_markers", (kind, payload)
        assert payload == ["duplicate_checksums"], payload
        case_count += 1
        bench_path.write_text(original_bench, encoding="utf-8")

        bench_path.write_text(
            original_bench.replace(SELF_TEST_MARKERS["reordered_checksums_case"], "", 1),
            encoding="utf-8",
        )
        kind, payload = validate_root(root)
        assert kind == "bench_self_test_missing_markers", (kind, payload)
        assert payload == ["reordered_checksums_case"], payload
        case_count += 1
        bench_path.write_text(original_bench, encoding="utf-8")

        workflow_path = root / WORKFLOW_REL
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(original_workflow.replace(WORKFLOW_MARKERS["bench_self_test_command"], "", 1), encoding="utf-8")
        kind, payload = validate_root(root)
        assert kind == "workflow_missing_markers", (kind, payload)
        assert payload == ["bench_self_test_command"], payload
        case_count += 1
        workflow_path.write_text(original_workflow, encoding="utf-8")

        (root / BENCH_REL).unlink()
        kind, payload = validate_root(root)
        assert kind == "missing_file", (kind, payload)
        assert payload == str(BENCH_REL), payload
        case_count += 1
        write_sample_root(root)

        (root / WORKFLOW_REL).unlink()
        kind, payload = validate_root(root)
        assert kind == "missing_file", (kind, payload)
        assert payload == str(WORKFLOW_REL), payload
        case_count += 1

    print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_EXPECTATIONS_VALIDATION_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Lane 16 expectations-validation failure packet for the Phase 1 bench checker."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample tree to the given directory",
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
        print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_PACKET=fail")
        print(f"PHASE1_BENCH_EXPECTATIONS_VALIDATION_PACKET_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_PACKET=pass")
    print("PHASE1_BENCH_EXPECTATIONS_VALIDATION_PACKET_REQUIRED_FILE_COUNT=2")
    print(f"PHASE1_BENCH_EXPECTATIONS_VALIDATION_PACKET_MARKER_COUNT={len(BENCH_MARKERS) + len(SELF_TEST_MARKERS) + len(WORKFLOW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

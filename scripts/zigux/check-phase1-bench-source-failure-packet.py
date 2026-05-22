#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BENCH_CHECKER = ROOT / "scripts" / "zigux" / "check-phase1-bench.py"
BOOTSTRAP_WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"

REQUIRED_FILES = {
    "bench_checker": BENCH_CHECKER,
    "bootstrap_workflow": BOOTSTRAP_WORKFLOW,
}

BENCH_REQUIRED_MARKERS = {
    "phase1_bench_path": 'PHASE1_BENCH = ROOT / "zigux" / "tests" / "phase1_bench.zig"',
    "source_markers_map": "FIND_BIT_REQUIRED_SOURCE_MARKERS = {",
    "runtime_source_loader": "kind, payload = load_runtime_bench_source(PHASE1_BENCH)",
    "missing_bench_source_file": 'return ("missing_bench_source_file", path)',
    "missing_bench_source_reason": 'return ("bench_source_missing_markers", missing)',
    "source_reason_print": 'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
    "source_path_print": 'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")',
}

WORKFLOW_REQUIRED_MARKERS = {
    "selftest_step": "- name: Self-test current Phase 1 bench checker",
    "selftest_run": "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_text(text: str, markers: dict[str, str], missing_kind: str) -> tuple[str, object]:
    missing = [label for label, marker in markers.items() if marker not in text]
    if missing:
        return (missing_kind, missing)
    return ("pass", None)


def validate_root(root: Path) -> tuple[str, object]:
    for required in REQUIRED_FILES.values():
        path = root / required.relative_to(ROOT)
        if not path.is_file():
            return ("missing_required_file", str(path.relative_to(root)))

    bench_text = read_text(root / BENCH_CHECKER.relative_to(ROOT))
    kind, payload = validate_text(
        bench_text,
        BENCH_REQUIRED_MARKERS,
        "missing_bench_source_markers",
    )
    if kind != "pass":
        return (kind, payload)

    workflow_text = read_text(root / BOOTSTRAP_WORKFLOW.relative_to(ROOT))
    kind, payload = validate_text(
        workflow_text,
        WORKFLOW_REQUIRED_MARKERS,
        "missing_workflow_markers",
    )
    if kind != "pass":
        return (kind, payload)

    return ("pass", None)


def write_sample_root(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)

    bench_path = dest / BENCH_CHECKER.relative_to(ROOT)
    bench_path.parent.mkdir(parents=True, exist_ok=True)
    bench_path.write_text(
        "\n".join(
            [
                '#!/usr/bin/env python3',
                'PHASE1_BENCH = ROOT / "zigux" / "tests" / "phase1_bench.zig"',
                "FIND_BIT_REQUIRED_SOURCE_MARKERS = {",
                '    "find_bit_bench_fn": "fn findBitBench() struct { checksum: u64 } {",',
                "}",
                'return ("missing_bench_source_file", path)',
                'return ("bench_source_missing_markers", missing)',
                "kind, payload = load_runtime_bench_source(PHASE1_BENCH)",
                'print(f"PHASE1_BENCH_CHECK_REASON={kind}")',
                'print(f"PHASE1_BENCH_SOURCE={PHASE1_BENCH}")',
                "",
            ]
        ),
        encoding="utf-8",
    )

    workflow_path = dest / BOOTSTRAP_WORKFLOW.relative_to(ROOT)
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(
        "\n".join(
            [
                "name: zigux-bootstrap",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test current Phase 1 bench checker",
                "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
                "",
            ]
        ),
        encoding="utf-8",
    )


def run_self_test() -> None:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-bench-source-failure-") as tmp:
        root = Path(tmp) / "sample"
        write_sample_root(root)
        kind, payload = validate_root(root)
        assert kind == "pass", (kind, payload)
        case_count += 1

        bench_path = root / BENCH_CHECKER.relative_to(ROOT)
        bench_path.write_text(
            read_text(bench_path).replace(
                'return ("bench_source_missing_markers", missing)\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        kind, payload = validate_root(root)
        assert kind == "missing_bench_source_markers"
        assert payload == ["missing_bench_source_reason"]
        case_count += 1

        write_sample_root(root)
        workflow_path = root / BOOTSTRAP_WORKFLOW.relative_to(ROOT)
        workflow_path.write_text(
            read_text(workflow_path).replace(
                "run: python3 scripts/zigux/check-phase1-bench.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        kind, payload = validate_root(root)
        assert kind == "missing_workflow_markers"
        assert payload == ["selftest_run"]
        case_count += 1

        write_sample_root(root)
        missing_path = root / BENCH_CHECKER.relative_to(ROOT)
        missing_path.unlink()
        kind, payload = validate_root(root)
        assert kind == "missing_required_file"
        assert payload == "scripts/zigux/check-phase1-bench.py"
        case_count += 1

    print("PHASE1_BENCH_SOURCE_FAILURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BENCH_SOURCE_FAILURE_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the current Phase 1 bench source-failure packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to inspect.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like root for replay.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker self-tests.",
    )
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        run_self_test()
        return 0

    kind, payload = validate_root(args.root)
    if kind != "pass":
        print("PHASE1_BENCH_SOURCE_FAILURE_PACKET=fail")
        print(f"PHASE1_BENCH_SOURCE_FAILURE_PACKET_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_BENCH_SOURCE_FAILURE_PACKET=pass")
    print(f"PHASE1_BENCH_SOURCE_FAILURE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_BENCH_SOURCE_FAILURE_PACKET_MARKER_COUNT={}".format(
            len(BENCH_REQUIRED_MARKERS) + len(WORKFLOW_REQUIRED_MARKERS)
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

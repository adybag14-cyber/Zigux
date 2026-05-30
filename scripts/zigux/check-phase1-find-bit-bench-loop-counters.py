#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
BENCH_REL = Path("zigux/tests/phase1_bench.zig")

REQUIRED_MARKERS = {
    "find_next_counter_const": "const iterations_find_bit: u64 = 20000;",
    "find_edge_counter_const": "const iterations_find_bit_edge: u64 = 20000;",
    "find_next_bench_fn": "fn findBitBench() struct { checksum: u64 } {",
    "find_edge_bench_fn": "fn findBitEdgeBench() struct { checksum: u64 } {",
    "find_next_counter_loop": "while (idx < iterations_find_bit) : (idx += 1) {",
    "find_edge_counter_loop": "while (idx < iterations_find_bit_edge) : (idx += 1) {",
    "find_next_iterations_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\\n", .{iterations_find_bit});',
    "find_edge_iterations_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\\n", .{iterations_find_bit_edge});',
    "find_next_checksum_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n", .{find_bit_result.checksum});',
    "find_edge_checksum_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n", .{find_bit_edge_result.checksum});',
}

UNIQUE_MARKERS = {
    "find_next_counter_const",
    "find_edge_counter_const",
    "find_next_bench_fn",
    "find_edge_bench_fn",
    "find_next_counter_loop",
    "find_edge_counter_loop",
    "find_next_iterations_print",
    "find_edge_iterations_print",
    "find_next_checksum_print",
    "find_edge_checksum_print",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else ROOT.resolve()


def bench_path(root: Path) -> Path:
    return root / BENCH_REL


def validate_text(text: str) -> tuple[str, object]:
    missing = [label for label, marker in REQUIRED_MARKERS.items() if marker not in text]
    if missing:
        return ("missing_markers", missing)

    duplicates = [
        label
        for label in sorted(UNIQUE_MARKERS)
        if text.count(REQUIRED_MARKERS[label]) != 1
    ]
    if duplicates:
        return ("duplicate_or_ambiguous_markers", duplicates)

    next_const = text.index(REQUIRED_MARKERS["find_next_counter_const"])
    edge_const = text.index(REQUIRED_MARKERS["find_edge_counter_const"])
    next_fn = text.index(REQUIRED_MARKERS["find_next_bench_fn"])
    edge_fn = text.index(REQUIRED_MARKERS["find_edge_bench_fn"])
    next_loop = text.index(REQUIRED_MARKERS["find_next_counter_loop"])
    edge_loop = text.index(REQUIRED_MARKERS["find_edge_counter_loop"])
    next_print = text.index(REQUIRED_MARKERS["find_next_iterations_print"])
    edge_print = text.index(REQUIRED_MARKERS["find_edge_iterations_print"])

    if not next_const < next_fn < next_loop < edge_fn:
        return ("find_next_counter_not_bound_to_bench_loop", [])
    if not edge_const < edge_fn < edge_loop < next_print < edge_print:
        return ("find_edge_counter_not_bound_to_bench_loop", [])

    return ("pass", text)


def validate_file(path: Path) -> tuple[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_bench_source", path)
    return validate_text(text)


def sample_bench(omit_label: str | None = None, duplicate_label: str | None = None) -> str:
    lines = [
        REQUIRED_MARKERS["find_next_counter_const"],
        REQUIRED_MARKERS["find_edge_counter_const"],
        REQUIRED_MARKERS["find_next_bench_fn"],
        "    var idx: u64 = 0;",
        f"    {REQUIRED_MARKERS['find_next_counter_loop']}",
        "    }",
        "}",
        REQUIRED_MARKERS["find_edge_bench_fn"],
        "    var idx: u64 = 0;",
        f"    {REQUIRED_MARKERS['find_edge_counter_loop']}",
        "    }",
        "}",
        "const find_bit_result = findBitBench();",
        "const find_bit_edge_result = findBitEdgeBench();",
        REQUIRED_MARKERS["find_next_iterations_print"],
        REQUIRED_MARKERS["find_edge_iterations_print"],
        REQUIRED_MARKERS["find_next_checksum_print"],
        REQUIRED_MARKERS["find_edge_checksum_print"],
    ]
    if omit_label is not None:
        lines = [line for line in lines if REQUIRED_MARKERS[omit_label] not in line]
    if duplicate_label is not None:
        lines.append(REQUIRED_MARKERS[duplicate_label])
    return "\n".join(lines) + "\n"


def assert_case(condition: bool, name: str, payload: object = None) -> None:
    if not condition:
        raise AssertionError((name, payload))


def run_self_test() -> None:
    cases = 0

    kind, payload = validate_text(sample_bench())
    assert_case(kind == "pass", "sample passes", (kind, payload))
    cases += 1

    kind, payload = validate_text(sample_bench(omit_label="find_next_counter_loop"))
    assert_case(kind == "missing_markers", "missing loop marker", (kind, payload))
    assert_case(payload == ["find_next_counter_loop"], "missing loop marker payload", payload)
    cases += 1

    kind, payload = validate_text(sample_bench(duplicate_label="find_edge_iterations_print"))
    assert_case(kind == "duplicate_or_ambiguous_markers", "duplicate print marker", (kind, payload))
    assert_case(payload == ["find_edge_iterations_print"], "duplicate print marker payload", payload)
    cases += 1

    unbound = sample_bench().replace(
        REQUIRED_MARKERS["find_next_counter_loop"],
        REQUIRED_MARKERS["find_edge_counter_loop"],
        1,
    )
    kind, payload = validate_text(unbound)
    assert_case(kind == "missing_markers", "counter swap loses next loop marker", (kind, payload))
    assert_case(payload == ["find_next_counter_loop"], "counter swap payload", payload)
    cases += 1

    with tempfile.TemporaryDirectory(prefix="phase1-find-bit-bench-loop-") as tmp:
        root = Path(tmp)
        path = bench_path(root)
        kind, payload = validate_file(path)
        assert_case(kind == "missing_bench_source", "missing source file", (kind, payload))
        cases += 1

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sample_bench(), encoding="utf-8")
        kind, payload = validate_file(path)
        assert_case(kind == "pass", "source file pass", (kind, payload))
        cases += 1

    print("PHASE1_FIND_BIT_BENCH_LOOP_COUNTER_CHECK_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_BENCH_LOOP_COUNTER_CHECK_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the Phase 1 find_bit bench counters are bound to their live bench loops."
    )
    parser.add_argument("--repo-root", "--root", dest="repo_root")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    path = bench_path(repo_root(args.repo_root))
    kind, payload = validate_file(path)
    if kind != "pass":
        print("PHASE1_FIND_BIT_BENCH_LOOP_COUNTER_CHECK=fail")
        print(f"PHASE1_FIND_BIT_BENCH_LOOP_COUNTER_CHECK_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_FIND_BIT_BENCH_LOOP_COUNTER_CHECK=pass")
    print(f"PHASE1_FIND_BIT_BENCH_LOOP_COUNTER_SOURCE={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
PHASE1_BENCH_REL = Path("zigux/tests/phase1_bench.zig")

FIND_BIT_BENCH_MARKERS = {
    "find_bit_bench_fn": "fn findBitBench() struct { checksum: u64 } {",
    "find_bit_edge_fn": "fn findBitEdgeBench() struct { checksum: u64 } {",
    "find_bit_bench_call": "const find_bit_result = findBitBench();",
    "find_bit_edge_call": "const find_bit_edge_result = findBitEdgeBench();",
    "find_next_iterations_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\\n", .{iterations_find_bit});',
    "find_next_checksum_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n", .{find_bit_result.checksum});',
    "find_edge_iterations_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\\n", .{iterations_find_bit_edge});',
    "find_edge_checksum_print": 'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n", .{find_bit_edge_result.checksum});',
    "boundary_next_bit": "checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));",
    "boundary_next_and_bit": "checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));",
    "boundary_next_zero_bit": "checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));",
    "tail_first_bit": "checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));",
    "tail_first_and_bit": "checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));",
    "tail_last_bit": "checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));",
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def bench_source_path(root: Path) -> Path:
    return root / PHASE1_BENCH_REL


def validate_bench_source(text: str) -> tuple[str, list[str]]:
    missing: list[str] = []
    duplicate: list[str] = []
    for label, marker in FIND_BIT_BENCH_MARKERS.items():
        count = text.count(marker)
        if count == 0:
            missing.append(label)
        elif count > 1:
            duplicate.append(f"{label}:count={count}")
    if missing:
        return ("missing_find_bit_bench_markers", missing)
    if duplicate:
        return ("duplicate_find_bit_bench_markers", duplicate)
    return ("pass", [])


def load_runtime_bench_source(path: Path) -> tuple[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_bench_source_file", path)
    kind, payload = validate_bench_source(text)
    return (kind, payload)


def build_sample_source(omit_label: str | None = None, duplicate_label: str | None = None) -> str:
    lines = [
        "fn findBitBench() struct { checksum: u64 } {",
        "    checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));",
        "    checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));",
        "    checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));",
        "}",
        "fn findBitEdgeBench() struct { checksum: u64 } {",
        "    checksum +%= @intCast(find_bit.findFirstBit(&tail_set, tail_nbits));",
        "    checksum +%= @intCast(find_bit.findFirstAndBit(&tail_set, &tail_set, tail_nbits));",
        "    checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));",
        "}",
        "const find_bit_result = findBitBench();",
        "const find_bit_edge_result = findBitEdgeBench();",
        'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS={d}\\n", .{iterations_find_bit});',
        'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n", .{find_bit_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS={d}\\n", .{iterations_find_bit_edge});',
        'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n", .{find_bit_edge_result.checksum});',
    ]

    if omit_label is not None:
        marker = FIND_BIT_BENCH_MARKERS[omit_label]
        lines = [line for line in lines if marker not in line]
    if duplicate_label is not None:
        marker = FIND_BIT_BENCH_MARKERS[duplicate_label]
        for idx, line in enumerate(lines):
            if marker in line:
                lines.insert(idx + 1, line)
                break
    return "\n".join(lines) + "\n"


def assert_case(condition: bool, name: str, payload: object = None) -> None:
    if not condition:
        raise AssertionError((name, payload))


def run_self_test() -> None:
    case_count = 0

    kind, payload = validate_bench_source(build_sample_source())
    assert_case(kind == "pass", "baseline", (kind, payload))
    case_count += 1

    for label in FIND_BIT_BENCH_MARKERS:
        kind, payload = validate_bench_source(build_sample_source(omit_label=label))
        assert_case(kind == "missing_find_bit_bench_markers", f"missing {label}", (kind, payload))
        assert_case(payload == [label], f"missing payload {label}", payload)
        case_count += 1

    for label in FIND_BIT_BENCH_MARKERS:
        kind, payload = validate_bench_source(build_sample_source(duplicate_label=label))
        assert_case(kind == "duplicate_find_bit_bench_markers", f"duplicate {label}", (kind, payload))
        assert_case(payload == [f"{label}:count=2"], f"duplicate payload {label}", payload)
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-find-bit-bench-unique-") as tmp:
        source_path = Path(tmp) / PHASE1_BENCH_REL
        kind, payload = load_runtime_bench_source(source_path)
        assert_case(kind == "missing_bench_source_file", "missing runtime source", (kind, payload))
        case_count += 1

        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(build_sample_source(), encoding="utf-8")
        kind, payload = load_runtime_bench_source(source_path)
        assert_case(kind == "pass", "runtime source pass", (kind, payload))
        case_count += 1

    print("PHASE1_FIND_BIT_BENCH_UNIQUENESS_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_BENCH_UNIQUENESS_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that the Phase 1 find_bit bench source keeps each required marker exactly once."
    )
    parser.add_argument("--repo-root", "--root", dest="repo_root", help="Override the repository root used for validation.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases only.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.repo_root)
    phase1_bench = bench_source_path(root)
    kind, payload = load_runtime_bench_source(phase1_bench)
    if kind != "pass":
        print("PHASE1_FIND_BIT_BENCH_UNIQUENESS=fail")
        print(f"PHASE1_FIND_BIT_BENCH_UNIQUENESS_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_FIND_BIT_BENCH_UNIQUENESS=pass")
    print(f"PHASE1_FIND_BIT_BENCH_UNIQUENESS_SOURCE={phase1_bench}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

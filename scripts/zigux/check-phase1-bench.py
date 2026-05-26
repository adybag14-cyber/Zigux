#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
EXPECTATIONS_REL = Path("zigux/tests/fixtures/phase1_bench_expectations.json")
PHASE1_BENCH_REL = Path("zigux/tests/phase1_bench.zig")

EXPECTED_ITERATIONS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS": 20000,
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
    "PHASE1_BENCH_STRING_ITERATIONS": 40000,
    "PHASE1_BENCH_HWEIGHT_ITERATIONS": 100000,
    "PHASE1_BENCH_LIST_SORT_ITERATIONS": 1000,
    "PHASE1_BENCH_RBTREE_ITERATIONS": 4000,
}

EXPECTED_CHECKSUMS = [
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    "PHASE1_BENCH_STRING_CHECKSUM",
    "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
]

REQUIRED_EXACT_CHECKSUMS = set(EXPECTED_CHECKSUMS)
RBTREE_REQUIRED_ITERATIONS = {"PHASE1_BENCH_RBTREE_ITERATIONS"}
BITMAP_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
}
FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
}
STRING_REQUIRED_EXACT_CHECKSUMS = {"PHASE1_BENCH_STRING_CHECKSUM"}
HWEIGHT_REQUIRED_EXACT_CHECKSUMS = {"PHASE1_BENCH_HWEIGHT_CHECKSUM"}
LIST_SORT_REQUIRED_EXACT_CHECKSUMS = {"PHASE1_BENCH_LIST_SORT_CHECKSUM"}
RBTREE_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_RBTREE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
}

FIND_BIT_REQUIRED_SOURCE_MARKERS = {
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

RBTREE_REQUIRED_SOURCE_MARKERS = {
    "rbtree_bench_fn": "fn rbtreeBench() struct { checksum: u64 } {",
    "rbtree_postorder_safe_fn": "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
    "rbtree_find_add_fn": "fn rbtreeFindAddBench() struct { checksum: u64 } {",
    "rbtree_duplicate_fn": "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
    "rbtree_cached_fn": "fn rbtreeCachedBench() struct { checksum: u64 } {",
    "rbtree_bench_call": "const rbtree_result = rbtreeBench();",
    "rbtree_postorder_safe_call": "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();",
    "rbtree_find_add_call": "const rbtree_find_add_result = rbtreeFindAddBench();",
    "rbtree_duplicate_call": "const rbtree_duplicate_result = rbtreeDuplicateBench();",
    "rbtree_cached_call": "const rbtree_cached_result = rbtreeCachedBench();",
    "rbtree_iterations_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\\n", .{iterations_rbtree});',
    "rbtree_checksum_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CHECKSUM={d}\\n", .{rbtree_result.checksum});',
    "rbtree_postorder_safe_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\\n", .{rbtree_postorder_safe_result.checksum});',
    "rbtree_find_add_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\\n", .{rbtree_find_add_result.checksum});',
    "rbtree_duplicate_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\\n", .{rbtree_duplicate_result.checksum});',
    "rbtree_cached_print": 'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n", .{rbtree_cached_result.checksum});',
    "rbtree_insert": "rbtree.add(&entry.node, &root, less);",
    "rbtree_postorder": "var node = rbtree.firstPostorder(&root);",
    "rbtree_find_add": "const existing = rbtree.findAdd(&probe.node, &root, cmp);",
    "rbtree_duplicate_range": "var iter = rbtree.matchIterator(&duplicate_key, &root, key_cmp);",
    "rbtree_cached_leftmost": "const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);",
}

SOURCE_MARKER_SETS = (
    FIND_BIT_REQUIRED_SOURCE_MARKERS,
    RBTREE_REQUIRED_SOURCE_MARKERS,
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def expectations_path(root: Path) -> Path:
    return root / EXPECTATIONS_REL


def bench_source_path(root: Path) -> Path:
    return root / PHASE1_BENCH_REL


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    zig = shutil.which("zig")
    if zig:
        return zig
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def parse_output(stdout: str) -> tuple[dict[str, str], dict[str, int]]:
    parsed: dict[str, str] = {}
    counts: dict[str, int] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key] = value
        counts[key] = counts.get(key, 0) + 1
    return parsed, counts


def load_expectations_text(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_expectations(path: Path) -> object:
    return load_expectations_text(path.read_text(encoding="utf-8"))


def load_runtime_expectations(path: Path) -> tuple[str, object]:
    try:
        expectations = load_expectations(path)
    except FileNotFoundError:
        return ("missing_expectations_file", path)
    except json.JSONDecodeError as exc:
        return ("expectations_json_error", exc)
    kind, payload = validate_expectations(expectations)
    if kind != "pass":
        return (kind, payload)
    return ("pass", expectations)


def validate_expectations(expectations: object) -> tuple[str, object]:
    if not isinstance(expectations, dict):
        return ("expectations_type", type(expectations).__name__)
    if isinstance(expectations, DuplicateTrackingDict) and expectations.duplicate_keys:
        return ("expectations_duplicate_keys", expectations.duplicate_keys)
    if expectations.get("status") != "pass":
        return ("expectations_status", expectations.get("status"))

    iterations = expectations.get("iterations")
    checksums = expectations.get("checksums")
    exact_checksums = expectations.get("exact_checksums")

    if not isinstance(iterations, dict):
        return ("expectations_iterations_type", type(iterations).__name__)
    if isinstance(iterations, DuplicateTrackingDict) and iterations.duplicate_keys:
        return ("expectations_duplicate_iteration_keys", iterations.duplicate_keys)
    if not isinstance(checksums, list):
        return ("expectations_checksums_type", type(checksums).__name__)
    if not isinstance(exact_checksums, dict):
        return ("expectations_exact_checksums_type", type(exact_checksums).__name__)
    if isinstance(exact_checksums, DuplicateTrackingDict) and exact_checksums.duplicate_keys:
        return ("expectations_duplicate_exact_checksum_keys", exact_checksums.duplicate_keys)

    iteration_keys = set(iterations)
    missing_rbtree_iterations = sorted(RBTREE_REQUIRED_ITERATIONS - iteration_keys)
    if missing_rbtree_iterations:
        return ("expectations_missing_rbtree_iterations", missing_rbtree_iterations)
    if iteration_keys != set(EXPECTED_ITERATIONS):
        missing = sorted(set(EXPECTED_ITERATIONS) - iteration_keys)
        unexpected = sorted(iteration_keys - set(EXPECTED_ITERATIONS))
        if missing:
            return ("expectations_missing_iterations", missing)
        return ("expectations_unexpected_iteration", unexpected[0])
    for key, expected in EXPECTED_ITERATIONS.items():
        value = iterations.get(key)
        if not isinstance(value, int):
            return ("expectations_iteration_value_type", (key, type(value).__name__))
        if value != expected:
            if key in RBTREE_REQUIRED_ITERATIONS:
                return ("expectations_rbtree_iteration_value", (key, expected, value))
            return ("expectations_iteration_value", (key, expected, value))

    seen: set[str] = set()
    duplicates: list[str] = []
    for item in checksums:
        if not isinstance(item, str):
            return ("expectations_checksum_type", type(item).__name__)
        if item in seen and item not in duplicates:
            duplicates.append(item)
        seen.add(item)
    if duplicates:
        return ("expectations_duplicate_checksums", duplicates)
    if checksums != EXPECTED_CHECKSUMS:
        return ("expectations_checksum_order", checksums)
    checksum_keys = set(checksums)
    if checksum_keys != set(EXPECTED_CHECKSUMS):
        missing = sorted(set(EXPECTED_CHECKSUMS) - checksum_keys)
        unexpected = sorted(checksum_keys - set(EXPECTED_CHECKSUMS))
        if missing:
            return ("expectations_missing_checksums", missing)
        return ("expectations_unexpected_checksums", unexpected)

    exact_requirements = (
        ("expectations_checksums_bitmap_exact_required", BITMAP_REQUIRED_EXACT_CHECKSUMS),
        ("expectations_checksums_find_bit_exact_required", FIND_BIT_REQUIRED_EXACT_CHECKSUMS),
        ("expectations_checksums_string_exact_required", STRING_REQUIRED_EXACT_CHECKSUMS),
        ("expectations_checksums_hweight_exact_required", HWEIGHT_REQUIRED_EXACT_CHECKSUMS),
        ("expectations_checksums_list_sort_exact_required", LIST_SORT_REQUIRED_EXACT_CHECKSUMS),
        ("expectations_checksums_rbtree_exact_required", RBTREE_REQUIRED_EXACT_CHECKSUMS),
    )
    for reason, required_keys in exact_requirements:
        for key in sorted(required_keys):
            if key in checksum_keys and key not in exact_checksums:
                return (reason, key)

    exact_keys = set(exact_checksums)
    if exact_keys != REQUIRED_EXACT_CHECKSUMS:
        missing = sorted(REQUIRED_EXACT_CHECKSUMS - exact_keys)
        unexpected = sorted(exact_keys - REQUIRED_EXACT_CHECKSUMS)
        if missing:
            return ("expectations_missing_exact_checksums", missing)
        return ("expectations_unexpected_exact_checksums", unexpected)
    for key, value in exact_checksums.items():
        if not isinstance(value, int):
            return ("expectations_exact_checksum_value_type", (key, type(value).__name__))
        if value <= 0:
            return ("expectations_exact_checksum_nonpositive", (key, value))

    return ("pass", expectations)


def duplicate_marker_labels(text: str, marker_set: dict[str, str]) -> list[str]:
    duplicates: list[str] = []
    for label, marker in marker_set.items():
        if text.count(marker) > 1:
            duplicates.append(label)
    return duplicates


def validate_bench_source(text: str) -> tuple[str, object]:
    missing: list[str] = []
    for marker_set in SOURCE_MARKER_SETS:
        for label, marker in marker_set.items():
            if marker not in text:
                missing.append(label)
    if missing:
        return ("bench_source_missing_markers", missing)
    duplicate_rbtree_markers = duplicate_marker_labels(text, RBTREE_REQUIRED_SOURCE_MARKERS)
    if duplicate_rbtree_markers:
        return ("bench_source_duplicate_rbtree_markers", duplicate_rbtree_markers)
    return ("pass", text)


def load_runtime_bench_source(path: Path) -> tuple[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing_bench_source_file", path)
    return validate_bench_source(text)


def validate_output(expectations: dict[str, object], stdout: str) -> tuple[str, object]:
    parsed, counts = parse_output(stdout)
    required_keys = {
        "PHASE1_BENCH",
        *expectations["iterations"],
        *expectations["checksums"],
        *expectations["exact_checksums"],
    }
    duplicate = sorted(key for key in required_keys if counts.get(key, 0) > 1)
    if duplicate:
        return ("duplicate", duplicate)

    unexpected = sorted(
        key for key in parsed if key.startswith("PHASE1_BENCH") and key not in required_keys
    )
    if unexpected:
        return ("unexpected", unexpected)

    if parsed.get("PHASE1_BENCH") != expectations["status"]:
        return ("status", (expectations["status"], parsed.get("PHASE1_BENCH")))

    missing: list[str] = []
    for key, expected in expectations["iterations"].items():
        actual = parsed.get(key)
        if actual is None:
            if key in RBTREE_REQUIRED_ITERATIONS:
                return ("missing_rbtree_iterations", [key])
            missing.append(key)
            continue
        try:
            value = int(actual)
        except ValueError:
            return ("iteration_value_type", (key, actual))
        if value != expected:
            if key in RBTREE_REQUIRED_ITERATIONS:
                return ("rbtree_iteration_mismatch", (key, expected, actual))
            return ("iteration_mismatch", (key, expected, actual))

    exact_categories = (
        ("missing_rbtree_exact_checksums", RBTREE_REQUIRED_EXACT_CHECKSUMS),
        ("missing_bitmap_exact_checksums", BITMAP_REQUIRED_EXACT_CHECKSUMS),
        ("missing_find_bit_exact_checksums", FIND_BIT_REQUIRED_EXACT_CHECKSUMS),
        ("missing_string_exact_checksums", STRING_REQUIRED_EXACT_CHECKSUMS),
        ("missing_hweight_exact_checksums", HWEIGHT_REQUIRED_EXACT_CHECKSUMS),
        ("missing_list_sort_exact_checksums", LIST_SORT_REQUIRED_EXACT_CHECKSUMS),
    )
    for reason, keys in exact_categories:
        missing_exact = sorted(key for key in keys if parsed.get(key) is None)
        if missing_exact:
            return (reason, missing_exact)

    for key in expectations["checksums"]:
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            value = int(actual)
        except ValueError:
            return ("checksum_value_type", (key, actual))
        if value <= 0:
            return ("nonpositive_checksum", (key, actual))
        expected_exact = expectations["exact_checksums"].get(key)
        if expected_exact is not None and value != expected_exact:
            return ("exact_checksum_mismatch", (key, expected_exact, value))

    for key, expected_exact in expectations["exact_checksums"].items():
        if key in expectations["checksums"]:
            continue
        actual = parsed.get(key)
        if actual is None:
            missing.append(key)
            continue
        try:
            value = int(actual)
        except ValueError:
            return ("checksum_value_type", (key, actual))
        if value != expected_exact:
            return ("exact_checksum_mismatch", (key, expected_exact, value))

    if missing:
        return ("missing", missing)
    return ("pass", parsed)


def build_find_bit_bench_source(omit_label: str | None = None) -> str:
    lines = [
        "fn findBitBench() struct { checksum: u64 } {",
        "    checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));",
        "}",
        "fn findBitEdgeBench() struct { checksum: u64 } {",
        "    checksum +%= @intCast(find_bit.findNextBit(&boundary_set, head_nbits, boundary));",
        "    checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));",
        "    checksum +%= @intCast(find_bit.findNextZeroBit(&boundary_zero, head_nbits, boundary));",
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
        marker = FIND_BIT_REQUIRED_SOURCE_MARKERS[omit_label]
        lines = [line for line in lines if line != marker]
    return "\n".join(lines) + "\n"


def build_rbtree_bench_source(omit_label: str | None = None) -> str:
    lines = [
        "fn rbtreeBench() struct { checksum: u64 } {",
        "    rbtree.add(&entry.node, &root, less);",
        "}",
        "fn rbtreePostorderSafeBench() struct { checksum: u64 } {",
        "    var node = rbtree.firstPostorder(&root);",
        "}",
        "fn rbtreeFindAddBench() struct { checksum: u64 } {",
        "    const existing = rbtree.findAdd(&probe.node, &root, cmp);",
        "}",
        "fn rbtreeDuplicateBench() struct { checksum: u64 } {",
        "    var iter = rbtree.matchIterator(&duplicate_key, &root, key_cmp);",
        "}",
        "fn rbtreeCachedBench() struct { checksum: u64 } {",
        "    const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root);",
        "}",
        "const rbtree_result = rbtreeBench();",
        "const rbtree_postorder_safe_result = rbtreePostorderSafeBench();",
        "const rbtree_find_add_result = rbtreeFindAddBench();",
        "const rbtree_duplicate_result = rbtreeDuplicateBench();",
        "const rbtree_cached_result = rbtreeCachedBench();",
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_ITERATIONS={d}\\n", .{iterations_rbtree});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CHECKSUM={d}\\n", .{rbtree_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM={d}\\n", .{rbtree_postorder_safe_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM={d}\\n", .{rbtree_find_add_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM={d}\\n", .{rbtree_duplicate_result.checksum});',
        'try stdout_writer.interface.print("PHASE1_BENCH_RBTREE_CACHED_CHECKSUM={d}\\n", .{rbtree_cached_result.checksum});',
    ]
    if omit_label is not None:
        marker = RBTREE_REQUIRED_SOURCE_MARKERS[omit_label]
        lines = [line for line in lines if line != marker]
    return "\n".join(lines) + "\n"


def build_full_bench_source(
    omit_find_bit_label: str | None = None,
    omit_rbtree_label: str | None = None,
) -> str:
    return (
        build_find_bit_bench_source(omit_find_bit_label)
        + build_rbtree_bench_source(omit_rbtree_label)
    )


def base_expectations() -> dict[str, object]:
    return {
        "status": "pass",
        "iterations": dict(EXPECTED_ITERATIONS),
        "checksums": list(EXPECTED_CHECKSUMS),
        "exact_checksums": {
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM": 1,
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM": 2,
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM": 3,
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM": 4,
            "PHASE1_BENCH_STRING_CHECKSUM": 5,
            "PHASE1_BENCH_HWEIGHT_CHECKSUM": 6,
            "PHASE1_BENCH_LIST_SORT_CHECKSUM": 7,
            "PHASE1_BENCH_RBTREE_CHECKSUM": 8,
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM": 9,
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM": 10,
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM": 11,
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM": 12,
        },
    }


def assert_case(condition: bool, name: str, payload: object = None) -> None:
    if not condition:
        raise AssertionError((name, payload))


def run_main_with_args(argv: list[str]) -> tuple[int, str]:
    with tempfile.TemporaryDirectory(prefix="phase1-bench-main-") as tmp:
        work = Path(tmp)
        original_default = globals()["DEFAULT_ROOT"]
        try:
            globals()["DEFAULT_ROOT"] = work
            parser = argparse.ArgumentParser(description="Run and validate the bounded Phase 1 benchmark smoke output.")
        finally:
            globals()["DEFAULT_ROOT"] = original_default
    return (0, "")


def invoke_main(argv: list[str]) -> tuple[int, str]:
    import contextlib
    import io
    import sys

    original_argv = sys.argv[:]
    stdout = io.StringIO()
    try:
        sys.argv = [str(HERE), *argv]
        with contextlib.redirect_stdout(stdout):
            try:
                code = main()
            except SystemExit as exc:
                code = int(exc.code) if isinstance(exc.code, int) else 1
    finally:
        sys.argv = original_argv
    return code, stdout.getvalue()


def run_self_test() -> None:
    case_count = 0

    expectations = base_expectations()
    kind, payload = validate_expectations(expectations)
    assert_case(kind == "pass", "expectations pass", (kind, payload))
    case_count += 1

    kind, payload = validate_bench_source(build_full_bench_source())
    assert_case(kind == "pass", "bench source pass", (kind, payload))
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-source-") as tmp:
        source_path = Path(tmp) / "phase1_bench.zig"

        kind, payload = load_runtime_bench_source(source_path)
        assert_case(kind == "missing_bench_source_file", "missing bench source", (kind, payload))
        case_count += 1

        source_path.write_text(build_full_bench_source(), encoding="utf-8")
        kind, payload = load_runtime_bench_source(source_path)
        assert_case(kind == "pass", "loaded bench source pass", (kind, payload))
        case_count += 1

        source_path.write_text(
            build_full_bench_source(omit_find_bit_label="find_edge_checksum_print"),
            encoding="utf-8",
        )
        kind, payload = load_runtime_bench_source(source_path)
        assert_case(kind == "bench_source_missing_markers", "missing find_bit marker", (kind, payload))
        assert_case(payload == ["find_edge_checksum_print"], "missing find_bit marker payload", payload)
        case_count += 1

        source_path.write_text(
            build_full_bench_source(omit_rbtree_label="rbtree_cached_print"),
            encoding="utf-8",
        )
        kind, payload = load_runtime_bench_source(source_path)
        assert_case(kind == "bench_source_missing_markers", "missing rbtree marker", (kind, payload))
        assert_case(payload == ["rbtree_cached_print"], "missing rbtree marker payload", payload)
        case_count += 1

        source_path.write_text(
            build_full_bench_source() + RBTREE_REQUIRED_SOURCE_MARKERS["rbtree_cached_print"] + "\n",
            encoding="utf-8",
        )
        kind, payload = load_runtime_bench_source(source_path)
        assert_case(
            kind == "bench_source_duplicate_rbtree_markers",
            "duplicate rbtree marker",
            (kind, payload),
        )
        assert_case(
            payload == ["rbtree_cached_print"],
            "duplicate rbtree marker payload",
            payload,
        )
        case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-root-") as tmp:
        root = Path(tmp)
        source_path = bench_source_path(root)
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(build_full_bench_source(), encoding="utf-8")

        expectations_file = expectations_path(root)
        expectations_file.parent.mkdir(parents=True, exist_ok=True)
        expectations_file.write_text(json.dumps(base_expectations(), indent=2) + "\n", encoding="utf-8")

        assert_case(repo_root(str(root)) == root.resolve(), "repo root override")
        kind, payload = load_runtime_bench_source(bench_source_path(root))
        assert_case(kind == "pass", "bench source root override", (kind, payload))
        kind, payload = load_runtime_expectations(expectations_path(root))
        assert_case(kind == "pass", "expectations root override", (kind, payload))
        case_count += 3

    duplicate_top_level_text = """{
  \"status\": \"pass\",
  \"status\": \"fail\",
  \"iterations\": {\"PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS\": 20000, \"PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS\": 20000, \"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS\": 20000, \"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS\": 20000, \"PHASE1_BENCH_STRING_ITERATIONS\": 40000, \"PHASE1_BENCH_HWEIGHT_ITERATIONS\": 100000, \"PHASE1_BENCH_LIST_SORT_ITERATIONS\": 1000, \"PHASE1_BENCH_RBTREE_ITERATIONS\": 4000},
  \"checksums\": [\"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM\", \"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM\", \"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\", \"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\", \"PHASE1_BENCH_STRING_CHECKSUM\", \"PHASE1_BENCH_HWEIGHT_CHECKSUM\", \"PHASE1_BENCH_LIST_SORT_CHECKSUM\", \"PHASE1_BENCH_RBTREE_CHECKSUM\", \"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM\", \"PHASE1_BENCH_FIND_ADD_CHECKSUM\", \"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM\", \"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"],
  \"exact_checksums\": {\"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM\": 1, \"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM\": 2, \"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\": 3, \"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\": 4, \"PHASE1_BENCH_STRING_CHECKSUM\": 5, \"PHASE1_BENCH_HWEIGHT_CHECKSUM\": 6, \"PHASE1_BENCH_LIST_SORT_CHECKSUM\": 7, \"PHASE1_BENCH_RBTREE_CHECKSUM\": 8, \"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM\": 9, \"PHASE1_BENCH_FIND_ADD_CHECKSUM\": 10, \"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM\": 11, \"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\": 12}
}"""
    kind, payload = validate_expectations(load_expectations_text(duplicate_top_level_text))
    assert_case(kind == "expectations_duplicate_keys", "duplicate top-level key", (kind, payload))
    assert_case(payload == ["status"], "duplicate top-level payload", payload)
    case_count += 1

    missing_rbtree_iteration_expectations = base_expectations()
    del missing_rbtree_iteration_expectations["iterations"]["PHASE1_BENCH_RBTREE_ITERATIONS"]
    kind, payload = validate_expectations(missing_rbtree_iteration_expectations)
    assert_case(kind == "expectations_missing_rbtree_iterations", "missing rbtree expectation iteration", (kind, payload))
    assert_case(payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"], "missing rbtree expectation iteration payload", payload)
    case_count += 1

    missing_rbtree_exact_expectations = base_expectations()
    del missing_rbtree_exact_expectations["exact_checksums"]["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"]
    kind, payload = validate_expectations(missing_rbtree_exact_expectations)
    assert_case(kind == "expectations_checksums_rbtree_exact_required", "missing rbtree expectation exact checksum", (kind, payload))
    assert_case(payload == "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", "missing rbtree expectation exact checksum payload", payload)
    case_count += 1

    ok_output = "\n".join(
        [
            "PHASE1_BENCH=pass",
            "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS=20000",
            "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS=20000",
            "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000",
            "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000",
            "PHASE1_BENCH_STRING_ITERATIONS=40000",
            "PHASE1_BENCH_HWEIGHT_ITERATIONS=100000",
            "PHASE1_BENCH_LIST_SORT_ITERATIONS=1000",
            "PHASE1_BENCH_RBTREE_ITERATIONS=4000",
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM=1",
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM=2",
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM=3",
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM=4",
            "PHASE1_BENCH_STRING_CHECKSUM=5",
            "PHASE1_BENCH_HWEIGHT_CHECKSUM=6",
            "PHASE1_BENCH_LIST_SORT_CHECKSUM=7",
            "PHASE1_BENCH_RBTREE_CHECKSUM=8",
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM=9",
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM=10",
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM=11",
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=12",
        ]
    )

    kind, payload = validate_output(base_expectations(), ok_output)
    assert_case(kind == "pass", "output pass", (kind, payload))
    case_count += 1

    missing_rbtree_iteration_output = "\n".join(
        line for line in ok_output.splitlines() if line != "PHASE1_BENCH_RBTREE_ITERATIONS=4000"
    )
    kind, payload = validate_output(base_expectations(), missing_rbtree_iteration_output)
    assert_case(kind == "missing_rbtree_iterations", "missing rbtree output iteration", (kind, payload))
    assert_case(payload == ["PHASE1_BENCH_RBTREE_ITERATIONS"], "missing rbtree output iteration payload", payload)
    case_count += 1

    missing_rbtree_exact_output = "\n".join(
        line for line in ok_output.splitlines() if line != "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM=12"
    )
    kind, payload = validate_output(base_expectations(), missing_rbtree_exact_output)
    assert_case(kind == "missing_rbtree_exact_checksums", "missing rbtree output exact checksum", (kind, payload))
    assert_case(payload == ["PHASE1_BENCH_RBTREE_CACHED_CHECKSUM"], "missing rbtree output exact checksum payload", payload)
    case_count += 1

    with tempfile.TemporaryDirectory(prefix="phase1-bench-json-error-") as tmp:
        root = Path(tmp)
        malformed = expectations_path(root)
        malformed.parent.mkdir(parents=True, exist_ok=True)
        malformed.write_text('{"status": "pass",\n', encoding="utf-8")
        code, output = invoke_main(["--root", str(root)])
        lines = output.strip().splitlines()
        assert_case(code == 1, "json error exit", (code, lines))
        assert_case(lines[0] == "PHASE1_BENCH_CHECK=fail", "json error fail header", lines)
        assert_case(
            "PHASE1_BENCH_CHECK_REASON=expectations_json_error" in lines,
            "json error reason line",
            lines,
        )
        assert_case(
            f"PHASE1_BENCH_EXPECTATIONS={malformed}" in lines,
            "json error expectations path",
            lines,
        )
        assert_case(
            any(line.startswith("EXPECTATIONS_JSON_ERROR=") for line in lines),
            "json error message line",
            lines,
        )
        assert_case(
            any(line.startswith("EXPECTATIONS_JSON_LINE=") for line in lines),
            "json error line number",
            lines,
        )
        assert_case(
            any(line.startswith("EXPECTATIONS_JSON_COLUMN=") for line in lines),
            "json error column",
            lines,
        )
        case_count += 1

    print("PHASE1_BENCH_CHECK_SELF_TEST=pass")
    print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and validate the bounded Phase 1 benchmark smoke output.")
    parser.add_argument("--repo-root", "--root", dest="repo_root", help="Override the repository root used for validation.")
    parser.add_argument("--zig", help="Path to Zig executable")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-test cases without invoking Zig.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.repo_root)
    expectations_file = expectations_path(root)
    phase1_bench = bench_source_path(root)

    kind, payload = load_runtime_expectations(expectations_file)
    if kind == "missing_expectations_file":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(f"EXPECTATIONS_PATH={payload}")
        return 1
    if kind == "expectations_json_error":
        exc = payload
        assert isinstance(exc, json.JSONDecodeError)
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")
        print(f"EXPECTATIONS_JSON_ERROR={exc.msg}")
        print(f"EXPECTATIONS_JSON_LINE={exc.lineno}")
        print(f"EXPECTATIONS_JSON_COLUMN={exc.colno}")
        return 1
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(payload)
        return 1

    expectations = payload
    assert isinstance(expectations, dict)

    kind, payload = load_runtime_bench_source(phase1_bench)
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(payload)
        return 1

    zig = find_zig(args.zig)
    result = subprocess.run(
        [zig, "build", "bench", "--build-file", "zigux/tests/build.zig", "-Doptimize=ReleaseSafe"],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("PHASE1_BENCH_CHECK=fail")
        print(f"BENCH_COMMAND_EXIT={result.returncode}")
        if result.stdout:
            print(result.stdout.rstrip("\n"))
        if result.stderr:
            print(result.stderr.rstrip("\n"))
        return 1

    kind, payload = validate_output(expectations, result.stdout)
    if kind != "pass":
        print("PHASE1_BENCH_CHECK=fail")
        print(f"PHASE1_BENCH_CHECK_REASON={kind}")
        print(payload)
        return 1

    print("PHASE1_BENCH_CHECK=pass")
    print(f"PHASE1_BENCH_EXPECTATIONS={expectations_file}")
    print(f"PHASE1_BENCH_SOURCE={phase1_bench}")
    print(f"PHASE1_BENCH_ZIG={zig}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
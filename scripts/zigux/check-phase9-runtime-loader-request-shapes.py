#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
REQUEST_SHAPES_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig"

REQUIRED_MARKERS = [
    'test "shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned" {',
    '        "runtime_bitmap",',
    '        "lib/test_bitmap.c",',
    '        "runtime_kretprobe",',
    '        "samples/kprobes/kretprobe_example.c",',
    "    try expectInitializedSharedRequestShape(bitmap_plan, .arena);",
    "    try expectInitializedSharedRequestShape(kretprobe_plan, .caller_provided);",
    "    var bitmap_request = try runtime_loader.prepareRequest(bitmap_plan);",
    "    var kretprobe_request = try runtime_loader.prepareRequest(kretprobe_plan);",
    "    const bitmap_pending = try bitmap_request.requestRuntimeLoad();",
    "    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();",
    "    try bitmap_request.releaseWithoutSubstrate();",
    "    try kretprobe_request.releaseWithoutSubstrate();",
]

EXACT_ONCE_MARKERS = [
    'test "shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned" {',
    "    try expectInitializedSharedRequestShape(bitmap_plan, .arena);",
    "    try expectInitializedSharedRequestShape(kretprobe_plan, .caller_provided);",
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / REQUEST_SHAPES_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_line_occurrences(content: str, marker: str) -> int:
    return sum(1 for line in content.splitlines() if line == marker)


def duplicate_marker_occurrence(content: str, marker: str) -> str:
    return content.replace(marker, f"{marker}\n{marker}", 1)


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    request_shapes_path = root / REQUEST_SHAPES_PATH
    if not request_shapes_path.exists():
        return [f"missing_file:{REQUEST_SHAPES_PATH}"]

    content = read_text(root, REQUEST_SHAPES_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in content:
            failures.append(f"missing_marker:{REQUEST_SHAPES_PATH}:{marker}")

    for marker in EXACT_ONCE_MARKERS:
        count = count_exact_line_occurrences(content, marker)
        if count != 1:
            failures.append(
                f"expected_exact_once:{REQUEST_SHAPES_PATH}:{marker}:count={count}"
            )

    return failures


def build_fixture_text() -> str:
    return """const std = @import(\"std\");
const runtime_loader = @import(\"runtime_loader\");
const contract = @import(\"runtime_loader_contract\");

const AllocatorHandoff = contract.AllocatorHandoff;
const LoadPlan = contract.LoadPlan;

fn makeInitializedPlan(
    module_name: []const u8,
    anchor: []const u8,
    entry_symbol: []const u8,
    exit_symbol: []const u8,
    allocator_handoff: AllocatorHandoff,
) LoadPlan {
    _ = entry_symbol;
    _ = exit_symbol;
    return .{
        .module_name = module_name,
        .anchor = anchor,
        .entry_symbol = \"unused\",
        .exit_symbol = \"unused\",
        .requires_runtime_substrate = true,
        .provides_selftest_hook = true,
        .allocator_handoff = allocator_handoff,
        .init_flow = .{
            .handoff_stage = .initialized,
            .init_runs = 1,
            .selftest_runs = 0,
            .exit_runs = 0,
        },
    };
}

fn expectInitializedSharedRequestShape(plan: LoadPlan, allocator_handoff: AllocatorHandoff) !void {
    _ = plan;
    _ = allocator_handoff;
}

test \"shared runtime loader keeps initialized-stage bitmap and kretprobe request shape aligned\" {
    const bitmap_plan = makeInitializedPlan(
        \"runtime_bitmap\",
        \"lib/test_bitmap.c\",
        \"zigux_runtime_bitmap_init\",
        \"zigux_runtime_bitmap_exit\",
        .arena,
    );
    const kretprobe_plan = makeInitializedPlan(
        \"runtime_kretprobe\",
        \"samples/kprobes/kretprobe_example.c\",
        \"zigux_runtime_kretprobe_init\",
        \"zigux_runtime_kretprobe_exit\",
        .caller_provided,
    );

    try expectInitializedSharedRequestShape(bitmap_plan, .arena);
    try expectInitializedSharedRequestShape(kretprobe_plan, .caller_provided);

    var bitmap_request = try runtime_loader.prepareRequest(bitmap_plan);
    var kretprobe_request = try runtime_loader.prepareRequest(kretprobe_plan);

    const bitmap_pending = try bitmap_request.requestRuntimeLoad();
    const kretprobe_pending = try kretprobe_request.requestRuntimeLoad();
    _ = bitmap_pending;
    _ = kretprobe_pending;

    try bitmap_request.releaseWithoutSubstrate();
    try kretprobe_request.releaseWithoutSubstrate();
}
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-runtime-loader-request-shapes-"))
    try:
        write_text(base / REQUEST_SHAPES_PATH, build_fixture_text())

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in REQUIRED_MARKERS:
            write_text(base / REQUEST_SHAPES_PATH, build_fixture_text())
            current = read_text(base, REQUEST_SHAPES_PATH)
            if current.count(marker) != 1:
                continue
            write_text(base / REQUEST_SHAPES_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{REQUEST_SHAPES_PATH}:{marker}")

        for marker in EXACT_ONCE_MARKERS:
            write_text(base / REQUEST_SHAPES_PATH, build_fixture_text())
            current = read_text(base, REQUEST_SHAPES_PATH)
            write_text(
                base / REQUEST_SHAPES_PATH,
                duplicate_marker_occurrence(current, marker),
            )
            expect_failure(
                base,
                f"expected_exact_once:{REQUEST_SHAPES_PATH}:{marker}:count=2",
            )

        write_text(base / REQUEST_SHAPES_PATH, build_fixture_text())
        (base / REQUEST_SHAPES_PATH).unlink()
        expect_failure(base, f"missing_file:{REQUEST_SHAPES_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_RUNTIME_LOADER_REQUEST_SHAPES_SELF_TEST=pass")
    print("PHASE9_RUNTIME_LOADER_REQUEST_SHAPES_FILE_COUNT=1")
    print(f"PHASE9_RUNTIME_LOADER_REQUEST_SHAPES_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_RUNTIME_LOADER_REQUEST_SHAPES_EXACT_ONCE_MARKER_COUNT="
        f"{len(EXACT_ONCE_MARKERS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the shared Phase 9 runtime-loader allocator/init-flow replay "
            "keeps the bitmap and kretprobe initialized-stage request shape explicit "
            "on current master."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_RUNTIME_LOADER_REQUEST_SHAPES_ERROR={failure}")
        return 1

    print("PHASE9_RUNTIME_LOADER_REQUEST_SHAPES_FILE_COUNT=1")
    print(f"PHASE9_RUNTIME_LOADER_REQUEST_SHAPES_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE9_RUNTIME_LOADER_REQUEST_SHAPES_EXACT_ONCE_MARKER_COUNT="
        f"{len(EXACT_ONCE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

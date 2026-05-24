#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile

SELF_PATH = Path(__file__).resolve()
SAMPLE_PATH = "samples/zigux/runtime_kretprobe.zig"
MODULE_PATH = "zigux/tests/runtime_kretprobe_module.zig"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SAMPLE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

FILE_MARKERS: dict[str, list[str]] = {
    SAMPLE_PATH: [
        '.name = "runtime_kretprobe"',
        '.anchor = "samples/kprobes/kretprobe_example.c"',
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
        'test "runtime kretprobe sample keeps selftest hook and return replay explicit" {',
        'test "runtime kretprobe sample keeps reusable probe replay explicit after selftest" {',
        'test "runtime kretprobe sample rejects re-selftest without disturbing summaries" {',
        'test "runtime kretprobe sample keeps failed exit rollback explicit while a probe is still registered" {',
        'test "runtime kretprobe sample keeps duplicate registration rollback explicit across initialized and selftested stages" {',
    ],
    MODULE_PATH: [
        'test "runtime kretprobe sample advertises the bounded pilot-module contract" {',
        'test "runtime kretprobe sample keeps selftest summary replay explicit at the module boundary" {',
        'test "runtime kretprobe sample keeps lifecycle snapshot replay explicit at the module boundary" {',
        'test "runtime kretprobe sample keeps rejected re-selftest rollback explicit at the module boundary" {',
        'test "runtime kretprobe sample keeps duplicate registration and failed exit rollback explicit at the module boundary" {',
        "try std.testing.expectError(error.ProbeAlreadyRegistered, selftested_module.registerProbe());",
        "try std.testing.expectError(error.OutstandingRegistration, selftested_module.exit());",
    ],
    PHASE9_BUILD_PATH: [
        '.root_source_file = b.path("../../samples/zigux/runtime_kretprobe.zig"),',
        '.name = "phase9-runtime-kretprobe-sample-tests"',
        '.root_source_file = b.path("runtime_kretprobe_module.zig"),',
        '.name = "phase9-runtime-kretprobe-module-tests"',
        '.name = "phase9-runtime-kretprobe-tests"',
        '"Run the Phase 9 runtime kretprobe sample and module lifecycle tests."',
    ],
}

FILE_EXACT_ONCE_MARKERS: dict[str, list[str]] = {
    SAMPLE_PATH: [
        'test "runtime kretprobe sample keeps failed exit rollback explicit while a probe is still registered" {',
        'test "runtime kretprobe sample keeps duplicate registration rollback explicit across initialized and selftested stages" {',
    ],
    MODULE_PATH: [
        'test "runtime kretprobe sample keeps duplicate registration and failed exit rollback explicit at the module boundary" {',
    ],
    PHASE9_BUILD_PATH: [
        '.name = "phase9-runtime-kretprobe-tests"',
    ],
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def break_marker(marker: str) -> str:
    if len(marker) == 1:
        return "_"
    replacement_tail = "_" if marker[-1] != "_" else "-"
    return marker[:-1] + replacement_tail


def tamper_marker_occurrences(content: str, marker: str) -> str:
    return content.replace(marker, break_marker(marker))


def duplicate_marker_occurrence(content: str, marker: str) -> str:
    return content.replace(marker, f"{marker}\n{marker}", 1)


def count_exact_line_occurrences(content: str, marker: str) -> int:
    return sum(1 for line in content.splitlines() if line == marker)


def build_fixture_text(rel_path: str, markers: list[str]) -> str:
    if rel_path.endswith(".zig"):
        return "\n".join(["const std = @import(\"std\");", "", *markers, ""])
    return "\n".join(markers) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in FILE_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in FILE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in FILE_EXACT_ONCE_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            count = count_exact_line_occurrences(text, marker)
            if count != 1:
                failures.append(f"expected_exact_once:{rel_path}:{marker}:count={count}")

    return failures


def seed_fixture_tree(base: Path) -> None:
    fixture_paths = set(FILE_MARKERS) | set(FILE_EXACT_ONCE_MARKERS)
    for rel_path in fixture_paths:
        markers = list(FILE_MARKERS.get(rel_path, []))
        for marker in FILE_EXACT_ONCE_MARKERS.get(rel_path, []):
            if marker not in markers:
                markers.append(marker)
        write_text(base / rel_path, build_fixture_text(rel_path, markers))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-kretprobe-runtime-packet-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, tamper_marker_occurrences(current, marker))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path, markers in FILE_EXACT_ONCE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, duplicate_marker_occurrence(current, marker))
                expect_failure(base, f"expected_exact_once:{rel_path}:{marker}:count=2")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_KRETPROBE_RUNTIME_PACKET_SELF_TEST=pass")
        print(f"PHASE9_KRETPROBE_RUNTIME_PACKET_FILE_COUNT={len(FILE_MARKERS)}")
        print(
            "PHASE9_KRETPROBE_RUNTIME_PACKET_EXACT_ONCE_MARKER_COUNT="
            f"{sum(len(markers) for markers in FILE_EXACT_ONCE_MARKERS.values())}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE9_KRETPROBE_RUNTIME_PACKET=pass")
    print(f"PHASE9_KRETPROBE_RUNTIME_PACKET_FILE_COUNT={len(FILE_MARKERS)}")
    print(
        "PHASE9_KRETPROBE_RUNTIME_PACKET_EXACT_ONCE_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_EXACT_ONCE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()

CATALOG_PATH = "scripts/zigux/phase9_catalog.py"
MANIFEST_PATH = "zigux/tests/runtime_pilot_manifest.json"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SAMPLE_PATH = "samples/zigux/runtime_atomic64.zig"
LOADER_PATH = "samples/zigux/runtime_atomic64_loader.zig"
MODULE_PATH = "zigux/tests/runtime_atomic64_module.zig"
DIFF_PATH = "zigux/tests/runtime_atomic64_diff.zig"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / CATALOG_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

FILE_MARKERS: dict[str, list[str]] = {
    CATALOG_PATH: [
        '"scripts/zigux/check-phase9-atomic64-runtime-packet.py"',
        '"zigux/tests/runtime_atomic64_diff.zig"',
        '"zigux/tests/runtime_atomic64_module.zig"',
        '"samples/zigux/runtime_atomic64.zig"',
        '"samples/zigux/runtime_atomic64_loader.zig"',
        '"zig build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig"',
        '"tighten one shared reminder surface at a time where current master still undercounts',
    ],
    MANIFEST_PATH: [
        '"scripts/zigux/check-phase9-atomic64-runtime-packet.py"',
        '"zigux/tests/runtime_atomic64_diff.zig"',
        '"zigux/tests/runtime_atomic64_module.zig"',
        '"samples/zigux/runtime_atomic64.zig"',
        '"samples/zigux/runtime_atomic64_loader.zig"',
        '"zig build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig"',
        '"scope": "shared reminder, manifest, catalog, ownership, validation, and module-metadata and depmod bridge boundary surfaces for the atomic64 pilot packet',
    ],
    PHASE9_BUILD_PATH: [
        '.root_source_file = b.path("../../samples/zigux/runtime_atomic64.zig")',
        '.root_source_file = b.path("../../samples/zigux/runtime_atomic64_loader.zig")',
        '.root_source_file = b.path("runtime_atomic64_diff.zig")',
        '.root_source_file = b.path("runtime_atomic64_module.zig")',
        '.name = "phase9-runtime-atomic64-diff-tests"',
        '.name = "phase9-runtime-atomic64-loader-tests"',
        '.name = "phase9-runtime-atomic64-module-tests"',
        '.name = "phase9-runtime-atomic64-sample-tests"',
        '"phase9-runtime-atomic64-tests"',
        "Run the Phase 9 runtime atomic64 lifecycle and differential replay tests.",
    ],
    MAKEFILE_PATH: [
        "phase9-runtime-atomic64-test:",
        "$(ZIG_REPO_ROOT) build phase9-runtime-atomic64-tests --build-file zigux/tests/phase9_build.zig --summary all",
        "phase9-test: phase9-runtime-atomic64-test",
    ],
    SAMPLE_PATH: [
        '.name = "runtime_atomic64"',
        '.anchor = "lib/atomic64_test.c"',
        ".requires_runtime_substrate = true",
        ".provides_selftest_hook = true",
        'test "runtime atomic64 sample rejects re-selftest without disturbing lifecycle summaries" {',
        'test "runtime atomic64 sample rejects re-init without disturbing initialized, selftest-complete, and exited summaries" {',
        'test "runtime atomic64 sample rejects re-exit without disturbing exited summaries" {',
    ],
    LOADER_PATH: [
        'test "runtime atomic64 loader keeps blocked publication and depmod surfaces out of the loader-facing payload" {',
        '"modinfo"',
        '"module_install_root"',
        '"depmod_manifest"',
        'test "runtime atomic64 loader keeps loaded seed stable through selftest and exit" {',
        'test "runtime atomic64 loader rejects re-selftest without disturbing summaries" {',
        'test "runtime atomic64 loader rejects re-exit without disturbing exited summaries" {',
    ],
    MODULE_PATH: [
        'test "runtime atomic64 sample advertises the bounded pilot-module contract" {',
        'test "runtime atomic64 sample keeps selftest summary replay explicit at the module boundary" {',
        'test "runtime atomic64 sample keeps lifecycle snapshot replay explicit at the module boundary" {',
        'test "runtime atomic64 sample keeps post-selftest mutation replay explicit at the module boundary" {',
        'test "runtime atomic64 sample keeps rejected re-selftest rollback explicit at the module boundary" {',
        'test "runtime atomic64 sample keeps rejected re-exit rollback explicit at the module boundary" {',
    ],
    DIFF_PATH: [
        'test "runtime atomic64 diff gate replays bounded atomic64_test.c arithmetic, exchange, cmpxchg, add_unless, and bitwise expectations" {',
        'test "runtime atomic64 diff gate keeps inc_not_zero and dec_if_positive guard paths explicit" {',
        'test "runtime atomic64 diff gate keeps selftest family coverage explicit" {',
        'test "runtime atomic64 diff gate rejects an empty threshold replay batch" {',
        'test "runtime atomic64 diff gate keeps a deterministic threshold replay batch ready for future perf baselines" {',
    ],
}

FILE_EXACT_ONCE_MARKERS: dict[str, list[str]] = {}


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
    if rel_path.endswith(".md"):
        return "\n".join(["# fixture", "", *markers, ""])
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
    base = Path(tempfile.mkdtemp(prefix="phase9-atomic64-runtime-packet-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                mutated = tamper_marker_occurrences(current, marker)
                if mutated == current:
                    raise SystemExit(f"unable to tamper marker for self-test: {rel_path}:{marker}")
                write_text(base / rel_path, mutated)
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

        print("PHASE9_ATOMIC64_RUNTIME_PACKET_SELF_TEST=pass")
        print(
            "PHASE9_ATOMIC64_RUNTIME_PACKET_MARKER_COUNT="
            f"{sum(len(markers) for markers in FILE_MARKERS.values())}"
        )
        print(
            "PHASE9_ATOMIC64_RUNTIME_PACKET_EXACT_ONCE_COUNT="
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

    print("PHASE9_ATOMIC64_RUNTIME_PACKET=pass")
    print(
        "PHASE9_ATOMIC64_RUNTIME_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_MARKERS.values())}"
    )
    print(
        "PHASE9_ATOMIC64_RUNTIME_PACKET_EXACT_ONCE_COUNT="
        f"{sum(len(markers) for markers in FILE_EXACT_ONCE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

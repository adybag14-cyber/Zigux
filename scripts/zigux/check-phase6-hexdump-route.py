#!/usr/bin/env python3
"""Guard the current Phase 6 hexdump review route."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MAKEFILE = Path("zigux/Makefile")
BUILD_FILE = Path("zigux/tests/phase6_build.zig")
PERF_FILE = Path("zigux/tests/phase6_hexdump_perf.zig")
PERF_MATRIX_FILE = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
CATALOG_FILE = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")

MAKEFILE_MARKERS = (
    "phase6-hexdump-review:",
    "$(PYTHON) scripts/zigux/check-phase6-hexdump-route.py",
)

BUILD_MARKERS = (
    'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
    'const hexdump_perf_matrix_test_step = b.step(',
    '"phase6-hexdump-perf-matrix-test",',
    "hexdump_review_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
    "hexdump_perf_matrix_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
)

PERF_MARKERS = (
    "try validatePerfMatrix();",
    'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
    "PHASE6_HEXDUMP_PERF={s}",
    "error.HexdumpPerfRegression",
)

PERF_MATRIX_MARKERS = (
    "pub fn validatePerfMatrix() !void {",
    '.label = "16B-plain-g1",',
    '.label = "32B-ascii-g2",',
    '.label = "16B-ascii-g4",',
    '.label = "16B-ascii-g8",',
    ".max_slowdown_pct = 175,",
    ".max_slowdown_pct = 550,",
    ".max_slowdown_pct = 600,",
    'test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {',
)

CATALOG_MARKERS = (
    "- `python3 scripts/zigux/check-phase6-hexdump-route.py`",
    "- `zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-hexdump-review`",
)

SELF_TEST_CASE_COUNT = 12


def resolve(root: Path, relative: Path) -> Path:
    return root / relative


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase6 hexdump route checker missing required file: {path.as_posix()}") from exc



def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def require_markers(path: Path, text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(
                f"phase6 hexdump route checker missing {label} marker in {path.as_posix()}: {marker}"
            )



def check_repo(root: Path) -> None:
    require_markers(resolve(root, MAKEFILE), read_text(resolve(root, MAKEFILE)), MAKEFILE_MARKERS, "Makefile")
    require_markers(resolve(root, BUILD_FILE), read_text(resolve(root, BUILD_FILE)), BUILD_MARKERS, "build")
    require_markers(resolve(root, PERF_FILE), read_text(resolve(root, PERF_FILE)), PERF_MARKERS, "perf")
    require_markers(
        resolve(root, PERF_MATRIX_FILE),
        read_text(resolve(root, PERF_MATRIX_FILE)),
        PERF_MATRIX_MARKERS,
        "perf-matrix",
    )
    require_markers(resolve(root, CATALOG_FILE), read_text(resolve(root, CATALOG_FILE)), CATALOG_MARKERS, "catalog")



def scaffold_repo(root: Path) -> None:
    write_text(resolve(root, MAKEFILE), "\n".join(MAKEFILE_MARKERS) + "\n")
    write_text(resolve(root, BUILD_FILE), "\n".join(BUILD_MARKERS) + "\n")
    write_text(resolve(root, PERF_FILE), "\n".join(PERF_MARKERS) + "\n")
    write_text(resolve(root, PERF_MATRIX_FILE), "\n".join(PERF_MATRIX_MARKERS) + "\n")
    write_text(resolve(root, CATALOG_FILE), "\n".join(CATALOG_MARKERS) + "\n")



def expect_failure(root: Path, path: Path, marker: str) -> None:
    original = read_text(path)
    if marker not in original:
        raise AssertionError(f"self-test marker not found: {marker}")
    write_text(path, original.replace(marker, "", 1))
    try:
        check_repo(root)
    except SystemExit as exc:
        if marker not in str(exc):
            raise AssertionError(f"expected marker {marker!r} in failure, got {exc!s}") from exc
    else:
        raise AssertionError("expected validation failure")
    finally:
        write_text(path, original)



def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_hexdump_route_") as tmp_dir:
        root = Path(tmp_dir)
        scaffold_repo(root)
        check_repo(root)

        cases_run = 0
        for path, marker in (
            (resolve(root, MAKEFILE), MAKEFILE_MARKERS[0]),
            (resolve(root, MAKEFILE), MAKEFILE_MARKERS[1]),
            (resolve(root, BUILD_FILE), BUILD_MARKERS[0]),
            (resolve(root, BUILD_FILE), BUILD_MARKERS[3]),
            (resolve(root, BUILD_FILE), BUILD_MARKERS[4]),
            (resolve(root, PERF_FILE), PERF_MARKERS[0]),
            (resolve(root, PERF_FILE), PERF_MARKERS[2]),
            (resolve(root, PERF_MATRIX_FILE), PERF_MATRIX_MARKERS[3]),
            (resolve(root, PERF_MATRIX_FILE), PERF_MATRIX_MARKERS[7]),
            (resolve(root, PERF_MATRIX_FILE), PERF_MATRIX_MARKERS[8]),
            (resolve(root, CATALOG_FILE), CATALOG_MARKERS[0]),
        ):
            expect_failure(root, path, marker)
            cases_run += 1

        scaffold_repo(root)
        resolve(root, PERF_MATRIX_FILE).unlink()
        try:
            check_repo(root)
        except SystemExit as exc:
            if PERF_MATRIX_FILE.as_posix() not in str(exc):
                raise AssertionError(f"expected missing file path in failure, got {exc!s}") from exc
        else:
            raise AssertionError("expected missing file failure")
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_HEXDUMP_ROUTE_SELF_TEST=pass")
    print(f"PHASE6_HEXDUMP_ROUTE_SELF_TEST_CASE_COUNT={cases_run}")
    return 0



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in route-guard self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_repo(args.root.resolve())
    print("PHASE6_HEXDUMP_ROUTE=pass")
    print(f"PHASE6_HEXDUMP_ROUTE_MAKEFILE={resolve(args.root.resolve(), MAKEFILE)}")
    print(f"PHASE6_HEXDUMP_ROUTE_BUILD={resolve(args.root.resolve(), BUILD_FILE)}")
    print(f"PHASE6_HEXDUMP_ROUTE_PERF_MATRIX={resolve(args.root.resolve(), PERF_MATRIX_FILE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

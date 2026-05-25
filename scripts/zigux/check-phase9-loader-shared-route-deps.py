#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"

REQUIRED_MARKERS = [
    'const runtime_trace_events_loader_substrate_drift_module = b.createModule(.{',
    '.root_source_file = b.path("runtime_trace_events_loader_substrate_drift.zig"),',
    'const runtime_trace_events_loader_substrate_drift_tests = b.addTest(.{',
    '.name = "phase9-runtime-trace-events-loader-substrate-drift-tests",',
    'const phase9_runtime_loader_shared = b.step(',
    '"phase9-runtime-loader-shared-tests",',
    'phase9_runtime_loader_shared.dependOn(&run_runtime_loader_kernel_tests.step);',
    'phase9_runtime_loader_shared.dependOn(&run_runtime_loader_contract_tests.step);',
    'phase9_runtime_loader_shared.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);',
    '&run_runtime_loader_command_env_boundary_guard_tests.step,',
    '&run_runtime_trace_events_loader_substrate_drift_tests.step,',
    'phase9_runtime_loader_shared.dependOn(&run_runtime_bitmap_loader_tests.step);',
]


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / PHASE9_BUILD_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_text() -> str:
    return "\n".join(REQUIRED_MARKERS) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    target = root / PHASE9_BUILD_PATH
    if not target.exists():
        return [f"missing_file:{PHASE9_BUILD_PATH}"]

    text = read_text(root, PHASE9_BUILD_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{PHASE9_BUILD_PATH}:{marker}")
    return failures


def tamper_marker(text: str, marker: str) -> str:
    if marker not in text:
        raise ValueError(f"marker not present: {marker}")
    replacement = marker[:-1] + "_" if len(marker) > 1 else "_"
    return text.replace(marker, replacement, 1)


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-loader-shared-route-deps-"))
    try:
        write_text(base / PHASE9_BUILD_PATH, build_fixture_text())
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in REQUIRED_MARKERS:
            write_text(base / PHASE9_BUILD_PATH, build_fixture_text())
            current = read_text(base, PHASE9_BUILD_PATH)
            write_text(base / PHASE9_BUILD_PATH, tamper_marker(current, marker))
            expect_failure(base, f"missing_marker:{PHASE9_BUILD_PATH}:{marker}")

        write_text(base / PHASE9_BUILD_PATH, build_fixture_text())
        (base / PHASE9_BUILD_PATH).unlink()
        expect_failure(base, f"missing_file:{PHASE9_BUILD_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_LOADER_SHARED_ROUTE_DEPS_SELF_TEST=pass")
    print(f"PHASE9_LOADER_SHARED_ROUTE_DEPS_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the shared Phase 9 loader rerun route in "
            "`zigux/tests/phase9_build.zig` keeps the kernel, contract, "
            "allocator/init-flow, command/environment boundary, trace-events "
            "loader-substrate drift, and bitmap-loader shards wired into "
            "`phase9-runtime-loader-shared-tests`."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_LOADER_SHARED_ROUTE_DEPS_ERROR={failure}")
        return 1

    print("PHASE9_LOADER_SHARED_ROUTE_DEPS=pass")
    print(f"PHASE9_LOADER_SHARED_ROUTE_DEPS_ROOT={args.repo_root}")
    print(f"PHASE9_LOADER_SHARED_ROUTE_DEPS_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

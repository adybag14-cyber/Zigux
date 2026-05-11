#!/usr/bin/env python3
"""Fail-closed checks for the shared Phase 9 runtime-loader replay packet."""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile


BUILD_EXPECTATIONS = (
    '.root_source_file = b.path("runtime_loader_allocator_init_flow.zig")',
    'runtime_loader_allocator_init_flow_module.addImport("runtime_loader", runtime_loader_facade_module);',
    'runtime_loader_allocator_init_flow_module.addImport("runtime_loader_contract", runtime_loader_contract_module);',
    '"phase9-runtime-loader-shared-tests"',
    'runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_contract_tests.step);',
    'runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_facade_tests.step);',
    'runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);',
)

ALLOCATOR_FLOW_EXPECTATIONS = (
    'test "phase 9 runtime loader allocator/init-flow replay keeps the smallest shared bitmap and kretprobe request shape explicit" {',
    'test "phase 9 runtime loader allocator/init-flow replay keeps bitmap and kretprobe selftest-complete request shape parity explicit" {',
    'test "phase 9 runtime loader allocator/init-flow replay keeps initialized prepared snapshots stable even if later live state would look exited" {',
    'request.plan.init_flow.selftest_runs = 2;',
    'error.PreparedPlanDrift',
)

README_EXPECTATIONS = (
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`make -C zigux phase9-runtime-loader-shared-tests`",
    "there is no dedicated shared `validate-phase9.py`",
)


def _read(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"missing required file: {path}") from exc


def _require(haystack: str, needle: str, label: str) -> None:
    if needle not in haystack:
        raise SystemExit(f"missing {label}: {needle}")


def check(root: pathlib.Path) -> None:
    build = _read(root / "zigux/tests/phase9_build.zig")
    allocator_flow = _read(root / "zigux/tests/runtime_loader_allocator_init_flow.zig")
    readme = _read(root / "scripts/zigux/README.md")

    for needle in BUILD_EXPECTATIONS:
        _require(build, needle, "Phase 9 build marker")

    for needle in ALLOCATOR_FLOW_EXPECTATIONS:
        _require(allocator_flow, needle, "allocator/init-flow replay marker")

    for needle in README_EXPECTATIONS:
        _require(readme, needle, "scripts README runtime-loader marker")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir)
        (root / "zigux/tests").mkdir(parents=True)
        (root / "scripts/zigux").mkdir(parents=True)

        (root / "zigux/tests/phase9_build.zig").write_text(
            "\n".join(BUILD_EXPECTATIONS) + "\n",
            encoding="utf-8",
        )
        (root / "zigux/tests/runtime_loader_allocator_init_flow.zig").write_text(
            "\n".join(ALLOCATOR_FLOW_EXPECTATIONS) + "\n",
            encoding="utf-8",
        )
        (root / "scripts/zigux/README.md").write_text(
            "\n".join(README_EXPECTATIONS) + "\n",
            encoding="utf-8",
        )

        check(root)

        (root / "zigux/tests/runtime_loader_allocator_init_flow.zig").write_text(
            "\n".join(ALLOCATOR_FLOW_EXPECTATIONS[:-1]) + "\n",
            encoding="utf-8",
        )
        try:
            check(root)
        except SystemExit as exc:
            if "allocator/init-flow replay marker" not in str(exc):
                raise SystemExit(f"unexpected self-test failure: {exc}") from exc
        else:
            raise SystemExit("self-test expected missing replay marker failure")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Check the shared Phase 9 runtime-loader replay packet."
    )
    parser.add_argument(
        "--repo-root",
        type=pathlib.Path,
        default=pathlib.Path("."),
        help="Path to the Zigux repository root (default: current directory).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        run_self_test()
        return 0

    check(args.repo_root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

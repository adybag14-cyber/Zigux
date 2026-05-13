#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/README.md").exists() and (candidate / "zigux/Makefile").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

NOTE_PATH = "Documentation/zigux/phase9-runtime-loader-allocator-init-flow-evidence.md"
TEST_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig"
BUILD_PATH = "zigux/tests/phase9_build.zig"

NOTE_MARKERS = [
    "PHASE9_SLICE=runtime-loader-allocator-init-flow-evidence",
    "PHASE9_EXACT_CHECK_TEST_COUNT=14",
    "PHASE9_PREPARED_PLAN_DRIFT_CASE_COUNT=8",
    "PHASE9_SHARED_BUILD_ROUTE_MARKER_COUNT=10",
    "make -C zigux phase9-runtime-loader-shared-tests",
    "python3 scripts/zigux/check-phase9-allocator-init-flow-evidence.py",
    "The replay covers all four shipped pilot families",
    "Prepared-plan drift still keeps the request pinned in prepared state across eight mutations",
    "The shared build route still carries ten exact route markers",
]

TEST_MARKERS = [
    'test "phase 9 runtime loader allocator/init-flow replay covers all shipped runtime pilot handoffs"',
    'test "phase 9 runtime loader allocator/init-flow replay keeps the smallest shared bitmap and kretprobe request shape explicit"',
    'test "phase 9 runtime loader allocator/init-flow replay keeps caller-provided selftest-complete request shape explicit across atomic64 and trace-events"',
    'test "phase 9 runtime loader allocator/init-flow replay keeps bitmap and kretprobe selftest-complete request shape parity explicit"',
    'test "phase 9 runtime loader allocator/init-flow replay keeps initialized prepared snapshots stable even if later live state would look exited"',
    'test "phase 9 runtime loader allocator/init-flow replay keeps selftest-complete prepared snapshots stable even if later live state would look exited"',
    'test "phase 9 runtime loader allocator/init-flow replay rejects missing-init, premature-selftest, exited, duplicate-init, duplicate-selftest, or incomplete handoffs"',
    'test "phase 9 runtime loader allocator/init-flow replay rejects direct approved-pilot-family drift"',
    'test "phase 9 runtime loader allocator/init-flow replay rejects loader-not-required handoffs directly"',
    'test "phase 9 runtime loader allocator/init-flow replay rejects selftest-hook evidence drift"',
    'test "phase 9 runtime loader allocator/init-flow replay keeps prepared snapshots pinned when requestRuntimeLoad sees prepared-plan drift"',
    'test "phase 9 runtime loader allocator/init-flow replay rejects stale loader state transitions"',
    'test "phase 9 runtime loader allocator/init-flow replay keeps the shared build route explicit"',
    'test "phase 9 runtime loader allocator/init-flow replay keeps exact current init and registration evidence explicit"',
]

BUILD_MARKERS = [
    '.root_source_file = b.path("runtime_loader_allocator_init_flow.zig")',
    'runtime_loader_allocator_init_flow_module.addImport("runtime_loader", runtime_loader_facade_module);',
    'runtime_loader_allocator_init_flow_module.addImport("runtime_loader_contract", runtime_loader_contract_module);',
    '.name = "phase9-runtime-loader-allocator-init-flow-tests"',
    '"phase9-runtime-loader-shared-tests"',
    'runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_contract_tests.step);',
    'runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_facade_tests.step);',
    'runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);',
    'test_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);',
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in [NOTE_PATH, TEST_PATH, BUILD_PATH]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    note = read_text(root, NOTE_PATH)
    test_source = read_text(root, TEST_PATH)
    build = read_text(root, BUILD_PATH)

    for marker in NOTE_MARKERS:
        if marker not in note:
            failures.append(f"missing_marker:{NOTE_PATH}:{marker}")

    for marker in TEST_MARKERS:
        if marker not in test_source:
            failures.append(f"missing_marker:{TEST_PATH}:{marker}")

    for marker in BUILD_MARKERS:
        if marker not in build:
            failures.append(f"missing_marker:{BUILD_PATH}:{marker}")

    return failures


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(
        root / NOTE_PATH,
        "\n".join(["# note", *NOTE_MARKERS, ""]),
    )
    write_text(
        root / TEST_PATH,
        "\n".join(["// test source", *TEST_MARKERS, ""]),
    )
    write_text(
        root / BUILD_PATH,
        "\n".join(["// build source", *BUILD_MARKERS, ""]),
    )


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-allocator-init-flow-evidence-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        note_path = base / NOTE_PATH
        note_text = note_path.read_text(encoding="utf-8")
        note_path.write_text(
            note_text.replace("PHASE9_EXACT_CHECK_TEST_COUNT=14", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:Documentation/zigux/phase9-runtime-loader-allocator-init-flow-evidence.md:PHASE9_EXACT_CHECK_TEST_COUNT=14",
        )

        write_fixture_tree(base)
        test_path = base / TEST_PATH
        test_text = test_path.read_text(encoding="utf-8")
        test_path.write_text(
            test_text.replace(
                'test "phase 9 runtime loader allocator/init-flow replay rejects selftest-hook evidence drift"',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            'missing_marker:zigux/tests/runtime_loader_allocator_init_flow.zig:test "phase 9 runtime loader allocator/init-flow replay rejects selftest-hook evidence drift"',
        )

        write_fixture_tree(base)
        build_path = base / BUILD_PATH
        build_text = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            build_text.replace(
                'runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:zigux/tests/phase9_build.zig:runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
        )
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_ALLOCATOR_INIT_FLOW_EVIDENCE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the Phase 9 runtime-loader allocator/init-flow exact-readback evidence packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_ALLOCATOR_INIT_FLOW_EVIDENCE_ERROR={failure}")
        return 1

    print("PHASE9_ALLOCATOR_INIT_FLOW_EVIDENCE_NOTE=pass")
    print(f"PHASE9_ALLOCATOR_INIT_FLOW_EVIDENCE_TEST_MARKER_COUNT={len(TEST_MARKERS)}")
    print("PHASE9_ALLOCATOR_INIT_FLOW_EVIDENCE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
TESTS_README_PATH = "zigux/tests/README.md"
SAMPLE_PATH = "samples/zigux/runtime_trace_events.zig"

TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
ABSENT_SHARED_LOADER_MARKER = "Current `master` does not currently expose the broader shared runtime-loader packet"
ABSENT_PHASE9_BUILD_MARKER = "`zigux/tests/phase9_build.zig`"
ABSENT_RUNTIME_LOADER_KERNEL_MARKER = "`zigux/kernel/runtime_loader.zig`"
ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER = "`samples/zigux/runtime_*_loader.zig` scaffolds"

TESTS_README_BACKLOG_MARKER = (
    "there is no shared `zigux/tests/runtime_*` replay packet, `zigux/tests/phase9_build.zig`, "
    "`make -C zigux phase9*` route family, or dedicated shared `validate-phase9.py` visible on current `master`"
)

SAMPLE_DESCRIPTOR_MARKER = ".provides_selftest_hook = true"
SAMPLE_RUN_SELFTEST_MARKER = "pub fn runSelftest(self: *Self) !EmissionSummary {"
SAMPLE_EXIT_MARKER = "pub fn exit(self: *Self) !void {"
SAMPLE_DUPLICATE_REGISTRATION_TEST_MARKER = (
    'test "trace-events sample rejects duplicate function-thread registration" {'
)
SAMPLE_DUPLICATE_REGISTRATION_ERROR_MARKER = "error.FunctionThreadAlreadyRegistered"
SAMPLE_CONTINUITY_TEST_MARKER = (
    'test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {'
)
SAMPLE_FAILED_EXIT_TEST_MARKER = (
    'test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {'
)
SAMPLE_REJECTED_SELFTEST_TEST_MARKER = (
    'test "trace-events sample keeps rejected re-selftest rollback explicit" {'
)
SAMPLE_INVALID_TRANSITION_MARKER = "error.InvalidLifecycleTransition"
SAMPLE_OUTSTANDING_REGISTRATION_MARKER = "error.OutstandingRegistration"

SEQUENCING_REQUIRED_MARKERS = [
    TRACE_EVENTS_SAMPLE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    ABSENT_SHARED_LOADER_MARKER,
    ABSENT_PHASE9_BUILD_MARKER,
    ABSENT_RUNTIME_LOADER_KERNEL_MARKER,
    ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER,
]

TESTS_README_REQUIRED_MARKERS = [
    TRACE_EVENTS_SAMPLE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    TESTS_README_BACKLOG_MARKER,
]

SAMPLE_REQUIRED_MARKERS = [
    SAMPLE_DESCRIPTOR_MARKER,
    SAMPLE_RUN_SELFTEST_MARKER,
    SAMPLE_EXIT_MARKER,
    SAMPLE_DUPLICATE_REGISTRATION_TEST_MARKER,
    SAMPLE_DUPLICATE_REGISTRATION_ERROR_MARKER,
    SAMPLE_CONTINUITY_TEST_MARKER,
    SAMPLE_FAILED_EXIT_TEST_MARKER,
    SAMPLE_REJECTED_SELFTEST_TEST_MARKER,
    SAMPLE_INVALID_TRANSITION_MARKER,
    SAMPLE_OUTSTANDING_REGISTRATION_MARKER,
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    sequencing_path = root / SEQUENCING_PATH
    tests_readme_path = root / TESTS_README_PATH
    sample_path = root / SAMPLE_PATH
    if not sequencing_path.exists():
        failures.append(f"missing_file:{SEQUENCING_PATH}")
    if not tests_readme_path.exists():
        failures.append(f"missing_file:{TESTS_README_PATH}")
    if not sample_path.exists():
        failures.append(f"missing_file:{SAMPLE_PATH}")
    if failures:
        return failures

    sequencing = read_text(root, SEQUENCING_PATH)
    for marker in SEQUENCING_REQUIRED_MARKERS:
        if marker not in sequencing:
            failures.append(f"missing_marker:{SEQUENCING_PATH}:{marker}")

    tests_readme = read_text(root, TESTS_README_PATH)
    for marker in TESTS_README_REQUIRED_MARKERS:
        if marker not in tests_readme:
            failures.append(f"missing_marker:{TESTS_README_PATH}:{marker}")

    sample = read_text(root, SAMPLE_PATH)
    for marker in SAMPLE_REQUIRED_MARKERS:
        if marker not in sample:
            failures.append(f"missing_marker:{SAMPLE_PATH}:{marker}")

    return failures


def build_sequencing_fixture_text() -> str:
    return f"""# Phase 9 Runtime Pilot Lane Sequencing

Current `master` keeps a narrow surviving runtime-pilot packet.

- surviving direct runtime-module sample: {TRACE_EVENTS_SAMPLE_MARKER}
- surviving runtime-module evidence inside that sample: {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}

{ABSENT_SHARED_LOADER_MARKER}.
Fresh repo-first rereads did not find {ABSENT_PHASE9_BUILD_MARKER}, the shared `zigux/tests/runtime_*` replay family, {ABSENT_RUNTIME_LOADER_KERNEL_MARKER}, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, or the older {ABSENT_RUNTIME_LOADER_SCAFFOLD_MARKER} on `master`.
"""


def build_tests_readme_fixture_text() -> str:
    return f"""# zigux/tests

Phase 9 review packet
  * the surviving trace-events sample still keeps the roadmap-backed runtime pilot shape concrete by exposing {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER} inside {TRACE_EVENTS_SAMPLE_MARKER}, so reviewers can still inspect one real runtime-module and selftest-hook surface while the broader shared loader packet remains backlog
  * {TESTS_README_BACKLOG_MARKER}
"""


def build_sample_fixture_text() -> str:
    return f"""const std = @import("std");

pub const ModuleDescriptor = struct {{
    provides_selftest_hook: bool,
}};

pub fn descriptor() ModuleDescriptor {{
    return .{{ .provides_selftest_hook = true }};
}}

pub fn runSelftest(self: *Self) !EmissionSummary {{
    _ = self;
    return undefined;
}}

pub fn exit(self: *Self) !void {{
    _ = self;
    return error.InvalidLifecycleTransition;
}}

test "trace-events sample rejects duplicate function-thread registration" {{
    try std.testing.expectError(error.FunctionThreadAlreadyRegistered, module.registerFunctionThread());
}}

test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity" {{
    try std.testing.expect(true);
}}

test "trace-events sample keeps failed-exit rollback explicit after selftest-ready replay" {{
    try std.testing.expectError(error.OutstandingRegistration, module.exit());
}}

test "trace-events sample keeps rejected re-selftest rollback explicit" {{
    try std.testing.expect(true);
}}
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-runtime-packet-"))
    try:
        sequencing_path = base / SEQUENCING_PATH
        tests_readme_path = base / TESTS_README_PATH
        sample_path = base / SAMPLE_PATH
        write_text(sequencing_path, build_sequencing_fixture_text())
        write_text(tests_readme_path, build_tests_readme_fixture_text())
        write_text(sample_path, build_sample_fixture_text())

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in SEQUENCING_REQUIRED_MARKERS:
            write_text(sequencing_path, build_sequencing_fixture_text().replace(marker, "", 1))
            write_text(tests_readme_path, build_tests_readme_fixture_text())
            write_text(sample_path, build_sample_fixture_text())
            expect_failure(base, f"missing_marker:{SEQUENCING_PATH}:{marker}")
            write_text(sequencing_path, build_sequencing_fixture_text())

        for marker in TESTS_README_REQUIRED_MARKERS:
            write_text(sequencing_path, build_sequencing_fixture_text())
            write_text(tests_readme_path, build_tests_readme_fixture_text().replace(marker, "", 1))
            write_text(sample_path, build_sample_fixture_text())
            expect_failure(base, f"missing_marker:{TESTS_README_PATH}:{marker}")
            write_text(tests_readme_path, build_tests_readme_fixture_text())

        for marker in SAMPLE_REQUIRED_MARKERS:
            write_text(sequencing_path, build_sequencing_fixture_text())
            write_text(tests_readme_path, build_tests_readme_fixture_text())
            write_text(sample_path, build_sample_fixture_text().replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{SAMPLE_PATH}:{marker}")
            write_text(sample_path, build_sample_fixture_text())

        shutil.rmtree(base / "Documentation", ignore_errors=True)
        expect_failure(base, f"missing_file:{SEQUENCING_PATH}")
        write_text(sequencing_path, build_sequencing_fixture_text())
        write_text(tests_readme_path, build_tests_readme_fixture_text())
        write_text(sample_path, build_sample_fixture_text())

        shutil.rmtree(base / "zigux/tests", ignore_errors=True)
        expect_failure(base, f"missing_file:{TESTS_README_PATH}")
        write_text(sequencing_path, build_sequencing_fixture_text())
        write_text(tests_readme_path, build_tests_readme_fixture_text())
        write_text(sample_path, build_sample_fixture_text())

        shutil.rmtree(base / "samples", ignore_errors=True)
        expect_failure(base, f"missing_file:{SAMPLE_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SELF_TEST=pass")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SEQUENCING_MARKER_COUNT={len(SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLE_MARKER_COUNT={len(SAMPLE_REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the surviving Phase 9 trace-events runtime packet stays aligned across the lane-sequencing note, the tests guide, and the sample lifecycle/selftest surface."
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
            print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_ERROR={failure}")
        return 1

    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SEQUENCING_MARKER_COUNT={len(SEQUENCING_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_PACKET_SAMPLE_MARKER_COUNT={len(SAMPLE_REQUIRED_MARKERS)}")
    print("PHASE9_TRACE_EVENTS_RUNTIME_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

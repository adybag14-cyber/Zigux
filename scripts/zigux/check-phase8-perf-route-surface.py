#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/Makefile").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE_PATH = "zigux/Makefile"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
PERF_BUILD_PATH = "zigux/tests/phase8_perf_buffer_poll_only_build.zig"
SHARED_BUILD_PATH = "zigux/tests/phase8_build.zig"

WORKFLOW_REQUIRED_MARKERS = [
    "Validate Phase 8 tooling routes",
    "make -C zigux phase8-validate",
    "Run focused Phase 8 exec-cmd tests",
    "Run focused Phase 8 libbpf segment tests",
    "Run Phase 8 tooling tests",
    "make -C zigux phase8-test",
]

MAKEFILE_REQUIRED_MARKERS = [
    "phase8-validate:",
    "phase8-exec-cmd-test:",
    "phase8-libbpf-segments-test:",
    "phase8-perf-buffer-poll-test:",
    "phase8-test:",
    "phase8: phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-file-path-handle-bridge-test phase8-libbpf-segments-test phase8-perf-buffer-poll-test phase8-test",
]

SCRIPTS_README_REQUIRED_MARKERS = [
    "Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit beside the surviving perf-buffer poll packet and the mixed-source file-path-handle bridge packet",
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/check-phase8-tests-readme-alignment.py`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` keep the directly readable checker, validator, tests-root reminder, helper, and focused perf-buffer packet explicit from the scripts root",
    "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the mixed-source file-path-handle bridge packet explicit on current `master` beside the surviving perf-buffer poll route",
]

TESTS_README_REQUIRED_MARKERS = [
    "current direct-readback Phase 8 anchors:",
    "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
    "`make -C zigux phase8-perf-buffer-poll-test`",
    "`make -C zigux phase8-test`",
]

PERF_BUILD_REQUIRED_MARKERS = [
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
    "../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
    "phase8-ready-buffer-fd-lookup-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig",
    "phase8-perf-buffer-poll-verify-tests",
    'const test_step = b.step("test", "Run focused Phase 8 perf-buffer poll tests");',
    "test_step.dependOn(&run_perf_buffer_poll_tests.step);",
    "test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);",
    "test_step.dependOn(&run_perf_buffer_poll_verify_tests.step);",
]

SHARED_BUILD_REQUIRED_MARKERS = [
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig",
    "phase8-perf-buffer-poll-verify-tests",
    "../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
    "phase8-ready-buffer-fd-lookup-tests",
    'const test_step = b.step("test", "Run the shared Phase 8 tooling tests.");',
    "test_step.dependOn(&run_perf_buffer_poll_tests.step);",
    "test_step.dependOn(&run_perf_buffer_poll_verify_tests.step);",
    "test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);",
]

REQUIRED_FILES = (
    WORKFLOW_PATH,
    MAKEFILE_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    PERF_BUILD_PATH,
    SHARED_BUILD_PATH,
)

MARKER_GROUPS = (
    (WORKFLOW_PATH, WORKFLOW_REQUIRED_MARKERS),
    (MAKEFILE_PATH, MAKEFILE_REQUIRED_MARKERS),
    (SCRIPTS_README_PATH, SCRIPTS_README_REQUIRED_MARKERS),
    (TESTS_README_PATH, TESTS_README_REQUIRED_MARKERS),
    (PERF_BUILD_PATH, PERF_BUILD_REQUIRED_MARKERS),
    (SHARED_BUILD_PATH, SHARED_BUILD_REQUIRED_MARKERS),
)


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in MARKER_GROUPS:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def build_fixture_root(root: Path) -> None:
    for rel_path, markers in MARKER_GROUPS:
        write_text(root, rel_path, "\n".join(markers) + "\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    case_count = 1
    with tempfile.TemporaryDirectory(prefix="phase8-perf-route-surface-") as tmp:
        base = Path(tmp)
        build_fixture_root(base)

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in MARKER_GROUPS:
            baseline = "\n".join(markers) + "\n"
            for marker in markers:
                write_text(base, rel_path, baseline.replace(marker, ""))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")
                write_text(base, rel_path, baseline)
                case_count += 1

        for rel_path in REQUIRED_FILES:
            path = base / rel_path
            original = path.read_text(encoding="utf-8")
            path.unlink()
            expect_failure(base, f"missing_file:{rel_path}")
            write_text(base, rel_path, original)
            case_count += 1

    print("PHASE8_PERF_ROUTE_SURFACE_SELF_TEST=pass")
    print(f"PHASE8_PERF_ROUTE_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    print(f"PHASE8_PERF_ROUTE_SURFACE_WORKFLOW_MARKER_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    print(f"PHASE8_PERF_ROUTE_SURFACE_MAKEFILE_MARKER_COUNT={len(MAKEFILE_REQUIRED_MARKERS)}")
    print(
        f"PHASE8_PERF_ROUTE_SURFACE_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}"
    )
    print(
        f"PHASE8_PERF_ROUTE_SURFACE_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}"
    )
    print(f"PHASE8_PERF_ROUTE_SURFACE_FOCUSED_BUILD_MARKER_COUNT={len(PERF_BUILD_REQUIRED_MARKERS)}")
    print(f"PHASE8_PERF_ROUTE_SURFACE_SHARED_BUILD_MARKER_COUNT={len(SHARED_BUILD_REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 8 perf-buffer rerun surface stays aligned "
            "across the bootstrap workflow, the make wrappers, the scripts/tests reminder "
            "surfaces, the focused perf-buffer replay, and the shared aggregate build."
        )
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
            print(f"PHASE8_PERF_ROUTE_SURFACE_ERROR={failure}")
        return 1

    print(f"PHASE8_PERF_ROUTE_SURFACE_WORKFLOW_MARKER_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    print(f"PHASE8_PERF_ROUTE_SURFACE_MAKEFILE_MARKER_COUNT={len(MAKEFILE_REQUIRED_MARKERS)}")
    print(
        f"PHASE8_PERF_ROUTE_SURFACE_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}"
    )
    print(
        f"PHASE8_PERF_ROUTE_SURFACE_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}"
    )
    print(f"PHASE8_PERF_ROUTE_SURFACE_FOCUSED_BUILD_MARKER_COUNT={len(PERF_BUILD_REQUIRED_MARKERS)}")
    print(f"PHASE8_PERF_ROUTE_SURFACE_SHARED_BUILD_MARKER_COUNT={len(SHARED_BUILD_REQUIRED_MARKERS)}")
    print("PHASE8_PERF_ROUTE_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

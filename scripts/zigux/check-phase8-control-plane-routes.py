#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "scripts/zigux/validate-phase8.py").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
PHASE8_TEST_PATH = "zigux/tests/phase8_perf_buffer_poll.zig"

WORKFLOW_REQUIRED_MARKERS = [
    "Validate Phase 8 tooling gates",
    "make -C zigux phase8-validate",
    "Run focused Phase 8 libbpf segment survey tests",
    "zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all",
]

VALIDATOR_REQUIRED_MARKERS = [
    'MAKEFILE_PATH = "zigux/Makefile"',
    'VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"',
    'PERF_BUFFER_POLL_GATE_PATH = "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"',
    'LIBBPF_SEGMENT_GATE_PATH = "scripts/zigux/check-phase8-libbpf-segment-gate.py"',
    'LIBBPF_SHARD_ROUTES_PATH = "scripts/zigux/check-phase8-libbpf-shard-routes.py"',
    'LIBBPF_SEGMENT_SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"',
    'BRIDGE_SLICE_PATH = "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"',
    'BRIDGE_BUILD_PATH = "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"',
    'PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"',
]

PHASE8_TEST_REQUIRED_MARKERS = [
    '"Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"',
    '"zigux/tests/phase8_perf_buffer_poll_only_build.zig"',
    '"python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py"',
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in (WORKFLOW_PATH, VALIDATOR_PATH, PHASE8_TEST_PATH):
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    workflow = read_text(root, WORKFLOW_PATH)
    for marker in WORKFLOW_REQUIRED_MARKERS:
        if marker not in workflow:
            failures.append(f"missing_marker:{WORKFLOW_PATH}:{marker}")

    validator = read_text(root, VALIDATOR_PATH)
    for marker in VALIDATOR_REQUIRED_MARKERS:
        if marker not in validator:
            failures.append(f"missing_marker:{VALIDATOR_PATH}:{marker}")

    phase8_test = read_text(root, PHASE8_TEST_PATH)
    for marker in PHASE8_TEST_REQUIRED_MARKERS:
        if marker not in phase8_test:
            failures.append(f"missing_marker:{PHASE8_TEST_PATH}:{marker}")

    return failures


def build_workflow_fixture() -> str:
    return """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Validate Phase 8 tooling gates
        run: make -C zigux phase8-validate
      - name: Run focused Phase 8 libbpf segment survey tests
        run: zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all
"""


def build_validator_fixture() -> str:
    return """MAKEFILE_PATH = "zigux/Makefile"
VALIDATOR_PATH = "scripts/zigux/validate-phase8.py"
PERF_BUFFER_POLL_GATE_PATH = "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"
LIBBPF_SEGMENT_GATE_PATH = "scripts/zigux/check-phase8-libbpf-segment-gate.py"
LIBBPF_SHARD_ROUTES_PATH = "scripts/zigux/check-phase8-libbpf-shard-routes.py"
LIBBPF_SEGMENT_SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
BRIDGE_SLICE_PATH = "Documentation/zigux/phase8-file-path-handle-bridge-slice.md"
BRIDGE_BUILD_PATH = "zigux/tests/phase8_file_path_handle_bridge_only_build.zig"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"
"""


def build_phase8_test_fixture() -> str:
    return """test "phase 8 perf-buffer poll bridge survey keeps the bounded helper packet explicit" {
    _ = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md";
    _ = "zigux/tests/phase8_perf_buffer_poll_only_build.zig";
    _ = "python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py";
}
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase8-control-plane-routes-"))
    try:
        write_text(base, WORKFLOW_PATH, build_workflow_fixture())
        write_text(base, VALIDATOR_PATH, build_validator_fixture())
        write_text(base, PHASE8_TEST_PATH, build_phase8_test_fixture())

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in WORKFLOW_REQUIRED_MARKERS:
            write_text(base, WORKFLOW_PATH, build_workflow_fixture().replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{WORKFLOW_PATH}:{marker}")
            write_text(base, WORKFLOW_PATH, build_workflow_fixture())

        for marker in VALIDATOR_REQUIRED_MARKERS:
            write_text(base, VALIDATOR_PATH, build_validator_fixture().replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{VALIDATOR_PATH}:{marker}")
            write_text(base, VALIDATOR_PATH, build_validator_fixture())

        for marker in PHASE8_TEST_REQUIRED_MARKERS:
            write_text(base, PHASE8_TEST_PATH, build_phase8_test_fixture().replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{PHASE8_TEST_PATH}:{marker}")
            write_text(base, PHASE8_TEST_PATH, build_phase8_test_fixture())

        shutil.rmtree(base / ".github", ignore_errors=True)
        expect_failure(base, f"missing_file:{WORKFLOW_PATH}")
        write_text(base, WORKFLOW_PATH, build_workflow_fixture())

        shutil.rmtree(base / "scripts", ignore_errors=True)
        expect_failure(base, f"missing_file:{VALIDATOR_PATH}")
        write_text(base, VALIDATOR_PATH, build_validator_fixture())

        shutil.rmtree(base / "zigux/tests", ignore_errors=True)
        expect_failure(base, f"missing_file:{PHASE8_TEST_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE8_CONTROL_PLANE_ROUTES_SELF_TEST=pass")
    print(f"PHASE8_CONTROL_PLANE_ROUTES_WORKFLOW_MARKER_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    print(f"PHASE8_CONTROL_PLANE_ROUTES_VALIDATOR_MARKER_COUNT={len(VALIDATOR_REQUIRED_MARKERS)}")
    print(f"PHASE8_CONTROL_PLANE_ROUTES_TEST_MARKER_COUNT={len(PHASE8_TEST_REQUIRED_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the live Phase 8 control-plane bundle keeps the validator, "
            "workflow, and focused perf-buffer poll replay routes aligned."
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
            print(f"PHASE8_CONTROL_PLANE_ROUTES_ERROR={failure}")
        return 1

    print(f"PHASE8_CONTROL_PLANE_ROUTES_WORKFLOW_MARKER_COUNT={len(WORKFLOW_REQUIRED_MARKERS)}")
    print(f"PHASE8_CONTROL_PLANE_ROUTES_VALIDATOR_MARKER_COUNT={len(VALIDATOR_REQUIRED_MARKERS)}")
    print(f"PHASE8_CONTROL_PLANE_ROUTES_TEST_MARKER_COUNT={len(PHASE8_TEST_REQUIRED_MARKERS)}")
    print("PHASE8_CONTROL_PLANE_ROUTES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

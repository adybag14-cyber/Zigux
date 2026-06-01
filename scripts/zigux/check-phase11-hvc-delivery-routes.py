#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 HVC shared-versus-dedicated delivery routes."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[2]

MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
BUILD_PATH = Path("zigux/tests/phase11_build.zig")
CONTRACT_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")

REQUIRED_MAKEFILE_MARKERS = (
    "phase11-contract:",
    "phase11-test:",
    "phase11-hvc-survey:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all",
    "phase11: phase11-contract phase11-test phase11-hvc-survey",
)

REQUIRED_BUILD_MARKERS = (
    'const test_step = b.step("test", "Run the shared Phase 11 starter packet");',
    "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);",
    "test_step.dependOn(&run_phase11_hvc_console_tests.step);",
    "test_step.dependOn(&run_hvc_console_verify_tests.step);",
    "test_step.dependOn(&run_phase11_hvc_cleanup_tests.step);",
    'const hvc_console_survey_step = b.step("hvc-console-survey", "Run the dedicated Phase 11 hvc_console archival survey");',
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
)

REQUIRED_SHARED_DOC_MARKERS = (
    "make -C zigux phase11-hvc-survey",
    "make -C zigux phase11",
    "zig build test --build-file zigux/tests/phase11_build.zig --summary all",
)

REQUIRED_DEDICATED_DOC_MARKERS = (
    "make -C zigux phase11-hvc-survey",
    "scripts/zigux/check-phase11-hvc-survey-packet.py",
    ".github/workflows/zigux-bootstrap.yml",
)

REQUIRED_WORKFLOW_SHARED_MARKERS = (
    "run: make -C zigux phase11-contract",
    "run: make -C zigux phase11-test",
)

WORKFLOW_DEDICATED_MARKERS = (
    "run: make -C zigux phase11-hvc-survey",
    "run: make -C zigux phase11",
)


@dataclass(frozen=True)
class PacketFiles:
    makefile: Path = MAKEFILE_PATH
    workflow: Path = WORKFLOW_PATH
    build: Path = BUILD_PATH
    contract: Path = CONTRACT_PATH
    matrix: Path = MATRIX_PATH
    scripts_readme: Path = SCRIPTS_README_PATH
    tests_readme: Path = TESTS_README_PATH


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise AssertionError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise AssertionError(f"{label} is missing required markers: {missing}")


def require_workflow_delivery_route(text: str) -> None:
    require_markers("workflow", text, REQUIRED_WORKFLOW_SHARED_MARKERS)
    workflow_lines = {line.strip() for line in text.splitlines()}
    if not any(marker in workflow_lines for marker in WORKFLOW_DEDICATED_MARKERS):
        raise AssertionError(
            "workflow is missing the dedicated Phase 11 HVC delivery route; "
            "expected either `make -C zigux phase11-hvc-survey` or `make -C zigux phase11`"
        )


def check_packet(root: Path) -> None:
    files = PacketFiles()
    makefile = read_text(root, files.makefile)
    workflow = read_text(root, files.workflow)
    build = read_text(root, files.build)
    contract = read_text(root, files.contract)
    matrix = read_text(root, files.matrix)
    scripts_readme = read_text(root, files.scripts_readme)
    tests_readme = read_text(root, files.tests_readme)

    require_markers("makefile", makefile, REQUIRED_MAKEFILE_MARKERS)
    require_markers("phase11_build", build, REQUIRED_BUILD_MARKERS)
    require_markers("shared replay contract", contract, REQUIRED_SHARED_DOC_MARKERS)
    require_markers("validation matrix", matrix, REQUIRED_DEDICATED_DOC_MARKERS)
    require_markers("scripts README", scripts_readme, REQUIRED_SHARED_DOC_MARKERS)
    require_markers("tests README", tests_readme, REQUIRED_DEDICATED_DOC_MARKERS)
    require_workflow_delivery_route(workflow)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_self_test() -> None:
    passing_workflow = """jobs:\n  bootstrap:\n    steps:\n      - name: Validate Phase 11 shared routes\n        run: make -C zigux phase11-contract\n      - name: Run Phase 11 shared tests\n        run: make -C zigux phase11-test\n      - name: Run Phase 11 dedicated hvc survey\n        run: make -C zigux phase11-hvc-survey\n"""
    missing_dedicated_workflow = """jobs:\n  bootstrap:\n    steps:\n      - name: Validate Phase 11 shared routes\n        run: make -C zigux phase11-contract\n      - name: Run Phase 11 shared tests\n        run: make -C zigux phase11-test\n"""
    passing_makefile = """phase11-contract:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py --self-test\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py\nphase11-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_build.zig --summary all\nphase11-hvc-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all\nphase11: phase11-contract phase11-test phase11-hvc-survey\n"""
    passing_build = """const test_step = b.step(\"test\", \"Run the shared Phase 11 starter packet\");\ntest_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);\ntest_step.dependOn(&run_phase11_hvc_console_tests.step);\ntest_step.dependOn(&run_hvc_console_verify_tests.step);\ntest_step.dependOn(&run_phase11_hvc_cleanup_tests.step);\nconst hvc_console_survey_step = b.step(\"hvc-console-survey\", \"Run the dedicated Phase 11 hvc_console archival survey\");\nhvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);\n"""
    passing_shared_doc = """make -C zigux phase11\nmake -C zigux phase11-hvc-survey\nzig build test --build-file zigux/tests/phase11_build.zig --summary all\nscripts/zigux/check-phase11-hvc-survey-packet.py\n.github/workflows/zigux-bootstrap.yml\n"""
    missing_matrix_marker = """make -C zigux phase11-hvc-survey\nscripts/zigux/check-phase11-hvc-survey-packet.py\n"""

    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        write(root / MAKEFILE_PATH, passing_makefile)
        write(root / WORKFLOW_PATH, passing_workflow)
        write(root / BUILD_PATH, passing_build)
        write(root / CONTRACT_PATH, passing_shared_doc)
        write(root / MATRIX_PATH, passing_shared_doc)
        write(root / SCRIPTS_README_PATH, passing_shared_doc)
        write(root / TESTS_README_PATH, passing_shared_doc)

        check_packet(root)

        write(root / WORKFLOW_PATH, missing_dedicated_workflow)
        try:
            check_packet(root)
        except AssertionError as exc:
            if "workflow is missing the dedicated Phase 11 HVC delivery route" not in str(exc):
                raise
        else:
            raise AssertionError("missing dedicated workflow route should fail")

        write(root / WORKFLOW_PATH, passing_workflow)
        write(root / MATRIX_PATH, missing_matrix_marker)
        try:
            check_packet(root)
        except AssertionError as exc:
            if "validation matrix is missing required markers" not in str(exc):
                raise
        else:
            raise AssertionError("missing validation-matrix markers should fail")

    print("PHASE11_HVC_DELIVERY_ROUTES_SELF_TEST=pass")
    print("PHASE11_HVC_DELIVERY_ROUTES_SELF_TEST_CASES=3")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        check_packet(args.root)
    except AssertionError as exc:
        print(f"PHASE11_HVC_DELIVERY_ROUTES=fail: {exc}", file=sys.stderr)
        return 1

    print("PHASE11_HVC_DELIVERY_ROUTES=pass")
    print("PHASE11_HVC_DELIVERY_ROUTE_FILES=7")
    print("PHASE11_HVC_SHARED_COMMANDS=2")
    print("PHASE11_HVC_DEDICATED_COMMANDS=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

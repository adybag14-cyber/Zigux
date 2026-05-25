#!/usr/bin/env python3
"""Fail closed if the Phase 11 workflow packet drifts."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase11.py")
TARGET_NAME = "phase11-validate"

SELFTEST_STEP_NAME = "Self-test current Phase 11 workflow route checker"
SELFTEST_STEP_RUN = "python3 scripts/zigux/check-phase11-workflow-route-counts.py --self-test"
CHECK_STEP_NAME = "Check current Phase 11 workflow route packet"
CHECK_STEP_RUN = "python3 scripts/zigux/check-phase11-workflow-route-counts.py"
VALIDATE_STEP_NAME = "Validate current Phase 11 support bundle"
VALIDATE_STEP_RUN = "make -C zigux phase11-validate"

FORBIDDEN_RUN_LINES = (
    "run: make -C zigux phase11",
    "run: make -C zigux phase11-contract",
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def find_exact_line_index(lines: list[str], marker: str) -> int:
    indexes = [index for index, line in enumerate(lines) if line.strip() == marker]
    if not indexes:
        raise CheckError(f"missing workflow line: {marker}")
    if len(indexes) != 1:
        raise CheckError(f"workflow line must appear exactly once: {marker}")
    return indexes[0]


def extract_makefile_recipe(makefile_path: Path, target_name: str) -> list[str]:
    lines = read_text(makefile_path).splitlines()
    for index, line in enumerate(lines):
        if line.startswith(f"{target_name}:"):
            recipe: list[str] = []
            cursor = index + 1
            while cursor < len(lines):
                current = lines[cursor]
                if current.startswith("\t"):
                    recipe.append(current.strip())
                    cursor += 1
                    continue
                if not current.strip():
                    cursor += 1
                    continue
                break
            if not recipe:
                raise CheckError(f"target {target_name} has no recipe")
            return recipe
    raise CheckError(f"missing target: {target_name}")


def run_check(root: Path) -> tuple[int, int]:
    workflow_text = read_text(root / WORKFLOW_PATH)
    workflow_lines = workflow_text.splitlines()

    for marker in (
        f"- name: {SELFTEST_STEP_NAME}",
        f"run: {SELFTEST_STEP_RUN}",
        f"- name: {CHECK_STEP_NAME}",
        f"run: {CHECK_STEP_RUN}",
        f"- name: {VALIDATE_STEP_NAME}",
        f"run: {VALIDATE_STEP_RUN}",
    ):
        if count_exact_lines(workflow_text, marker) != 1:
            raise CheckError(f"workflow line must appear exactly once: {marker}")

    selftest_name_index = find_exact_line_index(workflow_lines, f"- name: {SELFTEST_STEP_NAME}")
    selftest_run_index = find_exact_line_index(workflow_lines, f"run: {SELFTEST_STEP_RUN}")
    check_name_index = find_exact_line_index(workflow_lines, f"- name: {CHECK_STEP_NAME}")
    check_run_index = find_exact_line_index(workflow_lines, f"run: {CHECK_STEP_RUN}")
    validate_name_index = find_exact_line_index(workflow_lines, f"- name: {VALIDATE_STEP_NAME}")
    validate_run_index = find_exact_line_index(workflow_lines, f"run: {VALIDATE_STEP_RUN}")

    if not (selftest_name_index < selftest_run_index < check_name_index < check_run_index < validate_name_index < validate_run_index):
        raise CheckError("workflow Phase 11 route packet is out of order")

    for marker in FORBIDDEN_RUN_LINES:
        if count_exact_lines(workflow_text, marker) != 0:
            raise CheckError(f"forbidden workflow route present: {marker}")

    recipe = extract_makefile_recipe(root / MAKEFILE_PATH, TARGET_NAME)
    if not any(VALIDATOR_PATH.as_posix() in line for line in recipe):
        raise CheckError(f"{TARGET_NAME} must call {VALIDATOR_PATH.as_posix()}")

    return len(recipe), 6


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, workflow_text: str | None = None, makefile_text: str | None = None) -> None:
    write(
        root / WORKFLOW_PATH,
        workflow_text
        or "\n".join(
            [
                "name: zigux-bootstrap",
                "",
                "jobs:",
                "  bootstrap:",
                "    runs-on: ubuntu-latest",
                "    steps:",
                f"      - name: {SELFTEST_STEP_NAME}",
                f"        run: {SELFTEST_STEP_RUN}",
                f"      - name: {CHECK_STEP_NAME}",
                f"        run: {CHECK_STEP_RUN}",
                f"      - name: {VALIDATE_STEP_NAME}",
                f"        run: {VALIDATE_STEP_RUN}",
                "",
            ]
        ),
    )
    write(
        root / MAKEFILE_PATH,
        makefile_text
        or "\n".join(
            [
                "phase11-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
                "",
            ]
        ),
    )
    write(root / VALIDATOR_PATH, "CHECKS = ()\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase11_workflow_route_counts_"))
    try:
        passing = tempdir / "passing"
        build_fixture(passing)
        recipe_count, workflow_marker_count = run_check(passing)
        case_count = 1

        missing_selftest = tempdir / "missing_selftest"
        build_fixture(
            missing_selftest,
            workflow_text="\n".join(
                [
                    "name: zigux-bootstrap",
                    "jobs:",
                    "  bootstrap:",
                    "    runs-on: ubuntu-latest",
                    "    steps:",
                    f"      - name: {CHECK_STEP_NAME}",
                    f"        run: {CHECK_STEP_RUN}",
                    f"      - name: {VALIDATE_STEP_NAME}",
                    f"        run: {VALIDATE_STEP_RUN}",
                    "",
                ]
            ),
        )
        expect_failure(missing_selftest, SELFTEST_STEP_NAME)
        case_count += 1

        duplicate_validate = tempdir / "duplicate_validate"
        build_fixture(
            duplicate_validate,
            workflow_text="\n".join(
                [
                    "name: zigux-bootstrap",
                    "jobs:",
                    "  bootstrap:",
                    "    runs-on: ubuntu-latest",
                    "    steps:",
                    f"      - name: {SELFTEST_STEP_NAME}",
                    f"        run: {SELFTEST_STEP_RUN}",
                    f"      - name: {CHECK_STEP_NAME}",
                    f"        run: {CHECK_STEP_RUN}",
                    f"      - name: {VALIDATE_STEP_NAME}",
                    f"        run: {VALIDATE_STEP_RUN}",
                    f"      - name: {VALIDATE_STEP_NAME}",
                    f"        run: {VALIDATE_STEP_RUN}",
                    "",
                ]
            ),
        )
        expect_failure(duplicate_validate, VALIDATE_STEP_NAME)
        case_count += 1

        wrong_order = tempdir / "wrong_order"
        build_fixture(
            wrong_order,
            workflow_text="\n".join(
                [
                    "name: zigux-bootstrap",
                    "jobs:",
                    "  bootstrap:",
                    "    runs-on: ubuntu-latest",
                    "    steps:",
                    f"      - name: {CHECK_STEP_NAME}",
                    f"        run: {CHECK_STEP_RUN}",
                    f"      - name: {SELFTEST_STEP_NAME}",
                    f"        run: {SELFTEST_STEP_RUN}",
                    f"      - name: {VALIDATE_STEP_NAME}",
                    f"        run: {VALIDATE_STEP_RUN}",
                    "",
                ]
            ),
        )
        expect_failure(wrong_order, "out of order")
        case_count += 1

        forbidden_route = tempdir / "forbidden_route"
        build_fixture(
            forbidden_route,
            workflow_text="\n".join(
                [
                    "name: zigux-bootstrap",
                    "jobs:",
                    "  bootstrap:",
                    "    runs-on: ubuntu-latest",
                    "    steps:",
                    f"      - name: {SELFTEST_STEP_NAME}",
                    f"        run: {SELFTEST_STEP_RUN}",
                    f"      - name: {CHECK_STEP_NAME}",
                    f"        run: {CHECK_STEP_RUN}",
                    f"      - name: legacy",
                    "        run: make -C zigux phase11",
                    f"      - name: {VALIDATE_STEP_NAME}",
                    f"        run: {VALIDATE_STEP_RUN}",
                    "",
                ]
            ),
        )
        expect_failure(forbidden_route, "forbidden workflow route present")
        case_count += 1

        missing_target = tempdir / "missing_target"
        build_fixture(missing_target, makefile_text="phase10-validate:\n\ttrue\n")
        expect_failure(missing_target, "missing target: phase11-validate")
        case_count += 1

        missing_validator = tempdir / "missing_validator"
        build_fixture(
            missing_validator,
            makefile_text="\n".join(
                [
                    "phase11-validate:",
                    "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
                    "",
                ]
            ),
        )
        expect_failure(missing_validator, "must call scripts/zigux/validate-phase11.py")
        case_count += 1

        print("PHASE11_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass")
        print(f"PHASE11_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT={case_count}")
        print(f"PHASE11_WORKFLOW_ROUTE_COUNTS_RECIPE_LINE_COUNT={recipe_count}")
        print(f"PHASE11_WORKFLOW_ROUTE_COUNTS_MARKER_COUNT={workflow_marker_count}")
        return 0
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        recipe_count, workflow_marker_count = run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_WORKFLOW_ROUTE_COUNTS=fail: {exc}")
        return 1

    print("PHASE11_WORKFLOW_ROUTE_COUNTS=pass")
    print(f"PHASE11_WORKFLOW_ROUTE_COUNTS_RECIPE_LINE_COUNT={recipe_count}")
    print(f"PHASE11_WORKFLOW_ROUTE_COUNTS_MARKER_COUNT={workflow_marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

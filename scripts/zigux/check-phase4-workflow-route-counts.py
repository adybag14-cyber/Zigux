#!/usr/bin/env python3
"""Fail closed on the shipped Phase 4 workflow-route packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
import textwrap
from pathlib import Path


SCRIPT_PATH = Path("scripts/zigux/check-phase4-workflow-route-counts.py")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

WORKFLOW_REQUIRED_ROUTES = (
    "run: make -C zigux phase4-validate",
    "run: python3 scripts/zigux/validate-phase4.py --self-test",
    "run: python3 scripts/zigux/validate-phase4.py",
    "run: zig build test --build-file zigux/tests/phase4_build.zig",
)

MAKEFILE_REQUIRED_MARKERS = (
    "phase4-validate:",
    "$(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py",
)

SCRIPTS_README_REQUIRED_MARKERS = (
    "`check-phase4-workflow-route-counts.py`",
    "`scripts/zigux/check-phase4-workflow-route-counts.py`",
)

SELF_TEST_CASES = (
    "baseline_round_trip",
    "missing_workflow_route_marker",
    "unexpected_extra_workflow_route_marker",
    "missing_makefile_checker_marker",
    "missing_scripts_readme_marker",
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path.as_posix()}")
    return path.read_text(encoding="utf-8")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def require_line_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    lines = {line.strip() for line in text.splitlines()}
    for marker in markers:
        if marker not in lines:
            raise CheckError(f"missing {label} marker: {marker}")


def count_phase4_workflow_routes(workflow_text: str) -> int:
    workflow_lines = [
        line.strip()
        for line in workflow_text.splitlines()
        if line.strip().startswith("run:")
    ]
    return sum(1 for line in workflow_lines if line in WORKFLOW_REQUIRED_ROUTES)


def validate_repo(root: Path) -> None:
    workflow_text = read_text(root, WORKFLOW_PATH)
    makefile_text = read_text(root, MAKEFILE_PATH)
    scripts_readme_text = read_text(root, SCRIPTS_README_PATH)

    require_line_markers(workflow_text, WORKFLOW_REQUIRED_ROUTES, "workflow route")
    route_count = count_phase4_workflow_routes(workflow_text)
    expected_route_count = len(WORKFLOW_REQUIRED_ROUTES)
    if route_count != expected_route_count:
        raise CheckError(
            "unexpected Phase 4 workflow route count: "
            f"expected {expected_route_count}, found {route_count}"
        )

    require_markers(makefile_text, MAKEFILE_REQUIRED_MARKERS, "Makefile")
    require_markers(
        scripts_readme_text,
        SCRIPTS_README_REQUIRED_MARKERS,
        "scripts README",
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def build_self_test_repo(root: Path) -> None:
    write(
        root / WORKFLOW_PATH,
        """
        name: zigux-bootstrap
        jobs:
          bootstrap:
            steps:
              - name: Validate Phase 4 diff gates
                run: make -C zigux phase4-validate
              - name: Self-test Phase 4 validator directly
                run: python3 scripts/zigux/validate-phase4.py --self-test
              - name: Validate Phase 4 diff packet directly
                run: python3 scripts/zigux/validate-phase4.py
              - name: Run Phase 4 diff tests directly
                run: zig build test --build-file zigux/tests/phase4_build.zig
        """,
    )
    write(
        root / MAKEFILE_PATH,
        """
        phase4-validate:
        	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test
        	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py
        	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase4-workflow-route-counts.py
        """,
    )
    write(
        root / SCRIPTS_README_PATH,
        """
        - `check-phase4-workflow-route-counts.py`

        Phase 4 flow
        - `make -C zigux phase4-validate` reruns `scripts/zigux/check-phase4-workflow-route-counts.py`
        """,
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        validate_repo(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise CheckError(
                f"expected self-test failure containing {expected_fragment!r}, got: {exc}"
            ) from exc
        return
    raise CheckError("expected self-test mutation to fail closed")


def run_self_test() -> None:
    tempdir = Path(tempfile.mkdtemp(prefix="phase4-workflow-route-counts-"))
    try:
        build_self_test_repo(tempdir)
        validate_repo(tempdir)

        missing_workflow = tempdir / "missing-workflow"
        shutil.copytree(tempdir, missing_workflow)
        write(
            missing_workflow / WORKFLOW_PATH,
            """
            name: zigux-bootstrap
            jobs:
              bootstrap:
                steps:
                  - name: Validate Phase 4 diff gates
                    run: make -C zigux phase4-validate
                  - name: Self-test Phase 4 validator directly
                    run: python3 scripts/zigux/validate-phase4.py --self-test
                  - name: Run Phase 4 diff tests directly
                    run: zig build test --build-file zigux/tests/phase4_build.zig
            """,
        )
        expect_failure(missing_workflow, "missing workflow route marker")

        extra_workflow = tempdir / "extra-workflow"
        shutil.copytree(tempdir, extra_workflow)
        write(
            extra_workflow / WORKFLOW_PATH,
            """
            name: zigux-bootstrap
            jobs:
              bootstrap:
                steps:
                  - name: Validate Phase 4 diff gates
                    run: make -C zigux phase4-validate
                  - name: Self-test Phase 4 validator directly
                    run: python3 scripts/zigux/validate-phase4.py --self-test
                  - name: Validate Phase 4 diff packet directly
                    run: python3 scripts/zigux/validate-phase4.py
                  - name: Run Phase 4 diff tests directly
                    run: zig build test --build-file zigux/tests/phase4_build.zig
                  - name: Duplicate Phase 4 diff tests directly
                    run: zig build test --build-file zigux/tests/phase4_build.zig
            """,
        )
        expect_failure(extra_workflow, "unexpected Phase 4 workflow route count")

        missing_makefile = tempdir / "missing-makefile"
        shutil.copytree(tempdir, missing_makefile)
        write(
            missing_makefile / MAKEFILE_PATH,
            """
            phase4-validate:
            	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py --self-test
            	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase4.py
            """,
        )
        expect_failure(missing_makefile, "missing Makefile marker")

        missing_scripts_readme = tempdir / "missing-scripts-readme"
        shutil.copytree(tempdir, missing_scripts_readme)
        write(
            missing_scripts_readme / SCRIPTS_README_PATH,
            """
            Phase 4 flow
            - `make -C zigux phase4-validate` reruns the validator-first packet
            """,
        )
        expect_failure(missing_scripts_readme, "missing scripts README marker")

        print("PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST=pass")
        print(f"PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")
        print(
            "PHASE4_WORKFLOW_ROUTE_COUNTS_SELF_TEST_CASES="
            + ",".join(SELF_TEST_CASES)
        )
    finally:
        shutil.rmtree(tempdir)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    validate_repo(Path.cwd())
    print("PHASE4_WORKFLOW_ROUTE_COUNTS_CHECK=pass")
    print(f"PHASE4_WORKFLOW_REQUIRED_ROUTE_COUNT={len(WORKFLOW_REQUIRED_ROUTES)}")
    print(
        f"PHASE4_WORKFLOW_PHASE4_ROUTE_COUNT={len(WORKFLOW_REQUIRED_ROUTES)}"
    )
    print("PHASE4_WORKFLOW_VALIDATE_ROUTE_CHECKER_PRESENT=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=shared_smoke_route

Fail-closed checker for the bounded Phase 14 shared smoke route.

This guard exists for the lane-local executable path only. It validates that
 the current repo exposes a dedicated `phase14-validate` Makefile route, that
 the route reruns the shared smoke route checker plus the current tests-root
 smoke-summary checker, validator, and release-boundary checker packets, and
 that the bootstrap workflow reruns that same route, without claiming that the
 missing `phase14-smoke`, `phase14-test`, or full bundle wrappers have
 returned.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=shared_smoke_route"
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

MAKEFILE_MARKERS = [
    ".PHONY:",
    "phase14-validate",
    "phase14-validate:",
    "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "scripts/zigux/check-phase14-shared-smoke-route.py",
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
    "scripts/zigux/validate-phase14.py --self-test",
    "scripts/zigux/validate-phase14.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
]

WORKFLOW_MARKERS = [
    "- name: Self-test current Phase 14 shared smoke route checker",
    "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "- name: Run current Phase 14 validate route",
    "run: make -C zigux phase14-validate",
]

FORBIDDEN_WORKFLOW_MARKERS = [
    "run: make -C zigux phase14-smoke",
    "run: make -C zigux phase14-test",
]


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden_marker:{rel.as_posix()}:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in [MAKEFILE_PATH, WORKFLOW_PATH]:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)

    require_markers(errors, MAKEFILE_PATH, makefile, MAKEFILE_MARKERS)
    require_markers(errors, WORKFLOW_PATH, workflow, WORKFLOW_MARKERS)
    require_absent(errors, WORKFLOW_PATH, workflow, FORBIDDEN_WORKFLOW_MARKERS)
    return errors


def fixture_makefile() -> str:
    return """PYTHON ?= python3
ZIGUX_ROOT := ..

.PHONY: phase12-smoke phase12-test phase12 phase14-validate

phase12-smoke:
\tcd $(ZIGUX_ROOT) && zig build smoke --build-file zigux/tests/phase12_build.zig --summary all

phase12-test:
\tcd $(ZIGUX_ROOT) && zig build test --build-file zigux/tests/phase12_build.zig --summary all

phase12: phase12-smoke phase12-test

phase14-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
"""


def fixture_workflow() -> str:
    return """name: zigux-bootstrap
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 14 shared smoke route checker
        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
      - name: Run current Phase 14 validate route
        run: make -C zigux phase14-validate
"""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(root, WORKFLOW_PATH, fixture_workflow())


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-shared-smoke-route-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write_fixture_tree(base)
        write_text(base, MAKEFILE_PATH, fixture_makefile().replace("phase14-validate:", "phase14-validate-missing:", 1))
        if not any("phase14-validate:" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected missing target marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            MAKEFILE_PATH,
            fixture_makefile().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py\n",
                "",
                1,
            ),
        )
        if not any("check-phase14-tests-readme-smoke-summary.py --self-test" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected tests-readme checker marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            WORKFLOW_PATH,
            fixture_workflow() + "      - name: Wrong smoke route\n        run: make -C zigux phase14-smoke\n",
        )
        if not any("phase14-smoke" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected forbidden workflow smoke wrapper failure")
            return 1

        print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass")
        print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST_CASE_COUNT=3")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_SHARED_SMOKE_ROUTE=fail")
        print("PHASE14_SHARED_SMOKE_ROUTE_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_SHARED_SMOKE_ROUTE_ISSUES_END")
        return 1

    print("PHASE14_SHARED_SMOKE_ROUTE=pass")
    print(f"PHASE14_SHARED_SMOKE_ROUTE_REQUIRED_MARKER_COUNT={len(MAKEFILE_MARKERS) + len(WORKFLOW_MARKERS)}")
    print(f"PHASE14_SHARED_SMOKE_ROUTE_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_WORKFLOW_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
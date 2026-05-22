#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=shared_smoke_route

Fail-closed checker for the bounded Phase 14 shared smoke route.

This guard exists for the lane-local executable path only. It validates that
the current repo exposes a dedicated `phase14-validate` Makefile route, that
the route reruns the shared smoke route checker plus the current tests-root
smoke-summary checker, validator, and release-boundary checker packets, that
the bootstrap workflow reruns that same route, and that the shared smoke
manifest records the same single-route Makefile split plus the focused raw
build-file smoke shard without claiming that the missing `phase14-smoke`,
`phase14-test`, or full bundle wrappers have returned.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=shared_smoke_route"
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")

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

REQUIRED_MANIFEST_VALUES = {
    ("productization", "validation_gate"): "make -C zigux phase14-validate",
    ("smoke_commands",): ["make -C zigux phase14-validate"],
    ("smoke_shard_commands",): ["zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"],
    ("survey_summary", "phase14_make_target_present"): True,
    ("survey_summary", "phase14_make_smoke_target_present"): False,
    ("survey_summary", "workflow_runs_phase14_validate"): True,
    ("survey_summary", "workflow_runs_phase14_build"): False,
    ("survey_summary", "workflow_runs_phase14_smoke_shard"): False,
}


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


def lookup_path(payload: object, path: tuple[str, ...]) -> object:
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(".".join(path))
        current = current[key]
    return current


def require_manifest_values(errors: list[str], manifest: object) -> None:
    for path, expected in REQUIRED_MANIFEST_VALUES.items():
        try:
            actual = lookup_path(manifest, path)
        except KeyError:
            errors.append(f"missing_manifest_key:{'.'.join(path)}")
            continue
        if actual != expected:
            errors.append(
                "manifest_value_mismatch:"
                f"{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in [MAKEFILE_PATH, WORKFLOW_PATH, MANIFEST_PATH]:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    require_markers(errors, MAKEFILE_PATH, makefile, MAKEFILE_MARKERS)
    require_markers(errors, WORKFLOW_PATH, workflow, WORKFLOW_MARKERS)
    require_absent(errors, WORKFLOW_PATH, workflow, FORBIDDEN_WORKFLOW_MARKERS)

    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors
    require_manifest_values(errors, manifest)
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


def fixture_manifest() -> str:
    payload = {
        "productization": {"validation_gate": "make -C zigux phase14-validate"},
        "smoke_commands": ["make -C zigux phase14-validate"],
        "smoke_shard_commands": [
            "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
        ],
        "survey_summary": {
            "phase14_make_target_present": True,
            "phase14_make_smoke_target_present": False,
            "workflow_runs_phase14_validate": True,
            "workflow_runs_phase14_build": False,
            "workflow_runs_phase14_smoke_shard": False,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(root, WORKFLOW_PATH, fixture_workflow())
    write_text(root, MANIFEST_PATH, fixture_manifest())


def write_fixture_manifest(root: Path, payload: object) -> None:
    write_text(root, MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")


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

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["smoke_commands"] = ["make -C zigux phase14-smoke"]
        write_fixture_manifest(base, manifest)
        if not any("manifest_value_mismatch:smoke_commands" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected smoke command manifest drift failure")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["workflow_runs_phase14_build"] = True
        write_fixture_manifest(base, manifest)
        if not any("manifest_value_mismatch:survey_summary.workflow_runs_phase14_build" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected workflow summary manifest drift failure")
            return 1

        print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass")
        print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST_CASE_COUNT=5")
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
    print(f"PHASE14_SHARED_SMOKE_ROUTE_MANIFEST_ASSERTION_COUNT={len(REQUIRED_MANIFEST_VALUES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

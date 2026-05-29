#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=shared_smoke_route

Fail-closed checker for the bounded Phase 14 shared smoke route.

This guard exists for the lane-local executable path only. It validates that
the current repo exposes a dedicated `phase14-validate` Makefile route, keeps
the staged-toolchain fallback chain explicit, reruns the shared checker packet,
and keeps the validator-side skbuff, ring-buffer, and RCU compile-route checks
recorded in both the validator and shared smoke manifest without promoting the
missing `phase14-smoke`, `phase14-test`, or full bundle wrappers.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase14.py")

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
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
    "scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py --self-test",
    "scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py",
    "scripts/zigux/check-phase14-rcu-rollback-guardrail.py --self-test",
    "scripts/zigux/check-phase14-rcu-rollback-guardrail.py",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py",
]
MAKEFILE_TOOLCHAIN_MARKERS = [
    "ZIG_PINNED_TARGET :=",
    "ZIG_PINNED_CHANNEL :=",
    "ZIG_PINNED_EXTRACT_ROOT :=",
    "ZIG_PINNED_EXECUTABLE :=",
    "ZIG_LOCAL_TOOLCHAIN :=",
    "ZIG_PINNED_TOOLCHAIN :=",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
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
VALIDATOR_MARKERS = [
    'SKBUFF_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-skbuff-compile-route.py"',
    'RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = (\n    "scripts/zigux/check-phase14-ring-buffer-compile-route.py"\n)',
    'RCU_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-rcu-compile-route.py"',
    "run_guardrail_checker(\n                args.root,\n                SKBUFF_COMPILE_ROUTE_CHECKER_PATH,\n                self_test=False,",
    "run_guardrail_checker(\n                args.root,\n                RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,\n                self_test=False,",
    "run_guardrail_checker(\n                args.root,\n                RCU_COMPILE_ROUTE_CHECKER_PATH,\n                self_test=False,",
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
    ("survey_summary", "phase14_validate_runs_rollback_threshold_sequencing"): True,
    ("survey_summary", "phase14_validate_runs_skbuff_stay_in_c_guardrail"): True,
    ("survey_summary", "phase14_validate_runs_skbuff_compile_route_checker"): True,
    ("survey_summary", "shared_manifest_records_skbuff_compile_route_checker"): True,
    ("survey_summary", "phase14_validate_runs_ring_buffer_compile_route_checker"): True,
    ("survey_summary", "shared_manifest_records_ring_buffer_compile_route_checker"): True,
    ("survey_summary", "phase14_validate_runs_rcu_compile_route_checker"): True,
    ("survey_summary", "shared_manifest_records_rcu_compile_route_checker"): True,
    ("survey_summary", "phase14_validate_runs_rcu_rollback_guardrail"): True,
    ("survey_summary", "phase14_make_uses_pinned_toolchain_fallback"): True,
    ("survey_summary", "phase14_make_uses_local_toolchain_probe"): True,
    ("survey_summary", "phase14_make_falls_back_to_path_zig"): True,
}
EXPECTED_COMPILE_SHARDS = [
    {"label": "phase14-workqueue-bridge-tests", "root_source": "phase14_workqueue_bridge.zig", "coverage": "full_bundle_only"},
    {"label": "phase14-workqueue-reviewability-tests", "root_source": "phase14_workqueue_reviewability.zig", "coverage": "full_bundle_only"},
    {"label": "phase14-skbuff-bridge-tests", "root_source": "phase14_skbuff_bridge.zig", "coverage": "full_bundle_only"},
    {"label": "phase14-ring-buffer-survey-tests", "root_source": "phase14_ring_buffer_survey.zig", "coverage": "full_bundle_only"},
    {"label": "phase14-rcu-tree-survey-tests", "root_source": "phase14_rcu_tree_survey.zig", "coverage": "full_bundle_only"},
    {"label": "phase14-end-to-end-smoke-tests", "root_source": "phase14_end_to_end_smoke_survey.zig", "coverage": "focused_and_full_bundle"},
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
            errors.append(f"manifest_value_mismatch:{'.'.join(path)}:expected={expected!r}:actual={actual!r}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in [MAKEFILE_PATH, WORKFLOW_PATH, MANIFEST_PATH, VALIDATOR_PATH]:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    validator = read_text(root, VALIDATOR_PATH)
    require_markers(errors, MAKEFILE_PATH, makefile, MAKEFILE_MARKERS)
    require_markers(errors, MAKEFILE_PATH, makefile, MAKEFILE_TOOLCHAIN_MARKERS)
    require_markers(errors, WORKFLOW_PATH, workflow, WORKFLOW_MARKERS)
    for marker in FORBIDDEN_WORKFLOW_MARKERS:
        if marker in workflow:
            errors.append(f"forbidden_marker:{WORKFLOW_PATH.as_posix()}:{marker}")
    require_markers(errors, VALIDATOR_PATH, validator, VALIDATOR_MARKERS)
    try:
        manifest = json.loads(read_text(root, MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        return [f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}"]
    require_manifest_values(errors, manifest)
    if lookup_path(manifest, ("compile_shards",)) != EXPECTED_COMPILE_SHARDS:
        errors.append("manifest_value_mismatch:compile_shards")
    return errors


def fixture_makefile() -> str:
    return """PYTHON ?= python3
PHASE2_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..
ZIG_PINNED_CHANNEL := 0.17.0-dev.87+9b177a7d2
ZIG_PINNED_TARGET := x86_64-linux
ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)
ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))
ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))
ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))
ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)
.PHONY: phase12-smoke phase12-test phase12 phase14-validate
phase14-validate:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rcu-rollback-guardrail.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rcu-rollback-guardrail.py
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py
"""


def fixture_workflow() -> str:
    return """steps:
  - name: Self-test current Phase 14 shared smoke route checker
    run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
  - name: Run current Phase 14 validate route
    run: make -C zigux phase14-validate
"""


def fixture_manifest() -> str:
    payload = {"productization": {"validation_gate": "make -C zigux phase14-validate"}, "smoke_commands": ["make -C zigux phase14-validate"], "smoke_shard_commands": ["zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"], "compile_shards": EXPECTED_COMPILE_SHARDS, "survey_summary": {}}
    for path, expected in REQUIRED_MANIFEST_VALUES.items():
        if len(path) == 2 and path[0] == "survey_summary":
            payload["survey_summary"][path[1]] = expected
    return json.dumps(payload, indent=2) + "\n"


def fixture_validator() -> str:
    return '''SKBUFF_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-skbuff-compile-route.py"
RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH = (
    "scripts/zigux/check-phase14-ring-buffer-compile-route.py"
)
RCU_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-rcu-compile-route.py"
def main(args):
    run_guardrail_checker(
                args.root,
                SKBUFF_COMPILE_ROUTE_CHECKER_PATH,
                self_test=False,
            )
    run_guardrail_checker(
                args.root,
                RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH,
                self_test=False,
            )
    run_guardrail_checker(
                args.root,
                RCU_COMPILE_ROUTE_CHECKER_PATH,
                self_test=False,
            )
'''


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(root, WORKFLOW_PATH, fixture_workflow())
    write_text(root, MANIFEST_PATH, fixture_manifest())
    write_text(root, VALIDATOR_PATH, fixture_validator())


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-shared-smoke-route-"))
    try:
        write_fixture_tree(base)
        if check(base):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("fixture failed clean check")
            return 1
        manifest_keys = ["phase14_validate_runs_skbuff_compile_route_checker", "shared_manifest_records_skbuff_compile_route_checker", "phase14_validate_runs_ring_buffer_compile_route_checker", "shared_manifest_records_ring_buffer_compile_route_checker", "phase14_validate_runs_rcu_compile_route_checker", "shared_manifest_records_rcu_compile_route_checker"]
        for key in manifest_keys:
            write_fixture_tree(base)
            payload = json.loads(fixture_manifest())
            payload["survey_summary"][key] = False
            write_text(base, MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")
            if not any(f"manifest_value_mismatch:survey_summary.{key}" in error for error in check(base)):
                print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
                print(f"expected {key} manifest drift failure")
                return 1
        validator_keys = ["SKBUFF_COMPILE_ROUTE_CHECKER_PATH", "RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH", "RCU_COMPILE_ROUTE_CHECKER_PATH"]
        for key in validator_keys:
            write_fixture_tree(base)
            write_text(base, VALIDATOR_PATH, read_text(base, VALIDATOR_PATH).replace(key, f"MISSING_{key}", 1))
            if not any(key in error for error in check(base)):
                print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
                print(f"expected {key} validator drift failure")
                return 1
        write_fixture_tree(base)
        write_text(base, WORKFLOW_PATH, fixture_workflow() + "  - run: make -C zigux phase14-smoke\n")
        if not any("phase14-smoke" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected forbidden workflow smoke wrapper failure")
            return 1
        print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass")
        print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST_CASE_COUNT=10")
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
    print(f"PHASE14_SHARED_SMOKE_ROUTE_REQUIRED_MARKER_COUNT={len(MAKEFILE_MARKERS) + len(MAKEFILE_TOOLCHAIN_MARKERS) + len(WORKFLOW_MARKERS) + len(VALIDATOR_MARKERS)}")
    print(f"PHASE14_SHARED_SMOKE_ROUTE_FORBIDDEN_MARKER_COUNT={len(FORBIDDEN_WORKFLOW_MARKERS)}")
    print(f"PHASE14_SHARED_SMOKE_ROUTE_MANIFEST_ASSERTION_COUNT={len(REQUIRED_MANIFEST_VALUES) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

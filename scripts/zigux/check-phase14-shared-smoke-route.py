#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=shared_smoke_route

Fail-closed checker for the bounded Phase 14 shared smoke route.

This guard exists for the lane-local executable path only. It validates that
the current repo exposes a dedicated `phase14-validate` Makefile route, that
the Makefile keeps the staged-toolchain fallback chain explicit, that the route
reruns the shared smoke route checker plus the current tests-root
smoke-summary checker, validator, rollback-threshold sequencing checker,
dedicated skbuff stay-in-C guardrail, validator-side skbuff compile-route
checker, validator-side RCU compile-route checker, dedicated RCU rollback
guardrail, and release-boundary checker packets, and that the shared smoke
manifest records the same single-route Makefile split plus the focused raw
build-file smoke shard as reminder vocabulary without claiming that the missing
`phase14-smoke`, `phase14-test`, or full bundle wrappers have returned.
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
    'RCU_COMPILE_ROUTE_CHECKER_PATH = "scripts/zigux/check-phase14-rcu-compile-route.py"',
    "run_guardrail_checker(\n                args.root,\n                SKBUFF_COMPILE_ROUTE_CHECKER_PATH,\n                self_test=False,",
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
    ("survey_summary", "phase14_validate_runs_rcu_compile_route_checker"): True,
    ("survey_summary", "shared_manifest_records_rcu_compile_route_checker"): True,
    ("survey_summary", "phase14_validate_runs_rcu_rollback_guardrail"): True,
    ("survey_summary", "phase14_make_uses_pinned_toolchain_fallback"): True,
    ("survey_summary", "phase14_make_uses_local_toolchain_probe"): True,
    ("survey_summary", "phase14_make_falls_back_to_path_zig"): True,
}

EXPECTED_COMPILE_SHARDS = [
    {
        "label": "phase14-workqueue-bridge-tests",
        "root_source": "phase14_workqueue_bridge.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-workqueue-reviewability-tests",
        "root_source": "phase14_workqueue_reviewability.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-skbuff-bridge-tests",
        "root_source": "phase14_skbuff_bridge.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-ring-buffer-survey-tests",
        "root_source": "phase14_ring_buffer_survey.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-rcu-tree-survey-tests",
        "root_source": "phase14_rcu_tree_survey.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-end-to-end-smoke-tests",
        "root_source": "phase14_end_to_end_smoke_survey.zig",
        "coverage": "focused_and_full_bundle",
    },
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


def require_compile_shards(errors: list[str], manifest: object) -> None:
    try:
        compile_shards = lookup_path(manifest, ("compile_shards",))
    except KeyError:
        errors.append("missing_manifest_key:compile_shards")
        return

    if compile_shards != EXPECTED_COMPILE_SHARDS:
        errors.append(
            "manifest_value_mismatch:"
            f"compile_shards:expected={EXPECTED_COMPILE_SHARDS!r}:actual={compile_shards!r}"
        )


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
    require_absent(errors, WORKFLOW_PATH, workflow, FORBIDDEN_WORKFLOW_MARKERS)
    require_markers(errors, VALIDATOR_PATH, validator, VALIDATOR_MARKERS)

    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors
    require_manifest_values(errors, manifest)
    require_compile_shards(errors, manifest)
    return errors


def fixture_makefile() -> str:
    return """PYTHON ?= python3
PHASE2_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..
PHASE2_TOOLCHAIN_POLICY := $(PHASE2_SCRIPT_ROOT)/zig-toolchain-policy.json
ZIG_PINNED_CHANNEL := 0.17.0-dev.87+9b177a7d2
ZIG_PINNED_TARGET := x86_64-linux
ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)
ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))
ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))
ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))
ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)

.PHONY: phase12-smoke phase12-test phase12 phase14-validate

phase12-smoke:
	cd $(ZIGUX_ROOT) && zig build smoke --build-file zigux/tests/phase12_build.zig --summary all

phase12-test:
	cd $(ZIGUX_ROOT) && zig build test --build-file zigux/tests/phase12_build.zig --summary all

phase12: phase12-smoke phase12-test

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
        "compile_shards": EXPECTED_COMPILE_SHARDS,
        "survey_summary": {
            "phase14_make_target_present": True,
            "phase14_make_smoke_target_present": False,
            "workflow_runs_phase14_validate": True,
            "workflow_runs_phase14_build": False,
            "workflow_runs_phase14_smoke_shard": False,
            "phase14_validate_runs_rollback_threshold_sequencing": True,
            "phase14_validate_runs_skbuff_stay_in_c_guardrail": True,
            "phase14_validate_runs_skbuff_compile_route_checker": True,
            "phase14_validate_runs_rcu_compile_route_checker": True,
            "shared_manifest_records_rcu_compile_route_checker": True,
            "phase14_validate_runs_rcu_rollback_guardrail": True,
            "phase14_make_uses_pinned_toolchain_fallback": True,
            "phase14_make_uses_local_toolchain_probe": True,
            "phase14_make_falls_back_to_path_zig": True,
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def fixture_validator() -> str:
    return """#!/usr/bin/env python3
SKBUFF_COMPILE_ROUTE_CHECKER_PATH = \"scripts/zigux/check-phase14-skbuff-compile-route.py\"
RCU_COMPILE_ROUTE_CHECKER_PATH = \"scripts/zigux/check-phase14-rcu-compile-route.py\"

def run_guardrail_checker(root, rel_path, *, self_test):
    return []

def main(args):
    run_guardrail_checker(
                args.root,
                SKBUFF_COMPILE_ROUTE_CHECKER_PATH,
                self_test=False,
            )
    run_guardrail_checker(
                args.root,
                RCU_COMPILE_ROUTE_CHECKER_PATH,
                self_test=False,
            )
"""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(root, WORKFLOW_PATH, fixture_workflow())
    write_text(root, MANIFEST_PATH, fixture_manifest())
    write_text(root, VALIDATOR_PATH, fixture_validator())


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
                "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))\n",
                "",
                1,
            ),
        )
        if not any("ZIG_LOCAL_TOOLCHAIN :=" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected local toolchain probe marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            MAKEFILE_PATH,
            fixture_makefile().replace(
                "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)\n",
                "",
                1,
            ),
        )
        if not any("ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected fallback chain marker failure")
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
            MAKEFILE_PATH,
            fixture_makefile().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rollback-threshold-sequencing.py\n",
                "",
                1,
            ),
        )
        if not any("check-phase14-rollback-threshold-sequencing.py --self-test" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected rollback-threshold checker marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            VALIDATOR_PATH,
            fixture_validator().replace(
                "run_guardrail_checker(\n                args.root,\n                SKBUFF_COMPILE_ROUTE_CHECKER_PATH,\n                self_test=False,\n            )\n",
                "",
                1,
            ),
        )
        if not any("SKBUFF_COMPILE_ROUTE_CHECKER_PATH" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected validator-side skbuff compile-route marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            VALIDATOR_PATH,
            fixture_validator().replace(
                "run_guardrail_checker(\n                args.root,\n                RCU_COMPILE_ROUTE_CHECKER_PATH,\n                self_test=False,\n            )\n",
                "",
                1,
            ),
        )
        if not any("RCU_COMPILE_ROUTE_CHECKER_PATH" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected validator-side rcu compile-route marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            MAKEFILE_PATH,
            fixture_makefile().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py\n",
                "",
                1,
            ),
        )
        if not any("check-phase14-skbuff-stay-in-c-guardrail.py --self-test" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected skbuff stay-in-c guardrail marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            MAKEFILE_PATH,
            fixture_makefile().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rcu-rollback-guardrail.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-rcu-rollback-guardrail.py\n",
                "",
                1,
            ),
        )
        if not any("check-phase14-rcu-rollback-guardrail.py --self-test" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected RCU rollback guardrail marker failure")
            return 1

        write_fixture_tree(base)
        write_text(
            base,
            MAKEFILE_PATH,
            fixture_makefile().replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test\n"
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-release-boundary-exact-counts.py\n",
                "",
                1,
            ),
        )
        if not any("check-phase14-release-boundary-exact-counts.py --self-test" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected release-boundary checker marker failure")
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
        manifest["survey_summary"]["phase14_validate_runs_skbuff_stay_in_c_guardrail"] = False
        write_fixture_manifest(base, manifest)
        if not any("manifest_value_mismatch:survey_summary.phase14_validate_runs_skbuff_stay_in_c_guardrail" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected skbuff guardrail manifest drift failure")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_skbuff_compile_route_checker"] = False
        write_fixture_manifest(base, manifest)
        if not any("manifest_value_mismatch:survey_summary.phase14_validate_runs_skbuff_compile_route_checker" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected skbuff compile-route manifest drift failure")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_rcu_compile_route_checker"] = False
        write_fixture_manifest(base, manifest)
        if not any("manifest_value_mismatch:survey_summary.phase14_validate_runs_rcu_compile_route_checker" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected rcu compile-route manifest drift failure")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["shared_manifest_records_rcu_compile_route_checker"] = False
        write_fixture_manifest(base, manifest)
        if not any("manifest_value_mismatch:survey_summary.shared_manifest_records_rcu_compile_route_checker" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected rcu shared-manifest marker drift failure")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_validate_runs_rcu_rollback_guardrail"] = False
        write_fixture_manifest(base, manifest)
        if not any("manifest_value_mismatch:survey_summary.phase14_validate_runs_rcu_rollback_guardrail" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected RCU guardrail manifest drift failure")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["phase14_make_uses_local_toolchain_probe"] = False
        write_fixture_manifest(base, manifest)
        if not any("manifest_value_mismatch:survey_summary.phase14_make_uses_local_toolchain_probe" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected local toolchain manifest drift failure")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["compile_shards"][5]["coverage"] = "full_bundle_only"
        write_fixture_manifest(base, manifest)
        if not any("manifest_value_mismatch:compile_shards" in error for error in check(base)):
            print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=fail")
            print("expected compile-shard manifest drift failure")
            return 1

        print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST=pass")
        print("PHASE14_SHARED_SMOKE_ROUTE_SELF_TEST_CASE_COUNT=19")
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

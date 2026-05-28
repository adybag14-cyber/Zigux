#!/usr/bin/env python3
"""Validate the current Phase 2 closure note against the shipped closure packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_REL = Path("zigux/Makefile")
PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
PHASE2_BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
PHASE2_TOOL_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
PHASE2_ARTIFACT_TOOLS_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")
PHASE2_CROSS_TARGETS_REL = Path("zigux/tests/fixtures/phase2_cross_targets.json")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
GENKSYMS_CASES_REL = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")

VALIDATOR_COMMANDS = (
    "python3 scripts/zigux/validate-phase2.py",
    "python3 scripts/zigux/validate-phase2-closure.py",
)

GENKSYMS_COMMANDS = (
    "python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "python3 scripts/zigux/check-genksyms-bridge.py",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "zig test scripts/zigux/genksyms.zig",
    "make -C zigux phase2-genksyms",
)

SHARED_TOOLING_COMMANDS = (
    "python3 scripts/zigux/check-phase2-tool-manifest.py",
    "python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "python3 scripts/zigux/check-phase2-cross.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "python3 scripts/zigux/check-fixdep-diff.py",
)

SHARED_GENKSYMS_PROOF_PATHS = (
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)
HELPER_LOCAL_INLINE_SHORT_PROOF = (
    "scripts/zigux/genksyms_inline_short_option_argument_test.zig"
)

GENKSYMS_REQUIRED_NOTE_MARKERS = (
    "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/genksyms.zig",
    *SHARED_GENKSYMS_PROOF_PATHS,
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
)

SHARED_TOOLING_REQUIRED_NOTE_MARKERS = (
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
)

MANIFEST_SURFACE_KEYS = (
    "review_surfaces",
    "closure_notes",
    "validators",
    "checkers",
    "bootstrap_helpers",
    "archive_support",
    "artifact_support",
    "bridge_helpers",
    "cross_route_support",
    "fixdep_support",
    "fixture_roster",
    "make_wrappers",
    "policy",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_string_list(
    issues: list[tuple[str, str]], manifest: dict[str, object], key: str
) -> list[str]:
    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return []
    value = present_surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return []
    return list(value)


def manifest_paths(surface_values: list[str]) -> list[str]:
    return [value for value in surface_values if not value.startswith("make -C ")]


def expected_genksyms_fixture_paths(genksyms_manifest: dict[str, object]) -> list[str]:
    fixture_root = genksyms_manifest.get("fixture_root")
    if not isinstance(fixture_root, str) or not fixture_root:
        raise SystemExit(
            f"invalid fixture_root in required file: {GENKSYMS_MANIFEST_REL}"
        )

    expected_lists = (
        "bridge_expected_packet",
        "help_packet",
        "process_output_packet",
    )
    paths = [
        GENKSYMS_CASES_REL.as_posix(),
        GENKSYMS_MANIFEST_REL.as_posix(),
    ]
    for key in expected_lists:
        values = genksyms_manifest.get(key)
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise SystemExit(f"invalid {key} in required file: {GENKSYMS_MANIFEST_REL}")
        for value in values:
            paths.append(f"{fixture_root}/{value}")

    return paths


def helper_local_genksyms_proof_paths(genksyms_manifest: dict[str, object]) -> list[str]:
    proofs = genksyms_manifest.get("standalone_proof_packet")
    if not isinstance(proofs, list) or not all(isinstance(item, str) for item in proofs):
        raise SystemExit(
            f"invalid standalone_proof_packet in required file: {GENKSYMS_MANIFEST_REL}"
        )
    return list(proofs)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in (
        WORKFLOW_REL,
        MAKEFILE_REL,
        PHASE2_CLOSURE_REL,
        PHASE2_BOOTSTRAP_NOTES_REL,
        PHASE2_VALIDATE_REL,
        PHASE2_CLOSURE_VALIDATE_REL,
        PHASE2_TOOL_MANIFEST_REL,
        PHASE2_ARTIFACT_TOOLS_MANIFEST_REL,
        PHASE2_CROSS_TARGETS_REL,
        GENKSYMS_MANIFEST_REL,
        GENKSYMS_CASES_REL,
    ):
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    workflow_text = read_text(root / WORKFLOW_REL)
    makefile_text = read_text(root / MAKEFILE_REL)
    manifest = read_json(root / PHASE2_TOOL_MANIFEST_REL)
    genksyms_manifest = read_json(root / GENKSYMS_MANIFEST_REL)

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues
    if not isinstance(genksyms_manifest, dict):
        issues.append(("INVALID_GENKSYMS_MANIFEST_SHAPE", "root"))
        return issues

    if manifest.get("repo_reality_gaps") != []:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest.get("repo_reality_gaps"))))

    manifest_surface_values: dict[str, list[str]] = {}
    for key in MANIFEST_SURFACE_KEYS:
        manifest_surface_values[key] = require_string_list(issues, manifest, key)

    if issues:
        return issues

    for key, values in manifest_surface_values.items():
        for value in manifest_paths(values):
            if not (root / value).exists():
                issues.append(("MISSING_MANIFEST_SURFACE", f"{key}:{value}"))

    fixture_roster = set(manifest_surface_values["fixture_roster"])
    bridge_helpers = set(manifest_surface_values["bridge_helpers"])
    for path in expected_genksyms_fixture_paths(genksyms_manifest):
        if path not in fixture_roster:
            issues.append(("MISSING_MANIFEST_SURFACE", f"fixture_roster:{path}"))

    helper_local_proof_paths = helper_local_genksyms_proof_paths(genksyms_manifest)
    for path in helper_local_proof_paths:
        if not (root / path).exists():
            issues.append(("MISSING_HELPER_LOCAL_PROOF_PATH", path))

    for path in SHARED_GENKSYMS_PROOF_PATHS:
        if path not in helper_local_proof_paths:
            issues.append(("MISSING_SHARED_GENKSYMS_PROOF", path))
        if path not in bridge_helpers:
            issues.append(("MISSING_MANIFEST_SURFACE", f"bridge_helpers:{path}"))

    for path in helper_local_proof_paths:
        if path.endswith("_test.zig") and path.startswith("scripts/zigux/genksyms_"):
            if path not in SHARED_GENKSYMS_PROOF_PATHS and path in bridge_helpers:
                issues.append(("UNEXPECTED_SHARED_GENKSYMS_PROOF", path))

    process_output_packet = genksyms_manifest.get("process_output_packet")
    if not isinstance(process_output_packet, list) or not all(
        isinstance(item, str) for item in process_output_packet
    ):
        issues.append(("INVALID_GENKSYMS_MANIFEST_SHAPE", "process_output_packet"))
        return issues

    expected_process_output_line = (
        "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET="
        + ",".join(
            f"zigux/tests/fixtures/genksyms_bridge/{item}" for item in process_output_packet
        )
    )
    if expected_process_output_line not in closure_text:
        issues.append(("MISSING_CLOSURE_LINE", expected_process_output_line))

    expected_routes = [
        value for value in manifest_surface_values["make_wrappers"] if value.startswith("make -C ")
    ]
    expected_routes_line = "PHASE2_SHARED_MAKE_ROUTES=" + ",".join(expected_routes)
    if expected_routes_line not in closure_text:
        issues.append(("MISSING_CLOSURE_LINE", expected_routes_line))

    expected_validator_line = "PHASE2_CLOSURE_VALIDATORS=" + ",".join(VALIDATOR_COMMANDS)
    if expected_validator_line not in closure_text:
        issues.append(("MISSING_CLOSURE_LINE", expected_validator_line))

    expected_shared_tooling_line = "PHASE2_SHARED_TOOLING_CHECKERS=" + ",".join(
        SHARED_TOOLING_COMMANDS
    )
    if expected_shared_tooling_line not in closure_text:
        issues.append(("MISSING_CLOSURE_LINE", expected_shared_tooling_line))

    for marker in (
        *GENKSYMS_REQUIRED_NOTE_MARKERS,
        *SHARED_TOOLING_REQUIRED_NOTE_MARKERS,
        *VALIDATOR_COMMANDS,
        *GENKSYMS_COMMANDS,
        *SHARED_TOOLING_COMMANDS,
    ):
        if f"`{marker}`" not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    expected_workflow_lines = tuple(f"run: {command}" for command in GENKSYMS_COMMANDS)
    for marker in expected_workflow_lines:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    expected_makefile_lines = (
        "phase2-genksyms: phase2-toolchain",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
        "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    )
    for marker in expected_makefile_lines:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    process_output_packet = [
        "abbreviated_version_expected.json",
        "ambiguous_long_option_expected.json",
        "invalid_option_expected.json",
        "missing_long_dump_types_argument_expected.json",
        "missing_long_reference_argument_expected.json",
        "missing_reference_argument_expected.json",
        "too_many_reference_files_expected.json",
        "unsupported_long_option_expected.json",
        "unexpected_long_help_argument_expected.json",
        "abbreviated_unexpected_long_help_argument_expected.json",
    ]
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "repo_reality_gaps": [],
        "present_surfaces": {
            "review_surfaces": [
                "Documentation/zigux/README.md",
                "Documentation/zigux/phase2-closure.md",
                "Documentation/zigux/review-checklist.md",
                "scripts/zigux/README.md",
                "zigux/tests/README.md",
            ],
            "closure_notes": [
                "Documentation/zigux/phase2-closure.md",
                "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            ],
            "validators": [
                "scripts/zigux/validate-phase2.py",
                "scripts/zigux/validate-phase2-closure.py",
            ],
            "checkers": [
                "scripts/zigux/check-genksyms-bridge.py",
                "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
                "scripts/zigux/check-phase2-tool-manifest.py",
                "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
                "scripts/zigux/check-phase2-artifact-tools-manifest.py",
                "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
                "scripts/zigux/check-phase2-cross.py",
                "scripts/zigux/check-phase2-fixdep-gate.py",
                "scripts/zigux/check-fixdep-diff.py",
            ],
            "bootstrap_helpers": [
                "scripts/zigux/install-zig.py",
            ],
            "archive_support": [
                "third_party/README.md",
            ],
            "artifact_support": [
                "scripts/zigux/artifact_diff.py",
                "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
            ],
            "bridge_helpers": [
                "scripts/zigux/genksyms.zig",
                *SHARED_GENKSYMS_PROOF_PATHS,
            ],
            "cross_route_support": [
                "scripts/zigux/check-phase2-cross.py",
                "zigux/tests/fixtures/phase2_cross_targets.json",
            ],
            "fixdep_support": [
                "scripts/zigux/fixdep.zig",
                "scripts/zigux/check-phase2-fixdep-gate.py",
                "scripts/zigux/check-fixdep-diff.py",
                "zigux/tests/fixtures/fixdep/cases.json",
            ],
            "fixture_roster": [
                "zigux/tests/fixtures/genksyms_bridge/cases.json",
                "zigux/tests/fixtures/genksyms_bridge/manifest.json",
                "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
                "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
                *[
                    f"zigux/tests/fixtures/genksyms_bridge/{name}"
                    for name in process_output_packet
                ],
            ],
            "make_wrappers": [
                "zigux/Makefile",
                "make -C zigux phase2-toolchain",
                "make -C zigux phase2-tools",
                "make -C zigux phase2-kconfig",
                "make -C zigux phase2-cross",
                "make -C zigux phase2-genksyms",
                "make -C zigux phase2-fixdep",
                "make -C zigux phase2-validate",
                "make -C zigux phase2",
            ],
            "policy": [
                "scripts/zigux/zig-toolchain-policy.json",
            ],
        },
    }
    genksyms_manifest = {
        "tool": "scripts/zigux/genksyms.zig",
        "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
        "bridge_expected_packet": ["minimal_expected.json"],
        "help_packet": ["help_expected.json"],
        "process_output_packet": process_output_packet,
        "standalone_proof_packet": list(SHARED_GENKSYMS_PROOF_PATHS),
    }

    closure_text = """# Phase 2 Closure

This note keeps the shared Phase 2 closure packet parked while making the current `genksyms` evidence and shared repo-tooling reminder surfaces explicit and replayable from directly readable `master` surfaces.

## Status

- `PHASE2_STATUS=parked`
- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`
- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`
- shared note: `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- shared validator pair: `python3 scripts/zigux/validate-phase2.py` and `python3 scripts/zigux/validate-phase2-closure.py`

## Current Genksyms Evidence

- `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`
- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`
- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- `python3 scripts/zigux/check-genksyms-bridge.py`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `zig test scripts/zigux/genksyms.zig`
- `make -C zigux phase2-genksyms`
- `PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`

## Current Shared Repo-Tooling Evidence

- `scripts/zigux/check-phase2-tool-manifest.py`, `scripts/zigux/check-phase2-bootstrap-workflow-routes.py`, and `scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`, `scripts/zigux/check-phase2-cross.py`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/check-phase2-fixdep-gate.py`, and `scripts/zigux/check-fixdep-diff.py`
- `scripts/zigux/artifact_diff.py` and `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `python3 scripts/zigux/check-phase2-tool-manifest.py`
- `python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py`
- `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`
- `python3 scripts/zigux/check-phase2-cross.py`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- `python3 scripts/zigux/check-fixdep-diff.py`
- `PHASE2_SHARED_TOOLING_CHECKERS=python3 scripts/zigux/check-phase2-tool-manifest.py,python3 scripts/zigux/check-phase2-bootstrap-workflow-routes.py,python3 scripts/zigux/check-phase2-artifact-tools-manifest.py,python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py,python3 scripts/zigux/check-phase2-cross.py,python3 scripts/zigux/check-phase2-fixdep-gate.py,python3 scripts/zigux/check-fixdep-diff.py`

## Shared Replay Routes

- `PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2`
- `PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py`

## Repo-Reality Gaps

- `PHASE2_CURRENT_GAP_PACKET=`
"""

    workflow_lines = "\n".join(
        [
            "name: zigux-bootstrap",
            *[f"run: {command}" for command in GENKSYMS_COMMANDS],
        ]
    )
    makefile_lines = "\n".join(
        [
            "phase2-genksyms: phase2-toolchain",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
            "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
            "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
            "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
        ]
    )

    write_text(root / PHASE2_CLOSURE_REL, closure_text)
    write_text(root / WORKFLOW_REL, workflow_lines + "\n")
    write_text(root / MAKEFILE_REL, makefile_lines + "\n")
    write_text(root / PHASE2_TOOL_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
    write_text(
        root / PHASE2_ARTIFACT_TOOLS_MANIFEST_REL,
        json.dumps({"present": True}, indent=2) + "\n",
    )
    write_text(root / PHASE2_CROSS_TARGETS_REL, "[]\n")
    write_text(root / GENKSYMS_MANIFEST_REL, json.dumps(genksyms_manifest, indent=2) + "\n")
    write_text(root / GENKSYMS_CASES_REL, "[]\n")

    for rel in (
        "Documentation/zigux/README.md",
        "Documentation/zigux/review-checklist.md",
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "scripts/zigux/README.md",
        "zigux/tests/README.md",
        "scripts/zigux/validate-phase2.py",
        "scripts/zigux/validate-phase2-closure.py",
        "scripts/zigux/check-genksyms-bridge.py",
        "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
        "scripts/zigux/check-phase2-tool-manifest.py",
        "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
        "scripts/zigux/check-phase2-artifact-tools-manifest.py",
        "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
        "scripts/zigux/check-phase2-cross.py",
        "scripts/zigux/check-phase2-fixdep-gate.py",
        "scripts/zigux/check-fixdep-diff.py",
        "scripts/zigux/install-zig.py",
        "third_party/README.md",
        "scripts/zigux/artifact_diff.py",
        "scripts/zigux/genksyms.zig",
        *SHARED_GENKSYMS_PROOF_PATHS,
        "scripts/zigux/fixdep.zig",
        "zigux/tests/fixtures/fixdep/cases.json",
        "scripts/zigux/zig-toolchain-policy.json",
    ):
        write_text(root / rel, "present\n")

    write_text(
        root / "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
        "present\n",
    )
    write_text(
        root / "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
        "{}\n",
    )
    write_text(
        root / "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
        "{}\n",
    )
    for name in process_output_packet:
        write_text(root / f"zigux/tests/fixtures/genksyms_bridge/{name}", "{}\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(root / PHASE2_TOOL_MANIFEST_REL))
        manifest["present_surfaces"]["fixture_roster"].remove(
            "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json"
        )
        write_text(root / PHASE2_TOOL_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        assert (
            "MISSING_MANIFEST_SURFACE",
            "fixture_roster:zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        write_text(
            closure_path,
            read_text(closure_path).replace(
                "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=",
                "PHASE2_DROPPED_PROCESS_OUTPUT_PACKET=",
                1,
            ),
        )
        assert any(code == "MISSING_CLOSURE_LINE" for code, _ in collect_issues(root))
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        write_text(
            closure_path,
            read_text(closure_path).replace(
                "PHASE2_SHARED_TOOLING_CHECKERS=",
                "PHASE2_DROPPED_SHARED_TOOLING_CHECKERS=",
                1,
            ),
        )
        assert (
            "MISSING_CLOSURE_LINE",
            "PHASE2_SHARED_TOOLING_CHECKERS="
            + ",".join(SHARED_TOOLING_COMMANDS),
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        write_text(
            closure_path,
            read_text(closure_path).replace(
                "`zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`\n",
                "",
                1,
            ),
        )
        assert (
            "MISSING_CLOSURE_MARKER",
            "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        write_text(
            closure_path,
            read_text(closure_path).replace(
                "`scripts/zigux/check-phase2-tool-manifest.py`",
                "`scripts/zigux/check-phase2-tool-manifest.py.dropped`",
                1,
            ),
        )
        assert (
            "MISSING_CLOSURE_MARKER",
            "scripts/zigux/check-phase2-tool-manifest.py",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(root / PHASE2_TOOL_MANIFEST_REL))
        manifest["repo_reality_gaps"] = ["drift"]
        write_text(root / PHASE2_TOOL_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        assert ("UNEXPECTED_MANIFEST_GAPS", "['drift']") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (root / "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json").unlink()
        assert (
            "MISSING_MANIFEST_SURFACE",
            "fixture_roster:zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(root / GENKSYMS_MANIFEST_REL))
        manifest["standalone_proof_packet"].append(HELPER_LOCAL_INLINE_SHORT_PROOF)
        write_text(root / GENKSYMS_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        write_text(root / HELPER_LOCAL_INLINE_SHORT_PROOF, "present\n")
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(root / GENKSYMS_MANIFEST_REL))
        manifest["standalone_proof_packet"] = [SHARED_GENKSYMS_PROOF_PATHS[0]]
        write_text(root / GENKSYMS_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        assert (
            "MISSING_SHARED_GENKSYMS_PROOF",
            SHARED_GENKSYMS_PROOF_PATHS[1],
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest = json.loads(read_text(root / GENKSYMS_MANIFEST_REL))
        manifest["standalone_proof_packet"].append(HELPER_LOCAL_INLINE_SHORT_PROOF)
        write_text(root / GENKSYMS_MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")
        tool_manifest = json.loads(read_text(root / PHASE2_TOOL_MANIFEST_REL))
        tool_manifest["present_surfaces"]["bridge_helpers"].append(HELPER_LOCAL_INLINE_SHORT_PROOF)
        write_text(root / PHASE2_TOOL_MANIFEST_REL, json.dumps(tool_manifest, indent=2) + "\n")
        write_text(root / HELPER_LOCAL_INLINE_SHORT_PROOF, "present\n")
        assert (
            "UNEXPECTED_SHARED_GENKSYMS_PROOF",
            HELPER_LOCAL_INLINE_SHORT_PROOF,
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 2 closure note against the shipped closure packet."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print("PHASE2_CLOSURE_STATUS=parked")
    print("PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure")
    print("PHASE2_CLOSURE_REMAINING_GAPS=")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

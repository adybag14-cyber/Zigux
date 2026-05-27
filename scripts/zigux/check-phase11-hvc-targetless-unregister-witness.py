#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 HVC targetless-unregister witness packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


REQUIRED_COMMAND = "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"
PHASE11_VALIDATE_COMMAND = "make -C zigux phase11-validate"
PHASE11_VALIDATE_STEP = "Validate current Phase 11 support bundle"
TARGETLESS_WITNESS_SELF_TEST_COMMAND = (
    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test"
)
TARGETLESS_WITNESS_COMMAND = (
    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"
)
TARGETLESS_WITNESS_TEST_NAME = "phase11-hvc-targetless-unregister-gap"
TARGETLESS_WITNESS_REPLAY = "zigux/tests/phase11_hvc_targetless_unregister_gap.zig"
TARGETLESS_WITNESS_BUILD_REPLAY = "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"

WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
LANE_NOTE_PATH = "Documentation/zigux/phase11-driver-lane-sequencing.md"
CLEANUP_COMPANION_PATH = "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"
VALIDATION_MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
SURVEY_PATH = "Documentation/zigux/phase11-hvc-console-survey.md"
VERIFY_BOUNDARY_PATH = "Documentation/zigux/phase11-hvc-verify-helper-boundary.md"
DRIVER_PATH = "drivers/tty/hvc/hvc_console.zig"
CLEANUP_CHECKER_PATH = "scripts/zigux/check-phase11-hvc-cleanup-current-head.py"
VALIDATE_PHASE11_PATH = "scripts/zigux/validate-phase11.py"
MAKEFILE_PATH = "zigux/Makefile"
INVENTORY_PATH = "zigux/tests/fixtures/phase11_build_inventory.json"
WITNESS_PATH = TARGETLESS_WITNESS_REPLAY
WITNESS_BUILD_PATH = TARGETLESS_WITNESS_BUILD_REPLAY
SELF_PATH = "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"

CLEANUP_SELF_TEST_COMMAND = "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test"
CLEANUP_COMMAND = "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py"

REQUIRED_PACKET_FILES = (
    WORKFLOW_PATH,
    LANE_NOTE_PATH,
    CLEANUP_COMPANION_PATH,
    VALIDATION_MATRIX_PATH,
    SURVEY_PATH,
    VERIFY_BOUNDARY_PATH,
    DRIVER_PATH,
    CLEANUP_CHECKER_PATH,
    SELF_PATH,
    VALIDATE_PHASE11_PATH,
    MAKEFILE_PATH,
    INVENTORY_PATH,
    WITNESS_PATH,
    WITNESS_BUILD_PATH,
)

FILE_EXPECTATIONS = {
    WORKFLOW_PATH: (
        PHASE11_VALIDATE_STEP,
        PHASE11_VALIDATE_COMMAND,
    ),
    LANE_NOTE_PATH: (
        DRIVER_PATH,
        VERIFY_BOUNDARY_PATH,
        CLEANUP_COMPANION_PATH,
        CLEANUP_CHECKER_PATH,
        SELF_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
    ),
    CLEANUP_COMPANION_PATH: (
        DRIVER_PATH,
        VERIFY_BOUNDARY_PATH,
        CLEANUP_CHECKER_PATH,
        SELF_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
        "standalone targetless-unregister witness",
        "separate failure-mode replay",
        "build-inventory checker",
        "shared inventory-backed proof routes",
    ),
    VALIDATION_MATRIX_PATH: (
        VERIFY_BOUNDARY_PATH,
        CLEANUP_COMPANION_PATH,
        CLEANUP_CHECKER_PATH,
        "scripts/zigux/check-phase11-build-inventory.py",
        SELF_PATH,
        INVENTORY_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
        "make -C zigux phase11-validate",
        "witness shard now rereads the live starter and the boundary note together",
        "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet",
    ),
    SURVEY_PATH: (
        CLEANUP_COMPANION_PATH,
        CLEANUP_CHECKER_PATH,
        "scripts/zigux/check-phase11-build-inventory.py",
        INVENTORY_PATH,
        SELF_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
        "standalone targetless-unregister witness pair likewise stays",
        "without promoting itself into the shared three-entry build inventory",
    ),
    VERIFY_BOUNDARY_PATH: (
        "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge",
        "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable",
        "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.",
        "the literal-fallback helpers keep the targetless sysrq path without notifier, the sanitized registered-but-targetless sysrq path, and the non-kernel sysrq literal fallback explicit",
    ),
    DRIVER_PATH: (
        "pub const TargetlessNotifierEdgeSummary = struct {",
        "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
        "targetless_no_unregister_edge: bool,",
        "targetless_unregister_request_sanitized: bool,",
        "keeps_live_notifier_execution_out_of_scope: bool,",
        ".targetless_no_unregister_edge = request.notifier_registered and !request.target_present and !request.unregister_requested,",
        ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,",
        ".unregister_requested = request.unregister_requested and request.target_present and request.notifier_registered,",
        'test "phase11 hvc console keeps targetless notifier no-unregister edge reviewable" {',
        "try std.testing.expect(targetless_sanitized.targetless_unregister_request_sanitized);",
        "try std.testing.expect(!targetless_sanitized.unregister_requested);",
        "try std.testing.expect(targetless_sanitized.keeps_live_notifier_execution_out_of_scope);",
        'test "phase11 hvc console keeps unregistered targeted notifier-unregister request sanitized" {',
        "try std.testing.expect(!summary.unregister_requested);",
    ),
    CLEANUP_CHECKER_PATH: (
        "check-phase11-hvc-targetless-unregister-witness.py",
        "phase11_hvc_targetless_unregister_gap_build.zig",
    ),
    VALIDATE_PHASE11_PATH: (
        CLEANUP_CHECKER_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
        "phase11-hvc-cleanup-current-head",
        '"phase11-hvc-targetless-unregister-witness-self-test",',
        '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test"),',
        '"phase11-hvc-targetless-unregister-witness",',
        '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"),',
        "phase11-hvc-targetless-unregister-gap-build",
    ),
    MAKEFILE_PATH: (
        "phase11-validate:",
        "phase11_hvc_targetless_unregister_gap_build.zig",
    ),
    WITNESS_PATH: (
        'test "phase11 hvc notifier witness records current-head targetless unregister sanitizer" {',
        f'const driver = try readRepoFile("{DRIVER_PATH}");',
        f'const boundary = try readRepoFile("{VERIFY_BOUNDARY_PATH}");',
        f'const companion = try readRepoFile("{CLEANUP_COMPANION_PATH}");',
        f'const survey = try readRepoFile("{SURVEY_PATH}");',
        f'const matrix = try readRepoFile("{VALIDATION_MATRIX_PATH}");',
        'try expectContains(driver, "targetless_no_unregister_edge: bool,");',
        'try expectContains(driver, ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,");',
        'try expectContains(driver, "try std.testing.expect(!targetless_sanitized.unregister_requested);");',
        'try expectContains(driver, "try std.testing.expect(targetless_sanitized.keeps_live_notifier_execution_out_of_scope);");',
        'try expectContains(boundary, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge");',
        'try expectContains(boundary, "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable");',
        'try expectContains(boundary, "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.");',
        'try expectContains(boundary, "the literal-fallback helpers keep the targetless sysrq path without notifier, the sanitized registered-but-targetless sysrq path, and the non-kernel sysrq literal fallback explicit");',
        'try expectContains(companion, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`");',
        'try expectContains(companion, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");',
        'try expectContains(companion, "standalone targetless-unregister witness");',
        'try expectContains(companion, "separate failure-mode replay");',
        'try expectContains(survey, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`");',
        'try expectContains(survey, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");',
        'try expectContains(survey, "standalone targetless-unregister witness pair likewise stays");',
        'try expectContains(survey, "without promoting itself into the shared three-entry build inventory");',
        'try expectContains(matrix, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`");',
        'try expectContains(matrix, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");',
        'try expectContains(matrix, "witness shard now rereads the live starter and the boundary note together");',
        'try expectContains(matrix, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet");',
    ),
    WITNESS_BUILD_PATH: (
        '.root_source_file = b.path("phase11_hvc_targetless_unregister_gap.zig"),',
        '.name = "phase11-hvc-targetless-unregister-gap",',
        'const test_step = b.step("test", "Run the focused Phase 11 HVC targetless-unregister gap witness.");',
    ),
}

FIXTURE_TEXT = {
    WORKFLOW_PATH: "\n".join(
        (
            "jobs:",
            "  bootstrap:",
            "    steps:",
            f"      - name: {PHASE11_VALIDATE_STEP}",
            f"        run: {PHASE11_VALIDATE_COMMAND}",
        )
    )
    + "\n",
    LANE_NOTE_PATH: "\n".join(("## sequencing", *FILE_EXPECTATIONS[LANE_NOTE_PATH])) + "\n",
    CLEANUP_COMPANION_PATH: "\n".join(("## companion", *FILE_EXPECTATIONS[CLEANUP_COMPANION_PATH])) + "\n",
    VALIDATION_MATRIX_PATH: "\n".join(("## matrix", *FILE_EXPECTATIONS[VALIDATION_MATRIX_PATH])) + "\n",
    SURVEY_PATH: "\n".join(("## survey", *FILE_EXPECTATIONS[SURVEY_PATH])) + "\n",
    VERIFY_BOUNDARY_PATH: "\n".join(("## boundary", *FILE_EXPECTATIONS[VERIFY_BOUNDARY_PATH])) + "\n",
    DRIVER_PATH: "\n".join(FILE_EXPECTATIONS[DRIVER_PATH]) + "\n",
    CLEANUP_CHECKER_PATH: "\n".join(
        ("## cleanup checker", *FILE_EXPECTATIONS[CLEANUP_CHECKER_PATH], "PHASE11_HVC_CLEANUP_CURRENT_HEAD=pass")
    )
    + "\n",
    VALIDATE_PHASE11_PATH: "\n".join(("## validate", *FILE_EXPECTATIONS[VALIDATE_PHASE11_PATH])) + "\n",
    MAKEFILE_PATH: "\n".join(
        (
            "phase11-validate:",
            "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
        )
    )
    + "\n",
    WITNESS_PATH: "\n".join(FILE_EXPECTATIONS[WITNESS_PATH]) + "\n",
    WITNESS_BUILD_PATH: "\n".join(FILE_EXPECTATIONS[WITNESS_BUILD_PATH]) + "\n",
    SELF_PATH: "## self\n",
}


class ValidationError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {relative_path}") from exc


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_packet_files(root: Path) -> None:
    missing = [path for path in REQUIRED_PACKET_FILES if not (root / path).is_file()]
    if missing:
        raise ValidationError(
            "missing required Phase 11 HVC targetless-unregister witness packet files: "
            + ", ".join(missing)
        )


def require_fragments(root: Path) -> None:
    for relative_path, fragments in FILE_EXPECTATIONS.items():
        text = read_text(root, relative_path)
        for fragment in fragments:
            if fragment not in text:
                raise ValidationError(
                    f"{relative_path} is missing required fragment: {fragment!r}"
                )


def require_inventory(root: Path) -> None:
    try:
        inventory = json.loads(read_text(root, INVENTORY_PATH))
    except json.JSONDecodeError as exc:
        raise ValidationError(
            "zigux/tests/fixtures/phase11_build_inventory.json is not valid JSON"
        ) from exc

    exact_current_checks = inventory.get("exact_current_checks")
    if not isinstance(exact_current_checks, list):
        raise ValidationError(
            "phase11_build_inventory.json must keep exact_current_checks as a JSON array"
        )
    for command in (
        CLEANUP_SELF_TEST_COMMAND,
        CLEANUP_COMMAND,
        TARGETLESS_WITNESS_SELF_TEST_COMMAND,
        TARGETLESS_WITNESS_COMMAND,
        REQUIRED_COMMAND,
    ):
        if command not in exact_current_checks:
            raise ValidationError(
                f"phase11_build_inventory.json must keep {command!r} in exact_current_checks"
            )

    workflow_steps = inventory.get("workflow_phase11_steps")
    if not isinstance(workflow_steps, list):
        raise ValidationError(
            "phase11_build_inventory.json must keep workflow_phase11_steps as a JSON array"
        )
    required_step = {"name": PHASE11_VALIDATE_STEP, "run": PHASE11_VALIDATE_COMMAND}
    if required_step not in workflow_steps:
        raise ValidationError(
            "phase11_build_inventory.json must keep the targetless-unregister witness workflow step explicit"
        )

    build_test_names = inventory.get("build_test_names")
    if isinstance(build_test_names, list) and TARGETLESS_WITNESS_TEST_NAME in build_test_names:
        raise ValidationError(
            "phase11_build_inventory.json must keep the targetless-unregister witness outside build_test_names"
        )

    shared_adjunct_replays = inventory.get("shared_adjunct_replays")
    if isinstance(shared_adjunct_replays, list) and TARGETLESS_WITNESS_REPLAY in shared_adjunct_replays:
        raise ValidationError(
            "phase11_build_inventory.json must keep the targetless-unregister witness outside shared_adjunct_replays"
        )

    shared_adjunct_build_replays = inventory.get("shared_adjunct_build_replays")
    if isinstance(shared_adjunct_build_replays, list) and TARGETLESS_WITNESS_BUILD_REPLAY in shared_adjunct_build_replays:
        raise ValidationError(
            "phase11_build_inventory.json must keep the targetless-unregister witness outside shared_adjunct_build_replays"
        )


def validate(root: Path) -> None:
    require_packet_files(root)
    require_fragments(root)
    require_inventory(root)


def build_fixture(root: Path) -> None:
    for relative_path in REQUIRED_PACKET_FILES:
        write_text(root, relative_path, FIXTURE_TEXT.get(relative_path, "placeholder\n"))

    inventory = {
        "build_test_names": [
            "phase11-hvc-hv-ops-layout-proof-tests",
            "phase11-hvc-export-surface-layout-proof-tests",
            "phase11-hvc-cleanup-packet-proof",
        ],
        "exact_current_checks": [
            CLEANUP_SELF_TEST_COMMAND,
            CLEANUP_COMMAND,
            TARGETLESS_WITNESS_SELF_TEST_COMMAND,
            TARGETLESS_WITNESS_COMMAND,
            REQUIRED_COMMAND,
        ],
        "workflow_phase11_steps": [
            {"name": PHASE11_VALIDATE_STEP, "run": PHASE11_VALIDATE_COMMAND},
        ],
        "shared_adjunct_replays": [
            "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
            "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
            "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
        ],
        "shared_adjunct_build_replays": [
            "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
            "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
            "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
        ],
    }
    write_text(root, INVENTORY_PATH, json.dumps(inventory, indent=2, sort_keys=True) + "\n")


def expect_failure(root: Path, mutate: callable, fragment: str) -> None:
    mutate(root)
    try:
        validate(root)
    except ValidationError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase11-hvc-targetless-witness-"))
    cases = 0
    try:
        fixture = temp_dir / "fixture"
        build_fixture(fixture)
        validate(fixture)
        cases += 1

        mutations = (
            (
                LANE_NOTE_PATH,
                VERIFY_BOUNDARY_PATH,
            ),
            (
                LANE_NOTE_PATH,
                DRIVER_PATH,
            ),
            (
                CLEANUP_COMPANION_PATH,
                VERIFY_BOUNDARY_PATH,
            ),
            (
                CLEANUP_COMPANION_PATH,
                CLEANUP_CHECKER_PATH,
            ),
            (
                CLEANUP_COMPANION_PATH,
                SELF_PATH,
            ),
            (
                CLEANUP_COMPANION_PATH,
                WITNESS_PATH,
            ),
            (
                CLEANUP_COMPANION_PATH,
                WITNESS_BUILD_PATH,
            ),
            (
                CLEANUP_COMPANION_PATH,
                "standalone targetless-unregister witness",
            ),
            (
                CLEANUP_COMPANION_PATH,
                "separate failure-mode replay",
            ),
            (
                CLEANUP_COMPANION_PATH,
                "build-inventory checker",
            ),
            (
                CLEANUP_COMPANION_PATH,
                "shared inventory-backed proof routes",
            ),
            (
                VALIDATION_MATRIX_PATH,
                VERIFY_BOUNDARY_PATH,
            ),
            (
                VALIDATION_MATRIX_PATH,
                CLEANUP_COMPANION_PATH,
            ),
            (
                VALIDATION_MATRIX_PATH,
                CLEANUP_CHECKER_PATH,
            ),
            (
                VALIDATION_MATRIX_PATH,
                "scripts/zigux/check-phase11-build-inventory.py",
            ),
            (
                VALIDATION_MATRIX_PATH,
                SELF_PATH,
            ),
            (
                VALIDATION_MATRIX_PATH,
                INVENTORY_PATH,
            ),
            (
                VALIDATION_MATRIX_PATH,
                WITNESS_PATH,
            ),
            (
                VALIDATION_MATRIX_PATH,
                WITNESS_BUILD_PATH,
            ),
            (
                VALIDATION_MATRIX_PATH,
                "make -C zigux phase11-validate",
            ),
            (
                VALIDATION_MATRIX_PATH,
                "witness shard now rereads the live starter and the boundary note together",
            ),
            (
                VALIDATION_MATRIX_PATH,
                "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet",
            ),
            (
                SURVEY_PATH,
                CLEANUP_COMPANION_PATH,
            ),
            (
                SURVEY_PATH,
                CLEANUP_CHECKER_PATH,
            ),
            (
                SURVEY_PATH,
                "scripts/zigux/check-phase11-build-inventory.py",
            ),
            (
                SURVEY_PATH,
                INVENTORY_PATH,
            ),
            (
                SURVEY_PATH,
                SELF_PATH,
            ),
            (
                SURVEY_PATH,
                WITNESS_PATH,
            ),
            (
                SURVEY_PATH,
                WITNESS_BUILD_PATH,
            ),
            (
                SURVEY_PATH,
                "standalone targetless-unregister witness pair likewise stays",
            ),
            (
                SURVEY_PATH,
                "without promoting itself into the shared three-entry build inventory",
            ),
            (
                VERIFY_BOUNDARY_PATH,
                "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge",
            ),
            (
                VERIFY_BOUNDARY_PATH,
                "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable",
            ),
            (
                VERIFY_BOUNDARY_PATH,
                "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.",
            ),
            (
                VERIFY_BOUNDARY_PATH,
                "the literal-fallback helpers keep the targetless sysrq path without notifier, the sanitized registered-but-targetless sysrq path, and the non-kernel sysrq literal fallback explicit",
            ),
            (
                DRIVER_PATH,
                "targetless_no_unregister_edge: bool,",
            ),
            (
                DRIVER_PATH,
                "targetless_unregister_request_sanitized: bool,",
            ),
            (
                DRIVER_PATH,
                "keeps_live_notifier_execution_out_of_scope: bool,",
            ),
            (
                CLEANUP_CHECKER_PATH,
                "check-phase11-hvc-targetless-unregister-witness.py",
            ),
            (
                CLEANUP_CHECKER_PATH,
                "phase11_hvc_targetless_unregister_gap_build.zig",
            ),
            (
                WITNESS_PATH,
                'try expectContains(companion, "separate failure-mode replay");',
            ),
            (
                WITNESS_PATH,
                'try expectContains(survey, "standalone targetless-unregister witness pair likewise stays");',
            ),
            (
                WITNESS_PATH,
                'try expectContains(survey, "without promoting itself into the shared three-entry build inventory");',
            ),
            (
                WITNESS_PATH,
                f'const matrix = try readRepoFile("{VALIDATION_MATRIX_PATH}");',
            ),
            (
                WITNESS_PATH,
                'try expectContains(matrix, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`");',
            ),
            (
                WITNESS_PATH,
                'try expectContains(matrix, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet");',
            ),
            (
                WITNESS_PATH,
                'try expectContains(matrix, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");',
            ),
            (
                WITNESS_BUILD_PATH,
                '.name = "phase11-hvc-targetless-unregister-gap",',
            ),
            (
                VALIDATE_PHASE11_PATH,
                WITNESS_PATH,
            ),
            (
                VALIDATE_PHASE11_PATH,
                WITNESS_BUILD_PATH,
            ),
            (
                VALIDATE_PHASE11_PATH,
                '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test"),',
            ),
            (
                VALIDATE_PHASE11_PATH,
                '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"),',
            ),
            (
                VALIDATE_PHASE11_PATH,
                "phase11-hvc-targetless-unregister-gap-build",
            ),
            (
                MAKEFILE_PATH,
                "phase11_hvc_targetless_unregister_gap_build.zig",
            ),
        )

        for index, (relative_path, fragment) in enumerate(mutations, start=1):
            broken = temp_dir / f"broken_{index:02d}"
            shutil.copytree(fixture, broken, dirs_exist_ok=True)
            expect_failure(
                broken,
                lambda root, rel=relative_path, frag=fragment: write_text(
                    root,
                    rel,
                    read_text(root, rel).replace(frag, "", 1),
                ),
                fragment,
            )
            cases += 1

        broken_workflow_step = temp_dir / "broken_workflow_step"
        shutil.copytree(fixture, broken_workflow_step, dirs_exist_ok=True)
        expect_failure(
            broken_workflow_step,
            lambda root: write_text(
                root,
                WORKFLOW_PATH,
                read_text(root, WORKFLOW_PATH).replace(PHASE11_VALIDATE_STEP, "", 1),
            ),
            PHASE11_VALIDATE_STEP,
        )
        cases += 1

        broken_workflow_marker = temp_dir / "broken_workflow_marker"
        shutil.copytree(fixture, broken_workflow_marker, dirs_exist_ok=True)
        expect_failure(
            broken_workflow_marker,
            lambda root: write_text(
                root,
                WORKFLOW_PATH,
                read_text(root, WORKFLOW_PATH).replace(PHASE11_VALIDATE_COMMAND, "", 1),
            ),
            PHASE11_VALIDATE_COMMAND,
        )
        cases += 1

        broken_inventory = temp_dir / "broken_inventory"
        shutil.copytree(fixture, broken_inventory, dirs_exist_ok=True)

        def mutate_inventory_missing_check(root: Path) -> None:
            payload = json.loads(read_text(root, INVENTORY_PATH))
            payload["exact_current_checks"] = [REQUIRED_COMMAND]
            write_text(root, INVENTORY_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n")

        expect_failure(
            broken_inventory,
            mutate_inventory_missing_check,
            "exact_current_checks",
        )
        cases += 1

        broken_workflow = temp_dir / "broken_workflow"
        shutil.copytree(fixture, broken_workflow, dirs_exist_ok=True)

        def mutate_inventory_missing_step(root: Path) -> None:
            payload = json.loads(read_text(root, INVENTORY_PATH))
            payload["workflow_phase11_steps"] = [{"name": "other", "run": "other"}]
            write_text(root, INVENTORY_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n")

        expect_failure(
            broken_workflow,
            mutate_inventory_missing_step,
            "workflow step explicit",
        )
        cases += 1

        broken_inventory_build_test_names = temp_dir / "broken_inventory_build_test_names"
        shutil.copytree(fixture, broken_inventory_build_test_names, dirs_exist_ok=True)

        def mutate_inventory_build_test_names(root: Path) -> None:
            payload = json.loads(read_text(root, INVENTORY_PATH))
            payload["build_test_names"].append(TARGETLESS_WITNESS_TEST_NAME)
            write_text(root, INVENTORY_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n")

        expect_failure(
            broken_inventory_build_test_names,
            mutate_inventory_build_test_names,
            "outside build_test_names",
        )
        cases += 1

        broken_inventory_adjunct_replays = temp_dir / "broken_inventory_adjunct_replays"
        shutil.copytree(fixture, broken_inventory_adjunct_replays, dirs_exist_ok=True)

        def mutate_inventory_adjunct_replays(root: Path) -> None:
            payload = json.loads(read_text(root, INVENTORY_PATH))
            payload["shared_adjunct_replays"].append(TARGETLESS_WITNESS_REPLAY)
            write_text(root, INVENTORY_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n")

        expect_failure(
            broken_inventory_adjunct_replays,
            mutate_inventory_adjunct_replays,
            "outside shared_adjunct_replays",
        )
        cases += 1

        broken_inventory_adjunct_build_replays = temp_dir / "broken_inventory_adjunct_build_replays"
        shutil.copytree(fixture, broken_inventory_adjunct_build_replays, dirs_exist_ok=True)

        def mutate_inventory_adjunct_build_replays(root: Path) -> None:
            payload = json.loads(read_text(root, INVENTORY_PATH))
            payload["shared_adjunct_build_replays"].append(TARGETLESS_WITNESS_BUILD_REPLAY)
            write_text(root, INVENTORY_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n")

        expect_failure(
            broken_inventory_adjunct_build_replays,
            mutate_inventory_adjunct_build_replays,
            "outside shared_adjunct_build_replays",
        )
        cases += 1

        broken_json = temp_dir / "broken_json"
        shutil.copytree(fixture, broken_json, dirs_exist_ok=True)
        expect_failure(
            broken_json,
            lambda root: write_text(root, INVENTORY_PATH, "{not json}\n"),
            "is not valid JSON",
        )
        cases += 1

        missing_file = temp_dir / "missing_file"
        shutil.copytree(fixture, missing_file, dirs_exist_ok=True)
        expect_failure(
            missing_file,
            lambda root: (root / WITNESS_PATH).unlink(),
            "missing required Phase 11 HVC targetless-unregister witness packet files",
        )
        cases += 1
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS_SELF_TEST=pass")
    print(f"PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS_SELF_TEST_CASE_COUNT={cases}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the Phase 11 HVC targetless-unregister witness packet for drift."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to the Zigux repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in fixture cases instead of validating a repository checkout.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    try:
        validate(Path(args.repo_root).resolve())
    except ValidationError as exc:
        print(f"PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=fail: {exc}")
        return 1

    print("PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass")
    print(f"PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS_REQUIRED_FILE_COUNT={len(REQUIRED_PACKET_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 HVC targetless-unregister witness packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


REQUIRED_COMMAND = "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"
REQUIRED_STEP_NAME = "Run current Phase 11 HVC targetless-unregister gap witness"
PHASE11_VALIDATE_COMMAND = "make -C zigux phase11-validate"
PHASE11_VALIDATE_STEP = "Validate current Phase 11 support bundle"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
LANE_NOTE_PATH = "Documentation/zigux/phase11-driver-lane-sequencing.md"
CLEANUP_COMPANION_PATH = "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"
VALIDATION_MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
SURVEY_PATH = "Documentation/zigux/phase11-hvc-console-survey.md"
VERIFY_BOUNDARY_PATH = "Documentation/zigux/phase11-hvc-verify-helper-boundary.md"
DRIVER_PATH = "drivers/tty/hvc/hvc_console.zig"
CLEANUP_CHECKER_PATH = "scripts/zigux/check-phase11-hvc-cleanup-current-head.py"
CLEANUP_SELF_TEST_COMMAND = "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test"
CLEANUP_COMMAND = "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py"
CLEANUP_SELF_TEST_STEP = "Self-test current Phase 11 HVC cleanup current-head checker"
CLEANUP_STEP = "Check current Phase 11 HVC cleanup current-head packet"
VALIDATE_PHASE11_PATH = "scripts/zigux/validate-phase11.py"
MAKEFILE_PATH = "zigux/Makefile"
INVENTORY_PATH = "zigux/tests/fixtures/phase11_build_inventory.json"
WITNESS_PATH = "zigux/tests/phase11_hvc_targetless_unregister_gap.zig"
WITNESS_BUILD_PATH = "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"
SELF_PATH = "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"


@dataclass(frozen=True)
class FileExpectation:
    relative_path: str
    required_fragments: tuple[str, ...]


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

FILE_EXPECTATIONS = (
    FileExpectation(
        WORKFLOW_PATH,
        (
            PHASE11_VALIDATE_STEP,
            PHASE11_VALIDATE_COMMAND,
        ),
    ),
    FileExpectation(
        LANE_NOTE_PATH,
        (
            CLEANUP_COMPANION_PATH,
            CLEANUP_CHECKER_PATH,
            SELF_PATH,
            WITNESS_PATH,
            WITNESS_BUILD_PATH,
        ),
    ),
    FileExpectation(
        CLEANUP_COMPANION_PATH,
        (
            CLEANUP_CHECKER_PATH,
            SELF_PATH,
            WITNESS_PATH,
            WITNESS_BUILD_PATH,
        ),
    ),
    FileExpectation(
        VALIDATION_MATRIX_PATH,
        (
            CLEANUP_COMPANION_PATH,
            CLEANUP_CHECKER_PATH,
            SELF_PATH,
            WITNESS_PATH,
            WITNESS_BUILD_PATH,
            "make -C zigux phase11-validate",
        ),
    ),
    FileExpectation(
        SURVEY_PATH,
        (
            CLEANUP_COMPANION_PATH,
            CLEANUP_CHECKER_PATH,
            SELF_PATH,
            WITNESS_PATH,
            WITNESS_BUILD_PATH,
            "standalone targetless-unregister witness pair",
        ),
    ),
    FileExpectation(
        VERIFY_BOUNDARY_PATH,
        (
            "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge",
            "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable",
            "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.",
            "the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit",
        ),
    ),
    FileExpectation(
        DRIVER_PATH,
        (
            "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
            "targetless_no_unregister_edge: bool,",
            "targetless_unregister_request_sanitized: bool,",
            ".targetless_no_unregister_edge = request.notifier_registered and !request.target_present and !request.unregister_requested,",
            ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,",
            ".unregister_requested = request.unregister_requested and request.target_present and request.notifier_registered,",
            'test "phase11 hvc console keeps targetless notifier no-unregister edge reviewable" {',
            "try std.testing.expect(targetless_sanitized.targetless_unregister_request_sanitized);",
            'test "phase11 hvc console keeps unregistered targeted notifier-unregister request sanitized" {',
        ),
    ),
    FileExpectation(
        CLEANUP_CHECKER_PATH,
        (
            "check-phase11-hvc-targetless-unregister-witness.py",
            "phase11_hvc_targetless_unregister_gap_build.zig",
        ),
    ),
    FileExpectation(
        VALIDATE_PHASE11_PATH,
        (
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
    ),
    FileExpectation(
        MAKEFILE_PATH,
        (
            "phase11-validate:",
            "phase11_hvc_targetless_unregister_gap_build.zig",
        ),
    ),
    FileExpectation(
        WITNESS_PATH,
        (
            'test "phase11 hvc notifier witness records current-head targetless unregister sanitizer" {',
            f'const driver = try readRepoFile("{DRIVER_PATH}");',
            f'const boundary = try readRepoFile("{VERIFY_BOUNDARY_PATH}");',
            'try expectContains(driver, "targetless_no_unregister_edge: bool,");',
            'try expectContains(driver, ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,");',
            'try expectContains(boundary, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge");',
            'try expectContains(boundary, "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable");',
            'try expectContains(matrix, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet");',
        ),
    ),
    FileExpectation(
        WITNESS_BUILD_PATH,
        (
            '.root_source_file = b.path("phase11_hvc_targetless_unregister_gap.zig"),',
            '.name = "phase11-hvc-targetless-unregister-gap",',
            'const test_step = b.step("test", "Run the focused Phase 11 HVC targetless-unregister gap witness.");',
        ),
    ),
)


class ValidationError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {relative_path}") from exc


def require_packet_files(root: Path) -> None:
    missing = [path for path in REQUIRED_PACKET_FILES if not (root / path).is_file()]
    if missing:
        raise ValidationError(
            "missing required Phase 11 HVC targetless-unregister witness packet files: "
            + ", ".join(missing)
        )


def require_fragments(root: Path) -> None:
    for expectation in FILE_EXPECTATIONS:
        text = read_text(root, expectation.relative_path)
        for fragment in expectation.required_fragments:
            if fragment not in text:
                raise ValidationError(
                    f"{expectation.relative_path} is missing required fragment: {fragment!r}"
                )


def require_inventory(root: Path) -> None:
    inventory_text = read_text(root, INVENTORY_PATH)
    try:
        inventory = json.loads(inventory_text)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            "zigux/tests/fixtures/phase11_build_inventory.json is not valid JSON"
        ) from exc

    exact_current_checks = inventory.get("exact_current_checks")
    if not isinstance(exact_current_checks, list):
        raise ValidationError(
            "phase11_build_inventory.json must keep exact_current_checks as a JSON array"
        )
    for command in (CLEANUP_SELF_TEST_COMMAND, CLEANUP_COMMAND, REQUIRED_COMMAND):
        if command not in exact_current_checks:
            raise ValidationError(
                f"phase11_build_inventory.json must keep {command!r} in exact_current_checks"
            )

    workflow_steps = inventory.get("workflow_phase11_steps")
    if not isinstance(workflow_steps, list):
        raise ValidationError(
            "phase11_build_inventory.json must keep workflow_phase11_steps as a JSON array"
        )

    required_steps = (
        {"name": PHASE11_VALIDATE_STEP, "run": PHASE11_VALIDATE_COMMAND},
    )
    for required_step in required_steps:
        if required_step not in workflow_steps:
            raise ValidationError(
                "phase11_build_inventory.json must keep the targetless-unregister witness workflow step explicit"
            )


def validate(root: Path) -> None:
    require_packet_files(root)
    require_fragments(root)
    require_inventory(root)


def write_text(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture(root: Path) -> None:
    for relative_path in REQUIRED_PACKET_FILES:
        write_text(root, relative_path, "placeholder\n")

    write_text(
        root,
        WORKFLOW_PATH,
        "\n".join(
            (
                "jobs:",
                "  bootstrap:",
                "    steps:",
                f"      - name: {PHASE11_VALIDATE_STEP}",
                f"        run: {PHASE11_VALIDATE_COMMAND}",
            )
        )
        + "\n",
    )
    write_text(
        root,
        LANE_NOTE_PATH,
        "\n".join(
            (
                "# sequencing",
                CLEANUP_COMPANION_PATH,
                CLEANUP_CHECKER_PATH,
                SELF_PATH,
                WITNESS_PATH,
                WITNESS_BUILD_PATH,
            )
        )
        + "\n",
    )
    write_text(
        root,
        CLEANUP_COMPANION_PATH,
        "\n".join(
            (
                "# companion",
                CLEANUP_CHECKER_PATH,
                SELF_PATH,
                WITNESS_PATH,
                WITNESS_BUILD_PATH,
            )
        )
        + "\n",
    )
    write_text(
        root,
        VALIDATION_MATRIX_PATH,
        "\n".join(
            (
                "# matrix",
                CLEANUP_COMPANION_PATH,
                CLEANUP_CHECKER_PATH,
                SELF_PATH,
                WITNESS_PATH,
                WITNESS_BUILD_PATH,
                "make -C zigux phase11-validate",
                "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet",
            )
        )
        + "\n",
    )
    write_text(
        root,
        SURVEY_PATH,
        "\n".join(
            (
                "# survey",
                CLEANUP_COMPANION_PATH,
                CLEANUP_CHECKER_PATH,
                SELF_PATH,
                WITNESS_PATH,
                WITNESS_BUILD_PATH,
                "standalone targetless-unregister witness pair",
            )
        )
        + "\n",
    )
    write_text(
        root,
        VERIFY_BOUNDARY_PATH,
        "\n".join(
            (
                "# boundary",
                "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge",
                "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable",
                "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.",
                "the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit",
            )
        )
        + "\n",
    )
    write_text(
        root,
        DRIVER_PATH,
        "\n".join(
            (
                "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
                "targetless_no_unregister_edge: bool,",
                "targetless_unregister_request_sanitized: bool,",
                ".targetless_no_unregister_edge = request.notifier_registered and !request.target_present and !request.unregister_requested,",
                ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,",
                ".unregister_requested = request.unregister_requested and request.target_present and request.notifier_registered,",
                "test \"phase11 hvc console keeps targetless notifier no-unregister edge reviewable\" {",
                "try std.testing.expect(targetless_sanitized.targetless_unregister_request_sanitized);",
                "test \"phase11 hvc console keeps unregistered targeted notifier-unregister request sanitized\" {",
            )
        )
        + "\n",
    )
    write_text(
        root,
        CLEANUP_CHECKER_PATH,
        "\n".join(
            (
                "# cleanup checker",
                "check-phase11-hvc-targetless-unregister-witness.py",
                "phase11_hvc_targetless_unregister_gap_build.zig",
                "PHASE11_HVC_CLEANUP_CURRENT_HEAD=pass",
            )
        )
        + "\n",
    )
    write_text(
        root,
        VALIDATE_PHASE11_PATH,
        "\n".join(
            (
                "# validate",
                CLEANUP_CHECKER_PATH,
                WITNESS_PATH,
                WITNESS_BUILD_PATH,
                "phase11-hvc-cleanup-current-head",
                '"phase11-hvc-targetless-unregister-witness-self-test",',
                '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test"),',
                '"phase11-hvc-targetless-unregister-witness",',
                '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"),',
                "phase11-hvc-targetless-unregister-gap-build",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE_PATH,
        "\n".join(
            (
                "phase11-validate:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
            )
        )
        + "\n",
    )
    write_text(
        root,
        WITNESS_PATH,
        "\n".join(
            (
                "test \"phase11 hvc notifier witness records current-head targetless unregister sanitizer\" {",
                f"const driver = try readRepoFile(\"{DRIVER_PATH}\");",
                f"const boundary = try readRepoFile(\"{VERIFY_BOUNDARY_PATH}\");",
                "try expectContains(driver, \"targetless_no_unregister_edge: bool,\");",
                "try expectContains(driver, \".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,\");",
                "try expectContains(boundary, \"`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge\");",
                "try expectContains(boundary, \"`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable\");",
                "try expectContains(matrix, \"keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet\");",
            )
        )
        + "\n",
    )
    write_text(
        root,
        WITNESS_BUILD_PATH,
        "\n".join(
            (
                ".root_source_file = b.path(\"phase11_hvc_targetless_unregister_gap.zig\"),",
                ".name = \"phase11-hvc-targetless-unregister-gap\",",
                "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC targetless-unregister gap witness.\");",
            )
        )
        + "\n",
    )
    write_text(root, SELF_PATH, "# self\n")

    inventory = {
        "exact_current_checks": [
            CLEANUP_SELF_TEST_COMMAND,
            CLEANUP_COMMAND,
            REQUIRED_COMMAND,
        ],
        "workflow_phase11_steps": [
            {"name": PHASE11_VALIDATE_STEP, "run": PHASE11_VALIDATE_COMMAND},
        ],
    }
    write_text(
        root,
        INVENTORY_PATH,
        json.dumps(inventory, indent=2, sort_keys=True) + "\n",
    )


def run_self_test() -> int:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase11-hvc-targetless-witness-"))
    total_cases = 0
    try:
        make_fixture(temp_dir)
        validate(temp_dir)
        total_cases += 1

        sequencing = temp_dir / LANE_NOTE_PATH
        sequencing.write_text("# sequencing\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected lane sequencing fragment check to fail")

        make_fixture(temp_dir)
        companion = temp_dir / CLEANUP_COMPANION_PATH
        companion.write_text("# companion\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected cleanup companion fragment check to fail")

        make_fixture(temp_dir)
        matrix = temp_dir / VALIDATION_MATRIX_PATH
        matrix.write_text("# matrix\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected validation matrix fragment check to fail")

        make_fixture(temp_dir)
        survey = temp_dir / SURVEY_PATH
        survey.write_text("# survey\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected survey fragment check to fail")

        make_fixture(temp_dir)
        boundary = temp_dir / VERIFY_BOUNDARY_PATH
        boundary.write_text("# boundary\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected verify-boundary fragment check to fail")

        make_fixture(temp_dir)
        driver = temp_dir / DRIVER_PATH
        driver.write_text("# driver\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected driver fragment check to fail")

        make_fixture(temp_dir)
        cleanup_checker = temp_dir / CLEANUP_CHECKER_PATH
        cleanup_checker.write_text("# cleanup checker\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected cleanup checker required-file validation to keep failing via coupled fragments")

        make_fixture(temp_dir)
        witness = temp_dir / WITNESS_PATH
        witness.write_text("# witness\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected witness replay fragment check to fail")

        make_fixture(temp_dir)
        witness_build = temp_dir / WITNESS_BUILD_PATH
        witness_build.write_text("# witness build\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected witness build fragment check to fail")

        make_fixture(temp_dir)
        workflow = temp_dir / WORKFLOW_PATH
        workflow.write_text("jobs:\n  bootstrap:\n    steps:\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected workflow fragment check to fail")

        make_fixture(temp_dir)
        inventory_path = temp_dir / INVENTORY_PATH
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory["exact_current_checks"] = [REQUIRED_COMMAND]
        inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected inventory exact_current_checks validation to fail")

        make_fixture(temp_dir)
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        inventory["workflow_phase11_steps"] = [{"name": REQUIRED_STEP_NAME, "run": REQUIRED_COMMAND}]
        inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected inventory workflow step validation to fail")

        make_fixture(temp_dir)
        inventory_path.write_text("{not json}\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError as exc:
            if "is not valid JSON" not in str(exc):
                raise
            total_cases += 1
        else:
            raise AssertionError("expected invalid inventory JSON validation to fail")

        make_fixture(temp_dir)
        missing_packet_file = temp_dir / WITNESS_PATH
        missing_packet_file.unlink()
        try:
            validate(temp_dir)
        except ValidationError as exc:
            if "missing required Phase 11 HVC targetless-unregister witness packet files" not in str(exc):
                raise
            total_cases += 1
        else:
            raise AssertionError("expected missing packet file validation to fail")

        make_fixture(temp_dir)
        validate_script = temp_dir / VALIDATE_PHASE11_PATH
        validate_script.write_text("# validate\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected validate-phase11 fragment validation to fail")

        make_fixture(temp_dir)
        validate_script = temp_dir / VALIDATE_PHASE11_PATH
        validate_script.write_text(
            read_text(temp_dir, VALIDATE_PHASE11_PATH).replace(
                '"phase11-hvc-targetless-unregister-witness-self-test",', "", 1
            ),
            encoding="utf-8",
        )
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected validate-phase11 witness self-test name validation to fail")

        make_fixture(temp_dir)
        validate_script = temp_dir / VALIDATE_PHASE11_PATH
        validate_script.write_text(
            read_text(temp_dir, VALIDATE_PHASE11_PATH).replace(
                '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test"),',
                "",
                1,
            ),
            encoding="utf-8",
        )
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected validate-phase11 witness self-test command validation to fail")

        make_fixture(temp_dir)
        validate_script = temp_dir / VALIDATE_PHASE11_PATH
        validate_script.write_text(
            read_text(temp_dir, VALIDATE_PHASE11_PATH).replace(
                '"phase11-hvc-targetless-unregister-witness",', "", 1
            ),
            encoding="utf-8",
        )
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected validate-phase11 witness live name validation to fail")

        make_fixture(temp_dir)
        validate_script = temp_dir / VALIDATE_PHASE11_PATH
        validate_script.write_text(
            read_text(temp_dir, VALIDATE_PHASE11_PATH).replace(
                '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"),',
                "",
                1,
            ),
            encoding="utf-8",
        )
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected validate-phase11 witness live command validation to fail")

        make_fixture(temp_dir)
        makefile = temp_dir / MAKEFILE_PATH
        makefile.write_text("phase11-validate:\n", encoding="utf-8")
        try:
            validate(temp_dir)
        except ValidationError:
            total_cases += 1
        else:
            raise AssertionError("expected Makefile witness route validation to fail")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print("PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS_SELF_TEST=pass")
    print(f"PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS_SELF_TEST_CASE_COUNT={total_cases}")
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

#!/usr/bin/env python3
"""Fail-closed checker for Phase 11 validator-check bundle parity."""

from __future__ import annotations

import argparse
import ast
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 3 else Path.cwd()
VALIDATE_PHASE11_PATH = Path("scripts/zigux/validate-phase11.py")
BUILD_INVENTORY_CHECKER_PATH = Path("scripts/zigux/check-phase11-build-inventory.py")


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def parse_module(path: Path) -> ast.Module:
    try:
        return ast.parse(read_text(path), filename=str(path))
    except SyntaxError as exc:
        raise CheckError(f"invalid Python syntax in {path}: {exc}") from exc


def find_assignment(module: ast.Module, name: str) -> ast.AST:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return node.value
    raise CheckError(f"missing assignment: {name}")


def extract_validate_checks(path: Path) -> list[tuple[str, ...]]:
    value = find_assignment(parse_module(path), "CHECKS")
    if not isinstance(value, ast.Tuple):
        raise CheckError("CHECKS is not a tuple")
    commands: list[tuple[str, ...]] = []
    for element in value.elts:
        if not isinstance(element, ast.Call) or not element.args:
            raise CheckError("CHECKS contains a non-CheckSpec entry")
        command_expr = element.args[-1]
        try:
            command = ast.literal_eval(command_expr)
        except (SyntaxError, ValueError) as exc:
            raise CheckError("CHECKS contains a non-literal command tuple") from exc
        if (
            not isinstance(command, tuple)
            or not command
            or any(not isinstance(item, str) for item in command)
        ):
            raise CheckError("CHECKS contains an invalid command tuple")
        commands.append(command)
    return commands


def extract_required_markers(path: Path) -> list[tuple[str, ...]]:
    value = find_assignment(parse_module(path), "REQUIRED_VALIDATE_PHASE11_MARKERS")
    if not isinstance(value, ast.Tuple):
        raise CheckError("REQUIRED_VALIDATE_PHASE11_MARKERS is not a tuple")
    markers: list[tuple[str, ...]] = []
    for element in value.elts:
        try:
            marker = ast.literal_eval(element)
            command = ast.literal_eval(marker)
        except (SyntaxError, ValueError) as exc:
            raise CheckError("REQUIRED_VALIDATE_PHASE11_MARKERS contains a non-literal tuple marker") from exc
        if (
            not isinstance(command, tuple)
            or not command
            or any(not isinstance(item, str) for item in command)
        ):
            raise CheckError("REQUIRED_VALIDATE_PHASE11_MARKERS contains an invalid command tuple")
        markers.append(command)
    return markers


def run_check(root: Path) -> None:
    validate_checks = extract_validate_checks(root / VALIDATE_PHASE11_PATH)
    required_markers = extract_required_markers(root / BUILD_INVENTORY_CHECKER_PATH)
    if validate_checks[0] != ("python", "scripts/zigux/validate-phase11.py", "--self-test"):
        raise CheckError("validate-phase11.py no longer starts with its own self-test replay")
    if validate_checks != required_markers:
        raise CheckError("build-inventory validate marker bundle does not match validate-phase11.py CHECKS")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


FIXTURE_VALIDATE_TEXT = """\
from dataclasses import dataclass

@dataclass(frozen=True)
class CheckSpec:
    name: str
    command: tuple[str, ...]

CHECKS = (
    CheckSpec("phase11-validation-self-test", ("python", "scripts/zigux/validate-phase11.py", "--self-test")),
    CheckSpec("phase11-build-inventory-self-test", ("python", "scripts/zigux/check-phase11-build-inventory.py", "--self-test")),
    CheckSpec("phase11-build-inventory", ("python", "scripts/zigux/check-phase11-build-inventory.py")),
    CheckSpec("phase11-focused-direct-build-replays-self-test", ("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py", "--self-test")),
    CheckSpec("phase11-focused-direct-build-replays", ("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py")),
    CheckSpec("phase11-shared-replay-contract-counts-self-test", ("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py", "--self-test")),
    CheckSpec("phase11-shared-replay-contract-counts", ("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py")),
    CheckSpec("phase11-matrix-gap-survey-self-test", ("python", "scripts/zigux/check-phase11-matrix-gap-survey.py", "--self-test")),
    CheckSpec("phase11-matrix-gap-survey", ("python", "scripts/zigux/check-phase11-matrix-gap-survey.py")),
    CheckSpec("phase11-validation-matrix-gap-survey-self-test", ("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py", "--self-test")),
    CheckSpec("phase11-validation-matrix-gap-survey", ("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py")),
    CheckSpec("phase11-header-boundary-packet-self-test", ("python", "scripts/zigux/check-phase11-header-boundary-packet.py", "--self-test")),
    CheckSpec("phase11-header-boundary-packet", ("python", "scripts/zigux/check-phase11-header-boundary-packet.py")),
    CheckSpec("phase11-hvc-cleanup-current-head-self-test", ("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py", "--self-test")),
    CheckSpec("phase11-hvc-cleanup-current-head", ("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py")),
    CheckSpec("phase11-hvc-targetless-unregister-witness-self-test", ("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test")),
    CheckSpec("phase11-hvc-targetless-unregister-witness", ("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py")),
    CheckSpec("phase11-dw-wdt-teardown-packet-self-test", ("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py", "--self-test")),
    CheckSpec("phase11-dw-wdt-teardown-packet", ("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py")),
    CheckSpec("phase11-dw-wdt-verify-alignment-self-test", ("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py", "--self-test")),
    CheckSpec("phase11-dw-wdt-verify-alignment", ("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py")),
    CheckSpec("phase11-bcm2835-wdt-manifest-packet-survey-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig")),
    CheckSpec("phase11-dw-wdt-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_build.zig")),
    CheckSpec("phase11-dw-wdt-restart-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_restart_build.zig")),
    CheckSpec("phase11-dw-wdt-pm-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_pm_build.zig")),
    CheckSpec("phase11-gpio-wdt-preflight-review-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig")),
    CheckSpec("phase11-gpio-wdt-register-device-glue-review-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig")),
    CheckSpec("phase11-gpio-wdt-nowayout-policy-review-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig")),
    CheckSpec("phase11-hvc-hv-ops-layout-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_hv_ops_layout_build.zig")),
    CheckSpec("phase11-hvc-export-surface-layout-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_export_surface_layout_build.zig")),
    CheckSpec("phase11-hvc-cleanup-packet-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_cleanup_packet_build.zig")),
    CheckSpec("phase11-hvc-modem-control-proof-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_modem_control_proof_build.zig")),
    CheckSpec("phase11-hvc-targetless-unregister-gap-build", ("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig")),
)
"""


FIXTURE_MARKERS_TEXT = """\
REQUIRED_VALIDATE_PHASE11_MARKERS = (
    '("python", "scripts/zigux/validate-phase11.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-build-inventory.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-build-inventory.py")',
    '("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-focused-direct-build-replays.py")',
    '("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py")',
    '("python", "scripts/zigux/check-phase11-matrix-gap-survey.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-matrix-gap-survey.py")',
    '("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py")',
    '("python", "scripts/zigux/check-phase11-header-boundary-packet.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-header-boundary-packet.py")',
    '("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py")',
    '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py")',
    '("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py")',
    '("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_restart_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_pm_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_hv_ops_layout_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_export_surface_layout_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_cleanup_packet_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_modem_control_proof_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig")',
)
"""


def build_fixture(root: Path) -> None:
    write(root / VALIDATE_PHASE11_PATH, FIXTURE_VALIDATE_TEXT)
    write(root / BUILD_INVENTORY_CHECKER_PATH, FIXTURE_MARKERS_TEXT)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_validate_check_bundle_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_marker = tmpdir / "missing_marker"
        shutil.copytree(fixture, missing_marker, dirs_exist_ok=True)
        write(
            missing_marker / BUILD_INVENTORY_CHECKER_PATH,
            read_text(missing_marker / BUILD_INVENTORY_CHECKER_PATH).replace(
                '\'("python", "scripts/zigux/check-phase11-header-boundary-packet.py")\',\n',
                "",
                1,
            ),
        )
        expect_failure(missing_marker, "does not match")
        case_count += 1

        reordered_marker = tmpdir / "reordered_marker"
        shutil.copytree(fixture, reordered_marker, dirs_exist_ok=True)
        write(
            reordered_marker / BUILD_INVENTORY_CHECKER_PATH,
            read_text(reordered_marker / BUILD_INVENTORY_CHECKER_PATH).replace(
                '\'("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_modem_control_proof_build.zig")\',\n'
                '    \'("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig")\',\n',
                '    \'("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig")\',\n'
                '    \'("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_modem_control_proof_build.zig")\',\n',
                1,
            ),
        )
        expect_failure(reordered_marker, "does not match")
        case_count += 1

        missing_self_test = tmpdir / "missing_self_test"
        shutil.copytree(fixture, missing_self_test, dirs_exist_ok=True)
        write(
            missing_self_test / VALIDATE_PHASE11_PATH,
            read_text(missing_self_test / VALIDATE_PHASE11_PATH).replace(
                'CheckSpec("phase11-validation-self-test", ("python", "scripts/zigux/validate-phase11.py", "--self-test")),\n',
                "",
                1,
            ),
        )
        expect_failure(missing_self_test, "no longer starts with its own self-test replay")
        case_count += 1

        print("PHASE11_VALIDATE_CHECK_BUNDLE_SELF_TEST=pass")
        print(f"PHASE11_VALIDATE_CHECK_BUNDLE_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_VALIDATE_CHECK_BUNDLE=fail: {exc}")
        return 1

    print("PHASE11_VALIDATE_CHECK_BUNDLE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

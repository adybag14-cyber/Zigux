#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 exact validate-check roster."""

from __future__ import annotations

import argparse
import ast
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else Path.cwd()
VALIDATE_PATH = Path("scripts/zigux/validate-phase11.py")
FIXTURE_PATH = Path("zigux/tests/fixtures/phase11_validate_checks.json")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
SELF_CHECK_PATH = "scripts/zigux/check-phase11-validate-check-roster.py"
SELF_FIXTURE_PATH = "zigux/tests/fixtures/phase11_validate_checks.json"
DW_WDT_BUILD_ROUTE_CHECK_PATH = "scripts/zigux/check-phase11-dw-wdt-build-route.py"
DW_WDT_BUILD_INVENTORY_PATH = "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json"
SHARED_TOOLING_CHECK_PATH = "scripts/zigux/check-phase11-shared-tooling-manifest.py"
SHARED_TOOLING_FIXTURE_PATH = "zigux/tests/fixtures/phase11_shared_tooling_manifest.json"
SHARED_TOOLING_SURVEY_PATH = "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md"
EXPECTED_VALIDATE_ROUTE = "make -C zigux phase11-validate"
EXPECTED_VALIDATE_SCRIPT = "scripts/zigux/validate-phase11.py"
EXPECTED_PHASE = "Phase 11"
EXPECTED_LANE_KEY = "P11-L15"
EXPECTED_INVENTORY_DETERMINISTIC_LANE = "P11-L07"
EXPECTED_INVENTORY_DETERMINISTIC_FIXTURE_SURFACES = [
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
]
EXPECTED_FOCUSED_TEARDOWN_FAILURE_MODE_BUILDS = [
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
]
EXPECTED_DETERMINISTIC_GOLDEN_OUTPUT_GAP = (
    "phase11-validate now carries the dedicated golden-output fixture roster "
    "`zigux/tests/fixtures/phase11_validate_checks.json` plus fail-closed "
    "`scripts/zigux/check-phase11-validate-check-roster.py`, "
    "`scripts/zigux/check-phase11-validate-route-alignment.py`, and "
    "`scripts/zigux/check-phase11-dw-wdt-build-route.py` guards while keeping both "
    "`zigux/tests/fixtures/phase11_build_inventory.json` and "
    "`zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json` inside the deterministic validator packet"
)
EXPECTED_REQUIRED_CHECKS = (
    ("phase11-validate-check-roster-self-test", ["python", SELF_CHECK_PATH, "--self-test"]),
    ("phase11-validate-check-roster", ["python", SELF_CHECK_PATH]),
    ("phase11-shared-tooling-manifest-self-test", ["python", SHARED_TOOLING_CHECK_PATH, "--self-test"]),
    ("phase11-shared-tooling-manifest", ["python", SHARED_TOOLING_CHECK_PATH]),
    ("phase11-dw-wdt-build-route-self-test", ["python", DW_WDT_BUILD_ROUTE_CHECK_PATH, "--self-test"]),
    ("phase11-dw-wdt-build-route", ["python", DW_WDT_BUILD_ROUTE_CHECK_PATH]),
)


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError(f"expected object in {path}")
    return value


def assignment_node(module: ast.Module, name: str) -> ast.AST:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return node.value
    raise CheckError(f"missing assignment: {name}")


def literal_assignment(module: ast.Module, name: str) -> object:
    try:
        return ast.literal_eval(assignment_node(module, name))
    except (ValueError, SyntaxError) as exc:
        raise CheckError(f"{name} must be a Python literal") from exc


def parse_checks(node: ast.AST) -> list[dict[str, object]]:
    if not isinstance(node, (ast.Tuple, ast.List)):
        raise CheckError("CHECKS must be a tuple of CheckSpec(...) calls")
    parsed: list[dict[str, object]] = []
    for entry in node.elts:
        if not isinstance(entry, ast.Call):
            raise CheckError("CHECKS entries must be CheckSpec(...) calls")
        if not isinstance(entry.func, ast.Name) or entry.func.id != "CheckSpec":
            raise CheckError("CHECKS entries must call CheckSpec")
        if len(entry.args) != 2:
            raise CheckError("CheckSpec entries must have exactly two positional arguments")
        try:
            name = ast.literal_eval(entry.args[0])
            command = ast.literal_eval(entry.args[1])
        except (ValueError, SyntaxError) as exc:
            raise CheckError("CheckSpec entries must use literal names and commands") from exc
        if not isinstance(name, str):
            raise CheckError("CheckSpec names must be strings")
        if not isinstance(command, tuple) or any(not isinstance(part, str) for part in command):
            raise CheckError("CheckSpec commands must be tuples of strings")
        parsed.append({"name": name, "command": list(command)})
    names = [entry["name"] for entry in parsed]
    if len(names) != len(set(names)):
        raise CheckError("duplicate CheckSpec names in CHECKS")
    return parsed


def parse_validate_phase11(validate_path: Path) -> tuple[list[str], list[dict[str, object]]]:
    text = read_text(validate_path)
    try:
        module = ast.parse(text, filename=str(validate_path))
    except SyntaxError as exc:
        raise CheckError(f"invalid Python in {validate_path}: {exc}") from exc
    required_paths = literal_assignment(module, "REQUIRED_PATHS")
    if not isinstance(required_paths, tuple) or any(not isinstance(item, str) for item in required_paths):
        raise CheckError("REQUIRED_PATHS must be a tuple of strings")
    checks = parse_checks(assignment_node(module, "CHECKS"))
    return list(required_paths), checks


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    if len(value) != len(set(value)):
        raise CheckError(f"duplicate entry in {label}")
    return list(value)


def normalized_fixture_checks(fixture: dict[str, object]) -> list[dict[str, object]]:
    exact_checks = fixture.get("exact_checks")
    if not isinstance(exact_checks, list) or any(not isinstance(item, dict) for item in exact_checks):
        raise CheckError(f"expected object list for exact_checks in {FIXTURE_PATH}")
    normalized: list[dict[str, object]] = []
    for item in exact_checks:
        name = item.get("name")
        command = item.get("command")
        if not isinstance(name, str):
            raise CheckError(f"expected string name in {FIXTURE_PATH}")
        if not isinstance(command, list) or any(not isinstance(part, str) for part in command):
            raise CheckError(f"expected string-list command in {FIXTURE_PATH}")
        normalized.append({"name": name, "command": list(command)})
    return normalized


def run_check(root: Path) -> tuple[int, int]:
    required_paths, checks = parse_validate_phase11(root / VALIDATE_PATH)
    fixture = read_json(root / FIXTURE_PATH)
    inventory = read_json(root / INVENTORY_PATH)

    for required in (
        SELF_CHECK_PATH,
        SELF_FIXTURE_PATH,
        str(INVENTORY_PATH),
        DW_WDT_BUILD_ROUTE_CHECK_PATH,
        DW_WDT_BUILD_INVENTORY_PATH,
        SHARED_TOOLING_CHECK_PATH,
        SHARED_TOOLING_FIXTURE_PATH,
        SHARED_TOOLING_SURVEY_PATH,
    ):
        if required not in required_paths:
            raise CheckError(f"validate-phase11 REQUIRED_PATHS is missing {required}")

    if fixture.get("lane_key") != EXPECTED_LANE_KEY:
        raise CheckError("lane_key mismatch in phase11_validate_checks.json")
    if fixture.get("phase") != EXPECTED_PHASE:
        raise CheckError("phase mismatch in phase11_validate_checks.json")
    if fixture.get("validate_script") != EXPECTED_VALIDATE_SCRIPT:
        raise CheckError("validate_script mismatch in phase11_validate_checks.json")
    if fixture.get("validate_route") != EXPECTED_VALIDATE_ROUTE:
        raise CheckError("validate_route mismatch in phase11_validate_checks.json")

    if inventory.get("deterministic_tooling_lane") != EXPECTED_INVENTORY_DETERMINISTIC_LANE:
        raise CheckError("deterministic_tooling_lane mismatch in phase11_build_inventory.json")
    if expect_string_list(
        "deterministic_fixture_surfaces",
        inventory.get("deterministic_fixture_surfaces"),
    ) != EXPECTED_INVENTORY_DETERMINISTIC_FIXTURE_SURFACES:
        raise CheckError("deterministic_fixture_surfaces mismatch in phase11_build_inventory.json")
    if expect_string_list(
        "focused_teardown_failure_mode_builds",
        inventory.get("focused_teardown_failure_mode_builds"),
    ) != EXPECTED_FOCUSED_TEARDOWN_FAILURE_MODE_BUILDS:
        raise CheckError("focused_teardown_failure_mode_builds mismatch in phase11_build_inventory.json")
    if inventory.get("deterministic_golden_output_gap") != EXPECTED_DETERMINISTIC_GOLDEN_OUTPUT_GAP:
        raise CheckError("deterministic_golden_output_gap mismatch in phase11_build_inventory.json")

    fixture_checks = normalized_fixture_checks(fixture)
    if checks != fixture_checks:
        raise CheckError("exact_checks does not match validate-phase11 CHECKS")

    for expected_name, expected_command in EXPECTED_REQUIRED_CHECKS:
        if {"name": expected_name, "command": expected_command} not in checks:
            raise CheckError(f"validate-phase11 CHECKS is missing {expected_name}")

    return len(required_paths), len(checks)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, omit_required_path: str | None = None, wrong_fixture_command: bool = False, wrong_inventory_surfaces: bool = False) -> None:
    required_paths = [
        "scripts/zigux/validate-phase11.py",
        SELF_CHECK_PATH,
        SELF_FIXTURE_PATH,
        str(INVENTORY_PATH),
        DW_WDT_BUILD_ROUTE_CHECK_PATH,
        DW_WDT_BUILD_INVENTORY_PATH,
        SHARED_TOOLING_CHECK_PATH,
        SHARED_TOOLING_FIXTURE_PATH,
        SHARED_TOOLING_SURVEY_PATH,
    ]
    if omit_required_path is not None:
        required_paths.remove(omit_required_path)

    checks = [
        {"name": "phase11-validation-self-test", "command": ["python", "scripts/zigux/validate-phase11.py", "--self-test"]},
        {"name": "phase11-validate-check-roster-self-test", "command": ["python", SELF_CHECK_PATH, "--self-test"]},
        {"name": "phase11-validate-check-roster", "command": ["python", SELF_CHECK_PATH]},
        {"name": "phase11-shared-tooling-manifest-self-test", "command": ["python", SHARED_TOOLING_CHECK_PATH, "--self-test"]},
        {"name": "phase11-shared-tooling-manifest", "command": ["python", SHARED_TOOLING_CHECK_PATH]},
        {"name": "phase11-dw-wdt-build-route-self-test", "command": ["python", DW_WDT_BUILD_ROUTE_CHECK_PATH, "--self-test"]},
        {"name": "phase11-dw-wdt-build-route", "command": ["python", DW_WDT_BUILD_ROUTE_CHECK_PATH]},
        {"name": "phase11-validation", "command": ["python", "scripts/zigux/validate-phase11.py"]},
    ]
    fixture_checks = json.loads(json.dumps(checks))
    if wrong_fixture_command:
        fixture_checks[-2]["command"] = ["python", DW_WDT_BUILD_ROUTE_CHECK_PATH]

    validate_text = "\n".join(
        [
            "from dataclasses import dataclass",
            "",
            "@dataclass(frozen=True)",
            "class CheckSpec:",
            "    name: str",
            "    command: tuple[str, ...]",
            "",
            "REQUIRED_PATHS = (",
            *(f'    \"{path}\",' for path in required_paths),
            ")",
            "",
            "CHECKS = (",
            '    CheckSpec(\"phase11-validation-self-test\", (\"python\", \"scripts/zigux/validate-phase11.py\", \"--self-test\")),',
            f'    CheckSpec(\"phase11-validate-check-roster-self-test\", (\"python\", \"{SELF_CHECK_PATH}\", \"--self-test\")),',
            f'    CheckSpec(\"phase11-validate-check-roster\", (\"python\", \"{SELF_CHECK_PATH}\")),',
            f'    CheckSpec(\"phase11-shared-tooling-manifest-self-test\", (\"python\", \"{SHARED_TOOLING_CHECK_PATH}\", \"--self-test\")),',
            f'    CheckSpec(\"phase11-shared-tooling-manifest\", (\"python\", \"{SHARED_TOOLING_CHECK_PATH}\")),',
            f'    CheckSpec(\"phase11-dw-wdt-build-route-self-test\", (\"python\", \"{DW_WDT_BUILD_ROUTE_CHECK_PATH}\", \"--self-test\")),',
            f'    CheckSpec(\"phase11-dw-wdt-build-route\", (\"python\", \"{DW_WDT_BUILD_ROUTE_CHECK_PATH}\")),',
            '    CheckSpec(\"phase11-validation\", (\"python\", \"scripts/zigux/validate-phase11.py\")),',
            ")",
            "",
        ]
    )
    write(root / VALIDATE_PATH, validate_text)
    write(
        root / FIXTURE_PATH,
        json.dumps(
            {
                "lane_key": EXPECTED_LANE_KEY,
                "phase": EXPECTED_PHASE,
                "validate_script": EXPECTED_VALIDATE_SCRIPT,
                "validate_route": EXPECTED_VALIDATE_ROUTE,
                "exact_checks": fixture_checks,
            },
            indent=2,
        ) + "\n",
    )
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "deterministic_tooling_lane": EXPECTED_INVENTORY_DETERMINISTIC_LANE,
                "deterministic_fixture_surfaces": (
                    EXPECTED_INVENTORY_DETERMINISTIC_FIXTURE_SURFACES[:-1]
                    if wrong_inventory_surfaces
                    else EXPECTED_INVENTORY_DETERMINISTIC_FIXTURE_SURFACES
                ),
                "focused_teardown_failure_mode_builds": EXPECTED_FOCUSED_TEARDOWN_FAILURE_MODE_BUILDS,
                "deterministic_golden_output_gap": EXPECTED_DETERMINISTIC_GOLDEN_OUTPUT_GAP,
            },
            indent=2,
        ) + "\n",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_validate_check_roster_"))
    try:
        passing = tmpdir / "passing"
        build_fixture(passing)
        required_path_count, check_count = run_check(passing)
        case_count = 1

        missing_required_path = tmpdir / "missing_required_path"
        build_fixture(missing_required_path, omit_required_path=DW_WDT_BUILD_INVENTORY_PATH)
        expect_failure(missing_required_path, DW_WDT_BUILD_INVENTORY_PATH)
        case_count += 1

        wrong_fixture = tmpdir / "wrong_fixture"
        build_fixture(wrong_fixture, wrong_fixture_command=True)
        expect_failure(wrong_fixture, "exact_checks does not match validate-phase11 CHECKS")
        case_count += 1

        wrong_inventory = tmpdir / "wrong_inventory"
        build_fixture(wrong_inventory, wrong_inventory_surfaces=True)
        expect_failure(wrong_inventory, "deterministic_fixture_surfaces mismatch")
        case_count += 1

        missing_required_check = tmpdir / "missing_required_check"
        build_fixture(missing_required_check)
        write(
            missing_required_check / VALIDATE_PATH,
            read_text(missing_required_check / VALIDATE_PATH).replace(
                f'    CheckSpec(\"phase11-dw-wdt-build-route\", (\"python\", \"{DW_WDT_BUILD_ROUTE_CHECK_PATH}\")),\n',
                "",
                1,
            ),
        )
        fixture = read_json(missing_required_check / FIXTURE_PATH)
        fixture["exact_checks"] = [
            item for item in fixture["exact_checks"] if item.get("name") != "phase11-dw-wdt-build-route"
        ]
        write(missing_required_check / FIXTURE_PATH, json.dumps(fixture, indent=2) + "\n")
        expect_failure(missing_required_check, "validate-phase11 CHECKS is missing phase11-dw-wdt-build-route")
        case_count += 1

        syntax_error = tmpdir / "syntax_error"
        write(syntax_error / VALIDATE_PATH, "CHECKS = (\n")
        write(syntax_error / FIXTURE_PATH, "{}\n")
        write(syntax_error / INVENTORY_PATH, "{}\n")
        expect_failure(syntax_error, "invalid Python")
        case_count += 1

        print("PHASE11_VALIDATE_CHECK_ROSTER_SELF_TEST=pass")
        print(f"PHASE11_VALIDATE_CHECK_ROSTER_SELF_TEST_CASE_COUNT={case_count}")
        print(f"PHASE11_VALIDATE_CHECK_ROSTER_FIXTURE_REQUIRED_PATH_COUNT={required_path_count}")
        print(f"PHASE11_VALIDATE_CHECK_ROSTER_FIXTURE_CHECK_COUNT={check_count}")
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
        required_path_count, check_count = run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_VALIDATE_CHECK_ROSTER=fail: {exc}")
        return 1

    print("PHASE11_VALIDATE_CHECK_ROSTER=pass")
    print(f"PHASE11_VALIDATE_CHECK_ROSTER_REQUIRED_PATH_COUNT={required_path_count}")
    print(f"PHASE11_VALIDATE_CHECK_ROSTER_CHECK_COUNT={check_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify the current Phase 11 delivery-tooling bounded step."""

from __future__ import annotations

import argparse
import ast
import json
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)
VALIDATE_PATH = Path("scripts/zigux/validate-phase11.py")
VALIDATE_FIXTURE_PATH = Path("zigux/tests/fixtures/phase11_validate_checks.json")
GOLDEN_CHECKER_PATH = Path("scripts/zigux/check-phase11-deterministic-fixture-golden-output.py")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
EXPECTED_LANE_KEY = "P11-L15"
EXPECTED_PHASE = "Phase 11"
EXPECTED_VALIDATE_ROUTE = "make -C zigux phase11-validate"
EXPECTED_VALIDATE_SCRIPT = "scripts/zigux/validate-phase11.py"
EXPECTED_GOLDEN_STATUS = "standalone_pending_aggregate_route"
EXPECTED_GOLDEN_CHECKER_NAME = "phase11-deterministic-fixture-golden-output"
EXPECTED_GOLDEN_CHECKER_COMMANDS = (
    ["python", str(GOLDEN_CHECKER_PATH), "--self-test"],
    ["python", str(GOLDEN_CHECKER_PATH)],
)
EXPECTED_GOLDEN_MARKERS = (
    "scripts/zigux/check-phase11-deterministic-fixture-golden-output.py",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "inside the deterministic validator packet",
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


def parse_checks(validate_text: str) -> list[dict[str, object]]:
    try:
        module = ast.parse(validate_text)
    except SyntaxError as exc:
        raise CheckError(f"invalid Python in {VALIDATE_PATH}: {exc}") from exc
    checks_node = assignment_node(module, "CHECKS")
    if not isinstance(checks_node, ast.Tuple):
        raise CheckError("CHECKS must be a tuple")

    parsed: list[dict[str, object]] = []
    for item in checks_node.elts:
        if not isinstance(item, ast.Call) or not isinstance(item.func, ast.Name) or item.func.id != "CheckSpec":
            raise CheckError("CHECKS entries must be CheckSpec calls")
        if len(item.args) != 2:
            raise CheckError("CheckSpec entries must carry name and command")
        name = ast.literal_eval(item.args[0])
        command = ast.literal_eval(item.args[1])
        if not isinstance(name, str) or not isinstance(command, tuple):
            raise CheckError("CheckSpec entries must use a string name and tuple command")
        if any(not isinstance(part, str) for part in command):
            raise CheckError("CheckSpec command entries must be strings")
        parsed.append({"name": name, "command": list(command)})

    names = [entry["name"] for entry in parsed]
    if len(names) != len(set(names)):
        raise CheckError("duplicate CheckSpec names in validate-phase11 CHECKS")
    return parsed


def normalized_fixture_checks(fixture: dict[str, object]) -> list[dict[str, object]]:
    exact_checks = fixture.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise CheckError(f"expected list for exact_checks in {VALIDATE_FIXTURE_PATH}")
    normalized: list[dict[str, object]] = []
    for entry in exact_checks:
        if not isinstance(entry, dict):
            raise CheckError(f"expected object entries in {VALIDATE_FIXTURE_PATH}")
        name = entry.get("name")
        command = entry.get("command")
        if not isinstance(name, str):
            raise CheckError(f"expected string name in {VALIDATE_FIXTURE_PATH}")
        if not isinstance(command, list) or any(not isinstance(part, str) for part in command):
            raise CheckError(f"expected string-list command in {VALIDATE_FIXTURE_PATH}")
        normalized.append({"name": name, "command": list(command)})
    return normalized


def require_absent_golden_aggregate_entries(checks: list[dict[str, object]]) -> None:
    for entry in checks:
        name = entry["name"]
        command = entry["command"]
        if name == EXPECTED_GOLDEN_CHECKER_NAME or command in EXPECTED_GOLDEN_CHECKER_COMMANDS:
            raise CheckError("golden-output checker is already in the aggregate route; update this bounded-step checker")


def run_check(root: Path) -> tuple[int, str]:
    validate_text = read_text(root / VALIDATE_PATH)
    fixture = read_json(root / VALIDATE_FIXTURE_PATH)
    inventory = read_json(root / INVENTORY_PATH)
    golden_text = read_text(root / GOLDEN_CHECKER_PATH)

    if fixture.get("lane_key") != EXPECTED_LANE_KEY:
        raise CheckError("phase11_validate_checks lane_key mismatch")
    if fixture.get("phase") != EXPECTED_PHASE:
        raise CheckError("phase11_validate_checks phase mismatch")
    if fixture.get("validate_script") != EXPECTED_VALIDATE_SCRIPT:
        raise CheckError("phase11_validate_checks validate_script mismatch")
    if fixture.get("validate_route") != EXPECTED_VALIDATE_ROUTE:
        raise CheckError("phase11_validate_checks validate_route mismatch")

    validate_checks = parse_checks(validate_text)
    fixture_checks = normalized_fixture_checks(fixture)
    if validate_checks != fixture_checks:
        raise CheckError("phase11_validate_checks exact_checks does not match validate-phase11 CHECKS")
    require_absent_golden_aggregate_entries(validate_checks)

    golden_gap = inventory.get("deterministic_golden_output_gap")
    if not isinstance(golden_gap, str):
        raise CheckError("expected deterministic_golden_output_gap string in phase11_build_inventory.json")
    for marker in EXPECTED_GOLDEN_MARKERS:
        if marker not in golden_gap and marker not in golden_text:
            raise CheckError(f"missing golden-output bounded-step marker: {marker}")

    return len(validate_checks), EXPECTED_GOLDEN_STATUS


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_validate(checks: list[dict[str, object]]) -> str:
    lines = [
        "from __future__ import annotations",
        "from dataclasses import dataclass",
        "@dataclass(frozen=True)",
        "class CheckSpec:",
        "    name: str",
        "    command: tuple[str, ...]",
        "CHECKS = (",
    ]
    for entry in checks:
        command = ", ".join(repr(part) for part in entry["command"])
        lines.append(f"    CheckSpec({entry['name']!r}, ({command})),")
    lines.append(")")
    return "\n".join(lines) + "\n"


def build_sample(root: Path, *, include_golden_in_aggregate: bool = False) -> None:
    checks = [
        {"name": "phase11-validation-self-test", "command": ["python", str(VALIDATE_PATH), "--self-test"]},
        {"name": "phase11-build-inventory", "command": ["python", "scripts/zigux/check-phase11-build-inventory.py"]},
    ]
    if include_golden_in_aggregate:
        checks.append({"name": EXPECTED_GOLDEN_CHECKER_NAME, "command": list(EXPECTED_GOLDEN_CHECKER_COMMANDS[1])})
    write(root / VALIDATE_PATH, sample_validate(checks))
    write(
        root / VALIDATE_FIXTURE_PATH,
        json.dumps(
            {
                "lane_key": EXPECTED_LANE_KEY,
                "phase": EXPECTED_PHASE,
                "validate_script": EXPECTED_VALIDATE_SCRIPT,
                "validate_route": EXPECTED_VALIDATE_ROUTE,
                "exact_checks": checks,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "deterministic_golden_output_gap": " ".join(EXPECTED_GOLDEN_MARKERS),
            },
            indent=2,
        )
        + "\n",
    )
    write(root / GOLDEN_CHECKER_PATH, "# sample golden checker\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_delivery_tooling_bounded_step_"))
    try:
        baseline = tmpdir / "baseline"
        build_sample(baseline)
        check_count, status = run_check(baseline)
        if check_count != 2 or status != EXPECTED_GOLDEN_STATUS:
            raise AssertionError("unexpected baseline report")
        case_count = 1

        mismatched_fixture = tmpdir / "mismatched_fixture"
        shutil.copytree(baseline, mismatched_fixture)
        fixture = read_json(mismatched_fixture / VALIDATE_FIXTURE_PATH)
        fixture["exact_checks"] = fixture["exact_checks"][:-1]
        write(mismatched_fixture / VALIDATE_FIXTURE_PATH, json.dumps(fixture) + "\n")
        expect_failure(mismatched_fixture, "exact_checks does not match")
        case_count += 1

        wrong_lane = tmpdir / "wrong_lane"
        shutil.copytree(baseline, wrong_lane)
        fixture = read_json(wrong_lane / VALIDATE_FIXTURE_PATH)
        fixture["lane_key"] = "P11-L99"
        write(wrong_lane / VALIDATE_FIXTURE_PATH, json.dumps(fixture) + "\n")
        expect_failure(wrong_lane, "lane_key mismatch")
        case_count += 1

        already_aggregate = tmpdir / "already_aggregate"
        build_sample(already_aggregate, include_golden_in_aggregate=True)
        expect_failure(already_aggregate, "already in the aggregate route")
        case_count += 1

        missing_golden_gap = tmpdir / "missing_golden_gap"
        shutil.copytree(baseline, missing_golden_gap)
        inventory = read_json(missing_golden_gap / INVENTORY_PATH)
        inventory["deterministic_golden_output_gap"] = ""
        write(missing_golden_gap / INVENTORY_PATH, json.dumps(inventory) + "\n")
        write(missing_golden_gap / GOLDEN_CHECKER_PATH, "# sample\n")
        expect_failure(missing_golden_gap, "missing golden-output bounded-step marker")
        case_count += 1

        print("PHASE11_DELIVERY_TOOLING_BOUNDED_STEP_SELF_TEST=pass")
        print(f"PHASE11_DELIVERY_TOOLING_BOUNDED_STEP_SELF_TEST_CASE_COUNT={case_count}")
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
        check_count, status = run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_DELIVERY_TOOLING_BOUNDED_STEP=fail: {exc}")
        return 1

    print("PHASE11_DELIVERY_TOOLING_BOUNDED_STEP=pass")
    print(f"PHASE11_DELIVERY_TOOLING_EXACT_CHECK_COUNT={check_count}")
    print(f"PHASE11_DELIVERY_TOOLING_GOLDEN_OUTPUT_STATUS={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

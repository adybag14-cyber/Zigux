#!/usr/bin/env python3
"""Fail closed if the Phase 11 Makefile route drifts from validate-phase11.py."""

from __future__ import annotations

import argparse
import ast
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
MAKEFILE_PATH = Path("zigux/Makefile")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase11.py")
TARGET_NAME = "phase11-validate"
VALIDATOR_ROUTE = "scripts/zigux/validate-phase11.py"


class CheckError(RuntimeError):
    pass


@dataclass(frozen=True)
class CheckSpecRecord:
    name: str
    command: tuple[str, ...]


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def parse_checkspec_records(validate_path: Path) -> list[CheckSpecRecord]:
    text = read_text(validate_path)
    try:
        module = ast.parse(text, filename=str(validate_path))
    except SyntaxError as exc:
        raise CheckError(f"invalid Python in {validate_path}: {exc}") from exc

    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "CHECKS":
                if not isinstance(node.value, ast.Tuple):
                    raise CheckError("CHECKS must be a tuple")
                records: list[CheckSpecRecord] = []
                for entry in node.value.elts:
                    if not isinstance(entry, ast.Call) or not isinstance(entry.func, ast.Name) or entry.func.id != "CheckSpec":
                        raise CheckError("CHECKS entries must be CheckSpec(...) calls")
                    if len(entry.args) != 2:
                        raise CheckError("CHECKS entries must pass name and command")
                    try:
                        name = ast.literal_eval(entry.args[0])
                        command = ast.literal_eval(entry.args[1])
                    except Exception as exc:  # noqa: BLE001
                        raise CheckError(f"unable to parse CheckSpec entry: {exc}") from exc
                    if not isinstance(name, str):
                        raise CheckError("CheckSpec name must be a string")
                    if not isinstance(command, tuple) or any(not isinstance(item, str) for item in command):
                        raise CheckError(f"CheckSpec command for {name} must be a tuple of strings")
                    records.append(CheckSpecRecord(name=name, command=command))
                return records
    raise CheckError("missing assignment: CHECKS")


def extract_validator_build_files(validate_path: Path) -> list[str]:
    build_files: list[str] = []
    for record in parse_checkspec_records(validate_path):
        command = record.command
        if command[:4] == ("zig", "build", "test", "--build-file") and len(command) >= 5:
            build_files.append(command[4])
    if not build_files:
        raise CheckError("validate-phase11.py does not declare any zig build fan-out")
    return build_files


def extract_makefile_recipe(makefile_path: Path, target_name: str) -> list[str]:
    lines = read_text(makefile_path).splitlines()
    for index, line in enumerate(lines):
        if line.startswith(f"{target_name}:"):
            recipe: list[str] = []
            cursor = index + 1
            while cursor < len(lines):
                current = lines[cursor]
                if current.startswith("\t"):
                    recipe.append(current.strip())
                    cursor += 1
                    continue
                if not current.strip():
                    cursor += 1
                    continue
                break
            if not recipe:
                raise CheckError(f"target {target_name} has no recipe")
            return recipe
    raise CheckError(f"missing target: {target_name}")


def extract_makefile_build_files(recipe: list[str]) -> list[str]:
    build_files: list[str] = []
    for line in recipe:
        match = re.search(r"--build-file\s+(\S+)", line)
        if match:
            build_files.append(match.group(1))
    return build_files


def run_check(root: Path) -> tuple[int, int]:
    validator_path = root / VALIDATOR_PATH
    makefile_path = root / MAKEFILE_PATH

    validator_build_files = extract_validator_build_files(validator_path)
    recipe = extract_makefile_recipe(makefile_path, TARGET_NAME)

    validator_recipe_indexes = [
        index for index, line in enumerate(recipe) if VALIDATOR_ROUTE in line
    ]
    if not validator_recipe_indexes:
        raise CheckError(f"{TARGET_NAME} is missing the {VALIDATOR_ROUTE} route")
    if len(validator_recipe_indexes) != 1:
        raise CheckError(f"{TARGET_NAME} must call {VALIDATOR_ROUTE} exactly once")

    makefile_build_files = extract_makefile_build_files(recipe)
    if not makefile_build_files:
        raise CheckError(f"{TARGET_NAME} has no zig build fan-out")

    if validator_recipe_indexes[0] > min(index for index, line in enumerate(recipe) if "--build-file" in line):
        raise CheckError(f"{TARGET_NAME} must run {VALIDATOR_ROUTE} before the Zig build fan-out")

    if makefile_build_files != validator_build_files:
        raise CheckError(
            f"{TARGET_NAME} build fan-out mismatch: expected {validator_build_files}, found {makefile_build_files}"
        )

    return len(validator_build_files), len(recipe)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, recipe_lines: list[str] | None = None, checks_text: str | None = None) -> None:
    write(
        root / VALIDATOR_PATH,
        checks_text
        or "\n".join(
            [
                "from dataclasses import dataclass",
                "",
                "@dataclass(frozen=True)",
                "class CheckSpec:",
                "    name: str",
                "    command: tuple[str, ...]",
                "",
                "CHECKS = (",
                "    CheckSpec(\"phase11-validation-self-test\", (\"python\", \"scripts/zigux/validate-phase11.py\", \"--self-test\")),",
                "    CheckSpec(\"phase11-validate-route-alignment-self-test\", (\"python\", \"scripts/zigux/check-phase11-validate-route-alignment.py\", \"--self-test\")),",
                "    CheckSpec(\"phase11-validate-route-alignment\", (\"python\", \"scripts/zigux/check-phase11-validate-route-alignment.py\")),",
                "    CheckSpec(\"phase11-a\", (\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_a_build.zig\")),",
                "    CheckSpec(\"phase11-b\", (\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_b_build.zig\")),",
                ")",
                "",
            ]
        ),
    )
    write(
        root / MAKEFILE_PATH,
        "\n".join(
            [
                "phase11-validate:",
                *(recipe_lines or [
                    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                    "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_a_build.zig",
                    "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_b_build.zig",
                ]),
                "",
            ]
        ),
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
    tempdir = Path(tempfile.mkdtemp(prefix="phase11_validate_route_alignment_"))
    try:
        baseline = tempdir / "baseline"
        build_fixture(baseline)
        build_count, recipe_count = run_check(baseline)
        case_count = 1

        missing_target = tempdir / "missing_target"
        build_fixture(missing_target)
        write(missing_target / MAKEFILE_PATH, "phase10-validate:\n\ttrue\n")
        expect_failure(missing_target, "missing target: phase11-validate")
        case_count += 1

        missing_validator = tempdir / "missing_validator"
        build_fixture(
            missing_validator,
            recipe_lines=[
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_a_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_b_build.zig",
            ],
        )
        expect_failure(missing_validator, "missing the scripts/zigux/validate-phase11.py route")
        case_count += 1

        duplicate_validator = tempdir / "duplicate_validator"
        build_fixture(
            duplicate_validator,
            recipe_lines=[
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_a_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_b_build.zig",
            ],
        )
        expect_failure(duplicate_validator, "must call scripts/zigux/validate-phase11.py exactly once")
        case_count += 1

        wrong_order = tempdir / "wrong_order"
        build_fixture(
            wrong_order,
            recipe_lines=[
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_a_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_b_build.zig",
            ],
        )
        expect_failure(wrong_order, "must run scripts/zigux/validate-phase11.py before the Zig build fan-out")
        case_count += 1

        missing_build = tempdir / "missing_build"
        build_fixture(
            missing_build,
            recipe_lines=[
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_a_build.zig",
            ],
        )
        expect_failure(missing_build, "build fan-out mismatch")
        case_count += 1

        extra_build = tempdir / "extra_build"
        build_fixture(
            extra_build,
            recipe_lines=[
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_a_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_b_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_c_build.zig",
            ],
        )
        expect_failure(extra_build, "build fan-out mismatch")
        case_count += 1

        no_makefile_builds = tempdir / "no_makefile_builds"
        build_fixture(
            no_makefile_builds,
            recipe_lines=[
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
            ],
        )
        expect_failure(no_makefile_builds, "phase11-validate has no zig build fan-out")
        case_count += 1

        no_validator_builds = tempdir / "no_validator_builds"
        build_fixture(
            no_validator_builds,
            checks_text="\n".join(
                [
                    "from dataclasses import dataclass",
                    "",
                    "@dataclass(frozen=True)",
                    "class CheckSpec:",
                    "    name: str",
                    "    command: tuple[str, ...]",
                    "",
                    "CHECKS = (",
                    "    CheckSpec(\"phase11-validation-self-test\", (\"python\", \"scripts/zigux/validate-phase11.py\", \"--self-test\")),",
                    "    CheckSpec(\"phase11-validate-route-alignment-self-test\", (\"python\", \"scripts/zigux/check-phase11-validate-route-alignment.py\", \"--self-test\")),",
                    "    CheckSpec(\"phase11-validate-route-alignment\", (\"python\", \"scripts/zigux/check-phase11-validate-route-alignment.py\")),",
                    ")",
                    "",
                ]
            ),
        )
        expect_failure(no_validator_builds, "validate-phase11.py does not declare any zig build fan-out")
        case_count += 1

        bad_validator = tempdir / "bad_validator"
        build_fixture(bad_validator, checks_text="CHECKS = (\n")
        expect_failure(bad_validator, "invalid Python")
        case_count += 1

        print("PHASE11_VALIDATE_ROUTE_ALIGNMENT_SELF_TEST=pass")
        print(f"PHASE11_VALIDATE_ROUTE_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
        print(f"PHASE11_VALIDATE_ROUTE_ALIGNMENT_BUILD_COUNT={build_count}")
        print(f"PHASE11_VALIDATE_ROUTE_ALIGNMENT_RECIPE_LINE_COUNT={recipe_count}")
        return 0
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        build_count, recipe_count = run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_VALIDATE_ROUTE_ALIGNMENT=fail: {exc}")
        return 1

    print("PHASE11_VALIDATE_ROUTE_ALIGNMENT=pass")
    print(f"PHASE11_VALIDATE_ROUTE_ALIGNMENT_BUILD_COUNT={build_count}")
    print(f"PHASE11_VALIDATE_ROUTE_ALIGNMENT_RECIPE_LINE_COUNT={recipe_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

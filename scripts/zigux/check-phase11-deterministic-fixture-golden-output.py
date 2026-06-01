#!/usr/bin/env python3
"""Guard Phase 11 deterministic fixture and golden-output metadata."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = (
    Path(__file__).resolve().parents[2]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")

EXPECTED_DETERMINISTIC_FIXTURE_SURFACES = (
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
)

EXPECTED_GOLDEN_OUTPUT_MARKERS = (
    "phase11-validate now carries the dedicated golden-output fixture roster",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "scripts/zigux/check-phase11-validate-check-roster.py",
    "scripts/zigux/check-phase11-validate-route-alignment.py",
    "scripts/zigux/check-phase11-deterministic-fixture-golden-output.py",
    "scripts/zigux/check-phase11-dw-wdt-build-route.py",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "inside the deterministic validator packet",
)


class CheckError(RuntimeError):
    pass


def read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"expected object in {path}")
    return payload


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    if len(value) != len(set(value)):
        raise CheckError(f"duplicate entry in {label}")
    return list(value)


def expect_string(label: str, value: object) -> str:
    if not isinstance(value, str):
        raise CheckError(f"expected string for {label}")
    return value


def expect_existing_paths(root: Path, label: str, values: list[str]) -> None:
    missing = [value for value in values if not (root / value).is_file()]
    if missing:
        raise CheckError(f"missing fixture surface file in {label}: {', '.join(missing)}")


def run_check(root: Path) -> None:
    inventory = read_json(root / INVENTORY_PATH)

    fixture_surfaces = expect_string_list(
        "deterministic_fixture_surfaces",
        inventory.get("deterministic_fixture_surfaces"),
    )
    if fixture_surfaces != list(EXPECTED_DETERMINISTIC_FIXTURE_SURFACES):
        raise CheckError("deterministic_fixture_surfaces does not match the Phase 11 fixture packet")
    expect_existing_paths(root, "deterministic_fixture_surfaces", fixture_surfaces)

    golden_output_gap = expect_string(
        "deterministic_golden_output_gap",
        inventory.get("deterministic_golden_output_gap"),
    )
    for marker in EXPECTED_GOLDEN_OUTPUT_MARKERS:
        if marker not in golden_output_gap:
            raise CheckError(f"missing golden-output marker: {marker}")


def write_inventory(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_fixture_surfaces(root: Path) -> None:
    for rel in EXPECTED_DETERMINISTIC_FIXTURE_SURFACES:
        if rel == str(INVENTORY_PATH):
            continue
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")


def fixture_inventory() -> dict[str, object]:
    return {
        "deterministic_fixture_surfaces": list(EXPECTED_DETERMINISTIC_FIXTURE_SURFACES),
        "deterministic_golden_output_gap": " ".join(EXPECTED_GOLDEN_OUTPUT_MARKERS),
    }


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_deterministic_fixture_golden_"))
    try:
        fixture = tmpdir / "fixture"
        write_inventory(fixture / INVENTORY_PATH, fixture_inventory())
        write_fixture_surfaces(fixture)
        run_check(fixture)
        case_count = 1

        missing_fixture_surfaces = tmpdir / "missing_fixture_surfaces"
        shutil.copytree(fixture, missing_fixture_surfaces, dirs_exist_ok=True)
        payload = read_json(missing_fixture_surfaces / INVENTORY_PATH)
        payload.pop("deterministic_fixture_surfaces")
        write_inventory(missing_fixture_surfaces / INVENTORY_PATH, payload)
        expect_failure(missing_fixture_surfaces, "expected string list for deterministic_fixture_surfaces")
        case_count += 1

        missing_fixture_surface_file = tmpdir / "missing_fixture_surface_file"
        shutil.copytree(fixture, missing_fixture_surface_file, dirs_exist_ok=True)
        (missing_fixture_surface_file / "zigux/tests/fixtures/phase11_validate_checks.json").unlink()
        expect_failure(
            missing_fixture_surface_file,
            "missing fixture surface file in deterministic_fixture_surfaces",
        )
        case_count += 1

        duplicate_fixture_surface = tmpdir / "duplicate_fixture_surface"
        shutil.copytree(fixture, duplicate_fixture_surface, dirs_exist_ok=True)
        payload = read_json(duplicate_fixture_surface / INVENTORY_PATH)
        payload["deterministic_fixture_surfaces"] = [
            EXPECTED_DETERMINISTIC_FIXTURE_SURFACES[0],
            EXPECTED_DETERMINISTIC_FIXTURE_SURFACES[0],
        ]
        write_inventory(duplicate_fixture_surface / INVENTORY_PATH, payload)
        expect_failure(duplicate_fixture_surface, "duplicate entry in deterministic_fixture_surfaces")
        case_count += 1

        wrong_fixture_surface = tmpdir / "wrong_fixture_surface"
        shutil.copytree(fixture, wrong_fixture_surface, dirs_exist_ok=True)
        payload = read_json(wrong_fixture_surface / INVENTORY_PATH)
        payload["deterministic_fixture_surfaces"] = list(EXPECTED_DETERMINISTIC_FIXTURE_SURFACES[:-1])
        write_inventory(wrong_fixture_surface / INVENTORY_PATH, payload)
        expect_failure(wrong_fixture_surface, "deterministic_fixture_surfaces does not match")
        case_count += 1

        missing_golden_gap = tmpdir / "missing_golden_gap"
        shutil.copytree(fixture, missing_golden_gap, dirs_exist_ok=True)
        payload = read_json(missing_golden_gap / INVENTORY_PATH)
        payload.pop("deterministic_golden_output_gap")
        write_inventory(missing_golden_gap / INVENTORY_PATH, payload)
        expect_failure(missing_golden_gap, "expected string for deterministic_golden_output_gap")
        case_count += 1

        missing_golden_marker = tmpdir / "missing_golden_marker"
        shutil.copytree(fixture, missing_golden_marker, dirs_exist_ok=True)
        payload = read_json(missing_golden_marker / INVENTORY_PATH)
        payload["deterministic_golden_output_gap"] = payload["deterministic_golden_output_gap"].replace(
            "scripts/zigux/check-phase11-dw-wdt-build-route.py",
            "",
            1,
        )
        write_inventory(missing_golden_marker / INVENTORY_PATH, payload)
        expect_failure(missing_golden_marker, "scripts/zigux/check-phase11-dw-wdt-build-route.py")
        case_count += 1

        print("PHASE11_DETERMINISTIC_FIXTURE_GOLDEN_OUTPUT=pass")
        print(f"PHASE11_DETERMINISTIC_FIXTURE_GOLDEN_OUTPUT_SELF_TEST_CASE_COUNT={case_count}")
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
        print(f"PHASE11_DETERMINISTIC_FIXTURE_GOLDEN_OUTPUT=fail: {exc}")
        return 1

    print("PHASE11_DETERMINISTIC_FIXTURE_GOLDEN_OUTPUT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

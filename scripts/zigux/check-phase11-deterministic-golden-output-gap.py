#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

SURVEY_PATH = Path("Documentation/zigux/phase11-deterministic-golden-output-gap-survey.md")
MATRIX_SURVEY_PATH = Path("Documentation/zigux/phase11-validation-matrix-gap-survey.md")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
VALIDATE_CHECKS_PATH = Path("zigux/tests/fixtures/phase11_validate_checks.json")

EXPECTED_FIXTURE_SURFACES = [
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
]

EXPECTED_FOCUSED_BUILDS = [
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
]

EXPECTED_GAP = (
    "phase11-validate now carries the dedicated golden-output fixture roster "
    "`zigux/tests/fixtures/phase11_validate_checks.json` plus fail-closed "
    "`scripts/zigux/check-phase11-validate-check-roster.py` and "
    "`scripts/zigux/check-phase11-validate-route-alignment.py` guards; keep "
    "future deterministic output drift inside that validator packet"
)

SURVEY_MARKERS = (
    "`PHASE11_DETERMINISTIC_TOOLING_GAP_STATUS=refresh_route_and_artifact_diff_guard_missing`",
    "lane: `P11-L07`",
    "Current `master` already ships the narrower machine-readable deterministic surfaces through:",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/fixtures/phase11_validate_checks.json`",
    "`zigux/tests/phase11_dw_wdt_manifest.json`",
    "`scripts/zigux/validate-phase11.py`",
    "`make -C zigux phase11-validate`",
    "`scripts/zigux/check-phase11-validate-check-roster.py`",
    "`scripts/zigux/check-phase11-validate-route-alignment.py`",
    "Current `master` still does not ship:",
    "a dedicated refresh helper route for shared Phase 11 expected outputs",
    "an artifact-diff-style deterministic output guard for the driver-local proof builds",
    "inventory-backed and build-proof-first, yet it cannot refresh and diff stable golden outputs",
)

MATRIX_MARKERS = (
    "deterministic tooling survey lane: `P11-L07`",
    "It still does not rematerialize a refresh helper route or an artifact-diff-style deterministic output guard for the driver-local proof builds.",
    "That leaves a narrower roadmap-facing deterministic tooling gap",
)

REQUIRED_VALIDATE_CHECK_NAMES = (
    "phase11-validate-check-roster-self-test",
    "phase11-validate-check-roster",
    "phase11-validate-route-alignment-self-test",
    "phase11-validate-route-alignment",
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.is_file():
        raise CheckError(f"missing required file: {rel.as_posix()}")
    return path.read_text(encoding="utf-8")


def read_json(root: Path, rel: Path) -> dict[str, object]:
    try:
        value = json.loads(read_text(root, rel))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {rel.as_posix()}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError(f"expected object in {rel.as_posix()}")
    return value


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> None:
    normalized = normalize_whitespace(text)
    for marker in markers:
        if normalize_whitespace(marker) not in normalized:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    return list(value)


def run_check(root: Path) -> None:
    require_markers("survey", read_text(root, SURVEY_PATH), SURVEY_MARKERS)
    require_markers("matrix survey", read_text(root, MATRIX_SURVEY_PATH), MATRIX_MARKERS)

    inventory = read_json(root, INVENTORY_PATH)
    if inventory.get("deterministic_tooling_lane") != "P11-L07":
        raise CheckError("deterministic_tooling_lane does not match P11-L07")
    if expect_string_list("deterministic_fixture_surfaces", inventory.get("deterministic_fixture_surfaces")) != EXPECTED_FIXTURE_SURFACES:
        raise CheckError("deterministic_fixture_surfaces does not match the current packet")
    if expect_string_list("focused_teardown_failure_mode_builds", inventory.get("focused_teardown_failure_mode_builds")) != EXPECTED_FOCUSED_BUILDS:
        raise CheckError("focused_teardown_failure_mode_builds does not match the current packet")
    if inventory.get("deterministic_golden_output_gap") != EXPECTED_GAP:
        raise CheckError("deterministic_golden_output_gap does not match the current packet")

    validate_checks = read_json(root, VALIDATE_CHECKS_PATH)
    exact_checks = validate_checks.get("exact_checks")
    if not isinstance(exact_checks, list) or any(not isinstance(item, dict) for item in exact_checks):
        raise CheckError("expected object list for exact_checks")
    names = [item.get("name") for item in exact_checks]
    for name in REQUIRED_VALIDATE_CHECK_NAMES:
        if name not in names:
            raise CheckError(f"missing validate roster entry: {name}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / SURVEY_PATH,
        "\n".join(
            [
                "# Phase 11 Deterministic Golden-Output Tooling Gap Survey",
                "",
                "- `PHASE11_DETERMINISTIC_TOOLING_GAP_STATUS=refresh_route_and_artifact_diff_guard_missing`",
                "- lane: `P11-L07`",
                "- Current `master` already ships the narrower machine-readable deterministic surfaces through:",
                "- `zigux/tests/fixtures/phase11_build_inventory.json`",
                "- `zigux/tests/fixtures/phase11_validate_checks.json`",
                "- `zigux/tests/phase11_dw_wdt_manifest.json`",
                "- `scripts/zigux/validate-phase11.py`",
                "- `make -C zigux phase11-validate`",
                "- `scripts/zigux/check-phase11-validate-check-roster.py`",
                "- `scripts/zigux/check-phase11-validate-route-alignment.py`",
                "- Current `master` still does not ship:",
                "- a dedicated refresh helper route for shared Phase 11 expected outputs",
                "- an artifact-diff-style deterministic output guard for the driver-local proof builds",
                "- inventory-backed and build-proof-first, yet it cannot refresh and diff stable golden outputs",
                "",
            ]
        ),
    )
    write(
        root / MATRIX_SURVEY_PATH,
        "\n".join(
            [
                "# Phase 11 Validation Matrix Gap Survey",
                "- deterministic tooling survey lane: `P11-L07`",
                "- It still does not rematerialize a refresh helper route or an artifact-diff-style deterministic output guard for the driver-local proof builds.",
                "- That leaves a narrower roadmap-facing deterministic tooling gap",
                "",
            ]
        ),
    )
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "deterministic_tooling_lane": "P11-L07",
                "deterministic_fixture_surfaces": EXPECTED_FIXTURE_SURFACES,
                "focused_teardown_failure_mode_builds": EXPECTED_FOCUSED_BUILDS,
                "deterministic_golden_output_gap": EXPECTED_GAP,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / VALIDATE_CHECKS_PATH,
        json.dumps(
            {
                "exact_checks": [
                    {
                        "name": "phase11-validate-check-roster-self-test",
                        "command": ["python", "scripts/zigux/check-phase11-validate-check-roster.py", "--self-test"],
                    },
                    {
                        "name": "phase11-validate-check-roster",
                        "command": ["python", "scripts/zigux/check-phase11-validate-check-roster.py"],
                    },
                    {
                        "name": "phase11-validate-route-alignment-self-test",
                        "command": ["python", "scripts/zigux/check-phase11-validate-route-alignment.py", "--self-test"],
                    },
                    {
                        "name": "phase11-validate-route-alignment",
                        "command": ["python", "scripts/zigux/check-phase11-validate-route-alignment.py"],
                    },
                ]
            },
            indent=2,
        )
        + "\n",
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_deterministic_gap_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_survey_marker = tmpdir / "missing_survey_marker"
        shutil.copytree(fixture, missing_survey_marker, dirs_exist_ok=True)
        write(
            missing_survey_marker / SURVEY_PATH,
            read_text(missing_survey_marker, SURVEY_PATH).replace(
                "- a dedicated refresh helper route for shared Phase 11 expected outputs\n",
                "",
                1,
            ),
        )
        expect_failure(missing_survey_marker, "a dedicated refresh helper route for shared Phase 11 expected outputs")
        case_count += 1

        wrong_lane = tmpdir / "wrong_lane"
        shutil.copytree(fixture, wrong_lane, dirs_exist_ok=True)
        payload = read_json(wrong_lane, INVENTORY_PATH)
        payload["deterministic_tooling_lane"] = "P11-L99"
        write(wrong_lane / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_lane, "deterministic_tooling_lane does not match P11-L07")
        case_count += 1

        wrong_gap = tmpdir / "wrong_gap"
        shutil.copytree(fixture, wrong_gap, dirs_exist_ok=True)
        payload = read_json(wrong_gap, INVENTORY_PATH)
        payload["deterministic_golden_output_gap"] = "stale gap"
        write(wrong_gap / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_gap, "deterministic_golden_output_gap does not match the current packet")
        case_count += 1

        missing_validate_entry = tmpdir / "missing_validate_entry"
        shutil.copytree(fixture, missing_validate_entry, dirs_exist_ok=True)
        payload = read_json(missing_validate_entry, VALIDATE_CHECKS_PATH)
        payload["exact_checks"] = payload["exact_checks"][1:]
        write(missing_validate_entry / VALIDATE_CHECKS_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(missing_validate_entry, "phase11-validate-check-roster-self-test")
        case_count += 1

        print("PHASE11_DETERMINISTIC_GOLDEN_OUTPUT_GAP_SELF_TEST=pass")
        print(f"PHASE11_DETERMINISTIC_GOLDEN_OUTPUT_GAP_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_DETERMINISTIC_GOLDEN_OUTPUT_GAP=fail: {exc}")
        return 1

    print("PHASE11_DETERMINISTIC_GOLDEN_OUTPUT_GAP=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

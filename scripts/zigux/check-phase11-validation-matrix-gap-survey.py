#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 driver-local matrix packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SCRIPT_PATH = "scripts/zigux/check-phase11-validation-matrix-gap-survey.py"

FILES = {
    "matrix_gap_note": "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "inventory": "zigux/tests/fixtures/phase11_build_inventory.json",
}

MARKERS = {
    "matrix_gap_note": [
        "# Phase 11 Validation Matrix Gap Survey",
        "`PHASE11_MATRIX_GAP_STATUS=four_matrix_direct_readback_restored`",
        "lane: `P11-L03`",
        "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
        "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
        "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "matrix packet is once again an honest four-matrix direct-readback claim",
        "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains",
        "`zigux/tests/fixtures/phase11_build_inventory.json` still records 14 build test",
        "13 shared depend steps, and one dedicated survey replay",
        "`phase11-bcm2835-wdt-tests`",
        "`phase11-gpio-wdt-tests`",
        "`phase11-hvc-console-tests`",
        "`phase11-dw-wdt-tests`",
    ],
}

FORBIDDEN_MARKERS = {
    "matrix_gap_note": [
        "`PHASE11_MATRIX_GAP_STATUS=driver_local_matrix_docs_absent_shared_header_matrix_only`",
        "shared matrix packet is no longer an honest four-matrix direct-readback claim",
        "The only directly readable Phase 11 matrix note on current `master` is",
    ],
}

REQUIRED_BUILD_TEST_NAMES = (
    "phase11-gpio-wdt-tests",
    "phase11-gpio-wdt-survey-tests",
    "phase11-bcm2835-wdt-tests",
    "phase11-bcm2835-wdt-verify-tests",
    "phase11-bcm2835-wdt-survey-tests",
    "phase11-dw-wdt-tests",
    "phase11-dw-wdt-registration-scaffold-tests",
    "phase11-dw-wdt-verify-tests",
    "phase11-dw-wdt-survey-tests",
    "phase11-hvc-console-tests",
    "phase11-hvc-console-verify-tests",
    "phase11-hvc-cleanup-tests",
    "phase11-hvc-console-survey-tests",
    "phase11-uapi-header-parity-survey-tests",
)

REQUIRED_SHARED_DEPEND_STEPS = (
    "run_phase11_gpio_wdt_tests",
    "run_phase11_gpio_wdt_survey_tests",
    "run_phase11_bcm2835_wdt_tests",
    "run_bcm2835_wdt_verify_tests",
    "run_phase11_bcm2835_wdt_survey_tests",
    "run_phase11_dw_wdt_tests",
    "run_phase11_dw_wdt_registration_scaffold_tests",
    "run_dw_wdt_verify_tests",
    "run_phase11_dw_wdt_survey_tests",
    "run_phase11_uapi_header_parity_survey_tests",
    "run_phase11_hvc_console_tests",
    "run_hvc_console_verify_tests",
    "run_phase11_hvc_cleanup_tests",
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_forbidden_markers_absent(label: str, text: str) -> None:
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if marker in text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    if len(value) != len(set(value)):
        raise CheckError(f"duplicate entry in {label}")
    return list(value)


def run_check(root: Path) -> None:
    survey_text = read_text(root, FILES["matrix_gap_note"])
    expect_markers("matrix_gap_note", survey_text, MARKERS["matrix_gap_note"])
    expect_forbidden_markers_absent("matrix_gap_note", survey_text)

    inventory = json.loads(read_text(root, FILES["inventory"]))
    if not isinstance(inventory, dict):
        raise CheckError("expected object in inventory")

    build_test_names = expect_string_list("build_test_names", inventory.get("build_test_names"))
    if len(build_test_names) != 14:
        raise CheckError("expected 14 build_test_names entries")
    for name in REQUIRED_BUILD_TEST_NAMES:
        if name not in build_test_names:
            raise CheckError(f"missing build_test_names entry: {name}")

    shared_steps = expect_string_list("shared_test_depend_steps", inventory.get("shared_test_depend_steps"))
    if len(shared_steps) != 13:
        raise CheckError("expected 13 shared_test_depend_steps entries")
    for step in REQUIRED_SHARED_DEPEND_STEPS:
        if step not in shared_steps:
            raise CheckError(f"missing shared_test_depend_steps entry: {step}")
    if "run_phase11_hvc_console_survey_tests" in shared_steps:
        raise CheckError("expected HVC survey replay to stay dedicated")

    dedicated_survey_replays = expect_string_list(
        "dedicated_survey_replays",
        inventory.get("dedicated_survey_replays"),
    )
    if dedicated_survey_replays != ["zigux/tests/phase11_hvc_console_survey.zig"]:
        raise CheckError("unexpected dedicated_survey_replays packet")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    write(
        root / FILES["matrix_gap_note"],
        """# Phase 11 Validation Matrix Gap Survey

- `PHASE11_MATRIX_GAP_STATUS=four_matrix_direct-readback_restored`
- lane: `P11-L03`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- shared matrix packet is once again an honest four-matrix direct-readback claim
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains
- `zigux/tests/fixtures/phase11_build_inventory.json` still records 14 build test names, 13 shared depend steps, and one dedicated survey replay
- `phase11-bcm2835-wdt-tests`
- `phase11-gpio-wdt-tests`
- `phase11-hvc-console-tests`
- `phase11-dw-wdt-tests`
""",
    )
    write(
        root / FILES["inventory"],
        json.dumps(
            {
                "build_test_names": list(REQUIRED_BUILD_TEST_NAMES),
                "shared_test_depend_steps": list(REQUIRED_SHARED_DEPEND_STEPS),
                "dedicated_survey_replays": ["zigux/tests/phase11_hvc_console_survey.zig"],
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_matrix_gap_validation_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        required_cases = [
            ("matrix_gap_note", "`PHASE11_MATRIX_GAP_STATUS=four_matrix_direct_readback_restored`"),
        ]
        for idx, (label, marker) in enumerate(required_cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.writeText(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1).replace(marker, "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_root = tmpdir / "forbidden"
        shutil.copytree(fixture_root, forbidden_root, dirs_exist_ok=True)
        path = forbidden_root / FILES["matrix_gap_note"]
        path.write_text(
            path.read_text(encoding="utf-8")
            + "`PHASE11_MATRIX_GAP_STATUS=driver_local_matrix_docs_absent_shared_header_matrix_only`\n",
            encoding="utf-8",
        )
        expect_failure(
            forbidden_root,
            "`PHASE11_MATRIX_GAP_STATUS=driver_local_matrix_docs_absent_shared_header_matrix_only`",
        )

        wrong_count_root = tmpdir / "wrong_count"
        shutil.copytree(fixture_root, wrong_count_root, dirs_exist_ok=True)
        inventory = json.loads((wrong_count_root / FILES["inventory"]).read_text(encoding="utf-8"))
        inventory["shared_test_depend_steps"] = inventory["shared_test_depend_steps"][:-1]
        write(wrong_count_root / FILES["inventory"], json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_count_root, "expected 13 shared_test_depend_steps entries")

        wrong_dedicated_root = tmpdir / "wrong_dedicated"
        shutil.copytree(fixture_root, wrong_dedicated_root, dirs_exist_ok=True)
        inventory = json.loads((wrong_dedicated_root / FILES["inventory"]).read_text(encoding="utf-8"))
        inventory["dedicated_survey_replays"] = []
        write(wrong_dedicated_root / FILES["inventory"], json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_dedicated_root, "unexpected dedicated_survey_replays packet")

        print("PHASE11_MATRIX_GAP_SURVEY_CHECK=pass")
        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=4")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_MATRIX_GAP_SURVEY_CHECK=fail: {exc}")
        return 1

    print("PHASE11_MATRIX_GAP_SURVEY_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
        "`PHASE11_MATRIX_GAP_STATUS=gpio_and_hvc_matrices_direct_readback_only`",
        "lane: `P11-L03`",
        "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
        "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
        "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
        "Current direct contents reads in this run rematerialize the gpio watchdog and HVC matrix notes",
        "do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "The directly readable driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` and `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
        "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains",
        "`zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower current-head HVC continuity packet",
        "3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays",
        "does not stand in for a whole-Phase-11 replay roster while the current direct-readback expansion is limited to the gpio and HVC matrix notes plus the existing HVC continuity packet",
        "`phase11-hvc-hv-ops-layout-proof-tests`",
        "`phase11-hvc-export-surface-layout-proof-tests`",
        "`phase11-hvc-cleanup-packet-proof`",
    ],
}

FORBIDDEN_MARKERS = {
    "matrix_gap_note": [
        "`PHASE11_MATRIX_GAP_STATUS=all_phase11_driver_matrices_direct_readback_only`",
        "The directly readable driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "Current direct contents reads in this run now rematerialize all four driver-local Phase 11 matrix notes named by the roadmap",
        "does not stand in for a whole-Phase-11 replay roster while the current direct-readback expansion is limited to the four driver-local matrix notes plus the existing HVC continuity packet",
    ],
}

REQUIRED_BUILD_TEST_NAMES = (
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
)

REQUIRED_SHARED_DEPEND_STEPS: tuple[str, ...] = ()

REQUIRED_MODULE_ROOT_SOURCE_FILES = (
    {
        "module": "hv_ops_proof_module",
        "path": "phase11_hvc_hv_ops_layout_proof.zig",
    },
    {
        "module": "export_surface_proof_module",
        "path": "phase11_hvc_export_surface_layout_proof.zig",
    },
    {
        "module": "proof_module",
        "path": "phase11_hvc_cleanup_packet_proof.zig",
    },
)

REQUIRED_TEST_ROOT_MODULES = (
    {
        "test": "phase11-hvc-hv-ops-layout-proof-tests",
        "root_module": "hv_ops_proof_module",
    },
    {
        "test": "phase11-hvc-export-surface-layout-proof-tests",
        "root_module": "export_surface_proof_module",
    },
    {
        "test": "phase11-hvc-cleanup-packet-proof",
        "root_module": "proof_module",
    },
)

REQUIRED_DEDICATED_SURVEY_REPLAYS: tuple[str, ...] = ()

REQUIRED_SHARED_ADJUNCT_REPLAYS = (
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
)


class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    normalized_text = normalize_whitespace(text)
    for marker in markers:
        if normalize_whitespace(marker) not in normalized_text:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_forbidden_markers_absent(label: str, text: str) -> None:
    normalized_text = normalize_whitespace(text)
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if normalize_whitespace(marker) in normalized_text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    if len(value) != len(set(value)):
        raise CheckError(f"duplicate entry in {label}")
    return list(value)


def expect_exact_string_list(label: str, actual: object, expected: tuple[str, ...]) -> None:
    if expect_string_list(label, actual) != list(expected):
        raise CheckError(f"{label} does not match the current-head HVC continuity packet")


def expect_exact_object_list(
    label: str,
    actual: object,
    expected: tuple[dict[str, str], ...],
) -> None:
    if not isinstance(actual, list) or any(not isinstance(item, dict) for item in actual):
        raise CheckError(f"expected object list for {label}")
    if actual != list(expected):
        raise CheckError(f"{label} does not match the current-head HVC continuity packet")


def run_check(root: Path) -> None:
    survey_text = read_text(root, FILES["matrix_gap_note"])
    expect_markers("matrix_gap_note", survey_text, MARKERS["matrix_gap_note"])
    expect_forbidden_markers_absent("matrix_gap_note", survey_text)

    inventory = json.loads(read_text(root, FILES["inventory"]))
    if not isinstance(inventory, dict):
        raise CheckError("expected object in inventory")

    expect_exact_string_list(
        "build_test_names",
        inventory.get("build_test_names"),
        REQUIRED_BUILD_TEST_NAMES,
    )
    expect_exact_string_list(
        "shared_test_depend_steps",
        inventory.get("shared_test_depend_steps"),
        REQUIRED_SHARED_DEPEND_STEPS,
    )
    expect_exact_object_list(
        "module_root_source_files",
        inventory.get("module_root_source_files"),
        REQUIRED_MODULE_ROOT_SOURCE_FILES,
    )
    expect_exact_object_list(
        "test_root_modules",
        inventory.get("test_root_modules"),
        REQUIRED_TEST_ROOT_MODULES,
    )
    expect_exact_string_list(
        "dedicated_survey_replays",
        inventory.get("dedicated_survey_replays"),
        REQUIRED_DEDICATED_SURVEY_REPLAYS,
    )
    expect_exact_string_list(
        "shared_adjunct_replays",
        inventory.get("shared_adjunct_replays"),
        REQUIRED_SHARED_ADJUNCT_REPLAYS,
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    write(
        root / FILES["matrix_gap_note"],
        """# Phase 11 Validation Matrix Gap Survey

- `PHASE11_MATRIX_GAP_STATUS=gpio_and_hvc_matrices_direct_readback_only`
- lane: `P11-L03`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- Current direct contents reads in this run rematerialize the gpio watchdog and HVC matrix notes, but do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, so the shared matrix packet should treat gpio and HVC as current direct-readback matrix evidence while keeping bcm2835 and DesignWare in repo-reality-gap vocabulary.
- The directly readable driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` and `Documentation/zigux/phase11-hvc-console-validation-matrix.md`.
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains useful adjacent shared evidence, but it is not one of the driver-local Phase 11 validation matrices named by the roadmap
- `zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower current-head HVC continuity packet
- 3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays
- the shared build inventory does not stand in for a whole-Phase-11 replay roster while the current direct-readback expansion is limited to the gpio and HVC matrix notes plus the existing HVC continuity packet
- `phase11-hvc-hv-ops-layout-proof-tests`
- `phase11-hvc-export-surface-layout-proof-tests`
- `phase11-hvc-cleanup-packet-proof`
""",
    )
    write(
        root / FILES["inventory"],
        json.dumps(
            {
                "build_test_names": list(REQUIRED_BUILD_TEST_NAMES),
                "shared_test_depend_steps": list(REQUIRED_SHARED_DEPEND_STEPS),
                "module_root_source_files": list(REQUIRED_MODULE_ROOT_SOURCE_FILES),
                "test_root_modules": list(REQUIRED_TEST_ROOT_MODULES),
                "dedicated_survey_replays": list(REQUIRED_DEDICATED_SURVEY_REPLAYS),
                "shared_adjunct_replays": list(REQUIRED_SHARED_ADJUNCT_REPLAYS),
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
            ("matrix_gap_note", "`PHASE11_MATRIX_GAP_STATUS=gpio_and_hvc_matrices_direct_readback_only`"),
            (
                "matrix_gap_note",
                "The directly readable driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` and `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
            ),
        ]
        for idx, (label, marker) in enumerate(required_cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1).replace(marker, "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_root = tmpdir / "forbidden"
        shutil.copytree(fixture_root, forbidden_root, dirs_exist_ok=True)
        path = forbidden_root / FILES["matrix_gap_note"]
        path.write_text(
            path.read_text(encoding="utf-8")
            + "`PHASE11_MATRIX_GAP_STATUS=all_phase11_driver_matrices_direct_readback_only`\n",
            encoding="utf-8",
        )
        expect_failure(
            forbidden_root,
            "`PHASE11_MATRIX_GAP_STATUS=all_phase11_driver_matrices_direct_readback_only`",
        )

        wrong_count_root = tmpdir / "wrong_count"
        shutil.copytree(fixture_root, wrong_count_root, dirs_exist_ok=True)
        inventory = json.loads((wrong_count_root / FILES["inventory"]).read_text(encoding="utf-8"))
        inventory["shared_adjunct_replays"] = inventory["shared_adjunct_replays"][:-1]
        write(wrong_count_root / FILES["inventory"], json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_count_root, "shared_adjunct_replays does not match")

        wrong_module_root_root = tmpdir / "wrong_module_root"
        shutil.copytree(fixture_root, wrong_module_root_root, dirs_exist_ok=True)
        inventory = json.loads((wrong_module_root_root / FILES["inventory"]).read_text(encoding="utf-8"))
        inventory["module_root_source_files"][2]["path"] = "phase11_hvc_cleanup.zig"
        write(wrong_module_root_root / FILES["inventory"], json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_module_root_root, "module_root_source_files does not match")

        wrong_test_root_root = tmpdir / "wrong_test_root"
        shutil.copytree(fixture_root, wrong_test_root_root, dirs_exist_ok=True)
        inventory = json.loads((wrong_test_root_root / FILES["inventory"]).read_text(encoding="utf-8"))
        inventory["test_root_modules"][2]["root_module"] = "export_surface_proof_module"
        write(wrong_test_root_root / FILES["inventory"], json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_test_root_root, "test_root_modules does not match")

        print("PHASE11_MATRIX_GAP_SURVEY_CHECK=pass")
        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=6")
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

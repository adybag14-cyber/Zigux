#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path

FILES = {
    "matrix_gap_note": "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "inventory": "zigux/tests/fixtures/phase11_build_inventory.json",
}
REQUIRED_BUILD_TEST_NAMES = (
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
)
REQUIRED_SHARED_DEPEND_STEPS: tuple[str, ...] = ()
REQUIRED_MODULE_ROOT_SOURCE_FILES = (
    {"module": "hv_ops_proof_module", "path": "phase11_hvc_hv_ops_layout_proof.zig"},
    {"module": "export_surface_proof_module", "path": "phase11_hvc_export_surface_layout_proof.zig"},
    {"module": "proof_module", "path": "phase11_hvc_cleanup_packet_proof.zig"},
)
REQUIRED_TEST_ROOT_MODULES = (
    {"test": "phase11-hvc-hv-ops-layout-proof-tests", "root_module": "hv_ops_proof_module"},
    {"test": "phase11-hvc-export-surface-layout-proof-tests", "root_module": "export_surface_proof_module"},
    {"test": "phase11-hvc-cleanup-packet-proof", "root_module": "proof_module"},
)
REQUIRED_DEDICATED_SURVEY_REPLAYS: tuple[str, ...] = ()
REQUIRED_SHARED_ADJUNCT_REPLAYS = (
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
)
REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS = (
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
)
SURVEY_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    "Authenticated GitHub contents rereads in this run rematerialize the gpio watchdog and HVC console driver-local Phase 11 matrix notes named by the roadmap, while raw `master` fallback rereads also rematerialize the bcm2835 and DesignWare driver-local matrix notes on current `master`",
    "The currently reread driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays",
    "The same narrower continuity packet also stays `layout_assert`-backed through `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` and `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, so keep those surviving ABI proof shards explicit as adjacent HVC continuity evidence instead of treating the three build routes as prose-only review support.",
    "The directly readable HVC current-head packet also now includes the standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` witness and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` build shard",
    "The same narrower continuity packet also keeps the dedicated `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` guard explicit through `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test` and `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "That adjacent HVC-only proof packet still leaves a roadmap-facing ABI proof gap on current `master`: the repo does not yet rematerialize a broader shared replay or survey route that would carry cross-driver public-struct ABI proof beyond those surviving `layout_assert` shards.",
    "Current `master` also materializes `scripts/zigux/validate-phase11.py` and `zigux/Makefile`, and the live Makefile exposes `make -C zigux phase11-validate`",
]
FORBIDDEN_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=driver_local_matrix_roster_incomplete_on_current_master`",
    "Current direct contents reads in this run rematerialize the gpio watchdog and HVC console driver-local Phase 11 matrix notes named by the roadmap, but they do not rematerialize the bcm2835 or DesignWare driver-local matrix notes on current `master`",
    "Current direct contents reads in this run do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
]
FIXTURE_SURVEY_TEXT = Path(__file__).resolve().parents[2].joinpath(FILES["matrix_gap_note"]).read_text(encoding="utf-8") if Path(__file__).resolve().parents[2].joinpath(FILES["matrix_gap_note"]).exists() else ""


class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    if len(value) != len(set(value)):
        raise CheckError(f"duplicate entry in {label}")
    return list(value)


def expect_exact_string_list(label: str, actual: object, expected: tuple[str, ...]) -> None:
    if expect_string_list(label, actual) != list(expected):
        raise CheckError(f"{label} does not match the current-head HVC continuity packet")


def expect_exact_object_list(label: str, actual: object, expected: tuple[dict[str, str], ...]) -> None:
    if not isinstance(actual, list) or any(not isinstance(item, dict) for item in actual):
        raise CheckError(f"expected object list for {label}")
    if actual != list(expected):
        raise CheckError(f"{label} does not match the current-head HVC continuity packet")


def run_check(root: Path) -> None:
    survey_text = read_text(root, FILES["matrix_gap_note"])
    normalized = " ".join(survey_text.split())
    for marker in SURVEY_MARKERS:
        if normalize_whitespace(marker) not in normalized:
            raise CheckError(f"missing marker in matrix_gap_note: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if normalize_whitespace(marker) in normalized:
            raise CheckError(f"forbidden marker in matrix_gap_note: {marker}")
    inventory = json.loads(read_text(root, FILES["inventory"]))
    if not isinstance(inventory, dict):
        raise CheckError("expected object in inventory")
    expect_exact_string_list("build_test_names", inventory.get("build_test_names"), REQUIRED_BUILD_TEST_NAMES)
    expect_exact_string_list("shared_test_depend_steps", inventory.get("shared_test_depend_steps"), REQUIRED_SHARED_DEPEND_STEPS)
    expect_exact_object_list("module_root_source_files", inventory.get("module_root_source_files"), REQUIRED_MODULE_ROOT_SOURCE_FILES)
    expect_exact_object_list("test_root_modules", inventory.get("test_root_modules"), REQUIRED_TEST_ROOT_MODULES)
    expect_exact_string_list("dedicated_survey_replays", inventory.get("dedicated_survey_replays"), REQUIRED_DEDICATED_SURVEY_REPLAYS)
    expect_exact_string_list("shared_adjunct_replays", inventory.get("shared_adjunct_replays"), REQUIRED_SHARED_ADJUNCT_REPLAYS)
    expect_exact_string_list("shared_adjunct_build_replays", inventory.get("shared_adjunct_build_replays"), REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(fragment) from exc
        return
    raise AssertionError(fragment)


def remove_marker(text: str, marker: str) -> str:
    pattern = r"\s+".join(re.escape(part) for part in marker.split())
    updated_text, count = re.subn(pattern, "", text, flags=re.MULTILINE)
    if count < 1:
        raise AssertionError(marker)
    return updated_text


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_matrix_gap_validation_"))
    try:
        fixture_root = tmpdir / "fixture"
        (fixture_root / FILES["matrix_gap_note"]).parent.mkdir(parents=True, exist_ok=True)
        (fixture_root / FILES["matrix_gap_note"]).write_text(FIXTURE_SURVEY_TEXT, encoding="utf-8")
        (fixture_root / FILES["inventory"]).parent.mkdir(parents=True, exist_ok=True)
        (fixture_root / FILES["inventory"]).write_text(json.dumps({
            "build_test_names": list(REQUIRED_BUILD_TEST_NAMES),
            "shared_test_depend_steps": list(REQUIRED_SHARED_DEPEND_STEPS),
            "module_root_source_files": list(REQUIRED_MODULE_ROOT_SOURCE_FILES),
            "test_root_modules": list(REQUIRED_TEST_ROOT_MODULES),
            "dedicated_survey_replays": list(REQUIRED_DEDICATED_SURVEY_REPLAYS),
            "shared_adjunct_replays": list(REQUIRED_SHARED_ADJUNCT_REPLAYS),
            "shared_adjunct_build_replays": list(REQUIRED_SHARED_ADJUNCT_BUILD_REPLAYS),
        }, indent=2) + "\n", encoding="utf-8")
        run_check(fixture_root)
        for index, marker in enumerate(SURVEY_MARKERS[:5], start=1):
            case_root = tmpdir / f"required_{index}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES["matrix_gap_note"]
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            expect_failure(case_root, marker)
        dedicated_witness_root = tmpdir / "required_dedicated_witness"
        shutil.copytree(fixture_root, dedicated_witness_root, dirs_exist_ok=True)
        path = dedicated_witness_root / FILES["matrix_gap_note"]
        marker = SURVEY_MARKERS[6]
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
        expect_failure(dedicated_witness_root, marker)
        abi_gap_root = tmpdir / "required_abi_gap"
        shutil.copytree(fixture_root, abi_gap_root, dirs_exist_ok=True)
        path = abi_gap_root / FILES["matrix_gap_note"]
        marker = SURVEY_MARKERS[7]
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
        expect_failure(abi_gap_root, marker)
        forbidden_root = tmpdir / "forbidden"
        shutil.copytree(fixture_root, forbidden_root, dirs_exist_ok=True)
        path = forbidden_root / FILES["matrix_gap_note"]
        marker = FORBIDDEN_MARKERS[0]
        path.write_text(path.read_text(encoding="utf-8") + "\n" + marker + "\n", encoding="utf-8")
        expect_failure(forbidden_root, marker)
        bad_inventory_root = tmpdir / "bad_inventory"
        shutil.copytree(fixture_root, bad_inventory_root, dirs_exist_ok=True)
        inventory = json.loads((bad_inventory_root / FILES["inventory"]).read_text(encoding="utf-8"))
        inventory["build_test_names"] = inventory["build_test_names"][:-1]
        (bad_inventory_root / FILES["inventory"]).write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
        expect_failure(bad_inventory_root, "build_test_names does not match")
        print("PHASE11_MATRIX_GAP_SURVEY_CHECK=pass")
        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=9")
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
